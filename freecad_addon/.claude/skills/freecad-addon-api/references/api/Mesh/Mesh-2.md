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

## `Mesh.Mesh.mergeFacets`

```python
def mergeFacets(self) -> Any:
```

Merge facets to optimize topology

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 649.

## `Mesh.Mesh.optimizeTopology`

```python
def optimizeTopology(self, max_angle: float=..., /) -> None:
```

Optimize the edges to get nicer facets

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Mesh/__init__.pyi` line(s) 653.

## `Mesh.Mesh.optimizeEdges`

```python
def optimizeEdges(self) -> Any:
```

Optimize the edges to get nicer facets

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 657.

## `Mesh.Mesh.nearestFacetOnRay`

```python
def nearestFacetOnRay(self, point: _VectorInput, direction: _VectorInput, max_angle: float=..., /) -> dict:
```

nearestFacetOnRay(tuple, tuple) -> dict
Get the index and intersection point of the nearest facet to a ray.
The first parameter is a tuple of three floats the base point of the ray,
the second parameter is ut uple of three floats for the direction.
The result is a dictionary with an index and the intersection point or
an empty dictionary if there is no intersection.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Mesh/__init__.pyi` line(s) 661.

## `Mesh.Mesh.getPlanarSegments`

```python
def getPlanarSegments(self, deviation: float, min_facets: int=..., /) -> list:
```

getPlanarSegments(dev,[min faces=0]) -> list
Get all planes of the mesh as segment.
In the worst case each triangle can be regarded as single
plane if none of its neighbours is coplanar.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Mesh/__init__.pyi` line(s) 670.

## `Mesh.Mesh.getSegmentsOfType`

```python
def getSegmentsOfType(self, type: str, deviation: float, min_facets: int=..., /) -> list:
```

getSegmentsOfType(type, dev,[min faces=0]) -> list
Get all segments of type.
Type can be Plane, Cylinder or Sphere

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Mesh/__init__.pyi` line(s) 677.

## `Mesh.Mesh.getSegmentsByCurvature`

```python
def getSegmentsByCurvature(self, curvature: list[tuple[float, float, float, float, int]], /) -> list:
```

getSegmentsByCurvature(list) -> list
The argument list gives a list if tuples where it defines the preferred maximum curvature,
the preferred minimum curvature, the tolerances and the number of minimum faces for the segment.
Example:
c=(1.0, 0.0, 0.1, 0.1, 500) # search for a cylinder with radius 1.0
p=(0.0, 0.0, 0.1, 0.1, 500) # search for a plane
mesh.getSegmentsByCurvature([c,p])

Evidence: public stub `Mesh/__init__.pyi` line(s) 683.

## `Mesh.Mesh.getCurvaturePerVertex`

```python
def getCurvaturePerVertex(self) -> Any:
```

getCurvaturePerVertex() -> list
The items in the list contains minimum and maximum curvature with their directions

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 693.

## `Mesh.Mesh.Points`

```python
Points: Final[list]
```

A collection of the mesh points
With this attribute it is possible to get access to the points of the mesh
for p in mesh.Points:
	print p.x, p.y, p.z

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Mesh/__init__.pyi` line(s) 698.

## `Mesh.Mesh.CountPoints`

```python
CountPoints: Final[int]
```

Return the number of vertices of the mesh object.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Mesh/__init__.pyi` line(s) 700.

## `Mesh.Mesh.CountEdges`

```python
CountEdges: Final[int]
```

Return the number of edges of the mesh object.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Mesh/__init__.pyi` line(s) 702.

## `Mesh.Mesh.Facets`

```python
Facets: Final[list]
```

A collection of facets
With this attribute it is possible to get access to the facets of the mesh
for p in mesh.Facets:
	print p

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Mesh/__init__.pyi` line(s) 704.

## `Mesh.Mesh.CountFacets`

```python
CountFacets: Final[int]
```

Return the number of facets of the mesh object.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Mesh/__init__.pyi` line(s) 706.

## `Mesh.Mesh.Topology`

```python
Topology: Final[tuple]
```

Return the points and face indices as tuple.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Mesh/__init__.pyi` line(s) 708.

## `Mesh.Mesh.Area`

```python
Area: Final[float]
```

Return the area of the mesh object.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Mesh/__init__.pyi` line(s) 710.

## `Mesh.Mesh.Volume`

```python
Volume: Final[float]
```

Return the volume of the mesh object.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Mesh/__init__.pyi` line(s) 712.

