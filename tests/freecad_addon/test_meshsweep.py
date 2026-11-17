"""Swept Body: the cross-section mesh and the swept volume mesh (meshsweep.py, a mesher module).
Run from the repo root: pixi run -e addon pytest tests/freecad_addon/test_meshsweep.py"""

import os
import sys

import gmsh
import numpy as np
import pytest

from .test_mesher import MESHER, write_rect
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
