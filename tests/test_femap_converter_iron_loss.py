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
    converter.vectors = {"iron_loss": []}
    converter.get_data_array = lambda step, vectors: {
        f"IRON_LOSS-elem-{index}": np.array([float(index)], dtype=np.float32) for index in range(1, 7)
    }
    mesh = _single_vertex_mesh()

    converter._process_iron_loss_field(40, mesh)

    for index, name in enumerate(IRON_LOSS_NAMES, start=1):
        np.testing.assert_allclose(mesh.cell_data[name], np.array([float(index)], dtype=np.float32))


def test_process_iron_loss_field_skips_step_missing_from_file():
    # iron_loss holds only the averaged step (40); other files may define steps it doesn't have.
    converter = FemapConverter.__new__(FemapConverter)
    converter.vectors = {"iron_loss": [{"set_id": 40, "title": "IRON_LOSS-elem-1", "ent_type": 8, "results": {}}]}
    mesh = _single_vertex_mesh()

    converter._process_iron_loss_field(1, mesh)

    assert not any(name in mesh.cell_data for name in IRON_LOSS_NAMES)
