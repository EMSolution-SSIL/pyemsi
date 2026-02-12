---
sidebar_position: 16
title: sample_point()
---

# `sample_point()`

Sample mesh data at a single point coordinate.

This method creates a probe at the specified 3D coordinate and samples the mesh data onto it using PyVista's `sample()` filter. For temporal datasets, automatically sweeps all time points unless `time_value` is specified. For static datasets, returns values directly.

:::tip[Parameters]
- **`point`** (`Sequence[float]`) — 3D coordinate `[x, y, z]` to sample at.
- **`time_value`** (`float | None`, default: `None`) — Query a specific time value instead of sweeping all time points. Ignored for static datasets.
- **`tolerance`** (`float | None`, default: `None`) — Tolerance for the sample operation. If `None`, PyVista generates a tolerance automatically.
:::

:::info[Returns]
Returns a dictionary with array names as keys. Both static and temporal datasets use the same structure, with static datasets using `time: [0]`. Each dictionary includes a `"coordinates"` key with the probe position.

```python
# Scalars:
{
    "scalar_name": {
        "time": [0.0, 0.001, 0.002, ...],  # [0] for static
        "value": [val0, val1, val2, ...]
    },
    "coordinates": {
        "x": 1.0,
        "y": 2.0,
        "z": 3.0
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
    "coordinates": {
        "x": 1.0,
        "y": 2.0,
        "z": 3.0
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
data = p.sample_point([1.0, 2.0, 3.0])

# Scalar: time is [0] for static
print(data["Temperature"]["value"][0])  # e.g., 300.5

# Coordinates
print(data["coordinates"]["x"])  # 1.0
```

### Temporal MultiBlock mesh

```python
from pyemsi import Plotter

p = Plotter("output.pvd")
data = p.sample_point([5.0, 10.0, 0.0])

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
# Sample at t=0.05 only
data = p.sample_point([1.0, 2.0, 3.0], time_value=0.05)

print(data["B-Mag (T)"]["time"])   # [0.05]
print(data["B-Mag (T)"]["value"])  # [value at t=0.05]
```

### Sample from specific block

```python
from pyemsi import Plotter

p = Plotter("output.vtm")
# Sample only from the "coil" block
data = p.sample_point([1.0, 2.0, 3.0], block_name="coil")
```

## See Also

- [`sample_points()`](./sample_points.md) — Sample at multiple point coordinates
- [`sample_line()`](./sample_line.md) — Sample along a straight line
- [`query_point()`](./query_point.md) — Query data by point ID (indexed access)
