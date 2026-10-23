# `Part.Point`

[Module](index.md)

```python
class Point(Geometry):
```

Describes a point
To create a point there are several ways:
Part.Point()
    Creates a default point

Part.Point(Point)
    Creates a copy of the given point

Part.Point(Vector)
    Creates a line for the given coordinates

Author: Werner Mayer (wmayer@users.sourceforge.net)
Licence: LGPL

Evidence: public stub `Part/__init__.pyi` line 3219. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.Point.__init__`

```python
@overload
def __init__(self) -> None:

@overload
def __init__(self, other: 'Point') -> None:

@overload
def __init__(self, coordinates: Vector) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Evidence: public stub `Part/__init__.pyi` line(s) 3237, 3241, 3245.

## `Part.Point.toShape`

```python
def toShape(self) -> object:
```

Create a vertex from this point.

Evidence: public stub `Part/__init__.pyi` line(s) 3248.

## `Part.Point.X`

```python
X: float = ...
```

X component of this point.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 3253.

## `Part.Point.Y`

```python
Y: float = ...
```

Y component of this point.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 3255.

## `Part.Point.Z`

```python
Z: float = ...
```

Z component of this point.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 3257.

