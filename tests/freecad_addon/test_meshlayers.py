"""Prism layers grown inward from a body's surface mesh, and the tetrahedral core inside them (meshlayers.py, a mesher
module). Run from the repo root: pixi run -e addon pytest tests/freecad_addon/test_meshlayers.py"""

import json
import os
import sys

import gmsh
import numpy as np
import pytest

from .test_mesher import MESHER

sys.path.insert(0, os.path.dirname(MESHER))  # meshlayers imports its neighbours by bare name, as in the mesher process
import meshlayers  # noqa: E402 - needs the path above

PRISM_FACES = ((0, 1, 2), (3, 4, 5), (0, 1, 4, 3), (1, 2, 5, 4), (2, 0, 3, 5))
TET_FACES = ((0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3))


@pytest.fixture
def session():
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    gmsh.model.add("main")
    try:
        yield
    finally:
        gmsh.finalize()


def surface(make, size, cut=lambda face: False):
    """Mesh the surface of the OCC body make() at size. Returns X (n, 3), the outward tris (m, 3) of the faces that
    are not cut, the volume tag, and {cut face tag: (k, 2) rim edges} (the edges of the curves around each cut face),
    all as indexes into X."""
    body = make()
    gmsh.model.occ.synchronize()
    gmsh.option.setNumber("Mesh.MeshSizeMin", size)
    gmsh.option.setNumber("Mesh.MeshSizeMax", size)
    gmsh.model.mesh.generate(2)
    tags, coords, _ = gmsh.model.mesh.getNodes()
    xyz = dict(zip(tags.tolist(), np.array(coords).reshape(-1, 3)))
    faces = [abs(t) for _, t in gmsh.model.getBoundary([(3, body)], combined=False)]
    tris, cuts = [], {}
    for face in faces:
        if cut(face):
            edges = []
            for _, curve in gmsh.model.getBoundary([(2, face)], combined=False, oriented=False):
                _, en = gmsh.model.mesh.getElementsByType(1, abs(curve))
                edges.append(np.array(en, dtype=np.int64).reshape(-1, 2))
            cuts[face] = np.vstack(edges)
            continue
        _, en = gmsh.model.mesh.getElementsByType(2, face)
        T = np.array(en, dtype=np.int64).reshape(-1, 3)
        P = np.array([[xyz[n] for n in t] for t in T])
        normal = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0])
        centre = P.mean(axis=1)
        uv = gmsh.model.getParametrization(2, face, centre.ravel().tolist())
        cad = np.array(gmsh.model.getNormal(face, uv)).reshape(-1, 3)  # outward on an OCC solid's face
        flip = np.einsum("ij,ij->i", normal, cad) < 0
        T[flip] = T[flip][:, ::-1]
        tris.append(T)
    T = np.vstack(tris)
    nodes = np.unique(T)
    index = {n: i for i, n in enumerate(nodes.tolist())}
    X = np.array([xyz[n] for n in nodes.tolist()])
    tris = np.vectorize(index.get)(T)
    cuts = {face: np.vectorize(index.get)(edges) for face, edges in cuts.items()}
    return X, tris, body, cuts


def fillet_box(dx, dy, dz, r):
    def make():
        box = gmsh.model.occ.addBox(-dx / 2, -dy / 2, -dz / 2, dx, dy, dz)
        gmsh.model.occ.synchronize()
        curves = sorted({abs(c) for _, c in gmsh.model.getEntities(1)})
        return gmsh.model.occ.fillet([box], curves, [r])[0][1]

    return make


def all_nodes(X, layered):
    return np.vstack([X, layered.coords])


def signed_volumes(P, tets):
    a, b, c, d = (P[tets[:, i]] for i in range(4))
    return np.einsum("ij,ij->i", np.cross(b - a, c - a), d - a) / 6


def test_heights():
    assert meshlayers.heights(1, 2, 2) == pytest.approx([0.5 * 2 / 1.82, 1.1 * 2 / 1.82, 2.0])
    h = meshlayers.heights(1, 4, 1)
    assert abs(h[0] - 0.25) <= 0.025
    assert h[-1] == pytest.approx(1.0)


def test_sphere_layers(session):
    X, tris, _, _ = surface(lambda: gmsh.model.occ.addSphere(0, 0, 0, 5), 1.0)
    layered = meshlayers.build(X, tris, {}, meshlayers.heights(1, 2, 2), 1.0, 3.0)
    assert len(layered.prisms) == 3 * len(tris)
    P = all_nodes(X, layered)
    assert len(layered.tets) > 0
    assert (signed_volumes(P, layered.tets) > 0).all()
    inside = np.array([w == (3, 0) for w in layered.where])
    assert inside.any()
    assert (5 - np.linalg.norm(layered.coords[inside], axis=1) >= 0.5 - 1e-9).all()


def test_folded_counts_inside_out_prisms():
    X = np.array([[0.0, 0, 0], [1, 0, 0], [0, 1, 0]])
    tris = np.array([[0, 1, 2]])  # outward +z
    assert meshlayers.folded([X, X - [0, 0, 0.1]], tris) == 0
    assert meshlayers.folded([X, X + [0, 0, 0.1]], tris) == 1
    assert meshlayers.folded([X, X * np.nan], tris) == 1


def test_rounded_busbar_layers(session):
    X, tris, _, _ = surface(fillet_box(20, 10, 8, 3), 1.0)
    layered = meshlayers.build(X, tris, {}, meshlayers.heights(1, 2, 2), 1.0, 3.0)
    assert len(layered.prisms) == 3 * len(tris)
    assert len(layered.tets) > 0


def test_thin_strip_folds(session):
    X, tris, _, _ = surface(fillet_box(20, 8, 5, 2.4), 1.0)
    with pytest.raises(meshlayers.LayerFailed) as failed:
        meshlayers.build(X, tris, {}, meshlayers.heights(1, 2, 2), 1.0, 3.0)
    assert failed.value.kind in ("fold", "core")


def cylinder_rims(X, cuts):
    rims = {}
    for face, edges in cuts.items():
        nodes = np.unique(edges)
        radial = X[nodes] * [0, 1, 1]
        normal = {int(i): v / np.linalg.norm(v) for i, v in zip(nodes, radial)}
        plane = np.array([1.0 if X[nodes[0], 0] > 0 else -1.0, 0, 0])
        rims[face] = meshlayers.Rim(plane, edges, normal)
    return rims


def test_wire_with_cut_ends(session):
    def make():
        return gmsh.model.occ.addCylinder(-5, 0, 0, 10, 0, 0, 1.0)

    def is_cut(face):
        com = gmsh.model.occ.getCenterOfMass(2, face)
        return abs(abs(com[0]) - 5) < 1e-9

    X, tris, _, cuts = surface(make, 0.2, is_cut)
    assert len(cuts) == 2
    rims = cylinder_rims(X, cuts)
    layered = meshlayers.build(X, tris, rims, meshlayers.heights(0.2, 2, 2), 0.2, 0.5)
    assert len(layered.prisms) == 3 * len(tris)
    for face, edges in cuts.items():
        quads, triangles = layered.faces[face]
        assert len(quads) == len(edges) * 3
        assert len(triangles) > 0
    count = {}
    for elements, shapes in ((layered.prisms, PRISM_FACES), (layered.tets, TET_FACES)):
        for e in elements:
            for f in shapes:
                key = frozenset(e[list(f)].tolist())
                count[key] = count.get(key, 0) + 1
    once = {key for key, n in count.items() if n == 1}
    expected = {frozenset(t.tolist()) for t in tris}
    for quads, triangles in layered.faces.values():
        expected |= {frozenset(q.tolist()) for q in quads} | {frozenset(t.tolist()) for t in triangles}
    assert once == expected
    P = all_nodes(X, layered)
    assert (signed_volumes(P, layered.tets) > 0).all()
    for face in cuts:
        on = [i + len(X) for i, w in enumerate(layered.where) if w == (2, face)]
        assert on and np.allclose(abs(P[on, 0]), 5)


def torus_normal(p):
    centre = 4 * p * [1, 1, 0] / np.linalg.norm(p[:2])
    n = p - centre
    return n / np.linalg.norm(n)


def test_seam_cap_moved(session):
    def make():
        torus = gmsh.model.occ.addTorus(0, 0, 0, 4, 1.0)
        box = gmsh.model.occ.addBox(0, 0, -3, 8, 8, 6)
        return gmsh.model.occ.intersect([(3, torus)], [(3, box)])[0][0][1]

    def is_cut(face):
        com = gmsh.model.occ.getCenterOfMass(2, face)
        return abs(com[0]) < 1e-9 or abs(com[1]) < 1e-9

    X, tris, _, cuts = surface(make, 0.3, is_cut)
    assert len(cuts) == 2
    rims, by_plane = {}, {}
    for face, edges in cuts.items():
        nodes = np.unique(edges)
        on_x0 = abs(X[nodes[0], 0]) < 1e-9
        plane = np.array([-1.0, 0, 0]) if on_x0 else np.array([0, -1.0, 0])
        rims[face] = meshlayers.Rim(plane, edges, {int(i): torus_normal(X[i]) for i in nodes})
        by_plane["x0" if on_x0 else "y0"] = face
    master, slave = by_plane["y0"], by_plane["x0"]  # the y = 0 face turned by 90 degrees about z is the x = 0 face
    rotation = [0, -1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
    layered = meshlayers.build(X, tris, rims, meshlayers.heights(0.2, 2, 2), 0.3, 0.6, [(slave, master, rotation)])
    P = all_nodes(X, layered)
    M = np.array(rotation, dtype=float).reshape(4, 4)
    moved = P[np.unique(layered.faces[master][1])] @ M[:3, :3].T + M[:3, 3]
    target = P[np.unique(layered.faces[slave][1])]
    assert len(moved) == len(target)
    size = np.ptp(X, axis=0).max()
    gap = np.linalg.norm(moved[:, None, :] - target[None, :, :], axis=2).min(axis=1)
    assert gap.max() <= 1e-9 * size
    assert (signed_volumes(P, layered.tets) > 0).all()


def test_core_restores_options(session):
    values = {
        "Mesh.MeshOnlyVisible": 1,
        "Mesh.MeshSizeMax": 7,
        "Mesh.MeshSizeExtendFromBoundary": 0,
        "Mesh.Algorithm3D": 10,
    }
    for name, value in values.items():
        gmsh.option.setNumber(name, value)
    gmsh.model.add("caller")
    square = np.array([[0.0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]])
    inner, cap_tris = meshlayers.cap(square, [], 0.5)
    assert len(cap_tris) >= 2
    assert gmsh.model.getCurrent() == "caller"
    # a tetrahedron's surface, outward
    X = np.array([[0.0, 0, 0], [2, 0, 0], [0, 2, 0], [0, 0, 2]])
    tris = np.array([[0, 2, 1], [0, 1, 3], [0, 3, 2], [1, 2, 3]])
    coords, tets = meshlayers.core(X, tris, [], 0.5, 1.0)
    assert len(tets) > 0
    assert (signed_volumes(np.vstack([X, coords]), tets) > 0).all()
    assert gmsh.model.getCurrent() == "caller"
    for name, value in values.items():
        assert gmsh.option.getNumber(name) == value, name


def test_heights_nearest_count():
    assert len(meshlayers.heights(1, 1, 2)) == 2  # sums 1 and 2.2: 2.2 is nearer 2
    assert len(meshlayers.heights(1, 1, 3)) == 3  # sums 2.2 and 3.64: 3.64 is nearer 3
    assert meshlayers.heights(1, 1, 3)[-1] == pytest.approx(3.0)
    assert len(meshlayers.heights(1, 2, 2.6)) == 4


OPTIONS = {
    "Mesh.MeshOnlyVisible": 1,
    "Mesh.MeshSizeMax": 7,
    "Mesh.MeshSizeExtendFromBoundary": 0,
    "Mesh.Algorithm3D": 10,
}


def assert_restored():
    assert gmsh.model.getCurrent() == "caller"
    for name, value in OPTIONS.items():
        assert gmsh.option.getNumber(name) == value, name


def test_cap_self_crossing_loop_fails(session):
    for name, value in OPTIONS.items():
        gmsh.option.setNumber(name, value)
    gmsh.model.add("caller")
    bowtie = np.array([[0.0, 0, 0], [1, 1, 0], [1, 0, 0], [0, 1, 0]])
    with pytest.raises(meshlayers.LayerFailed) as failed:
        meshlayers.cap(bowtie, [], 0.2)
    assert failed.value.kind == "core"
    assert_restored()


def test_core_failure_restores_options(session):
    for name, value in OPTIONS.items():
        gmsh.option.setNumber(name, value)
    gmsh.model.add("caller")
    X = np.array([[0.0, 0, 0], [2, 0, 0], [0, 2, 0], [0, 0, 2]])
    tris = np.array([[0, 2, 1], [0, 1, 3], [0, 3, 2]])  # a tetrahedron's surface less one face: open
    with pytest.raises(meshlayers.LayerFailed) as failed:
        meshlayers.core(X, tris, [], 0.5, 1.0)
    assert failed.value.kind == "core"
    assert_restored()


def test_note_printed_once_per_job(capsys):
    import meshcommon

    meshcommon._noted.clear()
    text = "Skin Layer Skin: MAT_ID 1 has a sharp edge on its surface; graded tetrahedra instead of prism layers"
    for _ in range(3):  # a retried job builds again, and one MAT_ID may have several solids
        meshcommon._note(text)
    meshcommon._note(
        "Skin Layer Skin: MAT_ID 2 has a sharp edge on its surface; graded tetrahedra instead of prism layers"
    )
    err = capsys.readouterr().err
    assert err.count(f"NOTE: {text}") == 1
    assert err.count("NOTE: ") == 2
    meshcommon._noted.clear()  # what run and check do for the next job
    meshcommon._note(text)
    assert capsys.readouterr().err.count("NOTE: ") == 1


def sphere_job(folder):
    """A job of the sphere r 5 (MAT_ID 1) with prism layers in an air box, for meshcommon.run in-process."""
    from .test_mesher import layer_skin, write_box, write_occ

    os.makedirs(os.path.join(folder, "geometry"))
    write_occ(os.path.join(folder, "geometry", "vol_1.brep"), lambda occ: occ.addSphere(0, 0, 0, 5))
    write_box(os.path.join(folder, "geometry", "air.brep"), -20, -20, -20, 40, 40, 40)
    job = {
        "model_name": "Model",
        "mesh_file": os.path.join(folder, "pre_geom.msh"),
        "volumes": [{"mat_id": 1, "name": "Sphere", "file": "geometry/vol_1.brep", "size": 2.0}],
        "surfaces": [],
        "sizes": [],
        "air": {"name": "Air", "mat_id": 2, "file": "geometry/air.brep", "size": 4.0},
        "skin": [layer_skin()],
    }
    path = os.path.join(folder, "job.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(job, fh)
    return path


def element_types(path, group):
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(path)
        return {
            gmsh.model.mesh.getElementProperties(int(t))[0]
            for e in gmsh.model.getEntitiesForPhysicalGroup(3, group)
            for t in gmsh.model.mesh.getElements(3, e)[0]
        }
    finally:
        gmsh.finalize()


def test_wrong_sign_grows_no_layers_outward(tmp_path, monkeypatch, capsys):
    # every face's sign turned: the surface is inside out and the layers would grow outward, into the air, unfolded
    import mesher
    import meshcommon

    real = meshlayers._signs
    monkeypatch.setattr(meshlayers, "_signs", lambda vol: {f: -s for f, s in real(vol).items()})
    path = sphere_job(str(tmp_path))
    meshcommon.run(path, mesher.build, 3)
    err = capsys.readouterr().err
    assert (
        "NOTE: Skin Layer Skin: MAT_ID 1: the prism layers would fold (the layer is too deep for its curves); graded"
        " tetrahedra instead" in err
    )
    assert element_types(str(tmp_path / "pre_geom.msh"), 1) == {"Tetrahedron 4"}


def test_seams_that_do_not_match_say_so(tmp_path, monkeypatch, capsys):
    # the ring cell of test_mesher's test_layered_ring_cells with its seams' corners taken to differ (meshsym._same
    # False while _layer_seams runs): note N8, not N5, and graded tetrahedra
    import math

    import mesher
    import meshgroups
    import meshsym
    from .test_mesher import layer_skin, turn_z, write_box, write_faces, write_round_ring

    folder = str(tmp_path)
    geometry = os.path.join(folder, "geometry")
    os.makedirs(geometry)
    write_round_ring(os.path.join(geometry, "cell_1.brep"), 20, 3, 90)
    files = write_faces(
        os.path.join(geometry, "cell_1.brep"), geometry, "skin_free_1", lambda c: math.hypot(c[0], c[1]) < 19.9
    )
    entry = layer_skin("Skin", (1,), 0.66, 2.0, 2.0, True)
    entry["faces"] = [{"mat_id": 1, "file": "geometry/" + f} for f in files]
    write_box(os.path.join(geometry, "air.brep"), -29, -29, -9, 58, 58, 18)
    volume = {"mat_id": 1, "name": "Ring", "file": "geometry/cell_1.brep", "size": 1.0}
    group = {
        "name": "Ring",
        "side": "fixed",
        "job": {"volumes": [volume], "surfaces": [], "sizes": [], "skin": [entry]},
        "cells": [1],
        "transforms": [turn_z(90 * k) for k in range(4)],
        "parts": [{"mat_id": 5 + c, "name": f"Copy{c}"} for c in range(4)],
        "rows": [{"cell": 1, "file": None, "parts": [0, 1, 2, 3]}],
    }
    air = {"name": "Air", "mat_id": 30, "file": "geometry/air.brep", "size": 4.0}
    free = [{"side": "fixed", "job": {"volumes": [], "surfaces": [], "sizes": [], "air": air}}]
    job = {
        "model_name": "Model",
        "mesh_file": os.path.join(folder, "pre_geom.msh"),
        "options": {},
        "symmetric": {"groups": [group], "free": free},
    }
    path = os.path.join(folder, "job.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(job, fh)
    real = meshgroups._layer_seams

    def layer_seams(*args):
        with monkeypatch.context() as patch:
            patch.setattr(meshsym, "_same", lambda *a: False)
            real(*args)

    monkeypatch.setattr(meshgroups, "_layer_seams", layer_seams)
    meshgroups.run(path, mesher.build, 3)
    err = capsys.readouterr().err
    assert (
        "NOTE: Skin Layer Skin: MAT_ID 1: its seams with its own copies do not match; graded tetrahedra instead of"
        " prism layers" in err
    )
    assert "meets a copy of another cell" not in err
    for c in range(4):
        assert element_types(str(tmp_path / "pre_geom.msh"), 5 + c) == {"Tetrahedron 4"}
