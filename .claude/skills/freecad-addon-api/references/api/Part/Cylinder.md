# `Part.Cylinder`

[Module](index.md)

```python
class Cylinder(GeometrySurface):
```

Describes a cylinder in 3D space

To create a cylinder there are several ways:

Part.Cylinder()
    Creates a default cylinder with center (0,0,0) and radius 1

Part.Cylinder(Cylinder)
    Creates a copy of the given cylinder

Part.Cylinder(Cylinder, Distance)
    Creates a cylinder parallel to given cylinder at a certain distance

Part.Cylinder(Point1, Point2, Point2)
    Creates a cylinder defined by three non-linear points

Part.Cylinder(Circle)
    Creates a cylinder by a circular base

Author: Werner Mayer (wmayer@users.sourceforge.net)
Licence: LGPL

Evidence: public stub `Part/__init__.pyi` line 2143. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.Cylinder.Radius`

```python
Radius: float
```

The radius of the cylinder.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 2167.

## `Part.Cylinder.Center`

```python
Center: Vector
```

Center of the cylinder.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 2169.

## `Part.Cylinder.Axis`

```python
Axis: Vector
```

The axis direction of the cylinder

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 2171.

## `Part.Cylinder.__init__`

```python
@overload
def __init__(self) -> None:

@overload
def __init__(self, cylinder: 'Cylinder') -> None:

@overload
def __init__(self, cylinder: 'Cylinder', distance: float) -> None:

@overload
def __init__(self, point1: Vector, point2: Vector, point3: Vector) -> None:

@overload
def __init__(self, circle: Circle) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Evidence: public stub `Part/__init__.pyi` line(s) 2175, 2179, 2183, 2187, 2191.

