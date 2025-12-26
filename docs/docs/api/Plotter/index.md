---
sidebar_position: 3
title: Plotter
---

`Plotter` is a small wrapper around PyVista that supports two visualization modes:

- **Desktop (Qt)**: an interactive Qt window powered by `pyvistaqt.QtInteractor` (requires `PySide6` + `pyvistaqt`)
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

### Parameters

- **`filepath`** (`str | Path | None`, optional) — Mesh file to load immediately (calls `set_file()`).
- **`title`** (`str`, default: `"pyemsi Plotter"`) — Qt window title (desktop mode only).
- **`window_size`** (`tuple[int, int]`, default: `(1024, 768)`) — Qt window size (desktop mode only).
- **`position`** (`tuple[int, int] | None`, default: `None`) — Qt window position (desktop mode only).
- **`notebook`** (`bool`, default: `False`) — Use PyVista notebook plotting instead of Qt.
- **`backend`** (`str | None`, default: `"html"`) — PyVista notebook backend passed to `pyvista.set_jupyter_backend()`.
- **`**kwargs`** — Passed to the underlying plotter (`QtInteractor` in desktop mode, `pyvista.Plotter` in notebook mode).

## Key attributes

- **`plotter`** — The underlying plotter instance:
  - desktop mode: `pyvistaqt.QtInteractor`
  - notebook mode: `pyvista.Plotter`
- **`reader`** — The PyVista reader created by `set_file()` (e.g. a `PVDReader` for `*.pvd`).
- **`mesh`** — A property that lazily reads and caches the current mesh from `reader`.

## Working with time series (`*.pvd`)

When the input file is a `*.pvd`, `Plotter.reader` is a `PVDReader`. You can select a time step before plotting:

```python
from pyemsi import Plotter

p = Plotter("path/to/output.pvd")
p.reader.set_active_time_point(-1)   # last time step
p.plotter.view_xy()                  # any PyVista camera helper
p.set_scalar("B-Mag (T)", mode="element", cell2point=True)
p.set_vector("B-Vec (T)", scale="B-Mag (T)", factor=5e-3, opacity=0.5)
p.show()
```

## Visualization pipeline

If a file was loaded (via `filepath` or `set_file()`), `show()` and `export()` will (re)build the visualization in this order:

1. Scalar field (`set_scalar()`)
2. Contours (`set_contour()`)
3. Vector glyphs (`set_vector()`)
4. Feature edges (`set_feature_edges()`, enabled by default)
5. Camera reset

If no file was loaded, you can still use the underlying `plotter` directly and add any PyVista meshes/actors.

## API

Each method has its own page:

- [`set_file(filepath)`](./set_file)
- [`set_feature_edges(color="black", line_width=1, opacity=1.0, **kwargs)`](./set_feature_edges)
- [`set_scalar(name, mode="element", cell2point=True, **kwargs)`](./set_scalar)
- [`set_contour(name, n_contours=10, color="red", line_width=3, **kwargs)`](./set_contour)
- [`set_vector(name, scale=None, glyph_type="arrow", factor=1.0, tolerance=None, color_mode="scale", **kwargs)`](./set_vector)
- [`show()`](./show)
- [`export(filename, transparent_background=False, window_size=(800, 600), scale=None)`](./export)
