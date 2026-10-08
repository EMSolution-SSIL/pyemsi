# `Part.GeomPlate.PointConstraint`

[Module](index.md)

```python
class PointConstraint:
```

Defines points as constraints to be used to deform a surface

Author: Werner Mayer (wmayer@users.sourceforge.net)
Licence: LGPL

Evidence: public stub `Part/GeomPlate.pyi` line 246. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.GeomPlate.PointConstraint.__init__`

```python
@overload
def __init__(self, Point: Vector, Order: int=..., TolDist: float=...) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/GeomPlate.pyi` line(s) 255.

## `Part.GeomPlate.PointConstraint.setOrder`

```python
def setOrder(self, order: int, /) -> None:
```

Allows you to set the order of continuity required for
the constraints: G0, G1, and G2 (as 0, 1 and 2), controlled
respectively by G0Criterion G1Criterion and G2Criterion.

Evidence: public stub `Part/GeomPlate.pyi` line(s) 258.

## `Part.GeomPlate.PointConstraint.order`

```python
def order(self) -> int:
```

Returns the order of constraint (0, 1 or 2 for G0, G1 or G2)

Evidence: public stub `Part/GeomPlate.pyi` line(s) 266.

## `Part.GeomPlate.PointConstraint.G0Criterion`

```python
def G0Criterion(self) -> float:
```

Returns the G0 criterion.
This is the greatest distance allowed between
the constraint and the target surface.

Evidence: public stub `Part/GeomPlate.pyi` line(s) 272.

## `Part.GeomPlate.PointConstraint.G1Criterion`

```python
def G1Criterion(self) -> float:
```

Returns the G1 criterion.
This is the greatest angle allowed between
the constraint and the target surface.
Raises an exception if  the  curve  is  not  on  a  surface.

Evidence: public stub `Part/GeomPlate.pyi` line(s) 280.

## `Part.GeomPlate.PointConstraint.G2Criterion`

```python
def G2Criterion(self) -> float:
```

Returns the G2 criterion.
This is the greatest difference in curvature
allowed between the constraint and the target surface.
Raises an exception if  the  curve  is  not  on  a  surface.

Evidence: public stub `Part/GeomPlate.pyi` line(s) 289.

## `Part.GeomPlate.PointConstraint.setG0Criterion`

```python
def setG0Criterion(self, value: float, /) -> None:
```

Allows you to set the G0 criterion. This is the law
defining the greatest distance allowed between the
constraint and the target surface for each point of the
constraint. If this criterion is not set, TolDist, the
distance tolerance from the constructor, is used.

Evidence: public stub `Part/GeomPlate.pyi` line(s) 298.

## `Part.GeomPlate.PointConstraint.setG1Criterion`

```python
def setG1Criterion(self, value: float, /) -> None:
```

Allows you to set the G1 criterion. This is the law
defining the greatest angle allowed between the
constraint and the target surface. If this criterion is not
set, TolAng, the angular tolerance from the constructor, is used.
Raises an exception if  the  curve  is  not  on  a  surface

Evidence: public stub `Part/GeomPlate.pyi` line(s) 308.

## `Part.GeomPlate.PointConstraint.setG2Criterion`

```python
def setG2Criterion(self, value: float, /) -> None:
```

Allows you to set the G2 criterion. This is the law
defining the greatest difference in curvature  allowed between the
constraint and the target surface. If this criterion is not
set, TolCurv, the curvature tolerance from the constructor, is used.
Raises  ConstructionError if  the  curve  is  not  on  a  surface

Evidence: public stub `Part/GeomPlate.pyi` line(s) 318.

## `Part.GeomPlate.PointConstraint.hasPnt2dOnSurf`

```python
def hasPnt2dOnSurf(self) -> bool:
```

Checks if there is a 2D point associated with the surface. It returns a boolean indicating whether such a point exists.

Evidence: public stub `Part/GeomPlate.pyi` line(s) 328.

## `Part.GeomPlate.PointConstraint.setPnt2dOnSurf`

```python
def setPnt2dOnSurf(self, x: float, y: float, /) -> None:
```

Allows you to set a 2D point on the surface. It takes a gp_Pnt2d as an argument, representing the 2D point to be associated with the surface.

Evidence: public stub `Part/GeomPlate.pyi` line(s) 334.

## `Part.GeomPlate.PointConstraint.pnt2dOnSurf`

```python
def pnt2dOnSurf(self) -> Tuple[float, float]:
```

Returns the 2D point on the surface. It returns a gp_Pnt2d representing the associated 2D point.

Evidence: public stub `Part/GeomPlate.pyi` line(s) 340.

