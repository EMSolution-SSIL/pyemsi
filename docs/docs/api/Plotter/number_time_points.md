---
title: number_time_points
sidebar_position: 15
---

The total number of available time steps on the underlying [`reader`](./reader.md), when it is time-aware (for example, [`PVDReader`](https://docs.pyvista.org/api/readers/_autosummary/pyvista.pvdreader)).

Proxies [`TimeReader.number_time_points`](https://docs.pyvista.org/api/readers/_autosummary/pyvista.timereader.number_time_points). Returns `None` if the reader is not time-aware.

:::info[Type]
- `int | None`
:::

### Example

```python
from pyemsi import Plotter, examples

file_path = examples.transient_path()
p = Plotter(file_path)
p.set_scalar("B-Mag (T)")
p.set_block_visibility("4", False)

print(p.number_time_points)  # 10

# Iterate over all time steps
for i in range(p.number_time_points):
    p.set_active_time_point(i)
    p.export(f"frame_{i:02d}.png")
```

### See also

- [`time_values`](./time_values.md) — list all available time values
- [`active_time_value`](./active_time_value.md) — read the currently active time value
- [`set_active_time_point()`](./set_active_time_point.md) — activate a time step by index
- [`set_active_time_value()`](./set_active_time_value.md) — activate a time step by value
- [`time_point_value()`](./time_point_value.md) — convert a time step index to its time value
