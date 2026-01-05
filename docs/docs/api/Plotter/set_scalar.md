---
title: set_scalar()
sidebar_position: 3
---

Configures scalar visualization for the loaded mesh. The scalar field is applied when [`show()`](/docs/api/Plotter/show.md) / [`export()`](/docs/api/Plotter/export.md) refresh the scene.

:::tip[Parameters]
- **`name`** (`Literal[...]`) — Name of the scalar array to plot (must exist in the mesh arrays).
    - `"B-Mag (T)"`
    - `"Flux (A/m)"`
    - `"J-Mag (A/m^2)"`
    - `"Loss (W/m^3)"`
    - `"F Nodal-Mag (N/m^3)"`
    - `"F Lorents-Mag (N/m^3)"`
    - `"Heat Density (W/m^3)"`
    - `"Heat (W)"`
- **`mode`** (`"node" | "element"`, default: `"element"`) — Whether `name` is point data (`"node"`) or cell data (`"element"`).
- **`cell2point`** (`bool`, default: `True`) — If `mode="element"`, convert cell data to point data before plotting (smoother shading).
- **`**kwargs`** — Forwarded to [`add_mesh()`](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter.add_mesh) for the scalar mesh actor.
:::

Useful `**kwargs` include `cmap`, `clim`, `show_edges`, `edge_color`, `edge_opacity`, `show_scalar_bar`, `scalar_bar_args`.

:::info[Returns]
- `Plotter` — returns `self` to enable chaining.
:::

### Examples

```python
from pyemsi import Plotter

Plotter("mesh.vtm").set_scalar("Flux (A/m)", mode="node", show_scalar_bar=False).show()
Plotter("mesh.vtm").set_scalar("B-Mag (T)", mode="element", cell2point=True).show()
```

