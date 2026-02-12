---
sidebar_position: 19
title: sample_lines()
---

# `sample_lines()`

Sample mesh data along multiple straight lines.

Creates line probes for each `(pointa, pointb)` pair and samples the mesh data onto each line. For temporal datasets, automatically sweeps all time points unless `time_value` is specified.

:::tip[Parameters]
- **`lines`** (`Sequence[tuple[Sequence[float], Sequence[float]]]`) — List of line definitions, each as a tuple `(pointa, pointb)` where `pointa` and `pointb` are `[x, y, z]` coordinates.
- **`resolution`** (`int | list[int]`, default: `100`) — Number of segments to divide each line into. Can be a single `int` (applied to all lines) or a list of `int`s (one per line).
- **`time_value`** (`float | None`, default: `None`) — Query a specific time value instead of sweeping all time points. Ignored for static datasets.
- **`tolerance`** (`float | None`, default: `None`) — Tolerance for the sample operation. If `None`, PyVista generates a tolerance automatically.
- **`progress_callback`** (`callable | None`, default: `None`) — Callback function for progress updates. Called with `(current_line, total_lines)`. Should return `True` to continue or `False` to cancel.
:::

:::info[Returns]
Returns a list of results (one per line), where each result is a list of dictionaries (one per time step) with a `"time"` key and array names as keys. Each array has:
- For **scalars**: `"distance"`, `"value"`, `"x"`, `"y"`, `"z"` (sample point coordinates)
- For **vectors**: `"distance"`, `"x_value"`, `"y_value"`, `"z_value"`, `"tangential"`, `"normal"`, `"x"`, `"y"`, `"z"` (sample point coordinates)

```python
[
    # First line results
    [
        # Time 0
        {"time": 0.0, "scalar_name": {"distance": [...], "value": [...], "x": [...], "y": [...], "z": [...]}, ...},
        # Time 1
        {"time": 0.01, "scalar_name": {"distance": [...], "value": [...], "x": [...], "y": [...], "z": [...]}, ...},
        ...
    ],
    # Second line results
    [
        {"time": 0.0, "scalar_name": {"distance": [...], "value": [...], "x": [...], "y": [...], "z": [...]}, ...},
        ...
    ],
    ...
]
```
:::

## Examples

### Compare profiles along multiple lines

```python
from pyemsi import Plotter
import matplotlib.pyplot as plt

p = Plotter("mesh.vtu")

# Define three parallel lines
lines = [
    ([0, 0, 0], [10, 0, 0]),  # y=0
    ([0, 1, 0], [10, 1, 0]),  # y=1
    ([0, 2, 0], [10, 2, 0]),  # y=2
]

data = p.sample_lines(lines, resolution=50)

# Plot temperature profiles for all three lines
for i, line_data in enumerate(data):
    # For static dataset, use first (only) time step
    temps = line_data[0]["Temperature"]["value"]
    distances = line_data[0]["Temperature"]["distance"]
    plt.plot(distances, temps, label=f"y={i}")

plt.xlabel("Distance along line")
plt.ylabel("Temperature")
plt.legend()
plt.show()
```

### Different resolutions per line

```python
from pyemsi import Plotter

p = Plotter("mesh.vtu")

lines = [
    ([0, 0, 0], [10, 0, 0]),
    ([0, 0, 0], [0, 10, 0]),
]

# First line with 100 points, second with 50
data = p.sample_lines(lines, resolution=[100, 50])

print(f"First line has {len(data[0][0]['Temperature']['value'])} points")   # 101
print(f"Second line has {len(data[1][0]['Temperature']['value'])} points")  # 51
```

### Temporal dataset with progress tracking

```python
from pyemsi import Plotter

def progress(current, total):
    print(f"Sampling line {current+1}/{total}")
    return True

p = Plotter("output.pvd")

# Radial lines from origin
import numpy as np
angles = np.linspace(0, 2*np.pi, 8, endpoint=False)
lines = [([0, 0, 0], [5*np.cos(a), 5*np.sin(a), 0]) for a in angles]

data = p.sample_lines(lines, resolution=25, progress_callback=progress)

# Access data: data[line_idx][time_idx][array_name]
first_line_time0 = data[0][0]  # Line 0, time 0
b_mag_along_line = first_line_time0["B-Mag (T)"]["value"]
distances = first_line_time0["B-Mag (T)"]["distance"]
```

### Grid of horizontal and vertical lines

```python
from pyemsi import Plotter

p = Plotter("mesh.vtu")

# Create grid of lines
lines = []
# Horizontal lines
for y in range(0, 11, 2):
    lines.append(([0, y, 0], [10, y, 0]))
# Vertical lines
for x in range(0, 11, 2):
    lines.append(([x, 0, 0], [x, 10, 0]))

data = p.sample_lines(lines, resolution=50)

print(f"Total lines: {len(data)}")  # 11
print(f"Points per line: {len(data[0][0]['Temperature']['value'])}")  # 51
```

## See Also

- [`sample_line()`](./sample_line.md) — Sample along a single line
- [`sample_arcs()`](./sample_arcs.md) — Sample along multiple circular arcs
- [`sample_points()`](./sample_points.md) — Sample at multiple point coordinates
