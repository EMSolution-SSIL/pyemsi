# `Part.Circle`

[Module](index.md)

```python
class Circle(Conic):
```

Describes a circle in 3D space
To create a circle there are several ways:
Part.Circle()
    Creates a default circle with center (0,0,0) and radius 1

Part.Circle(Circle)
    Creates a copy of the given circle

Part.Circle(Circle, Distance)
    Creates a circle parallel to given circle at a certain distance

Part.Circle(Center,Normal,Radius)
    Creates a circle defined by center, normal direction and radius

Part.Circle(Point1,Point2,Point3)
    Creates a circle defined by three non-linear points

Evidence: public stub `Part/__init__.pyi` line 2025. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.Circle.Radius`

```python
Radius: float = 0.0
```

The radius of the circle.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 2044.

## `Part.Circle.__init__`

```python
@overload
def __init__(self) -> None:

@overload
def __init__(self, circle: 'Circle') -> None:

@overload
def __init__(self, circle: 'Circle', distance: float) -> None:

@overload
def __init__(self, center: Vector, normal: Vector, radius: float) -> None:

@overload
def __init__(self, point1: Vector, point2: Vector, point3: Vector) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Evidence: public stub `Part/__init__.pyi` line(s) 2048, 2052, 2056, 2060, 2064.

