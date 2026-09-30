# `FreeCAD.Base.Vector`

[Module](index.md)

```python
class Vector:
```

Base.Vector class.

This class represents a 3D float vector.
Useful to represent points in the 3D space.

The following constructors are supported:

Vector(x=0, y=0, z=0)
x : float
y : float
z : float

Vector(vector)
Copy constructor.
vector : Base.Vector

Vector(seq)
Define from a sequence of float.
seq : sequence of float.

Author: Juergen Riegel (FreeCAD@juergen-riegel.net)
Licence: LGPL

Evidence: public stub `FreeCAD/Base.pyi` line 1734. Inherited members are on the named base's reference; aliases keep their imported identity.

## `FreeCAD.Base.Vector.Length`

```python
Length: float = 0.0
```

Gets or sets the length of this vector.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1759.

## `FreeCAD.Base.Vector.x`

```python
x: float = 0.0
```

Gets or sets the X component of this vector.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1761.

## `FreeCAD.Base.Vector.y`

```python
y: float = 0.0
```

Gets or sets the Y component of this vector.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1763.

## `FreeCAD.Base.Vector.z`

```python
z: float = 0.0
```

Gets or sets the Z component of this vector.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1765.

## `FreeCAD.Base.Vector.__init__`

```python
@overload
def __init__(self, x: float=0, y: float=0, z: float=0) -> None:

@overload
def __init__(self, vector: 'Vector') -> None:

@overload
def __init__(self, seq: Sequence[float]) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1769, 1773, 1777.

## `FreeCAD.Base.Vector.__add__`

```python
def __add__(self, vector2: 'Vector', /) -> 'Vector':
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1780.

## `FreeCAD.Base.Vector.__sub__`

```python
def __sub__(self, vector2: 'Vector', /) -> 'Vector':
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1783.

## `FreeCAD.Base.Vector.__mul__`

```python
@overload
def __mul__(self, factor: float, /) -> 'Vector':

@overload
def __mul__(self, vector2: 'Vector', /) -> float:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1787, 1791.

## `FreeCAD.Base.Vector.__rmul__`

```python
def __rmul__(self, factor: float, /) -> 'Vector':
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1794.

## `FreeCAD.Base.Vector.__truediv__`

```python
def __truediv__(self, factor: float, /) -> 'Vector':
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1797.

## `FreeCAD.Base.Vector.__reduce__`

```python
def __reduce__(self) -> tuple:
```

Serialization of Vector objects.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1800.

## `FreeCAD.Base.Vector.add`

```python
def add(self, vector2: 'Vector', /) -> 'Vector':
```

Returns the sum of this vector and `vector2`.

vector2 : Base.Vector

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1806.

## `FreeCAD.Base.Vector.sub`

```python
def sub(self, vector2: 'Vector', /) -> 'Vector':
```

Returns the difference of this vector and `vector2`.

vector2 : Base.Vector

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1814.

## `FreeCAD.Base.Vector.negative`

```python
def negative(self) -> 'Vector':
```

Returns the negative (opposite) of this vector.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1822.

## `FreeCAD.Base.Vector.scale`

```python
def scale(self, x: float, y: float, z: float, /) -> 'Vector':
```

Scales in-place this vector by the given factor in each component.

x : float
    x-component factor scale.
y : float
    y-component factor scale.
z : float
    z-component factor scale.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1828.

## `FreeCAD.Base.Vector.multiply`

```python
def multiply(self, factor: float, /) -> 'Vector':
```

Multiplies in-place each component of this vector by a single factor.
Equivalent to scale(factor, factor, factor).

factor : float

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1841.

## `FreeCAD.Base.Vector.dot`

```python
def dot(self, vector2: 'Vector', /) -> float:
```

Returns the scalar product (dot product) between this vector and `vector2`.

vector2 : Base.Vector

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1850.

## `FreeCAD.Base.Vector.cross`

```python
def cross(self, vector2: 'Vector', /) -> 'Vector':
```

Returns the vector product (cross product) between this vector and `vector2`.

vector2 : Base.Vector

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1858.

## `FreeCAD.Base.Vector.isOnLineSegment`

```python
def isOnLineSegment(self, vector1: 'Vector', vector2: 'Vector', /) -> bool:
```

Checks if this vector is on the line segment generated by `vector1` and `vector2`.

vector1 : Base.Vector
vector2 : Base.Vector

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1866.

## `FreeCAD.Base.Vector.getAngle`

```python
def getAngle(self, vector2: 'Vector', /) -> float:
```

Returns the angle in radians between this vector and `vector2`.

vector2 : Base.Vector

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1875.

## `FreeCAD.Base.Vector.normalize`

```python
def normalize(self) -> 'Vector':
```

Normalizes in-place this vector to the length of 1.0.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1883.

## `FreeCAD.Base.Vector.isEqual`

```python
def isEqual(self, vector2: 'Vector', tol: float, /) -> bool:
```

Checks if the distance between the points represented by this vector
and `vector2` is less or equal to the given tolerance.

vector2 : Base.Vector
tol : float

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1889.

## `FreeCAD.Base.Vector.isParallel`

```python
def isParallel(self, vector2: 'Vector', tol: float, /) -> bool:
```

Checks if this vector and `vector2` are
parallel less or equal to the given tolerance.

vector2 : Base.Vector
tol : float

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1899.

## `FreeCAD.Base.Vector.isNormal`

```python
def isNormal(self, vector2: 'Vector', tol: float, /) -> bool:
```

Checks if this vector and `vector2` are
normal less or equal to the given tolerance.

vector2 : Base.Vector
tol : float

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1909.

## `FreeCAD.Base.Vector.projectToLine`

```python
def projectToLine(self, point: 'Vector', dir: 'Vector', /) -> 'Vector':
```

Projects `point` on a line that goes through the origin with the direction `dir`.
The result is the vector from `point` to the projected point.
The operation is equivalent to dir_n.cross(dir_n.cross(point)), where `dir_n` is
the vector `dir` normalized.
The method modifies this vector instance according to result and does not
depend on the vector itself.

point : Base.Vector
dir : Base.Vector

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1919.

## `FreeCAD.Base.Vector.projectToPlane`

```python
def projectToPlane(self, base: 'Vector', normal: 'Vector', /) -> 'Vector':
```

Projects in-place this vector on a plane defined by a base point
represented by `base` and a normal defined by `normal`.

base : Base.Vector
normal : Base.Vector

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1933.

## `FreeCAD.Base.Vector.distanceToPoint`

```python
def distanceToPoint(self, point2: 'Vector', /) -> float:
```

Returns the distance to another point represented by `point2`.

point2 : Base.Vector

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1943.

## `FreeCAD.Base.Vector.distanceToLine`

```python
def distanceToLine(self, base: 'Vector', dir: 'Vector', /) -> float:
```

Returns the distance between the point represented by this vector
and a line defined by a base point represented by `base` and a
direction `dir`.

base : Base.Vector
dir : Base.Vector

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1951.

## `FreeCAD.Base.Vector.distanceToLineSegment`

```python
def distanceToLineSegment(self, point1: 'Vector', point2: 'Vector', /) -> 'Vector':
```

Returns the vector between the point represented by this vector and the point
on the line segment with the shortest distance. The line segment is defined by
`point1` and `point2`.

point1 : Base.Vector
point2 : Base.Vector

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1962.

## `FreeCAD.Base.Vector.distanceToPlane`

```python
def distanceToPlane(self, base: 'Vector', normal: 'Vector', /) -> float:
```

Returns the distance between this vector and a plane defined by a
base point represented by `base` and a normal defined by `normal`.

base : Base.Vector
normal : Base.Vector

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1973.

