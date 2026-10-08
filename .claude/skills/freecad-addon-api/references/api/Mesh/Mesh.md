# `Mesh.Mesh`

[Module](index.md)

```python
class Mesh(ComplexGeoData):
```

Mesh() -- Create an empty mesh object.

This class allows one to manipulate the mesh object by adding new facets, deleting facets, importing from an STL file,
transforming the mesh and much more.
For a complete overview of what can be done see also the documentation of mesh.
A mesh object cannot be added to an existing document directly. Therefore the document must create an object
with a property class that supports meshes.
Example:
m = Mesh.Mesh()
... # Manipulate the mesh
d = FreeCAD.activeDocument() # Get a reference to the actie document
f = d.addObject("Mesh::Feature", "Mesh") # Create a mesh feature
f.Mesh = m # Assign the mesh object to the internal property
d.recompute()

Author: Juergen Riegel (Juergen.Riegel@web.de)
License: LGPL-2.1-or-later

Evidence: public stub `Mesh/__init__.pyi` line 206. Inherited members are on the named base's reference; aliases keep their imported identity.

[part 1](Mesh.md) | [part 2](Mesh-2.md)

## `Mesh.Mesh.read`

```python
@overload
def read(self, Filename: str) -> None:

@overload
def read(self, Stream: object, Format: str=...) -> None:

def read(self, **kwargs) -> None:
```

Read in a mesh object from file.
mesh.read(Filename='mymesh.stl')
mesh.read(Stream=file,Format='STL')

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Mesh/__init__.pyi` line(s) 228, 232, 235.

## `Mesh.Mesh.write`

```python
@overload
def write(self, Filename: str, Format: str=..., Name: str=..., Material: dict=...) -> None:

@overload
def write(self, Stream: object, Format: str=..., Name: str=..., Material: dict=...) -> None:

def write(self, **kwargs) -> None:
```

Write the mesh object into file.
mesh.write(Filename='mymesh.stl',[Format='STL',Name='Object name',Material=colors])
mesh.write(Stream=file,Format='STL',[Name='Object name',Material=colors])

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Mesh/__init__.pyi` line(s) 242, 246, 249.

## `Mesh.Mesh.writeInventor`

```python
def writeInventor(self, creaseangle: float=0.0, /) -> str:
```

Write the mesh in OpenInventor format to a string.

Evidence: public stub `Mesh/__init__.pyi` line(s) 255.

## `Mesh.Mesh.copy`

```python
def copy(self) -> Any:
```

Create a copy of this mesh

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 259.

## `Mesh.Mesh.offset`

```python
def offset(self, offset: float, /) -> None:
```

Move the point along their normals

Evidence: public stub `Mesh/__init__.pyi` line(s) 263.

## `Mesh.Mesh.offsetSpecial`

```python
def offsetSpecial(self, offset: float, zmin: float, zmax: float, /) -> None:
```

Move the point along their normals

Evidence: public stub `Mesh/__init__.pyi` line(s) 267.

## `Mesh.Mesh.crossSections`

```python
def crossSections(self, planes: list[tuple[_VectorInput, _VectorInput]], min_eps: float=..., poly: bool=..., /) -> list:
```

Get cross-sections of the mesh through several planes

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Mesh/__init__.pyi` line(s) 271.

## `Mesh.Mesh.unite`

```python
def unite(self, mesh: Mesh, /) -> Mesh:
```

Union of this and the given mesh object.

Evidence: public stub `Mesh/__init__.pyi` line(s) 275.

## `Mesh.Mesh.intersect`

```python
def intersect(self, mesh: Mesh, /) -> Mesh:
```

Intersection of this and the given mesh object.

Evidence: public stub `Mesh/__init__.pyi` line(s) 279.

## `Mesh.Mesh.difference`

```python
def difference(self, mesh: Mesh, /) -> Mesh:
```

Difference of this and the given mesh object.

Evidence: public stub `Mesh/__init__.pyi` line(s) 283.

## `Mesh.Mesh.inner`

```python
def inner(self, mesh: Mesh, /) -> Mesh:
```

Get the part inside of the intersection

Evidence: public stub `Mesh/__init__.pyi` line(s) 287.

## `Mesh.Mesh.outer`

```python
def outer(self, mesh: Mesh, /) -> Mesh:
```

Get the part outside the intersection

Evidence: public stub `Mesh/__init__.pyi` line(s) 291.

## `Mesh.Mesh.section`

```python
def section(self, Mesh: Mesh, ConnectLines: bool=True, MinDist: float=0.0001) -> list:
```

Get the section curves of this and the given mesh object.
lines = mesh.section(mesh2, [ConnectLines=True, MinDist=0.0001])

Evidence: public stub `Mesh/__init__.pyi` line(s) 295.

## `Mesh.Mesh.translate`

```python
def translate(self, x: float, y: float, z: float, /) -> None:
```

Apply a translation to the mesh

Evidence: public stub `Mesh/__init__.pyi` line(s) 300.

## `Mesh.Mesh.rotate`

```python
def rotate(self, x: float, y: float, z: float, /) -> None:
```

Apply a rotation to the mesh

Evidence: public stub `Mesh/__init__.pyi` line(s) 304.

## `Mesh.Mesh.transform`

```python
def transform(self, matrix: Matrix, /) -> None:
```

Apply a transformation to the mesh

Evidence: public stub `Mesh/__init__.pyi` line(s) 308.

## `Mesh.Mesh.transformToEigen`

```python
def transformToEigen(self) -> Any:
```

Transform the mesh to its eigenbase

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 312.

## `Mesh.Mesh.getEigenSystem`

```python
def getEigenSystem(self) -> Any:
```

Get Eigen base of the mesh

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 316.

## `Mesh.Mesh.addFacet`

```python
@overload
def addFacet(self, x1: float, y1: float, z1: float, x2: float, y2: float, z2: float, x3: float, y3: float, z3: float, /) -> None:

@overload
def addFacet(self, v1: Vector, v2: Vector, v3: Vector, /) -> None:

@overload
def addFacet(self, facet: Facet, /) -> None:

def addFacet(self, *args) -> None:
```

Add a facet to the mesh

Evidence: public stub `Mesh/__init__.pyi` line(s) 321, 325, 329, 332.

## `Mesh.Mesh.addFacets`

```python
@overload
def addFacets(self, facets: list, /) -> None:

@overload
def addFacets(self, mesh: tuple[list, list], check: bool=True, /) -> None:

def addFacets(self, *args) -> None:
```

Add a list of facets to the mesh

Evidence: public stub `Mesh/__init__.pyi` line(s) 337, 341, 344.

## `Mesh.Mesh.removeFacets`

```python
def removeFacets(self, facets: list[int], /) -> None:
```

Remove a list of facet indices from the mesh

Evidence: public stub `Mesh/__init__.pyi` line(s) 348.

## `Mesh.Mesh.removeNeedles`

```python
def removeNeedles(self, length: float, /) -> None:
```

Remove all edges that are smaller than a given length

Evidence: public stub `Mesh/__init__.pyi` line(s) 352.

## `Mesh.Mesh.removeFullBoundaryFacets`

```python
def removeFullBoundaryFacets(self) -> Any:
```

Remove facets whose all three points are on the boundary

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 356.

## `Mesh.Mesh.getInternalFacets`

```python
def getInternalFacets(self) -> Any:
```

Builds a list of facet indices with triangles that are inside a volume mesh

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 360.

## `Mesh.Mesh.rebuildNeighbourHood`

```python
def rebuildNeighbourHood(self) -> Any:
```

Repairs the neighbourhood which might be broken

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 364.

## `Mesh.Mesh.addMesh`

```python
def addMesh(self, mesh: Mesh, /) -> None:
```

Combine this mesh with another mesh.

Evidence: public stub `Mesh/__init__.pyi` line(s) 368.

## `Mesh.Mesh.setPoint`

```python
def setPoint(self, index: int, point: Vector, /) -> None:
```

setPoint(int, Vector)
Sets the point at index.

Evidence: public stub `Mesh/__init__.pyi` line(s) 372.

## `Mesh.Mesh.movePoint`

```python
@overload
def movePoint(self, index: int, x: float, y: float, z: float, /) -> None:

@overload
def movePoint(self, index: int, vector: Vector, /) -> None:

def movePoint(self, *args) -> None:
```

movePoint(int, Vector)
This method moves the point in the mesh along the
given vector. This affects the geometry of the mesh.
Be aware that moving points may cause self-intersections.

Evidence: public stub `Mesh/__init__.pyi` line(s) 378, 382, 385.

## `Mesh.Mesh.getPointNormals`

```python
def getPointNormals(self) -> Any:
```

getPointNormals()
Get the normals of the points.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 392.

## `Mesh.Mesh.addSegment`

```python
def addSegment(self, indices: list[int], /) -> None:
```

Add a list of facet indices that describes a segment to the mesh

Evidence: public stub `Mesh/__init__.pyi` line(s) 397.

## `Mesh.Mesh.countSegments`

```python
def countSegments(self) -> Any:
```

Get the number of segments which may also be 0

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 401.

## `Mesh.Mesh.getSegment`

```python
def getSegment(self, index: int, /) -> list[int]:
```

Get a list of facet indices that describes a segment

Evidence: public stub `Mesh/__init__.pyi` line(s) 405.

## `Mesh.Mesh.getSeparateComponents`

```python
def getSeparateComponents(self) -> Any:
```

Returns a list containing the different
components (separated areas) of the mesh as separate meshes

import Mesh
for c in mesh.getSeparatecomponents():
Mesh.show(c)

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 409.

## `Mesh.Mesh.getFacetSelection`

```python
def getFacetSelection(self) -> Any:
```

Get a list of the indices of selected facets

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 418.

## `Mesh.Mesh.getPointSelection`

```python
def getPointSelection(self) -> Any:
```

Get a list of the indices of selected points

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 422.

## `Mesh.Mesh.meshFromSegment`

```python
def meshFromSegment(self, segment: list[int], /) -> Mesh:
```

Create a mesh from segment

Evidence: public stub `Mesh/__init__.pyi` line(s) 426.

## `Mesh.Mesh.clear`

```python
def clear(self) -> Any:
```

Clear the mesh

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 430.

## `Mesh.Mesh.isSolid`

```python
def isSolid(self) -> Any:
```

Check if the mesh is a solid

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 434.

## `Mesh.Mesh.hasNonManifolds`

```python
def hasNonManifolds(self) -> Any:
```

Check if the mesh has non-manifolds

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 438.

## `Mesh.Mesh.removeNonManifolds`

```python
def removeNonManifolds(self) -> Any:
```

Remove non-manifolds

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 442.

## `Mesh.Mesh.removeNonManifoldPoints`

```python
def removeNonManifoldPoints(self) -> Any:
```

Remove non-manifold points

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 446.

## `Mesh.Mesh.hasSelfIntersections`

```python
def hasSelfIntersections(self) -> Any:
```

Check if the mesh intersects itself

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 450.

## `Mesh.Mesh.getSelfIntersections`

```python
def getSelfIntersections(self) -> Any:
```

Returns a tuple of indices of intersecting triangles

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 454.

## `Mesh.Mesh.fixSelfIntersections`

```python
def fixSelfIntersections(self) -> Any:
```

Repair self-intersections

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 458.

## `Mesh.Mesh.removeFoldsOnSurface`

```python
def removeFoldsOnSurface(self) -> Any:
```

Remove folds on surfaces

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 462.

## `Mesh.Mesh.hasNonUniformOrientedFacets`

```python
def hasNonUniformOrientedFacets(self) -> Any:
```

Check if the mesh has facets with inconsistent orientation

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 466.

## `Mesh.Mesh.countNonUniformOrientedFacets`

```python
def countNonUniformOrientedFacets(self) -> Any:
```

Get the number of wrong oriented facets

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 470.

## `Mesh.Mesh.getNonUniformOrientedFacets`

```python
def getNonUniformOrientedFacets(self) -> Any:
```

Get a tuple of wrong oriented facets

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 474.

## `Mesh.Mesh.hasInvalidPoints`

```python
def hasInvalidPoints(self) -> Any:
```

Check if the mesh has points with invalid coordinates (NaN)

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 478.

## `Mesh.Mesh.removeInvalidPoints`

```python
def removeInvalidPoints(self) -> Any:
```

Remove points with invalid coordinates (NaN)

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 482.

## `Mesh.Mesh.hasPointsOnEdge`

```python
def hasPointsOnEdge(self) -> Any:
```

Check if points lie on edges

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 486.

## `Mesh.Mesh.removePointsOnEdge`

```python
def removePointsOnEdge(self, FillBoundary: bool=False) -> None:
```

removePointsOnEdge(FillBoundary=False)
Remove points that lie on edges.
If FillBoundary is True then the holes by removing the affected facets
will be re-filled.

Evidence: public stub `Mesh/__init__.pyi` line(s) 490.

## `Mesh.Mesh.hasInvalidNeighbourhood`

```python
def hasInvalidNeighbourhood(self) -> Any:
```

Check if the mesh has invalid neighbourhood indices

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 497.

## `Mesh.Mesh.hasPointsOutOfRange`

```python
def hasPointsOutOfRange(self) -> Any:
```

Check if the mesh has point indices that are out of range

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 501.

## `Mesh.Mesh.hasFacetsOutOfRange`

```python
def hasFacetsOutOfRange(self) -> Any:
```

Check if the mesh has facet indices that are out of range

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 505.

## `Mesh.Mesh.hasCorruptedFacets`

```python
def hasCorruptedFacets(self) -> Any:
```

Check if the mesh has corrupted facets

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 509.

## `Mesh.Mesh.countComponents`

```python
def countComponents(self) -> Any:
```

Get the number of topologic independent areas

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 513.

## `Mesh.Mesh.removeComponents`

```python
def removeComponents(self, count: int, /) -> None:
```

Remove components with less or equal to number of given facets

Evidence: public stub `Mesh/__init__.pyi` line(s) 517.

## `Mesh.Mesh.fixIndices`

```python
def fixIndices(self) -> Any:
```

Repair any invalid indices

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 521.

## `Mesh.Mesh.fixCaps`

```python
def fixCaps(self, max_angle: float=..., split_factor: float=..., /) -> None:
```

Repair caps by swapping the edge

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Mesh/__init__.pyi` line(s) 525.

## `Mesh.Mesh.fixDeformations`

```python
def fixDeformations(self, max_angle: float, epsilon: float=..., /) -> None:
```

Repair deformed facets

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Mesh/__init__.pyi` line(s) 529.

## `Mesh.Mesh.fixDegenerations`

```python
def fixDegenerations(self, epsilon: float=..., /) -> None:
```

Remove degenerated facets

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Mesh/__init__.pyi` line(s) 533.

## `Mesh.Mesh.removeDuplicatedPoints`

```python
def removeDuplicatedPoints(self) -> Any:
```

Remove duplicated points

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 537.

## `Mesh.Mesh.removeDuplicatedFacets`

```python
def removeDuplicatedFacets(self) -> Any:
```

Remove duplicated facets

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 541.

## `Mesh.Mesh.refine`

```python
def refine(self) -> Any:
```

Refine the mesh

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 545.

## `Mesh.Mesh.splitEdges`

```python
def splitEdges(self) -> Any:
```

Split all edges

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 549.

## `Mesh.Mesh.splitEdge`

```python
def splitEdge(self, facet: int, neighbour: int, vertex: Vector, /) -> None:
```

Split edge

Evidence: public stub `Mesh/__init__.pyi` line(s) 553.

## `Mesh.Mesh.splitFacet`

```python
def splitFacet(self, facet: int, vertex1: Vector, vertex2: Vector, /) -> None:
```

Split facet

Evidence: public stub `Mesh/__init__.pyi` line(s) 557.

## `Mesh.Mesh.swapEdge`

```python
def swapEdge(self, facet: int, neighbour: int, /) -> None:
```

Swap the common edge with the neighbour

Evidence: public stub `Mesh/__init__.pyi` line(s) 561.

## `Mesh.Mesh.collapseEdge`

```python
def collapseEdge(self, facet: int, neighbour: int, /) -> None:
```

Remove an edge and both facets that share this edge

Evidence: public stub `Mesh/__init__.pyi` line(s) 565.

## `Mesh.Mesh.collapseFacet`

```python
def collapseFacet(self, facet: int, /) -> None:
```

Remove a facet

Evidence: public stub `Mesh/__init__.pyi` line(s) 569.

## `Mesh.Mesh.collapseFacets`

```python
def collapseFacets(self, facets: list[int], /) -> None:
```

Remove a list of facets

Evidence: public stub `Mesh/__init__.pyi` line(s) 573.

## `Mesh.Mesh.insertVertex`

```python
def insertVertex(self, facet: int, vertex: Vector, /) -> None:
```

Insert a vertex into a facet

Evidence: public stub `Mesh/__init__.pyi` line(s) 577.

## `Mesh.Mesh.snapVertex`

```python
def snapVertex(self, facet: int, vertex: Vector, /) -> None:
```

Insert a new facet at the border

Evidence: public stub `Mesh/__init__.pyi` line(s) 581.

## `Mesh.Mesh.printInfo`

```python
def printInfo(self) -> Any:
```

Get detailed information about the mesh

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 585.

## `Mesh.Mesh.foraminate`

```python
def foraminate(self, point: _VectorInput, direction: _VectorInput, max_angle: float=..., /) -> dict:
```

Get a list of facet indices and intersection points

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Mesh/__init__.pyi` line(s) 589.

## `Mesh.Mesh.cut`

```python
def cut(self, polygon: list[_VectorInput], mode: int, /) -> None:
```

Cuts the mesh with a given closed polygon
cut(list, int) -> None
The argument list is an array of points, a polygon
The argument int is the mode: 0=inner, 1=outer

Evidence: public stub `Mesh/__init__.pyi` line(s) 593.

## `Mesh.Mesh.trim`

```python
def trim(self, polygon: list[_VectorInput], mode: int, /) -> None:
```

Trims the mesh with a given closed polygon
trim(list, int) -> None
The argument list is an array of points, a polygon
The argument int is the mode: 0=inner, 1=outer

Evidence: public stub `Mesh/__init__.pyi` line(s) 600.

## `Mesh.Mesh.trimByPlane`

```python
def trimByPlane(self, base: Vector, normal: Vector, /) -> None:
```

Trims the mesh with a given plane
trimByPlane(Vector, Vector) -> None
The plane is defined by a base and normal vector. Depending on the
direction of the normal the part above or below will be kept.

Evidence: public stub `Mesh/__init__.pyi` line(s) 607.

## `Mesh.Mesh.harmonizeNormals`

```python
def harmonizeNormals(self) -> Any:
```

Adjust wrong oriented facets

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 614.

## `Mesh.Mesh.flipNormals`

```python
def flipNormals(self) -> Any:
```

Flip the mesh normals

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 618.

## `Mesh.Mesh.fillupHoles`

```python
def fillupHoles(self, length: int, level: int=..., max_area: float=..., /) -> None:
```

Fillup holes

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Mesh/__init__.pyi` line(s) 622.

## `Mesh.Mesh.smooth`

```python
def smooth(self, Method: str='Laplace', Iteration: int=1, Lambda: float=0, Micro: float=0, Maximum: float=1000, Weight: int=1) -> None:
```

Smooth the mesh
smooth([iteration=1,maxError=FLT_MAX])

Evidence: public stub `Mesh/__init__.pyi` line(s) 626.

## `Mesh.Mesh.decimate`

```python
@overload
def decimate(self, tolerance: float, reduction: float, /) -> None:

@overload
def decimate(self, target_size: int, /) -> None:

def decimate(self, *args) -> None:
```

Decimate the mesh
decimate(tolerance(Float), reduction(Float))
tolerance: maximum error
reduction: reduction factor must be in the range [0.0,1.0]
Example:
mesh.decimate(0.5, 0.1) # reduction by up to 10 percent
mesh.decimate(0.5, 0.9) # reduction by up to 90 percent

Evidence: public stub `Mesh/__init__.pyi` line(s) 632, 636, 639.

