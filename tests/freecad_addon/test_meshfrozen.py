"""Array operations on frozen meshes: copy with transforms, node join, boundary, quad pyramids, shells and regions."""

import gmsh
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


TET = np.array([(0, 2, 1), (0, 1, 3), (0, 3, 2), (1, 2, 3)])
CUBE_TRIS = np.array(
    [
        (0, 2, 1),
        (0, 3, 2),
        (4, 5, 6),
        (4, 6, 7),
        (0, 1, 5),
        (0, 5, 4),
        (2, 3, 7),
        (2, 7, 6),
        (1, 2, 6),
        (1, 6, 5),
        (3, 0, 4),
        (3, 4, 7),
    ]
)


def square(half, first):
    """The corners of a square about the origin, and its four edges numbered from node first."""
    corners = [(-half, -half, 0), (half, -half, 0), (half, half, 0), (-half, half, 0)]
    return corners, [(first + k, first + (k + 1) % 4) for k in range(4)]


def nested_cubes():
    """Nodes and triangles of a cube of side 3 around a unit cube; the cube of side 3 has facets 0 to 11."""
    V = np.vstack([3.0 * CUBE - 1.0, CUBE])
    return V, np.vstack([CUBE_TRIS, CUBE_TRIS + 8])


def test_shells_of_two_separate_tetrahedra():
    found = meshfrozen.shells(np.vstack([TET, TET + 4]))
    assert [sorted(s.tolist()) for s in found] == [[0, 1, 2, 3], [4, 5, 6, 7]]


def test_open_surface_is_refused():
    with pytest.raises(meshfrozen.FrozenError):
        meshfrozen.shells(TET[1:])


def test_edge_of_three_faces_is_refused():
    with pytest.raises(meshfrozen.FrozenError):
        meshfrozen.shells(np.vstack([TET, [(0, 1, 9), (0, 9, 1), (0, 1, 8)]]))


def test_node_used_three_times_is_refused_in_2d():
    with pytest.raises(meshfrozen.FrozenError):
        meshfrozen.shells(np.array([(0, 1), (1, 2), (2, 0), (0, 3), (3, 4), (4, 0), (0, 5)]))


def test_loops_in_2d_are_found_by_nodes():
    edges = np.array(square(1, 0)[1] + square(2, 4)[1])
    assert [sorted(s.tolist()) for s in meshfrozen.shells(edges)] == [[0, 1, 2, 3], [4, 5, 6, 7]]


def test_cube_inside_a_cube_nests():
    V, facets = nested_cubes()
    found = meshfrozen.shells(facets)
    assert len(found) == 2
    assert meshfrozen.nest(V, facets, found) == [(0, [1])]


def test_nest_does_not_need_the_facets_oriented_alike():  # a surface from gmsh is oriented face by face
    V, facets = nested_cubes()
    facets[[0, 1, 5, 13]] = facets[[0, 1, 5, 13]][:, ::-1]
    assert meshfrozen.nest(V, facets, meshfrozen.shells(facets)) == [(0, [1])]


def test_ring_gives_two_regions():  # three nested squares: the inner region is a new outer boundary
    V, edges = [], []
    for half in (3, 2, 1):
        corners, sides = square(half, len(V))
        V += corners
        edges += sides
    edges = np.array(edges)
    assert meshfrozen.nest(np.array(V, float), edges, meshfrozen.shells(edges)) == [(0, [1]), (2, [])]


def test_nest_in_the_zx_plane():
    V, edges = [], []
    for half in (2, 1):
        corners, sides = square(half, len(V))
        V += [(x, 0.0, y) for x, y, _ in corners]
        edges += sides
    edges = np.array(edges)
    assert meshfrozen.nest(np.array(V, float), edges, meshfrozen.shells(edges)) == [(0, [1])]


@pytest.fixture
def model():
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    gmsh.model.add("test")
    yield
    gmsh.finalize()


def tet_volume(V, tets):
    t = V[tets]
    return float(
        np.abs(np.einsum("ij,ij->i", np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0]), t[:, 3] - t[:, 0])).sum() / 6
    )


def test_mesh_region_3d_keeps_the_frozen_nodes_and_faces(model):
    V, facets = nested_cubes()
    V2, per_type = meshfrozen.mesh_region(V, facets, np.arange(12), [np.arange(12, 24)], 0.5, 3)
    assert np.array_equal(V2[: len(V)], V)
    assert list(per_type) == [4]
    b = meshfrozen.boundary(V2, [per_type], 3)
    assert b.over_used == 0
    assert {tuple(sorted(row)) for row in b.tri.tolist()} == {tuple(sorted(row)) for row in facets.tolist()}
    assert tet_volume(V2, per_type[4]) == pytest.approx(27 - 1)


def test_mesh_region_3d_takes_only_the_nodes_of_its_shells(model):  # the other nodes keep their numbers and places
    V, facets = nested_cubes()
    V = np.vstack([V, [(50.0, 50.0, 50.0)]])
    V2, per_type = meshfrozen.mesh_region(V, facets, np.arange(12), [], 0.7, 3)
    assert np.array_equal(V2[: len(V)], V)
    assert tet_volume(V2, per_type[4]) == pytest.approx(27)
    assert not set(range(8, len(V))) & set(np.unique(per_type[4]).tolist())


def test_mesh_region_2d_is_a_polygon_with_holes(model):
    corners, edges = square(3, 0)
    inner, holes = square(1, 4)
    V = np.array([(x, 0.0, z) for x, z, _ in corners + inner], float)  # the plane y = 0, as in a ZX Study
    facets = np.array(edges + holes)
    V2, per_type = meshfrozen.mesh_region(V, facets, np.arange(4), [np.arange(4, 8)], 0.8, 2)
    assert np.array_equal(V2[: len(V)], V) and set(per_type) == {2}
    b = meshfrozen.boundary(V2, [per_type], 2)
    assert {tuple(sorted(e)) for e in b.edge.tolist()} == {tuple(sorted(e)) for e in facets.tolist()}
    assert float(meshfrozen._area(V2, per_type[2]).sum()) == pytest.approx(36 - 4)
    assert np.abs(V2[:, 1]).max() == 0


def test_mesh_region_leaves_the_options_as_they_were(model):
    gmsh.option.setNumber("Mesh.Renumber", 1)
    gmsh.option.setNumber("Mesh.MeshSizeMax", 7.0)
    V, facets = nested_cubes()
    meshfrozen.mesh_region(V, facets, np.arange(12), [np.arange(12, 24)], 0.5, 3)
    assert gmsh.option.getNumber("Mesh.Renumber") == 1 and gmsh.option.getNumber("Mesh.MeshSizeMax") == 7.0


def test_on_surface(model):
    """A chord of the lateral face, a rim triangle of the end cap and a facet of the top with its owner outside."""
    gmsh.model.occ.addCylinder(0, 0, 0, 0, 0, 2, 1)
    gmsh.model.occ.synchronize()
    faces = [abs(t) for _, t in gmsh.model.getBoundary([(3, 1)], oriented=False)]
    lateral = next(f for f in faces if gmsh.model.getType(2, f) == "Cylinder")
    bottom = next(f for f in faces if gmsh.model.occ.getCenterOfMass(2, f)[2] < 0.5 and f != lateral)
    top = next(f for f in faces if f not in (lateral, bottom))
    ring = lambda a, z: (np.cos(a), np.sin(a), z)  # noqa: E731 - one rim point
    V = np.array([ring(0, 0), ring(0.1, 0), ring(0.1, 2), ring(0.2, 0), (0, 0, 2), (0.5, 0, 2), (0, 0.5, 2)], float)
    V = np.vstack([V, [(0, 0, 1), (0.1, 0, 1), (0, 0.1, 1)]])
    facets = np.array([[0, 1, 2], [0, 1, 3], [4, 5, 6], [7, 8, 9]])
    owners = np.array([(0.5, 0, 1), (0.5, 0, -1), (0.2, 0.2, 5), (0, 0, 1)], float)
    on = meshfrozen.on_surface(V, facets, owners, faces, 3)
    found = dict(zip(on.index.tolist(), zip(on.face.tolist(), on.inside.tolist())))
    assert found == {0: (lateral, True), 1: (bottom, False), 2: (top, False)}  # the last facet lies on nothing


def test_on_surface_of_a_line_in_2d(model):
    gmsh.model.occ.addRectangle(0, 0, 0, 4, 2)
    gmsh.model.occ.synchronize()
    lines = [abs(t) for _, t in gmsh.model.getBoundary([(2, 1)], oriented=False)]
    V = np.array([(1, 0, 0), (2, 0, 0), (1, 1, 0), (2, 1, 0)], float)
    on = meshfrozen.on_surface(V, np.array([[0, 1], [2, 3]]), np.array([(1.5, 1, 0), (1.5, 2, 0)], float), lines, 2)
    assert on.index.tolist() == [0] and on.inside.tolist() == [True]


def test_on_facets_takes_a_point_over_a_chord():  # a point of a curved wall is off the flat facet by the sagitta
    V = np.array([(0, 0, 0), (1, 0, 0), (0, 1, 0)], float)
    tri = np.array([[0, 1, 2]])
    assert meshfrozen.on_facets(V, tri, np.array([0.25, 0.25, 0.05]), 1e-6)
    assert not meshfrozen.on_facets(V, tri, np.array([0.25, 0.25, 0.5]), 1e-6)  # too far off its plane
    assert not meshfrozen.on_facets(V, tri, np.array([0.8, 0.8, 0.0]), 1e-6)  # beside the triangle


def test_on_facets_of_edges_in_2d():
    V = np.array([(0, 0, 0), (2, 0, 0)], float)
    edge = np.array([[0, 1]])
    assert meshfrozen.on_facets(V, edge, np.array([1.0, 0.1, 0.0]), 1e-6)
    assert not meshfrozen.on_facets(V, edge, np.array([3.0, 0.0, 0.0]), 1e-6)
