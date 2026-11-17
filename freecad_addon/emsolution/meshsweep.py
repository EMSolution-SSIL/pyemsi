"""Swept Body: mesh the cross-section of a swept solid in 2D and sweep it into hexahedra and prisms. Runs in the
mesher process; never import FreeCAD here."""

import math
import os
from collections import namedtuple

import gmsh
import numpy as np

from meshcommon import JobError, apply_size_fields, apply_refinements, skin_refinements, apply_quad_layers, _smooth
from meshcommon import _note, import_brep
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
    middle in equal steps of at most size. When both ends' steps exceed length, they are scaled down to fill it."""
    if first is None:
        return np.linspace(0.0, length, max(1, round(length / size)) + 1)
    graded = []
    for end in ends:
        layer = []
        while end and sum(layer) < depth:
            layer.append(min(first * ratio ** len(layer), size))
        graded.append(layer)
    total = sum(graded[0]) + sum(graded[1])
    if total >= length * (1 - 1e-9):  # the layers fill the length: no middle
        d = np.array(graded[0] + graded[1][::-1]) * (length / total)
    else:
        middle = length - total
        n = max(1, math.ceil(middle / size - 1e-9))  # ceil, so no step exceeds size
        d = np.array(graded[0] + [middle / n] * n + graded[1][::-1])
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


def _generate():
    """Mesh the section in 2D; when gmsh cannot make the quad layers, graded triangles instead (as meshcommon)."""
    try:
        gmsh.model.mesh.generate(2)
    except Exception:
        field = gmsh.model.mesh.field
        layers = [f for f in field.list() if field.getType(f) == "BoundaryLayer"]
        if not layers:
            raise
        for f in layers:
            field.remove(f)
        gmsh.model.mesh.clear()
        _note("Skin Layer: gmsh could not make the quad layers; graded triangles instead")
        gmsh.model.mesh.generate(2)


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
                    _note(
                        f"Swept Body {name}: the cross-section of MAT_ID {m} has sharp corners and is not"
                        " four-sided; graded triangles, so prisms"
                    )
            elif entry["recombine"]:
                gmsh.model.mesh.setRecombine(2, face)
            _generate()
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
