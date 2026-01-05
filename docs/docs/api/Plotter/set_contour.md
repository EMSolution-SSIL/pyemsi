---
title: set_contour()
sidebar_position: 4
---
Adds contour lines/surfaces derived from a scalar field.

For [`pyvista.MultiBlock`](https://docs.pyvista.org/api/core/_autosummary/pyvista.multiblock) datasets, [`Plotter`](/docs/api/Plotter/index.md) computes a global min/max across blocks and generates shared contour levels so contours are consistent across the full model.

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
from pyemsi import Plotter

Plotter("mesh.vtm").set_contour("Flux (A/m)", n_contours=20).show()
```
