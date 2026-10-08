# `Part.Geom2d.Circle2d`

[Module](index.md)

```python
class Circle2d(Conic2d):
```

Describes a circle in 3D space
To create a circle there are several ways:
Part.Geom2d.Circle2d()
    Creates a default circle with center (0,0) and radius 1

Part.Geom2d.Circle2d(circle)
    Creates a copy of the given circle

Part.Geom2d.Circle2d(circle, Distance)
    Creates a circle parallel to given circle at a certain distance

Part.Geom2d.Circle2d(Center,Radius)
    Creates a circle defined by center and radius

Part.Geom2d.Circle2d(Point1,Point2,Point3)
    Creates a circle defined by three non-linear points

Author: Werner Mayer (wmayer@users.sourceforge.net)
Licence: LGPL

Evidence: public stub `Part/Geom2d.pyi` line 647. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.Geom2d.Circle2d.Radius`

```python
Radius: float = ...
```

The radius of the circle.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/Geom2d.pyi` line(s) 669.

## `Part.Geom2d.Circle2d.__init__`

```python
@overload
def __init__(self) -> None:

@overload
def __init__(self, circle: 'Circle2d') -> None:

@overload
def __init__(self, circle: 'Circle2d', Distance: float) -> None:

@overload
def __init__(self, Center: Tuple[float, float], Radius: float) -> None:

@overload
def __init__(self, Point1: Tuple[float, float], Point2: Tuple[float, float], Point3: Tuple[float, float]) -> None:

@overload
def __init__(self, *args, **kwargs) -> None:
```

Describes a circle in 3D space
To create a circle there are several ways:
Part.Geom2d.Circle2d()
    Creates a default circle with center (0,0) and radius 1

Part.Geom2d.Circle2d(circle)
    Creates a copy of the given circle

Part.Geom2d.Circle2d(circle, Distance)
    Creates a circle parallel to given circle at a certain distance

Part.Geom2d.Circle2d(Center,Radius)
    Creates a circle defined by center and radius

Part.Geom2d.Circle2d(Point1,Point2,Point3)
    Creates a circle defined by three non-linear points

Evidence: public stub `Part/Geom2d.pyi` line(s) 673, 677, 681, 685, 689, 693.

## `Part.Geom2d.Circle2d.getCircleCenter`

```python
@staticmethod
def getCircleCenter(p1: Any, p2: Any, p3: Any, /) -> Any:
```

Get the circle center defined by three points

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Part/Geom2d.pyi` line(s) 715.

