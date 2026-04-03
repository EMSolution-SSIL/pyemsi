---
title: set_vector()
sidebar_position: 5
---

Configures vector glyphs (arrows/cones/spheres) for a 3-component vector array.

`set_vector()` is part of the [visualization pipeline](./index.md#visualization-pipeline). Like the other pipeline methods, calling it only stores the configuration — glyphs are not computed or added to the scene until [`show()`](./show.md) or [`export()`](./export.md) triggers a rebuild.

Glyphs are generated per-block for [`pyvista.MultiBlock`](https://docs.pyvista.org/api/core/_autosummary/pyvista.multiblock) datasets.

:::tip[Parameters]
- **`name`** (`Literal[...]`) — Vector array name (must exist and be 3-component).
  - `"B-Mag (T)"`
  - `"B-Vec (T)"`
  - `"Flux (A/m)"`
  - `"J-Mag (A/m^2)"`
  - `"J-Vec (A/m^2)"`
  - `"Loss (W/m^3)"`
  - `"F Nodal-Mag (N/m^3)"`
  - `"F Nodal-Vec (N/m^3)"`
  - `"F Lorents-Mag (N/m^3)"`
  - `"F Lorents-Vec (N/m^3)"`
  - `"Heat Density (W/m^3)"`
  - `"Heat (W)"`
- **`scale`** (`str | bool | None`, default: `None`) — Controls glyph scaling:
  - `None`: scale by vector magnitude (internally uses `name`)
  - `str`: scale by a separate scalar array
  - `False`: uniform glyph size
- **`glyph_type`** (`"arrow" | "cone" | "sphere"`, default: `"arrow"`) — Glyph geometry.
- **`factor`** (`float`, default: `1.0`) — Global size multiplier.
- **`tolerance`** (`float | None`, default: `None`) — Reduce glyph density (fraction of bounding box). `None` shows all glyphs.
- **`color_mode`** (`str`, default: `"scale"`) — Passed to PyVista’s glyph coloring (typically `"scale"`, `"scalar"`, or `"vector"`).
- **`**kwargs`** — Forwarded to [`add_mesh()`](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter.add_mesh) for the glyph actor(s) (examples: `cmap`, `clim`, `opacity`).
:::

:::info[Returns]
- `Plotter` — returns `self` to enable chaining.
:::

### Examples

```python
from pyemsi import Plotter, examples

file_path = examples.transient_path()
plt = Plotter(file_path)
plt.set_vector("B-Vec (T)", scale="B-Mag (T)", factor=5e-1, show_scalar_bar=False)
plt.set_feature_edges(color="red", line_width=3)
plt.set_block_visibility("4", False)
plt.show()
```

<iframe
  src="/pyemsi/demos/set_vector.html"
  style={{aspectRatio: "1.5"}}
/>

### See also

- [`set_scalar()`](./set_scalar.md) — configure scalar field coloring
- [`set_contour()`](./set_contour.md) — add contour lines
- [`set_feature_edges()`](./set_feature_edges.md) — configure edge overlay
- [`set_block_visibility()`](./set_block_visibility.md) — hide/show individual mesh blocks
- [`show()`](./show.md) — trigger rendering and apply the full pipeline
- [`export()`](./export.md) — render and save a screenshot