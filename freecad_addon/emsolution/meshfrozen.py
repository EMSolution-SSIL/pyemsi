"""Array operations on frozen meshes for the mesher process: read, copy with transforms, join nodes, find the
boundary, close quads with pyramids, split a boundary into closed shells and mesh the region they bound. numpy only
(plus gmsh in read_model, on_surface, inside and mesh_region); never imports FreeCAD."""

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
# index: the rows of facets lying on a face; face: the tag of that face, for each; inside: whether its owning element
# is inside the free object, for each
OnFaces = namedtuple("OnFaces", "index face inside")


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


def inside(dim, entity, points):
    """For each of points[n, 3]: True when it lies inside the OCC entity of the current gmsh model."""
    import gmsh

    box = np.array(gmsh.model.getBoundingBox(dim, entity))
    tol = 1e-6 * max(1.0, float(np.linalg.norm(box[3:] - box[:3])))
    near = np.all(points >= box[:3] - tol, axis=1) & np.all(points <= box[3:] + tol, axis=1)
    for k in np.flatnonzero(near):
        near[k] = gmsh.model.isInside(dim, entity, points[k].tolist()) > 0
    return near


def _free_entity(face_tags, dim):
    """The entity of dimension dim of the current gmsh model whose whole boundary is face_tags. A face between two
    bodies is above both, so the boundary is what tells them apart."""
    import gmsh

    wanted = {int(f) for f in face_tags}
    above = set.intersection(*[{int(e) for e in gmsh.model.getAdjacencies(dim - 1, f)[0]} for f in wanted])
    for entity in sorted(above):
        faces = gmsh.model.getBoundary([(dim, entity)], combined=False, oriented=False)
        if {abs(int(t)) for _, t in faces} == wanted:
            return entity
    raise ValueError(f"no entity of dimension {dim} has the faces {sorted(wanted)}")


def on_surface(V, facets, owners, face_tags, dim):
    """The frozen facets (rows of nodes into V; owners: the centre of each one's owning element) lying on a face
    of the free object bounded by the faces face_tags (lines in 2D) of the current gmsh model. Returns OnFaces.
    A facet lies on a face when all its nodes do, within a small tolerance, its centre projects inside the trimmed
    face, and in 3D its normal roughly matches the face's: a facet may be a chord of a curved face, or a triangle of
    an end cap with all its corners on a rim."""
    import gmsh

    V = np.asarray(V, dtype=float)
    facets = np.asarray(facets, dtype=np.int64)
    empty = OnFaces(np.zeros(0, dtype=np.int64), np.zeros(0, dtype=np.int64), np.zeros(0, dtype=bool))
    if not len(facets) or not len(face_tags):
        return empty
    model_box = np.array(gmsh.model.getBoundingBox(-1, -1))
    tol = 1e-6 * max(1.0, float(np.linalg.norm(model_box[3:] - model_box[:3])))
    fdim = dim - 1
    centres = V[facets].mean(axis=1)
    index, faces = [], []
    assigned = np.zeros(len(facets), dtype=bool)
    for face in face_tags:
        box = np.array(gmsh.model.getBoundingBox(fdim, face))
        in_box = np.all((V[facets] >= box[:3] - tol) & (V[facets] <= box[3:] + tol), axis=(1, 2))
        near = np.flatnonzero(in_box & ~assigned)
        if not len(near):
            continue
        nodes = np.unique(facets[near])
        points = np.asarray(gmsh.model.getClosestPoint(fdim, face, V[nodes].ravel().tolist())[0]).reshape(-1, 3)
        on = np.zeros(len(V), dtype=bool)
        on[nodes[np.linalg.norm(points - V[nodes], axis=1) <= tol]] = True
        for k in near[on[facets[near]].all(axis=1)]:
            point, uv = gmsh.model.getClosestPoint(fdim, face, centres[k].tolist())
            if gmsh.model.isInside(fdim, face, list(point)) != 1:
                continue
            if dim == 3:
                row = facets[k]
                cross = np.cross(V[row[2]] - V[row[0]], V[row[-1]] - V[row[1]])
                normal = np.asarray(gmsh.model.getNormal(face, list(uv)))
                if abs(float(cross @ normal)) < 0.7 * float(np.linalg.norm(cross)):
                    continue
            index.append(k)
            faces.append(int(face))
            assigned[k] = True
    if not index:
        return empty
    index = np.array(index, dtype=np.int64)
    entity = _free_entity(face_tags, dim)
    return OnFaces(index, np.array(faces, dtype=np.int64), inside(dim, entity, np.asarray(owners)[index]))


def on_facets(V, facets, point, tol):
    """True when point lies on one of facets: triangles (rows of 3) or 2D edges (rows of 2). It may be off a facet by a
    fifth of the facet's longest side, so a point of a curved face counts as on the flat facet that is a chord of it."""
    V = np.asarray(V, dtype=float)
    facets = np.asarray(facets, dtype=np.int64)
    point = np.asarray(point, dtype=float)
    a, e0 = V[facets[:, 0]], V[facets[:, 1]] - V[facets[:, 0]]
    to = point - a
    if facets.shape[1] == 2:
        t = np.einsum("ij,ij->i", to, e0) / np.einsum("ij,ij->i", e0, e0)
        off = np.linalg.norm(to - t[:, None] * e0, axis=1)
        return bool(((t >= -1e-3) & (t <= 1 + 1e-3) & (off <= np.maximum(tol, 0.2 * np.linalg.norm(e0, axis=1)))).any())
    e1 = V[facets[:, 2]] - a
    d00, d01, d11 = (np.einsum("ij,ij->i", p, q) for p, q in ((e0, e0), (e0, e1), (e1, e1)))
    d20, d21 = np.einsum("ij,ij->i", to, e0), np.einsum("ij,ij->i", to, e1)
    under = d00 * d11 - d01 * d01
    v, w = (d11 * d20 - d01 * d21) / under, (d00 * d21 - d01 * d20) / under
    normal = np.cross(e0, e1)
    normal /= np.linalg.norm(normal, axis=1)[:, None]
    off = np.abs(np.einsum("ij,ij->i", to, normal))
    longest = np.sqrt(np.maximum(d00, d11))
    return bool(((v >= -1e-3) & (w >= -1e-3) & (v + w <= 1 + 1e-3) & (off <= np.maximum(tol, 0.2 * longest))).any())


CLEAR = 0.4  # a pyramid rises at most this share of the room in front of it, so two facing ones never meet


def _closest_on_triangles(p, tri):
    """The point of each triangle tri[m, 3, 3] closest to p[m, 3]: the foot on its plane when that lies inside it,
    else the closest point of its edges."""
    a, b, c = tri[:, 0], tri[:, 1], tri[:, 2]
    best = None
    for s, e in ((a, b), (b, c), (c, a)):
        d = e - s
        t = np.clip(np.einsum("ij,ij->i", p - s, d) / np.maximum(np.einsum("ij,ij->i", d, d), 1e-300), 0, 1)
        q = s + t[:, None] * d
        best = q if best is None else np.where((_sq(p - q) < _sq(p - best))[:, None], q, best)
    normal = np.cross(b - a, c - a)
    twice = np.linalg.norm(normal, axis=1)
    normal = normal / np.maximum(twice, 1e-300)[:, None]
    foot = p - np.einsum("ij,ij->i", p - a, normal)[:, None] * normal
    sides = [np.einsum("ij,ij->i", np.cross(e - s, foot - s), normal) for s, e in ((a, b), (b, c), (c, a))]
    inside = (twice > 0) & (np.minimum.reduce(sides) >= 0)
    return np.where(inside[:, None], foot, best)


def _sq(v):
    return np.einsum("ij,ij->i", v, v)


def _room(corners, centre, normal, height, around):
    """The highest each pyramid on the quads corners[n, 4, 3] may rise (at most height) so that it keeps clear of
    the triangles around[m, 3, 3]: CLEAR times the height over the quad's plane of a triangle's point closest to its
    centre, divided by how much of the pyramid stands at that point's distance from the axis (1 on the axis, 0 at the
    quad's circumradius). Points beside, behind or beyond reach of a quad do not limit it, nor do triangles with a
    corner of the quad (its own, its neighbours': a warped quad's own triangles rise a little over its plane).
    Triangles are matched to the quads near them on a grid of cells as big as the farthest reach."""
    radius = np.linalg.norm(corners - centre[:, None], axis=2).max(axis=1)
    reach = np.sqrt((height / CLEAR) ** 2 + radius**2)
    out = height.copy()
    if not len(around) or not len(centre):
        return out
    cell = reach.max()
    lo = np.minimum(around.min(axis=1).min(axis=0), (centre - reach[:, None]).min(axis=0)) - cell
    first = np.floor((around.min(axis=1) - lo) / cell).astype(np.int64)
    span = np.floor((around.max(axis=1) - lo) / cell).astype(np.int64) - first + 1
    count = span.prod(axis=1)
    which = np.repeat(np.arange(len(around)), count)  # each triangle once in every cell its box touches
    local = np.arange(count.sum()) - np.repeat(np.cumsum(count) - count, count)
    sx, sy = span[which, 0], span[which, 1]
    cells = first[which] + np.column_stack([local % sx, local // sx % sy, local // (sx * sy)])
    size = np.maximum(cells.max(axis=0), np.floor((centre - lo) / cell).max(axis=0).astype(np.int64)) + 2
    key = (cells[:, 0] * size[1] + cells[:, 1]) * size[2] + cells[:, 2]
    order = np.argsort(key, kind="stable")
    key, which = key[order], which[order]
    home = np.floor((centre - lo) / cell).astype(np.int64)
    for offset in np.array(np.meshgrid(*[[-1, 0, 1]] * 3)).reshape(3, -1).T:
        near = home + offset
        k = (near[:, 0] * size[1] + near[:, 1]) * size[2] + near[:, 2]
        start, stop = np.searchsorted(key, k, "left"), np.searchsorted(key, k, "right")
        hits = stop - start
        quad = np.repeat(np.arange(len(centre)), hits)
        if not len(quad):
            continue
        tri = which[np.repeat(start, hits) + np.arange(hits.sum()) - np.repeat(np.cumsum(hits) - hits, hits)]
        to = _closest_on_triangles(centre[quad], around[tri]) - centre[quad]
        up = np.einsum("ij,ij->i", to, normal[quad])
        aside = np.linalg.norm(to - up[:, None] * normal[quad], axis=1)
        standing = 1 - aside / radius[quad]
        apart = np.linalg.norm(around[tri][:, :, None] - corners[quad][:, None], axis=3).min(axis=(1, 2))
        limits = (up > 1e-6 * radius[quad]) & (standing > 0) & (apart > 1e-6 * radius[quad])
        np.minimum.at(out, quad[limits], CLEAR * up[limits] / standing[limits])
    return out


def _warp(corners, centre, normal):
    """The least height over centre along normal at which an apex sees every corner of the quads corners[n, 4, 3]
    from above the plane of that corner and its two neighbours (a warped quad needs some): below it the pyramid is
    inverted at a corner."""
    least = np.zeros(len(corners))
    for k in range(4):
        p = corners[:, k]
        plane = np.cross(corners[:, (k + 1) % 4] - p, corners[:, (k + 3) % 4] - p)
        along = np.einsum("ij,ij->i", plane, normal)
        need = np.einsum("ij,ij->i", plane, p - centre) / np.where(along > 0, along, np.inf)
        least = np.maximum(least, need)
    return least


def quad_pyramids(V, quads, around=None):
    """Close each outward-oriented quad with a pyramid on the outside. The apex is the centroid plus the outward
    normal times 0.3 * sqrt(area), lower where the triangles around[m, 3, 3] (coordinates: what else bounds the
    region, the quads' own triangles may be among them) come close in front of it (_room). Returns
    (V2, pyramids[n, 5], tris[4n, 3]): V with the apexes appended, the pyramids (base nodes then apex) and their four
    outward triangular sides each."""
    V = np.asarray(V, dtype=float)
    quads = np.asarray(quads, dtype=np.int64).reshape(-1, 4)
    n = len(quads)
    cross = np.cross(V[quads[:, 2]] - V[quads[:, 0]], V[quads[:, 3]] - V[quads[:, 1]])
    length = np.linalg.norm(cross, axis=1)
    centre, normal = V[quads].mean(axis=1), cross / length[:, None]
    height = 0.3 * np.sqrt(0.5 * length)
    if around is not None:
        room = _room(V[quads], centre, normal, height, np.asarray(around, dtype=float).reshape(-1, 3, 3))
        height = np.minimum(height, np.maximum(room, 2 * _warp(V[quads], centre, normal)))
    apex = centre + normal * height[:, None]
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


def _wraps_3d(point, corners):
    """How many times the closed surface with triangles corners[n, 3, 3] wraps around point: its solid angle / 4 pi."""
    a, b, c = corners[:, 0] - point, corners[:, 1] - point, corners[:, 2] - point
    la, lb, lc = np.linalg.norm(a, axis=1), np.linalg.norm(b, axis=1), np.linalg.norm(c, axis=1)
    top = np.einsum("ij,ij->i", a, np.cross(b, c))
    under = la * lb * lc + np.einsum("ij,ij->i", a, b) * lc + np.einsum("ij,ij->i", b, c) * la
    under += np.einsum("ij,ij->i", c, a) * lb
    return float((2.0 * np.arctan2(top, under)).sum() / (4.0 * np.pi))


def _wraps_2d(point, start, end):
    """How many times the closed set of directed segments from start[n, 2] to end[n, 2] goes around point[2]."""
    a, b = start - point, end - point
    angle = np.arctan2(a[:, 0] * b[:, 1] - a[:, 1] * b[:, 0], np.einsum("ij,ij->i", a, b))
    return float(angle.sum() / (2.0 * np.pi))


def wraps(V, facets, point):
    """How many times directed facets (triangles, or 2D edges) that together are closed go around point[3], signed.
    They need not be one connected or manifold surface; the facets of a Boundary run outward, so it is 1 or -1 inside
    a copy and 0 outside, in a cavity of one included."""
    V = np.asarray(V, dtype=float)
    facets = np.asarray(facets, dtype=np.int64)
    point = np.asarray(point, dtype=float)
    if facets.shape[1] == 3:
        return _wraps_3d(point, V[facets])
    axes = np.sort(np.argsort(np.ptp(V[np.unique(facets)], axis=0))[1:])  # the plane of the drawing: XY or ZX
    return _wraps_2d(point[axes], V[facets[:, 0]][:, axes], V[facets[:, 1]][:, axes])


def _directed(facets, shell):
    """The facets of one shell made to agree: triangles turned alike, 2D edges chained into a loop."""
    facets = np.asarray(facets, dtype=np.int64)
    if facets.shape[1] == 3:
        return _oriented(facets[shell])
    loop = _chain(facets[shell])
    return np.column_stack([loop, np.roll(loop, -1)])


def encloses(V, facets, shell, point):
    """True when the closed shell (indexes into facets) goes around point."""
    return abs(wraps(V, _directed(facets, shell), point)) > 0.5


def nest(V, facets, shells):
    """Which shells bound which regions. shells: as returned by shells(facets). Returns [(outer, [inner, ...])], in
    shell numbers: a shell at even depth is the outer boundary of a region, one at odd depth a hole of its parent."""
    V = np.asarray(V, dtype=float)
    rings = [_directed(facets, s) for s in shells]
    points = [V[ring[0]].mean(axis=0) for ring in rings]
    count = len(rings)
    around = [[j for j in range(count) if j != i and abs(wraps(V, rings[j], points[i])) > 0.5] for i in range(count)]
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


def _size_field(rules, points):
    """Grade the size of the current gmsh model from the size rules (see mesh_region), as its background field.
    points: the tags of the model points added at each rule's points, in order; rules without points are left out."""
    import gmsh

    field = gmsh.model.mesh.field
    thresholds = []
    for rule, tags in zip(rules, points):
        distance = field.add("Distance")
        field.setNumbers(distance, "PointsList", tags)
        threshold = field.add("Threshold")
        field.setNumber(threshold, "InField", distance)
        field.setNumber(threshold, "SizeMin", rule["fine"])
        field.setNumber(threshold, "SizeMax", rule["coarse"])
        field.setNumber(threshold, "DistMin", rule["fine_distance"])
        field.setNumber(threshold, "DistMax", rule["fine_distance"] + rule["growth"])
        field.setNumber(threshold, "StopAtDistMax", 1)
        thresholds.append(threshold)
    if len(thresholds) > 1:
        joined = field.add("Min")
        field.setNumbers(joined, "FieldsList", thresholds)
        thresholds = [joined]
    if thresholds:
        field.setAsBackgroundMesh(thresholds[0])


def _region_3d(V, facets, rings, rules):
    """In the current, empty gmsh model: mesh the volume bounded by the triangles of the shells rings, the outer shell
    first, graded by the size rules (with points). The nodes' gmsh tags are their indexes in V + 1."""
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
    tag = max([t for _, t in gmsh.model.getEntities(0)], default=0)  # clear of the discrete points
    points = []
    for rule in rules:
        points.append(list(range(tag + 1, tag + 1 + len(rule["points"]))))
        for t, p in zip(points[-1], rule["points"].tolist()):
            gmsh.model.geo.addPoint(*p, tag=t)
        tag += len(rule["points"])
    gmsh.model.geo.synchronize()
    _size_field(rules, points)
    gmsh.model.mesh.generate(3)


def _region_2d(V, facets, rings, rules):
    """In the current, empty gmsh model: mesh the plane surface bounded by the polygons of the shells rings, the outer
    one first, through the nodes' real coordinates, each polygon line one element, graded by the size rules (with
    points)."""
    import gmsh

    occ = gmsh.model.occ
    loops, lines = [], []
    for shell in rings:
        points = [occ.addPoint(*V[n].tolist()) for n in _chain(facets[shell]).tolist()]
        ring = [occ.addLine(p, q) for p, q in zip(points, points[1:] + points[:1])]
        loops.append(occ.addCurveLoop(ring))
        lines += ring
    occ.addPlaneSurface(loops)
    points = [[occ.addPoint(*p) for p in rule["points"].tolist()] for rule in rules]
    occ.synchronize()
    for line in lines:
        gmsh.model.mesh.setTransfiniteCurve(line, 2)
    _size_field(rules, points)
    gmsh.model.mesh.generate(2)


def mesh_region(V, facets, outer, inners, size, dim, rules=()):
    """Mesh the region bounded by the shell outer (indexes into facets, whose node numbers refer to V), minus the
    shells inners. Returns (V2, {etype: connectivity}): V with the new nodes the elements use appended, nodes 0 to
    len(V) - 1 unchanged, connectivity into V2. A frozen node moved by gmsh raises FrozenError. The current gmsh model
    stays as it was.
    rules: size rules, each {"points": (n, 3), "fine", "fine_distance", "coarse", "growth"}: the size is fine within
    fine_distance of the points and grows to coarse over growth beyond it. Rules without points are left out."""
    import gmsh

    V = np.asarray(V, dtype=float).reshape(-1, 3)
    facets = np.asarray(facets, dtype=np.int64)
    rings = [np.asarray(outer, dtype=np.int64)] + [np.asarray(s, dtype=np.int64) for s in inners]
    used = np.unique(facets[np.concatenate(rings)])
    rules = [dict(r, points=np.asarray(r["points"], dtype=float).reshape(-1, 3)) for r in rules]
    rules = [r for r in rules if len(r["points"])]
    options = {"Mesh.Renumber": 0, "Mesh.MeshSizeMax": size, "Mesh.MeshSizeExtendFromBoundary": 1, "Mesh.Optimize": 1}
    if dim == 3:
        options["Mesh.Algorithm3D"] = 1
    current = gmsh.model.getCurrent()
    gmsh.model.add("region")
    try:
        with _options(options):
            (_region_3d if dim == 3 else _region_2d)(V, facets, rings, rules)
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
    meshed = np.zeros(len(index), dtype=bool)  # the rules' points come back as nodes no element uses
    for a in found.values():
        meshed[np.concatenate(a).ravel()] = True
    fresh = np.flatnonzero(~kept & meshed[tags])
    fresh = fresh[np.argsort(tags[fresh], kind="stable")]
    index[tags[fresh]] = len(V) + np.arange(len(fresh))
    return np.vstack([V, xyz[fresh]]), {t: index[np.vstack(a)] for t, a in found.items()}
