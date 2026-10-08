# `PathApp.Voronoi.Vertex`

[Module](index.md)

```python
class Vertex(BaseClass):
```

Vertex of a Voronoi diagram

Author: sliptonic (shopinthewoods@gmail.com)
License: LGPL-2.1-or-later

Evidence: public stub `PathApp/Voronoi.pyi` line 186. Inherited members are on the named base's reference; aliases keep their imported identity.

## `PathApp.Voronoi.Vertex.toPoint`

```python
def toPoint(self, z: float=0.0, /) -> Vector | None:
```

Returns a Vector - or None if not possible

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 194.

## `PathApp.Voronoi.Vertex.Index`

```python
Index: Final[int]
```

Internal id of the element.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 197.

## `PathApp.Voronoi.Vertex.Color`

```python
Color: int
```

Assigned color of the receiver.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 199.

## `PathApp.Voronoi.Vertex.X`

```python
X: Final[float]
```

X position

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 201.

## `PathApp.Voronoi.Vertex.Y`

```python
Y: Final[float]
```

Y position

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 203.

## `PathApp.Voronoi.Vertex.IncidentEdge`

```python
IncidentEdge: Final[Any]
```

Y position

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 205.

