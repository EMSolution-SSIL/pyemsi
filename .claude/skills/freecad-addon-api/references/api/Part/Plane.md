# `Part.Plane`

[Module](index.md)

```python
class Plane(GeometrySurface):
```

    Describes an infinite plane
To create a plane there are several ways:
Part.Plane()
    Creates a default plane with base (0,0,0) and normal (0,0,1)

Part.Plane(Plane)
    Creates a copy of the given plane

Part.Plane(Plane, Distance)
    Creates a plane parallel to given plane at a certain distance

Part.Plane(Location,Normal)
    Creates a plane with a given location and normal

Part.Plane(Point1,Point2,Point3)
    Creates a plane defined by three non-linear points

Part.Plane(A,B,C,D)
    Creates a plane from its cartesian equation
    Ax+By+Cz+D=0

Evidence: public stub `Part/__init__.pyi` line 3180. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.Plane.Position`

```python
Position: object = ...
```

Returns the position point of this plane.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 3203.

## `Part.Plane.Axis`

```python
Axis: object = ...
```

Returns the axis of this plane.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 3205.

