---
title: set_vector()
sidebar_position: 5
---
Adds vector glyphs (arrows/cones/spheres) for a 3-component vector array.

Glyphs are generated per-block for [`pyvista.MultiBlock`](https://docs.pyvista.org/api/core/_autosummary/pyvista.multiblock) datasets and are added during [`show()`](/docs/api/Plotter/show.md) / [`export()`](/docs/api/Plotter/export.md).

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
from pyemsi import Plotter

Plotter("mesh.vtu").set_vector("B-Vec (T)", scale="B-Mag (T)", factor=5e-3, opacity=0.5).show()
Plotter("mesh.vtu").set_vector("Velocity", glyph_type="cone", tolerance=0.1).show()
```

