# `PathApp.Voronoi.Diagram`

[Module](index.md)

```python
class Diagram(BaseClass):
```

Voronoi([segments]): Create voronoi for given collection of line segments

Author: sliptonic (shopinthewoods@gmail.com)
License: LGPL-2.1-or-later

Evidence: public stub `PathApp/Voronoi.pyi` line 11. Inherited members are on the named base's reference; aliases keep their imported identity.

## `PathApp.Voronoi.Diagram.numCells`

```python
def numCells(self) -> int:
```

Return number of cells

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 19.

## `PathApp.Voronoi.Diagram.numEdges`

```python
def numEdges(self) -> int:
```

Return number of edges

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 23.

## `PathApp.Voronoi.Diagram.numVertices`

```python
def numVertices(self) -> int:
```

Return number of vertices

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 27.

## `PathApp.Voronoi.Diagram.addPoint`

```python
def addPoint(self, point: Vector, /) -> None:
```

add given point to input collection

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 31.

## `PathApp.Voronoi.Diagram.addSegment`

```python
def addSegment(self, point1: Vector, point2: Vector, /) -> None:
```

add given segment to input collection

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 35.

## `PathApp.Voronoi.Diagram.construct`

```python
def construct(self) -> None:
```

constructs the voronoi diagram from the input collections

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 39.

## `PathApp.Voronoi.Diagram.colorExterior`

```python
def colorExterior(self, color: int, callback: Any=..., /) -> None:
```

assign given color to all exterior edges and vertices

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 43.

## `PathApp.Voronoi.Diagram.colorTwins`

```python
def colorTwins(self, color: int, /) -> None:
```

assign given color to all twins of edges (which one is considered a twin is arbitrary)

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 47.

## `PathApp.Voronoi.Diagram.colorColinear`

```python
def colorColinear(self, color: int, degree: float=..., /) -> None:
```

assign given color to all edges sourced by two segments almost in line with each other (optional angle in degrees)

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 51.

## `PathApp.Voronoi.Diagram.resetColor`

```python
def resetColor(self, color: int, /) -> None:
```

assign color 0 to all elements with the given color

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 55.

## `PathApp.Voronoi.Diagram.getPoints`

```python
def getPoints(self, z: float=..., /) -> list[Vector]:
```

Get list of all input points.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 59.

## `PathApp.Voronoi.Diagram.numPoints`

```python
def numPoints(self) -> int:
```

Return number of input points

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 63.

## `PathApp.Voronoi.Diagram.getSegments`

```python
def getSegments(self, z: float=..., /) -> list[tuple[Vector, Vector]]:
```

Get list of all input segments.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 67.

## `PathApp.Voronoi.Diagram.numSegments`

```python
def numSegments(self) -> int:
```

Return number of input segments

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 71.

## `PathApp.Voronoi.Diagram.Cells`

```python
Cells: Final[list]
```

List of all cells of the voronoi diagram

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 74.

## `PathApp.Voronoi.Diagram.Edges`

```python
Edges: Final[list]
```

List of all edges of the voronoi diagram

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 76.

## `PathApp.Voronoi.Diagram.Vertices`

```python
Vertices: Final[list]
```

List of all vertices of the voronoi diagram

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 78.

