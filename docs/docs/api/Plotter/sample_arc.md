---
sidebar_position: 20
title: sample_arc()
---

# `sample_arc()`

Sample mesh data along a circular arc.

Creates a circular arc probe from `pointa` to `pointb` around `center` with the specified resolution and samples the mesh data onto each point along the arc. For temporal datasets, automatically sweeps all time points unless `time_value` is specified.

:::tip[Parameters]
- **`pointa`** (`Sequence[float]`) — Starting point `[x, y, z]` of the arc.
- **`pointb`** (`Sequence[float]`) — Ending point `[x, y, z]` of the arc.
- **`center`** (`Sequence[float]`) — Center point `[x, y, z]` of the circle containing the arc.
- **`resolution`** (`int`, default: `100`) — Number of segments to divide the arc into. The resulting arc will have `resolution + 1` points.
- **`negative`** (`bool`, default: `False`) — If `False`, the arc spans the positive angle from `pointa` to `pointb` around `center`. If `True`, spans the negative (reflex) angle.
- **`time_value`** (`float | None`, default: `None`) — Query a specific time value instead of sweeping all time points. Ignored for static datasets.
- **`tolerance`** (`float | None`, default: `None`) — Tolerance for the sample operation. If `None`, PyVista generates a tolerance automatically.
:::

:::info[Returns]
Returns a list of dictionaries (one per time step) with a `"time"` key and array names as keys. Each array has:
- For **scalars**: `"distance"`, `"value"`, `"x"`, `"y"`, `"z"` (sample point coordinates)
- For **vectors**: `"distance"`, `"x_value"`, `"y_value"`, `"z_value"`, `"tangential"` (component along arc), `"normal"` (component perpendicular to arc), `"x"`, `"y"`, `"z"` (sample point coordinates)

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

### Plot arc profile for static mesh

```python
from pyemsi import Plotter
import matplotlib.pyplot as plt
import numpy as np

p = Plotter("mesh.vtu")

# Quarter circle arc in XY plane
data = p.sample_arc(
    pointa=[1, 0, 0],
    pointb=[0, 1, 0],
    center=[0, 0, 0],
    resolution=50
)

# Extract magnetic field along arc (static dataset has 1 time step)
b_mag = data[0]["B-Mag (T)"]["value"]
arc_distances = data[0]["B-Mag (T)"]["distance"]
time_val = data[0]["time"]

plt.plot(arc_distances, b_mag)
plt.xlabel("Arc length")
plt.ylabel("B-Mag (T)")
plt.title(f"Profile at t={time_val}")
plt.show()
```

### Temporal dataset arc sampling

```python
from pyemsi import Plotter
import matplotlib.pyplot as plt

p = Plotter("output.pvd")

# Circular arc around coil
data = p.sample_arc(
    pointa=[5, 0, 0],
    pointb=[0, 5, 0],
    center=[0, 0, 0],
    resolution=100
)

# Plot time evolution at arc midpoint (point 50 of 101)
midpoint_idx = 50
b_values = [time_data["B-Mag (T)"]["value"][midpoint_idx] for time_data in data]
times = [time_data["time"] for time_data in data]

plt.plot(times, b_values)
plt.xlabel("Time (s)")
plt.ylabel("B-Mag (T) at midpoint")
plt.show()
```

### Using negative arc direction

```python
from pyemsi import Plotter

p = Plotter("mesh.vtu")

# Positive arc (short path, 90 degrees)
data_pos = p.sample_arc(
    pointa=[1, 0, 0],
    pointb=[0, 1, 0],
    center=[0, 0, 0],
    resolution=50,
    negative=False
)

# Negative arc (long path, 270 degrees)
data_neg = p.sample_arc(
    pointa=[1, 0, 0],
    pointb=[0, 1, 0],
    center=[0, 0, 0],
    resolution=150,
    negative=True
)

print(f"Positive arc points: {len(data_pos[0]['Temperature']['value'])}")  # 51
print(f"Negative arc points: {len(data_neg[0]['Temperature']['value'])}")  # 151
```

### Sample from specific block

```python
from pyemsi import Plotter

p = Plotter("output.vtm")

# Sample only from the "stator" block along an arc
data = p.sample_arc(
    pointa=[10, 0, 0],
    pointb=[0, 10, 0],
    center=[0, 0, 0],
    block_name="stator",
    resolution=100
)
```

### Create polar plot

```python
from pyemsi import Plotter
import matplotlib.pyplot as plt
import numpy as np

p = Plotter("mesh.vtu")

# Full circle arc (360 degrees)
data = p.sample_arc(
    pointa=[5, 0, 0],
    pointb=[5, 0, 0],  # Same as start for full circle
    center=[0, 0, 0],
    resolution=360
)

# Extract values and angles (static dataset)
b_mag = data[0]["B-Mag (T)"]["value"]
angles = np.linspace(0, 2*np.pi, len(b_mag))
time_val = data[0]["time"]

# Create polar plot
fig, ax = plt.subplots(subplot_kw=dict(projection='polar'))
ax.plot(angles, b_mag)
ax.set_title(f"B-Mag around coil (t={time_val})")
plt.show()
```

## See Also

- [`sample_arcs()`](./sample_arcs.md) — Sample along multiple circular arcs
- [`sample_line()`](./sample_line.md) — Sample along a straight line
- [`sample_point()`](./sample_point.md) — Sample at a single point coordinate
