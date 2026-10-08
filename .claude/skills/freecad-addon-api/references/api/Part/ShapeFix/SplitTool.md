# `Part.ShapeFix.SplitTool`

[Module](index.md)

```python
class SplitTool:
```

Tool for splitting and cutting edges

Author: Werner Mayer (wmayer@users.sourceforge.net)
Licence: LGPL

Evidence: public stub `Part/ShapeFix.pyi` line 793. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.ShapeFix.SplitTool.splitEdge`

```python
@overload
def splitEdge(self, edge: TopoShapeEdge, param1: float, vertex: TopoShapeVertex, face: TopoShapeFace, tol3d: float, tol2d: float, /) -> tuple[TopoShape, TopoShape]:

@overload
def splitEdge(self, edge: TopoShapeEdge, param1: float, param2: float, vertex: TopoShapeVertex, face: TopoShapeFace, tol3d: float, tol2d: float, /) -> tuple[TopoShape, TopoShape]:

def splitEdge(self, *args) -> tuple[TopoShape, TopoShape]:
```

Split edge on two new edges using new vertex

Evidence: public stub `Part/ShapeFix.pyi` line(s) 802, 806, 809.

## `Part.ShapeFix.SplitTool.cutEdge`

```python
def cutEdge(self, edge: TopoShapeEdge, pend: float, cut: float, face: TopoShapeFace, /) -> bool:
```

Cut edge by parameters pend and cut

Evidence: public stub `Part/ShapeFix.pyi` line(s) 815.

