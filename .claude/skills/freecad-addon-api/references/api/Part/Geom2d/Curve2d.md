# `Part.Geom2d.Curve2d`

[Module](index.md)

```python
class Curve2d(Geometry2d):
```

The abstract class Geom2dCurve is the root class of all curve objects.
Author: Werner Mayer (wmayer@users.sourceforge.net)
Licence: LGPL

Evidence: public stub `Part/Geom2d.pyi` line 739. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.Geom2d.Curve2d.Continuity`

```python
Continuity: Final[str] = ...
```

Returns the global continuity of the curve.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/Geom2d.pyi` line(s) 745.

## `Part.Geom2d.Curve2d.Closed`

```python
Closed: Final[bool] = ...
```

Returns true if the curve is closed.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/Geom2d.pyi` line(s) 747.

## `Part.Geom2d.Curve2d.Periodic`

```python
Periodic: Final[bool] = ...
```

Returns true if the curve is periodic.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/Geom2d.pyi` line(s) 749.

## `Part.Geom2d.Curve2d.FirstParameter`

```python
FirstParameter: Final[float] = ...
```

Returns the value of the first parameter.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/Geom2d.pyi` line(s) 751.

## `Part.Geom2d.Curve2d.LastParameter`

```python
LastParameter: Final[float] = ...
```

Returns the value of the last parameter.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/Geom2d.pyi` line(s) 753.

## `Part.Geom2d.Curve2d.reverse`

```python
def reverse(self) -> None:
```

Changes the direction of parametrization of the curve.

Evidence: public stub `Part/Geom2d.pyi` line(s) 756.

## `Part.Geom2d.Curve2d.toShape`

```python
@overload
def toShape(self) -> object:

@overload
def toShape(self, param1: float, param2: float, /) -> object:

@overload
def toShape(self, surface: GeometrySurface, /) -> object:

@overload
def toShape(self, surface: GeometrySurface, param1: float, param2: float, /) -> object:

@overload
def toShape(self, face: TopoShapeFace, /) -> object:

@overload
def toShape(self, face: TopoShapeFace, param1: float, param2: float, /) -> object:

def toShape(self, *args) -> object:
```

Return the shape for the geometry.

Evidence: public stub `Part/Geom2d.pyi` line(s) 763, 767, 771, 775, 779, 783, 786.

## `Part.Geom2d.Curve2d.discretize`

```python
@overload
def discretize(self, Number: int, First: float=None, Last: float=None) -> List[Vector]:

@overload
def discretize(self, QuasiNumber: int, First: float=None, Last: float=None) -> List[Vector]:

@overload
def discretize(self, Distance: float, First: float=None, Last: float=None) -> List[Vector]:

@overload
def discretize(self, Deflection: float, First: float=None, Last: float=None) -> List[Vector]:

@overload
def discretize(self, QuasiDeflection: float, First: float=None, Last: float=None) -> List[Vector]:

@overload
def discretize(self, Angular: float, Curvature: float, First: float=None, Last: float=None, Minimum: int=2) -> List[Vector]:

def discretize(self, **kwargs) -> List[Vector]:
```

Discretizes the curve and returns a list of points.
The function accepts keywords as argument:
discretize(Number=n) => gives a list of 'n' equidistant points.
discretize(QuasiNumber=n) => gives a list of 'n' quasi-equidistant points (is faster than the method above).
discretize(Distance=d) => gives a list of equidistant points with distance 'd'.
discretize(Deflection=d) => gives a list of points with a maximum deflection 'd' to the curve.
discretize(QuasiDeflection=d) => gives a list of points with a maximum deflection 'd' to the curve (faster).
discretize(Angular=a,Curvature=c,[Minimum=m]) => gives a list of points with an angular deflection of 'a'
    and a curvature deflection of 'c'. Optionally a minimum number of points
    can be set, which by default is set to 2.

Optionally you can set the keywords 'First' and 'Last' to define
    a sub-range of the parameter range of the curve.

If no keyword is given, then it depends on whether the argument is an int or float.
If it's an int then the behaviour is as if using the keyword 'Number',
if it's a float then the behaviour is as if using the keyword 'Distance'.

Example:

import Part
c=PartGeom2d.Circle2d()
c.Radius=5
p=c.discretize(Number=50,First=3.14)
s=Part.Compound([Part.Vertex(i) for i in p])
Part.show(s)


p=c.discretize(Angular=0.09,Curvature=0.01,Last=3.14,Minimum=100)
s=Part.Compound([Part.Vertex(i) for i in p])
Part.show(s)

Evidence: public stub `Part/Geom2d.pyi` line(s) 793, 797, 801, 805, 809, 813, 816.

## `Part.Geom2d.Curve2d.length`

```python
@overload
def length(self, /) -> float:

@overload
def length(self, uMin: float, /) -> float:

@overload
def length(self, uMin: float, uMax: float, /) -> float:

@overload
def length(self, uMin: float, uMax: float, Tol: float, /) -> float:

def length(self, *args: float) -> float:
```

Computes the length of a curve
length([uMin,uMax,Tol]) -> Float

Evidence: public stub `Part/Geom2d.pyi` line(s) 853, 857, 861, 865, 868.

## `Part.Geom2d.Curve2d.parameterAtDistance`

```python
@overload
def parameterAtDistance(self, abscissa: float, /) -> float:

@overload
def parameterAtDistance(self, abscissa: float, startingParameter: float, /) -> float:

def parameterAtDistance(self, *args: float) -> float:
```

Returns the parameter on the curve of a point at
the given distance from a starting parameter.
parameterAtDistance([abscissa, startingParameter]) -> Float

Evidence: public stub `Part/Geom2d.pyi` line(s) 876, 880, 883.

## `Part.Geom2d.Curve2d.value`

```python
def value(self, u: float, /) -> Vector:
```

Computes the point of parameter u on this curve

Evidence: public stub `Part/Geom2d.pyi` line(s) 891.

## `Part.Geom2d.Curve2d.tangent`

```python
def tangent(self, u: float, /) -> Vector:
```

Computes the tangent of parameter u on this curve

Evidence: public stub `Part/Geom2d.pyi` line(s) 897.

## `Part.Geom2d.Curve2d.parameter`

```python
def parameter(self, point: Vector, /) -> float:
```

Returns the parameter on the curve of the
nearest orthogonal projection of the point.

Evidence: public stub `Part/Geom2d.pyi` line(s) 903.

## `Part.Geom2d.Curve2d.normal`

```python
def normal(self, pos: float, /) -> Vector:
```

Vector = normal(pos) - Get the normal vector at the given parameter [First|Last] if defined.

Evidence: public stub `Part/Geom2d.pyi` line(s) 910.

## `Part.Geom2d.Curve2d.curvature`

```python
def curvature(self, pos: float, /) -> float:
```

Float = curvature(pos) - Get the curvature at the given parameter [First|Last] if defined.

Evidence: public stub `Part/Geom2d.pyi` line(s) 916.

## `Part.Geom2d.Curve2d.centerOfCurvature`

```python
def centerOfCurvature(self, pos: float, /) -> Vector:
```

Vector = centerOfCurvature(float pos) - Get the center of curvature at the given parameter [First|Last] if defined.

Evidence: public stub `Part/Geom2d.pyi` line(s) 922.

## `Part.Geom2d.Curve2d.intersectCC`

```python
def intersectCC(self, other: 'Curve2d', tolerance: float=..., /) -> List[Vector]:
```

Returns all intersection points between this curve and the given curve.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/Geom2d.pyi` line(s) 928.

## `Part.Geom2d.Curve2d.toBSpline`

```python
@overload
def toBSpline(self, /) -> BSplineCurve:

@overload
def toBSpline(self, First: float=..., Last: float=..., /) -> BSplineCurve:

def toBSpline(self, *args: float) -> BSplineCurve:
```

Converts a curve of any type (only part from First to Last)
toBSpline([Float=First, Float=Last]) -> B-Spline curve

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/Geom2d.pyi` line(s) 935, 939, 942.

## `Part.Geom2d.Curve2d.approximateBSpline`

```python
def approximateBSpline(self, Tolerance: float, MaxSegments: int, MaxDegree: int, Order: str='C2', /) -> BSplineCurve:
```

Approximates a curve of any type to a B-Spline curve
approximateBSpline(Tolerance, MaxSegments, MaxDegree, [Order='C2']) -> B-Spline curve

Evidence: public stub `Part/Geom2d.pyi` line(s) 949.

