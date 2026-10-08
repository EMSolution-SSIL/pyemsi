# `PathApp.Voronoi.Edge`

[Module](index.md)

```python
class Edge(BaseClass):
```

Edge of a Voronoi diagram

Author: sliptonic (shopinthewoods@gmail.com)
License: LGPL-2.1-or-later

Evidence: public stub `PathApp/Voronoi.pyi` line 119. Inherited members are on the named base's reference; aliases keep their imported identity.

## `PathApp.Voronoi.Edge.isFinite`

```python
def isFinite(self) -> Any:
```

Returns true if both vertices are finite

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 127.

## `PathApp.Voronoi.Edge.isInfinite`

```python
def isInfinite(self) -> Any:
```

Returns true if the end vertex is infinite

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 131.

## `PathApp.Voronoi.Edge.isLinear`

```python
def isLinear(self) -> Any:
```

Returns true if edge is straight

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 135.

## `PathApp.Voronoi.Edge.isCurved`

```python
def isCurved(self) -> Any:
```

Returns true if edge is curved

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 139.

## `PathApp.Voronoi.Edge.isPrimary`

```python
def isPrimary(self) -> Any:
```

Returns false if edge goes through endpoint of the segment site

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 143.

## `PathApp.Voronoi.Edge.isSecondary`

```python
def isSecondary(self) -> Any:
```

Returns true if edge goes through endpoint of the segment site

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 147.

## `PathApp.Voronoi.Edge.isBorderline`

```python
def isBorderline(self) -> Any:
```

Returns true if the point is on the segment

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 151.

## `PathApp.Voronoi.Edge.toShape`

```python
def toShape(self, z0: float=0.0, z1: float=0.0, dbg: bool=False, /) -> TopoShapeEdge | None:
```

Returns a shape for the edge

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 155.

## `PathApp.Voronoi.Edge.getDistances`

```python
def getDistances(self) -> Any:
```

Returns the distance of the vertices to the input source

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 159.

## `PathApp.Voronoi.Edge.getSegmentAngle`

```python
def getSegmentAngle(self) -> float | None:
```

Returns the angle (in degree) of the segments if the edge was formed by two segments

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 163.

## `PathApp.Voronoi.Edge.Index`

```python
Index: Final[int]
```

Internal id of the element.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 166.

## `PathApp.Voronoi.Edge.Color`

```python
Color: int
```

Assigned color of the receiver.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 168.

## `PathApp.Voronoi.Edge.Cell`

```python
Cell: Final[Any]
```

cell the edge belongs to

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 170.

## `PathApp.Voronoi.Edge.Vertices`

```python
Vertices: Final[list]
```

Begin and End voronoi vertex

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 172.

## `PathApp.Voronoi.Edge.Next`

```python
Next: Final[Any]
```

CCW next edge within voronoi cell

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 174.

## `PathApp.Voronoi.Edge.Prev`

```python
Prev: Final[Any]
```

CCW previous edge within voronoi cell

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 176.

## `PathApp.Voronoi.Edge.RotNext`

```python
RotNext: Final[Any]
```

Rotated CCW next edge within voronoi cell

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 178.

## `PathApp.Voronoi.Edge.RotPrev`

```python
RotPrev: Final[Any]
```

Rotated CCW previous edge within voronoi cell

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 180.

## `PathApp.Voronoi.Edge.Twin`

```python
Twin: Final[Any]
```

Twin edge

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 182.

