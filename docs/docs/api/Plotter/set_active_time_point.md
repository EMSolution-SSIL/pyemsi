---
title: set_active_time_point()
sidebar_position: 8
---

Selects the active time step on time-aware readers (for example, [`PVDReader`](https://docs.pyvista.org/api/readers/_autosummary/pyvista.pvdreader)).

Delegates to [`TimeReader.set_active_time_point()`](https://docs.pyvista.org/api/readers/_autosummary/pyvista.timereader.set_active_time_point) on the underlying [`reader`](./reader.md).

If the current [`reader`](./reader.md) is not time-aware, this method is a silent no-op and returns `None`.

:::tip[Parameters]
- **`time_point`** (`int`) — Zero-based index of the time step to activate. Supports Python negative indexing: `0` selects the first time step, `-1` the last, `-2` the second-to-last, and so on.
:::

:::info[Returns]
- `None`
:::

:::note
After calling `set_active_time_point()`, the next call to [`show()`](./show.md) or [`export()`](./export.md) will re-read the mesh at the newly selected time step.
You can inspect the resulting time value with [`active_time_value`](./active_time_value.md), or retrieve all available time values via [`time_values`](./time_values.md).
:::

### Example

```python
from pyemsi import Plotter, examples

file_path = examples.transient_path()
p = Plotter(file_path)

print(p.number_time_points)   # 10
print(p.time_values)          # [0.01, 0.02, 0.03, ..., 0.1]

p.set_active_time_point(0)    # first time step  (t = 0.01 s)
p.set_active_time_point(-1)   # last time step   (t = 0.1 s,  equivalent to index 9)
p.set_active_time_point(-2)   # second-to-last   (t = 0.09 s, equivalent to index 8)

p.set_scalar("B-Mag (T)")
p.show()
```

### See also

- [`set_active_time_value()`](./set_active_time_value.md) — select a time step by its actual time value instead of its index
- [`time_point_value()`](./time_point_value.md) — convert a time step index to its time value
- [`active_time_value`](./active_time_value.md) — read the currently active time value
- [`time_values`](./time_values.md) — list all available time values
- [`number_time_points`](./number_time_points.md) — total count of available time steps
