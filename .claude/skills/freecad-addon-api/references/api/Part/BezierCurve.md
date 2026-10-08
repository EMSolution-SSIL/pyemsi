# `Part.BezierCurve`

[Module](index.md)

```python
class BezierCurve(BoundedCurve):
```

Describes a rational or non-rational Bezier curve:
-- a non-rational Bezier curve is defined by a table of poles (also called control points)
-- a rational Bezier curve is defined by a table of poles with varying weights

Constructor takes no arguments.

Example usage:
    p1 = Base.Vector(-1, 0, 0)
    p2 = Base.Vector(0, 1, 0.2)
    p3 = Base.Vector(1, 0, 0.4)
    p4 = Base.Vector(0, -1, 1)

    bc = BezierCurve()
    bc.setPoles([p1, p2, p3, p4])
    curveShape = bc.toShape()

Evidence: public stub `Part/__init__.pyi` line 1590. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.BezierCurve.Degree`

```python
Degree: Final[int] = 0
```


    Returns the polynomial degree of this Bezier curve,
    which is equal to the number of poles minus 1.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 1608.

## `Part.BezierCurve.MaxDegree`

```python
MaxDegree: Final[int] = 25
```


    Returns the value of the maximum polynomial degree of any
    Bezier curve curve. This value is 25.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 1610.

## `Part.BezierCurve.NbPoles`

```python
NbPoles: Final[int] = 0
```

Returns the number of poles of this Bezier curve.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 1612.

## `Part.BezierCurve.StartPoint`

```python
StartPoint: Final[Vector] = Vector()
```

Returns the start point of this Bezier curve.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 1614.

## `Part.BezierCurve.EndPoint`

```python
EndPoint: Final[Vector] = Vector()
```

Returns the end point of this Bezier curve.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 1616.

## `Part.BezierCurve.isRational`

```python
def isRational(self) -> bool:
```

Returns false if the weights of all the poles of this Bezier curve are equal.

Evidence: public stub `Part/__init__.pyi` line(s) 1619.

## `Part.BezierCurve.isPeriodic`

```python
def isPeriodic(self) -> bool:
```

Returns false.

Evidence: public stub `Part/__init__.pyi` line(s) 1625.

## `Part.BezierCurve.isClosed`

```python
def isClosed(self) -> bool:
```

Returns true if the distance between the start point and end point of
this Bezier curve is less than or equal to gp::Resolution().

Evidence: public stub `Part/__init__.pyi` line(s) 1631.

## `Part.BezierCurve.increase`

```python
def increase(self, degree: int, /) -> None:
```

Increases the degree of this Bezier curve to degree.
As a result, the poles and weights tables are modified.

Evidence: public stub `Part/__init__.pyi` line(s) 1638.

## `Part.BezierCurve.insertPoleAfter`

```python
def insertPoleAfter(self, index: int, pole: Vector, weight: float=..., /) -> None:
```

Inserts a pole after the pole of the given index.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 1645.

## `Part.BezierCurve.insertPoleBefore`

```python
def insertPoleBefore(self, index: int, pole: Vector, weight: float=..., /) -> None:
```

Inserts a pole before the pole of the given index.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 1651.

## `Part.BezierCurve.removePole`

```python
def removePole(self, index: int, /) -> None:
```

Removes the pole at the given index from the table of poles of this Bezier curve.
If this Bezier curve is rational, it can become non-rational.

Evidence: public stub `Part/__init__.pyi` line(s) 1657.

## `Part.BezierCurve.segment`

```python
def segment(self, u1: float, u2: float, /) -> None:
```

Modifies this Bezier curve by segmenting it between u1 and u2.

Evidence: public stub `Part/__init__.pyi` line(s) 1664.

## `Part.BezierCurve.setPole`

```python
def setPole(self, index: int, pole: Vector, weight: float=..., /) -> None:
```

Set a pole of the Bezier curve.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 1670.

## `Part.BezierCurve.getPole`

```python
def getPole(self, index: int, /) -> Vector:
```

Get a pole of the Bezier curve.

Evidence: public stub `Part/__init__.pyi` line(s) 1676.

## `Part.BezierCurve.getPoles`

```python
def getPoles(self) -> List[Vector]:
```

Get all poles of the Bezier curve.

Evidence: public stub `Part/__init__.pyi` line(s) 1682.

## `Part.BezierCurve.setPoles`

```python
def setPoles(self, poles: List[Vector], /) -> None:
```

Set the poles of the Bezier curve.

Takes a list of 3D Base.Vector objects.

Evidence: public stub `Part/__init__.pyi` line(s) 1688.

## `Part.BezierCurve.setWeight`

```python
def setWeight(self, index: int, weight: float, /) -> None:
```

(index, weight) Set a weight of the Bezier curve.

Evidence: public stub `Part/__init__.pyi` line(s) 1696.

## `Part.BezierCurve.getWeight`

```python
def getWeight(self, index: int, /) -> float:
```

Get a weight of the Bezier curve.

Evidence: public stub `Part/__init__.pyi` line(s) 1702.

## `Part.BezierCurve.getWeights`

```python
def getWeights(self) -> List[float]:
```

Get all weights of the Bezier curve.

Evidence: public stub `Part/__init__.pyi` line(s) 1708.

## `Part.BezierCurve.getResolution`

```python
def getResolution(self, tolerance_3d: float, /) -> float:
```

Computes for this Bezier curve the parametric tolerance (UTolerance)
for a given 3D tolerance (tolerance_3d).
If f(t) is the equation of this Bezier curve, the parametric tolerance
ensures that:
|t1-t0| < UTolerance =""==> |f(t1)-f(t0)| < tolerance_3d

Evidence: public stub `Part/__init__.pyi` line(s) 1714.

## `Part.BezierCurve.interpolate`

```python
def interpolate(self, constraints: List[List], parameters: List[float]=..., /) -> None:
```

Interpolates a list of constraints.
Each constraint is a list of a point and some optional derivatives
An optional list of parameters can be passed. It must be of same size as constraint list.
Otherwise, a simple uniform parametrization is used.
Example :
bezier.interpolate([[pt1, deriv11, deriv12], [pt2,], [pt3, deriv31]], [0, 0.4, 1.0])

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 1724.

