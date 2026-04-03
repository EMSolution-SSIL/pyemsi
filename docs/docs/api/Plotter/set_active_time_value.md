---
title: set_active_time_value()
sidebar_position: 9
---

Selects the active time step by its time value on time-aware readers (for example, [`PVDReader`](https://docs.pyvista.org/api/readers/_autosummary/pyvista.pvdreader)).

Delegates to [`TimeReader.set_active_time_value()`](https://docs.pyvista.org/api/readers/_autosummary/pyvista.timereader.set_active_time_value) on the underlying [`reader`](./reader.md).

If the current [`reader`](./reader.md) is not time-aware, this method is a silent no-op and returns `None`.

:::tip[Parameters]
- **`time_value`** (`float`) — The time value to activate. Must match one of the values in [`time_values`](./time_values.md). Use [`set_active_time_point()`](./set_active_time_point.md) instead if you want to select by index rather than by value.
:::

:::info[Returns]
- `None`
:::

:::note
After calling `set_active_time_value()`, the next call to [`show()`](./show.md) or [`export()`](./export.md) will re-read the mesh at the newly selected time step.
You can confirm the active time value with [`active_time_value`](./active_time_value.md).
:::

### Example

```python
from pyemsi import Plotter, examples

file_path = examples.transient_path()
p = Plotter(file_path)

print(p.time_values)          # [0.01, 0.02, 0.03, ..., 0.1]

p.set_active_time_value(0.05) # select the t = 0.05 s time step
print(p.active_time_value)    # 0.05

p.set_scalar("B-Mag (T)")
p.show()
```

### See also

- [`set_active_time_point()`](./set_active_time_point.md) — select a time step by index instead of value
- [`time_point_value()`](./time_point_value.md) — convert a time step index to its time value
- [`active_time_value`](./active_time_value.md) — read the currently active time value
- [`time_values`](./time_values.md) — list all available time values
- [`number_time_points`](./number_time_points.md) — total count of available time steps
