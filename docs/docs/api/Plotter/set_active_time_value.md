---
title: set_active_time_value()
sidebar_position: 9
---

Selects the active time value on time-aware readers (for example, [`pyvista.PVDReader`](https://docs.pyvista.org/api/readers/_autosummary/pyvista.pvdreader)).

If the current [`reader`](/docs/api/Plotter/reader.md) is not time-aware, this method is a no-op and returns `None`.

:::tip[Parameters]
- **`time_value`** (`float`) — Time value to activate.
:::

:::info[Returns]
- `None`
:::

### Example

```python
from pyemsi import Plotter

p = Plotter("path/to/output.pvd")
p.set_active_time_value(0.05)
p.show()
```
