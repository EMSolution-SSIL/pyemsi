---
sidebar_position: 22
title: sample_arcs_from_normal()
---

# `sample_arcs_from_normal()`

Sample mesh data along multiple circular arcs defined by normal vectors.

Creates circular arc probes for each `(center, normal, polar, angle)` tuple and samples the mesh data onto each arc. For temporal datasets, automatically sweeps all time points unless `time_value` is specified.

:::tip[Parameters]
- **`arcs`** (`Sequence[tuple[Sequence[float], Sequence[float] | None, Sequence[float] | None, float | None]]`) — List of arc definitions, each as a tuple `(center, normal, polar, angle)` where `center` is `[x, y, z]`, `normal` is `[x, y, z]` or `None` (defaults to `[0, 0, 1]`), `polar` is `[x, y, z]` or `None` (defaults to `[1, 0, 0]`), and `angle` is a float in degrees or `None` (defaults to 90).
- **`resolution`** (`int | list[int]`, default: `100`) — Number of segments to divide each arc into. Can be a single `int` (applied to all arcs) or a list of `int`s (one per arc).
- **`time_value`** (`float | None`, default: `None`) — Query a specific time value instead of sweeping all time points. Ignored for static datasets.
- **`tolerance`** (`float | None`, default: `None`) — Tolerance for the sample operation. If `None`, PyVista generates a tolerance automatically.
- **`progress_callback`** (`callable | None`, default: `None`) — Callback function for progress updates. Called with `(current_arc, total_arcs)`. Should return `True` to continue or `False` to cancel.
:::

:::info[Returns]
Returns a list of results (one per arc), where each result is a list of dictionaries (one per time step) with a `"time"` key and array names as keys. Each array has:
- For **scalars**: `"distance"`, `"value"`, `"x"`, `"y"`, `"z"` (sample point coordinates)
- For **vectors**: `"distance"`, `"x_value"`, `"y_value"`, `"z_value"`, `"tangential"` (component along arc), `"normal"` (component perpendicular to arc), `"x"`, `"y"`, `"z"` (sample point coordinates)

```python
[
    # Results for arc 0
    [
        {"time": 0.0, "scalar_name": {...}, ...},
        {"time": 0.01, "scalar_name": {...}, ...},
        ...
    ],
    # Results for arc 1
    [
        {"time": 0.0, "scalar_name": {...}, ...},
        {"time": 0.01, "scalar_name": {...}, ...},
        ...
    ],
    ...
]
```
:::

## Examples

### Sample multiple arcs with uniform resolution

```python
from pyemsi import Plotter
import matplotlib.pyplot as plt

p = Plotter("mesh.vtu")

# Define three arcs in different planes
arcs = [
    ([0, 0, 0], [0, 0, 1], [-1, 0, 0], 90),   # XY plane, quarter arc
    ([0, 0, 0], [1, 0, 0], [0, 1, 0], 180),   # YZ plane, half arc
    ([0, 0, 0], [0, 1, 0], [0, 0, 1], 360),   # XZ plane, full circle
]

data = p.sample_arcs_from_normal(arcs, resolution=100)

# Plot magnetic field for each arc
fig, axes = plt.subplots(3, 1, figsize=(8, 10))
for i, (arc_data, ax) in enumerate(zip(data, axes)):
    b_mag = arc_data[0]["B-Mag (T)"]["value"]
    distances = arc_data[0]["B-Mag (T)"]["distance"]
    ax.plot(distances, b_mag)
    ax.set_xlabel("Arc length")
    ax.set_ylabel("B-Mag (T)")
    ax.set_title(f"Arc {i}")

plt.tight_layout()
plt.show()
```

### Variable resolution per arc

```python
from pyemsi import Plotter

p = Plotter("mesh.vtu")

# Different resolutions for arcs of different lengths
arcs = [
    ([0, 0, 0], [0, 0, 1], [1, 0, 0], 45),    # Small arc
    ([0, 0, 0], [0, 0, 1], [1, 0, 0], 180),   # Medium arc
    ([0, 0, 0], [0, 0, 1], [1, 0, 0], 360),   # Full circle
]

# Proportional resolution: ~2 points per degree
resolutions = [90, 360, 720]

data = p.sample_arcs_from_normal(arcs, resolution=resolutions)

for i, arc_data in enumerate(data):
    num_points = len(arc_data[0]["Temperature"]["value"])
    print(f"Arc {i}: {num_points} points")
```

### Progress callback

```python
from pyemsi import Plotter

p = Plotter("mesh.vtu")

# Many arcs for detailed analysis
arcs = [
    ([0, 0, z], [0, 0, 1], [1, 0, 0], 360)  # Full circles at different Z
    for z in range(0, 10)
]

def progress(current, total):
    print(f"Processing arc {current + 1}/{total}")
    return True  # Continue

data = p.sample_arcs_from_normal(
    arcs,
    resolution=200,
    progress_callback=progress
)

print(f"Completed sampling {len(data)} arcs")
```

### Temporal analysis across multiple arcs

```python
from pyemsi import Plotter
import numpy as np
import matplotlib.pyplot as plt

p = Plotter("output.pvd")

# Radial arcs at different angles
angles = np.linspace(0, 360, 8, endpoint=False)
arcs = [
    ([0, 0, 0], [0, 0, 1], [np.cos(np.radians(a)), np.sin(np.radians(a)), 0], 90)
    for a in angles
]

data = p.sample_arcs_from_normal(arcs, resolution=50)

# Compare temperature evolution at arc midpoints
midpoint_idx = 25
times = [time_data["time"] for time_data in data[0]]

fig, ax = plt.subplots(figsize=(10, 6))
for i, arc_data in enumerate(data):
    temps = [time_data["Temperature"]["value"][midpoint_idx] for time_data in arc_data]
    ax.plot(times, temps, label=f"Arc {i} ({angles[i]:.0f}°)")

ax.set_xlabel("Time (s)")
ax.set_ylabel("Temperature (K)")
ax.set_title("Temperature evolution at arc midpoints")
ax.legend()
plt.show()
```

### Analyzing symmetry in cylindrical geometry

```python
from pyemsi import Plotter
import matplotlib.pyplot as plt

p = Plotter("mesh.vtu")

# Sample at different radii to check radial symmetry
radii = [1, 2, 3, 4, 5]
arcs = [
    ([0, 0, 0], [0, 0, 1], [r, 0, 0], 360)  # Full circles at different radii
    for r in radii
]

data = p.sample_arcs_from_normal(arcs, resolution=100)

# Check if field magnitude is constant around each circle
for i, (radius, arc_data) in enumerate(zip(radii, data)):
    b_mag = arc_data[0]["B-Mag (T)"]["value"]
    plt.plot(arc_data[0]["B-Mag (T)"]["distance"], b_mag, label=f"r={radius}")

plt.xlabel("Arc length")
plt.ylabel("B-Mag (T)")
plt.title("Radial field profile")
plt.legend()
plt.show()
```

### Using None for default parameters

```python
from pyemsi import Plotter

p = Plotter("mesh.vtu")

# Use None to get default normal=[0,0,1], polar=[1,0,0], angle=90
arcs = [
    ([0, 0, 0], None, None, None),          # All defaults: 90° in XY plane
    ([0, 0, 0], None, None, 180),           # Custom angle only
    ([0, 0, 0], [1, 0, 0], None, 180),     # Custom normal and angle
    ([0, 0, 0], [0, 1, 0], [1, 0, 0], 90), # All custom
]

data = p.sample_arcs_from_normal(arcs, resolution=50)

for i, arc_data in enumerate(data):
    coords = arc_data[0]["Temperature"]
    print(f"Arc {i}: Start ({coords['x'][0]:.2f}, {coords['y'][0]:.2f}, {coords['z'][0]:.2f})")
```

### Cancelling with progress callback

```python
from pyemsi import Plotter

p = Plotter("mesh.vtu")

arcs = [([0, 0, z], [0, 0, 1], [1, 0, 0], 360) for z in range(100)]

def progress(current, total):
    print(f"Arc {current + 1}/{total}")
    # Cancel after 10 arcs
    return current < 10

data = p.sample_arcs_from_normal(arcs, resolution=100, progress_callback=progress)

print(f"Processed {len(data)} arcs before cancellation")  # Will print 10
```

## Notes

- Each arc is constructed in a **counterclockwise** direction from the polar vector as viewed from the direction of the normal vector.
- Use `None` for `normal`, `polar`, or `angle` to get PyVista defaults: `[0, 0, 1]`, `[1, 0, 0]`, and 90 degrees respectively.
- The `progress_callback` is useful for long-running operations. Return `False` to cancel processing.
- For vectors, `tangential` represents the component along the arc direction, while `normal` represents the magnitude perpendicular to the arc.
- The `"x"`, `"y"`, `"z"` keys contain the actual 3D coordinates of sample points along each arc.

## See Also

- [`sample_arc_from_normal()`](sample_arc_from_normal.md) - Sample single arc defined by normal vector
- [`sample_arcs()`](sample_arcs.md) - Sample multiple arcs defined by start/end points
- [`sample_lines()`](sample_lines.md) - Sample along multiple straight lines
