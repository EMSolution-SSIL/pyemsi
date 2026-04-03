---
title: export()
sidebar_position: 7
---

Saves a screenshot of the rendered scene to an image file via [`plotter.screenshot()`](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter.screenshot#pyvista.Plotter.screenshot).

If a file-backed mesh is loaded, `export()` triggers the same full [visualization pipeline](./index.md#visualization-pipeline) rebuild as [`show()`](./show.md) before capturing the image — so all configured pipeline components ([`set_scalar()`](./set_scalar.md), [`set_contour()`](./set_contour.md), [`set_vector()`](./set_vector.md), [`set_feature_edges()`](./set_feature_edges.md)) are applied automatically.

If no mesh is loaded, the current state of the underlying [`plotter`](./plotter0.md) is captured as-is.

:::tip[Parameters]
- **`filename`** (`str | Path`) — Output image path. Supported formats: `*.png`, `*.jpg`, `*.tif`.
- **`transparent_background`** (`bool`, default: `False`) — Save with a transparent background (PNG only).
- **`window_size`** (`tuple[int, int]`, default: `(800, 600)`) — Offscreen render resolution in pixels.
- **`scale`** (`float | None`, default: `None`) — Resolution scaling factor. For example, `scale=2` doubles the pixel dimensions relative to `window_size`.
:::

:::info[Returns]
- `Plotter` — returns `self` to enable chaining.
:::

### Example

```python
from pyemsi import Plotter, examples

file_path = examples.transient_path()
plt = Plotter(file_path)
plt.set_scalar("B-Mag (T)", scalar_bar_args={"vertical": True})
plt.set_block_visibility("4", False)
plt.export("docs/static/demos/exported_plot.png")
```

The output image would look like the following:

![Exported plot](/demos/exported_plot.png)

### See also

- [`show()`](./show.md) — render interactively instead of saving to file
- [`set_scalar()`](./set_scalar.md) — configure scalar field coloring
- [`set_contour()`](./set_contour.md) — add contour lines
- [`set_vector()`](./set_vector.md) — overlay vector glyphs
- [`set_feature_edges()`](./set_feature_edges.md) — configure edge overlay