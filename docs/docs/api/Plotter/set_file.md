---
title: set_file()
sidebar_position: 1
---
Loads a mesh file by creating a PyVista reader via [`pyvista.get_reader(...)`](https://docs.pyvista.org/api/readers/_autosummary/pyvista.get_reader) and storing it on [`Plotter.reader`](/docs/api/Plotter/reader.md).

The dataset itself is loaded lazily (via the [`mesh`](/docs/api/Plotter/mesh.md) property or when [`show()`](/docs/api/Plotter/mesh.md) / [`export()`](/docs/api/Plotter/export.md) rebuild the scene).

:::tip[Parameters]
- **`filepath`** (`str | Path`) — Path to a mesh file supported by PyVista (e.g. `*.vtu`, `*.vtm`, `*.pvd`, `*.stl`, ...).
:::

:::info[Returns]
- `Plotter` — returns `self` to enable chaining.
:::

:::danger[Raises]
- `FileNotFoundError` — if `filepath` does not exist.
- `ValueError` — if PyVista cannot create a reader for the file.
:::

### Examples

```python
from pyemsi import Plotter

Plotter().set_file("mesh.vtm").show()
Plotter().set_file("output.pvd").set_scalar("B-Mag (T)", mode="element").show()
```

