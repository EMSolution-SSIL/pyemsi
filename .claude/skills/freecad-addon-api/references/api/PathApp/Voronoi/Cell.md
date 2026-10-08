# `PathApp.Voronoi.Cell`

[Module](index.md)

```python
class Cell(BaseClass):
```

Cell of a Voronoi diagram

Author: sliptonic (shopinthewoods@gmail.com)
License: LGPL-2.1-or-later

Evidence: public stub `PathApp/Voronoi.pyi` line 82. Inherited members are on the named base's reference; aliases keep their imported identity.

## `PathApp.Voronoi.Cell.containsPoint`

```python
def containsPoint(self) -> Any:
```

Returns true if the cell contains a point site

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 90.

## `PathApp.Voronoi.Cell.containsSegment`

```python
def containsSegment(self) -> Any:
```

Returns true if the cell contains a segment site

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 94.

## `PathApp.Voronoi.Cell.isDegenerate`

```python
def isDegenerate(self) -> Any:
```

Returns true if the cell doesn't have an incident edge

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 98.

## `PathApp.Voronoi.Cell.getSource`

```python
def getSource(self, z: float=0.0, /) -> Any:
```

Returns the Source for the cell

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 102.

## `PathApp.Voronoi.Cell.Index`

```python
Index: Final[int]
```

Internal id of the element.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 105.

## `PathApp.Voronoi.Cell.Color`

```python
Color: int
```

Assigned color of the receiver.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 107.

## `PathApp.Voronoi.Cell.SourceIndex`

```python
SourceIndex: Final[int]
```

Returns the index of the cell's source

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 109.

## `PathApp.Voronoi.Cell.SourceCategory`

```python
SourceCategory: Final[int]
```

Returns the cell's category as an integer

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 111.

## `PathApp.Voronoi.Cell.SourceCategoryName`

```python
SourceCategoryName: Final[str]
```

Returns the cell's category as a string

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 113.

## `PathApp.Voronoi.Cell.IncidentEdge`

```python
IncidentEdge: Final[Any]
```

Incident edge of the cell - if exists

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `PathApp/Voronoi.pyi` line(s) 115.

