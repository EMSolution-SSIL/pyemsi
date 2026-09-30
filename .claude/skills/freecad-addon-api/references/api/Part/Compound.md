# `Part.Compound`

[Module](index.md)

```python
class Compound(Shape):
```

Create a compound out of a list of shapes

Author: Juergen Riegel (Juergen.Riegel@web.de)
Licence: LGPL

Evidence: public stub `Part/__init__.pyi` line 4461. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.Compound.__init__`

```python
@overload
def __init__(self) -> None:

@overload
def __init__(self, shapes: Shape | Sequence[Shape], /) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Evidence: public stub `Part/__init__.pyi` line(s) 4470, 4474.

## `Part.Compound.add`

```python
def add(self, shape: Shape, /) -> None:
```

Add a shape to the compound.
add(shape)

Evidence: public stub `Part/__init__.pyi` line(s) 4477.

## `Part.Compound.connectEdgesToWires`

```python
def connectEdgesToWires(self, Shared: bool=True, Tolerance: float=1e-07, /) -> 'TopoShapeCompound':
```

Build a compound of wires out of the edges of this compound.
connectEdgesToWires([Shared = True, Tolerance = 1e-7]) -> Compound
--
If Shared is True  connection is performed only when adjacent edges share the same vertex.
If Shared is False connection is performed only when ends of adjacent edges are at distance less than Tolerance.

Evidence: public stub `Part/__init__.pyi` line(s) 4484.

## `Part.Compound.setFaces`

```python
def setFaces(self, data: tuple, accuracy: float=..., /) -> None:
```

A shape is created from points and triangles and set to this object

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 4494.

