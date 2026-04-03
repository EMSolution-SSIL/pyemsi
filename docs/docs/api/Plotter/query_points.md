---
sidebar_position: 14
title: query_points()
---

# `query_points()`

Query point data for multiple points.

For temporal datasets, automatically sweeps all time points unless `time_value` is specified. For static datasets, returns values directly.

:::tip[Parameters]
- **`point_ids`** (`list[int]`) — The point IDs to query.
- **`block_names`** (`list[str] | str | None`, default: `None`) — Block names for MultiBlock meshes. If `str`, applies to all points. If `list`, must match length of `point_ids`. Must be `None` for single-block meshes.
- **`time_value`** (`float | None`, default: `None`) — Query a specific time value instead of sweeping all time points. Ignored for static datasets.
:::

:::info[Returns]
Returns a list of dictionaries, one per point ID. Each dictionary has the same structure as [`query_point`](./query_point.md).

```python
[
    {  # point_ids[0]
        "scalar_name": {"time": [...], "value": [...]},
        "vector_name": {"time": [...], "x_value": [...], "y_value": [...], "z_value": [...]},
        ...
    },
    {  # point_ids[1]
        ...
    },
    ...
]
```
:::

## Examples

### Sweep all time steps

```python
from pyemsi import Plotter, examples
from matplotlib import pyplot

file_path = examples.transient_path()
plt = Plotter(file_path)
data = plt.query_points(point_ids=[0, 108, 360, 159, 239], block_names=["1", "1", "1", "3", "3"])

fig, axes = pyplot.subplots(2, 1, figsize=(8, 10))

# Block 1
axes[0].plot(data[0]["B-Mag (T)"]["time"], data[0]["B-Mag (T)"]["value"], marker="o", label="Point ID 0")
axes[0].plot(data[1]["B-Mag (T)"]["time"], data[1]["B-Mag (T)"]["value"], marker="o", label="Point ID 108")
axes[0].plot(data[2]["B-Mag (T)"]["time"], data[2]["B-Mag (T)"]["value"], marker="o", label="Point ID 360")
axes[0].set_xlabel("Time (s)")
axes[0].set_ylabel("B-Mag (T)")
axes[0].set_title("B-Mag (T) at Points in Block 1")
axes[0].legend()

# Block 3
axes[1].plot(data[3]["B-Mag (T)"]["time"], data[3]["B-Mag (T)"]["value"], marker="o", label="Point ID 159")
axes[1].plot(data[4]["B-Mag (T)"]["time"], data[4]["B-Mag (T)"]["value"], marker="o", label="Point ID 239")
axes[1].set_xlabel("Time (s)")
axes[1].set_ylabel("B-Mag (T)")
axes[1].set_title("B-Mag (T) at Points in Block 3")
axes[1].legend()

fig.tight_layout()
fig.savefig("docs/static/demos/query_points.png")
```
![Query Points](/demos/query_points.png)

### Query a single time value

```python
from pyemsi import Plotter, examples

file_path = examples.transient_path()
plt = Plotter(file_path)

# Use time_point_value() to look up the time value for a given index
t = plt.time_point_value(4)   # 0.05  (5th time step, zero-based)

# Query only at that time value instead of sweeping all time steps
results = plt.query_points(point_ids=[0, 108, 360], block_names="1", time_value=t)

# Each result has single-element time/value lists
print(results[0]["B-Mag (T)"]["time"])   # [0.05]
print(results[0]["B-Mag (T)"]["value"])  # [0.10820599645376205]
print(results[1]["B-Mag (T)"]["value"])  # [0.09952189773321152]
print(results[2]["B-Mag (T)"]["value"])  # [0.01703610084950924]
```

## See Also

- [`query_point`](./query_point.md) — Query a single point
- [`query_cells`](./query_cells.md) — Query multiple cells
- [`mesh`](./mesh.md) — Access the underlying mesh
- [PyVista DataSetAttributes](https://docs.pyvista.org/api/core/_autosummary/pyvista.datasetattributes)
