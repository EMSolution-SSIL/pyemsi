"""Array operations on frozen meshes: copy with transforms, node join, boundary, quad pyramids (numpy only)."""

import numpy as np
import pytest

from emsolution import meshfrozen

ID = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
MX = [-1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
SHIFT = [1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
CUBE = np.array([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0), (0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)], float)
HEX = {"a": {5: np.arange(8)[None]}}


def signed(V, c):  # triple product of the three edges at the first corner of a hexahedron
    return np.dot(np.cross(V[c[1]] - V[c[0]], V[c[3]] - V[c[0]]), V[c[4]] - V[c[0]])


def test_mirrored_copy_keeps_positive_volume():
    V, out = meshfrozen.copy_mesh(CUBE, HEX, [ID, MX])
    assert signed(V, out[("a", 0)][5][0]) > 0 and signed(V, out[("a", 1)][5][0]) > 0


def test_copies_share_nodes_where_they_touch():
    V, out = meshfrozen.copy_mesh(CUBE, HEX, [ID, SHIFT])
    assert len(V) == 12


def test_join_stops_at_the_tolerance():
    assert meshfrozen.join_nodes(np.array([(0, 0, 0), (0, 0, 1e-8), (0, 0, 1e-3)], float))[0] == 2


def test_boundary_of_two_touching_cubes():
    V, out = meshfrozen.copy_mesh(CUBE, HEX, [ID, SHIFT])
    b = meshfrozen.boundary(V, list(out.values()), 3)
    assert len(b.quad) == 10 and b.over_used == 0 and b.shared_area == pytest.approx(1.0)


def test_face_of_three_elements_is_counted():
    V, out = meshfrozen.copy_mesh(CUBE, HEX, [ID, SHIFT])
    b = meshfrozen.boundary(V, list(out.values()) + [out[("a", 0)]], 3)
    assert b.over_used > 0


def test_pyramid_points_away_from_its_hexahedron():
    b = meshfrozen.boundary(CUBE, [HEX["a"]], 3)
    V2, pyr, tris = meshfrozen.quad_pyramids(CUBE, b.quad)
    assert (np.abs(V2[pyr[:, 4]] - 0.5) > 0.5).any(axis=1).all() and len(tris) == 24


def test_boundary_of_two_squares_in_2d():
    xy = np.array([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)], float)
    V, out = meshfrozen.copy_mesh(xy, {"a": {3: np.arange(4)[None]}}, [ID, SHIFT])
    b = meshfrozen.boundary(V, list(out.values()), 2)
    assert len(b.edge) == 6 and b.shared_area == pytest.approx(1.0)
