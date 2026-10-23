# `Part.ShapeFix.EdgeConnect`

[Module](index.md)

```python
class EdgeConnect:
```

Root class for fixing operations

Author: Werner Mayer (wmayer@users.sourceforge.net)
Licence: LGPL

Evidence: public stub `Part/ShapeFix.pyi` line 208. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.ShapeFix.EdgeConnect.add`

```python
@overload
def add(self, edge1: TopoShapeEdge, edge2: TopoShapeEdge, /) -> None:

@overload
def add(self, shape: TopoShape, /) -> None:

def add(self, *args, **kwargs) -> None:
```

add(edge, edge)
Adds information on connectivity between start vertex
of second edge and end vertex of first edge taking
edges orientation into account

add(shape)
Adds connectivity information for the whole shape.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 217, 221, 224.

## `Part.ShapeFix.EdgeConnect.build`

```python
def build(self) -> None:
```

Builds shared vertices, updates their positions and tolerances

Evidence: public stub `Part/ShapeFix.pyi` line(s) 236.

## `Part.ShapeFix.EdgeConnect.clear`

```python
def clear(self) -> None:
```

Clears internal data structure

Evidence: public stub `Part/ShapeFix.pyi` line(s) 242.

