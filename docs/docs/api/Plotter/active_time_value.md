---
title: active_time_value
sidebar_position: 14
---

Active time value when the reader is time-aware. Inherited from PyVista's [`pyvista.TimeReader.active_time_value`](https://docs.pyvista.org/api/readers/_autosummary/pyvista.timereader.set_active_time_point#pyvista.TimeReader.set_active_time_point).

:::info[Returns]
- `float | None` : Active time value.
    - Returns `None` if the reader is not time-aware.
    - Changes when you call [`set_active_time_point(...)`](./set_active_time_point.md) or [`set_active_time_value(...)`](./set_active_time_value.md).
:::

### Example

```python
from pyemsi import Plotter

p = Plotter("path/to/output.pvd")
print(p.active_time_value)
```
