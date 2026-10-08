# `Part.ChFi2d.FilletAPI`

[Module](index.md)

```python
class FilletAPI:
```

Algorithm that creates fillet edge

Author: Werner Mayer (wmayer[at]users.sourceforge.net)
Licence: LGPL

Evidence: public stub `Part/ChFi2d.pyi` line 97. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.ChFi2d.FilletAPI.init`

```python
@overload
def init(self, wire: TopoShapeWire, plane: Plane, /) -> None:

@overload
def init(self, edge1: TopoShapeEdge, edge2: TopoShapeEdge, plane: Plane, /) -> None:

def init(self, *args) -> None:
```

Initializes a fillet algorithm: accepts a wire consisting of two edges in a plane

Evidence: public stub `Part/ChFi2d.pyi` line(s) 106, 110, 113.

## `Part.ChFi2d.FilletAPI.perform`

```python
def perform(self, radius: float, /) -> bool:
```

perform(radius) -> bool

Constructs a fillet edge

Evidence: public stub `Part/ChFi2d.pyi` line(s) 119.

## `Part.ChFi2d.FilletAPI.numberOfResults`

```python
def numberOfResults(self, point: Vector, /) -> int:
```

Returns number of possible solutions

Evidence: public stub `Part/ChFi2d.pyi` line(s) 127.

## `Part.ChFi2d.FilletAPI.result`

```python
def result(self, point: Point, solution: int=-1, /) -> tuple[TopoShapeEdge, TopoShapeEdge, TopoShapeEdge]:
```

result(point, solution=-1)

Returns result (fillet edge, modified edge1, modified edge2)

Evidence: public stub `Part/ChFi2d.pyi` line(s) 133.

