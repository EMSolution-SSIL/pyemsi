# `Mesh.Facet`

[Module](index.md)

```python
class Facet:
```

Facet in mesh
This is a facet in a MeshObject. You can get it by e.g. iterating a
mesh. The facet has a connection to its mesh and allows therefore
topological operations. It is also possible to create an unbounded facet e.g. to create
a mesh. In this case the topological operations will fail. The same is
when you cut the bound to the mesh by calling unbound().

Author: Juergen Riegel (Juergen.Riegel@web.de)
License: LGPL-2.1-or-later

Evidence: public stub `Mesh/__init__.pyi` line 138. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Mesh.Facet.unbound`

```python
def unbound(self) -> None:
```

method unbound()
Cut the connection to a MeshObject. The facet becomes
free and is more or less a simple facet.
After calling unbound() no topological operation will
work!

Evidence: public stub `Mesh/__init__.pyi` line(s) 151.

## `Mesh.Facet.intersect`

```python
def intersect(self, facet: Facet, /) -> list[tuple[float, float, float]]:
```

intersect(Facet) -> list
Get a list of intersection points with another triangle.

Evidence: public stub `Mesh/__init__.pyi` line(s) 159.

## `Mesh.Facet.isDegenerated`

```python
def isDegenerated(self, epsilon: float=..., /) -> bool:
```

isDegenerated([float]) -> boolean
Returns true if the facet is degenerated, otherwise false.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Mesh/__init__.pyi` line(s) 164.

## `Mesh.Facet.isDeformed`

```python
def isDeformed(self, min_angle: float, max_angle: float, /) -> bool:
```

isDegenerated(MinAngle, MaxAngle) -> boolean
Returns true if the facet is deformed, otherwise false.
A triangle is considered deformed if an angle is less than MinAngle
or higher than MaxAngle.
The two angles are given in radian.

Evidence: public stub `Mesh/__init__.pyi` line(s) 169.

## `Mesh.Facet.getEdge`

```python
def getEdge(self, index: int, /) -> Edge:
```

getEdge(int) -> Edge
Returns the edge of the facet.

Evidence: public stub `Mesh/__init__.pyi` line(s) 177.

## `Mesh.Facet.Index`

```python
Index: Final[int]
```

The index of this facet in the MeshObject

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Mesh/__init__.pyi` line(s) 181.

## `Mesh.Facet.Bound`

```python
Bound: Final[bool]
```

Bound state of the facet

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Mesh/__init__.pyi` line(s) 183.

## `Mesh.Facet.Normal`

```python
Normal: Final[Vector]
```

Normal vector of the facet.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Mesh/__init__.pyi` line(s) 185.

## `Mesh.Facet.Points`

```python
Points: Final[list]
```

A list of points of the facet

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Mesh/__init__.pyi` line(s) 187.

## `Mesh.Facet.PointIndices`

```python
PointIndices: Final[tuple]
```

The index tuple of point vertices of the mesh this facet is built of

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Mesh/__init__.pyi` line(s) 189.

## `Mesh.Facet.NeighbourIndices`

```python
NeighbourIndices: Final[tuple]
```

The index tuple of neighbour facets of the mesh this facet is adjacent with

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Mesh/__init__.pyi` line(s) 191.

## `Mesh.Facet.Area`

```python
Area: Final[float]
```

The area of the facet

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Mesh/__init__.pyi` line(s) 193.

## `Mesh.Facet.AspectRatio`

```python
AspectRatio: Final[float]
```

The aspect ratio of the facet computed by longest edge and its height

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Mesh/__init__.pyi` line(s) 195.

## `Mesh.Facet.AspectRatio2`

```python
AspectRatio2: Final[float]
```

The aspect ratio of the facet computed by radius of circum-circle and in-circle

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Mesh/__init__.pyi` line(s) 197.

## `Mesh.Facet.Roundness`

```python
Roundness: Final[float]
```

The roundness of the facet

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Mesh/__init__.pyi` line(s) 199.

## `Mesh.Facet.CircumCircle`

```python
CircumCircle: Final[tuple]
```

The center and radius of the circum-circle

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Mesh/__init__.pyi` line(s) 201.

## `Mesh.Facet.InCircle`

```python
InCircle: Final[tuple]
```

The center and radius of the in-circle

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Mesh/__init__.pyi` line(s) 203.

