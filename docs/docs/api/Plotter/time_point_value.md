---
title: time_point_value()
sidebar_position: 10
---
Returns the time value for a time step when the reader is time-aware.

If the current [`reader`](/docs/api/Plotter/reader.md) is not time-aware, this returns `None`.

:::tip[Parameters]
- **`time_point`** (`int`) — Zero-based time step index. Negative indices follow Python indexing.
:::

:::info[Returns]
- `float | None`
:::

### Example

```python
from pyemsi import Plotter

p = Plotter("path/to/output.pvd")
last_time = p.time_point_value(-1)
```
