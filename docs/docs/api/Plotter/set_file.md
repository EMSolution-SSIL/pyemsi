---
title: set_file
sidebar_position: 1
---

## `set_file(filepath)`

Loads a mesh file by creating a PyVista reader via `pyvista.get_reader(...)` and storing it on `Plotter.reader`.

The dataset itself is loaded lazily (via the `mesh` property or when `show()` / `export()` rebuild the scene).

### Parameters

- **`filepath`** (`str | Path`) — Path to a mesh file supported by PyVista (e.g. `*.vtu`, `*.vtm`, `*.pvd`, `*.stl`, ...).

### Returns

- `Plotter` — returns `self` to enable chaining.

### Raises

- `FileNotFoundError` — if `filepath` does not exist.
- `ValueError` — if PyVista cannot create a reader for the file.

### Examples

```python
from pyemsi import Plotter

Plotter().set_file("mesh.vtm").show()
Plotter().set_file("output.pvd").set_scalar("B-Mag (T)", mode="element").show()
```

