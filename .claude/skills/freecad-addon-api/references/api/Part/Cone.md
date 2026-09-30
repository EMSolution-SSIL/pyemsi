# `Part.Cone`

[Module](index.md)

```python
class Cone(GeometrySurface):
```

Describes a cone in 3D space

To create a cone there are several ways:

Part.Cone()
    Creates a default cone with radius 1

Part.Cone(Cone)
    Creates a copy of the given cone

Part.Cone(Cone, Distance)
    Creates a cone parallel to given cone at a certain distance

Part.Cone(Point1,Point2,Radius1,Radius2)
    Creates a cone defined by two points and two radii
    The axis of the cone is the line passing through
    Point1 and Poin2.
    Radius1 is the radius of the section passing through
    Point1 and Radius2 the radius of the section passing
    through Point2.

Part.Cone(Point1,Point2,Point3,Point4)
    Creates a cone passing through three points Point1,
    Point2 and Point3.
    Its axis is defined by Point1 and Point2 and the radius of
    its base is the distance between Point3 and its axis.
    The distance between Point and the axis is the radius of
    the section passing through Point4.

Author: Werner Mayer (wmayer@users.sourceforge.net)
Licence: LGPL

Evidence: public stub `Part/__init__.pyi` line 2067. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.Cone.Apex`

```python
Apex: Final[Vector] = Vector()
```

Compute the apex of the cone.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 2101.

## `Part.Cone.Radius`

```python
Radius: float = 0.0
```

The radius of the cone.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 2103.

## `Part.Cone.SemiAngle`

```python
SemiAngle: float = 0.0
```

The semi-angle of the cone.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 2105.

## `Part.Cone.Center`

```python
Center: Vector = Vector()
```

Center of the cone.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 2107.

## `Part.Cone.Axis`

```python
Axis: AxisPy = AxisPy()
```

The axis direction of the cone

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 2109.

