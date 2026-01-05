---
title: set_feature_edges()
sidebar_position: 2
---

Controls how feature edges are rendered when a file-backed mesh is plotted.

On [`show()`](/docs/api/Plotter/mesh.md) / [`export()`](/docs/api/Plotter/export.md), [`Plotter`](/docs/api/Plotter/index.md) extracts feature edges using [`extract_feature_edges()`](https://docs.pyvista.org/api/core/_autosummary/pyvista.datasetfilters.extract_feature_edges) on each block (for [`pyvista.MultiBlock`](https://docs.pyvista.org/api/core/_autosummary/pyvista.multiblock) datasets) and adds them as a separate actor.

:::tip[Parameters]
- **`color`** (`str`, default: `"white"`) — Edge color.
- **`line_width`** (`int`, default: `1`) — Edge line width.
- **`opacity`** (`float`, default: `1.0`) — Edge opacity in `[0, 1]`.
- **`**kwargs`** — Additional kwargs forwarded to [`add_mesh()`](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter.add_mesh) for the edge actor(s).
:::

:::info[Returns]
- [`Plotter`](/docs/api/Plotter/index.md) — returns `self` to enable chaining.
:::

### Example

```python
from pyemsi import Plotter

Plotter("mesh.vtm").set_feature_edges(color="white", line_width=2, opacity=0.5).show()
```

