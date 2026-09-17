"""Interactive viewer for the feature-edges/deformation layering demo.

Run this directly (not through pytest) to open a real, rotatable 3D window:

    pixi run python tests/interactive_deformation_demo.py plate
    pixi run python tests/interactive_deformation_demo.py beam

The WHITE outline is the mesh's original (undeformed) shape, frozen because
feature edges are extracted before deformation is applied. The colored
surface, yellow contour lines, and red arrows are drawn after deformation, so
they show the mesh's new, deformed shape. Rotate/zoom with the mouse; close
the window to exit.
"""

import sys

from pyemsi.plotter.plotter import Plotter
from tests.deformation_demo_meshes import (
    CONTOUR_FIELD,
    DISPLACEMENT_FIELD,
    SCALAR_FIELD,
    VECTOR_FIELD,
    build_2d_plate_mesh,
    build_3d_beam_mesh,
)


class _StaticReader:
    def __init__(self, mesh):
        self._mesh = mesh

    def read(self):
        return self._mesh.copy(deep=True)


def main(shape: str) -> None:
    mesh = build_2d_plate_mesh() if shape == "plate" else build_3d_beam_mesh()

    plotter = Plotter(title=f"Deformation demo: {shape}")
    plotter.reader = _StaticReader(mesh)
    plotter.set_scalar(SCALAR_FIELD, mode="node", show_edges=True, edge_color="gray", cmap="viridis")
    plotter.set_contour(CONTOUR_FIELD, n_contours=8, color="yellow", line_width=2)
    plotter.set_vector(VECTOR_FIELD, glyph_type="arrow", factor=0.8, color="red")
    plotter.set_deformation(DISPLACEMENT_FIELD, scale=1.0)
    plotter.show()


if __name__ == "__main__":
    shape_arg = sys.argv[1] if len(sys.argv) > 1 else "plate"
    if shape_arg not in {"plate", "beam"}:
        raise SystemExit(f"Usage: python {sys.argv[0]} [plate|beam]")
    main(shape_arg)
