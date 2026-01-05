---
title: reader
sidebar_position: 12
---

PyVista reader created by [`set_file()`](./set_file.md) or the `filepath` constructor argument.

:::info[Returns]
- [`pyvista.BaseReader`](https://docs.pyvista.org/api/readers/_autosummary/pyvista.basereader) | `None`
    - `None` until you load a file.
    - For `*.pvd`, the reader is a [`PVDReader`](https://docs.pyvista.org/api/readers/_autosummary/pyvista.pvdreader), which is time-aware.
:::

### Example

```python
from pyemsi import Plotter

p = Plotter("path/to/output.pvd")
print(type(p.reader).__name__)
```
