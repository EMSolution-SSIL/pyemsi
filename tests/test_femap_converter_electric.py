from pathlib import Path

import numpy as np
import pyvista as pv
import pytest
from vtk import VTK_VERTEX

from pyemsi.tools.FemapConverter import FemapConverter


def _single_vertex_mesh() -> pv.UnstructuredGrid:
    cells = np.array([1, 0])
    cell_types = np.array([VTK_VERTEX], dtype=np.uint8)
    points = np.array([[0.0, 0.0, 0.0]])
    return pv.UnstructuredGrid(cells, cell_types, points)


def _electric_test_arrays() -> dict[str, np.ndarray]:
    return {
        "ELEC-node-1": np.array([1.0], dtype=np.float32),
        "ELEC-node-2": np.array([2.0], dtype=np.float32),
        "ELEC-node-3": np.array([3.0], dtype=np.float32),
        "ELEC-node-4": np.array([4.0], dtype=np.float32),
        "ELEC-node-5": np.array([5.0], dtype=np.float32),
        "ELEC-elem-1": np.array([6.0], dtype=np.float32),
        "ELEC-elem-2": np.array([7.0], dtype=np.float32),
        "ELEC-elem-3": np.array([8.0], dtype=np.float32),
        "ELEC-elem-4": np.array([9.0], dtype=np.float32),
        "ELEC-elem-5": np.array([10.0], dtype=np.float32),
    }


def _converter_with_electric_arrays() -> FemapConverter:
    converter = FemapConverter.__new__(FemapConverter)
    converter.get_data_array = lambda step, vectors: _electric_test_arrays()
    converter.vectors = {"electric": [{"set_id": 1}]}
    return converter


@pytest.mark.parametrize(
    ("input_control", "vector_name", "magnitude_name", "scalar_name"),
    [
        (
            {"2_Analysis_Type": {"STATIC": 2}, "10_3_Post_Files": {"CURRENT": 1}},
            "D-Vec (C/m^2)",
            "D-Mag (C/m^2)",
            "Electric Energy Density (J/m^3)",
        ),
        (
            {"2_Analysis_Type": {"STATIC": 2}, "10_3_Post_Files": {"CURRENT": 2}},
            "E-Vec (V/m)",
            "E-Mag (V/m)",
            "Electric Energy Density (J/m^3)",
        ),
        (
            {"2_Analysis_Type": {"STATIC": 3}, "10_3_Post_Files": {"CURRENT": 1}},
            "J-e-Vec (A/m^2)",
            "J-e-Mag (A/m^2)",
            "Joule Loss (W/m^3)",
        ),
    ],
)
def test_process_electric_field_uses_input_control_labels(input_control, vector_name, magnitude_name, scalar_name):
    converter = _converter_with_electric_arrays()
    mesh = _single_vertex_mesh()
    converter.input_control = input_control

    converter._process_electric_field(1, mesh)

    np.testing.assert_allclose(mesh.point_data[vector_name], np.array([[1.0, 2.0, 3.0]], dtype=np.float32))
    np.testing.assert_allclose(mesh.point_data[magnitude_name], np.array([4.0], dtype=np.float32))
    np.testing.assert_allclose(mesh.point_data["Potential (V)"], np.array([5.0], dtype=np.float32))
    np.testing.assert_allclose(mesh.cell_data[vector_name], np.array([[6.0, 7.0, 8.0]], dtype=np.float32))
    np.testing.assert_allclose(mesh.cell_data[magnitude_name], np.array([9.0], dtype=np.float32))
    np.testing.assert_allclose(mesh.cell_data[scalar_name], np.array([10.0], dtype=np.float32))


def test_process_electric_field_warns_and_defaults_without_input_control(caplog):
    converter = _converter_with_electric_arrays()
    mesh = _single_vertex_mesh()
    converter.input_control = None

    with caplog.at_level("WARNING"):
        converter._process_electric_field(1, mesh)

    assert "assuming STATIC=3 and CURRENT=1" in caplog.text
    np.testing.assert_allclose(mesh.point_data["J-e-Vec (A/m^2)"], np.array([[1.0, 2.0, 3.0]], dtype=np.float32))
    np.testing.assert_allclose(mesh.point_data["J-e-Mag (A/m^2)"], np.array([4.0], dtype=np.float32))
    np.testing.assert_allclose(mesh.point_data["Potential (V)"], np.array([5.0], dtype=np.float32))
    np.testing.assert_allclose(mesh.cell_data["J-e-Vec (A/m^2)"], np.array([[6.0, 7.0, 8.0]], dtype=np.float32))
    np.testing.assert_allclose(mesh.cell_data["J-e-Mag (A/m^2)"], np.array([9.0], dtype=np.float32))
    np.testing.assert_allclose(mesh.cell_data["Joule Loss (W/m^3)"], np.array([10.0], dtype=np.float32))


def test_run_allows_current_and_electric_together():
    converter = FemapConverter.__new__(FemapConverter)
    converter.current_file = Path("current")
    converter.electric_file = Path("electric")
    converter._mesh_file = Path("mesh")
    converter._force_2d = False

    calls = []

    def _record_build(mesh_file, force_2d=False):
        calls.append(("build", mesh_file, force_2d))

    converter._build_mesh = _record_build
    converter.parse_data_files = lambda: calls.append(("parse",))
    converter.init_pvd = lambda: calls.append(("pvd",))
    converter.time_stepping = lambda: calls.append(("time",))

    converter.run()

    assert calls == [
        ("build", Path("mesh"), False),
        ("parse",),
        ("pvd",),
        ("time",),
    ]
