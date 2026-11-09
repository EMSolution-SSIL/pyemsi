"""Array operations on frozen meshes for the mesher process: read, copy with transforms, join nodes, find the
boundary, close quads with pyramids, split a boundary into closed shells and mesh the region they bound. numpy only
(plus gmsh in read_model and mesh_region); never imports FreeCAD."""

from collections import namedtuple
from contextlib import contextmanager

import numpy as np

# Gmsh element types 1 to 7: line, triangle, quadrangle, tetrahedron, hexahedron, prism, pyramid.
NPE = {1: 2, 2: 3, 3: 4, 4: 4, 5: 8, 6: 6, 7: 5}
# Node order that reverses an element's orientation (a mirror turns it inside out).
FLIP = {
    2: [0, 2, 1],
    3: [0, 3, 2, 1],
    4: [0, 2, 1, 3],
    5: [4, 5, 6, 7, 0, 1, 2, 3],
    6: [3, 4, 5, 0, 1, 2],
    7: [0, 3, 2, 1, 4],
}
# Faces of each 3D element, as local node indexes, oriented outward.
TRI_FACES = {
    4: [[0, 2, 1], [0, 1, 3], [0, 3, 2], [1, 2, 3]],
    6: [[0, 2, 1], [3, 4, 5]],
    7: [[0, 1, 4], [1, 2, 4], [2, 3, 4], [3, 0, 4]],
}
QUAD_FACES = {
    5: [[0, 3, 2, 1], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7], [4, 5, 6, 7]],
    6: [[0, 1, 4, 3], [1, 2, 5, 4], [2, 0, 3, 5]],
    7: [[0, 3, 2, 1]],
}
# Edges of each 2D element.
EDGE_FACES = {2: [[0, 1], [1, 2], [2, 0]], 3: [[0, 1], [1, 2], [2, 3], [3, 0]]}

Boundary = namedtuple("Boundary", "tri quad edge tri_owner quad_owner edge_owner over_used shared_area")


class FrozenError(Exception):
    """A frozen surface that cannot bound a region of the mesh. nodes: the node numbers where, when known."""

    def __init__(self, message, nodes=None):
        super().__init__(message)
        self.nodes = nodes


def read_model(dim, entities):
    """Elements of `entities` ({key: [entity tags]}) of dimension `dim` in the current gmsh model.
    Returns (xyz[n, 3], {key: {etype: connectivity}}), node indexes 0-based into xyz; nodes shared by keys stay shared."""
    import gmsh

    raw = {}
    for key, tags in entities.items():
        per_type = {}
        for tag in tags:
            types, _, nodes = gmsh.model.mesh.getElements(dim, tag)
            for etype, nds in zip(types, nodes):
                if etype in NPE:
                    per_type.setdefault(int(etype), []).append(np.asarray(nds, dtype=np.int64).reshape(-1, NPE[etype]))
        raw[key] = {t: np.vstack(a) for t, a in per_type.items()}
    used = [c.ravel() for per_type in raw.values() for c in per_type.values()]
    if not used:
        return np.zeros((0, 3)), {key: {} for key in entities}
    node_tags, inverse = np.unique(np.concatenate(used), return_inverse=True)
    inverse = inverse.ravel()
    all_tags, coords, _ = gmsh.model.mesh.getNodes()
    all_tags = np.asarray(all_tags)
    order = np.argsort(all_tags)
    xyz = np.asarray(coords, dtype=float).reshape(-1, 3)[order][np.searchsorted(all_tags[order], node_tags)]
    out, start = {}, 0
    for key, per_type in raw.items():
        out[key] = {}
        for etype, conn in per_type.items():
            out[key][etype] = inverse[start : start + conn.size].reshape(conn.shape)
            start += conn.size
    return xyz, out


def join_nodes(V, tol=1e-6):
    """Join nodes closer than `tol`. Returns (count, labels): labels[i] is the 0-based joined node of node i.
    Points are rounded to grids of cell 2 * tol, offset by half a cell on each subset of axes, so a pair split by
    one grid is caught by another; the lowest label then spreads through each cell until nothing changes."""
    V = np.asarray(V, dtype=float).reshape(-1, 3)
    n = len(V)
    if n == 0:
        return 0, np.zeros(0, dtype=np.int64)
    h = 2.0 * tol
    groups = []
    for mask in range(8):
        shift = np.array([0.5 if mask >> a & 1 else 0.0 for a in range(3)])
        keys = np.floor(V / h + shift).astype(np.int64)
        groups.append(np.unique(keys, axis=0, return_inverse=True)[1].ravel())
    label = np.arange(n)
    while True:
        old = label
        for g in groups:
            low = np.full(g.max() + 1, n, dtype=np.int64)
            np.minimum.at(low, g, label)
            label = low[g]
        label = label[label]
        if np.array_equal(label, old):
            break
    _, labels = np.unique(label, return_inverse=True)
    labels = labels.ravel()
    return int(labels.max()) + 1, labels


def copy_mesh(xyz, bodies, transforms):
    """Copy `bodies` ({key: {etype: connectivity}}) once per transform (16 floats, row-major 4x4) and join the
    nodes that coincide. Connectivity is reversed when the transform's determinant is negative.
    Returns (V, {(key, copy): {etype: connectivity}})."""
    xyz = np.asarray(xyz, dtype=float).reshape(-1, 3)
    n = len(xyz)
    moved, flipped = [], []
    for t in transforms:
        M = np.asarray(t, dtype=float).reshape(4, 4)
        moved.append(xyz @ M[:3, :3].T + M[:3, 3])
        flipped.append(np.linalg.det(M[:3, :3]) < 0)
    allv = np.vstack(moved)
    count, labels = join_nodes(allv)
    V = np.zeros((count, 3))
    V[labels[::-1]] = allv[::-1]  # the first node of each group wins
    out = {}
    for i, flip in enumerate(flipped):
        for key, per_type in bodies.items():
            out[(key, i)] = {}
            for etype, conn in per_type.items():
                new = labels[np.asarray(conn) + i * n]
                if flip and etype in FLIP:
                    new = new[:, FLIP[etype]]
                out[(key, i)][etype] = new
    return V, out


def _facets(V, elements, faces, width):
    """Facets of `width` nodes of all elements: unique rows (the first orientation kept), use counts, and the
    centroid of the first element using each."""
    rows, owners = [], []
    for per_type in elements:
        for etype, conn in per_type.items():
            conn = np.asarray(conn)
            for local in faces.get(etype, ()):
                rows.append(conn[:, local])
                owners.append(V[conn].mean(axis=1))
    if not rows:
        return np.zeros((0, width), dtype=np.int64), np.zeros(0, dtype=np.int64), np.zeros((0, 3))
    rows, owners = np.vstack(rows), np.vstack(owners)
    _, first, inverse = np.unique(np.sort(rows, axis=1), axis=0, return_index=True, return_inverse=True)
    return rows[first], np.bincount(inverse.ravel()), owners[first]


def _area(V, f):
    if f.shape[1] == 2:
        return np.linalg.norm(V[f[:, 1]] - V[f[:, 0]], axis=1)
    if f.shape[1] == 3:
        return 0.5 * np.linalg.norm(np.cross(V[f[:, 1]] - V[f[:, 0]], V[f[:, 2]] - V[f[:, 0]]), axis=1)
    return 0.5 * np.linalg.norm(np.cross(V[f[:, 2]] - V[f[:, 0]], V[f[:, 3]] - V[f[:, 1]]), axis=1)


def boundary(V, elements, dim):
    """Facets used by exactly one element of `elements` (a list of {etype: connectivity}): `tri` and `quad` in 3D,
    `edge` in 2D (the others empty), each with `*_owner`, the centroid of the element using it. `over_used`
    counts facets in 3 or more elements; `shared_area` is the area (length in 2D) of the facets used twice."""
    V = np.asarray(V, dtype=float)
    faces = {"tri": TRI_FACES, "quad": QUAD_FACES} if dim == 3 else {"edge": EDGE_FACES}
    width = {"tri": 3, "quad": 4, "edge": 2}
    found, over_used, shared = {}, 0, 0.0
    for name in ("tri", "quad", "edge"):
        facets, use, owner = _facets(V, elements, faces.get(name, {}), width[name])
        once = use == 1
        found[name] = (facets[once], owner[once])
        over_used += int((use >= 3).sum())
        shared += float(_area(V, facets[use == 2]).sum()) if len(facets) else 0.0
    return Boundary(
        found["tri"][0],
        found["quad"][0],
        found["edge"][0],
        found["tri"][1],
        found["quad"][1],
        found["edge"][1],
        over_used,
        shared,
    )


def quad_pyramids(V, quads):
    """Close each outward-oriented quad with a pyramid on the outside. The apex is the centroid plus the outward
    normal times 0.3 * sqrt(area). Returns (V2, pyramids[n, 5], tris[4n, 3]): V with the apexes appended, the
    pyramids (base nodes then apex) and their four outward triangular sides each."""
    V = np.asarray(V, dtype=float)
    quads = np.asarray(quads, dtype=np.int64).reshape(-1, 4)
    n = len(quads)
    cross = np.cross(V[quads[:, 2]] - V[quads[:, 0]], V[quads[:, 3]] - V[quads[:, 1]])
    length = np.linalg.norm(cross, axis=1)
    apex = V[quads].mean(axis=1) + cross / length[:, None] * 0.3 * np.sqrt(0.5 * length)[:, None]
    V2 = np.vstack([V, apex])
    pyramids = np.column_stack([quads, len(V) + np.arange(n)])
    tris = np.stack([pyramids[:, f] for f in TRI_FACES[7]], axis=1).reshape(-1, 3)
    return V2, pyramids, tris


def _components(n, pairs):
    """Connected components of n items joined by pairs[m, 2]: label[i] is the lowest item of i's component."""
    label = np.arange(n)
    a, b = pairs[:, 0], pairs[:, 1]
    while True:
        old = label
        low = np.minimum(label[a], label[b])
        label = label.copy()
        np.minimum.at(label, a, low)
        np.minimum.at(label, b, low)
        label = label[label]
        if np.array_equal(label, old):
            return label


def shells(facets):
    """The connected components of a closed surface: triangles over their shared edges, or 2D edges over their shared
    nodes. Returns a list of arrays of facet indexes, in the order of each component's first facet. A surface that
    is not closed and manifold (an edge, in 2D a node, not used exactly twice) raises FrozenError."""
    facets = np.asarray(facets, dtype=np.int64)
    if not len(facets):
        return []
    local = [[0, 1], [1, 2], [2, 0]] if facets.shape[1] == 3 else [[0], [1]]
    what = "an edge" if facets.shape[1] == 3 else "a node"
    sides = np.sort(np.vstack([facets[:, k] for k in local]), axis=1)
    owner = np.tile(np.arange(len(facets)), len(local))
    unique, inverse, counts = np.unique(sides, axis=0, return_inverse=True, return_counts=True)
    if (counts != 2).any():
        raise FrozenError(f"{what} of the surface is not used exactly twice", unique[counts != 2][0])
    order = np.argsort(inverse.ravel(), kind="stable")
    label = _components(len(facets), owner[order].reshape(-1, 2))
    order = np.argsort(label, kind="stable")
    return np.split(order, np.flatnonzero(np.diff(label[order])) + 1)


def _chain(edges):
    """The nodes of one closed loop of 2D edges, in order."""
    links = {}
    for a, b in edges.tolist():
        links.setdefault(a, []).append(b)
        links.setdefault(b, []).append(a)
    start = int(edges[0, 0])
    loop, last, node = [start], start, int(edges[0, 1])
    while node != start:
        loop.append(node)
        last, node = node, links[node][0] if links[node][1] == last else links[node][1]
    return np.array(loop, dtype=np.int64)


def _oriented(tris):
    """A closed connected surface of triangles with every triangle turned to agree with the first (a surface from
    gmsh is oriented face by face)."""
    tris = tris.copy()
    sides = {}
    for f, t in enumerate(tris.tolist()):
        for k in range(3):
            sides.setdefault(frozenset((t[k], t[(k + 1) % 3])), []).append(f)
    seen, stack = {0}, [0]
    while stack:
        f = stack.pop()
        t = tris[f].tolist()
        for k in range(3):
            a, b = t[k], t[(k + 1) % 3]
            for g in sides[frozenset((a, b))]:
                if g in seen:
                    continue
                other = tris[g].tolist()
                j = other.index(a)
                if other[(j + 1) % 3] == b:  # both run a to b: g is the wrong way round
                    tris[g] = tris[g][::-1]
                seen.add(g)
                stack.append(g)
    return tris


def _winding_3d(point, corners):
    """The winding number about point of the closed surface with triangles corners[n, 3, 3]."""
    a, b, c = corners[:, 0] - point, corners[:, 1] - point, corners[:, 2] - point
    la, lb, lc = np.linalg.norm(a, axis=1), np.linalg.norm(b, axis=1), np.linalg.norm(c, axis=1)
    top = np.einsum("ij,ij->i", a, np.cross(b, c))
    under = la * lb * lc + np.einsum("ij,ij->i", a, b) * lc + np.einsum("ij,ij->i", b, c) * la
    under += np.einsum("ij,ij->i", c, a) * lb
    return float((2.0 * np.arctan2(top, under)).sum() / (4.0 * np.pi))


def _winding_2d(point, start, end):
    """The winding number about point[2] of the closed set of directed segments from start[n, 2] to end[n, 2]."""
    a, b = start - point, end - point
    angle = np.arctan2(a[:, 0] * b[:, 1] - a[:, 1] * b[:, 0], np.einsum("ij,ij->i", a, b))
    return float(angle.sum() / (2.0 * np.pi))


def winding(V, facets, point):
    """The winding number about point[3] of directed facets (triangles, or 2D edges) that together are closed. They
    need not be one connected or manifold surface; the facets of a Boundary run outward, so it is 1 or -1 inside a
    copy and 0 outside, in a cavity of one included."""
    V = np.asarray(V, dtype=float)
    facets = np.asarray(facets, dtype=np.int64)
    point = np.asarray(point, dtype=float)
    if facets.shape[1] == 3:
        return _winding_3d(point, V[facets])
    axes = np.sort(np.argsort(np.ptp(V[np.unique(facets)], axis=0))[1:])  # the plane of the drawing: XY or ZX
    return _winding_2d(point[axes], V[facets[:, 0]][:, axes], V[facets[:, 1]][:, axes])


def _directed(facets, shell):
    """The facets of one shell made to agree: triangles turned alike, 2D edges chained into a loop."""
    facets = np.asarray(facets, dtype=np.int64)
    if facets.shape[1] == 3:
        return _oriented(facets[shell])
    loop = _chain(facets[shell])
    return np.column_stack([loop, np.roll(loop, -1)])


def encloses(V, facets, shell, point):
    """True when the closed shell (indexes into facets) goes around point."""
    return abs(winding(V, _directed(facets, shell), point)) > 0.5


def nest(V, facets, shells):
    """Which shells bound which regions. shells: as returned by shells(facets). Returns [(outer, [inner, ...])], in
    shell numbers: a shell at even depth is the outer boundary of a region, one at odd depth a hole of its parent."""
    V = np.asarray(V, dtype=float)
    rings = [_directed(facets, s) for s in shells]
    points = [V[ring[0]].mean(axis=0) for ring in rings]
    count = len(rings)
    around = [[j for j in range(count) if j != i and abs(winding(V, rings[j], points[i])) > 0.5] for i in range(count)]
    depth = [len(a) for a in around]
    regions = {i: [] for i in range(count) if depth[i] % 2 == 0}
    for i in range(count):
        if depth[i] % 2:
            regions[next(j for j in around[i] if depth[j] == depth[i] - 1)].append(i)
    return list(regions.items())


@contextmanager
def _options(values):
    """Set gmsh options for one step and put them back after it, so the steps after it are not affected."""
    import gmsh

    saved = {name: gmsh.option.getNumber(name) for name in values}
    try:
        for name, value in values.items():
            gmsh.option.setNumber(name, value)
        yield
    finally:
        for name, value in saved.items():
            gmsh.option.setNumber(name, value)


def _region_3d(V, facets, rings):
    """In the current, empty gmsh model: mesh the volume bounded by the triangles of the shells rings, the outer shell
    first. The nodes' gmsh tags are their indexes in V + 1."""
    import gmsh

    triangles = facets[np.concatenate(rings)]
    used = np.unique(triangles)
    gmsh.model.addDiscreteEntity(2, 1)
    gmsh.model.mesh.addNodes(2, 1, (used + 1).tolist(), V[used].ravel().tolist())
    gmsh.model.mesh.addElementsByType(1, 2, [], (triangles + 1).ravel().tolist())
    gmsh.model.mesh.createTopology()
    ring_of = {tuple(sorted(t)): k for k, shell in enumerate(rings) for t in (facets[shell] + 1).tolist()}
    surfaces = [[] for _ in rings]
    for _, tag in gmsh.model.getEntities(2):
        nodes = gmsh.model.mesh.getElements(2, tag)[2]
        if len(nodes) and len(nodes[0]):  # createTopology may leave an entity without elements
            surfaces[ring_of[tuple(sorted(int(n) for n in nodes[0][:3]))]].append(tag)
    loops = [gmsh.model.geo.addSurfaceLoop(tags) for tags in surfaces]
    gmsh.model.geo.addVolume(loops)
    gmsh.model.geo.synchronize()
    gmsh.model.mesh.generate(3)


def _region_2d(V, facets, rings):
    """In the current, empty gmsh model: mesh the plane surface bounded by the polygons of the shells rings, the outer
    one first, through the nodes' real coordinates, each polygon line one element."""
    import gmsh

    occ = gmsh.model.occ
    loops, lines = [], []
    for shell in rings:
        points = [occ.addPoint(*V[n].tolist()) for n in _chain(facets[shell]).tolist()]
        ring = [occ.addLine(p, q) for p, q in zip(points, points[1:] + points[:1])]
        loops.append(occ.addCurveLoop(ring))
        lines += ring
    occ.addPlaneSurface(loops)
    occ.synchronize()
    for line in lines:
        gmsh.model.mesh.setTransfiniteCurve(line, 2)
    gmsh.model.mesh.generate(2)


def mesh_region(V, facets, outer, inners, size, dim):
    """Mesh the region bounded by the shell outer (indexes into facets, whose node numbers refer to V), minus the
    shells inners. Returns (V2, {etype: connectivity}): V with the new nodes appended, nodes 0 to len(V) - 1 unchanged,
    connectivity into V2. A frozen node moved by gmsh raises FrozenError. The current gmsh model stays as it was."""
    import gmsh

    V = np.asarray(V, dtype=float).reshape(-1, 3)
    facets = np.asarray(facets, dtype=np.int64)
    rings = [np.asarray(outer, dtype=np.int64)] + [np.asarray(s, dtype=np.int64) for s in inners]
    used = np.unique(facets[np.concatenate(rings)])
    options = {"Mesh.Renumber": 0, "Mesh.MeshSizeMax": size, "Mesh.MeshSizeExtendFromBoundary": 1, "Mesh.Optimize": 1}
    if dim == 3:
        options["Mesh.Algorithm3D"] = 1
    current = gmsh.model.getCurrent()
    gmsh.model.add("region")
    try:
        with _options(options):
            (_region_3d if dim == 3 else _region_2d)(V, facets, rings)
        tags, coords, _ = gmsh.model.mesh.getNodes()
        tags = np.asarray(tags, dtype=np.int64)
        xyz = np.asarray(coords, dtype=float).reshape(-1, 3)
        found = {}
        for _, entity in gmsh.model.getEntities(dim):
            types, _, nodes = gmsh.model.mesh.getElements(dim, entity)
            for etype, conn in zip(types, nodes):
                found.setdefault(int(etype), []).append(np.asarray(conn, dtype=np.int64).reshape(-1, NPE[int(etype)]))
    finally:
        gmsh.model.remove()
        gmsh.model.setCurrent(current)
    index = np.zeros(int(tags.max()) + 1, dtype=np.int64)
    if dim == 3:  # the frozen nodes kept their tags
        kept = np.isin(tags, used + 1)
        if (
            np.abs(xyz[kept] - V[tags[kept] - 1]).max(axis=1) > 1e-9 * max(float(np.ptp(V[used], axis=0).max()), 1.0)
        ).any():
            raise FrozenError("gmsh moved a frozen node")
        index[tags[kept]] = tags[kept] - 1
    else:  # the polygon nodes came back under new tags: join them with V by position
        count, labels = join_nodes(np.vstack([V[used], xyz]))
        first = np.full(count, -1, dtype=np.int64)
        first[labels[::-1]] = np.arange(len(labels))[::-1]
        twin = first[labels[len(used) :]]
        kept = twin < len(used)
        index[tags[kept]] = used[twin[kept]]
    fresh = np.flatnonzero(~kept)
    fresh = fresh[np.argsort(tags[fresh], kind="stable")]
    index[tags[fresh]] = len(V) + np.arange(len(fresh))
    return np.vstack([V, xyz[fresh]]), {t: index[np.vstack(a)] for t, a in found.items()}
