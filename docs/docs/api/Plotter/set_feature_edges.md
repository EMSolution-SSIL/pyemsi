---
title: set_feature_edges
sidebar_position: 2
---

## `set_feature_edges(color="black", line_width=1, opacity=1.0, **kwargs)`

Controls how feature edges are rendered when a file-backed mesh is plotted.

On `show()` / `export()`, `Plotter` extracts feature edges using `extract_feature_edges()` on each block (for `MultiBlock` datasets) and adds them as a separate actor.

### Parameters

- **`color`** (`str`, default: `"black"`) — Edge color.
- **`line_width`** (`int`, default: `1`) — Edge line width.
- **`opacity`** (`float`, default: `1.0`) — Edge opacity in `[0, 1]`.
- **`**kwargs`** — Additional kwargs forwarded to `plotter.add_mesh(...)` for the edge actor(s).

### Returns

- `Plotter` — returns `self` to enable chaining.

### Example

```python
from pyemsi import Plotter

Plotter("mesh.vtm").set_feature_edges(color="white", line_width=2, opacity=0.5).show()
```

