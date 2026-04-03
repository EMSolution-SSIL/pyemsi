---
sidebar_position: 12
title: query_point()
---

# `query_point()`

Query point data for a single point.

For temporal datasets, automatically sweeps all time points unless `time_value` is specified. For static datasets, returns values directly.

:::tip[Parameters]
- **`point_id`** (`int`) — The point ID to query.
- **`block_name`** (`str | None`, default: `None`) — Block name for MultiBlock meshes. Must be `None` for single-block meshes.
- **`time_value`** (`float | None`, default: `None`) — Query a specific time value instead of sweeping all time points. Ignored for static datasets.
:::

:::info[Returns]
Returns a dictionary with array names as keys. Both static and temporal datasets use the same structure, with static datasets using `time: [0]`.

```python
# Scalars:
{
    "scalar_name": {
        "time": [0.0, 0.001, 0.002, ...],  # [0] for static
        "value": [val0, val1, val2, ...]
    },
    ...
}

# Vectors (3-component):
{
    "vector_name": {
        "time": [0.0, 0.001, 0.002, ...],  # [0] for static
        "x_value": [x0, x1, x2, ...],
        "y_value": [y0, y1, y2, ...],
        "z_value": [z0, z1, z2, ...]
    },
    ...
}
```
:::

## Examples

### Sweep all time steps

```python
from pyemsi import Plotter, examples
from matplotlib import pyplot

file_path = examples.transient_path()
plt = Plotter(file_path)
data = plt.query_point(point_id=360, block_name="1")

fig, ax = pyplot.subplots()
ax.plot(data["B-Mag (T)"]["time"], data["B-Mag (T)"]["value"], marker="o")
ax.set_xlabel("Time (s)")
ax.set_ylabel("B-Mag (T)")
ax.set_title("B-Mag (T) at Point ID 360 in Block 1")
fig.tight_layout()
fig.savefig("docs/static/demos/query_point.png")
```
![Query Point](/demos/query_point.png)

### Query a single time value

```python
from pyemsi import Plotter, examples

file_path = examples.transient_path()
plt = Plotter(file_path)

# Use time_point_value() to look up the time value for a given index
t = plt.time_point_value(4)   # 0.05  (5th time step, zero-based)

# Query only at that time value instead of sweeping all time steps
data = plt.query_point(point_id=360, block_name="1", time_value=t)

print(data["B-Mag (T)"]["time"])   # [0.05]
print(data["B-Mag (T)"]["value"])  # [0.01703610084950924]
```

## See Also

- [`query_points`](./query_points.md) — Query multiple points
- [`query_cell`](./query_cell.md) — Query cell data
- [`mesh`](./mesh.md) — Access the underlying mesh
- [PyVista DataSetAttributes](https://docs.pyvista.org/api/core/_autosummary/pyvista.datasetattributes)
