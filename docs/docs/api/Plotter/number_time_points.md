---
title: number_time_points
sidebar_position: 15
---
Total number of time steps when the reader is time-aware. Inherited from PyVista's [`pyvista.TimeReader.number_time_points`](https://docs.pyvista.org/api/readers/_autosummary/pyvista.timereader.set_active_time_point#pyvista.TimeReader.set_active_time_point).

:::info[Returns]
- `int | None`
    - Returns `None` if the reader is not time-aware.
:::

### Example

```python
from pyemsi import Plotter

p = Plotter("path/to/output.pvd")
print(p.number_time_points)
```
