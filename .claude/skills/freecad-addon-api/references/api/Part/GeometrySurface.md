# `Part.GeometrySurface`

[Module](index.md)

```python
class GeometrySurface(Geometry):
```

The abstract class GeometrySurface is the root class of all surface objects.

Author: Werner Mayer (wmayer@users.sourceforge.net)
Licence: LGPL

Evidence: public stub `Part/__init__.pyi` line 2740. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.GeometrySurface.Continuity`

```python
Continuity: Final[str] = ''
```

Returns the global continuity of the surface.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 2747.

## `Part.GeometrySurface.Rotation`

```python
Rotation: Final[RotationPy] = ...
```

Returns a rotation object to describe the orientation for surface that supports it

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 2749.

## `Part.GeometrySurface.toShape`

```python
def toShape(self, u1: float=..., u2: float=..., v1: float=..., v2: float=..., /) -> Any:
```

Return the shape for the geometry, optionally within the given parametric bounds.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 2752.

## `Part.GeometrySurface.toShell`

```python
def toShell(self, Bounds: tuple=..., Segment: bool=...) -> Any:
```

Make a shell of the surface.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 2758.

## `Part.GeometrySurface.getD0`

```python
def getD0(self, u: float, v: float, /) -> Vector:
```

Returns the point at the given parameters (u, v)

Evidence: public stub `Part/__init__.pyi` line(s) 2764.

## `Part.GeometrySurface.getDN`

```python
def getDN(self, u: float, v: float, nu: int, nv: int, /) -> Any:
```

Returns the derivative of order (nu, nv) at the given parameters (u, v)

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Part/__init__.pyi` line(s) 2770.

## `Part.GeometrySurface.value`

```python
def value(self, u: float, v: float, /) -> Vector:
```

value(u,v) -> Point
Computes the point of parameter (u,v) on this surface

Evidence: public stub `Part/__init__.pyi` line(s) 2776.

## `Part.GeometrySurface.tangent`

```python
def tangent(self, u: float, v: float, /) -> Tuple[Vector, Vector]:
```

tangent(u,v) -> (Vector,Vector)
Computes the tangent of parameter (u,v) on this geometry

Evidence: public stub `Part/__init__.pyi` line(s) 2783.

## `Part.GeometrySurface.normal`

```python
def normal(self, u: float, v: float, /) -> Vector:
```

normal(u,v) -> Vector
Computes the normal of parameter (u,v) on this geometry

Evidence: public stub `Part/__init__.pyi` line(s) 2790.

## `Part.GeometrySurface.projectPoint`

```python
@overload
def projectPoint(self, Point: Vector, Method: Literal['NearestPoint']='NearestPoint') -> Vector:

@overload
def projectPoint(self, Point: Vector, Method: Literal['LowerDistance']) -> float:

@overload
def projectPoint(self, Point: Vector, Method: Literal['LowerDistanceParameters']) -> Tuple[float, float]:

@overload
def projectPoint(self, Point: Vector, Method: Literal['Distance']) -> List[float]:

@overload
def projectPoint(self, Point: Vector, Method: Literal['Parameters']) -> List[Tuple[float, float]]:

@overload
def projectPoint(self, Point: Vector, Method: Literal['Point']) -> List[Vector]:

def projectPoint(self, Point: Vector, Method: str=...) -> Any:
```

Computes the projection of a point on the surface

projectPoint(Point=Vector,[Method="NearestPoint"])
projectPoint(Vector,"NearestPoint") -> Vector
projectPoint(Vector,"LowerDistance") -> float
projectPoint(Vector,"LowerDistanceParameters") -> tuple of floats (u,v)
projectPoint(Vector,"Distance") -> list of floats
projectPoint(Vector,"Parameters") -> list of tuples of floats
projectPoint(Vector,"Point") -> list of points

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 2798, 2802, 2806, 2810, 2814, 2818, 2821.

## `Part.GeometrySurface.isUmbillic`

```python
def isUmbillic(self, u: float, v: float, /) -> bool:
```

isUmbillic(u,v) -> bool
Check if the geometry on parameter is an umbillic point,
i.e. maximum and minimum curvature are equal.

Evidence: public stub `Part/__init__.pyi` line(s) 2835.

## `Part.GeometrySurface.curvature`

```python
def curvature(self, u: float, v: float, type: str, /) -> float:
```

curvature(u,v,type) -> float
The value of type must be one of this: Max, Min, Mean or Gauss
Computes the curvature of parameter (u,v) on this geometry

Evidence: public stub `Part/__init__.pyi` line(s) 2843.

## `Part.GeometrySurface.curvatureDirections`

```python
def curvatureDirections(self, u: float, v: float, /) -> Tuple[Vector, Vector]:
```

curvatureDirections(u,v) -> (Vector,Vector)
Computes the directions of maximum and minimum curvature
of parameter (u,v) on this geometry.
The first vector corresponds to the maximum curvature,
the second vector corresponds to the minimum curvature.

Evidence: public stub `Part/__init__.pyi` line(s) 2851.

## `Part.GeometrySurface.bounds`

```python
def bounds(self) -> Tuple[float, float, float, float]:
```

Returns the parametric bounds (U1, U2, V1, V2) of this trimmed surface.

Evidence: public stub `Part/__init__.pyi` line(s) 2861.

## `Part.GeometrySurface.isPlanar`

```python
def isPlanar(self, tolerance: float=0.0, /) -> bool:
```

isPlanar([float]) -> Bool
Checks if the surface is planar within a certain tolerance.

Evidence: public stub `Part/__init__.pyi` line(s) 2867.

## `Part.GeometrySurface.uIso`

```python
def uIso(self, u: float, /) -> Union[Curve, Line]:
```

Builds the U isoparametric curve

Evidence: public stub `Part/__init__.pyi` line(s) 2874.

## `Part.GeometrySurface.vIso`

```python
def vIso(self, v: float, /) -> Union[Curve, Line]:
```

Builds the V isoparametric curve

Evidence: public stub `Part/__init__.pyi` line(s) 2880.

## `Part.GeometrySurface.isUPeriodic`

```python
def isUPeriodic(self) -> bool:
```

Returns true if this patch is periodic in the given parametric direction.

Evidence: public stub `Part/__init__.pyi` line(s) 2886.

## `Part.GeometrySurface.isVPeriodic`

```python
def isVPeriodic(self) -> bool:
```

Returns true if this patch is periodic in the given parametric direction.

Evidence: public stub `Part/__init__.pyi` line(s) 2892.

## `Part.GeometrySurface.isUClosed`

```python
def isUClosed(self) -> bool:
```

Checks if this surface is closed in the u parametric direction.

Evidence: public stub `Part/__init__.pyi` line(s) 2898.

## `Part.GeometrySurface.isVClosed`

```python
def isVClosed(self) -> bool:
```

Checks if this surface is closed in the v parametric direction.

Evidence: public stub `Part/__init__.pyi` line(s) 2904.

## `Part.GeometrySurface.UPeriod`

```python
def UPeriod(self) -> float:
```

Returns the period of this patch in the u parametric direction.

Evidence: public stub `Part/__init__.pyi` line(s) 2910.

## `Part.GeometrySurface.VPeriod`

```python
def VPeriod(self) -> float:
```

Returns the period of this patch in the v parametric direction.

Evidence: public stub `Part/__init__.pyi` line(s) 2916.

## `Part.GeometrySurface.parameter`

```python
def parameter(self, point: Vector, precision: float=..., /) -> float:
```

Returns the parameter on the curve
of the nearest orthogonal projection of the point.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 2922.

## `Part.GeometrySurface.toBSpline`

```python
@overload
def toBSpline(self, Tol3d: float=1e-07, UContinuity: Literal['C0', 'G0', 'G1', 'C1', 'G2', 'C3', 'CN']='C1', VContinuity: Literal['C0', 'G0', 'G1', 'C1', 'G2', 'C3', 'CN']='C1', MaxDegreeU: int=25, MaxDegreeV: int=25, MaxSegments: int=1000, PrecisCode: int=0) -> Any:

def toBSpline(self, Tol3d: float=1e-07, UContinuity: str='C1', VContinuity: str='C1', MaxDegreeU: int=25, MaxDegreeV: int=25, MaxSegments: int=1000, PrecisCode: int=0) -> Any:
```

Returns a B-Spline representation of this surface.
The optional arguments are:
* tolerance (default=1e-7)
* continuity in u (as string e.g. C0, G0, G1, C1, G2, C3, CN) (default='C1')
* continuity in v (as string e.g. C0, G0, G1, C1, G2, C3, CN) (default='C1')
* maximum degree in u (default=25)
* maximum degree in v (default=25)
* maximum number of segments (default=1000)
* precision code (default=0)
Will raise an exception if surface is infinite in U or V (like planes, cones or cylinders)

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Part/__init__.pyi` line(s) 2930, 2933.

## `Part.GeometrySurface.intersect`

```python
def intersect(self, other: object, precision: float=..., /) -> Any:
```

Returns all intersection points/curves between the surface and the curve/surface.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 2948.

## `Part.GeometrySurface.intersectSS`

```python
def intersectSS(self, second_surface: Any, precision: float=..., /) -> Any:
```

Returns all intersection curves of this surface and the given surface.
The required arguments are:
* second_surface
* precision (optional, default=0)

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 2954.

