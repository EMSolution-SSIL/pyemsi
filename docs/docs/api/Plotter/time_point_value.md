---
title: time_point_value()
sidebar_position: 10
---

Returns the time value for a given time step index.

Delegates to [`TimeReader.time_point_value()`](https://docs.pyvista.org/api/readers/_autosummary/pyvista.timereader.time_point_value) on the underlying [`reader`](./reader.md).

If the current [`reader`](./reader.md) is not time-aware, this returns `None`.

:::tip[Parameters]
- **`time_point`** (`int`) — Zero-based time step index. Supports Python negative indexing: `0` is the first step, `-1` is the last, `-2` the second-to-last, and so on.
:::

:::info[Returns]
- `float | None` — The corresponding time value, or `None` if the reader is not time-aware.
:::

### Example

```python
from pyemsi import Plotter, examples

file_path = examples.transient_path()
p = Plotter(file_path)

print(p.time_point_value(0))   # 0.01  (first time step)
print(p.time_point_value(-1))  # 0.1   (last time step)
print(p.time_point_value(-2))  # 0.09  (second-to-last)
```

### See also

- [`set_active_time_point()`](./set_active_time_point.md) — activate a time step by index
- [`set_active_time_value()`](./set_active_time_value.md) — activate a time step by value
- [`time_values`](./time_values.md) — list all available time values
- [`active_time_value`](./active_time_value.md) — read the currently active time value
- [`number_time_points`](./number_time_points.md) — total count of available time steps
