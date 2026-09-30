# `Part.GeomPlate.CurveConstraint`

[Module](index.md)

```python
class CurveConstraint:
```

Defines curves as constraints to be used to deform a surface

Author: Werner Mayer (wmayer@users.sourceforge.net)
Licence: LGPL

Evidence: public stub `Part/GeomPlate.pyi` line 130. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.GeomPlate.CurveConstraint.NbPoints`

```python
NbPoints: int = ...
```


    The number of points on the curve used as a
    constraint. The default setting is 10. This parameter
    affects computation time, which increases by the cube of
    the number of points.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/GeomPlate.pyi` line(s) 137.

## `Part.GeomPlate.CurveConstraint.FirstParameter`

```python
FirstParameter: Final[float] = ...
```


    This function returns the first parameter of the curve.
    The first parameter is the lowest parametric value for the curve, which defines the starting point of the curve.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/GeomPlate.pyi` line(s) 139.

## `Part.GeomPlate.CurveConstraint.LastParameter`

```python
LastParameter: Final[float] = ...
```


    This function returns the last parameter of the curve.
    The last parameter is the highest parametric value for the curve, which defines the ending point of the curve.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/GeomPlate.pyi` line(s) 141.

## `Part.GeomPlate.CurveConstraint.Length`

```python
Length: Final[float] = ...
```


    This function returns the length of the curve.
    The length of the curve is a geometric property that indicates how long the curve is in the space.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/GeomPlate.pyi` line(s) 143.

## `Part.GeomPlate.CurveConstraint.setOrder`

```python
def setOrder(self, order: int, /) -> None:
```

Allows you to set the order of continuity required for the constraints: G0, G1, and G2, controlled
respectively by G0Criterion G1Criterion and G2Criterion.

Evidence: public stub `Part/GeomPlate.pyi` line(s) 146.

## `Part.GeomPlate.CurveConstraint.order`

```python
def order(self) -> int:
```

Returns the order of constraint, one of G0, G1 or G2

Evidence: public stub `Part/GeomPlate.pyi` line(s) 153.

## `Part.GeomPlate.CurveConstraint.G0Criterion`

```python
def G0Criterion(self, u: float, /) -> float:
```

Returns the G0 criterion at the parametric point U on the curve.
This is the greatest distance allowed between the constraint and the target surface at U.

Evidence: public stub `Part/GeomPlate.pyi` line(s) 159.

## `Part.GeomPlate.CurveConstraint.G1Criterion`

```python
def G1Criterion(self, u: float, /) -> float:
```

Returns the G1 criterion at the parametric point U on the curve.
This is the greatest angle allowed between the constraint and the target surface at U.
Raises an exception if the curve is not on a surface.

Evidence: public stub `Part/GeomPlate.pyi` line(s) 166.

## `Part.GeomPlate.CurveConstraint.G2Criterion`

```python
def G2Criterion(self, u: float, /) -> float:
```

Returns the G2 criterion at the parametric point U on the curve.
This is the greatest difference in curvature allowed between the constraint and the target surface at U.
Raises an exception if the curve is not on a surface.

Evidence: public stub `Part/GeomPlate.pyi` line(s) 174.

## `Part.GeomPlate.CurveConstraint.setG0Criterion`

```python
def setG0Criterion(self) -> None:
```

Allows you to set the G0 criterion. This is the law
defining the greatest distance allowed between the
constraint and the target surface for each point of the
constraint. If this criterion is not set, TolDist, the
distance tolerance from the constructor, is used.

Evidence: public stub `Part/GeomPlate.pyi` line(s) 182.

## `Part.GeomPlate.CurveConstraint.setG1Criterion`

```python
def setG1Criterion(self) -> None:
```

Allows you to set the G1 criterion. This is the law
defining the greatest angle allowed between the
constraint and the target surface. If this criterion is not
set, TolAng, the angular tolerance from the constructor, is used.
Raises an exception if the curve is not on a surface.

Evidence: public stub `Part/GeomPlate.pyi` line(s) 192.

## `Part.GeomPlate.CurveConstraint.setG2Criterion`

```python
def setG2Criterion(self) -> None:
```

Allows you to set the G2 criterion. This is the law
defining the greatest difference in curvature allowed
between the constraint and the target surface. If this
criterion is not set, TolCurv, the curvature tolerance from
the constructor, is used.
Raises ConstructionError if the point is not on the surface.

Evidence: public stub `Part/GeomPlate.pyi` line(s) 202.

## `Part.GeomPlate.CurveConstraint.curve3d`

```python
def curve3d(self) -> None:
```

Returns a 3d curve associated the surface resulting of the constraints

Evidence: public stub `Part/GeomPlate.pyi` line(s) 213.

## `Part.GeomPlate.CurveConstraint.setCurve2dOnSurf`

```python
def setCurve2dOnSurf(self, curve: Curve2d, /) -> None:
```

Loads a 2d curve associated the surface resulting of the constraints

Evidence: public stub `Part/GeomPlate.pyi` line(s) 219.

## `Part.GeomPlate.CurveConstraint.curve2dOnSurf`

```python
def curve2dOnSurf(self) -> None:
```

Returns a 2d curve associated the surface resulting of the constraints

Evidence: public stub `Part/GeomPlate.pyi` line(s) 225.

## `Part.GeomPlate.CurveConstraint.setProjectedCurve`

```python
def setProjectedCurve(self, curve: Curve2d, tol_u: float, tol_v: float, /) -> None:
```

Loads a 2d curve  resulting from the normal projection of
the curve on the initial surface

Evidence: public stub `Part/GeomPlate.pyi` line(s) 231.

## `Part.GeomPlate.CurveConstraint.projectedCurve`

```python
def projectedCurve(self) -> None:
```

Returns the projected curve resulting from the normal projection of the
curve on the initial surface

Evidence: public stub `Part/GeomPlate.pyi` line(s) 238.

