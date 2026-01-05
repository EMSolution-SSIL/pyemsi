---
title: mesh
sidebar_position: 13
---

## `mesh`

Lazily loaded mesh from the current `reader` in `pyvista` format.

:::info[Returns]
- [`pyvista.DataSet`](https://docs.pyvista.org/api/core/_autosummary/pyvista.dataset) | [`pyvista.MultiBlock`](https://docs.pyvista.org/api/core/_autosummary/pyvista.multiblock) | `None`
    - Accessing `mesh` reads data from the reader and caches it on [`Plotter`](/docs/api/Plotter/index.md).
    - For [`PVDReader`](https://docs.pyvista.org/api/readers/_autosummary/pyvista.pvdreader), `mesh` returns the first block from [`reader.read()`](https://docs.pyvista.org/api/readers/_autosummary/pyvista.basereader.read#pyvista.BaseReader.read).
    - [`show()`](/docs/api/Plotter/mesh.md) and [`export()`](/docs/api/Plotter/export.md) reset the cached mesh before rebuilding the scene.
:::

:::danger[Raises]
- `ValueError` — if no reader is available (call [`set_file()`](/docs/api/Plotter/set_file.md) first).
:::

### Example

```python
from pyemsi import Plotter

p = Plotter("mesh.vtm")
dataset = p.mesh
print(dataset.n_points)
```
