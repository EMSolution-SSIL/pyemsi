"""Swept Body: the cross-section mesh and the swept volume mesh (meshsweep.py, a mesher module).
Run from the repo root: pixi run -e addon pytest tests/freecad_addon/test_meshsweep.py"""

import json
import math
import os
import sys

import gmsh
import numpy as np
import pytest

from .test_mesher import MESHER, write_box, write_rect
from .test_mesher2d import write_polygons

sys.path.insert(0, os.path.dirname(MESHER))  # meshsweep imports its neighbours by bare name, as in the mesher process
import meshsweep  # noqa: E402 - needs the path above
import meshcommon  # noqa: E402 - needs the path above

SKIN = {"depth": 1.0, "per_depth": 2.0, "layer": 3.0}


def entry(profile, skin=SKIN, section_size=2.0, recombine=False):
    piece = {"origin": [0, 0, 0], "axis": [0, 0, 1], "angle": 0.0, "advance": 40.0}
    return {
        "name": "Bar",
        "mat_id": 7,
        "path_size": 4.0,
        "section_size": section_size,
        "recombine": recombine,
        "skin": skin,
        "solids": [{"profile": profile, "pieces": [piece]}],
    }


def section(profile, real, folder, **options):
    """section_mesh of the profile in a gmsh session with a main model, as in the mesher: the main model is current
    afterwards and the section's own model is gone."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.model.add("main")
        gmsh.model.occ.addBox(0, 0, 0, 1, 1, 1)
        gmsh.model.occ.synchronize()
        models, opts = gmsh.model.list(), [gmsh.option.getNumber(o) for o in meshsweep.SIZE_OPTIONS]
        s = meshsweep.section_mesh(entry(profile, **options), 0, real, str(folder))
        assert gmsh.model.getCurrent() == "main"
        assert gmsh.model.list() == models and len(gmsh.model.getEntities(3)) == 1
        assert [gmsh.option.getNumber(o) for o in meshsweep.SIZE_OPTIONS] == opts
        return s
    finally:
        gmsh.finalize()


def curve_boxes(path):
    """The bounding boxes of the profile face's curves, in getBoundary order."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.model.occ.importShapes(str(path))
        gmsh.model.occ.synchronize()
        curves = [abs(t) for _, t in gmsh.model.getBoundary(gmsh.model.getEntities(2), oriented=False)]
        return [gmsh.model.getBoundingBox(1, c) for c in curves]
    finally:
        gmsh.finalize()


def write_disc(path, r):
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.model.occ.addDisk(0, 0, 0, r, r)
        gmsh.model.occ.synchronize()
        gmsh.write(str(path))
    finally:
        gmsh.finalize()


def steps(section, key):
    """The lengths of the section's edges along the profile curve key, in its node order."""
    return np.linalg.norm(np.diff(section.xyz[section.edges[key]], axis=0), axis=1)


def side(section, axis, value):
    """The key of the straight profile curve whose nodes all have coordinate axis == value."""
    keys = [k for k, nodes in section.edges.items() if np.allclose(section.xyz[nodes, axis], value)]
    assert len(keys) == 1
    return keys[0]


def test_graded_positions_uniform():
    assert np.allclose(meshsweep.graded_positions(40, 4), np.arange(0, 41, 4))


def test_graded_positions_both_ends():
    p = meshsweep.graded_positions(10, 2, first=0.5, depth=3)
    d = np.diff(p)
    assert p[0] == 0 and p[-1] == pytest.approx(10)
    assert d[0] == pytest.approx(0.5) and d[-1] == pytest.approx(0.5)
    assert d[1] == pytest.approx(0.6) and d[2] == pytest.approx(0.72)
    assert d.max() <= 2 + 1e-9
    assert np.allclose(d, d[::-1])


def test_graded_positions_one_end():
    p = meshsweep.graded_positions(10, 2, first=0.5, depth=3, ends=(True, False))
    d = np.diff(p)
    assert d[0] == pytest.approx(0.5) and p[-1] == pytest.approx(10)
    assert d[-1] == pytest.approx(d[-2]) and d[-1] > 1.2  # the middle step
    assert d.max() <= 2 + 1e-9


def test_graded_positions_layer_fills_the_length():
    p = meshsweep.graded_positions(2, 2, first=0.5, depth=3)
    d = np.diff(p)
    assert p[0] == 0 and p[-1] == pytest.approx(2)
    assert (d > 0).all()
    assert np.allclose(d, d[::-1])
    assert d[0] < d[1]
    assert d[0] == pytest.approx(0.5, rel=0.25)  # the first step stays near first


def test_graded_positions_meeting_layers_leave_no_sliver():
    for length, ends in [(4, (True, True)), (4, (True, False)), (7.6, (True, True)), (8, (True, True))]:
        d = np.diff(meshsweep.graded_positions(length, 2, first=0.5, depth=3, ends=ends))
        assert d.sum() == pytest.approx(length)
        assert d[0] == pytest.approx(0.5, rel=0.25)
        assert (d[1:] >= 0.5 * d[:-1]).all() and (d[:-1] >= 0.5 * d[1:]).all()


def test_section_of_a_bar_is_a_graded_grid(tmp_path):
    write_rect(str(tmp_path / "bar.brep"), -5, -2, 3, 10, 4)
    s = section("bar.brep", [0, 1, 2, 3], tmp_path)
    assert len(s.tri) == 0 and len(s.quad) > 0
    assert np.allclose(s.xyz[:, 2], 3)  # global coordinates
    assert len(s.edges[side(s, 1, -2)]) == len(s.edges[side(s, 1, 2)])
    assert len(s.edges[side(s, 0, -5)]) == len(s.edges[side(s, 0, 5)])
    for key in (side(s, 1, -2), side(s, 1, 2)):  # the long sides, 10: graded 0.5, 0.6, ... from both ends
        d = steps(s, key)
        assert d[0] == pytest.approx(0.5) and d[-1] == pytest.approx(0.5)
        assert d.max() <= 2 + 1e-9
    for key in (side(s, 0, -5), side(s, 0, 5)):  # the short sides, 4: the two layers meet and fill it
        d = steps(s, key)
        assert d[0] == pytest.approx(d[-1]) and d.min() == pytest.approx(0.5, rel=0.25)
        assert d.sum() == pytest.approx(4)


def write_spline_rect(path, x, y, z, dx, dy):
    """The rectangle of write_rect with each side a straight B-spline whose parameter is not its length (the middle
    control point a tenth along), as a pipe's start face stores its straight edges."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        occ = gmsh.model.occ
        corners = [(x, y, z), (x + dx, y, z), (x + dx, y + dy, z), (x, y + dy, z)]
        tags = [occ.addPoint(*c) for c in corners]
        sides = []
        for k, (p, q) in enumerate(zip(corners, corners[1:] + corners[:1])):
            mid = occ.addPoint(*(a + 0.1 * (b - a) for a, b in zip(p, q)))
            sides.append(occ.addBSpline([tags[k], mid, tags[(k + 1) % 4]], degree=2))
        occ.addPlaneSurface([occ.addCurveLoop(sides)])
        occ.synchronize()
        gmsh.write(path)
    finally:
        gmsh.finalize()


def test_section_with_straight_spline_sides_is_a_graded_grid(tmp_path):
    write_rect(str(tmp_path / "lines.brep"), -5, -2, 3, 10, 4)
    write_spline_rect(str(tmp_path / "bar.brep"), -5, -2, 3, 10, 4)
    s = section("bar.brep", [0, 1, 2, 3], tmp_path)
    grid = section("lines.brep", [0, 1, 2, 3], tmp_path)
    assert len(s.tri) == 0 and len(s.quad) == len(grid.quad)
    assert np.allclose(sorted(map(tuple, s.xyz.round(9))), sorted(map(tuple, grid.xyz.round(9))))
    for key in (side(s, 1, -2), side(s, 1, 2)):
        d = steps(s, key)
        assert d[0] == pytest.approx(0.5) and d[-1] == pytest.approx(0.5)


def test_section_of_a_wire_has_quad_layers(tmp_path):
    write_disc(tmp_path / "wire.brep", 5)
    s = section("wire.brep", [0], tmp_path)
    r = np.hypot(s.xyz[:, 0], s.xyz[:, 1])
    assert len(s.quad) > 0 and len(s.tri) > 0
    assert r[s.quad].mean(axis=1).min() >= 5 - 3.5
    assert r[s.tri].mean(axis=1).max() < 5 - 1
    (rim,) = s.edges.values()
    assert rim[0] == rim[-1]  # a closed curve: the first node again at the end
    assert np.allclose(r[rim], 5)


def test_section_skips_cut_sides(tmp_path):
    write_rect(str(tmp_path / "bar.brep"), -5, -2, 0, 10, 4)
    cut = next(k for k, box in enumerate(curve_boxes(tmp_path / "bar.brep")) if np.isclose(box[4], -2))  # y = -2
    s = section("bar.brep", [k for k in range(4) if k != cut], tmp_path)
    assert len(s.tri) == 0
    d = steps(s, side(s, 0, -5))  # a short side, graded toward y = 2 only
    if s.xyz[s.edges[side(s, 0, -5)][0], 1] > 0:
        d = d[::-1]  # from y = -2 to y = 2
    assert d[-1] == pytest.approx(0.5, rel=0.25)
    assert d[0] > d[-1]  # not graded toward the cut
    assert (d[1:] >= 0.5 * d[:-1]).all() and (d[:-1] >= 0.5 * d[1:]).all()  # no sliver beside the cut
    assert len(s.edges[side(s, 1, -2)]) == len(s.edges[side(s, 1, 2)])


def test_section_of_an_l_has_triangles(tmp_path, capsys):
    write_polygons(str(tmp_path / "l.brep"), [[(0, 0), (10, 0), (10, 3), (3, 3), (3, 10), (0, 10)]])
    s = section("l.brep", list(range(6)), tmp_path)
    assert len(s.tri) > 0 and len(s.quad) == 0
    assert len(s.edges) == 6
    assert (
        "NOTE: Swept Body Bar: the cross-section of MAT_ID 7 has sharp corners and is not four-sided; graded"
        " triangles, so prisms" in capsys.readouterr().err
    )


def test_section_recombine_with_skin(tmp_path):
    write_disc(tmp_path / "wire.brep", 5)
    s = section("wire.brep", [0], tmp_path, recombine=True)
    assert len(s.tri) == 0 and len(s.quad) > 0


def test_section_recombine_with_sharp_corners(tmp_path, capsys):
    write_polygons(str(tmp_path / "l.brep"), [[(0, 0), (10, 0), (10, 3), (3, 3), (3, 10), (0, 10)]])
    s = section("l.brep", list(range(6)), tmp_path, recombine=True)
    assert len(s.tri) == 0 and len(s.quad) > 0
    assert "so prisms" not in capsys.readouterr().err


def test_section_without_skin_is_sized(tmp_path):
    write_rect(str(tmp_path / "bar.brep"), -5, -2, 0, 10, 4)
    s = section("bar.brep", [0, 1, 2, 3], tmp_path, skin=None, recombine=True)
    assert len(s.quad) > 0
    for key in s.edges:
        assert steps(s, key).max() <= 2 * 1.01


def test_section_of_a_bar_without_skin_is_a_grid(tmp_path):
    write_rect(str(tmp_path / "bar.brep"), -5, -2, 0, 10, 4)
    s = section("bar.brep", [0, 1, 2, 3], tmp_path, skin=None, recombine=False)
    assert (len(s.quad), len(s.tri)) == (10, 0)  # 5 x 2 quads at size 2, without Recombine
    assert sorted(len(nodes) for nodes in s.edges.values()) == [3, 3, 6, 6]
    for key in s.edges:
        assert np.allclose(steps(s, key), 2.0)


def grid(nx, ny):
    """A flat section of nx x ny unit quads."""
    x, y = np.meshgrid(np.arange(nx + 1.0), np.arange(ny + 1.0), indexing="ij")
    xyz = np.column_stack([x.ravel(), y.ravel(), np.zeros(x.size)])
    at = np.arange(x.size).reshape(nx + 1, ny + 1)
    quad = np.array([[at[i, j], at[i + 1, j], at[i + 1, j + 1], at[i, j + 1]] for i in range(nx) for j in range(ny)])
    return meshsweep.Section(xyz, np.zeros((0, 3), int), quad, {})


def jacobians(V, cells, a, b, c):
    return np.einsum(
        "ij,ij->i",
        np.cross(V[cells[:, a]] - V[cells[:, 0]], V[cells[:, b]] - V[cells[:, 0]]),
        V[cells[:, c]] - V[cells[:, 0]],
    )


def test_stations_translate_along_the_axis():
    piece = {"origin": [0, 0, 0], "axis": [0, 0, 1], "angle": 0.0, "advance": 40.0}
    ts = meshsweep.stations(piece, [0.0, 4.0])
    assert len(ts) == 2
    assert np.allclose(ts[0], np.eye(4))
    assert np.allclose(ts[1][:3, 3], [0, 0, 4]) and np.allclose(ts[1][:3, :3], np.eye(3))


def test_stations_rotate():
    piece = {"origin": [0, 0, 0], "axis": [0, 0, 1], "angle": 90.0, "advance": 0.0}
    ts = meshsweep.stations(piece, [0.0, 20 * np.pi / 2], rc=20)
    assert np.allclose(ts[0], np.eye(4))
    assert np.allclose(ts[1][:3, :3], [[0, -1, 0], [1, 0, 0], [0, 0, 1]]) and np.allclose(ts[1][:3, 3], 0)


def test_stations_rotate_about_an_offset_axis():
    piece = {"origin": [10, 0, 0], "axis": [0, 0, 1], "angle": 180.0, "advance": 0.0}
    (t,) = meshsweep.stations(piece, [5 * np.pi], rc=5)
    assert np.allclose(t @ [15, 0, 3, 1], [5, 0, 3, 1])


def test_stations_helix():
    piece = {"origin": [0, 0, 0], "axis": [0, 0, 1], "angle": 360.0, "advance": 6.0}
    length = np.hypot(20 * 2 * np.pi, 6.0)
    t0, half, end = meshsweep.stations(piece, [0.0, length / 2, length], rc=20)
    assert np.allclose(t0, np.eye(4))
    assert np.allclose(half[:3, :3], [[-1, 0, 0], [0, -1, 0], [0, 0, 1]]) and np.allclose(half[:3, 3], [0, 0, 3])
    assert np.allclose(half @ [20, 0, 0, 1], [-20, 0, 3, 1])
    assert np.allclose(end[:3, :3], np.eye(3)) and np.allclose(end[:3, 3], [0, 0, 6])


def test_chain_joints_are_stations():
    pieces = [
        {"origin": [25, -30, 0], "axis": [0, 1, 0], "angle": 0.0, "advance": 30.0},
        {"origin": [0, 0, 0], "axis": [0, 0, 1], "angle": 90.0, "advance": 0.0},
        {"origin": [0, 25, 0], "axis": [-1, 0, 0], "angle": 0.0, "advance": 30.0},
    ]
    centre = np.array([25.0, -30, 0])
    chain = meshsweep._chain(pieces, centre)
    assert [round(length, 9) for _, _, length, _ in chain] == [30, round(25 * np.pi / 2, 9), 30]
    at = _moved_all(meshsweep._path(chain, 4.0), centre)
    for joint in ([25, 0, 0], [0, 25, 0]):
        assert np.linalg.norm(at - joint, axis=1).min() < 1e-9
    assert np.allclose(at[0], centre) and np.allclose(at[-1], [-30, 25, 0])
    steps = np.linalg.norm(np.diff(at, axis=0), axis=1)
    assert steps.min() > 1.0 and steps.max() < 4.0 + 1e-9  # no repeated station at a joint, chords at most a step


def _moved_all(transforms, point):
    return np.array([t[:3, :3] @ point + t[:3, 3] for t in transforms])


def test_sweep_closed_ring_joins():
    flat = grid(2, 2)  # 4 quads, turned into the plane y = 0 at x 20..22
    xyz = np.column_stack([20 + flat.xyz[:, 0], np.zeros(len(flat.xyz)), flat.xyz[:, 1]])
    section = meshsweep.Section(xyz, flat.tri, flat.quad, {})
    piece = {"origin": [0, 0, 0], "axis": [0, 0, 1], "angle": 360.0, "advance": 0.0}
    rc = 21.0
    positions = np.linspace(0, 2 * np.pi * rc, 37)[:-1]
    V, cells = meshsweep.sweep(section, meshsweep.stations(piece, positions, rc=rc), closed=True)
    assert len(cells[5]) == 36 * 4 and len(cells[6]) == 0
    assert len(V) == 36 * len(xyz)
    assert len(np.unique(np.round(V, 9), axis=0)) == len(V)  # no duplicate nodes
    assert len(np.unique(cells[5])) == len(V)  # every node used, the last station joined to the first
    assert (jacobians(V, cells[5], 1, 3, 4) > 0).all()


@pytest.mark.parametrize("axis", [[0, 0, 1], [0, 0, -1]])
def test_sweep_counts(axis):
    section = grid(10, 4)
    piece = {"origin": [0, 0, 0], "axis": axis, "angle": 0.0, "advance": 36.0}
    V, cells = meshsweep.sweep(section, meshsweep.stations(piece, np.linspace(0, 36, 10)))
    assert len(V) == 10 * len(section.xyz)
    assert len(cells[5]) == 9 * 40 and len(cells[6]) == 0
    assert (jacobians(V, cells[5], 1, 3, 4) > 0).all()


def test_sweep_of_triangles_gives_prisms():
    xyz = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], float)
    section = meshsweep.Section(xyz, np.array([[0, 2, 1]]), np.zeros((0, 4), int), {})
    piece = {"origin": [0, 0, 0], "axis": [0, 0, 1], "angle": 0.0, "advance": 2.0}
    V, cells = meshsweep.sweep(section, meshsweep.stations(piece, [0, 1, 2]))
    assert len(cells[6]) == 2 and len(cells[5]) == 0
    assert (jacobians(V, cells[6], 1, 2, 3) > 0).all()


def test_closed_sweep_joins_the_last_station_to_the_first():
    section = grid(1, 1)
    ts = [np.eye(4) for _ in range(3)]
    for k, t in enumerate(ts):
        t[:3, 3] = [0, 0, k]
    V, cells = meshsweep.sweep(section, ts, closed=True)
    assert len(V) == 3 * 4 and len(cells[5]) == 3
    assert set(cells[5][-1].tolist()) == {8, 9, 10, 11, 0, 1, 2, 3}


def test_empty_volume_around_swept_fails_loudly():
    """gmsh may log an error and leave a volume empty without raising: _check_filled names the body."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.model.add("main")
        gmsh.model.occ.addBox(0, 0, 0, 1, 1, 1)
        gmsh.model.occ.addBox(1, 0, 0, 1, 1, 1)
        gmsh.model.occ.fragment([(3, 1)], [(3, 2)])
        gmsh.model.occ.synchronize()
        gmsh.model.addPhysicalGroup(3, [1], 1, name="Bar")
        gmsh.model.addPhysicalGroup(3, [2], 2, name="Air")
        gmsh.model.mesh.generate(2)
        gmsh.model.mesh.generate(3)
        meshcommon._check_filled([], [])  # both filled
        gmsh.model.mesh.clear([(3, 2)])
        with pytest.raises(
            meshcommon.JobError, match=r"gmsh could not mesh Air \(MAT_ID 2\) around the swept bodies \(PLC"
        ):
            meshcommon._check_filled([(3, 1)], ["Error: PLC Error: A segment and a facet intersect at point"])
    finally:
        gmsh.finalize()


def test_empty_volume_in_a_cell_model_names_the_group():
    """In a cell model (meshgroups.mesh_cell) there is no air: the advice names the group and the sizes."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.model.add("main")
        gmsh.model.occ.addBox(0, 0, 0, 1, 1, 1)
        gmsh.model.occ.addBox(1, 0, 0, 1, 1, 1)
        gmsh.model.occ.fragment([(3, 1)], [(3, 2)])
        gmsh.model.occ.synchronize()
        gmsh.model.addPhysicalGroup(3, [1], 1, name="Bar")
        gmsh.model.addPhysicalGroup(3, [2], 2, name="Iron")
        gmsh.model.mesh.generate(2)
        with pytest.raises(meshcommon.AirFailed) as err:
            meshcommon._check_filled([(3, 1)], ["Error: PLC Error"], "Ring")
        assert str(err.value) == (
            "group Ring: gmsh could not mesh Iron (MAT_ID 2) around the swept cell (PLC Error); make the cell objects'"
            " Mesh Size or the Swept Body's Path Size and Section Size smaller"
        )
    finally:
        gmsh.finalize()


def test_failed_3d_mesh_in_a_cell_model_names_the_group(monkeypatch):
    def fail(dim):
        if dim == 3:
            raise Exception("boom")
        return []

    monkeypatch.setattr(meshcommon, "mesh_with_fallback", fail)
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.option.setNumber("Mesh.OptimizePyramids", 0)
        gmsh.model.add("main")
        with pytest.raises(meshcommon.AirFailed) as err:
            meshcommon._swept_stages({"swept_add": [], "swept_group": "Ring"}, 3)
        assert str(err.value) == (
            "group Ring: gmsh could not mesh around the swept cell (boom); make the cell objects' Mesh Size or the"
            " Swept Body's Path Size and Section Size smaller"
        )
        with pytest.raises(meshcommon.AirFailed, match=r"\(boom\); give the air more room or use a finer size there"):
            meshcommon._swept_stages({"swept_add": []}, 3)  # an ordinary Study: as before
    finally:
        gmsh.finalize()


def bar_section(x0=18.0, x1=22.0):
    """One quad x x0..x1, z -1..1 in the plane y = 0."""
    xyz = np.array([[x0, 0, -1], [x1, 0, -1], [x1, 0, 1], [x0, 0, 1]], float)
    return meshsweep.Section(xyz, np.zeros((0, 3), int), np.array([[0, 1, 2, 3]]), {})


def test_coarse_ring_has_twelve_stations():
    section = bar_section()
    piece = {"origin": [0, 0, 0], "axis": [0, 0, 1], "angle": 360.0, "advance": 0.0}
    ((_, rc, length, start),) = meshsweep._chain([piece], np.array([20.0, 0, 0]))
    for size in (1000.0, 60.0, 40.0):  # 1, 2 and 3 steps before
        positions = meshsweep.turned_positions(length, 360.0, size)
        assert len(positions) == 13
        V, cells = meshsweep.sweep(section, meshsweep.stations(piece, positions, rc)[:-1], closed=True)
        assert len(cells[5]) == 12 and (meshsweep._volume(V, cells[5], 5) > 0).all()
        assert meshsweep._flat(V, cells) == 0


def test_coarse_u_bend_is_not_flat():
    section = bar_section()
    piece = {"origin": [0, 0, 0], "axis": [0, 0, 1], "angle": 180.0, "advance": 0.0}
    ((_, rc, length, _),) = meshsweep._chain([piece], np.array([20.0, 0, 0]))
    one = meshsweep.stations(piece, meshsweep.graded_positions(length, 1000.0), rc)  # one step: the ends coplanar
    assert meshsweep._flat(*meshsweep.sweep(section, one)) == 1
    positions = meshsweep.turned_positions(length, 180.0, 1000.0)
    assert len(positions) == 7
    V, cells = meshsweep.sweep(section, meshsweep.stations(piece, positions, rc))
    assert (meshsweep._volume(V, cells[5], 5) > 0).all() and meshsweep._flat(V, cells) == 0


def test_turned_positions_station_at_each_cut():
    p = meshsweep.turned_positions(100.0, 90.0, 4.0, cuts=[37.0, 0.0, 100.0])
    assert np.isclose(p, 37.0).any() and p[0] == 0 and p[-1] == 100.0
    assert np.allclose(np.diff(p), 4.0, atol=0.5)
    assert np.allclose(meshsweep.turned_positions(100.0, 90.0, 4.0), meshsweep.graded_positions(100.0, 4.0))


def test_crossings_bisect_a_sample_near_the_plane():
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.model.add("crossings")
        vol = gmsh.model.occ.addBox(0, 0, -1, 1, 1, 2.0002)  # the vertical edges' middle samples at z = 1e-4
        gmsh.model.occ.synchronize()
        points = meshsweep._crossings(vol, np.zeros(3), np.array([0, 0, 1.0]), 1e-3)
    finally:
        gmsh.finalize()
    assert len(points) == 4
    assert np.abs(points[:, 2]).max() < 1e-9


def test_sweep_turns_each_element_as_it_faces():
    flat = grid(2, 1)
    quad = flat.quad.copy()
    quad[1] = quad[1][::-1]  # the second quad faces the other way, as gmsh's quad layers may
    section = meshsweep.Section(flat.xyz, flat.tri, quad, {})
    piece = {"origin": [0, 0, 0], "axis": [0, 0, 1], "angle": 0.0, "advance": 2.0}
    V, cells = meshsweep.sweep(section, meshsweep.stations(piece, [0, 1, 2]))
    assert (jacobians(V, cells[5], 1, 3, 4) > 0).all() and meshsweep._flat(V, cells) == 0


def test_cuts_on_the_second_turn_of_a_helix():
    # a corner a quarter turn past the first whole turn of a 1.5-turn helix: at 2.5 of its 3 pi radians
    xyz = np.array([[1.0, 0, -0.2], [1.4, 0, -0.2], [1.4, 0, 0.2], [1.0, 0, 0.2]])
    section = meshsweep.Section(xyz, np.zeros((0, 3), int), np.array([[0, 1, 2, 3]]), {})
    piece = {"origin": [0, 0, 0], "axis": [0, 0, 1], "angle": 540.0, "advance": 15.0}
    ((_, rc, length, start),) = meshsweep._chain([piece], np.array([1.2, 0, 0]))
    corner = _moved_all(meshsweep.stations(piece, [5 * length / 6], rc), xyz[2])[0]
    cuts = meshsweep._cuts(piece, rc, length, start, section, [corner], 1e-6)
    assert len(cuts) == 1 and np.isclose(cuts[0], 5 * length / 6)  # not at a sixth, the same angle on turn one


def strand_section(rc=1.2, pitch=10.0, r=0.45, n=16):
    """A round strand's section at (rc, 0, 0), in the plane normal to the helix about z there (tilted to the axis),
    and its unit normal and binormal."""
    c = pitch / (2 * np.pi)
    tangent = np.array([0, rc, c]) / np.hypot(rc, c)
    normal, binormal = np.array([-1.0, 0, 0]), np.cross(tangent, [-1.0, 0, 0])
    a = 2 * np.pi * np.arange(n) / n
    xyz = np.vstack([[rc, 0, 0], [rc, 0, 0] + r * (np.cos(a)[:, None] * normal + np.sin(a)[:, None] * binormal)])
    tri = np.array([[0, 1 + k, 1 + (k + 1) % n] for k in range(n)])
    return meshsweep.Section(xyz, tri, np.zeros((0, 4), int), {}), normal, binormal


def test_helix_end_face_corners_are_no_cuts():
    # the end faces' own corners (a seam vertex anywhere on the circle) lie on the end stations: no sliver beside them
    section, normal, binormal = strand_section()
    piece = {"origin": [0, 0, 0], "axis": [0, 0, 1], "angle": 432.0, "advance": 12.0}
    chain = meshsweep._chain([piece], np.array([1.2, 0, 0]))
    ((_, rc, length, start),) = chain
    (end,) = meshsweep.stations(piece, [length], rc)
    rim = [np.array([1.2, 0, 0]) + 0.45 * (np.cos(a) * normal + np.sin(a) * binormal) for a in np.linspace(0, 6, 7)]
    corners = rim + [end[:3, :3] @ q + end[:3, 3] for q in rim]
    cuts = meshsweep._cuts(piece, rc, length, start, section, corners, 2.5e-5 * 15)
    assert cuts == []
    skin = {"depth": 0.2, "per_depth": 2.0, "layer": 2.0}
    at = _moved_all(meshsweep._path(chain, 0.4, skin, (True, True), [cuts]), np.array([1.2, 0, 0]))
    steps = np.linalg.norm(np.diff(at, axis=0), axis=1)
    assert abs(steps[0] - 0.1) < 1e-3 and abs(steps[-1] - 0.1) < 1e-3


def test_helix_cut_near_an_end_is_merged():
    section, normal, _ = strand_section()
    piece = {"origin": [0, 0, 0], "axis": [0, 0, 1], "angle": 432.0, "advance": 12.0}
    chain = meshsweep._chain([piece], np.array([1.2, 0, 0]))
    ((_, rc, length, start),) = chain
    near = meshsweep.stations(piece, [0.003], rc)[0]
    corner = near[:3, :3] @ (np.array([1.2, 0, 0]) + 0.45 * normal) + near[:3, 3]
    cuts = meshsweep._cuts(piece, rc, length, start, section, [corner], 1e-6)
    assert len(cuts) == 1 and abs(cuts[0] - 0.003) < 1e-9  # found at its station
    at = _moved_all(meshsweep._path(chain, 0.4, None, (False, False), [cuts]), np.array([1.2, 0, 0]))
    assert np.linalg.norm(np.diff(at, axis=0), axis=1).min() > 0.3  # merged into the end station


def box_job(folder):
    """A job meshing one box, for meshcommon.run."""
    os.mkdir(folder / "geometry")
    write_box(str(folder / "geometry" / "vol_1.brep"), 0, 0, 0, 1, 1, 1)
    job = {
        "model_name": "Model",
        "mesh_file": str(folder / "pre_geom.msh"),
        "volumes": [{"mat_id": 1, "name": "Box", "file": "geometry/vol_1.brep", "size": 0.5}],
        "surfaces": [],
        "sizes": [],
    }
    (folder / "job.json").write_text(json.dumps(job), encoding="utf-8")
    return str(folder / "job.json")


@pytest.mark.parametrize("failures", [1, 2])
def test_failed_air_mesh_is_tried_once_more(tmp_path, monkeypatch, capsys, failures):
    import mesher  # here: it needs the path above, and only this test runs it in-process

    real, calls = meshcommon.generate, []

    def generate(job, dim):  # gmsh's air mesh beside a swept body fails the first failures times
        calls.append(dim)
        if len(calls) <= failures:
            raise meshcommon.AirFailed("gmsh could not mesh around the swept bodies (overlapping facets)")
        real(job, dim)

    monkeypatch.setattr(meshcommon, "generate", generate)
    path = box_job(tmp_path)
    if failures == 1:
        meshcommon.run(path, mesher.build, 3)
        assert os.path.isfile(tmp_path / "pre_geom.msh")
        err = capsys.readouterr().err  # a plain note: the advice is only for the final failure
        assert (
            "Swept Body: gmsh could not mesh the air around the swept bodies; meshing once more from the start" in err
        )
        assert "overlapping facets" not in err
    else:
        with pytest.raises(meshcommon.AirFailed, match="overlapping facets"):
            meshcommon.run(path, mesher.build, 3)
        assert not os.path.isfile(tmp_path / "pre_geom.msh")
    assert len(calls) == 2


def box_group_job(folder):
    """A job of one Symmetric Group: the box of box_job as its cell, one copy, for meshgroups.run."""
    path = box_job(folder)
    with open(path, encoding="utf-8") as fh:
        cell = json.load(fh)
    group = {
        "name": "Boxes",
        "side": "fixed",
        "job": {"volumes": cell["volumes"], "surfaces": [], "sizes": []},
        "cells": [1],
        "transforms": [[1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]],
        "parts": [{"mat_id": 7, "name": "Box"}],
        "rows": [{"cell": 1, "file": None, "parts": [0]}],
    }
    job = {"model_name": "Model", "mesh_file": cell["mesh_file"], "options": {}, "symmetric": {"groups": [group]}}
    (folder / "job.json").write_text(json.dumps(job), encoding="utf-8")
    return path


@pytest.mark.parametrize(
    "failures, meshed",
    [(("pyramids",), True), (("air",), True), (("pyramids", "air"), True), (("air", "air"), False)],
)
def test_symmetric_job_is_meshed_again_like_an_ordinary_one(tmp_path, monkeypatch, capsys, failures, meshed):
    # the bounded retry of meshcommon.run (once without the pushed-out pyramids, once more after a failed air mesh)
    import mesher
    import meshgroups

    real, calls = meshgroups.mesh, []

    def mesh(job, folder, build, dim):
        calls.append(job.get("optimize_pyramids"))
        if len(calls) <= len(failures):
            if failures[len(calls) - 1] == "pyramids":
                raise meshcommon.PyramidsFailed("PLC Error")
            raise meshcommon.AirFailed("gmsh could not mesh Air around the swept bodies (overlapping facets)")
        return real(job, folder, build, dim)

    monkeypatch.setattr(meshgroups, "mesh", mesh)
    path = box_group_job(tmp_path)
    if meshed:
        meshgroups.run(path, mesher.build, 3)
        assert os.path.isfile(tmp_path / "pre_geom.msh")
        assert len(calls) == len(failures) + 1
    else:
        with pytest.raises(meshcommon.AirFailed, match="overlapping facets"):
            meshgroups.run(path, mesher.build, 3)
        assert len(calls) == 2
    if "pyramids" in failures:
        assert calls[1:] == [0] * (len(calls) - 1)  # meshed without the pushed-out pyramids from then on
        assert "could not optimise the pyramids" in capsys.readouterr().err


def test_real_faces_of_a_free_face_split_in_the_cell_model(tmp_path):
    # the bar x 0..1, y 0..1, z 0..4 fragmented with a block x 0..0.5, y 1..2: its free face y = 1 is split at x = 0.5,
    # and neither piece is the file's face whole. With no neighbours given, only the fallback makes them real
    (tmp_path / "geometry").mkdir()
    write_box(str(tmp_path / "geometry" / "bar.brep"), 0, 0, 0, 1, 1, 4)
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        occ = gmsh.model.occ
        bar = occ.addBox(0, 0, 0, 1, 1, 4)
        occ.synchronize()
        (top,) = [t for _, t in gmsh.model.getEntities(2) if abs(occ.getCenterOfMass(2, t)[1] - 1) < 1e-9]
        occ.copy([(2, top)])
        occ.remove([(3, bar)], recursive=True)
        occ.synchronize()
        gmsh.write(str(tmp_path / "geometry" / "free_1.brep"))  # the whole face y = 1
        gmsh.clear()
        _, out = occ.fragment([(3, occ.addBox(0, 0, 0, 1, 1, 4))], [(3, occ.addBox(0, 1, 0, 0.5, 1, 4))])
        occ.synchronize()
        vol = out[0][0][1]
        faces = [abs(t) for _, t in gmsh.model.getBoundary([(3, vol)], oriented=False)]
        entry = {"name": "Bar", "free_faces": ["geometry/free_1.brep"]}
        real = meshsweep._real_faces(entry, str(tmp_path), faces, set(), math.sqrt(18))
        on_top = sorted(
            round(occ.getCenterOfMass(2, f)[0], 6) for f in faces if abs(occ.getCenterOfMass(2, f)[1] - 1) < 1e-9
        )
        assert on_top == [0.25, 0.75]  # split in two
        assert sorted(round(occ.getCenterOfMass(2, f)[0], 6) for f in real) == [0.25, 0.75]  # both, and nothing else
    finally:
        gmsh.finalize()
