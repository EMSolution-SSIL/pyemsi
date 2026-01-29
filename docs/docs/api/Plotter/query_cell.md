---
sidebar_position: 13
title: query_cell()
---

# `query_cell()`

Query cell data for a single cell.

For temporal datasets, automatically sweeps all time points unless `time_value` is specified. For static datasets, returns values directly.

:::tip[Parameters]
- **`cell_id`** (`int`) — The cell ID to query.
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
data = p.query_cell(42)

# Scalar: time is [0] for static
print(data["PropertyID"]["value"][0])      # e.g., 5
print(data["Loss (W/m^3)"]["value"][0])    # e.g., 1250.0
```

### Temporal MultiBlock mesh

```python
from pyemsi import Plotter

p = Plotter("output.pvd")
data = p.query_cell(100, block_name="coil")

# Scalar: dict with "time" and "value" lists
times = data["Loss (W/m^3)"]["time"]
values = data["Loss (W/m^3)"]["value"]

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
data = p.query_cell(100, block_name="coil", time_value=0.005)

# Result has single-element lists
print(data["Loss (W/m^3)"]["time"])   # [0.005]
print(data["Loss (W/m^3)"]["value"])  # [1250.0]
```

## See Also

- [`query_cells`](./query_cells.md) — Query multiple cells
- [`query_point`](./query_point.md) — Query point data
- [`mesh`](./mesh.md) — Access the underlying mesh
- [PyVista DataSetAttributes](https://docs.pyvista.org/api/core/_autosummary/pyvista.datasetattributes)
