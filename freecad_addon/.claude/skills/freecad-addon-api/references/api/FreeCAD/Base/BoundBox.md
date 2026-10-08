# `FreeCAD.Base.BoundBox`

[Module](index.md)

```python
class BoundBox:
```

Base.BoundBox class.

This class represents a bounding box.
A bounding box is a rectangular cuboid which is a way to describe outer
boundaries and is obtained from a lot of 3D types.
It is often used to check if a 3D entity lies in the range of another object.
Checking for bounding interference first can save a lot of computing time!
An invalid BoundBox is represented by inconsistent values at each direction:
The maximum float value of the system at the minimum coordinates, and the
opposite value at the maximum coordinates.

The following constructors are supported:

BoundBox()
Empty constructor. Returns an invalid BoundBox.

BoundBox(boundBox)
Copy constructor.
boundBox : Base.BoundBox

BoundBox(xMin, yMin=0, zMin=0, xMax=0, yMax=0, zMax=0)
Define from the minimum and maximum values at each direction.
xMin : float
    Minimum value at x-coordinate.
yMin : float
    Minimum value at y-coordinate.
zMin : float
    Minimum value at z-coordinate.
xMax : float
    Maximum value at x-coordinate.
yMax : float
    Maximum value at y-coordinate.
zMax : float
    Maximum value at z-coordinate.

App.BoundBox(min, max)
Define from two containers representing the minimum and maximum values of the
coordinates in each direction.
min : Base.Vector, tuple
    Minimum values of the coordinates.
max : Base.Vector, tuple
    Maximum values of the coordinates.

Author: Juergen Riegel (FreeCAD@juergen-riegel.net)
Licence: LGPL

Evidence: public stub `FreeCAD/Base.pyi` line 117. Inherited members are on the named base's reference; aliases keep their imported identity.

## `FreeCAD.Base.BoundBox.Center`

```python
Center: Final[Any] = ...
```

Center point of the bounding box.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 165.

## `FreeCAD.Base.BoundBox.XMax`

```python
XMax: float = 0.0
```

The maximum x boundary position.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 167.

## `FreeCAD.Base.BoundBox.YMax`

```python
YMax: float = 0.0
```

The maximum y boundary position.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 169.

## `FreeCAD.Base.BoundBox.ZMax`

```python
ZMax: float = 0.0
```

The maximum z boundary position.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 171.

## `FreeCAD.Base.BoundBox.XMin`

```python
XMin: float = 0.0
```

The minimum x boundary position.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 173.

## `FreeCAD.Base.BoundBox.YMin`

```python
YMin: float = 0.0
```

The minimum y boundary position.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 175.

## `FreeCAD.Base.BoundBox.ZMin`

```python
ZMin: float = 0.0
```

The minimum z boundary position.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 177.

## `FreeCAD.Base.BoundBox.XLength`

```python
XLength: Final[float] = 0.0
```

Length of the bounding box in x direction.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 179.

## `FreeCAD.Base.BoundBox.YLength`

```python
YLength: Final[float] = 0.0
```

Length of the bounding box in y direction.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 181.

## `FreeCAD.Base.BoundBox.ZLength`

```python
ZLength: Final[float] = 0.0
```

Length of the bounding box in z direction.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 183.

## `FreeCAD.Base.BoundBox.DiagonalLength`

```python
DiagonalLength: Final[float] = 0.0
```

Diagonal length of the bounding box.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 185.

## `FreeCAD.Base.BoundBox.__init__`

```python
@overload
def __init__(self) -> None:

@overload
def __init__(self, boundBox: 'BoundBox') -> None:

@overload
def __init__(self, xMin: float, yMin: float=0, zMin: float=0, xMax: float=0, yMax: float=0, zMax: float=0) -> None:

@overload
def __init__(self, min: Union[Vector, Tuple[float, float, float]], max: Union[Vector, Tuple[float, float, float]]) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 189, 193, 197, 201.

## `FreeCAD.Base.BoundBox.setVoid`

```python
def setVoid(self) -> None:
```

Invalidate the bounding box.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 204.

## `FreeCAD.Base.BoundBox.isValid`

```python
def isValid(self) -> bool:
```

Checks if the bounding box is valid.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 210.

## `FreeCAD.Base.BoundBox.add`

```python
@overload
def add(self, minMax: Vector, /) -> None:

@overload
def add(self, minMax: Tuple[float, float, float], /) -> None:

@overload
def add(self, x: float, y: float, z: float, /) -> None:

def add(self, *args: Any, **kwargs: Any) -> None:
```

Increase the maximum values or decrease the minimum values of this BoundBox by
replacing the current values with the given values, so the bounding box can grow
but not shrink.

minMax : Base.Vector, tuple
    Values to enlarge at each direction.
x : float
    Value to enlarge at x-direction.
y : float
    Value to enlarge at y-direction.
z : float
    Value to enlarge at z-direction.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 217, 221, 225, 228.

## `FreeCAD.Base.BoundBox.getPoint`

```python
def getPoint(self, index: int, /) -> Vector:
```

Get the point of the given index.
The index must be in the range of [0, 7].

index : int

Evidence: public stub `FreeCAD/Base.pyi` line(s) 245.

## `FreeCAD.Base.BoundBox.getEdge`

```python
def getEdge(self, index: int, /) -> Tuple[Vector, ...]:
```

Get the edge points of the given index.
The index must be in the range of [0, 11].

index : int

Evidence: public stub `FreeCAD/Base.pyi` line(s) 254.

## `FreeCAD.Base.BoundBox.closestPoint`

```python
@overload
def closestPoint(self, point: Union[Vector, Tuple[float, float, float]], /) -> Vector:

@overload
def closestPoint(self, x: float, y: float, z: float, /) -> Vector:

def closestPoint(self, *args: Any, **kwargs: Any) -> Vector:
```

Get the closest point of the bounding box to the given point.

point : Base.Vector, tuple
    Coordinates of the given point.
x : float
    X-coordinate of the given point.
y : float
    Y-coordinate of the given point.
z : float
    Z-coordinate of the given point.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 264, 268, 271.

## `FreeCAD.Base.BoundBox.intersect`

```python
@overload
def intersect(self, boundBox2: 'BoundBox', /) -> bool:

@overload
def intersect(self, base: Union[Vector, Tuple[float, float, float]], dir: Union[Vector, Tuple[float, float, float]], /) -> bool:

def intersect(self, *args: Any) -> bool:
```

Checks if the given object intersects with this bounding box. That can be
another bounding box or a line specified by base and direction.

boundBox2 : Base.BoundBox
base : Base.Vector, tuple
dir : Base.Vector, tuple

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 287, 291, 294.

## `FreeCAD.Base.BoundBox.intersected`

```python
def intersected(self, boundBox2: 'BoundBox', /) -> 'BoundBox':
```

Returns the intersection of this and the given bounding box.

boundBox2 : Base.BoundBox

Evidence: public stub `FreeCAD/Base.pyi` line(s) 305.

## `FreeCAD.Base.BoundBox.united`

```python
def united(self, boundBox2: 'BoundBox', /) -> 'BoundBox':
```

Returns the union of this and the given bounding box.

boundBox2 : Base.BoundBox

Evidence: public stub `FreeCAD/Base.pyi` line(s) 313.

## `FreeCAD.Base.BoundBox.enlarge`

```python
def enlarge(self, variation: float, /) -> None:
```

Decrease the minimum values and increase the maximum values by the given value.
A negative value shrinks the bounding box.

variation : float

Evidence: public stub `FreeCAD/Base.pyi` line(s) 321.

## `FreeCAD.Base.BoundBox.getIntersectionPoint`

```python
def getIntersectionPoint(self, base: Vector, dir: Vector, epsilon: float=0.0001, /) -> Vector:
```

Calculate the intersection point of a line with the bounding box.
The base point must lie inside the bounding box, if not an exception is thrown.

base : Base.Vector
    Base point of the line.
dir : Base.Vector
    Direction of the line.
epsilon : float
    Bounding box size tolerance.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 330.

## `FreeCAD.Base.BoundBox.move`

```python
@overload
def move(self, displacement: Vector, /) -> None:

@overload
def move(self, displacement: Tuple[float, float, float], /) -> None:

@overload
def move(self, x: float, y: float, z: float, /) -> None:

def move(self, *args: Any, **kwargs: Any) -> None:
```

Move the bounding box by the given values.

displacement : Base.Vector, tuple
    Displacement at each direction.
x : float
    Displacement at x-direction.
y : float
    Displacement at y-direction.
z : float
    Displacement at z-direction.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 345, 349, 353, 356.

## `FreeCAD.Base.BoundBox.scale`

```python
@overload
def scale(self, factor: Vector, /) -> None:

@overload
def scale(self, factor: Tuple[float, float, float], /) -> None:

@overload
def scale(self, x: float, y: float, z: float, /) -> None:

def scale(self, *args: Any, **kwargs: Any) -> None:
```

Scale the bounding box by the given values.

factor : Base.Vector, tuple
    Factor scale at each direction.
x : float
    Scale at x-direction.
y : float
    Scale at y-direction.
z : float
    Scale at z-direction.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 372, 376, 380, 383.

## `FreeCAD.Base.BoundBox.transformed`

```python
def transformed(self, matrix: Matrix, /) -> 'BoundBox':
```

Returns a new BoundBox containing the transformed rectangular cuboid
represented by this BoundBox.

matrix : Base.Matrix
    Transformation matrix.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 398.

## `FreeCAD.Base.BoundBox.isCutPlane`

```python
def isCutPlane(self, base: Vector, normal: Vector, /) -> bool:
```

Check if the plane specified by base and normal intersects (cuts) this bounding
box.

base : Base.Vector
normal : Base.Vector

Evidence: public stub `FreeCAD/Base.pyi` line(s) 408.

## `FreeCAD.Base.BoundBox.isInside`

```python
@overload
def isInside(self, object: Union[Vector, Tuple[float, float, float]], /) -> bool:

@overload
def isInside(self, object: 'BoundBox', /) -> bool:

@overload
def isInside(self, x: float, y: float, z: float, /) -> bool:

def isInside(self, *args: Any) -> bool:
```

Check if a point or a bounding box is inside this bounding box.

object : Base.Vector, Base.BoundBox
    Object to check if it is inside this bounding box.
x : float
    X-coordinate of the point to check.
y : float
    Y-coordinate of the point to check.
z : float
    Z-coordinate of the point to check.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 419, 423, 427, 430.

