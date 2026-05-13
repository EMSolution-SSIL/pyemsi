"""Tests for feature-edge small-loop filtering."""

import numpy as np
import pyvista as pv
import pytest

from pyemsi.plotter.plotter import Plotter, _remove_small_closed_loops

nx = pytest.importorskip("networkx")


def _poly_from_segments(points: np.ndarray, segments: list[tuple[int, int]]) -> pv.PolyData:
    """Build a PolyData of independent 2-point line cells."""
    cells = np.empty((len(segments), 3), dtype=np.int64)
    cells[:, 0] = 2
    cells[:, 1:] = np.asarray(segments, dtype=np.int64)
    return pv.PolyData(points.copy(), lines=cells.ravel())


def test_remove_small_closed_loops_removes_triangle_quad_pentagon() -> None:
    points = np.array([[float(i), 0.0, 0.0] for i in range(13)], dtype=float)
    segments = [
        (0, 1),
        (1, 2),
        (2, 0),  # triangle
        (3, 4),
        (4, 5),
        (5, 6),
        (6, 3),  # quad
        (7, 8),
        (8, 9),
        (9, 10),
        (10, 11),
        (11, 7),  # pentagon
        (11, 12),  # non-cycle survivor
    ]
    edges = _poly_from_segments(points, segments)

    cleaned, removed = _remove_small_closed_loops(edges, max_loop_edges=5)

    assert len(removed) >= 3
    assert cleaned.n_lines == 1
    assert np.array_equal(cleaned.lines, np.array([2, 11, 12]))


def test_remove_small_closed_loops_keeps_larger_cycle() -> None:
    points = np.array([[float(i), 0.0, 0.0] for i in range(6)], dtype=float)
    segments = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0)]
    edges = _poly_from_segments(points, segments)

    cleaned, removed = _remove_small_closed_loops(edges, max_loop_edges=5)

    assert removed == []
    assert np.array_equal(cleaned.lines, edges.lines)


def test_remove_small_closed_loops_preserves_points_and_ids() -> None:
    points = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [5.0, 5.0, 5.0],
            [6.0, 5.0, 5.0],
        ],
        dtype=float,
    )
    segments = [(0, 1), (1, 2), (2, 0), (3, 4)]
    edges = _poly_from_segments(points, segments)

    cleaned, _ = _remove_small_closed_loops(edges, max_loop_edges=5)

    assert np.array_equal(cleaned.points, points)
    assert np.array_equal(cleaned.lines, np.array([2, 3, 4]))


def test_remove_small_closed_loops_handles_empty_lines() -> None:
    points = np.array([[0.0, 0.0, 0.0]], dtype=float)
    edges = pv.PolyData(points.copy())

    cleaned, removed = _remove_small_closed_loops(edges, max_loop_edges=5)

    assert removed == []
    assert cleaned.n_lines == 0
    assert np.array_equal(cleaned.points, points)


def test_remove_small_closed_loops_keeps_noncyclic_segments() -> None:
    points = np.array([[float(i), 0.0, 0.0] for i in range(4)], dtype=float)
    segments = [(0, 1), (1, 2), (2, 3)]
    edges = _poly_from_segments(points, segments)

    cleaned, removed = _remove_small_closed_loops(edges, max_loop_edges=5)

    assert removed == []
    assert np.array_equal(cleaned.lines, edges.lines)


class _FakeEdgeBlock:
    def __init__(self, edge_poly: pv.PolyData) -> None:
        self._edge_poly = edge_poly
        self.n_points = 4

    def extract_feature_edges(self) -> pv.PolyData:
        return self._edge_poly


def _make_plotter_with_mesh(mesh: pv.PolyData):
    p = Plotter.__new__(Plotter)
    p._notebook = True
    p._backend = None
    p._mesh = mesh
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


def test_plot_feature_edges_invalid_line_cells_warns_and_falls_back() -> None:
    points = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 1.0, 0.0],
            [0.0, 1.0, 0.0],
        ],
        dtype=float,
    )
    invalid_lines = np.array([3, 0, 1, 2], dtype=np.int64)
    invalid_edges = pv.PolyData(points.copy(), lines=invalid_lines)
    mesh = _FakeEdgeBlock(invalid_edges)

    p = _make_plotter_with_mesh(mesh)
    p.set_feature_edges(remove_small_loops=True, max_loop_edges=5)

    with pytest.warns(UserWarning, match="small-loop removal skipped"):
        p._plot_feature_edges()

    assert "feature_edges" in p.plotter.renderer.actors
    p.plotter.close()
