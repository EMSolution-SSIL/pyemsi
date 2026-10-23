# `FreeCAD.Base.Placement`

[Module](index.md)

```python
class Placement:
```

Base.Placement class.

A Placement defines an orientation (rotation) and a position (base) in 3D space.
It is used when no scaling or other distortion is needed.

The following constructors are supported:

Placement()
Empty constructor.

Placement(placement)
Copy constructor.
placement : Base.Placement

Placement(matrix)
Define from a 4D matrix consisting of rotation and translation.
matrix : Base.Matrix

Placement(base, rotation)
Define from position and rotation.
base : Base.Vector
rotation : Base.Rotation

Placement(base, rotation, center)
Define from position and rotation with center.
base : Base.Vector
rotation : Base.Rotation
center : Base.Vector

Placement(base, axis, angle)
define position and rotation.
base : Base.Vector
axis : Base.Vector
angle : float

Evidence: public stub `FreeCAD/Base.pyi` line 909. Inherited members are on the named base's reference; aliases keep their imported identity.

## `FreeCAD.Base.Placement.Base`

```python
@property
def Base(self) -> Vector:

@Base.setter
def Base(self, value: Vector | Sequence[float]) -> None:
```

Vector to the Base Position of the Placement.

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 948, 953.

## `FreeCAD.Base.Placement.Rotation`

```python
@property
def Rotation(self) -> 'FreeCAD.Base.Rotation':

@Rotation.setter
def Rotation(self, value: 'FreeCAD.Base.Rotation | tuple[float, float, float, float]') -> None:
```

Orientation of the placement expressed as rotation.

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 957, 962.

## `FreeCAD.Base.Placement.Matrix`

```python
Matrix: 'FreeCAD.Base.Matrix' = ...
```

Set/get matrix representation of the placement.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 964.

## `FreeCAD.Base.Placement.__init__`

```python
@overload
def __init__(self) -> None:

@overload
def __init__(self, placement: 'Placement') -> None:

@overload
def __init__(self, matrix: 'FreeCAD.Base.Matrix') -> None:

@overload
def __init__(self, base: Vector, rotation: 'FreeCAD.Base.Rotation') -> None:

@overload
def __init__(self, base: Vector, rotation: 'FreeCAD.Base.Rotation', center: Vector) -> None:

@overload
def __init__(self, base: Vector, axis: Vector, angle: float) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 968, 972, 976, 980, 984, 988.

## `FreeCAD.Base.Placement.__mul__`

```python
@overload
def __mul__(self, vector: Vector, /) -> Vector:

@overload
def __mul__(self, rotation: 'FreeCAD.Base.Rotation', /) -> 'Placement':

@overload
def __mul__(self, matrix: 'FreeCAD.Base.Matrix', /) -> 'FreeCAD.Base.Matrix':

@overload
def __mul__(self, placement: 'Placement', /) -> 'Placement':
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 992, 996, 1000, 1004.

## `FreeCAD.Base.Placement.copy`

```python
def copy(self) -> 'Placement':
```

Returns a copy of this placement.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1007.

## `FreeCAD.Base.Placement.move`

```python
def move(self, vector: Vector, /) -> None:
```

Move the placement along a vector.

vector : Base.Vector
    Vector by which to move the placement.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1013.

## `FreeCAD.Base.Placement.translate`

```python
def translate(self, vector: Vector, /) -> None:
```

Alias to move(), to be compatible with TopoShape.translate().

vector : Base.Vector
    Vector by which to move the placement.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1022.

## `FreeCAD.Base.Placement.rotate`

```python
@overload
def rotate(self, center: Sequence[float], axis: Sequence[float], angle: float, *, comp: bool=False) -> None:

@overload
def rotate(self, center: Vector, axis: Vector, angle: float, *, comp: bool=False) -> None:

def rotate(self, *args, **kwargs) -> None:
```

Rotate the current placement around center and axis with the given angle.
This method is compatible with TopoShape.rotate() if the (optional) keyword
argument comp is True (default=False).

center : Base.Vector, sequence of float
    Rotation center.
axis : Base.Vector, sequence of float
    Rotation axis.
angle : float
    Rotation angle in degrees.
comp : bool
    optional keyword only argument, if True (default=False),
behave like TopoShape.rotate() (i.e. the resulting placements are interchangeable).

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1032, 1036, 1053.

## `FreeCAD.Base.Placement.multiply`

```python
def multiply(self, placement: 'Placement', /) -> 'Placement':
```

Right multiply this placement with another placement.
Also available as `*` operator.

placement : Base.Placement
    Placement by which to multiply this placement.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1056.

## `FreeCAD.Base.Placement.multVec`

```python
def multVec(self, vector: Vector, /) -> Vector:
```

Compute the transformed vector using the placement.

vector : Base.Vector
    Vector to be transformed.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1066.

## `FreeCAD.Base.Placement.toMatrix`

```python
def toMatrix(self) -> 'FreeCAD.Base.Matrix':
```

Compute the matrix representation of the placement.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1075.

## `FreeCAD.Base.Placement.inverse`

```python
def inverse(self) -> 'Placement':
```

Compute the inverse placement.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1081.

## `FreeCAD.Base.Placement.pow`

```python
def pow(self, t: float, shorten: bool=True, /) -> 'Placement':
```

Raise this placement to real power using ScLERP interpolation.
Also available as `**` operator.

t : float
    Real power.
shorten : bool
    If True, ensures rotation quaternion is net positive to make
    the path shorter.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1087.

## `FreeCAD.Base.Placement.sclerp`

```python
def sclerp(self, placement2: 'Placement', t: float, shorten: bool=True, /) -> 'Placement':
```

Screw Linear Interpolation (ScLERP) between this placement and `placement2`.
Interpolation is a continuous motion along a helical path parametrized by `t`
made of equal transforms if discretized.
If quaternions of rotations of the two placements differ in sign, the interpolation
will take a long path.

placement2 : Base.Placement
t : float
    Parameter of helical path. t=0 returns this placement, t=1 returns
    `placement2`. t can also be outside of [0, 1] range for extrapolation.
shorten : bool
    If True, the signs are harmonized before interpolation and the interpolation
    takes the shorter path.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1100.

## `FreeCAD.Base.Placement.slerp`

```python
def slerp(self, placement2: 'Placement', t: float, /) -> 'Placement':
```

Spherical Linear Interpolation (SLERP) between this placement and `placement2`.
This function performs independent interpolation of rotation and movement.
Result of such interpolation might be not what application expects, thus this tool
might be considered for simple cases or for interpolating between small intervals.
For more complex cases you better use the advanced sclerp() function.

placement2 : Base.Placement
t : float
    Parameter of the path. t=0 returns this placement, t=1 returns `placement2`.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1118.

## `FreeCAD.Base.Placement.isIdentity`

```python
def isIdentity(self, tol: float=0.0, /) -> bool:
```

Returns True if the placement has no displacement and no rotation.
Matrix representation is the 4D identity matrix.
tol : float
    Tolerance used to check for identity.
    If tol is negative or zero, no tolerance is used.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1132.

## `FreeCAD.Base.Placement.isSame`

```python
def isSame(self, other: 'Placement', tol: float=0.0, /) -> bool:
```

Checks whether this and the given placement are the same.
The default tolerance is set to 0.0

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1142.

