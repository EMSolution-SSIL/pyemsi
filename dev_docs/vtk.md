# Custom Unstructured Mesh → VTK (vtkUnstructuredGrid) with Python

This focused guide turns a **custom volume mesh** (tets/hexes/prisms/pyramids, possibly mixed) into a **`vtkUnstructuredGrid`**, attaches **point**/**cell** data (scalars & 3‑component vectors), and writes a `.vtu` file you can open in ParaView or any VTK‑based tool.


## 0) Prerequisites

```bash
pip install vtk
```

Python imports used below:

```python
import vtk
from vtk import (
    vtkPoints, vtkUnstructuredGrid, vtkIdList,
    vtkFloatArray, vtkDoubleArray,
    vtkXMLUnstructuredGridWriter
)
from vtk.util.numpy_support import numpy_to_vtk
```


## 1) Map your custom elements to VTK cell types

Pick the **VTK enum** per element type. Extend as needed.

```python
VTK_CELL = {
    'tet': 10,       # VTK_TETRA
    'hex': 12,       # VTK_HEXAHEDRON
    'wedge': 13,     # VTK_WEDGE (prism)
    'pyr': 14,       # VTK_PYRAMID
    'tri': 5,        # VTK_TRIANGLE  (allowed in UGrid)
    'quad': 9,       # VTK_QUAD      (allowed in UGrid)
}
```

> ⚠️ **Node ordering matters.** VTK expects a canonical ordering for each cell type (e.g., hex/tet corner order). If your format uses a different order, reorder indices before insertion.


## 2) Parse your custom mesh file

Template parser (adjust to your format). This example expects lines like:

* Nodes: `v id x y z`
* Elements: `e id type pid0 pid1 ...`

```python
def parse_custom_mesh(path):
    points = {}           # id -> (x, y, z)
    cells = []            # list[(vtk_cell_type, [point_ids])]

    with open(path, 'r') as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith('#'):
                continue
            tag, *rest = line.split()
            if tag == 'v':
                vid = int(rest[0]); x, y, z = map(float, rest[1:4])
                points[vid] = (x, y, z)
            elif tag == 'e':
                eid = int(rest[0]); etype = rest[1].lower()
                pid_list = list(map(int, rest[2:]))
                vtk_type = VTK_CELL[etype]
                cells.append((vtk_type, pid_list))
    return points, cells
```


## 3) Build the `vtkUnstructuredGrid`

Create VTK points and insert mixed‑type cells. Ensure VTK point IDs are **0..N-1**; keep a mapping if your file’s IDs are arbitrary.

```python
def build_unstructured_grid(points_dict, cells):
    # 1) Points (0..N-1 mapping)
    pts = vtkPoints()
    id_map = {}
    for new_id, (old_id, xyz) in enumerate(points_dict.items()):
        id_map[old_id] = new_id
        pts.InsertNextPoint(*xyz)

    ug = vtkUnstructuredGrid()
    ug.SetPoints(pts)
    ug.Allocate(len(cells))

    # 2) Cells (mixed types ok)
    for vtk_type, pid_list in cells:
        idlist = vtkIdList()
        for pid in pid_list:
            idlist.InsertNextId(id_map[pid])
        ug.InsertNextCell(vtk_type, idlist)

    return ug
```

> 🔎 For very large meshes, you can also build the connectivity in bulk (types + offsets + connectivity) and call `ug.SetCells(...)`. Start with the simple method above; optimize later if needed.


## 4) Attach point & cell data (scalars and vectors)

VTK arrays live in **`ug.GetPointData()`** or **`ug.GetCellData()`**.

### 4.1 Pure‑Python lists (portable)

```python
def add_point_scalar(ug, name, values, dtype='float'):
    arr = (vtkFloatArray() if dtype == 'float' else vtkDoubleArray())
    arr.SetName(name)
    arr.SetNumberOfComponents(1)
    arr.SetNumberOfTuples(len(values))
    for i, v in enumerate(values):
        arr.SetValue(i, float(v))
    ug.GetPointData().AddArray(arr)
    ug.GetPointData().SetActiveScalars(name)


def add_point_vector3(ug, name, vecs3, dtype='float'):
    arr = (vtkFloatArray() if dtype == 'float' else vtkDoubleArray())
    arr.SetName(name)
    arr.SetNumberOfComponents(3)
    arr.SetNumberOfTuples(len(vecs3))
    for i, (x, y, z) in enumerate(vecs3):
        arr.SetTuple3(i, float(x), float(y), float(z))
    ug.GetPointData().AddArray(arr)
    ug.GetPointData().SetActiveVectors(name)


def add_cell_scalar(ug, name, values, dtype='float'):
    arr = (vtkFloatArray() if dtype == 'float' else vtkDoubleArray())
    arr.SetName(name)
    arr.SetNumberOfComponents(1)
    arr.SetNumberOfTuples(len(values))
    for i, v in enumerate(values):
        arr.SetValue(i, float(v))
    ug.GetCellData().AddArray(arr)


def add_cell_vector3(ug, name, vecs3, dtype='float'):
    arr = (vtkFloatArray() if dtype == 'float' else vtkDoubleArray())
    arr.SetName(name)
    arr.SetNumberOfComponents(3)
    arr.SetNumberOfTuples(len(vecs3))
    for i, (x, y, z) in enumerate(vecs3):
        arr.SetTuple3(i, float(x), float(y), float(z))
    ug.GetCellData().AddArray(arr)
```

### 4.2 NumPy arrays (fast path)

```python
# Point scalars: np.array shape (N,) or (N,1)
def add_point_scalar_np(ug, name, np_values):
    arr = numpy_to_vtk(np_values, deep=True)
    arr.SetName(name)
    # Ensure 1 component
    if arr.GetNumberOfComponents() != 1:
        arr.SetNumberOfComponents(1)
    ug.GetPointData().AddArray(arr)
    ug.GetPointData().SetActiveScalars(name)

# Point vectors: np.array shape (N,3)
def add_point_vector_np(ug, name, np_vecs):
    arr = numpy_to_vtk(np_vecs, deep=True)
    arr.SetName(name)
    arr.SetNumberOfComponents(3)
    ug.GetPointData().AddArray(arr)
    ug.GetPointData().SetActiveVectors(name)

# Cell scalars/vectors mirror the point versions using ug.GetCellData()
```


## 5) Write to disk as `.vtu`

Use the XML writer for unstructured grids.

```python
writer = vtkXMLUnstructuredGridWriter()
writer.SetFileName("mesh.vtu")
writer.SetInputData(ug)
writer.Write()
```


## 6) End‑to‑end example

```python
# Parse your custom file
points_dict, cells = parse_custom_mesh("example.mesh")

# Build UnstructuredGrid
ug = build_unstructured_grid(points_dict, cells)

# Attach example data
num_points = len(points_dict)
num_cells = len(cells)

add_point_scalar(ug, "Temperature", [300.0]*num_points)
add_point_vector3(ug, "Displacement", [(0.0, 0.0, 0.0)]*num_points)
add_cell_scalar(ug, "MaterialId", list(range(num_cells)))
add_cell_vector3(ug, "AvgStress", [(1.0, 0.0, 0.0)]*num_cells)

# Write .vtu
writer = vtkXMLUnstructuredGridWriter()
writer.SetFileName("mesh.vtu")
writer.SetInputData(ug)
writer.Write()
```

Open `mesh.vtu` in ParaView. Color by `Temperature`. Use **Glyph** or **Warp By Vector** to visualize `Displacement`.


## 7) Minimal custom file example

```
# example.mesh
v 1 0.0 0.0 0.0
v 2 1.0 0.0 0.0
v 3 0.0 1.0 0.0
v 4 0.0 0.0 1.0
# one tetra (node ids)
e 1 tet 1 2 3 4
```

## 8) Gotchas specific to `vtkUnstructuredGrid`

* **Canonical node order** per VTK cell type is required for correct rendering/filters.
* **Array lengths** must match `#points` for `PointData` and `#cells` for `CellData`.
* **Mixed element types** are fine—insert each with its correct VTK enum.
* Prefer **XML writers** (`vtkXMLUnstructuredGridWriter`) over legacy `.vtk`.
* Start with `InsertNextCell` for clarity; consider bulk connectivity for very large meshes.
