"""Swept Body: mesh the cross-section of a swept solid in 2D and sweep it into hexahedra and prisms. Runs in the
mesher process; never import FreeCAD here."""

import math
import os
from collections import namedtuple

import gmsh
import numpy as np

from meshcommon import JobError, apply_size_fields, apply_refinements, skin_refinements, apply_quad_layers, _smooth
from meshcommon import _note, import_brep, mesh_with_fallback, real_boundary, air_items
from meshfrozen import FLIP, _options

RATIO = 1.2  # the growth of a skin's steps away from the surface
SIZE_OPTIONS = ("Mesh.MeshSizeExtendFromBoundary", "Mesh.MeshSizeFromPoints", "Mesh.MeshSizeFromCurvature")
JACOBIAN = {5: (1, 3, 4), 6: (1, 2, 3)}  # the nodes whose edges from node 0 make a positive triple product

# xyz: the section's nodes in global coordinates (n x 3); tri (t x 3) and quad (q x 4): its elements as node indexes;
# edges: {curve key: ordered node indexes} per profile curve, the key being the curve's index in gmsh.model.getBoundary
# order of the profile face, the nodes in the curve's own direction (a closed curve repeats its first node at the end)
Section = namedtuple("Section", "xyz tri quad edges")


def graded_positions(length, size, first=None, depth=0.0, ratio=RATIO, ends=(True, True)):
    """Node positions from 0 to length, increasing. Without first: equal steps of about size. With first, at each
    end in ends: steps first * ratio^k (each at most size) until they reach depth, the one that crosses it kept; the
    middle in equal steps of at most size. A middle under half the largest graded step beside it is left out: each
    graded end then fills its share of the length (half of it, or all with one graded end) with the first of its steps
    whose sum is nearest that share, scaled to fill it, so the first step stays near first and no sliver is left."""
    if first is None:
        return np.linspace(0.0, length, max(1, round(length / size)) + 1)
    graded = []
    for end in ends:
        layer = []
        while end and sum(layer) < depth:
            layer.append(min(first * ratio ** len(layer), size))
        graded.append(layer)
    middle = length - sum(graded[0]) - sum(graded[1])
    beside = max([layer[-1] for layer in graded if layer], default=0.0)
    if middle >= 0.5 * beside and middle > 1e-9 * length:
        n = max(1, math.ceil(middle / size - 1e-9))  # ceil, so no step exceeds size
        steps = [middle / n] * n
    else:  # the layers meet: no middle
        steps = []
        share = length / sum(1 for layer in graded if layer)
        for layer in graded:
            if layer:
                sums = np.cumsum(layer)
                k = int(np.argmin(np.abs(np.log(sums / share)))) + 1  # the prefix nearest the share
                layer[:] = [s * share / sums[k - 1] for s in layer[:k]]
    d = np.array(graded[0] + steps + graded[1][::-1])
    p = np.concatenate([[0.0], np.cumsum(d)])
    p[-1] = length
    return p


def _ends_of(curve):
    """The start and end points of a curve in its own direction."""
    lo, hi = (b[0] for b in gmsh.model.getParametrizationBounds(1, curve))
    return lo, hi, np.array(gmsh.model.getValue(1, curve, [lo])), np.array(gmsh.model.getValue(1, curve, [hi]))


def _structured(face, curves, real, entry):
    """Four straight curves: transfinite curves graded toward the real neighbouring sides, a recombined transfinite
    surface. Meshes the curves (generate(1)) and puts their nodes at the graded positions."""
    skin, size = entry["skin"], float(entry["section_size"])
    first, depth = skin["depth"] / skin["per_depth"], skin["layer"] * skin["depth"]
    info = {c: _ends_of(c) for c in curves}
    length = {c: float(np.linalg.norm(b - a)) for c, (_, _, a, b) in info.items()}
    tol = 1e-6 * max(1.0, *length.values())

    def real_at(c, where):  # the other curve that ends at where is real
        return any(
            o in real and min(np.linalg.norm(where - info[o][2]), np.linalg.norm(where - info[o][3])) < tol
            for o in curves
            if o != c
        )

    positions = {}
    for k, c in enumerate(curves):
        mean = (length[c] + length[curves[(k + 2) % 4]]) / 2  # opposite sides need the same node count
        ends = (real_at(c, info[c][2]), real_at(c, info[c][3]))
        positions[c] = graded_positions(mean, size, first, depth, RATIO, ends) * (length[c] / mean)
    for c in curves:
        gmsh.model.mesh.setTransfiniteCurve(c, len(positions[c]))
    gmsh.model.mesh.setTransfiniteSurface(face)
    gmsh.model.mesh.setRecombine(2, face)
    gmsh.model.mesh.generate(1)
    for c in curves:
        lo, hi, _, _ = info[c]
        tags, _, params = gmsh.model.mesh.getNodes(1, c)
        order = np.argsort(params)
        for tag, t in zip(np.asarray(tags)[order], positions[c][1:-1]):
            u = lo + (hi - lo) * t / length[c]
            gmsh.model.mesh.setNode(int(tag), gmsh.model.getValue(1, c, [u]), [u])


def _graded(face, real, entry, quads):
    """The 2D Skin Layer on the real curves: graded fields, plus BoundaryLayer quad layers when quads."""
    skin, m = entry["skin"], entry["mat_id"]
    skins = [{"name": entry["name"], "mat_ids": [m], "quads": quads, **skin}]
    picks = skin_refinements(skins, {m: float(entry["section_size"])}, {(0, m): {1: real}})
    apply_refinements(picks, {m: [face]}, 2)
    if quads:
        apply_quad_layers(skins, {m: [face]}, (), {(0, m): {1: real}})


def _read(face, curves):
    """The section model's mesh as a Section."""
    tags, xyz, _ = gmsh.model.mesh.getNodes()
    index = {int(t): i for i, t in enumerate(tags)}
    cells = {3: [], 4: []}
    for etype, _, conn in zip(*gmsh.model.mesh.getElements(2, face)):
        k = {2: 3, 3: 4}[int(etype)]
        cells[k].append(np.array([index[int(t)] for t in conn], int).reshape(-1, k))
    tri, quad = (np.vstack(cells[k]) if cells[k] else np.zeros((0, k), int) for k in (3, 4))
    edges = {}
    for key, c in enumerate(curves):
        lines = np.concatenate(gmsh.model.mesh.getElements(1, c)[2]).astype(int).reshape(-1, 2)  # in curve order
        edges[key] = [index[int(t)] for t in lines[:, 0]] + [index[int(lines[-1, 1])]]
    return Section(np.asarray(xyz, float).reshape(-1, 3), tri, quad, edges)


def section_mesh(entry, solid_index, real_curves, folder):
    """Mesh the profile of entry["solids"][solid_index] in a model of its own, removed afterwards; the current
    (main) model stays current. real_curves: the indexes (in getBoundary order of the profile face) of the profile
    curves whose side faces are real surface; the others are cuts and get no skin."""
    main = gmsh.model.getCurrent()
    name, m = entry["name"], entry["mat_id"]
    gmsh.model.add(f"swept section {name} {solid_index}")
    try:
        path = os.path.join(folder, entry["solids"][solid_index]["profile"])
        faces = import_brep(path, 2)
        gmsh.model.occ.synchronize()
        if len(faces) != 1:
            raise JobError(f"Swept Body {name}: {os.path.basename(path)} holds {len(faces)} faces, not one")
        face = faces[0][1]
        curves = [abs(t) for _, t in gmsh.model.getBoundary([(2, face)], oriented=False)]
        real = [curves[k] for k in real_curves]
        size = float(entry["section_size"])
        # apply_size_fields sets options, which hold for every model: the main model gets its own back
        with _options({o: gmsh.option.getNumber(o) for o in SIZE_OPTIONS}):
            apply_size_fields({size: {2: [face]}})
            if entry["skin"] and real:
                skin = entry["skin"]
                if len(curves) == 4 and all(gmsh.model.getType(1, c) == "Line" for c in curves):
                    _structured(face, curves, set(real), entry)
                elif _smooth(real, skin["layer"] * skin["depth"]):
                    _graded(face, real, entry, True)
                else:
                    _graded(face, real, entry, False)
                    if not entry["recombine"]:
                        _note(
                            f"Swept Body {name}: the cross-section of MAT_ID {m} has sharp corners and is not"
                            " four-sided; graded triangles, so prisms"
                        )
            if entry["recombine"]:  # every branch: Recombine on a swept body gives hexahedra only
                gmsh.model.mesh.setRecombine(2, face)
            mesh_with_fallback(2)
        return _read(face, curves)
    finally:
        gmsh.model.remove()
        gmsh.model.setCurrent(main)


def stations(piece, positions):
    """One 4 x 4 transform per position along the piece: a translation by position * axis (a straight sweep)."""
    if piece.get("angle", 0.0):
        raise JobError("only straight sweeps are made so far")
    axis = np.asarray(piece["axis"], float)
    out = []
    for p in positions:
        t = np.eye(4)
        t[:3, 3] = float(p) * axis
        out.append(t)
    return out


def _volume(V, cells, etype):
    """The triple product of the edges at the first node of each cell (positive: gmsh's orientation)."""
    a, b, c = (V[cells[:, k]] - V[cells[:, 0]] for k in JACOBIAN[etype])
    return np.einsum("ij,ij->i", np.cross(a, b), c)


def sweep(section, transforms, closed=False):
    """Copy the section to each station (transforms: 4 x 4) and join station j to j + 1: quads become hexahedra,
    triangles prisms, in gmsh node order. closed: a ring, the last station joined to the first. Returns the nodes
    (n x 3, station by station) and {5: hexahedra, 6: prisms}, both positively oriented."""
    xyz = np.asarray(section.xyz, float)
    n = len(xyz)
    V = np.vstack([xyz @ np.asarray(t)[:3, :3].T + np.asarray(t)[:3, 3] for t in transforms])
    layers = len(transforms) if closed else len(transforms) - 1
    cells = {}
    for etype, base in (
        (5, np.asarray(section.quad, int).reshape(-1, 4)),
        (6, np.asarray(section.tri, int).reshape(-1, 3)),
    ):
        joined = [np.hstack([base + j * n, base + (j + 1) % len(transforms) * n]) for j in range(layers)]
        c = np.vstack(joined) if joined and len(base) else np.zeros((0, 2 * base.shape[1]), int)
        if len(c) and _volume(V, c[:1], etype)[0] < 0:
            c = c[:, FLIP[etype]]
        cells[etype] = c
    return V, cells


TOL = 2.5e-5  # how far a node may lie from its point, curve or face, times the body's size (spike 7.1)
HEX_QUADS = ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7))
PRISM_TRIS = ((0, 2, 1), (3, 4, 5))
PRISM_QUADS = ((0, 1, 4, 3), (1, 2, 5, 4), (2, 0, 3, 5))


def _profile(path, name):
    """The profile face's bounding box (2 x 3) and the midpoint of each of its curves, in the getBoundary order
    section_mesh uses, read in a model of its own."""
    main = gmsh.model.getCurrent()
    gmsh.model.add(f"swept profile {name}")
    try:
        faces = import_brep(path, 2)
        gmsh.model.occ.synchronize()
        if len(faces) != 1:
            raise JobError(f"Swept Body {name}: {os.path.basename(path)} holds {len(faces)} faces, not one")
        face = faces[0][1]
        mids = []
        for _, c in gmsh.model.getBoundary([(2, face)], oriented=False):
            lo, hi = (b[0] for b in gmsh.model.getParametrizationBounds(1, abs(c)))
            mids.append(gmsh.model.getValue(1, abs(c), [(lo + hi) / 2]))
        box = np.reshape(gmsh.model.getBoundingBox(2, face), (2, 3))
    finally:
        gmsh.model.remove()
        gmsh.model.setCurrent(main)
    return box, np.array(mids, float).reshape(-1, 3)


def _nearest(dim, tags, points, tol):
    """For each point: the nearest of the dim-entities tags, the distance, the point on it and its parameters. Of two
    entities about as near (coplanar faces, collinear curves), the one whose bounding box holds the point."""
    pts = np.asarray(points, float).reshape(-1, 3)
    best, rank = np.full(len(pts), np.inf), np.full(len(pts), np.inf)
    tag, xyz, par = np.zeros(len(pts), int), pts.copy(), np.zeros((len(pts), 2))
    for t in tags:
        if dim == 0:
            x, u = np.tile(gmsh.model.getValue(0, t, []), (len(pts), 1)), np.zeros((len(pts), 0))
        else:
            x = np.reshape(gmsh.model.getClosestPoint(dim, t, pts.ravel().tolist())[0], (-1, 3))
            # getClosestPoint's parameters are garbage on OCC curves (gmsh 4.15): ask for them at the point found
            u = np.reshape(gmsh.model.getParametrization(dim, t, x.ravel().tolist()), (-1, dim))
        d = np.linalg.norm(x - pts, axis=1)
        box = np.reshape(gmsh.model.getBoundingBox(dim, t), (2, 3))
        inside = np.all((pts >= box[0] - tol) & (pts <= box[1] + tol), axis=1)
        r = np.maximum(d, tol) + np.where(inside, 0.0, 1e30)
        better = r < rank
        rank[better], best[better], tag[better], xyz[better] = r[better], d[better], t, x[better]
        par[better, :dim] = u[better]
    return tag, best, xyz, par


def _once(faces):
    """The faces (rows of node indexes) that only one cell has."""
    _, inverse, count = np.unique(np.sort(faces, axis=1), axis=0, return_inverse=True, return_counts=True)
    return faces[count[inverse.ravel()] == 1]


def _join(vol, V, cells, name):
    """Classify the swept mesh (V, cells from sweep) on vol and its faces, curves and points: each boundary node on
    the entity it lies on (projected onto it), each boundary face on a face, each boundary edge on a curve.
    Returns add(dim), which puts the nodes and elements of dimension dim into the model."""
    faces = [abs(t) for _, t in gmsh.model.getBoundary([(3, vol)], oriented=False)]
    curves = list(dict.fromkeys(abs(t) for _, t in gmsh.model.getBoundary([(2, f) for f in faces], False, False)))
    points = list(dict.fromkeys(abs(t) for _, t in gmsh.model.getBoundary([(1, c) for c in curves], False, False)))
    tol = TOL * float(np.linalg.norm(V.max(axis=0) - V.min(axis=0)))
    hexes, prisms = cells[5], cells[6]
    quads = _once(np.vstack([hexes[:, f] for f in HEX_QUADS] + [prisms[:, f] for f in PRISM_QUADS]))
    tris = _once(np.vstack([prisms[:, f] for f in PRISM_TRIS]))
    dim, tag = np.full(len(V), 3), np.full(len(V), vol)
    X, U = V.copy(), np.zeros((len(V), 2))
    rest = np.unique(np.concatenate([quads.ravel(), tris.ravel()]))
    for d, ents in ((0, points), (1, curves), (2, faces)):
        t, dist, x, u = _nearest(d, ents, V[rest], tol)
        on = dist < tol
        if d == 2 and not on.all():
            off = float(dist.max())
            raise JobError(f"Swept Body {name}: its swept mesh does not fit the body ({off:.3g} mm off its surface)")
        idx = rest[on]
        dim[idx], tag[idx], X[idx], U[idx] = d, t[on], x[on], u[on]
        rest = rest[~on]
    missing = set(points) - set(tag[dim == 0].tolist())
    if missing:
        at = _at(0, min(missing))
        raise JobError(f"Swept Body {name}: its swept mesh has no node on the corner at {at}")

    def surface_of(f):  # the face of its nodes on a face, else the face nearest its centre
        on = dim[f] == 2
        out = tag[f[np.arange(len(f)), np.argmax(on, axis=1)]]
        none = ~on.any(axis=1)
        if none.any():
            out[none] = _nearest(2, faces, X[f[none]].mean(axis=1), tol)[0]
        return out

    def along_normal(f, where):  # turned as the faces they lie on, as gmsh meshes a face
        f = f.copy()
        for t in np.unique(where):
            rows = np.where(where == t)[0]
            p = X[f[rows]]
            uv = gmsh.model.getParametrization(2, int(t), p.mean(axis=1).ravel().tolist())
            n = np.reshape(gmsh.model.getNormal(int(t), uv), (-1, 3))
            turned = np.einsum("ij,ij->i", np.cross(p[:, 1] - p[:, 0], p[:, 2] - p[:, 0]), n) < 0
            f[rows[turned]] = f[rows[turned]][:, ::-1]
        return f

    on_face = {k: (along_normal(f, w), w) for k, f in ((4, quads), (3, tris)) for w in [surface_of(f)]}
    sides = [np.stack([f[:, k], f[:, (k + 1) % f.shape[1]]], axis=1) for f in (quads, tris) for k in range(f.shape[1])]
    edges = np.unique(np.sort(np.vstack(sides), axis=1), axis=0)
    edges = edges[(dim[edges] <= 1).all(axis=1)]
    line = np.zeros(len(edges), int)  # the curve each edge lies on, 0 for none
    for c in curves:
        ends = (dim[edges] == 0) | ((dim[edges] == 1) & (tag[edges] == c))
        cand = np.where((line == 0) & ends.all(axis=1))[0]
        if not len(cand):
            continue
        e = edges[cand]
        a, b = X[e[:, 0]], X[e[:, 1]]
        good = _nearest(1, [c], (a + b) / 2, tol)[1] < tol + 0.15 * np.linalg.norm(b - a, axis=1)  # an arc's chord
        for k in (0, 1):  # a node on a point: the point must be on the curve
            p = dim[e[:, k]] == 0
            if p.any():
                good[p] &= _nearest(1, [c], X[e[p, k]], tol)[1] < tol
        line[cand[good]] = c
    chain = {c: _along(c, edges[line == c], dim, U, X, tol) for c in curves}
    used = np.concatenate([where for _, where in on_face.values()])
    for d, ents, on in ((1, curves, line), (2, faces, used)):
        bare = [t for t in ents if t not in set(on.tolist())]
        if bare:
            kind = "edge" if d == 1 else "face"
            raise JobError(f"Swept Body {name}: its swept mesh misses the {kind} at {_at(d, bare[0])}")
    node = np.zeros(len(V), np.int64)

    def add(d):
        start = int(gmsh.model.mesh.getMaxNodeTag()) + 1  # Mesh.Renumber is off: gmsh numbers on from the max
        element = [int(gmsh.model.mesh.getMaxElementTag()) + 1]
        for t in {0: points, 1: curves, 2: faces, 3: [vol]}[d]:
            idx = np.where((dim == d) & (tag == t))[0]
            if d == 1:  # in the curve's direction, as gmsh's own 1D mesh
                idx = idx[np.argsort(U[idx, 0])]
            node[idx] = np.arange(start, start + len(idx))
            start += len(idx)
            par = U[idx, :d].ravel().tolist() if d in (1, 2) else []
            gmsh.model.mesh.addNodes(d, t, node[idx].tolist(), X[idx].ravel().tolist(), par)

        def put(t, etype, conn):
            if len(conn):
                n = len(conn)
                tags = list(range(element[0], element[0] + n))
                gmsh.model.mesh.addElementsByType(t, etype, tags, node[conn].ravel().tolist())
                element[0] += n

        if d == 0:
            for p in points:
                put(p, 15, np.where((dim == 0) & (tag == p))[0][:1].reshape(-1, 1))
        elif d == 1:
            for c in curves:
                put(c, 1, chain[c])
        elif d == 2:
            for f in faces:
                for conn, where in on_face.values():
                    put(f, 3 if conn.shape[1] == 4 else 2, conn[where == f])
        else:
            put(vol, 5, hexes)
            put(vol, 6, prisms)

    return add


def _along(c, lines, dim, U, X, tol):
    """The lines on curve c in its direction, each from its lower to its higher parameter: gmsh meshes a face from
    its curves' lines in that order. A node on a point takes the parameter of the curve's end there (the nearer one
    to the line's other node on a closed curve)."""
    lo, hi = (b[0] for b in gmsh.model.getParametrizationBounds(1, c))
    ends = [(u, np.array(gmsh.model.getValue(1, c, [u]))) for u in (lo, hi)]
    u = np.where(dim[lines] == 1, U[lines, 0], np.nan)
    for i, k in zip(*np.where(dim[lines] == 0)):
        near = [v for v, at in ends if np.linalg.norm(at - X[lines[i, k]]) < tol] or [lo, hi]
        other = u[i, 1 - k] if not np.isnan(u[i, 1 - k]) else (lo, hi)[k]
        u[i, k] = min(near, key=lambda v: abs(v - other))
    lines = np.where((u[:, 0] > u[:, 1])[:, None], lines[:, ::-1], lines)
    return lines[np.argsort(np.minimum(u[:, 0], u[:, 1]))]


def _at(dim, tag):
    """The lowest corner of an entity's bounding box, for messages."""
    return "(" + ", ".join(f"{c:g}" for c in gmsh.model.getBoundingBox(dim, tag)[:3]) + ")"


def _volume_of(tags, box, shift, name):
    """Of the volumes tags, the one whose bounding box is the profile's (box) swept by shift."""
    if not tags:
        raise JobError(f"Swept Body {name}: it has more solids than volumes in the model")
    lo, hi = np.minimum(box[0], box[0] + shift), np.maximum(box[1], box[1] + shift)
    off = [np.abs(np.reshape(gmsh.model.getBoundingBox(3, t), (2, 3)) - [lo, hi]).max() for t in tags]
    return tags[int(np.argmin(off))]


def _graded_end(face, vol, air):
    """True when the end face is real surface against the air only: not a cut and not on another body (a terminal)."""
    others = [v for v in gmsh.model.getAdjacencies(2, face)[0] if v != vol]
    return bool(others) and all(v in air for v in others)


def _transforms(entry, section, pieces, faces, vol, air, tol):
    """The stations along the solid's pieces: every path size, graded toward a real end face when there is a skin."""
    skin, size = entry["skin"], float(entry["path_size"])
    shift = sum(float(p["advance"]) * np.asarray(p["axis"], float) for p in pieces)
    first = section.quad[0] if len(section.quad) else section.tri[0]
    centre = section.xyz[first].mean(axis=0)
    start, end = _nearest(2, faces, [centre, centre + shift], tol)[0]
    graded = (_graded_end(start, vol, air), _graded_end(end, vol, air))
    out, offset = [], np.zeros(3)
    for i, piece in enumerate(pieces):
        length = float(piece["advance"])
        ends = (graded[0] and i == 0, graded[1] and i == len(pieces) - 1)
        if skin and any(ends):
            first, depth = skin["depth"] / skin["per_depth"], skin["layer"] * skin["depth"]
            positions = graded_positions(length, size, first, depth, RATIO, ends)
        else:
            positions = graded_positions(length, size)
        steps = stations(piece, positions)
        for t in steps:
            t[:3, 3] += offset
        out += steps if i == 0 else steps[1:]  # pieces join at shared stations
        offset = offset + length * np.asarray(piece["axis"], float)
    return out


def apply_swept(job, folder, body_vols):
    """The swept mesh of every solid of job["swept"], at the end of build: each solid's volume (body_vols: {MAT_ID:
    final tags}), its section meshed with the skin on the profile curves whose side faces are real surface, swept along
    its pieces and classified on the volume's entities. job["swept_tags"] gets the volumes and job["swept_add"] one
    add(dim) per volume, for meshcommon.generate. Returns the volumes."""
    air = {t for a in air_items(job) for t in body_vols.get(a["mat_id"], [])}
    tags, adds = [], []
    for entry in job.get("swept", []):
        left = list(body_vols[entry["mat_id"]])
        for k, solid in enumerate(entry["solids"]):
            box, mids = _profile(os.path.join(folder, solid["profile"]), entry["name"])
            pieces = solid["pieces"]
            shift = sum(float(p["advance"]) * np.asarray(p["axis"], float) for p in pieces)
            vol = _volume_of(left, box, shift, entry["name"])
            left.remove(vol)
            faces = [abs(t) for _, t in gmsh.model.getBoundary([(3, vol)], oriented=False)]
            tol = TOL * float(np.linalg.norm(box[1] - box[0] + np.abs(shift)))
            real = set(real_boundary(3, [vol]))
            along = 0.5 * float(pieces[0]["advance"]) * np.asarray(pieces[0]["axis"], float)
            side = _nearest(2, faces, mids + along, tol)[0]  # the side face of each profile curve
            section = section_mesh(entry, k, [i for i, f in enumerate(side) if f in real], folder)
            V, cells = sweep(section, _transforms(entry, section, pieces, faces, vol, air, tol))
            adds.append(_join(vol, V, cells, entry["name"]))
            tags.append(vol)
    job["swept_tags"], job["swept_add"] = tags, adds
    return tags
