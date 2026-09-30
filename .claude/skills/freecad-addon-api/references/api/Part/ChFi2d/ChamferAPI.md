# `Part.ChFi2d.ChamferAPI`

[Module](index.md)

```python
class ChamferAPI:
```

Algorithm that creates a chamfer between two linear edges

Author: Werner Mayer (wmayer[at]users.sourceforge.net)
Licence: LGPL

Evidence: public stub `Part/ChFi2d.pyi` line 49. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.ChFi2d.ChamferAPI.__init__`

```python
@overload
def __init__(self, wire: object) -> None:

@overload
def __init__(self, edge1: object, edge2: object) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Evidence: public stub `Part/ChFi2d.pyi` line(s) 58, 62.

## `Part.ChFi2d.ChamferAPI.init`

```python
@overload
def init(self, wire: object, /) -> None:

@overload
def init(self, edge1: object, edge2: object, /) -> None:

def init(self, *args) -> None:
```

Initializes a chamfer algorithm: accepts a wire consisting of two edges in a plane,
or a pair of edges.

Evidence: public stub `Part/ChFi2d.pyi` line(s) 66, 70, 73.

## `Part.ChFi2d.ChamferAPI.perform`

```python
def perform(self) -> bool:
```

perform() -> bool

Constructs a chamfer edge

Evidence: public stub `Part/ChFi2d.pyi` line(s) 80.

## `Part.ChFi2d.ChamferAPI.result`

```python
def result(self, length1: float, length2: float, /) -> Tuple[object, object, object]:
```

result(length1, length2)

Returns result (chamfer edge, modified edge1, modified edge2)

Evidence: public stub `Part/ChFi2d.pyi` line(s) 88.

