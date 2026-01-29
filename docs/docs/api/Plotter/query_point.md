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

### Static single-block mesh

```python
from pyemsi import Plotter

p = Plotter("mesh.vtu")
data = p.query_point(42)

# Scalar: time is [0] for static
print(data["Temperature"]["value"][0])  # e.g., 300.5

# Vector: x_value, y_value, z_value
print(data["Velocity"]["x_value"][0])  # e.g., 1.0
```

### Temporal MultiBlock mesh

```python
from pyemsi import Plotter

p = Plotter("output.pvd")
data = p.query_point(100, block_name="coil")

# Scalar: dict with "time" and "value" lists
times = data["B-Mag (T)"]["time"]
values = data["B-Mag (T)"]["value"]

# Vector: dict with "time", "x_value", "y_value", "z_value" lists
times = data["B-Vec (T)"]["time"]
x_vals = data["B-Vec (T)"]["x_value"]
y_vals = data["B-Vec (T)"]["y_value"]
z_vals = data["B-Vec (T)"]["z_value"]
```

### Query specific time value

```python
from pyemsi import Plotter

p = Plotter("output.pvd")
# Query at t=0.005 seconds only
data = p.query_point(100, block_name="coil", time_value=0.005)

# Result has single-element lists
print(data["B-Mag (T)"]["time"])   # [0.005]
print(data["B-Mag (T)"]["value"])  # [1.234]
```

## See Also

- [`query_points`](./query_points.md) — Query multiple points
- [`query_cell`](./query_cell.md) — Query cell data
- [`mesh`](./mesh.md) — Access the underlying mesh
- [PyVista DataSetAttributes](https://docs.pyvista.org/api/core/_autosummary/pyvista.datasetattributes)
