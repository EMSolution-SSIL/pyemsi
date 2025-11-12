# FEMAP Neutral File to VTM Conversion Plan

## Overview

This document outlines the implementation plan for reading a FEMAP Neutral file (`post_geom`) and converting it to a VTK MultiBlock UnstructuredGrid (`.vtm`) file format for visualization in ParaView. The converter creates a MultiBlock dataset where each block is an UnstructuredGrid containing elements organized by property ID.

## Input File Structure

The `post_geom` file contains the following FEMAP Neutral data blocks, but the order of these blocks is not guaranteed:
- **Block 100**: Neutral File Header
- **Block 403**: Nodes (geometry points)
- **Block 404**: Elements (connectivity and topology)
- **Block 402**: Properties
- **Block 601**: Materials

Each block follows the structure:
```
   -1
   <block_id>
   <data_lines>
   -1
```

**IMPORTANT**: Blocks can appear in **any order** and can be repeated. The parser must identify blocks by their ID, not by position in the file.

## Implementation Steps

Details of the FEMAP Neutral file format can be found in the /dev_docs/femap.md file in this repository.
The vtkUnstructuredGrid details are in /dev_docs/vtk.md.

### 1. Parse FEMAP Neutral File Structure

**Goal**: Read the file and separate it into distinct data blocks.

**Details**:
- Each block starts with `   -1` (3 spaces + `-1`)
- Next line contains the block ID (100, 403, 402, 404, or 601)
- Block ends with `   -1`
- Values are comma-separated (but commas are optional; spaces work too)
- **Blocks can appear in any order**
- **Blocks of the same type can be repeated**

**Strategy**:
- Read file sequentially
- When encountering `   -1`, read next line to get block ID
- Collect all lines until next `   -1`
- Store in dictionary with block ID as key (use lists to handle repeated blocks)

**Output**: Dictionary mapping block IDs to lists of data blocks: `{100: [block_data], 403: [block_data], ...}`

---

### 2. Extract Data from Block 100 (Header)

**Goal**: Validate the FEMAP file format.

**Fields**:
- Line 1: Title (usually `<NULL>`)
- Line 2: Version (should be `4.41`)

**Validation**: Check that version matches expected value.

**Note**: Block 100 typically appears once but parser should handle it regardless of position.

---

### 3. Extract Data from Block 403 (Nodes)

**Goal**: Build a dictionary of node IDs to coordinates.

**Fields per node**:
```
ID,0,0,1,46,0,0,0,0,0,0,x,y,z,
```

**Parse**:
- Field 0: Node ID (integer)
- Fields 11, 12, 13: x, y, z coordinates (floats)

**Note**: Block 403 may be repeated to add more nodes. Collect all nodes from all Block 403 instances.

**Output**: `{node_id: (x, y, z), ...}`

---

### 4. Extract Data from Block 402 (Properties)

**Goal**: Build a dictionary of property IDs to property metadata.

**Fields**:
```
Line 1: ID,24,matlID,25,1,0,
Line 2: title,
Line 3-7: (other fields)
```

**Parse**:
- Field 0: Property ID (integer)
- Field 2: Material ID (integer)
- Line 2: Property title (string)

**Note**: Block 402 may be repeated. Collect all properties from all Block 402 instances.

**Output**: `{prop_id: {'material_id': int, 'title': str}, ...}`

---

### 5. Extract Data from Block 404 (Elements)

**Goal**: Build a list of elements with topology and connectivity.

**Fields**:
```
Line 1: ID,124,propID,25,topology,1,0,0,
Line 2: node[0],...,node[9],
Line 3: node[10],...,node[19],
Lines 4-7: (orientation/offset data - ignore)
```

**Parse**:
- Field 0: Element ID (integer)
- Field 2: Property ID (integer)
- Field 4: Topology code (integer)
- Lines 2-3: Node connectivity (up to 20 nodes)

**Topology Mapping** (see section 7):
- Extract only the required nodes based on topology type
- Discard unused node slots (value = 0)

**Note**: Block 404 may be repeated. Collect all elements from all Block 404 instances.

**Output**: `[{'id': int, 'prop_id': int, 'topology': int, 'nodes': [node_ids]}, ...]`

---

### 6. Extract Data from Block 601 (Materials)

**Goal**: Extract material metadata (mostly for reference).

**Note**: Block 601 uses default/placeholder values in most cases. We'll extract material ID but may not need detailed properties. Block 601 may be repeated.

**Output**: `{material_id: {...}, ...}`

---

### 7. Map FEMAP Topology to VTK Cell Types

**Goal**: Convert FEMAP topology codes to VTK cell type enums.

| FEMAP Topology | Element Type | VTK Type | VTK Enum | Node Count |
|----------------|--------------|----------|----------|------------|
| 9  | Point        | VTK_VERTEX | 1 | 1 |
| 0  | Line2        | VTK_LINE | 3 | 2 |
| -  | Line3        | VTK_QUADRATIC_EDGE | 21 | 3 |
| 2  | Tri3         | VTK_TRIANGLE | 5 | 3 |
| 3  | Tri6         | VTK_QUADRATIC_TRIANGLE | 22 | 6 |
| 4  | Quad4        | VTK_QUAD | 9 | 4 |
| 5  | Quad8        | VTK_QUADRATIC_QUAD | 23 | 8 |
| 6  | Tetra4       | VTK_TETRA | 10 | 4 |
| 10 | Tetra10      | VTK_QUADRATIC_TETRA | 24 | 10 |
| 7  | Wedge6       | VTK_WEDGE | 13 | 6 |
| 11 | Wedge15      | VTK_QUADRATIC_WEDGE | 26 | 15 |
| 8  | Brick8       | VTK_HEXAHEDRON | 12 | 8 |
| 12 | Brick20      | VTK_QUADRATIC_HEXAHEDRON | 25 | 20 |

**Node Reference Extraction** (from FEMAP doc):
- Point: node[0]
- Line2: node[0:2]
- Tri3: node[0:3]
- Tri6: node[0:6]
- Quad4: node[0:4]
- Quad8: node[0:8]
- Tetra4: node[0:4]
- Tetra10: node[0:10]
- Wedge6: node[0:6]
- Wedge15: node[0:15]
- Brick8: node[0:8]
- Brick20: node[0:20]

**Implementation**: Create a mapping dictionary:
```python
FEMAP_TO_VTK = {
    9: (1, 1),   # (vtk_type, num_nodes)
    0: (3, 2),
    2: (5, 3),
    3: (22, 6),
    4: (9, 4),
    5: (23, 8),
    6: (10, 4),
    10: (24, 10),
    7: (13, 6),
    11: (26, 15),
    8: (12, 8),
    12: (25, 20),
}
```

---

### 8. Build vtkMultiBlockDataSet by Property ID

**Goal**: Create a VTK MultiBlock UnstructuredGrid with separate UnstructuredGrid blocks for each property ID.

**Steps**:

1. **Group elements by property ID**:
   ```python
   elements_by_prop = {}
   for elem in elements:
       prop_id = elem['prop_id']
       if prop_id not in elements_by_prop:
           elements_by_prop[prop_id] = []
       elements_by_prop[prop_id].append(elem)
   ```

2. **Create shared vtkPoints** (used by all blocks):
   - Iterate through nodes dictionary
   - Map FEMAP node IDs to VTK 0-based indices
   - Insert point coordinates: `pts.InsertNextPoint(x, y, z)`

3. **Create ID mapping**:
   ```python
   femap_to_vtk_id = {femap_id: vtk_idx for vtk_idx, femap_id in enumerate(sorted(nodes.keys()))}
   ```

4. **Initialize vtkMultiBlockDataSet**:
   ```python
   mb = vtkMultiBlockDataSet()
   mb.SetNumberOfBlocks(len(elements_by_prop))
   ```

5. **Create a block for each property**:
   - For each property ID:
     - Create new vtkUnstructuredGrid
     - Set shared points
     - Insert cells for elements with this property
     - Add cell data arrays (ElementID, PropertyID, MaterialID, TopologyID)
     - Set block in multiblock dataset
     - Name the block as `Property_{ID}_{Title}`

**Code skeleton**:
```python
for block_idx, prop_id in enumerate(sorted(elements_by_prop.keys())):
    elements = elements_by_prop[prop_id]

    ug = vtkUnstructuredGrid()
    ug.SetPoints(pts)
    ug.Allocate(len(elements))

    for elem in elements:
        vtk_type, num_nodes = FEMAP_TO_VTK[elem['topology']]
        idlist = vtkIdList()
        for femap_node_id in elem['nodes'][:num_nodes]:
            vtk_idx = femap_to_vtk_id[femap_node_id]
            idlist.InsertNextId(vtk_idx)
        ug.InsertNextCell(vtk_type, idlist)

    # Add cell data arrays
    add_cell_data(ug, elements)

    # Add to multiblock
    mb.SetBlock(block_idx, ug)
    mb.GetMetaData(block_idx).Set(mb.NAME(), f"Property_{prop_id}")
```

---

### 9. Attach Property and Material IDs as Cell Data

**Goal**: Add metadata to cells in each block for visualization and filtering.

**Cell Data Arrays** (per block):
1. **Element ID**: Original FEMAP element ID
2. **Property ID**: Property assignment for each element
3. **Material ID**: Material assignment (via property lookup)
4. **Topology ID**: FEMAP topology code for debugging

**Implementation**: Each block contains its own cell data arrays populated during block creation.

---

### 10. Write vtkMultiBlockDataSet to .vtm File

**Goal**: Export the multiblock dataset to VTK XML format.

**Implementation**:
```python
from vtk import vtkXMLMultiBlockDataWriter

writer = vtkXMLMultiBlockDataWriter()
writer.SetFileName("output.vtm")
writer.SetInputData(mb)
writer.Write()
```

---

## Expected Output

**File**: `output.vtm`

**Contents**:
- VTK MultiBlock UnstructuredGrid with one UnstructuredGrid block per property ID
- Each UnstructuredGrid block contains:
  - Geometry: Nodes and elements for that property
  - Cell Data:
    - `ElementID`: FEMAP element IDs
    - `PropertyID`: Property assignments
    - `MaterialID`: Material assignments
    - `TopologyID`: FEMAP topology codes
- Block names: `Property_{ID}_{Title}`

**Visualization**: Open in ParaView to see separate UnstructuredGrid blocks for each property. Toggle visibility of individual blocks or color by PropertyID/MaterialID.

---

## Notes and Gotchas

1. **Block order is undefined**: Blocks can appear in any order in the file. The parser must identify blocks by their ID number, not by their position.

2. **Repeated blocks**: Blocks of the same type (e.g., multiple Block 403) can appear multiple times. All instances must be parsed and combined.

3. **Node ordering**: VTK expects canonical node ordering for each cell type. Verify FEMAP uses the same ordering, or reorder if necessary.

4. **Zero-based vs 1-based indexing**: FEMAP uses 1-based node IDs; VTK uses 0-based. Must create explicit mapping.

5. **Unused node slots**: Elements like Quad4 only use 4 nodes but FEMAP stores 20 node slots. Extract only the required nodes based on topology.

6. **Comma parsing**: FEMAP allows both comma-separated and space-separated values. Parser must handle both.

7. **Special strings**: `<NULL>` represents empty strings in FEMAP format.

8. **Mixed element types**: vtkUnstructuredGrid supports mixed topologies in a single grid—this is expected and correct. Each UnstructuredGrid block can contain mixed element types.

9. **Shared points**: All UnstructuredGrid blocks in the MultiBlock dataset share the same point set, ensuring consistency and reducing memory usage.

10. **MultiBlock structure**: The output is a vtkMultiBlockDataSet where each block is a vtkUnstructuredGrid, not a simple collection of grids.

---

## Future Enhancements

- [ ] Support for output sets (Block 450) and result vectors (Block 1051)
- [ ] Attach nodal/elemental results as point/cell data
- [ ] Handle special element types (Rigid, Contact, Weld)
- [ ] Validate node ordering against VTK canonical ordering
- [ ] Support for multiple material blocks
