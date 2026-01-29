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

### Query multiple points from same block

```python
from pyemsi import Plotter

p = Plotter("output.pvd")
results = p.query_points([10, 20, 30], block_names="coil")

for i, data in enumerate(results):
    print(f"Point {[10, 20, 30][i]}: {data['B-Mag (T)']['value']}")
```

### Query points from different blocks

```python
from pyemsi import Plotter

p = Plotter("output.pvd")
results = p.query_points(
    point_ids=[10, 20, 30],
    block_names=["coil", "core", "air"]
)

for data in results:
    print(data.keys())
```

### Query specific time value

```python
from pyemsi import Plotter

p = Plotter("output.pvd")
results = p.query_points([100, 200], block_names="coil", time_value=0.005)

# Each result has single-element time/value lists
for data in results:
    print(data["B-Mag (T)"]["time"])   # [0.005]
    print(data["B-Mag (T)"]["value"])  # [...]
```

## See Also

- [`query_point`](./query_point.md) — Query a single point
- [`query_cells`](./query_cells.md) — Query multiple cells
- [`mesh`](./mesh.md) — Access the underlying mesh
- [PyVista DataSetAttributes](https://docs.pyvista.org/api/core/_autosummary/pyvista.datasetattributes)
