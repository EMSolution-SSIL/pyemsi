# `Part.Geom2d.BezierCurve2d`

[Module](index.md)

```python
class BezierCurve2d(Curve2d):
```

Describes a rational or non-rational Bezier curve in 2d space:
    -- a non-rational Bezier curve is defined by a table of poles (also called control points)
    -- a rational Bezier curve is defined by a table of poles with varying weights

Author: Werner Mayer (wmayer@users.sourceforge.net)
Licence: LGPL

Evidence: public stub `Part/Geom2d.pyi` line 522. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.Geom2d.BezierCurve2d.Degree`

```python
Degree: Final[int] = ...
```

Returns the polynomial degree of this Bezier curve, which is equal to the number of poles minus 1.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/Geom2d.pyi` line(s) 531.

## `Part.Geom2d.BezierCurve2d.MaxDegree`

```python
MaxDegree: Final[int] = ...
```

Returns the value of the maximum polynomial degree of any Bezier curve curve. This value is 25.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/Geom2d.pyi` line(s) 533.

## `Part.Geom2d.BezierCurve2d.NbPoles`

```python
NbPoles: Final[int] = ...
```

Returns the number of poles of this Bezier curve.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/Geom2d.pyi` line(s) 535.

## `Part.Geom2d.BezierCurve2d.StartPoint`

```python
StartPoint: Final[object] = ...
```

Returns the start point of this Bezier curve.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/Geom2d.pyi` line(s) 537.

## `Part.Geom2d.BezierCurve2d.EndPoint`

```python
EndPoint: Final[object] = ...
```

Returns the end point of this Bezier curve.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/Geom2d.pyi` line(s) 539.

## `Part.Geom2d.BezierCurve2d.isRational`

```python
def isRational(self) -> bool:
```

Returns false if the weights of all the poles of this Bezier curve are equal.

Evidence: public stub `Part/Geom2d.pyi` line(s) 542.

## `Part.Geom2d.BezierCurve2d.isPeriodic`

```python
def isPeriodic(self) -> bool:
```

Returns false.

Evidence: public stub `Part/Geom2d.pyi` line(s) 548.

## `Part.Geom2d.BezierCurve2d.isClosed`

```python
def isClosed(self) -> bool:
```

Returns true if the distance between the start point and end point of this Bezier curve
is less than or equal to gp::Resolution().

Evidence: public stub `Part/Geom2d.pyi` line(s) 554.

## `Part.Geom2d.BezierCurve2d.increase`

```python
def increase(self, Degree: int, /) -> None:
```

increase(Int=Degree)
Increases the degree of this Bezier curve to Degree.
As a result, the poles and weights tables are modified.

Evidence: public stub `Part/Geom2d.pyi` line(s) 561.

## `Part.Geom2d.BezierCurve2d.insertPoleAfter`

```python
def insertPoleAfter(self, index: int, pole: Any, weight: float=..., /) -> None:
```

Inserts after the pole of index.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/Geom2d.pyi` line(s) 569.

## `Part.Geom2d.BezierCurve2d.insertPoleBefore`

```python
def insertPoleBefore(self, index: int, pole: Any, weight: float=..., /) -> None:
```

Inserts before the pole of index.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/Geom2d.pyi` line(s) 575.

## `Part.Geom2d.BezierCurve2d.removePole`

```python
def removePole(self, index: int, /) -> None:
```

Removes the pole of index Index from the table of poles of this Bezier curve.
If this Bezier curve is rational, it can become non-rational.

Evidence: public stub `Part/Geom2d.pyi` line(s) 581.

## `Part.Geom2d.BezierCurve2d.segment`

```python
def segment(self, u1: float, u2: float, /) -> None:
```

Modifies this Bezier curve by segmenting it.

Evidence: public stub `Part/Geom2d.pyi` line(s) 588.

## `Part.Geom2d.BezierCurve2d.setPole`

```python
def setPole(self, index: int, pole: object, weight: float=..., /) -> None:
```

Set a pole of the Bezier curve.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/Geom2d.pyi` line(s) 594.

## `Part.Geom2d.BezierCurve2d.getPole`

```python
def getPole(self, index: int, /) -> object:
```

Get a pole of the Bezier curve.

Evidence: public stub `Part/Geom2d.pyi` line(s) 600.

## `Part.Geom2d.BezierCurve2d.getPoles`

```python
def getPoles(self) -> List[object]:
```

Get all poles of the Bezier curve.

Evidence: public stub `Part/Geom2d.pyi` line(s) 606.

## `Part.Geom2d.BezierCurve2d.setPoles`

```python
def setPoles(self, poles: List[object], /) -> None:
```

Set the poles of the Bezier curve.

Evidence: public stub `Part/Geom2d.pyi` line(s) 612.

## `Part.Geom2d.BezierCurve2d.setWeight`

```python
def setWeight(self, index: int, weight: float, /) -> None:
```

Set a weight of the Bezier curve.

Evidence: public stub `Part/Geom2d.pyi` line(s) 618.

## `Part.Geom2d.BezierCurve2d.getWeight`

```python
def getWeight(self, index: int, /) -> float:
```

Get a weight of the Bezier curve.

Evidence: public stub `Part/Geom2d.pyi` line(s) 624.

## `Part.Geom2d.BezierCurve2d.getWeights`

```python
def getWeights(self) -> List[float]:
```

Get all weights of the Bezier curve.

Evidence: public stub `Part/Geom2d.pyi` line(s) 630.

## `Part.Geom2d.BezierCurve2d.getResolution`

```python
def getResolution(self, Tolerance3D: float, /) -> float:
```

Computes for this Bezier curve the parametric tolerance (UTolerance)
for a given 3D tolerance (Tolerance3D).
If f(t) is the equation of this Bezier curve,
the parametric tolerance ensures that:
|t1-t0| < UTolerance =""==> |f(t1)-f(t0)| < Tolerance3D

Evidence: public stub `Part/Geom2d.pyi` line(s) 636.

