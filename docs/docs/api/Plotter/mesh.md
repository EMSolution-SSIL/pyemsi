---
title: mesh
sidebar_position: 13
---

Lazily loaded mesh from the current [`reader`](/docs/api/Plotter/reader.md) as a native PyVista object.

In practice, `Plotter.mesh` is often a [`pyvista.MultiBlock`](https://docs.pyvista.org/api/core/_autosummary/pyvista.multiblock), especially for `*.vtm` and time-dependent `*.pvd` output. That means you usually start by inspecting the block structure, then drill down into the individual datasets inside each block.


:::info[Returns]
- [`pyvista.DataSet`](https://docs.pyvista.org/api/core/_autosummary/pyvista.dataset) | [`pyvista.MultiBlock`](https://docs.pyvista.org/api/core/_autosummary/pyvista.multiblock) | `None`
    - Accessing `mesh` reads data from the reader and caches it on [`Plotter`](/docs/api/Plotter/index.md).
    - For [`PVDReader`](https://docs.pyvista.org/api/readers/_autosummary/pyvista.pvdreader), `mesh` returns the first block from [`reader.read()`](https://docs.pyvista.org/api/readers/_autosummary/pyvista.basereader.read#pyvista.BaseReader.read).
    - [`show()`](/docs/api/Plotter/show.md) and [`export()`](/docs/api/Plotter/export.md) reset the cached mesh before rebuilding the scene.
:::

:::danger[Raises]
- `ValueError` — if no reader is available (call [`set_file()`](/docs/api/Plotter/set_file.md) first).
:::

The examples below were run with:

```python
from pyemsi import Plotter, examples

file_path = examples.transient_path()
plt = Plotter(file_path)
mesh = plt.mesh
```

For this transient example, `mesh` is a top-level `MultiBlock` with block names `"1"`, `"3"`, and `"4"`.

## Working With `MultiBlock`

The most useful first-step operations on a `MultiBlock` mesh are usually:

- `mesh.n_blocks` or `len(mesh)` to see how many top-level blocks exist.
- `mesh.keys()` to list block names.
- `mesh.get_block_name(i)` to retrieve the name for a given block index.
- `mesh[i]` or `mesh["name"]` to access a child block.
- `mesh.bounds` to get the overall bounding box of the full composite mesh.

Example:

```python
from pyemsi import Plotter, examples

file_path = examples.transient_path()
plt = Plotter(file_path)
mesh = plt.mesh

print(type(mesh).__name__)  # MultiBlock
print(mesh.n_blocks)  # 3
print(list(mesh.keys()))  # ['1', '3', '4']
print(mesh.get_block_name(0))  # 1
print(mesh.bounds)
# BoundsTuple(x_min = 0.0,
#             x_max = 0.25,
#             y_min = 0.0,
#             y_max = 0.25,
#             z_min = 0.0,
#             z_max = 0.25)
```

For the transient example above, the top-level `MultiBlock` already contains leaf datasets, so you can access a block like `mesh["1"]` directly.

Example:

```python
from pyemsi import Plotter, examples

file_path = examples.transient_path()
plt = Plotter(file_path)
mesh = plt.mesh

block = mesh["1"]
print(type(block).__name__)  # UnstructuredGrid
```

## Inspecting A Leaf Dataset

Once you reach a concrete [`pyvista.DataSet`](https://docs.pyvista.org/api/core/_autosummary/pyvista.dataset) such as an `UnstructuredGrid`, the most useful inspection attributes are:

- `block.array_names` for available scalar/vector arrays.
- `block.point_data.keys()` for point-data arrays.
- `block.cell_data.keys()` for cell-data arrays.
- `block.n_points` and `block.n_cells` for mesh size.
- `block.bounds` and `block.center` for spatial extent.
- `block.length` for the diagonal length of the dataset bounds.

Example:

```python
from pyemsi import Plotter, examples

file_path = examples.transient_path()
plt = Plotter(file_path)
mesh = plt.mesh
block = mesh["1"]

print(block.array_names)
# ['B-Vec (T)', 'B-Mag (T)', 'vtkOriginalPointIds', 'PropertyID', 'B-Vec (T)', 'B-Mag (T)', 'vtkOriginalCellIds']
print(list(block.point_data.keys()))
# ['B-Vec (T)', 'B-Mag (T)', 'vtkOriginalPointIds']
print(list(block.cell_data.keys()))
# ['PropertyID', 'B-Vec (T)', 'B-Mag (T)', 'vtkOriginalCellIds']
print(block.n_points)  # 396
print(block.n_cells)  # 250
print(block.bounds)
# BoundsTuple(x_min = 0.0,
#             x_max = 0.05000000074505806,
#             y_min = 0.0,
#             y_max = 0.05000000074505806,
#             z_min = 0.0,
#             z_max = 0.10000000149011612)
print(block.center)  # (0.02500000037252903, 0.02500000037252903, 0.05000000074505806)
print(block.length)  # 0.12247448896417099
```

These attributes are often the quickest way to answer questions like:

- Which field names are available for [`set_scalar()`](/docs/api/Plotter/set_scalar.md) or [`set_vector()`](/docs/api/Plotter/set_vector.md)?
- Which block contains the geometry I care about?
- How large is a block, and where is it located in space?

## Common Patterns

Get all top-level block names:

```python
from pyemsi import Plotter, examples

file_path = examples.transient_path()
plt = Plotter(file_path)
mesh = plt.mesh

names = [mesh.get_block_name(i) for i in range(mesh.n_blocks)]
print(names)  # ['1', '3', '4']
```

Loop over blocks and print useful summary information:

```python
from pyemsi import Plotter, examples

file_path = examples.transient_path()
plt = Plotter(file_path)
mesh = plt.mesh

for block_name in mesh.keys():
    block = mesh[block_name]
    print(block_name, block.n_points, block.n_cells, block.bounds)
    # 1 396 250 BoundsTuple(x_min = 0.0,
    #             x_max = 0.05000000074505806,
    #             y_min = 0.0,
    #             y_max = 0.05000000074505806,
    #             z_min = 0.0,
    #             z_max = 0.10000000149011612)
    # 3 384 225 BoundsTuple(x_min = 0.0,
    #             x_max = 0.10000000149011612,
    #             y_min = 0.0,
    #             y_max = 0.10000000149011612,
    #             z_min = 0.0,
    #             z_max = 0.05000000074505806)
    # 4 2902 2285 BoundsTuple(x_min = 0.0,
    #             x_max = 0.25,
    #             y_min = 0.0,
    #             y_max = 0.25,
    #             z_min = 0.0,
    #             z_max = 0.25)
```

Find which arrays exist in each block:

```python
from pyemsi import Plotter, examples

file_path = examples.transient_path()
plt = Plotter(file_path)
mesh = plt.mesh

for block_name in mesh.keys():
    block = mesh[block_name]
    print(block_name, block.array_names)
    # 1 ['B-Vec (T)', 'B-Mag (T)', 'vtkOriginalPointIds', 'PropertyID', 'B-Vec (T)', 'B-Mag (T)', 'vtkOriginalCellIds']
    # 3 ['B-Vec (T)', 'B-Mag (T)', 'vtkOriginalPointIds', 'PropertyID', 'B-Vec (T)', 'B-Mag (T)', 'vtkOriginalCellIds']
    # 4 ['B-Vec (T)', 'B-Mag (T)', 'vtkOriginalPointIds', 'PropertyID', 'B-Vec (T)', 'B-Mag (T)', 'vtkOriginalCellIds']
```

## Related Plotter Helpers

If you want the same block names through the `Plotter` API, use [`get_block_names()`](/docs/api/Plotter/get_block_names.md). To hide or show specific blocks in the rendered scene, use [`set_block_visibility()`](/docs/api/Plotter/set_block_visibility.md).

## Example

```python
from pyemsi import Plotter, examples

file_path = examples.transient_path()
plt = Plotter(file_path)
mesh = plt.mesh

if hasattr(mesh, "keys"):
    print(list(mesh.keys()))  # ['1', '3', '4']

block = mesh["1"]

print(block.array_names)
# ['B-Vec (T)', 'B-Mag (T)', 'vtkOriginalPointIds', 'PropertyID', 'B-Vec (T)', 'B-Mag (T)', 'vtkOriginalCellIds']
print(block.n_points)  # 396
print(block.n_cells)  # 250
print(block.bounds)
# BoundsTuple(x_min = 0.0,
#             x_max = 0.05000000074505806,
#             y_min = 0.0,
#             y_max = 0.05000000074505806,
#             z_min = 0.0,
#             z_max = 0.10000000149011612)
```
