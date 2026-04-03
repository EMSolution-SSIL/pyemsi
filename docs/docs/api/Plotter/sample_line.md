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

### Sweep all time steps

```python
from pyemsi import Plotter, examples
from matplotlib import pyplot
import numpy as np

file_path = examples.transient_path()
plt = Plotter(file_path)

data = plt.sample_line(pointa=(0.02, 0.02, 0.0), pointb=(0.02, 0.02, 0.25), resolution=100)

time_values = [time_data["time"] for time_data in data]
distances = data[0]["B-Mag (T)"]["distance"]
value_grid = np.array([time_data["B-Mag (T)"]["value"] for time_data in data])
time_grid, distance_grid = np.meshgrid(time_values, distances, indexing="ij")

fig, ax = pyplot.subplots(subplot_kw={"projection": "3d"})
ax.plot_surface(time_grid, distance_grid, value_grid, cmap="viridis")
ax.set_xlabel("Time (s)")
ax.set_ylabel("Distance Along Line (m)")
ax.set_zlabel("B-Mag (T)")
ax.set_title("B-Mag (T) Along Sampled Line")
fig.tight_layout()
fig.savefig("docs/static/demos/sample_line.png")
```
![Sample Line](/demos/sample_line.png)

### Plot three time slices

```python
from pyemsi import Plotter, examples
from matplotlib import pyplot

file_path = examples.transient_path()
plt = Plotter(file_path)

data = plt.sample_line(pointa=(0.02, 0.02, 0.0), pointb=(0.02, 0.02, 0.25), resolution=100)
time_indices = sorted({0, len(data) // 2, len(data) - 1})

fig, ax = pyplot.subplots()
for idx in time_indices:
    ax.plot(
        data[idx]["B-Mag (T)"]["distance"],
        data[idx]["B-Mag (T)"]["value"],
        label=f"t = {data[idx]['time']:.3f} s",
    )
ax.set_xlabel("Distance Along Line (m)")
ax.set_ylabel("B-Mag (T)")
ax.set_title("B-Mag (T) Along Sampled Line at Three Time Points")
ax.legend()
fig.tight_layout()
fig.savefig("docs/static/demos/sample_line_time_slices.png")
```
![Sample Line Time Slices](/demos/sample_line_time_slices.png)

## See Also

- [`sample_lines()`](./sample_lines.md) — Sample along multiple lines
- [`sample_arc()`](./sample_arc.md) — Sample along a circular arc
- [`sample_point()`](./sample_point.md) — Sample at a single point coordinate
