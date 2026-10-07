import sys

import numpy as np
import pyvista as pv
from vtk import VTK_VERTEX

from pyemsi.tools.FemapConverter import FemapConverter

IRON_LOSS_NAMES = [
    "Eddy Loss Density (W/m^3)",
    "Eddy Loss (W)",
    "Hysteresis Loss Density (W/m^3)",
    "Hysteresis Loss (W)",
    "Iron Loss Density (W/m^3)",
    "Iron Loss (W)",
]


def _single_vertex_mesh() -> pv.UnstructuredGrid:
    return pv.UnstructuredGrid(np.array([1, 0]), np.array([VTK_VERTEX], dtype=np.uint8), np.array([[0.0, 0.0, 0.0]]))


def test_process_iron_loss_field_maps_all_six_vectors():
    converter = FemapConverter.__new__(FemapConverter)
    converter.vectors, converter.iron_loss_sets = {"iron_loss": []}, {40: {}}
    converter.get_data_array = lambda step, vectors: {
        f"IRON_LOSS-elem-{index}": np.array([float(index)], dtype=np.float32) for index in range(1, 7)
    }
    mesh = _single_vertex_mesh()

    converter._process_iron_loss_field(40, mesh)

    for index, name in enumerate(IRON_LOSS_NAMES, start=1):
        np.testing.assert_allclose(mesh.cell_data[name], np.array([float(index)], dtype=np.float32))


def test_parse_data_file_keeps_iron_loss_out_of_steps(monkeypatch):
    file_sets = {
        "magnetic": {1: {"title": "STEP:1", "value": 0.01}, 2: {"title": "STEP:2", "value": 0.02}},
        "iron_loss": {40: {"title": "STEP:40", "value": 0.04}},
    }

    class _FakeParser:
        def __init__(self, path):
            self.name = path

        def parse(self):
            pass

        def get_output_sets(self):
            return file_sets[self.name]

        def get_output_vectors(self):
            return []

    monkeypatch.setattr(sys.modules[FemapConverter.__module__], "FEMAPParser", _FakeParser)
    converter = FemapConverter.__new__(FemapConverter)
    converter.sets, converter.vectors = {}, {}

    converter.parse_data_file("iron_loss", "iron_loss")
    converter.parse_data_file("magnetic", "magnetic")

    assert list(converter.sets) == [1, 2]  # iron_loss adds no steps of its own
    assert list(converter.iron_loss_sets) == [40]


def test_process_iron_loss_field_writes_averaged_set_on_every_step():
    # iron_loss holds averaged sets only; every frame gets the latest one at or before it (the first one before that).
    converter = FemapConverter.__new__(FemapConverter)
    converter.vectors, converter.iron_loss_sets = {"iron_loss": []}, {20: {}, 40: {}}
    requested = []
    converter.get_data_array = lambda step, vectors: (
        requested.append(step)
        or {f"IRON_LOSS-elem-{index}": np.array([float(step)], dtype=np.float32) for index in range(1, 7)}
    )

    for step in (1, 20, 39, 40, 41):
        mesh = _single_vertex_mesh()
        converter._process_iron_loss_field(step, mesh)
        assert all(name in mesh.cell_data for name in IRON_LOSS_NAMES)

    assert requested == [20, 20, 20, 40, 40]
