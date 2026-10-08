# `Part.ChFi2d.FilletAlgo`

[Module](index.md)

```python
class FilletAlgo:
```

Algorithm that creates fillet edge

Author: Werner Mayer (wmayer[at]users.sourceforge.net)
Licence: LGPL

Evidence: public stub `Part/ChFi2d.pyi` line 142. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.ChFi2d.FilletAlgo.init`

```python
@overload
def init(self, wire: TopoShapeWire, plane: Plane, /) -> None:

@overload
def init(self, edge1: TopoShapeEdge, edge2: TopoShapeEdge, plane: Plane, /) -> None:

def init(self, *args) -> None:
```

Initializes a fillet algorithm: accepts a wire consisting of two edges in a plane

Evidence: public stub `Part/ChFi2d.pyi` line(s) 151, 155, 158.

## `Part.ChFi2d.FilletAlgo.perform`

```python
def perform(self, radius: float, /) -> bool:
```

perform(radius) -> bool

Constructs a fillet edge

Evidence: public stub `Part/ChFi2d.pyi` line(s) 164.

## `Part.ChFi2d.FilletAlgo.numberOfResults`

```python
def numberOfResults(self, point: Vector, /) -> int:
```

Returns number of possible solutions

Evidence: public stub `Part/ChFi2d.pyi` line(s) 172.

## `Part.ChFi2d.FilletAlgo.result`

```python
def result(self, point: Vector, solution: int=-1, /) -> tuple[object, object, object]:
```

result(point, solution=-1)

Returns result (fillet edge, modified edge1, modified edge2)

Evidence: public stub `Part/ChFi2d.pyi` line(s) 178.

