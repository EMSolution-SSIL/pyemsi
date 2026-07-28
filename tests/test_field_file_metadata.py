import os

import numpy as np
import pyvista as pv

from pyemsi.gui._field_file_metadata import inspect_field_file


def _field_mesh(point_scalar_max: float = 4.0) -> pv.ImageData:
    mesh = pv.ImageData(dimensions=(3, 3, 3))
    mesh.point_data["Point Scalar"] = np.linspace(-2.0, point_scalar_max, mesh.n_points)
    point_vectors = np.zeros((mesh.n_points, 3))
    point_vectors[0] = [3.0, 4.0, 0.0]
    mesh.point_data["Point Vector"] = point_vectors
    mesh.point_data["Unsupported Tensor"] = np.zeros((mesh.n_points, 9))
    mesh.point_data["vtkOriginalPointIds"] = np.arange(mesh.n_points)
    mesh.point_data["Inconsistent"] = np.arange(mesh.n_points, dtype=float)
    mesh.cell_data["Cell Scalar"] = np.linspace(1.0, 3.0, mesh.n_cells)
    mesh.cell_data["Cell Vector"] = np.ones((mesh.n_cells, 3))
    mesh.cell_data["Inconsistent"] = np.ones((mesh.n_cells, 3))
    return mesh


def test_inspect_field_file_discovers_arrays_associations_ranges_and_scales(tmp_path):
    mesh = _field_mesh()
    field_path = tmp_path / "field.vti"
    mesh.save(field_path)

    metadata = inspect_field_file(field_path)

    assert metadata.resolved_path == os.path.abspath(os.path.normpath(os.fspath(field_path)))
    assert metadata.scalar_names == ["Point Scalar", "Cell Scalar"]
    assert metadata.contour_names == ["Point Scalar"]
    assert metadata.vector_names == ["Point Vector", "Cell Vector"]
    assert metadata.scalar_associations == {
        "Point Scalar": frozenset({"point"}),
        "Cell Scalar": frozenset({"cell"}),
    }
    assert metadata.vector_associations == {
        "Point Vector": frozenset({"point"}),
        "Cell Vector": frozenset({"cell"}),
    }
    assert metadata.array_ranges["Point Scalar"] == {"min": -2.0, "max": 4.0}
    assert metadata.array_ranges["Point Vector"] == {"min": 0.0, "max": 5.0}
    assert np.isclose(metadata.array_ranges["Cell Vector"]["max"], np.sqrt(3.0))
    assert metadata.vector_scale_names["Point Vector"] == ["Point Scalar", "Point Vector"]
    assert metadata.vector_scale_names["Cell Vector"] == ["Cell Scalar", "Cell Vector"]
    assert "Unsupported Tensor" not in metadata.scale_names
    assert "vtkOriginalPointIds" not in metadata.scale_names
    assert "Inconsistent" not in metadata.scale_names
    assert "Inconsistent" not in metadata.scalar_names
    assert "Inconsistent" not in metadata.vector_names
    assert metadata.mesh_length > 0.0


def test_inspect_field_file_scans_nested_multiblock_data(tmp_path, monkeypatch):
    field_path = tmp_path / "nested.vtm"
    field_path.write_text("placeholder", encoding="utf-8")
    first = _field_mesh()
    first.point_data["Mixed Association"] = np.arange(first.n_points, dtype=float)
    second = pv.ImageData(dimensions=(2, 2, 2))
    second.point_data["Second Scalar"] = np.arange(second.n_points, dtype=float)
    second.cell_data["Mixed Association"] = np.arange(second.n_cells, dtype=float)
    nested = pv.MultiBlock([first, pv.MultiBlock([second])])

    class _Reader:
        def read(self):
            return nested

    monkeypatch.setattr(pv, "get_reader", lambda _path: _Reader())

    metadata = inspect_field_file(field_path)

    assert metadata.scalar_names == ["Point Scalar", "Cell Scalar", "Second Scalar"]
    assert metadata.contour_names == ["Point Scalar", "Second Scalar"]
    assert "Mixed Association" not in metadata.scale_names


def test_inspect_field_file_scans_all_time_steps_and_restores_reader(tmp_path, monkeypatch):
    field_path = tmp_path / "series.pvd"
    field_path.write_text("placeholder", encoding="utf-8")
    meshes = [_field_mesh(point_scalar_max=4.0), _field_mesh(point_scalar_max=12.0)]
    meshes[1].point_data["Later Scalar"] = np.arange(meshes[1].n_points, dtype=float)

    class _TimeReader:
        def __init__(self):
            self.time_values = [0.0, 1.0]
            self.active_time_value = 1.0

        @property
        def number_time_points(self):
            return len(self.time_values)

        def set_active_time_point(self, index):
            self.active_time_value = self.time_values[index]

        def set_active_time_value(self, value):
            self.active_time_value = value

        def read(self):
            return meshes[self.time_values.index(self.active_time_value)]

    reader = _TimeReader()
    monkeypatch.setattr(pv, "TimeReader", _TimeReader)
    monkeypatch.setattr(pv, "get_reader", lambda _path: reader)

    metadata = inspect_field_file(field_path)

    assert reader.active_time_value == 1.0
    assert metadata.array_ranges["Point Scalar"] == {"min": -2.0, "max": 12.0}
    assert "Later Scalar" in metadata.scalar_names


def test_inspect_field_file_ignores_nonfinite_values(tmp_path):
    mesh = pv.ImageData(dimensions=(2, 2, 2))
    mesh.point_data["Finite Scalar"] = np.array([np.nan, np.inf, -np.inf, 2.0, 4.0, 3.0, 2.0, 1.0])
    mesh.point_data["No Finite Values"] = np.full(mesh.n_points, np.nan)
    field_path = tmp_path / "nonfinite.vti"
    mesh.save(field_path)

    metadata = inspect_field_file(field_path)

    assert metadata.array_ranges["Finite Scalar"] == {"min": 1.0, "max": 4.0}
    assert "No Finite Values" in metadata.scalar_names
    assert "No Finite Values" not in metadata.array_ranges
