---
sidebar_position: 4
title: Examples
---

# `pyemsi.examples`

The `pyemsi.examples` module provides built-in sample datasets for quick testing, tutorials, and demonstrations. These bundled files allow you to explore `pyemsi` functionality without needing your own data files.

## Available Datasets

### Transient Dataset

A 10-step electromagnetic transient simulation stored as a VTK PVD (ParaView Data) collection. Each time step contains multiblock VTM data with electromagnetic field quantities.

| Property | Value |
|----------|-------|
| Format | `.pvd` (ParaView Data Collection) |
| Time Steps | 10 |
| Time Range | 0.01 s → 0.1 s |
| Step Size | 0.01 s |

## Functions

### `transient_path()`

Returns the absolute file path to the bundled transient dataset.

```python
def transient_path() -> str
```

:::info[Returns]
- **`str`** — Absolute path to `transient.pvd` bundled with the package.
:::

## Usage Examples

### Basic Usage

```python
from pyemsi import examples

# Get the path to the transient dataset
file_path = examples.transient_path()
print(file_path)
# Output: /path/to/site-packages/pyemsi/examples/transient.pvd
```

### With Plotter

```python
from pyemsi import examples, Plotter

# Load the example transient dataset
file_path = examples.transient_path()
plt = Plotter(filepath=file_path)

# Set a scalar field for visualization
plt.set_scalar("B-Mag (T)", "node")

# Show the plot
plt.show()
```

### Exploring Time Steps

```python
from pyemsi import examples, Plotter

file_path = examples.transient_path()
plt = Plotter(filepath=file_path)

# Check available time values
print(plt.time_values)  # [0.01, 0.02, ..., 0.1]

# Set a specific time step
plt.set_active_time_value(0.05)

plt.set_scalar("B-Mag (T)", "node")
plt.show()
```

### Jupyter Notebook Mode

```python
from pyemsi import examples, Plotter

file_path = examples.transient_path()

# Use notebook mode for inline visualization
plt = Plotter(filepath=file_path, notebook=True, backend="html")
plt.set_scalar("B-Mag (T)", "node")
plt.show()
```

## Dataset Structure

The transient dataset is organized as follows:

```
examples/
├── transient.pvd              # PVD collection file
└── transient/
    ├── STEP1 Time 1.00000e-02.vtm
    ├── STEP2 Time 2.00000e-02.vtm
    ├── STEP3 Time 3.00000e-02.vtm
    ├── STEP4 Time 4.00000e-02.vtm
    ├── STEP5 Time 5.00000e-02.vtm
    ├── STEP6 Time 6.00000e-02.vtm
    ├── STEP7 Time 7.00000e-02.vtm
    ├── STEP8 Time 8.00000e-02.vtm
    ├── STEP9 Time 9.00000e-02.vtm
    └── STEP10 Time 1.00000e-01.vtm
```

Each `.vtm` file is a VTK MultiBlock dataset containing mesh geometry and associated field data for that time step.

:::tip
The example datasets are installed alongside the package, so they are always available regardless of your working directory.
:::
