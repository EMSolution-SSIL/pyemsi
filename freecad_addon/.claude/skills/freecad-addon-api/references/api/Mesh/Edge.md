# `Mesh.Edge`

[Module](index.md)

```python
class Edge:
```

Edge in mesh
This is an edge of a facet in a MeshObject. You can get it by e.g. iterating over the facets of a
mesh and calling getEdge(index).

Author: Werner Mayer (wmayer[at]users.sourceforge.net)
License: LGPL-2.1-or-later

Evidence: public stub `Mesh/__init__.pyi` line 93. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Mesh.Edge.intersectWithEdge`

```python
def intersectWithEdge(self, edge: Edge, /) -> list[tuple[float, float, float]]:
```

intersectWithEdge(Edge) -> list
Get a list of intersection points with another edge.

Evidence: public stub `Mesh/__init__.pyi` line(s) 103.

## `Mesh.Edge.isParallel`

```python
def isParallel(self, edge: Edge, /) -> bool:
```

isParallel(Edge) -> bool
Checks if the two edges are parallel.

Evidence: public stub `Mesh/__init__.pyi` line(s) 108.

## `Mesh.Edge.isCollinear`

```python
def isCollinear(self, edge: Edge, /) -> bool:
```

isCollinear(Edge) -> bool
Checks if the two edges are collinear.

Evidence: public stub `Mesh/__init__.pyi` line(s) 113.

## `Mesh.Edge.unbound`

```python
def unbound(self) -> None:
```

method unbound()
Cut the connection to a MeshObject. The edge becomes
free and is more or less a simple edge.
After calling unbound() no topological operation will
work!

Evidence: public stub `Mesh/__init__.pyi` line(s) 118.

## `Mesh.Edge.Index`

```python
Index: Final[int]
```

The index of this edge of the facet

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Mesh/__init__.pyi` line(s) 125.

## `Mesh.Edge.Points`

```python
Points: Final[list]
```

A list of points of the edge

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Mesh/__init__.pyi` line(s) 127.

## `Mesh.Edge.PointIndices`

```python
PointIndices: Final[tuple]
```

The index tuple of point vertices of the mesh this edge is built of

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Mesh/__init__.pyi` line(s) 129.

## `Mesh.Edge.NeighbourIndices`

```python
NeighbourIndices: Final[tuple]
```

The index tuple of neighbour facets of the mesh this edge is adjacent with

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Mesh/__init__.pyi` line(s) 131.

## `Mesh.Edge.Length`

```python
Length: Final[float]
```

The length of the edge

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Mesh/__init__.pyi` line(s) 133.

## `Mesh.Edge.Bound`

```python
Bound: Final[bool]
```

Bound state of the edge

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Mesh/__init__.pyi` line(s) 135.

