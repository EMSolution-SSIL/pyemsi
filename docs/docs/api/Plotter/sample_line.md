---
sidebar_position: 18
title: sample_line()
---

# `sample_line()`

Sample mesh data along a straight line.

Creates a line probe from `pointa` to `pointb` with the specified resolution and samples the mesh data onto each point along the line. For temporal datasets, automatically sweeps all time points unless `time_value` is specified.

:::tip[Parameters]
- **`pointa`** (`Sequence[float]`) — Starting point `[x, y, z]` of the line.
- **`pointb`** (`Sequence[float]`) — Ending point `[x, y, z]` of the line.
- **`resolution`** (`int`, default: `100`) — Number of segments to divide the line into. The resulting line will have `resolution + 1` points.
- **`time_value`** (`float | None`, default: `None`) — Query a specific time value instead of sweeping all time points. Ignored for static datasets.
- **`tolerance`** (`float | None`, default: `None`) — Tolerance for the sample operation. If `None`, PyVista generates a tolerance automatically.
:::

:::info[Returns]
Returns a list of dictionaries (one per time step) with a `"time"` key and array names as keys. Each array has:
- For **scalars**: `"distance"`, `"value"`, `"x"`, `"y"`, `"z"` (sample point coordinates)
- For **vectors**: `"distance"`, `"x_value"`, `"y_value"`, `"z_value"`, `"tangential"` (component along path), `"normal"` (component perpendicular to path), `"x"`, `"y"`, `"z"` (sample point coordinates)

For static datasets, returns a single-element list with time 0.0.

```python
[
    # Time 0 (or single time for static)
    {
        "time": 0.0,
        "scalar_name": {
            "distance": [0.0, 0.1, 0.2, ...],
            "value": [val0, val1, val2, ...],
            "x": [x0, x1, x2, ...],
            "y": [y0, y1, y2, ...],
            "z": [z0, z1, z2, ...]
        },
        "vector_name": {
            "distance": [0.0, 0.1, 0.2, ...],
            "x_value": [x0, x1, x2, ...],
            "y_value": [y0, y1, y2, ...],
            "z_value": [z0, z1, z2, ...],
            "tangential": [t0, t1, t2, ...],
            "normal": [n0, n1, n2, ...],
            "x": [x0, x1, x2, ...],
            "y": [y0, y1, y2, ...],
            "z": [z0, z1, z2, ...]
        },
        ...
    },
    # Time 1
    {"time": 0.01, ...},
    ...
]
```
:::

## Examples

### Plot line profile for static mesh

```python
from pyemsi import Plotter
import matplotlib.pyplot as plt

p = Plotter("mesh.vtu")
data = p.sample_line([0, 0, 0], [10, 0, 0], resolution=100)

# Extract temperature profile along line (static dataset has 1 time step)
temps = data[0]["Temperature"]["value"]
distances = data[0]["Temperature"]["distance"]

plt.plot(distances, temps)
plt.xlabel("Distance along line")
plt.ylabel("Temperature")
plt.show()
```

### Temporal dataset line sampling

```python
from pyemsi import Plotter
import matplotlib.pyplot as plt
import numpy as np

p = Plotter("output.pvd")
data = p.sample_line([0, 0, 0], [10, 0, 0], resolution=50)

# Plot time evolution at line midpoint (point 25 of 51)
midpoint_idx = 25
b_values = [time_data["B-Mag (T)"]["value"][midpoint_idx] for time_data in data]

plt.plot(range(len(data)), b_values)
plt.xlabel("Time step")
plt.ylabel("B-Mag (T) at midpoint")
plt.show()
```

### Create 2D plot (position vs time)

```python
from pyemsi import Plotter
import matplotlib.pyplot as plt
import numpy as np

p = Plotter("output.pvd")
data = p.sample_line([0, 0, 0], [10, 0, 0], resolution=50)

# Build 2D array: rows = position, cols = time
n_points = len(data[0]["Temperature"]["value"])
n_times = len(data)
temp_2d = np.zeros((n_points, n_times))

for t_idx, time_data in enumerate(data):
    temp_2d[:, t_idx] = time_data["Temperature"]["value"]

distances = data[0]["Temperature"]["distance"]

plt.pcolormesh(range(n_times), distances, temp_2d, shading='auto')
plt.xlabel("Time step")
plt.ylabel("Distance along line")
plt.colorbar(label="Temperature")
plt.show()
```

### Sample from specific block

```python
from pyemsi import Plotter

p = Plotter("output.vtm")
# Sample only from the "coil" block
data = p.sample_line([0, 0, 0], [10, 0, 0], block_name="coil", resolution=100)
```

## See Also

- [`sample_lines()`](./sample_lines.md) — Sample along multiple lines
- [`sample_arc()`](./sample_arc.md) — Sample along a circular arc
- [`sample_point()`](./sample_point.md) — Sample at a single point coordinate
