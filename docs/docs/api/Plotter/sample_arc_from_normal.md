---
sidebar_position: 21
title: sample_arc_from_normal()
---

# `sample_arc_from_normal()`

Sample mesh data along a circular arc defined by a normal vector.

Creates a circular arc probe defined by a normal to the plane of the arc, a polar starting vector, and an angle. The arc is sampled in a counterclockwise direction from the polar vector. For temporal datasets, automatically sweeps all time points unless `time_value` is specified.

:::tip[Parameters]
- **`center`** (`Sequence[float]`) — Center point `[x, y, z]` of the circle that defines the arc.
- **`resolution`** (`int`, default: `100`) — Number of segments to divide the arc into. The resulting arc will have `resolution + 1` points.
- **`normal`** (`Sequence[float] | None`, default: `None`) — Normal vector `[x, y, z]` to the plane of the arc. If `None`, defaults to `[0, 0, 1]` (positive Z direction).
- **`polar`** (`Sequence[float] | None`, default: `None`) — Starting point of the arc in polar coordinates `[x, y, z]`. If `None`, defaults to `[1, 0, 0]` (positive X direction).
- **`angle`** (`float | None`, default: `None`) — Arc length in degrees, beginning at the polar vector in a counterclockwise direction. If `None`, defaults to 90 degrees.
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

# Quarter circle arc in XY plane from negative X axis
data = p.sample_arc_from_normal(
    center=[0, 0, 0],
    normal=[0, 0, 1],     # Z-normal defines XY plane
    polar=[-1, 0, 0],     # Start from negative X axis
    angle=90,             # 90 degree arc
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

# Half circle in YZ plane
data = p.sample_arc_from_normal(
    center=[0, 0, 0],
    normal=[1, 0, 0],     # X-normal defines YZ plane
    polar=[0, 1, 0],      # Start from positive Y axis
    angle=180,            # Half circle
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

### Full circle with default parameters

```python
from pyemsi import Plotter

p = Plotter("mesh.vtu")

# Full circle in XY plane centered at origin
# Using defaults: normal=[0,0,1], polar=[1,0,0], angle=90
data = p.sample_arc_from_normal(
    center=[0, 0, 0],
    angle=360,            # Override default angle for full circle
    resolution=200
)

# Get coordinates along the circle
coords_x = data[0]["B-Mag (T)"]["x"]
coords_y = data[0]["B-Mag (T)"]["y"]
coords_z = data[0]["B-Mag (T)"]["z"]

import matplotlib.pyplot as plt
plt.plot(coords_x, coords_y)
plt.axis('equal')
plt.xlabel("X")
plt.ylabel("Y")
plt.title("Sample points on circle")
plt.show()
```

### Analyzing vector components

```python
from pyemsi import Plotter
import matplotlib.pyplot as plt

p = Plotter("mesh.vtu")

# Arc for analyzing current density
data = p.sample_arc_from_normal(
    center=[0, 0, 0],
    normal=[0, 0, 1],
    polar=[1, 0, 0],
    angle=90,
    resolution=100
)

# Get tangential and normal components
tangential = data[0]["Current Density"]["tangential"]
normal = data[0]["Current Density"]["normal"]
distance = data[0]["Current Density"]["distance"]

fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
ax1.plot(distance, tangential, label='Tangential')
ax1.set_ylabel('Tangential Component')
ax1.legend()

ax2.plot(distance, normal, label='Normal', color='red')
ax2.set_ylabel('Normal Component')
ax2.set_xlabel('Arc Distance')
ax2.legend()

plt.tight_layout()
plt.show()
```

### Specific time value query

```python
from pyemsi import Plotter

p = Plotter("output.pvd")

# Sample at t=0.05 only
data = p.sample_arc_from_normal(
    center=[0, 0, 0],
    normal=[0, 1, 0],
    polar=[1, 0, 0],
    angle=180,
    resolution=100,
    time_value=0.05
)

# data contains only one time step
print(f"Time: {data[0]['time']}")
print(f"Temperature range: {min(data[0]['Temperature']['value']):.2f} - {max(data[0]['Temperature']['value']):.2f}")
```

## Notes

- The arc is constructed in a **counterclockwise** direction from the polar vector as viewed from the direction of the normal vector.
- The default normal `[0, 0, 1]` and polar `[1, 0, 0]` create an arc in the XY plane starting from the positive X axis.
- For vectors, `tangential` represents the component along the arc direction, while `normal` represents the magnitude perpendicular to the arc.
- The `"x"`, `"y"`, `"z"` keys contain the actual 3D coordinates of sample points along the arc.
- This method is useful when you want to define an arc by plane orientation rather than explicit start/end points.

## See Also

- [`sample_arc()`](sample_arc.md) - Sample along arc defined by start/end points
- [`sample_arcs_from_normal()`](sample_arcs_from_normal.md) - Sample multiple arcs defined by normal vectors
- [`sample_line()`](sample_line.md) - Sample along straight line
