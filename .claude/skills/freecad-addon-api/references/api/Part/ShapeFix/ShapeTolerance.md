# `Part.ShapeFix.ShapeTolerance`

[Module](index.md)

```python
class ShapeTolerance:
```

Modifies tolerances of sub-shapes (vertices, edges, faces)

Author: Werner Mayer (wmayer@users.sourceforge.net)
Licence: LGPL

Evidence: public stub `Part/ShapeFix.pyi` line 597. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.ShapeFix.ShapeTolerance.limitTolerance`

```python
@overload
def limitTolerance(self, shape: TopoShape, tmin: float, /) -> bool:

@overload
def limitTolerance(self, shape: TopoShape, tmin: float, tmax: float, ShapeEnum: str=None, /) -> bool:

def limitTolerance(self, shape: TopoShape, tmin: float, tmax: float=0, ShapeEnum: str=None, /) -> bool:
```

limitTolerance(shape, tmin, [tmax=0, ShapeEnum=SHAPE])

Evidence: public stub `Part/ShapeFix.pyi` line(s) 606, 610, 613.

## `Part.ShapeFix.ShapeTolerance.setTolerance`

```python
@overload
def setTolerance(self, shape: TopoShape, precision: float, /) -> None:

@overload
def setTolerance(self, shape: TopoShape, precision: float, ShapeEnum: str=None, /) -> None:

def setTolerance(self, shape: TopoShape, precision: float, ShapeEnum: str=None, /) -> None:
```

setTolerance(shape, precision, [ShapeEnum=SHAPE])

Evidence: public stub `Part/ShapeFix.pyi` line(s) 620, 624, 627.

