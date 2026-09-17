"""Tests for Plotter nodal mesh deformation."""

import numpy as np
import pyvista as pv
import pytest

from pyemsi.plotter.plotter import Plotter


def _make_plotter(mesh: pv.DataSet | pv.MultiBlock) -> Plotter:
    """Create a lightweight Plotter with an in-memory mesh."""
    plotter = Plotter.__new__(Plotter)
    plotter._mesh = mesh
    plotter.reader = None
    plotter._deformation_props = None
    plotter._block_visibility = {}
    return plotter


def _triangle(offset: float = 0.0) -> pv.PolyData:
    points = np.array(
        [
            [offset, 0.0, 0.0],
            [offset + 1.0, 0.0, 0.0],
            [offset, 1.0, 0.0],
        ]
    )
    return pv.PolyData(points, faces=np.array([3, 0, 1, 2]))


def test_set_deformation_applies_scaled_point_vectors_and_returns_self() -> None:
    mesh = _triangle()
    original_points = mesh.points.copy()
    vectors = np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, 2.0, 0.0],
            [0.0, 0.0, 3.0],
        ]
    )
    mesh.point_data["displacement"] = vectors
    plotter = _make_plotter(mesh)

    result = plotter.set_deformation("displacement", scale=2.5)
    plotter._apply_deformation()

    assert result is plotter
    np.testing.assert_allclose(mesh.points, original_points + 2.5 * vectors)


@pytest.mark.parametrize("scale", [0.0, -2.0])
def test_set_deformation_supports_zero_and_negative_scale(scale: float) -> None:
    mesh = _triangle()
    original_points = mesh.points.copy()
    vectors = np.ones((mesh.n_points, 3))
    mesh.point_data["displacement"] = vectors
    plotter = _make_plotter(mesh)

    plotter.set_deformation("displacement", scale=10.0)
    plotter.set_deformation("displacement", scale=scale)
    plotter._apply_deformation()

    np.testing.assert_allclose(mesh.points, original_points + scale * vectors)


@pytest.mark.parametrize("scale", [np.nan, np.inf, -np.inf, "not-a-number"])
def test_set_deformation_rejects_non_finite_scale(scale) -> None:
    plotter = _make_plotter(_triangle())

    with pytest.raises(ValueError, match="scale must be a finite number"):
        plotter.set_deformation("displacement", scale=scale)


def test_apply_deformation_does_not_accumulate_across_fresh_reads() -> None:
    source = _triangle()
    source.point_data["displacement"] = np.full((source.n_points, 3), [0.25, 0.5, 0.0])
    original_points = source.points.copy()

    class _CopyingReader:
        def read(self):
            return source.copy(deep=True)

    plotter = _make_plotter(source.copy(deep=True))
    plotter.reader = _CopyingReader()
    plotter.set_deformation("displacement", scale=4.0)

    plotter._mesh = None
    plotter._apply_deformation()
    first_points = plotter.mesh.points.copy()

    plotter._mesh = None
    plotter._apply_deformation()
    second_points = plotter.mesh.points.copy()

    expected = original_points + 4.0 * source.point_data["displacement"]
    np.testing.assert_allclose(first_points, expected)
    np.testing.assert_allclose(second_points, expected)
    np.testing.assert_allclose(source.points, original_points)


@pytest.mark.parametrize("pipeline_method", ["show", "render", "export"])
def test_feature_edges_freeze_on_original_shape_other_layers_use_deformed_shape(
    pipeline_method: str,
) -> None:
    """Feature edges are extracted before deformation is applied, so they keep
    showing the original (undeformed) outline -- a visual "old boundary" marker.
    The scalar field, contours, and vector glyphs are drawn after deformation,
    so they reflect the new (deformed) shape. This is intentional: it lets a
    user compare "where the mesh used to be" against "where it is now" in a
    single frame.
    """
    source = _triangle()
    vectors = np.full((source.n_points, 3), [0.25, 0.0, 0.0])
    source.point_data["displacement"] = vectors
    original = source.points.copy()
    deformed = source.points + 2.0 * vectors

    class _CopyingReader:
        def read(self):
            return source.copy(deep=True)

    class _FakePyVistaPlotter:
        suppress_rendering = False

        def show(self):
            return None

        def render(self):
            return None

        def reset_camera(self):
            return None

        def screenshot(self, **kwargs):
            return None

    plotter = _make_plotter(source.copy(deep=True))
    plotter.reader = _CopyingReader()
    plotter._notebook = True
    plotter._window = None
    plotter._scalar_bar_sources = {}
    plotter.plotter = _FakePyVistaPlotter()
    plotter.set_deformation("displacement", scale=2.0)

    call_order = []
    feature_edges_points = []
    other_layer_points = []

    def _record_feature_edges():
        call_order.append("feature_edges")
        feature_edges_points.append(plotter.mesh.points.copy())

    def _record_other_layer(layer_name):
        def _record():
            call_order.append(layer_name)
            other_layer_points.append(plotter.mesh.points.copy())

        return _record

    plotter._plot_feature_edges = _record_feature_edges
    plotter._plot_scalar_field = _record_other_layer("scalar_field")
    plotter._plot_contours = _record_other_layer("contours")
    plotter._plot_vector_field = _record_other_layer("vector_field")

    if pipeline_method == "export":
        plotter.export("unused.png")
    else:
        getattr(plotter, pipeline_method)()

    assert call_order.index("feature_edges") < call_order.index("scalar_field")
    assert call_order.index("feature_edges") < call_order.index("contours")
    assert call_order.index("feature_edges") < call_order.index("vector_field")

    assert len(feature_edges_points) == 1
    np.testing.assert_allclose(feature_edges_points[0], original)

    assert len(other_layer_points) == 3
    for points in other_layer_points:
        np.testing.assert_allclose(points, deformed)


def test_apply_deformation_only_changes_matching_multiblock_blocks() -> None:
    deformed = _triangle()
    fixed = _triangle(offset=10.0)
    vectors = np.full((deformed.n_points, 3), [0.5, 0.0, 0.0])
    deformed.point_data["displacement"] = vectors
    deformed_original = deformed.points.copy()
    fixed_original = fixed.points.copy()
    mesh = pv.MultiBlock({"deformed": deformed, "fixed": fixed})
    plotter = _make_plotter(mesh)

    plotter.set_deformation("displacement", scale=3.0)
    plotter._apply_deformation()

    np.testing.assert_allclose(deformed.points, deformed_original + 3.0 * vectors)
    np.testing.assert_allclose(fixed.points, fixed_original)


def test_apply_deformation_rejects_missing_point_array() -> None:
    plotter = _make_plotter(_triangle())
    plotter.set_deformation("displacement")

    with pytest.raises(ValueError, match="was not found in any non-empty mesh block"):
        plotter._apply_deformation()


def test_apply_deformation_rejects_non_vector_point_array() -> None:
    mesh = _triangle()
    mesh.point_data["displacement"] = np.ones(mesh.n_points)
    plotter = _make_plotter(mesh)
    plotter.set_deformation("displacement")

    with pytest.raises(ValueError, match="must be a three-component point-data array"):
        plotter._apply_deformation()
