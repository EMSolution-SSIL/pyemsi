---
title: export
sidebar_position: 7
---

## `export(filename, transparent_background=False, window_size=(800, 600), scale=None)`

Exports a screenshot image via `plotter.screenshot(...)`.

If a file-backed mesh is available, `export()` refreshes the scene (same pipeline as `show()`) before saving.

### Parameters

- **`filename`** (`str | Path`) — Output image path (e.g. `*.png`, `*.jpg`, `*.tif`).
- **`transparent_background`** (`bool`, default: `False`) — Save with transparent background when supported.
- **`window_size`** (`tuple[int, int]`, default: `(800, 600)`) — Screenshot render size.
- **`scale`** (`float | None`, default: `None`) — Resolution scaling factor.

### Returns

- `Plotter` — returns `self` to enable chaining.

### Example

```python
from pyemsi import Plotter

p = Plotter("path/to/output.pvd")
p.reader.set_active_time_point(-1)
p.set_scalar("B-Mag (T)", mode="element", cell2point=True)
p.export("bmag_plot.png", scale=4)
```

