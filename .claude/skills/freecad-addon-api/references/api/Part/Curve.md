# `Part.Curve`

[Module](index.md)

```python
class Curve(Geometry):
```

The abstract class GeometryCurve is the root class of all curve objects.

Author: Werner Mayer (wmayer@users.sourceforge.net)
Licence: LGPL

Evidence: public stub `Part/__init__.pyi` line 2362. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.Curve.Continuity`

```python
Continuity: Final[str] = ''
```

Returns the global continuity of the curve.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 2369.

## `Part.Curve.FirstParameter`

```python
FirstParameter: Final[float] = 0.0
```

Returns the value of the first parameter.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 2371.

## `Part.Curve.LastParameter`

```python
LastParameter: Final[float] = 0.0
```

Returns the value of the last parameter.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 2373.

## `Part.Curve.Rotation`

```python
Rotation: Final[RotationPy] = ...
```

Returns a rotation object to describe the orientation for curve that supports it

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 2375.

## `Part.Curve.toShape`

```python
def toShape(self, u: float=..., v: float=..., /) -> Shape:
```

Return the shape for the geometry, optionally within the parameter range [u, v].

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 2378.

## `Part.Curve.discretize`

```python
@overload
def discretize(self, Number: int, First: Optional[float]=None, Last: Optional[float]=None) -> List[Vector]:

@overload
def discretize(self, QuasiNumber: int, First: Optional[float]=None, Last: Optional[float]=None) -> List[Vector]:

@overload
def discretize(self, Distance: float, First: Optional[float]=None, Last: Optional[float]=None) -> List[Vector]:

@overload
def discretize(self, Deflection: float, First: Optional[float]=None, Last: Optional[float]=None) -> List[Vector]:

@overload
def discretize(self, QuasiDeflection: float, First: Optional[float]=None, Last: Optional[float]=None) -> List[Vector]:

@overload
def discretize(self, Angular: float, Curvature: float, First: Optional[float]=None, Last: Optional[float]=None, Minimum: int=2) -> List[Vector]:

def discretize(self, **kwargs) -> List[Vector]:
```

Discretizes the curve and returns a list of points.

Discretizes the curve and returns a list of quasi equidistant points.

Discretizes the curve and returns a list of equidistant points with distance 'd'.

Discretizes the curve and returns a list of points with a maximum deflection 'd' to the curve.

Discretizes the curve and returns a list of points with a maximum deflection 'd' to the curve (faster).

Discretizes the curve and returns a list of points with an angular deflection of 'a' and a curvature deflection of 'c'.
Optionally a minimum number of points can be set.

Discretizes the curve and returns a list of points.

The function accepts keywords as argument:

discretize(Number=n) => gives a list of 'n' equidistant points
discretize(QuasiNumber=n) => gives a list of 'n' quasi equidistant points (is faster than the method above)
discretize(Distance=d) => gives a list of equidistant points with distance 'd'
discretize(Deflection=d) => gives a list of points with a maximum deflection 'd' to the curve
discretize(QuasiDeflection=d) => gives a list of points with a maximum deflection 'd' to the curve (faster)
discretize(Angular=a,Curvature=c,[Minimum=m]) => gives a list of points with an angular deflection of 'a'
                                    and a curvature deflection of 'c'. Optionally a minimum number of points
                                    can be set which by default is set to 2.

Optionally you can set the keywords 'First' and 'Last' to define a sub-range of the parameter range
of the curve.

If no keyword is given then it depends on whether the argument is an int or float.
If it's an int then the behaviour is as if using the keyword 'Number', if it's float
then the behaviour is as if using the keyword 'Distance'.

Example:

import Part
c=Part.Circle()
c.Radius=5
p=c.discretize(Number=50,First=3.14)
s=Part.Compound([Part.Vertex(i) for i in p])
Part.show(s)


p=c.discretize(Angular=0.09,Curvature=0.01,Last=3.14,Minimum=100)
s=Part.Compound([Part.Vertex(i) for i in p])
Part.show(s)

Evidence: public stub `Part/__init__.pyi` line(s) 2385, 2392, 2399, 2406, 2413, 2420, 2427.

## `Part.Curve.getD0`

```python
def getD0(self, parameter: float, /) -> Vector:
```

Returns the point of given parameter

Evidence: public stub `Part/__init__.pyi` line(s) 2465.

## `Part.Curve.getD1`

```python
def getD1(self, parameter: float, /) -> Vector:
```

Returns the point and first derivative of given parameter

Evidence: public stub `Part/__init__.pyi` line(s) 2471.

## `Part.Curve.getD2`

```python
def getD2(self, parameter: float, /) -> Vector:
```

Returns the point, first and second derivatives

Evidence: public stub `Part/__init__.pyi` line(s) 2477.

## `Part.Curve.getD3`

```python
def getD3(self, parameter: float, /) -> Vector:
```

Returns the point, first, second and third derivatives

Evidence: public stub `Part/__init__.pyi` line(s) 2483.

## `Part.Curve.getDN`

```python
def getDN(self, parameter: float, n: int, /) -> Vector:
```

Returns the n-th derivative

Evidence: public stub `Part/__init__.pyi` line(s) 2489.

## `Part.Curve.length`

```python
def length(self, u_min: float=..., u_max: float=..., tol: float=..., /) -> float:
```

Computes the length of a curve
length(u_min, u_max, tol) -> float

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 2495.

## `Part.Curve.parameterAtDistance`

```python
def parameterAtDistance(self, abscissa: float, starting_parameter: float=..., /) -> float:
```

Returns the parameter on the curve of a point at the given distance from a starting parameter.
parameterAtDistance(abscissa, starting_parameter) -> float

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 2502.

## `Part.Curve.value`

```python
def value(self, u: float, /) -> Vector:
```

Computes the point of parameter u on this curve

Evidence: public stub `Part/__init__.pyi` line(s) 2509.

## `Part.Curve.tangent`

```python
def tangent(self, u: float, /) -> Vector:
```

Computes the tangent of parameter u on this curve

Evidence: public stub `Part/__init__.pyi` line(s) 2515.

## `Part.Curve.makeRuledSurface`

```python
def makeRuledSurface(self, other_curve: 'GeometryCurve', /) -> object:
```

Make a ruled surface of this and the given curves

Evidence: public stub `Part/__init__.pyi` line(s) 2521.

## `Part.Curve.intersect2d`

```python
def intersect2d(self, other_curve: 'GeometryCurve', plane: Plane, /) -> List[Vector]:
```

Get intersection points with another curve lying on a plane.

Evidence: public stub `Part/__init__.pyi` line(s) 2527.

## `Part.Curve.continuityWith`

```python
def continuityWith(self, other_curve: 'GeometryCurve', u1: float=..., u2: float=..., rev1: bool=..., rev2: bool=..., tl: float=..., ta: float=..., /) -> str:
```

Computes the continuity of two curves

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 2533.

## `Part.Curve.parameter`

```python
def parameter(self, point: Vector, /) -> float:
```

Returns the parameter on the curve of the nearest orthogonal projection of the point.

Evidence: public stub `Part/__init__.pyi` line(s) 2539.

## `Part.Curve.normal`

```python
def normal(self, pos: float, /) -> Vector:
```

Vector = normal(pos) - Get the normal vector at the given parameter [First|Last] if defined

Evidence: public stub `Part/__init__.pyi` line(s) 2545.

## `Part.Curve.projectPoint`

```python
@overload
def projectPoint(self, Point: Vector, Method: str='NearestPoint') -> Vector:

@overload
def projectPoint(self, Point: Vector, Method: str='LowerDistance') -> float:

@overload
def projectPoint(self, Point: Vector, Method: str='LowerDistanceParameter') -> float:

@overload
def projectPoint(self, Point: Vector, Method: str='Distance') -> List[float]:

@overload
def projectPoint(self, Point: Vector, Method: str='Parameter') -> List[float]:

@overload
def projectPoint(self, Point: Vector, Method: str='Point') -> List[Vector]:

def projectPoint(self, **kwargs) -> Union[Vector, float, List[float], List[Vector]]:
```

projectPoint(Point=Vector, Method="NearestPoint") -> Vector

projectPoint(Vector, "LowerDistance") -> float.

projectPoint(Vector, "LowerDistanceParameter") -> float.

projectPoint(Vector, "Distance") -> list of floats.

projectPoint(Vector, "Parameter") -> list of floats.

projectPoint(Vector, "Point") -> list of points.

Computes the projection of a point on the curve

projectPoint(Point=Vector,[Method="NearestPoint"])
projectPoint(Vector,"NearestPoint") -> Vector
projectPoint(Vector,"LowerDistance") -> float
projectPoint(Vector,"LowerDistanceParameter") -> float
projectPoint(Vector,"Distance") -> list of floats
projectPoint(Vector,"Parameter") -> list of floats
projectPoint(Vector,"Point") -> list of points

Evidence: public stub `Part/__init__.pyi` line(s) 2552, 2559, 2566, 2573, 2580, 2587, 2593.

## `Part.Curve.curvature`

```python
def curvature(self, pos: float, /) -> float:
```

Float = curvature(pos) - Get the curvature at the given parameter [First|Last] if defined

Evidence: public stub `Part/__init__.pyi` line(s) 2607.

## `Part.Curve.centerOfCurvature`

```python
def centerOfCurvature(self, pos: float, /) -> Vector:
```

Vector = centerOfCurvature(float pos) - Get the center of curvature at the given parameter [First|Last] if defined

Evidence: public stub `Part/__init__.pyi` line(s) 2613.

## `Part.Curve.intersect`

```python
def intersect(self, curve_or_surface: object, precision: float=..., /) -> object:
```

Returns all intersection points and curve segments between the curve and the curve/surface.

arguments: curve/surface (for the intersection), precision (float)

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 2619.

## `Part.Curve.intersectCS`

```python
def intersectCS(self, surface: object, precision: float=..., /) -> object:
```

Returns all intersection points and curve segments between the curve and the surface.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 2627.

## `Part.Curve.intersectCC`

```python
def intersectCC(self, other_curve: 'GeometryCurve', precision: float=..., /) -> List[Vector]:
```

Returns all intersection points between this curve and the given curve.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 2633.

## `Part.Curve.toBSpline`

```python
def toBSpline(self, first: float=..., last: float=..., /) -> BSplineCurve:
```

Converts a curve of any type (only part from First to Last) to BSpline curve.
toBSpline(first, last) -> BSplineCurve

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 2639.

## `Part.Curve.toNurbs`

```python
def toNurbs(self, first: float=..., last: float=..., /) -> BSplineCurve:
```

Converts a curve of any type (only part from First to Last) to NURBS curve.
toNurbs(first, last) -> NurbsCurve

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 2646.

## `Part.Curve.trim`

```python
def trim(self, first: float=..., last: float=..., /) -> TrimmedCurve:
```

Returns a trimmed curve defined in the given parameter range.
trim(first, last) -> TrimmedCurve

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 2653.

## `Part.Curve.approximateBSpline`

```python
def approximateBSpline(self, tolerance: float, max_segments: int, max_degree: int, order: str=..., /) -> BSplineCurve:
```

Approximates a curve of any type to a B-Spline curve.
approximateBSpline(tolerance, max_segments, max_degree, [order='C2']) -> BSplineCurve

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 2660.

## `Part.Curve.reverse`

```python
def reverse(self) -> None:
```

Changes the direction of parametrization of the curve.

Evidence: public stub `Part/__init__.pyi` line(s) 2667.

## `Part.Curve.reversedParameter`

```python
def reversedParameter(self, u: float, /) -> float:
```

Returns the parameter on the reversed curve for the point of parameter u on this curve.

Evidence: public stub `Part/__init__.pyi` line(s) 2673.

## `Part.Curve.isPeriodic`

```python
def isPeriodic(self) -> bool:
```

Returns true if this curve is periodic.

Evidence: public stub `Part/__init__.pyi` line(s) 2679.

## `Part.Curve.period`

```python
def period(self) -> float:
```

Returns the period of this curve or raises an exception if it is not periodic.

Evidence: public stub `Part/__init__.pyi` line(s) 2685.

## `Part.Curve.isClosed`

```python
def isClosed(self) -> bool:
```

Returns true if the curve is closed.

Evidence: public stub `Part/__init__.pyi` line(s) 2691.

