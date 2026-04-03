---
sidebar_position: 2
title: IPM Motor
---

### IPM Motor Dataset

A 10-step interior permanent magnet (IPM) motor transient simulation stored as a VTK PVD (ParaView Data) collection. Each time step contains multiblock VTM data with electromagnetic field quantities.

| Property | Value |
|----------|-------|
| Format | `.pvd` (ParaView Data Collection) |
| Time Steps | 10 |
| Time Range | 0.00000000 s -> 0.00749997 s |
| Step Size | 0.00083333 s |

## Functions

### `ipm_motor_path()`

Returns the absolute file path to the bundled IPM motor dataset.

```python
def ipm_motor_path() -> str
```

:::info[Returns]
- **`str`** - Absolute path to `ipm_motor.pvd` bundled with the package.
:::

## Usage Examples

### Basic Usage

```python
from pyemsi import examples

# Get the path to the IPM motor dataset
file_path = examples.ipm_motor_path()
print(file_path)
# Output: /path/to/site-packages/pyemsi/examples/ipm_motor.pvd
```

### With Plotter

```python
from pyemsi import examples, Plotter

# Load the example IPM motor dataset
file_path = examples.ipm_motor_path()
plt = Plotter(file_path)

# Set a scalar field for visualization
plt.set_scalar("B-Mag (T)").set_contour("Flux (A/m)", n_contours=20)

# Show the plot
plt.show()
```

<iframe
  src="/pyemsi/demos/ipm_motor.html"
  style={{aspectRatio: "1.5"}}
/>

### Exploring Time Steps

```python
from pyemsi import examples, Plotter

file_path = examples.ipm_motor_path()
plt = Plotter(file_path)

# Check available time values
print(plt.time_values)  # [0.0, 0.00083333, ..., 0.00749997]

# Set a specific time step
plt.set_active_time_value(0.00416665)

plt.set_scalar("B-Mag (T)")
plt.show()
```

### Jupyter Notebook Mode

```python
from pyemsi import examples, Plotter

file_path = examples.ipm_motor_path()

# Use notebook mode for inline visualization
plt = Plotter(file_path, notebook=True, backend="html")
plt.set_scalar("B-Mag (T)")
plt.show()
```

## Dataset Structure

The IPM motor dataset is organized as follows:

```
examples/
├── ipm_motor.pvd              # PVD collection file
└── ipm_motor/
  ├── STEP1 Time 0.00000e+00.vtm
  ├── STEP2 Time 8.33330e-04.vtm
  ├── STEP3 Time 1.66666e-03.vtm
  ├── STEP4 Time 2.49999e-03.vtm
  ├── STEP5 Time 3.33332e-03.vtm
  ├── STEP6 Time 4.16665e-03.vtm
  ├── STEP7 Time 4.99998e-03.vtm
  ├── STEP8 Time 5.83331e-03.vtm
  ├── STEP9 Time 6.66664e-03.vtm
  └── STEP10 Time 7.49997e-03.vtm
```

Each `.vtm` file is a VTK MultiBlock dataset that references 15 `.vtu` blocks containing the motor mesh geometry and associated field data for that time step.

:::tip
The example datasets are installed alongside the package, so they are always available regardless of your working directory.
:::