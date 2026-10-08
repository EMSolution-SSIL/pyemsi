# `FreeCAD.Base.Rotation`

[Module](index.md)

```python
class Rotation:
```

Base.Rotation class.

A Rotation using a quaternion.

The following constructors are supported:

Rotation()
Empty constructor.

Rotation(rotation)
Copy constructor.

Rotation(Axis, Radian)
Rotation(Axis, Degree)
Define from an axis and an angle (in radians or degrees according to the keyword).
Axis : Base.Vector
Radian : float
Degree : float

Rotation(vector_start, vector_end)
Define from two vectors (rotation from/to vector).
vector_start : Base.Vector
vector_end : Base.Vector

Rotation(angle1, angle2, angle3)
Define from three floats (Euler angles) as yaw-pitch-roll in XY'Z'' convention.
angle1 : float
angle2 : float
angle3 : float

Rotation(seq, angle1, angle2, angle3)
Define from one string and three floats (Euler angles) as Euler rotation
of a given type. Call toEulerAngles() for supported sequence types.
seq : str
angle1 : float
angle2 : float
angle3 : float

Rotation(x, y, z, w)
Define from four floats (quaternion) where the quaternion is specified as:
q = xi+yj+zk+w, i.e. the last parameter is the real part.
x : float
y : float
z : float
w : float

Rotation(dir1, dir2, dir3, seq)
Define from three vectors that define rotated axes directions plus an optional
3-characher string of capital letters 'X', 'Y', 'Z' that sets the order of
importance of the axes (e.g., 'ZXY' means z direction is followed strictly,
x is used but corrected if necessary, y is ignored).
dir1 : Base.Vector
dir2 : Base.Vector
dir3 : Base.Vector
seq : str

Rotation(matrix)
Define from a matrix rotation in the 4D representation.
matrix : Base.Matrix

Rotation(*coef)
Define from 16 or 9 elements which represent the rotation in the 4D matrix
representation or in the 3D matrix representation, respectively.
coef : sequence of float

Author: Juergen Riegel (FreeCAD@juergen-riegel.net)
Licence: LGPL

Evidence: public stub `FreeCAD/Base.pyi` line 1339. Inherited members are on the named base's reference; aliases keep their imported identity.

## `FreeCAD.Base.Rotation.Q`

```python
Q: Tuple[float, ...] = ()
```

The rotation elements (as quaternion).

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1409.

## `FreeCAD.Base.Rotation.Axis`

```python
@property
def Axis(self) -> Vector:

@Axis.setter
def Axis(self, value: Vector | Sequence[float]) -> None:
```

The rotation axis of the quaternion.

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1413, 1418.

## `FreeCAD.Base.Rotation.RawAxis`

```python
RawAxis: Final[Vector] = ...
```

The rotation axis without normalization.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1420.

## `FreeCAD.Base.Rotation.Angle`

```python
Angle: float = 0.0
```

The rotation angle of the quaternion.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1422.

## `FreeCAD.Base.Rotation.__init__`

```python
@overload
def __init__(self) -> None:

@overload
def __init__(self, rotation: 'Rotation') -> None:

@overload
def __init__(self, axis: Vector, angle: float) -> None:

@overload
def __init__(self, vector_start: Vector, vector_end: Vector) -> None:

@overload
def __init__(self, angle1: float, angle2: float, angle3: float) -> None:

@overload
def __init__(self, seq: str, angle1: float, angle2: float, angle3: float) -> None:

@overload
def __init__(self, x: float, y: float, z: float, w: float) -> None:

@overload
def __init__(self, dir1: Vector, dir2: Vector, dir3: Vector, seq: str) -> None:

@overload
def __init__(self, matrix: Matrix) -> None:

@overload
def __init__(self, *coef: float) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1426, 1430, 1434, 1438, 1442, 1446, 1450, 1454, 1458, 1462.

## `FreeCAD.Base.Rotation.invert`

```python
def invert(self) -> None:
```

Sets the rotation to its inverse.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1465.

## `FreeCAD.Base.Rotation.inverted`

```python
def inverted(self) -> 'Rotation':
```

Returns the inverse of the rotation.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1471.

## `FreeCAD.Base.Rotation.isSame`

```python
def isSame(self, rotation: 'Rotation', tol: float=0, /) -> bool:
```

Checks if `rotation` perform the same transformation as this rotation.

rotation : Base.Rotation
tol : float
    Tolerance used to compare both rotations.
    If tol is negative or zero, no tolerance is used.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1477.

## `FreeCAD.Base.Rotation.multiply`

```python
def multiply(self, rotation: 'Rotation', /) -> 'Rotation':
```

Right multiply this rotation with another rotation.

rotation : Base.Rotation
    Rotation by which to multiply this rotation.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1488.

## `FreeCAD.Base.Rotation.__mul__`

```python
@overload
def __mul__(self, vector: Vector, /) -> Vector:

@overload
def __mul__(self, matrix: Matrix, /) -> Matrix:

@overload
def __mul__(self, placement: Placement, /) -> Placement:

@overload
def __mul__(self, rotation: Rotation, /) -> Rotation:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1498, 1502, 1506, 1510.

## `FreeCAD.Base.Rotation.multVec`

```python
def multVec(self, vector: Vector, /) -> Vector:
```

Compute the transformed vector using the rotation.

vector : Base.Vector
    Vector to be transformed.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1513.

## `FreeCAD.Base.Rotation.slerp`

```python
def slerp(self, rotation2: 'Rotation', t: float, /) -> 'Rotation':
```

Spherical Linear Interpolation (SLERP) of this rotation and `rotation2`.

t : float
    Parameter of the path. t=0 returns this rotation, t=1 returns `rotation2`.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1522.

## `FreeCAD.Base.Rotation.setYawPitchRoll`

```python
def setYawPitchRoll(self, angle1: float, angle2: float, angle3: float, /) -> None:
```

Set the Euler angles of this rotation as yaw-pitch-roll in XY'Z'' convention.

angle1 : float
    Angle around yaw axis in degrees.
angle2 : float
    Angle around pitch axis in degrees.
angle3 : float
    Angle around roll axis in degrees.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1531.

## `FreeCAD.Base.Rotation.getYawPitchRoll`

```python
def getYawPitchRoll(self) -> Tuple[float, float, float]:
```

Get the Euler angles of this rotation as yaw-pitch-roll in XY'Z'' convention.
The angles are given in degrees.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1544.

## `FreeCAD.Base.Rotation.setEulerAngles`

```python
def setEulerAngles(self, seq: str, angle1: float, angle2: float, angle3: float, /) -> None:
```

Set the Euler angles in a given sequence for this rotation.
The angles must be given in degrees.

seq : str
    Euler sequence name. All possible values given by toEulerAngles().
angle1 : float
angle2 : float
angle3 : float

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1551.

## `FreeCAD.Base.Rotation.toEulerAngles`

```python
def toEulerAngles(self, seq: str='', /) -> List[float]:
```

Get the Euler angles in a given sequence for this rotation.

seq : str
    Euler sequence name. If not given, the function returns
    all possible values of `seq`. Optional.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1564.

## `FreeCAD.Base.Rotation.toMatrix`

```python
def toMatrix(self) -> Matrix:
```

Convert the rotation to a 4D matrix representation.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1574.

## `FreeCAD.Base.Rotation.isNull`

```python
def isNull(self) -> bool:
```

Returns True if all values in the quaternion representation are zero.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1580.

## `FreeCAD.Base.Rotation.isIdentity`

```python
def isIdentity(self, tol: float=0, /) -> bool:
```

Returns True if the rotation equals the 4D identity matrix.
tol : float
    Tolerance used to check for identity.
    If tol is negative or zero, no tolerance is used.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1586.

