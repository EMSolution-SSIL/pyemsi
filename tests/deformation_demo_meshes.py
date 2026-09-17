"""Synthetic 2D and 3D meshes used to demonstrate deformation visualization.

Not a test module itself (no ``test_`` prefix, so pytest won't collect it).
Imported by ``test_plotter_deformation_visual.py`` and by
``interactive_deformation_demo.py``.
"""

import numpy as np
import pyvista as pv
from vtk import VTK_HEXAHEDRON

# Field names match the real, domain-specific names the Plotter's
# set_scalar()/set_contour()/set_vector() expect (see plotter.py Literal
# annotations), so this demo exercises the same code paths as real data.
SCALAR_FIELD = "B-Mag (T)"
CONTOUR_FIELD = "Flux (A/m)"
VECTOR_FIELD = "B-Vec (T)"
DISPLACEMENT_FIELD = "Displacement"


def build_2d_plate_mesh() -> pv.PolyData:
    """A flat rectangular plate (2D quad mesh) clamped at x=0.

    The displacement field bends the plate upward like a diving board: zero
    deflection at the clamped edge, growing toward the free edge.
    """
    nx, ny = 9, 5
    x = np.linspace(0.0, 4.0, nx)
    y = np.linspace(0.0, 2.0, ny)
    xx, yy = np.meshgrid(x, y, indexing="xy")
    points = np.column_stack([xx.ravel(), yy.ravel(), np.zeros(xx.size)])

    faces = []
    for j in range(ny - 1):
        for i in range(nx - 1):
            p0 = j * nx + i
            p1 = p0 + 1
            p2 = p0 + nx + 1
            p3 = p0 + nx
            faces.extend([4, p0, p1, p2, p3])

    mesh = pv.PolyData(points, faces=np.array(faces))

    x_norm = xx.ravel() / x[-1]
    y_norm = yy.ravel() / y[-1]

    mesh.point_data[SCALAR_FIELD] = x_norm
    mesh.point_data[CONTOUR_FIELD] = np.sin(x_norm * np.pi) * np.cos(y_norm * np.pi / 2.0)

    vectors = np.zeros_like(points)
    vectors[:, 0] = 0.3
    vectors[:, 2] = 0.1 * np.sin(y_norm * np.pi)
    mesh.point_data[VECTOR_FIELD] = vectors

    displacement = np.zeros_like(points)
    displacement[:, 2] = x_norm**2 * 1.5
    mesh.point_data[DISPLACEMENT_FIELD] = displacement

    return mesh


def build_3d_beam_mesh() -> pv.UnstructuredGrid:
    """A small hexahedral cantilever beam (3D mesh) clamped at x=0.

    The displacement field sags the beam downward, like a bending cantilever:
    zero deflection at the clamped end, growing toward the free tip.
    """
    nx, ny, nz = 9, 3, 3
    x = np.linspace(0.0, 4.0, nx)
    y = np.linspace(0.0, 1.0, ny)
    z = np.linspace(0.0, 1.0, nz)
    xx, yy, zz = np.meshgrid(x, y, z, indexing="ij")
    points = np.column_stack([xx.ravel(), yy.ravel(), zz.ravel()])

    def point_id(i: int, j: int, k: int) -> int:
        return i * ny * nz + j * nz + k

    cells = []
    for i in range(nx - 1):
        for j in range(ny - 1):
            for k in range(nz - 1):
                n0 = point_id(i, j, k)
                n1 = point_id(i + 1, j, k)
                n2 = point_id(i + 1, j + 1, k)
                n3 = point_id(i, j + 1, k)
                n4 = point_id(i, j, k + 1)
                n5 = point_id(i + 1, j, k + 1)
                n6 = point_id(i + 1, j + 1, k + 1)
                n7 = point_id(i, j + 1, k + 1)
                cells.extend([8, n0, n1, n2, n3, n4, n5, n6, n7])

    n_cells = (nx - 1) * (ny - 1) * (nz - 1)
    cell_types = np.full(n_cells, VTK_HEXAHEDRON)
    grid = pv.UnstructuredGrid(np.array(cells), cell_types, points)

    x_norm = xx.ravel() / x[-1]

    grid.point_data[SCALAR_FIELD] = x_norm
    grid.point_data[CONTOUR_FIELD] = np.sin(x_norm * np.pi)

    vectors = np.zeros_like(points)
    vectors[:, 2] = -0.2 * x_norm
    grid.point_data[VECTOR_FIELD] = vectors

    displacement = np.zeros_like(points)
    displacement[:, 2] = -1.0 * x_norm**2
    grid.point_data[DISPLACEMENT_FIELD] = displacement

    return grid
