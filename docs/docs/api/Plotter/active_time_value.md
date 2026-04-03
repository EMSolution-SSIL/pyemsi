---
title: active_time_value
sidebar_position: 14
---

The currently active time value on the underlying [`reader`](./reader.md), when it is time-aware (for example, [`PVDReader`](https://docs.pyvista.org/api/readers/_autosummary/pyvista.pvdreader)).

Proxies [`TimeReader.active_time_value`](https://docs.pyvista.org/api/readers/_autosummary/pyvista.timereader.active_time_value). Returns `None` if the reader is not time-aware. Updates when you call [`set_active_time_point()`](./set_active_time_point.md) or [`set_active_time_value()`](./set_active_time_value.md).

:::info[Type]
- `float | None`
:::

### Example

```python
from pyemsi import Plotter, examples

file_path = examples.transient_path()
p = Plotter(file_path)

print(p.active_time_value)    # 0.01  (first time step by default)

p.set_active_time_point(-1)
print(p.active_time_value)    # 0.1   (last time step)
```

### See also

- [`time_values`](./time_values.md) — list all available time values
- [`number_time_points`](./number_time_points.md) — total count of available time steps
- [`set_active_time_point()`](./set_active_time_point.md) — activate a time step by index
- [`set_active_time_value()`](./set_active_time_value.md) — activate a time step by value
- [`time_point_value()`](./time_point_value.md) — convert a time step index to its time value
