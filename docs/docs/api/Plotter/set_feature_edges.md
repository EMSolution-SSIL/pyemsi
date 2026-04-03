---
title: set_feature_edges()
sidebar_position: 2
---

Configures the feature-edge overlay rendered on top of the mesh.

`set_feature_edges()` is part of the [visualization pipeline](./index.md#visualization-pipeline). Feature edges are **enabled by default** — you only need to call this method if you want to change the appearance (color, width, opacity) or disable them. Like the other pipeline methods, calling it only stores the configuration; the edge actors are built during [`show()`](./show.md) or [`export()`](./export.md).

Feature edges are extracted using [`extract_feature_edges()`](https://docs.pyvista.org/api/core/_autosummary/pyvista.datasetfilters.extract_feature_edges) per block (for [`pyvista.MultiBlock`](https://docs.pyvista.org/api/core/_autosummary/pyvista.multiblock) datasets) and added as a separate actor.

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
from pyemsi import Plotter, examples

file_path = examples.transient_path()
plt = Plotter(file_path)
plt.set_scalar("B-Mag (T)", show_scalar_bar=False, show_edges=False)
plt.set_feature_edges(color="red", line_width=3)
plt.set_block_visibility("4", False)
plt.show()
```

<iframe
  src="/pyemsi/demos/set_feature_edges.html"
  style={{aspectRatio: "1.5"}}
/>

### See also

- [`set_scalar()`](./set_scalar.md) — configure scalar field coloring
- [`set_contour()`](./set_contour.md) — add contour lines
- [`set_vector()`](./set_vector.md) — overlay vector glyphs
- [`show()`](./show.md) — trigger rendering and apply the full pipeline
- [`export()`](./export.md) — render and save a screenshot
