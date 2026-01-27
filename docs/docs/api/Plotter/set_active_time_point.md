---
title: set_active_time_point()
sidebar_position: 8
---

Selects the active time step on time-aware readers (for example, `PVDReader`).

If the current `reader` is not time-aware, this method is a no-op and returns `None`.

:::tip[Parameters]
- **`time_point`** (`int`) — Zero-based time step index. Negative indices follow Python indexing.
:::

:::info[Returns]
- `None`
:::

### Example

```python
from pyemsi import Plotter

p = Plotter("path/to/output.pvd")
p.set_active_time_point(-1)
p.show()
```
