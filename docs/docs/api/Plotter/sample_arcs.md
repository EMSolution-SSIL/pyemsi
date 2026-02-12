---
sidebar_position: 21
title: sample_arcs()
---

# `sample_arcs()`

Sample mesh data along multiple circular arcs.

Creates circular arc probes for each `(pointa, pointb, center)` tuple and samples the mesh data onto each arc. For temporal datasets, automatically sweeps all time points unless `time_value` is specified.

:::tip[Parameters]
- **`arcs`** (`Sequence[tuple[Sequence[float], Sequence[float], Sequence[float]]]`) — List of arc definitions, each as a tuple `(pointa, pointb, center)` where each component is an `[x, y, z]` coordinate.
- **`resolution`** (`int | list[int]`, default: `100`) — Number of segments to divide each arc into. Can be a single `int` (applied to all arcs) or a list of `int`s (one per arc).
- **`negative`** (`bool`, default: `False`) — If `False`, arcs span the positive angle. If `True`, span the negative (reflex) angle. Applied to all arcs.
- **`time_value`** (`float | None`, default: `None`) — Query a specific time value instead of sweeping all time points. Ignored for static datasets.
- **`tolerance`** (`float | None`, default: `None`) — Tolerance for the sample operation. If `None`, PyVista generates a tolerance automatically.
- **`progress_callback`** (`callable | None`, default: `None`) — Callback function for progress updates. Called with `(current_arc, total_arcs)`. Should return `True` to continue or `False` to cancel.
:::

:::info[Returns]
Returns a list of results (one per arc), where each result is a list of dictionaries (one per time step) with a `"time"` key and array names as keys. Each array has:
- For **scalars**: `"distance"`, `"value"`, `"x"`, `"y"`, `"z"` (sample point coordinates)
- For **vectors**: `"distance"`, `"x_value"`, `"y_value"`, `"z_value"`, `"tangential"`, `"normal"`, `"x"`, `"y"`, `"z"` (sample point coordinates)

```python
[
    # First arc results
    [
        # Time 0
        {"time": 0.0, "scalar_name": {"distance": [...], "value": [...], "x": [...], "y": [...], "z": [...]}, ...},
        # Time 1
        {"time": 0.01, "scalar_name": {"distance": [...], "value": [...], "x": [...], "y": [...], "z": [...]}, ...},
        ...
    ],
    # Second arc results
    [
        {"time": 0.0, "scalar_name": {"distance": [...], "value": [...], "x": [...], "y": [...], "z": [...]}, ...},
        ...
    ],
    ...
]
```
:::

## Examples

### Compare profiles along concentric arcs

```python
from pyemsi import Plotter
import matplotlib.pyplot as plt
import numpy as np

p = Plotter("mesh.vtu")

# Define three concentric quarter-circle arcs
radii = [5, 10, 15]
arcs = [
    ([r, 0, 0], [0, r, 0], [0, 0, 0])
    for r in radii
]

data = p.sample_arcs(arcs, resolution=50)

# Plot magnetic field for all three arcs (static dataset)
for i, (arc_data, r) in enumerate(zip(data, radii)):
    b_mag = arc_data[0]["B-Mag (T)"]["value"]
    distances = arc_data[0]["B-Mag (T)"]["distance"]
    plt.plot(distances, b_mag, label=f"r={r}")

plt.xlabel("Arc length")
plt.ylabel("B-Mag (T)")
plt.legend()
plt.show()
```

### Different resolutions per arc

```python
from pyemsi import Plotter

p = Plotter("mesh.vtu")

arcs = [
    ([5, 0, 0], [0, 5, 0], [0, 0, 0]),   # Small arc
    ([10, 0, 0], [0, 10, 0], [0, 0, 0]), # Larger arc
]

# More points for larger arc
data = p.sample_arcs(arcs, resolution=[50, 100])

print(f"First arc has {len(data[0][0]['Temperature']['value'])} points")   # 51
print(f"Second arc has {len(data[1][0]['Temperature']['value'])} points")  # 101
```

### Temporal dataset with progress tracking

```python
from pyemsi import Plotter
import numpy as np

def progress(current, total):
    print(f"Sampling arc {current+1}/{total}")
    return True

p = Plotter("output.pvd")

# Multiple arcs at different heights
heights = [0, 2, 4, 6, 8]
arcs = [
    ([5, 0, z], [0, 5, z], [0, 0, z])
    for z in heights
]

data = p.sample_arcs(arcs, resolution=50, progress_callback=progress)

# Access data: data[arc_idx][time_idx][array_name]
first_arc_time0 = data[0][0]  # Arc 0, time 0
b_mag_along_arc = first_arc_time0["B-Mag (T)"]["value"]
distances = first_arc_time0["B-Mag (T)"]["distance"]
time_val = first_arc_time0["time"]
print(f"Data at t={time_val}")
```

### Full circles at different radii

```python
from pyemsi import Plotter
import matplotlib.pyplot as plt
import numpy as np

p = Plotter("mesh.vtu")

# Full circles (360 degrees) - start and end at same point
radii = [5, 10, 15, 20]
arcs = [
    ([r, 0, 0], [r, 0, 0], [0, 0, 0])
    for r in radii
]

data = p.sample_arcs(arcs, resolution=360)

# Create polar plot for each circle (static dataset)
fig, axes = plt.subplots(2, 2, subplot_kw=dict(projection='polar'))
angles = np.linspace(0, 2*np.pi, 361)

for ax, arc_data, r in zip(axes.flat, data, radii):
    b_mag = arc_data[0]["B-Mag (T)"]["value"]
    ax.plot(angles, b_mag)
    ax.set_title(f"r={r}")

plt.tight_layout()
plt.show()
```

### Using negative arc direction

```python
from pyemsi import Plotter

p = Plotter("mesh.vtu")

# Two arcs: one positive (90°), one negative (270°)
arcs = [
    ([5, 0, 0], [0, 5, 0], [0, 0, 0]),
    ([5, 0, 0], [0, 5, 0], [0, 0, 0]),
]

data_pos = p.sample_arcs(arcs[:1], resolution=50, negative=False)
data_neg = p.sample_arcs(arcs[1:], resolution=150, negative=True)

print(f"Positive arc points: {len(data_pos[0][0]['Temperature']['value'])}")  # 51
print(f"Negative arc points: {len(data_neg[0][0]['Temperature']['value'])}")  # 151
```

### Sample from specific block

```python
from pyemsi import Plotter

p = Plotter("output.vtm")

# Sample multiple arcs from the "rotor" block only
arcs = [
    ([10, 0, 0], [0, 10, 0], [0, 0, 0]),
    ([15, 0, 0], [0, 15, 0], [0, 0, 0]),
]

data = p.sample_arcs(arcs, block_name="rotor", resolution=100)
```

## See Also

- [`sample_arc()`](./sample_arc.md) — Sample along a single circular arc
- [`sample_lines()`](./sample_lines.md) — Sample along multiple straight lines
- [`sample_points()`](./sample_points.md) — Sample at multiple point coordinates
