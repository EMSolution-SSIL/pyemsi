---
title: time_values
sidebar_position: 16
---

All available time values on the underlying [`reader`](./reader.md), when it is time-aware (for example, [`PVDReader`](https://docs.pyvista.org/api/readers/_autosummary/pyvista.pvdreader)).

Proxies [`TimeReader.time_values`](https://docs.pyvista.org/api/readers/_autosummary/pyvista.timereader.time_values). Returns `None` if the reader is not time-aware.

:::info[Type]
- `Sequence[float] | None`
:::

### Example

```python
from pyemsi import Plotter, examples

file_path = examples.transient_path()
p = Plotter(file_path)

print(p.time_values)         # [0.01, 0.02, 0.03, ..., 0.1]
print(p.number_time_points)  # 10

# Use a specific value to activate a time step
p.set_active_time_value(p.time_values[-1])
```

### See also

- [`number_time_points`](./number_time_points.md) — total count of available time steps
- [`active_time_value`](./active_time_value.md) — read the currently active time value
- [`set_active_time_value()`](./set_active_time_value.md) — activate a time step by value
- [`set_active_time_point()`](./set_active_time_point.md) — activate a time step by index
- [`time_point_value()`](./time_point_value.md) — convert a time step index to its time value
