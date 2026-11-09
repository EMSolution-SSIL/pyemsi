"""Array operations on frozen meshes for the mesher process: read, copy with transforms, join nodes, find the
boundary, close quads with pyramids. numpy only (plus gmsh in read_model); never imports FreeCAD."""

from collections import namedtuple

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
