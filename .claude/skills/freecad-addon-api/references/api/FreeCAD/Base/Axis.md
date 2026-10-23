# `FreeCAD.Base.Axis`

[Module](index.md)

```python
class Axis:
```

Base.Axis class.

An Axis defines a direction and a position (base) in 3D space.

The following constructors are supported:

Axis()
Empty constructor.

Axis(axis)
Copy constructor.
axis : Base.Axis

Axis(base, direction)
Define from a position and a direction.
base : Base.Vector
direction : Base.Vector

Evidence: public stub `FreeCAD/Base.pyi` line 23. Inherited members are on the named base's reference; aliases keep their imported identity.

## `FreeCAD.Base.Axis.Base`

```python
Base: Vector = ...
```

Base position vector of the Axis.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 43.

## `FreeCAD.Base.Axis.Direction`

```python
Direction: Vector = ...
```

Direction vector of the Axis.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 45.

## `FreeCAD.Base.Axis.__init__`

```python
@overload
def __init__(self) -> None:

@overload
def __init__(self, axis: Axis) -> None:

@overload
def __init__(self, base: Vector, direction: Vector) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 49, 53, 57.

## `FreeCAD.Base.Axis.copy`

```python
def copy(self) -> Axis:
```

Returns a copy of this Axis.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 60.

## `FreeCAD.Base.Axis.move`

```python
def move(self, vector: Vector, /) -> None:
```

Move the axis base along the given vector.

vector : Base.Vector
    Vector by which to move the axis.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 66.

## `FreeCAD.Base.Axis.multiply`

```python
def multiply(self, placement: Placement, /) -> Axis:
```

Multiply this axis by a placement.

placement : Base.Placement
    Placement by which to multiply the axis.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 75.

## `FreeCAD.Base.Axis.reversed`

```python
def reversed(self) -> Axis:
```

Compute the reversed axis. This returns a new Base.Axis with
the original direction reversed.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 84.

