---
title: set_deformation()
sidebar_position: 5.1
---

Configures nodal mesh deformation using a named three-component point-data vector array.
For every matching mesh block, the displayed coordinates are calculated as:

```text
deformed_points = original_points + scale * vectors
```

`set_deformation()` is part of the [visualization pipeline](./index.md#visualization-pipeline).
Calling it stores the configuration; deformation is applied to a freshly read mesh when
[`show()`](./show.md), `render()`, or [`export()`](./export.md) rebuilds the scene.
The source VTK file is never modified, and repeated rebuilds do not accumulate deformation.

For a [`pyvista.MultiBlock`](https://docs.pyvista.org/api/core/_autosummary/pyvista.multiblock)
mesh, blocks containing the named point vector are deformed and other blocks remain unchanged.
At least one non-empty block must contain the array.

:::tip[Parameters]
- **`name`** (`str`) — Name of the three-component point-data vector array.
- **`scale`** (`float`, default: `1.0`) — Finite multiplier applied to every vector. Positive,
  zero, and negative values are supported.
:::

:::info[Returns]
- `Plotter` — returns `self` to enable chaining.
:::

:::danger[Raises]
- `ValueError` — if `scale` is not finite.
- `ValueError` — when no non-empty mesh block contains `name` as point data.
- `ValueError` — when a matching array does not have shape `(n_points, 3)`.
:::

## Rotor displacement example

```python
from pyemsi import Plotter, examples

file_path = examples.structural_displacement_path()

plt1 = Plotter(file_path)
plt1.set_feature_edges(color="red", line_width=2)
plt1.set_scalar("von_mises", mode="element")
plt1.set_deformation("displacement", scale=5e4)
plt1.show()
```

<iframe
  src="/pyemsi/demos/set_deformation.html"
  style={{aspectRatio: "1.5"}}
/>

The [bundled dataset](../Examples/structural_displacement.md) exposes two scalars that can be
used independently for coloring: `displacement_magnitude` (point data, so `mode="node"`) and
`von_mises` (cell data, so `mode="element"`).

### See also

- [Structural Displacement](../Examples/structural_displacement.md) — the bundled dataset used above
- [`mesh`](./mesh.md) — inspect point-data arrays on loaded datasets
- [`set_scalar()`](./set_scalar.md) — configure scalar field coloring
- [`set_vector()`](./set_vector.md) — display vectors as glyphs
- [`show()`](./show.md) — apply the pipeline and render interactively
- [`export()`](./export.md) — apply the pipeline and save a screenshot
