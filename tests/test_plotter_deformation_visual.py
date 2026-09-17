"""Visual demonstration of the feature-edges/deformation layering.

Running these tests renders two real off-screen scenes and saves them as PNG
files under tests/visual_output/, so you can open them and confirm with your
own eyes that:

- The WHITE outline (feature edges) stays on the mesh's ORIGINAL shape.
- The colored surface, yellow contour lines, and arrows show the mesh's
  DEFORMED shape.

See tests/visual_output/README.txt (written alongside the images) and
interactive_deformation_demo.py for how to view these live and rotate them
yourself instead of looking at a static screenshot.
"""

from pathlib import Path

import pyvista as pv

from pyemsi.plotter.plotter import Plotter
from tests.deformation_demo_meshes import (
    CONTOUR_FIELD,
    DISPLACEMENT_FIELD,
    SCALAR_FIELD,
    VECTOR_FIELD,
    build_2d_plate_mesh,
    build_3d_beam_mesh,
)

OUTPUT_DIR = Path(__file__).parent / "visual_output"


class _StaticReader:
    """Minimal reader stand-in: hands back a fresh copy of a fixed mesh."""

    def __init__(self, mesh):
        self._mesh = mesh

    def read(self):
        return self._mesh.copy(deep=True)


def _make_offscreen_plotter(mesh) -> Plotter:
    plotter = Plotter.__new__(Plotter)
    plotter._notebook = True
    plotter._backend = None
    plotter._mesh = None
    plotter.reader = _StaticReader(mesh)
    plotter._qt_props = {}
    plotter._qt_interactor_kwargs = {}
    plotter._deformation_props = None
    plotter._feature_edges_props = {
        "color": "white",
        "line_width": 4,
        "opacity": 1.0,
        "remove_small_loops": False,
        "max_loop_edges": 10,
        "feature_angle": 30,
    }
    plotter._scalar_props = {}
    plotter._vector_props = {}
    plotter._contour_props = {}
    plotter._block_visibility = {}
    plotter._scalar_bar_sources = {}
    plotter._window = None
    plotter.plotter = pv.Plotter(off_screen=True, window_size=(1000, 750))
    plotter.plotter.set_background("black")
    return plotter


def _configure_layering_demo(plotter: Plotter, deformation_scale: float) -> None:
    plotter.set_scalar(SCALAR_FIELD, mode="node", show_edges=True, edge_color="gray", cmap="viridis")
    plotter.set_contour(CONTOUR_FIELD, n_contours=8, color="yellow", line_width=2)
    plotter.set_vector(VECTOR_FIELD, glyph_type="arrow", factor=0.8, color="red")
    plotter.set_deformation(DISPLACEMENT_FIELD, scale=deformation_scale)


def _feature_edges_actor_bounds(plotter: Plotter):
    return plotter.plotter.renderer.actors["feature_edges"].GetBounds()


def _scalar_field_actor_bounds(plotter: Plotter):
    return plotter.plotter.renderer.actors["scalar_field"].GetBounds()


def test_visual_2d_plate_deformation_layering():
    """Renders tests/visual_output/2d_plate_deformation.png.

    The plate is clamped at x=0 and bends upward (+Z) toward its free edge.
    The white outline should stay flat (original shape); the colored surface
    should visibly lift toward the far edge (deformed shape).
    """
    mesh = build_2d_plate_mesh()
    plotter = _make_offscreen_plotter(mesh)
    _configure_layering_demo(plotter, deformation_scale=1.0)

    output_path = OUTPUT_DIR / "2d_plate_deformation.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plotter.export(str(output_path))

    fe_bounds = _feature_edges_actor_bounds(plotter)
    sf_bounds = _scalar_field_actor_bounds(plotter)
    plotter.plotter.close()

    assert output_path.exists()
    assert output_path.stat().st_size > 0

    fe_z_max = fe_bounds[5]
    sf_z_max = sf_bounds[5]
    assert fe_z_max < 1e-6, "feature edges should stay flat (original, undeformed shape)"
    assert sf_z_max > 1.0, "scalar-colored surface should lift up (deformed shape)"


def test_visual_3d_beam_deformation_layering():
    """Renders tests/visual_output/3d_beam_deformation.png.

    The beam is clamped at x=0 and sags downward (-Z) toward its free tip.
    The white outline should stay straight (original shape); the colored
    surface should visibly droop at the far end (deformed shape).
    """
    mesh = build_3d_beam_mesh()
    plotter = _make_offscreen_plotter(mesh)
    _configure_layering_demo(plotter, deformation_scale=1.0)

    output_path = OUTPUT_DIR / "3d_beam_deformation.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plotter.export(str(output_path))

    fe_bounds = _feature_edges_actor_bounds(plotter)
    sf_bounds = _scalar_field_actor_bounds(plotter)
    plotter.plotter.close()

    assert output_path.exists()
    assert output_path.stat().st_size > 0

    fe_z_min = fe_bounds[4]
    sf_z_min = sf_bounds[4]
    assert fe_z_min > -1e-6, "feature edges should stay straight (original, undeformed shape)"
    assert sf_z_min < -0.5, "scalar-colored surface should droop down (deformed shape)"
