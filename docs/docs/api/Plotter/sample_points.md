---
sidebar_position: 17
title: sample_points()
---

# `sample_points()`

Sample mesh data at multiple point coordinates (point cloud).

This method creates a point cloud probe from the specified coordinates and samples the mesh data onto each point. For temporal datasets, automatically sweeps all time points unless `time_value` is specified. For static datasets, returns values directly.

:::tip[Parameters]
- **`points`** (`Sequence[Sequence[float]]`) — List of 3D coordinates `[[x, y, z], ...]` to sample at.

- **`time_value`** (`float | None`, default: `None`) — Query a specific time value instead of sweeping all time points. Ignored for static datasets.
- **`tolerance`** (`float | None`, default: `None`) — Tolerance for the sample operation. If `None`, PyVista generates a tolerance automatically.
- **`progress_callback`** (`callable | None`, default: `None`) — Callback function for progress updates during temporal sweeps. Called with `(current, total)`. Should return `True` to continue or `False` to cancel.
:::

:::info[Returns]
Returns a list of dictionaries (one per point) with array names as keys. Each dictionary includes a `"coordinates"` key with the probe position.

```python
[
    {
        "scalar_name": {
            "time": [0.0, 0.001, 0.002, ...],
            "value": [val0, val1, val2, ...]
        },
        "coordinates": {"x": 1.0, "y": 2.0, "z": 3.0},
        ...
    },
    {
        "scalar_name": {
            "time": [0.0, 0.001, 0.002, ...],
            "value": [val0, val1, val2, ...]
        },
        "coordinates": {"x": 4.0, "y": 5.0, "z": 6.0},
        ...
    },
    ...
]
```
:::

## Examples

### Static mesh with point cloud

```python
from pyemsi import Plotter

p = Plotter("mesh.vtu")
points = [
    [1.0, 2.0, 3.0],
    [4.0, 5.0, 6.0],
    [7.0, 8.0, 9.0]
]
data = p.sample_points(points)

# Access data for first point
print(data[0]["Temperature"]["value"][0])
print(data[0]["coordinates"]["x"])  # 1.0

# Access data for second point
print(data[1]["Temperature"]["value"][0])
print(data[1]["coordinates"]["x"])  # 4.0
```

### Temporal dataset with progress callback

```python
from pyemsi import Plotter

def progress(current, total):
    print(f"Progress: {current}/{total}")
    return True  # Continue (return False to cancel)

p = Plotter("output.pvd")
points = [[x, 0, 0] for x in range(10)]
data = p.sample_points(points, progress_callback=progress)

# Plot time series for first point
import matplotlib.pyplot as plt
times = data[0]["B-Mag (T)"]["time"]
values = data[0]["B-Mag (T)"]["value"]
plt.plot(times, values)
plt.show()
```

### Sampling specific time value

```python
from pyemsi import Plotter

p = Plotter("output.pvd")
points = [[x, y, 0] for x in range(5) for y in range(5)]
# Sample at t=0.05 only
data = p.sample_points(points, time_value=0.05)

# Extract spatial distribution at t=0.05
temps = [pt["Temperature"]["value"][0] for pt in data]
x_coords = [pt["coordinates"]["x"] for pt in data]
y_coords = [pt["coordinates"]["y"] for pt in data]
```

## See Also

- [`sample_point()`](./sample_point.md) — Sample at a single point coordinate
- [`sample_line()`](./sample_line.md) — Sample along a straight line
- [`query_points()`](./query_points.md) — Query data by point IDs (indexed access)
