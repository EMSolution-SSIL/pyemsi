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

### Sweep all time steps

```python
from pyemsi import Plotter, examples
from matplotlib import pyplot
import numpy as np

file_path = examples.ipm_motor_path()
plt = Plotter(file_path)

data = plt.sample_arcs_from_normal(
    arcs=[
        ((0, 0, 0), (0, 0, 1), (0.080575, 0, 0), 45),
        ((0, 0, 0), (0, 0, 1), (0.0569751, 0.0569751, 0), 5),
    ],
    resolution=100,
)

fig, axes = pyplot.subplots(1, len(data), figsize=(14, 6), subplot_kw={"projection": "3d"})
axes = np.atleast_1d(axes)

for idx, arc_data in enumerate(data):
    time_values = [time_data["time"] for time_data in arc_data]
    distances = arc_data[0]["B-Mag (T)"]["distance"]
    value_grid = np.array([time_data["B-Mag (T)"]["value"] for time_data in arc_data])
    time_grid, distance_grid = np.meshgrid(time_values, distances, indexing="ij")

    axes[idx].plot_surface(time_grid, distance_grid, value_grid, cmap="viridis")
    axes[idx].set_xlabel("Time (s)")
    axes[idx].set_ylabel("Distance Along Arc (m)")
    axes[idx].set_zlabel("B-Mag (T)")
    axes[idx].set_title(f"Arc {idx + 1}")

fig.suptitle("B-Mag (T) Along Sampled Arcs")
fig.tight_layout()
fig.savefig("docs/static/demos/sample_arcs_from_normal.png")
```
![Sample Arcs From Normal](/demos/sample_arcs_from_normal.png)

### Plot three time slices

```python
from pyemsi import Plotter, examples
from matplotlib import pyplot
import numpy as np

file_path = examples.ipm_motor_path()
plt = Plotter(file_path)

data = plt.sample_arcs_from_normal(
    arcs=[
        ((0, 0, 0), (0, 0, 1), (0.080575, 0, 0), 45),
        ((0, 0, 0), (0, 0, 1), (0.0569751, 0.0569751, 0), 5),
    ],
    resolution=100,
)

fig, axes = pyplot.subplots(1, len(data), figsize=(14, 5))
axes = np.atleast_1d(axes)

for idx, arc_data in enumerate(data):
    time_indices = sorted({0, len(arc_data) // 2, len(arc_data) - 1})

    for time_idx in time_indices:
        axes[idx].plot(
            arc_data[time_idx]["B-Mag (T)"]["distance"],
            arc_data[time_idx]["B-Mag (T)"]["value"],
            label=f"t = {arc_data[time_idx]['time']:.3f} s",
        )

    axes[idx].set_xlabel("Distance Along Arc (m)")
    axes[idx].set_ylabel("B-Mag (T)")
    axes[idx].set_title(f"Arc {idx + 1}")
    axes[idx].legend()

fig.suptitle("B-Mag (T) Along Sampled Arcs at Three Time Points")
fig.tight_layout()
fig.savefig("docs/static/demos/sample_arcs_from_normal_time_slices.png")
```
![Sample Arcs From Normal Time Slices](/demos/sample_arcs_from_normal_time_slices.png)

### Plot tangential and normal B-Vec components

```python
from pyemsi import Plotter, examples
from matplotlib import pyplot
import numpy as np

file_path = examples.ipm_motor_path()
plt = Plotter(file_path)

data = plt.sample_arcs_from_normal(
    arcs=[
        ((0, 0, 0), (0, 0, 1), (0.080575, 0, 0), 45),
        ((0, 0, 0), (0, 0, 1), (0.0569751, 0.0569751, 0), 5),
    ],
    resolution=100,
)

fig, axes = pyplot.subplots(len(data), 2, figsize=(12, 4 * len(data)))
axes = np.array(axes, dtype=object)
if axes.ndim == 1:
    axes = axes[np.newaxis, :]

for idx, arc_data in enumerate(data):
    time_indices = sorted({0, len(arc_data) // 2, len(arc_data) - 1})

    for time_idx in time_indices:
        label = f"t = {arc_data[time_idx]['time']:.3f} s"
        axes[idx, 0].plot(
            arc_data[time_idx]["B-Vec (T)"]["distance"],
            arc_data[time_idx]["B-Vec (T)"]["tangential"],
            label=label,
        )
        axes[idx, 1].plot(
            arc_data[time_idx]["B-Vec (T)"]["distance"],
            arc_data[time_idx]["B-Vec (T)"]["normal"],
            label=label,
        )

    axes[idx, 0].set_xlabel("Distance Along Arc (m)")
    axes[idx, 0].set_ylabel("Tangential B-Vec (T)")
    axes[idx, 0].set_title(f"Arc {idx + 1} Tangential")
    axes[idx, 0].legend()

    axes[idx, 1].set_xlabel("Distance Along Arc (m)")
    axes[idx, 1].set_ylabel("Normal B-Vec (T)")
    axes[idx, 1].set_title(f"Arc {idx + 1} Normal")
    axes[idx, 1].legend()

fig.suptitle("B-Vec (T) Components Along Sampled Arcs at Three Time Points")
fig.tight_layout()
fig.savefig("docs/static/demos/sample_arcs_from_normal_bvec_components_time_slices.png")
```
![Sample Arcs From Normal B-Vec Components Time Slices](/demos/sample_arcs_from_normal_bvec_components_time_slices.png)

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
