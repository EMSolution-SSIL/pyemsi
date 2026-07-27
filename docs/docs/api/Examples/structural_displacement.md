---
sidebar_position: 3
title: Structural Displacement
---

### Structural Displacement Dataset

A static structural analysis result for a motor rotor cross-section, stored as a single legacy
VTK unstructured grid. It carries a nodal displacement vector field and a von Mises stress
field, making it the reference dataset for [`set_deformation()`](../Plotter/set_deformation.md).

| Property | Value |
|----------|-------|
| Format | `.vtk` (legacy VTK, `UNSTRUCTURED_GRID`) |
| Points | 431 |
| Cells | 756 |
| Time Steps | none (static result) |

## Functions

### `structural_displacement_path()`

Returns the absolute file path to the bundled structural displacement dataset.

```python
def structural_displacement_path() -> str
```

:::info[Returns]
- **`str`** - Absolute path to `structural_displacement.vtk` bundled with the package.
:::

## Data Arrays

| Array | Association | `mode` | Description |
|-------|-------------|--------|-------------|
| `displacement` | point | — | Three-component nodal displacement vector |
| `displacement_magnitude` | point | `"node"` | Magnitude of the displacement vector |
| `node_id` | point | `"node"` | Original node identifier |
| `von_mises` | cell | `"element"` | Von Mises stress |
| `element_id` | cell | `"element"` | Original element identifier |
| `property_id` | cell | `"element"` | Material/property group identifier |
| `element_kind` | cell | `"element"` | Element classification |
| `vtk_cell_type` | cell | `"element"` | VTK cell type code |

Since this is a single dataset rather than a multiblock collection, block-oriented methods such
as [`set_block_visibility()`](../Plotter/set_block_visibility.md) do not apply.

## Usage Examples

### Basic Usage

```python
from pyemsi import examples

# Get the path to the structural displacement dataset
file_path = examples.structural_displacement_path()
print(file_path)
# Output: /path/to/site-packages/pyemsi/examples/structural_displacement.vtk
```

### With Plotter

```python
from pyemsi import Plotter, examples

file_path = examples.structural_displacement_path()

plt1 = Plotter(file_path)
plt1.set_feature_edges(color="red", line_width=2)
plt1.set_scalar("von_mises", mode="element")
plt1.set_deformation("displacement", scale=5e4)
plt1.show()
```

<iframe
  src="/pyemsi/demos/set_deformation.html"
  style={{aspectRatio: "1.5"}}
/>

The displacements are small in absolute terms, so a large `scale` (here `5e4`) is needed to make
the deformed shape visible. The source file is never modified — the scale factor only affects
the rendered geometry.

### Coloring by Displacement Magnitude

```python
from pyemsi import Plotter, examples

plt1 = Plotter(examples.structural_displacement_path())
plt1.set_scalar("displacement_magnitude")  # point data -> default mode="node"
plt1.set_deformation("displacement", scale=5e4)
plt1.show()
```

:::tip
The example datasets are installed alongside the package, so they are always available
regardless of your working directory.
:::
