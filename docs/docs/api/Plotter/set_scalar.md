---
title: set_scalar()
sidebar_position: 3
---

Configures scalar field coloring for the loaded mesh.

`set_scalar()` is part of the [visualization pipeline](./index.md#visualization-pipeline). Calling it only stores the configuration — the scalar actor is not added to the scene until [`show()`](./show.md) or [`export()`](./export.md) triggers a full rebuild. This means you can call `set_scalar()` multiple times before rendering and only the last call takes effect, and the configuration is reapplied automatically on every subsequent `show()`/`export()` call (e.g. after changing the active time step).

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
- **`mode`** (`"node" | "element"`, default: `"node"`) — Whether `name` is point data (`"node"`) or cell data (`"element"`).
- **`**kwargs`** — Forwarded to [`add_mesh()`](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter.add_mesh) for the scalar mesh actor.
:::

Useful `**kwargs` include `cmap`, `clim`, `show_edges`, `edge_color`, `edge_opacity`, `show_scalar_bar`, `scalar_bar_args`.

:::info[Returns]
- `Plotter` — returns `self` to enable chaining.
:::

### Examples

```python
from pyemsi import Plotter, examples

file_path = examples.ipm_motor_path()
plt = Plotter(file_path)
plt.set_scalar("B-Mag (T)", cmap="viridis", edge_color="red", edge_opacity=0.2, show_scalar_bar=False)
plt.plotter.view_xy()
plt.show()
```

<iframe
  src="/pyemsi/demos/set_scalar1.html"
  style={{aspectRatio: "1.5"}}
/>

```python
from pyemsi import Plotter, examples

file_path = examples.transient_path()
plt = Plotter(file_path)
plt.set_scalar("B-Mag (T)", mode="element", show_edges=False, show_scalar_bar=False)
plt.set_block_visibility("4", False)
plt.show()
```

<iframe
  src="/pyemsi/demos/set_scalar2.html"
  style={{aspectRatio: "1.5"}}
/>

### See also

- [`set_contour()`](./set_contour.md) — add contour lines on top of the scalar field
- [`set_vector()`](./set_vector.md) — overlay vector glyphs
- [`set_feature_edges()`](./set_feature_edges.md) — configure edge overlay
- [`set_block_visibility()`](./set_block_visibility.md) — hide/show individual mesh blocks
- [`show()`](./show.md) — trigger rendering and apply the full pipeline
- [`export()`](./export.md) — render and save a screenshot