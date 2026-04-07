"""Tests for clim preservation across re-renders (time step changes)."""

import numpy as np
import pyvista as pv
import pytest

from pyemsi.plotter.plotter import Plotter


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class _FakeTimeReader:
    """Minimal time reader that serves pre-built meshes."""

    def __init__(self, time_values, meshes):
        self.time_values = list(time_values)
        self.number_time_points = len(self.time_values)
        self.active_time_value = self.time_values[0]
        self._meshes = list(meshes)

    def set_active_time_value(self, time_value):
        self.active_time_value = time_value

    def set_active_time_point(self, time_point):
        self.active_time_value = self.time_values[time_point]

    def time_point_value(self, time_point):
        return self.time_values[time_point]

    def read(self):
        idx = self.time_values.index(self.active_time_value)
        return self._meshes[idx]


def _make_plotter_with_offscreen():
    """Create a Plotter wrapping an off-screen pv.Plotter (no Qt needed)."""
    p = Plotter.__new__(Plotter)
    p._notebook = True
    p._backend = None
    p._mesh = None
    p.reader = None
    p._qt_props = {}
    p._qt_interactor_kwargs = {}
    p._feature_edges_props = {"color": "white", "line_width": 1, "opacity": 1.0}
    p._scalar_props = {}
    p._vector_props = {}
    p._contour_props = {}
    p._block_visibility = {}
    p._scalar_bar_sources = {}
    p._window = None
    p.plotter = pv.Plotter(off_screen=True)
    return p


def _scalar_bar_range(plotter, name):
    """Read the scalar bar lookup-table range for *name*."""
    bar = plotter.plotter.scalar_bars[name]
    return tuple(round(v, 6) for v in bar.GetLookupTable().GetRange())


# ---------------------------------------------------------------------------
# Scalar-field clim preservation
# ---------------------------------------------------------------------------


def test_scalar_field_first_render_auto_computes_clim():
    """On first render (no existing scalar bars) clim should auto-compute."""
    mesh = pv.Sphere(theta_resolution=8, phi_resolution=8)
    mesh["foo"] = np.linspace(10.0, 20.0, mesh.n_points)

    p = _make_plotter_with_offscreen()
    p._mesh = mesh
    p._scalar_props = {"name": "foo", "mode": "node", "show_edges": False}

    p._plot_scalar_field()

    assert "foo" in p.plotter.scalar_bars
    lo, hi = _scalar_bar_range(p, "foo")
    assert lo == pytest.approx(10.0, abs=0.01)
    assert hi == pytest.approx(20.0, abs=0.01)
    p.plotter.close()


def test_scalar_field_preserves_clim_on_rerender():
    """After a manual range adjustment, re-calling _plot_scalar_field should keep it."""
    mesh0 = pv.Sphere(theta_resolution=8, phi_resolution=8)
    mesh0["foo"] = np.linspace(10.0, 20.0, mesh0.n_points)
    mesh1 = pv.Sphere(theta_resolution=8, phi_resolution=8)
    mesh1["foo"] = np.linspace(100.0, 200.0, mesh1.n_points)

    p = _make_plotter_with_offscreen()
    p._mesh = mesh0
    p._scalar_props = {"name": "foo", "mode": "node", "show_edges": False}

    # First render – auto-compute
    p._plot_scalar_field()
    assert _scalar_bar_range(p, "foo") == pytest.approx((10.0, 20.0), abs=0.01)

    # User adjusts the range manually (e.g. via ScalarBarRangeDialog)
    p.apply_scalar_bar_range("foo", -5.0, 50.0)
    assert _scalar_bar_range(p, "foo") == pytest.approx((-5.0, 50.0), abs=0.01)

    # Simulate time step change: swap mesh, re-plot
    p._mesh = mesh1
    p._scalar_bar_sources = {}
    p._plot_scalar_field()

    # The manually-set range should be preserved, NOT replaced by [100, 200]
    lo, hi = _scalar_bar_range(p, "foo")
    assert lo == pytest.approx(-5.0, abs=0.01)
    assert hi == pytest.approx(50.0, abs=0.01)
    p.plotter.close()


def test_scalar_field_clim_resets_when_scalar_name_changes():
    """Switching to a different scalar should auto-compute (no matching bar)."""
    mesh = pv.Sphere(theta_resolution=8, phi_resolution=8)
    mesh["foo"] = np.linspace(10.0, 20.0, mesh.n_points)
    mesh["bar"] = np.linspace(100.0, 200.0, mesh.n_points)

    p = _make_plotter_with_offscreen()
    p._mesh = mesh
    p._scalar_props = {"name": "foo", "mode": "node", "show_edges": False}

    # First render with "foo"
    p._plot_scalar_field()
    assert _scalar_bar_range(p, "foo") == pytest.approx((10.0, 20.0), abs=0.01)

    # Switch scalar name to "bar"
    p._scalar_props = {"name": "bar", "mode": "node", "show_edges": False}
    p._scalar_bar_sources = {}
    p._plot_scalar_field()

    # "bar" range should be auto-computed from [100, 200], not from "foo"'s range
    assert "bar" in p.plotter.scalar_bars
    lo, hi = _scalar_bar_range(p, "bar")
    assert lo == pytest.approx(100.0, abs=0.01)
    assert hi == pytest.approx(200.0, abs=0.01)
    p.plotter.close()


def test_scalar_field_clim_preserved_through_render_method():
    """Full render() path: time step change preserves clim."""
    mesh0 = pv.Sphere(theta_resolution=8, phi_resolution=8)
    mesh0["foo"] = np.linspace(1.0, 2.0, mesh0.n_points)
    mesh1 = pv.Sphere(theta_resolution=8, phi_resolution=8)
    mesh1["foo"] = np.linspace(50.0, 60.0, mesh1.n_points)

    time_reader = _FakeTimeReader([0.0, 1.0], [mesh0, mesh1])

    p = _make_plotter_with_offscreen()
    p.reader = time_reader
    p._time_reader = lambda: time_reader
    p._scalar_props = {"name": "foo", "mode": "node", "show_edges": False}

    # Initial render at time 0
    p.render()
    assert _scalar_bar_range(p, "foo") == pytest.approx((1.0, 2.0), abs=0.01)

    # Set a fixed range
    p.apply_scalar_bar_range("foo", 0.0, 100.0)

    # Change to time step 1 and re-render
    time_reader.set_active_time_point(1)
    p.render()

    # Range should still be [0, 100], not [50, 60]
    lo, hi = _scalar_bar_range(p, "foo")
    assert lo == pytest.approx(0.0, abs=0.01)
    assert hi == pytest.approx(100.0, abs=0.01)
    p.plotter.close()


# ---------------------------------------------------------------------------
# Vector-field clim preservation
# ---------------------------------------------------------------------------


def test_vector_field_preserves_clim_on_rerender():
    """After first render, re-calling _plot_vector_field should preserve clim."""
    mesh0 = pv.Sphere(theta_resolution=8, phi_resolution=8)
    vecs0 = np.column_stack(
        [
            np.linspace(0, 1, mesh0.n_points),
            np.zeros(mesh0.n_points),
            np.zeros(mesh0.n_points),
        ]
    )
    mesh0["vec"] = vecs0
    mesh0["vec_mag"] = np.linalg.norm(vecs0, axis=1)

    mesh1 = pv.Sphere(theta_resolution=8, phi_resolution=8)
    vecs1 = np.column_stack(
        [
            np.linspace(0, 100, mesh1.n_points),
            np.zeros(mesh1.n_points),
            np.zeros(mesh1.n_points),
        ]
    )
    mesh1["vec"] = vecs1
    mesh1["vec_mag"] = np.linalg.norm(vecs1, axis=1)

    p = _make_plotter_with_offscreen()
    p._mesh = mesh0

    # Manually simulate first render: create a vector actor with known range
    glyphs0 = mesh0.glyph(orient="vec", scale="vec_mag", factor=1.0, geom=pv.Arrow(), tolerance=0.1)
    p.plotter.add_mesh(glyphs0, name="vector_field", reset_camera=False)
    actor0 = p.plotter.renderer.actors["vector_field"]
    first_range = tuple(actor0.mapper.scalar_range)

    # Now swap to mesh1 and call _plot_vector_field — it should read the
    # existing actor's scalar_range and inject it as clim.
    p._mesh = mesh1
    p._vector_props = {
        "name": "vec",
        "scale": "vec",
        "glyph_type": "arrow",
        "factor": 1.0,
        "tolerance": 0.1,
        "color_mode": "scale",
    }

    # Patch glyph to strip the unsupported scalar_bar_args kwarg
    import pyvista.core.filters.data_set as dsf

    _orig_glyph = dsf.DataSetFilters.glyph

    def _patched_glyph(self_mesh, *args, **kwargs):
        kwargs.pop("scalar_bar_args", None)
        return _orig_glyph(self_mesh, *args, **kwargs)

    dsf.DataSetFilters.glyph = _patched_glyph
    try:
        p._plot_vector_field()
    finally:
        dsf.DataSetFilters.glyph = _orig_glyph

    # The range should be preserved from the first render
    actor2 = p.plotter.renderer.actors.get("vector_field")
    second_range = tuple(actor2.mapper.scalar_range)
    assert second_range == pytest.approx(first_range, abs=0.01)
    p.plotter.close()
