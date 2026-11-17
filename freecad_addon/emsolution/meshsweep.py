"""Swept Body: mesh the cross-section of a swept solid in 2D and sweep it into hexahedra and prisms. Runs in the
mesher process; never import FreeCAD here."""

import math
import os
from collections import namedtuple

import gmsh
import numpy as np

from meshcommon import JobError, apply_size_fields, apply_refinements, skin_refinements, apply_quad_layers, _smooth
from meshcommon import _note, import_brep, mesh_with_fallback, real_boundary
from meshfrozen import FLIP, _options

RATIO = 1.2  # the growth of a skin's steps away from the surface
SIZE_OPTIONS = ("Mesh.MeshSizeExtendFromBoundary", "Mesh.MeshSizeFromPoints", "Mesh.MeshSizeFromCurvature")
SECTION_OPTIONS = ("Mesh.Algorithm", "Mesh.Smoothing", "Mesh.RecombinationAlgorithm")  # the user's, for the section
JACOBIAN = {5: (1, 3, 4), 6: (1, 2, 3)}  # the nodes whose edges from node 0 make a positive triple product
NOT_STRAIGHT = "only straight and revolved sweeps are made so far"  # as sweeps.NOT_STRAIGHT
MIN_TURN = 30.0  # degrees: the largest turn of one step of a revolved piece

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


def turned_positions(length, angle, size, cuts=(), first=None, depth=0.0, ends=(False, False)):
    """The positions (arc lengths, 0 to length) along a turned piece of angle degrees: as graded_positions, with a
    position at each of cuts (arc lengths inside the piece, where the body has a corner) and the parts between them
    spaced alike, graded at the piece's ends in ends (with first). At least ceil(angle / MIN_TURN) steps, so no cell is
    flat: a coarse ring still has 12, a 90 degree bend 3."""
    need = max(1, math.ceil(angle / MIN_TURN - 1e-9))
    tol = 1e-9 * length
    marks = [0.0]
    for c in sorted(float(c) for c in cuts):
        if tol < c < length - tol and c - marks[-1] > tol:
            marks.append(c)
    marks.append(length)
    step = min(size, length / need)
    for _ in range(200):  # each try with smaller steps
        out = [np.zeros(1)]
        for k, (a, b) in enumerate(zip(marks, marks[1:])):
            graded = (ends[0] and k == 0, ends[1] and k == len(marks) - 2)
            if first is not None and any(graded):
                p = graded_positions(b - a, step, first, depth, RATIO, graded)
            else:
                p = graded_positions(b - a, step)
            out.append(a + p[1:])
        out = np.concatenate(out)
        out[-1] = length
        if len(out) - 1 >= need:
            return out
        step *= 0.9
    raise JobError(f"a turn of {angle:g} degrees could not be split into {need} steps")


def _ends_of(curve):
    """The start and end points of a curve in its own direction."""
    lo, hi = (b[0] for b in gmsh.model.getParametrizationBounds(1, curve))
    return lo, hi, np.array(gmsh.model.getValue(1, curve, [lo])), np.array(gmsh.model.getValue(1, curve, [hi]))


def _structured(face, curves, real, entry):
    """Four straight curves: transfinite curves graded toward the real neighbouring sides (with a skin), else in equal
    steps of about the section size, a recombined transfinite surface. Meshes the curves (generate(1)) and puts their
    nodes at the graded positions."""
    skin, size = entry["skin"], float(entry["section_size"])
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
        if skin and any(ends):
            first, depth = skin["depth"] / skin["per_depth"], skin["layer"] * skin["depth"]
            positions[c] = graded_positions(mean, size, first, depth, RATIO, ends) * (length[c] / mean)
        else:
            positions[c] = graded_positions(mean, size) * (length[c] / mean)
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


def scaled(entry, options):
    """The entry with its path and section sizes as the user's global mesh settings (options: job["options"]) make
    them: times Mesh.MeshSizeFactor, clamped to Mesh.MeshSizeMin and Mesh.MeshSizeMax when those are set (> 0). The
    skin's steps are physical sizes and stay."""
    factor = float(options.get("Mesh.MeshSizeFactor", 1.0))
    lo, hi = float(options.get("Mesh.MeshSizeMin", 0.0)), float(options.get("Mesh.MeshSizeMax", 0.0))

    def size(s):
        s = float(s) * factor
        if hi > 0:
            s = min(s, hi)
        return max(s, lo) if lo > 0 else s

    return {**entry, "path_size": size(entry["path_size"]), "section_size": size(entry["section_size"])}


def section_mesh(entry, solid_index, real_curves, folder, options=None, points=()):
    """Mesh the profile of entry["solids"][solid_index] in a model of its own, removed afterwards; the current
    (main) model stays current. real_curves: the indexes (in getBoundary order of the profile face, split at points)
    of the profile curves whose side faces are real surface; the others are cuts and get no skin. options: the user's
    mesh settings (job["options"]), of which the 2D ones (SECTION_OPTIONS) hold while the section is meshed. points:
    where the profile's curves are split (from _profile), so the section has a node there."""
    main = gmsh.model.getCurrent()
    name, m = entry["name"], entry["mat_id"]
    gmsh.model.add(f"swept section {name} {solid_index}")
    try:
        path = os.path.join(folder, entry["solids"][solid_index]["profile"])
        faces = import_brep(path, 2)
        gmsh.model.occ.synchronize()
        if len(faces) != 1:
            raise JobError(f"Swept Body {name}: {os.path.basename(path)} holds {len(faces)} faces, not one")
        face = _split(faces[0][1], points)
        curves = [abs(t) for _, t in gmsh.model.getBoundary([(2, face)], oriented=False)]
        real = [curves[k] for k in real_curves]
        size = float(entry["section_size"])
        # apply_size_fields sets options, which hold for every model: the main model gets its own back
        user = {o: v for o, v in (options or {}).items() if o in SECTION_OPTIONS}
        with _options({**{o: gmsh.option.getNumber(o) for o in SIZE_OPTIONS}, **user}):
            apply_size_fields({size: {2: [face]}})
            four = len(curves) == 4 and all(gmsh.model.getType(1, c) == "Line" for c in curves)
            if four:  # a busbar or plate: a grid, with or without a skin
                _structured(face, curves, set(real) if entry["skin"] else set(), entry)
            elif entry["skin"] and real:
                skin = entry["skin"]
                if _smooth(real, skin["layer"] * skin["depth"]):
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


def stations(piece, positions, rc=None):
    """One 4 x 4 transform per position along the piece. A straight piece: a translation by position * axis. A
    revolved one (advance 0): positions are arc lengths at rc, each the rotation about (origin, axis) by position / rc
    radians, positive by the right-hand rule. A helical piece (angle and advance) is refused."""
    angle, advance = float(piece.get("angle", 0.0)), float(piece["advance"])
    if angle and advance:
        raise JobError(NOT_STRAIGHT)
    out = []
    if not angle:
        axis = np.asarray(piece["axis"], float)
        for p in positions:
            t = np.eye(4)
            t[:3, 3] = float(p) * axis
            out.append(t)
        return out
    axis = np.asarray(piece["axis"], float)
    axis = axis / np.linalg.norm(axis)
    origin = np.asarray(piece["origin"], float)
    k = np.array([[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]])
    for p in positions:
        a = float(p) / rc
        r = np.eye(3) + math.sin(a) * k + (1 - math.cos(a)) * (k @ k)  # Rodrigues
        t = np.eye(4)
        t[:3, :3], t[:3, 3] = r, origin - r @ origin
        out.append(t)
    return out


def _chain(pieces, centre):
    """Per piece: (piece, rc, length, start). rc: for a revolved piece the distance from its axis to the profile's
    centre of mass (centre) where the piece starts, else None; length: the piece's path length (at rc); start: the
    4 x 4 transform taking the profile to where the piece starts (each piece starts where the last ended)."""
    out, start = [], np.eye(4)
    for piece in pieces:
        rc, length = None, float(piece["advance"])
        if float(piece.get("angle", 0.0)):
            axis = np.asarray(piece["axis"], float)
            axis = axis / np.linalg.norm(axis)
            d = start[:3, :3] @ centre + start[:3, 3] - np.asarray(piece["origin"], float)
            rc = float(np.linalg.norm(d - axis * axis.dot(d)))
            length = rc * math.radians(float(piece["angle"]))
        out.append((piece, rc, length, start))
        start = stations(piece, [length], rc)[0] @ start
    return out


def _moved(points, t):
    """The points (n x 3) moved by the 4 x 4 transform t."""
    return np.asarray(points, float) @ t[:3, :3].T + t[:3, 3]


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
        if joined and len(base):
            # per section element, as its first cell turns (gmsh's quad layers and the rest may face either way);
            # a later layer turned inside out stays so, for _flat to find
            turned = _volume(V, joined[0], etype) < 0
            c = np.vstack([np.where(turned[:, None], j[:, FLIP[etype]], j) for j in joined])
        else:
            c = np.zeros((0, 2 * base.shape[1]), int)
        cells[etype] = c
    return V, cells


TOL = 2.5e-5  # how far a node may lie from its point, curve or face, times the body's size (spike 7.1)
HEX_QUADS = ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7))
PRISM_TRIS = ((0, 2, 1), (3, 4, 5))
PRISM_QUADS = ((0, 1, 4, 3), (1, 2, 5, 4), (2, 0, 3, 5))


def _profile(path, name, points=(), tol=0.0):
    """The profile face's bounding box (2 x 3), the midpoint of each of its curves, in the getBoundary order
    section_mesh uses, its centre of mass, its unit normal and, of points, those on its boundary within tol but not on
    a corner of it, read in a model of its own. The curves are split at those points (as section_mesh splits them)."""
    main = gmsh.model.getCurrent()
    gmsh.model.add(f"swept profile {name}")
    try:
        faces = import_brep(path, 2)
        gmsh.model.occ.synchronize()
        if len(faces) != 1:
            raise JobError(f"Swept Body {name}: {os.path.basename(path)} holds {len(faces)} faces, not one")
        face = faces[0][1]
        kept = []
        if len(points):
            curves = [abs(t) for _, t in gmsh.model.getBoundary([(2, face)], oriented=False)]
            corners = [
                gmsh.model.getValue(0, t, []) for _, t in gmsh.model.getBoundary([(2, face)], False, False, True)
            ]
            for q in np.asarray(points, float).reshape(-1, 3):
                near = _nearest(1, curves, [q], tol)[1][0] < tol
                if near and all(np.linalg.norm(q - np.asarray(x)) >= tol for x in corners + kept):
                    kept.append(q)
            face = _split(face, kept)
        mids = []
        for _, c in gmsh.model.getBoundary([(2, face)], oriented=False):
            lo, hi = (b[0] for b in gmsh.model.getParametrizationBounds(1, abs(c)))
            mids.append(gmsh.model.getValue(1, abs(c), [(lo + hi) / 2]))
        box = np.reshape(gmsh.model.getBoundingBox(2, face), (2, 3))
        centre = np.array(gmsh.model.occ.getCenterOfMass(2, face), float)
        normal = np.array(gmsh.model.getNormal(face, gmsh.model.getParametrization(2, face, centre.tolist())), float)
    finally:
        gmsh.model.remove()
        gmsh.model.setCurrent(main)
    return box, np.array(mids, float).reshape(-1, 3), centre, normal / np.linalg.norm(normal), kept


def _split(face, points):
    """The profile face (current model) with its boundary curves split at points (on them, not on a corner), or the
    face itself without points."""
    if not len(points):
        return face
    occ = gmsh.model.occ
    out, _ = occ.fragment([(2, face)], [(0, occ.addPoint(*map(float, q))) for q in points])
    occ.synchronize()
    faces = [t for d, t in out if d == 2]
    if len(faces) != 1:
        raise JobError(f"splitting the swept profile at the body's edges gave {len(faces)} faces, not one")
    return faces[0]


def _crossings(vol, centre, normal, tol):
    """The points where the curves of vol that do not lie in the profile's plane (through centre, normal) meet it:
    where the section must have a node (a seam circle crossing a ring's profile), wherever its own corners are."""
    faces = [(2, abs(t)) for _, t in gmsh.model.getBoundary([(3, vol)], oriented=False)]
    curves = list(dict.fromkeys(abs(t) for _, t in gmsh.model.getBoundary(faces, False, False)))
    out = []
    for c in curves:
        lo, hi = (b[0] for b in gmsh.model.getParametrizationBounds(1, c))

        def at(v):
            return np.reshape(gmsh.model.getValue(1, c, list(np.atleast_1d(v))), (-1, 3))

        u = np.linspace(lo, hi, 129)
        d = (at(u) - centre) @ normal
        if (np.abs(d) < tol).all():  # in the plane: a curve of the profile itself
            continue
        out += list(at(u[np.abs(d) < tol]))
        for k in np.where((d[:-1] * d[1:] < 0) & (np.abs(d[:-1]) >= tol) & (np.abs(d[1:]) >= tol))[0]:
            a, b = u[k], u[k + 1]
            for _ in range(60):  # bisection on the distance to the plane
                m = 0.5 * (a + b)
                if ((at(m)[0] - centre) @ normal) * d[k] <= 0:
                    b = m
                else:
                    a = m
            out.append(at(0.5 * (a + b))[0])
    return np.array(out, float).reshape(-1, 3)


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


def _swept_box(box, chain):
    """The bounding box (2 x 3) of the profile swept along the pieces (chain, from _chain): of its box's corners (box:
    the profile's bounding box) at each end of a straight piece and every 10 degrees of a revolved one, plus its
    end."""
    corners = np.array([[box[i, 0], box[j, 1], box[k, 2]] for i in (0, 1) for j in (0, 1) for k in (0, 1)])
    swept = [corners]
    for piece, rc, length, start in chain:
        n = max(1, math.ceil(float(piece.get("angle", 0.0)) / 10 - 1e-9))
        swept += [_moved(corners, t @ start) for t in stations(piece, np.linspace(0, length, n + 1)[1:], rc)]
    swept = np.vstack(swept)
    return np.array([swept.min(axis=0), swept.max(axis=0)])


def _volume_of(tags, swept, name):
    """Of the volumes tags, the one whose bounding box is nearest swept (the profile's, from _swept_box)."""
    if not tags:
        raise JobError(f"Swept Body {name}: it has more solids than volumes in the model")
    off = [np.abs(np.reshape(gmsh.model.getBoundingBox(3, t), (2, 3)) - swept).max() for t in tags]
    return tags[int(np.argmin(off))]


def _graded_end(face, vol, skinned):
    """True when the end face is real surface (not a cut of the domain) that no body with a skin of its own (skinned:
    their volumes; a Skin Layer marks a conductor) shares: the air and an iron core are graded toward, a terminal with
    a skin is not."""
    others = [v for v in gmsh.model.getAdjacencies(2, face)[0] if v != vol]
    return bool(others) and not any(v in skinned for v in others)


def _transforms(entry, section, chain, closed, faces, vol, skinned, tol):
    """The stations along the solid's pieces (chain, from _chain): every path size (arc length at rc on a revolved
    piece, with a station at each of the volume's corners on it and at least one per MIN_TURN), graded toward a real
    end face when there is a skin. A closed ring has no ends and no last station (it is the first)."""
    skin, size = entry["skin"], float(entry["path_size"])
def _cuts(piece, rc, length, start, section, points, tol):
    """The arc lengths (at rc) along the turned piece where it must have a station: of points (the volume's corners),
    those on the piece, each at its angle about the piece's axis from where the piece starts. A point is on the piece
    when, turned back by its angle, it lies in the box of the section where the piece starts."""
    axis = np.asarray(piece["axis"], float)
    axis = axis / np.linalg.norm(axis)
    origin = np.asarray(piece["origin"], float)
    xyz = np.asarray(section.xyz, float)
    lo, hi = xyz.min(axis=0) - tol, xyz.max(axis=0) + tol
    r0 = _moved([xyz.mean(axis=0)], start)[0] - origin
    r0 -= axis * axis.dot(r0)
    out = []
    for q in np.asarray(points, float).reshape(-1, 3):
        d = q - origin
        d -= axis * axis.dot(d)
        if np.linalg.norm(d) < tol:
            continue
        phi = math.atan2(axis.dot(np.cross(r0, d)), r0.dot(d)) % (2 * math.pi)
        arc = phi * rc
        if not tol < arc < length - tol:
            continue
        back = _moved([q], np.linalg.inv(stations(piece, [arc], rc)[0] @ start))[0]
        if ((back >= lo) & (back <= hi)).all():
            out.append(arc)
    return out


def _flat(V, cells):
    """The number of cells (from sweep) that are flat or turned inside out: a triple product at their first node not
    above 1e-9 times the product of its edges' lengths."""
    n = 0
    for etype, c in cells.items():
        if len(c):
            a, b, e = (V[c[:, k]] - V[c[:, 0]] for k in JACOBIAN[etype])
            scale = np.linalg.norm(a, axis=1) * np.linalg.norm(b, axis=1) * np.linalg.norm(e, axis=1)
            n += int((_volume(V, c, etype) <= 1e-9 * scale).sum())
    return n


    graded = (False, False)
    if not closed:
        first = section.quad[0] if len(section.quad) else section.tri[0]
        centre = section.xyz[first].mean(axis=0)
        piece, rc, length, start = chain[-1]
        far = _moved([centre], stations(piece, [length], rc)[0] @ start)[0]
        ends = _nearest(2, faces, [centre, far], tol)[0]
        graded = tuple(_graded_end(f, vol, skinned) for f in ends)
    out = []
    for i, (piece, rc, length, start) in enumerate(chain):
        ends = (graded[0] and i == 0, graded[1] and i == len(chain) - 1)
        angle = float(piece.get("angle", 0.0))
        if angle:  # a station at each corner of the body on the piece, at least one per MIN_TURN
            cuts = _cuts(piece, rc, length, start, section, corners, tol)
            if skin and any(ends):
                first, depth = skin["depth"] / skin["per_depth"], skin["layer"] * skin["depth"]
                positions = turned_positions(length, angle, size, cuts, first, depth, ends)
            else:
                positions = turned_positions(length, angle, size, cuts)
        elif skin and any(ends):
            first, depth = skin["depth"] / skin["per_depth"], skin["layer"] * skin["depth"]
    corners = [gmsh.model.getValue(0, t, []) for _, t in gmsh.model.getBoundary([(3, vol)], False, False, True)]
            positions = graded_positions(length, size, first, depth, RATIO, ends)
        else:
            positions = graded_positions(length, size)
        steps = [t @ start for t in stations(piece, positions, rc)]
        out += steps if i == 0 else steps[1:]  # pieces join at shared stations
    return out[:-1] if closed else out


def apply_swept(job, folder, body_vols):
    """The swept mesh of every solid of job["swept"], at the end of build: each solid's volume (body_vols: {MAT_ID:
    final tags}), its section meshed with the skin on the profile curves whose side faces are real surface, swept along
    its pieces and classified on the volume's entities. job["swept_tags"] gets the volumes and job["swept_add"] one
    add(dim) per volume, for meshcommon.generate. Returns the volumes."""
    skins = {m for e in job.get("skin", []) for m in e["mat_ids"]} | {e["mat_id"] for e in job["swept"] if e["skin"]}
    skinned = {t for m in skins for t in body_vols.get(m, [])}
    tags, adds = [], []
    options = job.get("options", {})  # applied only in generate, after this: the sizes and the section get them here
    for entry in job.get("swept", []):
        entry = scaled(entry, options)
        left = list(body_vols[entry["mat_id"]])
        for k, solid in enumerate(entry["solids"]):
            path = os.path.join(folder, solid["profile"])
            box, mids, centre, normal, _ = _profile(path, entry["name"])
            chain, closed = _chain(solid["pieces"], centre), bool(solid.get("closed", False))
            swept = _swept_box(box, chain)
            vol = _volume_of(left, swept, entry["name"])
            left.remove(vol)
            faces = [abs(t) for _, t in gmsh.model.getBoundary([(3, vol)], oriented=False)]
            tol = TOL * float(np.linalg.norm(swept[1] - swept[0]))
            real = set(real_boundary(3, [vol]))
            points = _crossings(vol, centre, normal, tol)
            if len(points):  # split the profile where the body's edges cross it: the mids of the split curves
                _, mids, _, _, points = _profile(path, entry["name"], points, tol)
            piece, rc, length, _ = chain[0]
            half = _moved(mids, stations(piece, [0.5 * length], rc)[0])  # half way along the first piece
            side = _nearest(2, faces, half, tol)[0]  # the side face of each profile curve
            section = section_mesh(entry, k, [i for i, f in enumerate(side) if f in real], folder, options, points)
            transforms = _transforms(entry, section, chain, closed, faces, vol, skinned, tol)
            V, cells = sweep(section, transforms, closed)
            adds.append(_join(vol, V, cells, entry["name"]))
            tags.append(vol)
    job["swept_tags"], job["swept_add"] = tags, adds
    return tags
            flat = _flat(V, cells)
            if flat:
                raise JobError(
                    f"Swept Body {entry['name']}: {flat} of its swept cells are flat or inside out; make its Path Size"
                    " smaller"
                )
