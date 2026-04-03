---
title: set_contour()
sidebar_position: 4
---

Configures contour lines/surfaces derived from a scalar field.

`set_contour()` is part of the [visualization pipeline](./index.md#visualization-pipeline). Like the other pipeline methods, calling it only stores the configuration — contours are not computed or added to the scene until [`show()`](./show.md) or [`export()`](./export.md) triggers a rebuild.

For [`pyvista.MultiBlock`](https://docs.pyvista.org/api/core/_autosummary/pyvista.multiblock) datasets, [`Plotter`](/docs/api/Plotter/index.md) computes a global min/max across all blocks and generates shared contour levels, so contours are consistent across the full model.

:::tip[Parameters]
- **`name`** (`Literal[...]`, default: `"Flux (A/m)"`) — Name of the scalar field to visualize (must exist in mesh arrays).
  - `"B-Mag (T)"`
  - `"Flux (A/m)"`
  - `"J-Mag (A/m^2)"`
  - `"Loss (W/m^3)"`
  - `"F Nodal-Mag (N/m^3)"`
  - `"F Lorents-Mag (N/m^3)"`
  - `"Heat Density (W/m^3)"`
  - `"Heat (W)"`
- **`n_contours`** (`int`, default: `10`) — Number of contour levels to generate.
- **`color`** (`str`, default: `"red"`) — Color of the contour lines/surfaces.
- **`line_width`** (`int`, default: `3`) — Width of the contour lines.
- **`**kwargs`** — Additional keyword arguments passed to [`add_mesh()`](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter.add_mesh) when rendering the contours.
:::

:::info[Returns]
- [`Plotter`](/docs/api/Plotter/index.md) — Returns `self` to enable method chaining.
:::

### Example

```python
from pyemsi import Plotter, examples

file_path = examples.ipm_motor_path()
plt = Plotter(file_path)
plt.set_scalar("B-Mag (T)").set_contour("Flux (A/m)", n_contours=20)
plt.plotter.view_xy()
plt.show()
```

<iframe
  src="/pyemsi/demos/ipm_motor.html"
  style={{aspectRatio: "1.5"}}
/>

### See also

- [`set_scalar()`](./set_scalar.md) — configure the scalar field that contours are derived from
- [`set_vector()`](./set_vector.md) — overlay vector glyphs
- [`set_feature_edges()`](./set_feature_edges.md) — configure edge overlay
- [`show()`](./show.md) — trigger rendering and apply the full pipeline
- [`export()`](./export.md) — render and save a screenshot