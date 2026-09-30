# `Part.BSplineSurface`

[Module](index.md)

```python
class BSplineSurface(GeometrySurface):
```

Describes a B-Spline surface in 3D space

Author: Werner Mayer (wmayer@users.sourceforge.net)
Licence: LGPL
DeveloperDocu: Describes a B-Spline surface in 3D space

Evidence: public stub `Part/__init__.pyi` line 1006. Inherited members are on the named base's reference; aliases keep their imported identity.

[part 1](BSplineSurface.md) | [part 2](BSplineSurface-2.md)

## `Part.BSplineSurface.getResolution`

```python
def getResolution(self, tolerance_3d: float, /) -> Any:
```

Computes two tolerance values for this B-Spline surface, based on the
given tolerance in 3D space tolerance_3d. The tolerances computed are:
-- UTolerance in the u parametric direction and
-- VTolerance in the v parametric direction.

If f(u,v) is the equation of this B-Spline surface, UTolerance and
VTolerance guarantee that:
|u1 - u0| < UTolerance
|v1 - v0| < VTolerance
====> ||f(u1, v1) - f(u2, v2)|| < tolerance_3d

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Part/__init__.pyi` line(s) 1365.

## `Part.BSplineSurface.movePoint`

```python
def movePoint(self, u: float, v: float, pole: Any, u_index1: int, u_index2: int, v_index1: int, v_index2: int, /) -> Any:
```

Moves the point of parameters (u, v) of this B-Spline surface to pole.
u_index1, u_index2, v_index1 and v_index2 are the indexes in the poles
table of this B-Spline surface, of the first and last poles which
can be moved in each parametric direction.
The returned indexes UFirstIndex, ULastIndex, VFirstIndex and
VLastIndex are the indexes of the first and last poles effectively
modified in each parametric direction.
In the event of incompatibility between u_index1, u_index2, v_index1,
v_index2 and the values u and v:
-- no change is made to this B-Spline surface, and
-- UFirstIndex, ULastIndex, VFirstIndex and VLastIndex are set to
   null.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Part/__init__.pyi` line(s) 1380.

## `Part.BSplineSurface.setUNotPeriodic`

```python
def setUNotPeriodic(self) -> None:
```

Changes this B-Spline surface into a non-periodic one in the u parametric direction.
If this B-Spline surface is already non-periodic in the given parametric direction,
it is not modified.
If this B-Spline surface is periodic in the given parametric direction, the boundaries
of the surface are not given by the first and last rows (or columns) of poles (because
the multiplicity of the first knot and of the last knot in the given parametric direction
are not modified, nor are they equal to Degree+1, where Degree is the degree of this
B-Spline surface in the given parametric direction). Only the function Segment ensures
this property.

Note: the poles and knots tables are modified.

Evidence: public stub `Part/__init__.pyi` line(s) 1397.

## `Part.BSplineSurface.setVNotPeriodic`

```python
def setVNotPeriodic(self) -> None:
```

Changes this B-Spline surface into a non-periodic one in the v parametric direction.
If this B-Spline surface is already non-periodic in the given parametric direction,
it is not modified.
If this B-Spline surface is periodic in the given parametric direction, the boundaries
of the surface are not given by the first and last rows (or columns) of poles (because
the multiplicity of the first knot and of the last knot in the given parametric direction
are not modified, nor are they equal to Degree+1, where Degree is the degree of this
B-Spline surface in the given parametric direction). Only the function Segment ensures
this property.

Note: the poles and knots tables are modified.

Evidence: public stub `Part/__init__.pyi` line(s) 1413.

## `Part.BSplineSurface.setUPeriodic`

```python
def setUPeriodic(self) -> None:
```

Modifies this surface to be periodic in the u parametric direction.
To become periodic in a given parametric direction a surface must
be closed in that parametric direction, and the knot sequence relative
to that direction must be periodic.
To generate this periodic sequence of knots, the functions FirstUKnotIndex
and LastUKnotIndex are used to compute I1 and I2. These are the indexes,
in the knot array associated with the given parametric direction, of the
knots that correspond to the first and last parameters of this B-Spline
surface in the given parametric direction. Hence the period is:

Knots(I1) - Knots(I2)

As a result, the knots and poles tables are modified.

Evidence: public stub `Part/__init__.pyi` line(s) 1429.

## `Part.BSplineSurface.setVPeriodic`

```python
def setVPeriodic(self) -> None:
```

Modifies this surface to be periodic in the v parametric direction.
To become periodic in a given parametric direction a surface must
be closed in that parametric direction, and the knot sequence relative
to that direction must be periodic.
To generate this periodic sequence of knots, the functions FirstUKnotIndex
and LastUKnotIndex are used to compute I1 and I2. These are the indexes,
in the knot array associated with the given parametric direction, of the
knots that correspond to the first and last parameters of this B-Spline
surface in the given parametric direction. Hence the period is:

Knots(I1) - Knots(I2)

As a result, the knots and poles tables are modified.

Evidence: public stub `Part/__init__.pyi` line(s) 1447.

## `Part.BSplineSurface.setUOrigin`

```python
def setUOrigin(self, index: int, /) -> None:
```

Assigns the knot at the given index in the knots table
in the u parametric direction to be the origin of
this periodic B-Spline surface. As a consequence,
the knots and poles tables are modified.

Evidence: public stub `Part/__init__.pyi` line(s) 1465.

## `Part.BSplineSurface.setVOrigin`

```python
def setVOrigin(self, index: int, /) -> None:
```

Assigns the knot at the given index in the knots table
in the v parametric direction to be the origin of
this periodic B-Spline surface. As a consequence,
the knots and poles tables are modified.

Evidence: public stub `Part/__init__.pyi` line(s) 1474.

## `Part.BSplineSurface.getUMultiplicity`

```python
def getUMultiplicity(self, index: int, /) -> Any:
```

Returns, for this B-Spline surface, the multiplicity of
the knot of index index in the u parametric direction.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Part/__init__.pyi` line(s) 1483.

## `Part.BSplineSurface.getVMultiplicity`

```python
def getVMultiplicity(self, index: int, /) -> Any:
```

Returns, for this B-Spline surface, the multiplicity of
the knot of index index in the v parametric direction.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Part/__init__.pyi` line(s) 1490.

## `Part.BSplineSurface.getUMultiplicities`

```python
def getUMultiplicities(self) -> List[Any]:
```

Returns, for this B-Spline surface, the table of
multiplicities in the u parametric direction

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Part/__init__.pyi` line(s) 1497.

## `Part.BSplineSurface.getVMultiplicities`

```python
def getVMultiplicities(self) -> List[Any]:
```

Returns, for this B-Spline surface, the table of
multiplicities in the v parametric direction

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Part/__init__.pyi` line(s) 1504.

## `Part.BSplineSurface.exchangeUV`

```python
def exchangeUV(self) -> None:
```

Exchanges the u and v parametric directions on this B-Spline surface.
As a consequence:
-- the poles and weights tables are transposed,
-- the knots and multiplicities tables are exchanged,
-- degrees of continuity and rational, periodic and uniform
   characteristics are exchanged and
-- the orientation of the surface is reversed.

Evidence: public stub `Part/__init__.pyi` line(s) 1511.

## `Part.BSplineSurface.reparametrize`

```python
def reparametrize(self, u: int, v: int, tol: float=..., /) -> Any:
```

Returns a reparametrized copy of this surface

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 1523.

## `Part.BSplineSurface.approximate`

```python
def approximate(self, *, Points: Any, DegMin: int=..., DegMax: int=..., Continuity: int=..., Tolerance: float=..., X0: float=..., dX: float=..., Y0: float=..., dY: float=..., ParamType: str=..., LengthWeight: float=..., CurvatureWeight: float=..., TorsionWeight: float=...) -> None:
```

Replaces this B-Spline surface by approximating a set of points.
This method uses keywords :
- Points = 2Darray of points (or floats, in combination with X0, dX, Y0, dY)
- DegMin (int), DegMax (int)
- Continuity = 0,1 or 2 (for C0, C1, C2)
- Tolerance (float)
- X0, dX, Y0, dY (floats) with Points = 2Darray of floats
- ParamType = 'Uniform','Centripetal' or 'ChordLength'
- LengthWeight, CurvatureWeight, TorsionWeight (floats)
(with this smoothing algorithm, continuity C1 requires DegMax >= 3 and C2, DegMax >=5)

Possible combinations :
- approximate(Points, DegMin, DegMax, Continuity, Tolerance)
- approximate(Points, DegMin, DegMax, Continuity, Tolerance, X0, dX, Y0, dY)
With explicit keywords :
- approximate(Points, DegMin, DegMax, Continuity, Tolerance, ParamType)
- approximate(Points, DegMax, Continuity, Tolerance, LengthWeight, CurvatureWeight, TorsionWeight)

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 1529.

## `Part.BSplineSurface.interpolate`

```python
def interpolate(self, points: Any, x0: float=..., dx: float=..., y0: float=..., dy: float=..., /) -> None:
```

interpolate(points)
interpolate(points, x0, dx, y0, dy)

Replaces this B-Spline surface by interpolating a set of points.
The resulting surface is of degree 3 and continuity C2.
Arguments:
a 2 dimensional array of vectors, that the surface passes through
or
a 2 dimensional array of floats with the z values,
the x starting point x0 (float),
the x increment dx (float),
the y starting point y0 and increment dy

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 1551.

## `Part.BSplineSurface.buildFromPolesMultsKnots`

```python
def buildFromPolesMultsKnots(self, *, poles: List[List[Any]], umults: List[Any], vmults: List[Any], uknots: List[Any]=..., vknots: List[Any]=..., uperiodic: bool=..., vperiodic: bool=..., udegree: int=..., vdegree: int=..., weights: List[List[float]]=...) -> None:
```

Builds a B-Spline by a lists of Poles, Mults and Knots
arguments: poles (sequence of sequence of Base.Vector), umults, vmults, [uknots, vknots, uperiodic, vperiodic, udegree, vdegree, weights (sequence of sequence of float)]

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 1568.

## `Part.BSplineSurface.buildFromNSections`

```python
def buildFromNSections(self, control_curves: Any, ref_surf: bool=..., /) -> None:
```

Builds a B-Spline from a list of control curves

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 1575.

## `Part.BSplineSurface.scaleKnotsToBounds`

```python
def scaleKnotsToBounds(self, u0: float=..., u1: float=..., v0: float=..., v1: float=..., /) -> None:
```

Scales the U and V knots lists to fit the specified bounds.
The shape of the surface is not modified.
bspline_surf.scaleKnotsToBounds(u0, u1, v0, v1)
Default arguments are 0.0, 1.0, 0.0, 1.0

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 1581.

