---
title: time_values
sidebar_position: 16
---
Available time values when the reader is time-aware.

:::info[Returns]
- `Sequence[float] | None`
    - Returns `None` if the reader is not time-aware.
:::

### Example

```python
from pyemsi import Plotter

p = Plotter("path/to/output.pvd")
print(p.time_values)
```
