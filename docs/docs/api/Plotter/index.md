---
sidebar_position: 3
title: Plotter
---

`Plotter` is a small wrapper around [PyVista](https://docs.pyvista.org/) that supports two visualization modes:

- **Desktop (Qt)**: an interactive Qt window powered by [`pyvistaqt.QtInteractor`](https://qtdocs.pyvista.org/api_reference.html#qtinteractor) (requires `PySide6` + `pyvistaqt`)
- **Notebook (Jupyter)**: PyVista’s notebook backends (set `notebook=True`)

It is designed for quick inspection of VTK datasets produced by `pyemsi` (especially `*.pvd` time series and `*.vtm` multiblock outputs), while still allowing you to access the underlying PyVista objects directly.

## Installation notes

- Desktop/Qt mode requires `PySide6` and `pyvistaqt` in addition to `pyvista`.
- Notebook mode requires a supported PyVista notebook backend. The default in `pyemsi` is `backend="html"`.

If Qt dependencies are missing and you instantiate `Plotter(notebook=False)`, it raises an `ImportError` with the suggested packages to install.

## Initialization

```python
from pyemsi import Plotter

# Load a dataset (VTU/VTM/PVD/...)
p = Plotter("path/to/output.pvd")

# Notebook mode (Jupyter)
p_nb = Plotter("path/to/output.pvd", notebook=True, backend="html")
```

:::info[Parameters]
- **`filepath`** (`str | Path | None`, optional) — Mesh file to load immediately (calls [`set_file()`](./set_file.md)).
- **`title`** (`str`, default: `"pyemsi Plotter"`) — Qt window title (desktop mode only).
- **`window_size`** (`tuple[int, int]`, default: `(1024, 768)`) — Qt window size (desktop mode only).
- **`position`** (`tuple[int, int] | None`, default: `None`) — Qt window position (desktop mode only).
- **`notebook`** (`bool`, default: `False`) — Use PyVista notebook plotting instead of Qt.
- **`backend`** (`str | None`, default: `"html"`) — PyVista notebook backend passed to [`pyvista.set_jupyter_backend()`](https://docs.pyvista.org/user-guide/jupyter/index.html).
- **`**kwargs`** — Passed to the underlying plotter (`QtInteractor` in desktop mode, [`pyvista.Plotter`](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter) in notebook mode).
:::

## Working with time series (`*.pvd`)

When the input file is a `*.pvd`, [`Plotter.reader`](/docs/api/Plotter/reader.md) is a [`PVDReader`](https://docs.pyvista.org/api/readers/_autosummary/pyvista.pvdreader). You can select a time step before plotting:

`Plotter` also exposes convenience proxies to PyVista’s [`TimeReader`](https://docs.pyvista.org/api/readers/_autosummary/pyvista.timereader) API:

- [`active_time_value`](/docs/api/Plotter/active_time_value.md)
- [`number_time_points`](/docs/api/Plotter/number_time_points.md)
- [`time_values`](/docs/api/Plotter/time_values.md)
- [`set_active_time_point(time_point)`](/docs/api/Plotter/set_active_time_point.md)
- [`set_active_time_value(time_value)`](/docs/api/Plotter/set_active_time_value.md)
- [`time_point_value(time_point)`](/docs/api/Plotter/time_point_value.md)

If the underlying `reader` is not a [`TimeReader`](https://docs.pyvista.org/api/readers/_autosummary/pyvista.timereader), the getter-style attributes return `None`, and the setter methods are silent no-ops that return `None`.

```python
from pyemsi import Plotter

p = Plotter("path/to/output.pvd")
p.set_active_time_point(-1)          # last time step (silent no-op if not time-aware)
p.plotter.view_xy()                  # any PyVista camera helper
p.set_scalar("B-Mag (T)", mode="element", cell2point=True)
p.set_vector("B-Vec (T)", scale="B-Mag (T)", factor=5e-3, opacity=0.5)
p.show()
```

## Visualization pipeline

If a file was loaded (via `filepath` or [`set_file()`](./set_file.md)), [`show()`](./show.md) and [`export()`](./export.md) will (re)build the visualization in this order:

1. Scalar field ([`set_scalar()`](./set_scalar.md))
2. Contours ([`set_contour()`](./set_contour.md))
3. Vector glyphs ([`set_vector()`](./set_vector.md))
4. Feature edges ([`set_feature_edges()`](./set_feature_edges.md), enabled by default)
5. Camera reset

If no file was loaded, you can still use the underlying `plotter` directly and add any PyVista meshes/actors.

## Methods

| | Description |
|---|---|
| [`set_file(filepath)`](./set_file) | Set `reader` from a mesh file. |
| [`set_active_time_point(time_point)`](./set_active_time_point) | Select active time step (no-op if not time-aware). |
| [`set_active_time_value(time_value)`](./set_active_time_value) | Select active time by value (no-op if not time-aware). |
| [`time_point_value(time_point)`](./time_point_value) | Get time value for a time step (or `None`). |
| [`set_feature_edges(...)`](./set_feature_edges) | Configure feature-edge overlay. |
| [`set_scalar(...)`](./set_scalar) | Configure scalar coloring. |
| [`set_contour(...)`](./set_contour) | Configure contours. |
| [`set_vector(...)`](./set_vector) | Configure vector glyphs. |
| [`get_block_names()`](./get_block_names) | Get list of block names from multi-block mesh. |
| [`get_block_visibility(block_name)`](./get_block_visibility) | Check visibility state of a block. |
| [`set_block_visibility(block_name, visible)`](./set_block_visibility) | Set visibility for a single block. |
| [`set_blocks_visibility(visibility)`](./set_blocks_visibility) | Set visibility for multiple blocks in batch. |
| [`query_point(...)`](./query_point) | Query point data for a single point. |
| [`query_points(...)`](./query_points) | Query point data for multiple points. |
| [`query_cell(...)`](./query_cell) | Query cell data for a single cell. |
| [`query_cells(...)`](./query_cells) | Query cell data for multiple cells. |
| [`sample_point(...)`](./sample_point) | Sample mesh data at a single point coordinate. |
| [`sample_points(...)`](./sample_points) | Sample mesh data at multiple point coordinates. |
| [`sample_line(...)`](./sample_line) | Sample mesh data along a straight line. |
| [`sample_lines(...)`](./sample_lines) | Sample mesh data along multiple straight lines. |
| [`sample_arc(...)`](./sample_arc) | Sample mesh data along a circular arc. |
| [`sample_arcs(...)`](./sample_arcs) | Sample mesh data along multiple circular arcs. |
| [`show()`](./show) | Render (Qt window or notebook output). |
| [`export(...)`](./export) | Save a screenshot to an image file. |

## Attributes

| | Description |
|---|---|
| [`plotter`](./plotter0) | Underlying plotter (`QtInteractor` desktop / [`pv.Plotter`](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter) notebook). |
| [`reader`](./reader) | PyVista reader created by [`set_file()`](./set_file.md) (e.g. for `*.pvd`). |
| [`mesh`](./mesh) | Lazily reads/caches the current mesh from `reader`. |
| [`active_time_value`](./active_time_value) | Current time value if `reader` is time-aware, else `None`. |
| [`number_time_points`](./number_time_points) | Number of time steps if time-aware, else `None`. |
| [`time_values`](./time_values) | Available time values if time-aware, else `None`. |
