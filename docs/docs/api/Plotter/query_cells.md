---
sidebar_position: 15
title: query_cells()
---

# `query_cells()`

Query cell data for multiple cells.

For temporal datasets, automatically sweeps all time points unless `time_value` is specified. For static datasets, returns values directly.

:::tip[Parameters]
- **`cell_ids`** (`list[int]`) — The cell IDs to query.
- **`block_names`** (`list[str] | str | None`, default: `None`) — Block names for MultiBlock meshes. If `str`, applies to all cells. If `list`, must match length of `cell_ids`. Must be `None` for single-block meshes.
- **`time_value`** (`float | None`, default: `None`) — Query a specific time value instead of sweeping all time points. Ignored for static datasets.
:::

:::info[Returns]
Returns a list of dictionaries, one per cell ID. Each dictionary has the same structure as [`query_cell`](./query_cell.md).

```python
[
    {  # cell_ids[0]
        "scalar_name": {"time": [...], "value": [...]},
        "vector_name": {"time": [...], "x_value": [...], "y_value": [...], "z_value": [...]},
        ...
    },
    {  # cell_ids[1]
        ...
    },
    ...
]
```
:::

## Examples

### Query multiple cells from same block

```python
from pyemsi import Plotter

p = Plotter("output.pvd")
results = p.query_cells([10, 20, 30], block_names="coil")

for i, data in enumerate(results):
    print(f"Cell {[10, 20, 30][i]}: {data['Loss (W/m^3)']['value']}")
```

### Query cells from different blocks

```python
from pyemsi import Plotter

p = Plotter("output.pvd")
results = p.query_cells(
    cell_ids=[10, 20, 30],
    block_names=["coil", "core", "air"]
)

for data in results:
    print(data.keys())
```

### Query specific time value

```python
from pyemsi import Plotter

p = Plotter("output.pvd")
results = p.query_cells([100, 200], block_names="coil", time_value=0.005)

# Each result has single-element time/value lists
for data in results:
    print(data["Loss (W/m^3)"]["time"])   # [0.005]
    print(data["Loss (W/m^3)"]["value"])  # [...]
```

## See Also

- [`query_cell`](./query_cell.md) — Query a single cell
- [`query_points`](./query_points.md) — Query multiple points
- [`mesh`](./mesh.md) — Access the underlying mesh
- [PyVista DataSetAttributes](https://docs.pyvista.org/api/core/_autosummary/pyvista.datasetattributes)
