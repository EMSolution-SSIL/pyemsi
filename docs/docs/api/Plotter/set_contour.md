---
title: set_contour
sidebar_position: 4
---

## `set_contour(name, n_contours=10, color="red", line_width=3, **kwargs)`

Adds contour lines/surfaces derived from a scalar field.

For `MultiBlock` datasets, `Plotter` computes a global min/max across blocks and generates shared contour levels so contours are consistent across the full model.

### Parameters

- **`name`** (`str`) — Scalar array name to contour.
- **`n_contours`** (`int`, default: `10`) — Number of contour levels (clamped to at least `1`).
- **`color`** (`str`, default: `"red"`) — Contour color.
- **`line_width`** (`int`, default: `3`) — Contour line width.
- **`**kwargs`** — Forwarded to `plotter.add_mesh(...)` for the contour actor(s).

### Returns

- `Plotter` — returns `self` to enable chaining.

### Example

```python
from pyemsi import Plotter

Plotter("mesh.vtm").set_scalar("B-Mag (T)").set_contour("Flux (A/m)", n_contours=20).show()
```

