# `Fem.FemMesh`

[Module](index.md)

```python
class FemMesh(ComplexGeoData):
```

FemMesh class

Author: Juergen Riegel (Juergen.Riegel@web.de)
License: LGPL-2.1-or-later

Evidence: public stub `Fem/__init__.pyi` line 87. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Fem.FemMesh.setShape`

```python
def setShape(self, shape: TopoShape, /) -> None:
```

Set the Part shape to mesh

Evidence: public stub `Fem/__init__.pyi` line(s) 95.

## `Fem.FemMesh.compute`

```python
def compute(self) -> None:
```

Update the internal mesh structure

Evidence: public stub `Fem/__init__.pyi` line(s) 99.

## `Fem.FemMesh.addHypothesis`

```python
def addHypothesis(self, hypothesis: object, shape: TopoShape=..., /) -> None:
```

Add hypothesis

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Fem/__init__.pyi` line(s) 103.

## `Fem.FemMesh.setStandardHypotheses`

```python
def setStandardHypotheses(self) -> None:
```

Set some standard hypotheses for the whole shape

Evidence: public stub `Fem/__init__.pyi` line(s) 107.

## `Fem.FemMesh.addNode`

```python
def addNode(self, x: float, y: float, z: float, elem_id: int | None=None, /) -> int:
```

Add a node by setting (x,y,z).

Evidence: public stub `Fem/__init__.pyi` line(s) 111.

## `Fem.FemMesh.addEdge`

```python
@overload
def addEdge(self, n1: int, n2: int, /) -> int:

@overload
def addEdge(self, nodes: list[int], elem_id: int | None=None, /) -> int:

def addEdge(self, *args) -> int:
```

Add an edge by setting two node indices.

Evidence: public stub `Fem/__init__.pyi` line(s) 116, 120, 123.

## `Fem.FemMesh.addEdgeList`

```python
def addEdgeList(self, nodes: list[int], np: list[int], /) -> list[int]:
```

Add list of edges by list of node indices and list of nodes per edge.

Evidence: public stub `Fem/__init__.pyi` line(s) 127.

## `Fem.FemMesh.addFace`

```python
@overload
def addFace(self, n1: int, n2: int, n3: int, /) -> int:

@overload
def addFace(self, nodes: list[int], elem_id: int | None=None, /) -> int:

def addFace(self) -> Any:
```

Add a face by setting three node indices.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Fem/__init__.pyi` line(s) 132, 136, 139.

## `Fem.FemMesh.addFaceList`

```python
def addFaceList(self, nodes: list[int], np: list[int], /) -> list[int]:
```

Add list of faces by list of node indices and list of nodes per face.

Evidence: public stub `Fem/__init__.pyi` line(s) 143.

## `Fem.FemMesh.addQuad`

```python
def addQuad(self, n1: int, n2: int, n3: int, n4: int, /) -> int:
```

Add a quad by setting four node indices.

Evidence: public stub `Fem/__init__.pyi` line(s) 147.

## `Fem.FemMesh.addVolume`

```python
@overload
def addVolume(self, n1: int, n2: int, n3: int, n4: int, /) -> int:

@overload
def addVolume(self, nodes: list[int], elem_id: int | None=None, /) -> int:

def addVolume(self, *args) -> int:
```

Add a volume by setting an arbitrary number of node indices.

Evidence: public stub `Fem/__init__.pyi` line(s) 152, 156, 159.

## `Fem.FemMesh.addVolumeList`

```python
def addVolumeList(self, nodes: list[int], np: list[int], /) -> list[int]:
```

Add list of volumes by list of node indices and list of nodes per volume.

Evidence: public stub `Fem/__init__.pyi` line(s) 163.

## `Fem.FemMesh.read`

```python
def read(self, file_name: str, vtk_cell_group_array: str=...) -> None:
```

Read in a various FEM mesh file formats.

Supported formats: DAT, INP, MED, STL, UNV, VTK, Z88

vtk_cell_group_array: If provided uses the given cell group array to create mesh groups.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Fem/__init__.pyi` line(s) 167.

## `Fem.FemMesh.write`

```python
def write(self, file_name: str, highest: bool=..., vtk_cell_group_array: str=..., vtk_group_id_map: dict=...) -> None:
```

Write out various FEM mesh file formats.

Supported formats: BDF, DAT, INP, MED, STL, UNV, VTK, Z88

highest: Export highest mesh elements only when true (default), all mesh elements if false

vtk_cell_group_array: When writing a VTK file the cell groups will be stored in a array with this name.
                      By default it is a string array with the group name written for each group element.
vtk_group_id_map:     When writing VTK with groups, the groupname can be mapped to a integer ID under
                      which it will be stored (lessmemory usage then string). When reloading the group
                      name is equal to the int ID as string.

Note on VTK group saving: The following limitations apply
    1. Only element/cell groups are supported, no node groups and no mixed groups
    2. Elements can only be in a single group, groups can not overlap
    3. Element IDs in the mesh need to be continuous and start with ID 1

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Fem/__init__.pyi` line(s) 177.

## `Fem.FemMesh.writeABAQUS`

```python
def writeABAQUS(self, fileName: str, elemParam: int, groupParam: bool, volVariant: str='standard', faceVariant: str='shell', edgeVariant: str='beam') -> None:
```

Write out as ABAQUS inp.

elemParam:
    0: All elements
    1: Highest elements only
    2: FEM elements only (only edges not belonging to faces and faces not belonging to volumes)

groupParam:
    True: Write group data
    False: Do not write group data

volVariant: Volume elements
    "standard": Tetra4 -> C3D4, Penta6 -> C3D6, Hexa8 -> C3D8, Tetra10 -> C3D10, Penta15 -> C3D15, Hexa20 -> C3D20
    "reduced": Hexa8 -> C3D8R, Hexa20 -> C3D20R
    "incompatible": Hexa8 -> C3D8I
    "modified": Tetra10 -> C3D10T
    "fluid": Tetra4 -> F3D4, Penta6 -> F3D6, Hexa8  -> F3D8

faceVariant: Face elements
    "shell": Tria3 -> S3, Quad4 -> S4, Tria6 -> S6, Quad8 -> S8
    "shell reduced": Tria3 -> S3, Quad4 -> S4R, Tria6 -> S6, Quad8 -> S8R
    "membrane": Tria3 -> M3D3, Quad4 -> M3D4, Tria6 -> M3D6, Quad8 -> M3D8
    "membrane reduced": Tria3 -> M3D3, Quad4 -> M3D4R, Tria6 -> M3D6, Quad8 -> M3D8R
    "stress": Tria3 -> CPS3, Quad4 -> CPS4, Tria6 -> CPS6, Quad8 -> CPS8
    "stress reduced": Tria3 -> CPS3, Quad4 -> CPS4R, Tria6 -> CPS6, Quad8 -> CPS8R
    "strain": Tria3 -> CPE3, Quad4 -> CPE4, Tria6 -> CPE6, Quad8 -> CPE8
    "strain reduced": Tria3 -> CPE3, Quad4 -> CPE4R, Tria6 -> CPE6, Quad8 -> CPE8R
    "axisymmetric": Tria3 -> CAX3, Quad4 -> CAX4, Tria6 -> CAX6, Quad8 -> CAX8
    "axisymmetric reduced": Tria3 -> CAX3, Quad4 -> CAX4R, Tria6 -> CAX6, Quad8 -> CAX8R

edgeVariant: Edge elements
    "beam": Seg2 -> B31, Seg3 -> B32
    "beam reduced": Seg2 -> B31R, Seg3 -> B32R
    "truss": Seg2 -> T3D2, eg3 -> T3D3
    "network": Seg3 -> D

Elements are selected according to CalculiX availability.
For example if volume variant "modified" is selected, Tetra10 mesh
elements are assigned to C3D10T and remain elements uses "standard".
Axisymmetric, plane strain and plane stress elements expect nodes in the plane z=0.

Evidence: public stub `Fem/__init__.pyi` line(s) 198.

## `Fem.FemMesh.setTransform`

```python
def setTransform(self, placement: Placement, /) -> None:
```

Use a Placement object to perform a translation or rotation

Evidence: public stub `Fem/__init__.pyi` line(s) 243.

## `Fem.FemMesh.copy`

```python
def copy(self) -> FemMesh:
```

Make a copy of this FEM mesh.

Evidence: public stub `Fem/__init__.pyi` line(s) 247.

## `Fem.FemMesh.getFacesByFace`

```python
def getFacesByFace(self, face: TopoShapeFace, /) -> list[int]:
```

Return a list of face IDs which belong to a TopoFace

Evidence: public stub `Fem/__init__.pyi` line(s) 251.

## `Fem.FemMesh.getEdgesByEdge`

```python
def getEdgesByEdge(self, edge: TopoShapeEdge, /) -> list[int]:
```

Return a list of edge IDs which belong to a TopoEdge

Evidence: public stub `Fem/__init__.pyi` line(s) 255.

## `Fem.FemMesh.getVolumesByFace`

```python
def getVolumesByFace(self, face: TopoShapeFace, /) -> list[tuple[int, int]]:
```

Return a list of tuples of volume IDs and face IDs which belong to a TopoFace

Evidence: public stub `Fem/__init__.pyi` line(s) 259.

## `Fem.FemMesh.getccxVolumesByFace`

```python
def getccxVolumesByFace(self, face: TopoShapeFace, /) -> list[tuple[int, int]]:
```

Return a list of tuples of volume IDs and ccx face numbers which belong to a TopoFace

Evidence: public stub `Fem/__init__.pyi` line(s) 263.

## `Fem.FemMesh.getNodeById`

```python
def getNodeById(self, node_id: int, /) -> Vector:
```

Get the node position vector by a Node-ID

Evidence: public stub `Fem/__init__.pyi` line(s) 267.

## `Fem.FemMesh.getNodesBySolid`

```python
def getNodesBySolid(self, shape: TopoShapeSolid, /) -> list[int]:
```

Return a list of node IDs which belong to a TopoSolid

Evidence: public stub `Fem/__init__.pyi` line(s) 271.

## `Fem.FemMesh.getNodesByFace`

```python
def getNodesByFace(self, face: TopoShapeFace, /) -> list[int]:
```

Return a list of node IDs which belong to a TopoFace

Evidence: public stub `Fem/__init__.pyi` line(s) 275.

## `Fem.FemMesh.getNodesByEdge`

```python
def getNodesByEdge(self, edge: TopoShapeEdge, /) -> list[int]:
```

Return a list of node IDs which belong to a TopoEdge

Evidence: public stub `Fem/__init__.pyi` line(s) 279.

## `Fem.FemMesh.getNodesByVertex`

```python
def getNodesByVertex(self, vertex: TopoShapeVertex, /) -> list[int]:
```

Return a list of node IDs which belong to a TopoVertex

Evidence: public stub `Fem/__init__.pyi` line(s) 283.

## `Fem.FemMesh.getElementNodes`

```python
def getElementNodes(self, elem_id: int, /) -> tuple[int, ...]:
```

Return a tuple of node IDs to a given element ID

Evidence: public stub `Fem/__init__.pyi` line(s) 287.

## `Fem.FemMesh.getNodeElements`

```python
def getNodeElements(self, elem_id: int, elem_type: str='All', /) -> tuple[int, ...]:
```

Return a tuple of specific element IDs associated to a given node ID

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Fem/__init__.pyi` line(s) 291.

## `Fem.FemMesh.getGroupName`

```python
def getGroupName(self, elem_id: int, /) -> str:
```

Return a string of group name to a given group ID

Evidence: public stub `Fem/__init__.pyi` line(s) 295.

## `Fem.FemMesh.getGroupElementType`

```python
def getGroupElementType(self, elem_id: int, /) -> str:
```

Return a string of group element type to a given group ID

Evidence: public stub `Fem/__init__.pyi` line(s) 299.

## `Fem.FemMesh.getGroupElements`

```python
def getGroupElements(self, elem_id: int, /) -> tuple[int, ...]:
```

Return a tuple of ElementIDs to a given group ID

Evidence: public stub `Fem/__init__.pyi` line(s) 303.

## `Fem.FemMesh.addGroup`

```python
def addGroup(self, name: str, group_type: str, group_id: int=-1, /) -> int:
```

Add a group to mesh with specific name and type

name: string
group_type: "All", "Node", "Edge", "Face", "Volume", "0DElement", "Ball"
group_id: int
    Optional group_id is used to force specific id for group, but does
    not work, yet.

Evidence: public stub `Fem/__init__.pyi` line(s) 307.

## `Fem.FemMesh.addGroupElements`

```python
def addGroupElements(self, group_id: int, elements: list[int], /) -> None:
```

Add a tuple of ElementIDs to a given group ID

group_id: int
elements: list of int
    Notice that the elements have to be in the mesh.

Evidence: public stub `Fem/__init__.pyi` line(s) 319.

## `Fem.FemMesh.removeGroup`

```python
def removeGroup(self, group_id: int, /) -> bool:
```

Remove a group with a given group ID
                    removeGroup(groupid)
                    groupid: int
                    Returns boolean.

Evidence: public stub `Fem/__init__.pyi` line(s) 329.

## `Fem.FemMesh.renameGroup`

```python
def renameGroup(self, group_id: int, name: str, /) -> None:
```

Rename a group with a given group ID
renameGroup(id, name)
groupid: int
name: string

Evidence: public stub `Fem/__init__.pyi` line(s) 337.

## `Fem.FemMesh.getElementType`

```python
def getElementType(self, elem_id: int, /) -> str:
```

Return the element type of a given ID

Evidence: public stub `Fem/__init__.pyi` line(s) 344.

## `Fem.FemMesh.getIdByElementType`

```python
def getIdByElementType(self, elem_type: str, /) -> tuple[int, ...]:
```

Return a tuple of IDs to a given element type

Evidence: public stub `Fem/__init__.pyi` line(s) 348.

## `Fem.FemMesh.Nodes`

```python
Nodes: Final[dict]
```

Dictionary of Nodes by ID (int ID:Vector())

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Fem/__init__.pyi` line(s) 351.

## `Fem.FemMesh.NodeCount`

```python
NodeCount: Final[int]
```

Number of nodes in the Mesh.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Fem/__init__.pyi` line(s) 353.

## `Fem.FemMesh.Edges`

```python
Edges: Final[tuple]
```

Tuple of edge IDs

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Fem/__init__.pyi` line(s) 355.

## `Fem.FemMesh.EdgesOnly`

```python
EdgesOnly: Final[tuple]
```

Tuple of edge IDs which does not belong to any face (and thus not belong to any volume too)

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Fem/__init__.pyi` line(s) 357.

## `Fem.FemMesh.EdgeCount`

```python
EdgeCount: Final[int]
```

Number of edges in the Mesh.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Fem/__init__.pyi` line(s) 359.

## `Fem.FemMesh.Faces`

```python
Faces: Final[tuple]
```

Tuple of face IDs

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Fem/__init__.pyi` line(s) 361.

## `Fem.FemMesh.FacesOnly`

```python
FacesOnly: Final[tuple]
```

Tuple of face IDs which does not belong to any volume

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Fem/__init__.pyi` line(s) 363.

## `Fem.FemMesh.FaceCount`

```python
FaceCount: Final[int]
```

Number of Faces in the Mesh.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Fem/__init__.pyi` line(s) 365.

## `Fem.FemMesh.TriangleCount`

```python
TriangleCount: Final[int]
```

Number of Triangles in the Mesh.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Fem/__init__.pyi` line(s) 367.

## `Fem.FemMesh.QuadrangleCount`

```python
QuadrangleCount: Final[int]
```

Number of Quadrangles in the Mesh.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Fem/__init__.pyi` line(s) 369.

## `Fem.FemMesh.PolygonCount`

```python
PolygonCount: Final[int]
```

Number of Quadrangles in the Mesh.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Fem/__init__.pyi` line(s) 371.

## `Fem.FemMesh.Volumes`

```python
Volumes: Final[tuple]
```

Tuple of volume IDs

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Fem/__init__.pyi` line(s) 373.

## `Fem.FemMesh.VolumeCount`

```python
VolumeCount: Final[int]
```

Number of Volumes in the Mesh.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Fem/__init__.pyi` line(s) 375.

## `Fem.FemMesh.TetraCount`

```python
TetraCount: Final[int]
```

Number of Tetras in the Mesh.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Fem/__init__.pyi` line(s) 377.

## `Fem.FemMesh.HexaCount`

```python
HexaCount: Final[int]
```

Number of Hexas in the Mesh.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Fem/__init__.pyi` line(s) 379.

## `Fem.FemMesh.PyramidCount`

```python
PyramidCount: Final[int]
```

Number of Pyramids in the Mesh.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Fem/__init__.pyi` line(s) 381.

## `Fem.FemMesh.PrismCount`

```python
PrismCount: Final[int]
```

Number of Prisms in the Mesh.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Fem/__init__.pyi` line(s) 383.

## `Fem.FemMesh.PolyhedronCount`

```python
PolyhedronCount: Final[int]
```

Number of Polyhedrons in the Mesh.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Fem/__init__.pyi` line(s) 385.

## `Fem.FemMesh.SubMeshCount`

```python
SubMeshCount: Final[int]
```

Number of SubMeshs in the Mesh.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Fem/__init__.pyi` line(s) 387.

## `Fem.FemMesh.GroupCount`

```python
GroupCount: Final[int]
```

Number of Groups in the Mesh.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Fem/__init__.pyi` line(s) 389.

## `Fem.FemMesh.Groups`

```python
Groups: Final[tuple]
```

Tuple of Group IDs.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Fem/__init__.pyi` line(s) 391.

## `Fem.FemMesh.Volume`

```python
Volume: Final[Any]
```

Volume of the mesh.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Fem/__init__.pyi` line(s) 393.

