# `Part.Line`

[Module](index.md)

```python
class Line(Curve):
```

Describes an infinite line
To create a line there are several ways:
Part.Line()
    Creates a default line

Part.Line(Line)
    Creates a copy of the given line

Part.Line(Point1,Point2)
    Creates a line that goes through two given points

Author: Werner Mayer (wmayer@users.sourceforge.net)
Licence: LGPL

Evidence: public stub `Part/__init__.pyi` line 3015. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.Line.Location`

```python
Location: Vector = ...
```

Returns the location of this line.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 3031.

## `Part.Line.Direction`

```python
Direction: Vector = ...
```

Returns the direction of this line.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 3033.

## `Part.Line.__init__`

```python
@overload
def __init__(self) -> None:

@overload
def __init__(self, line: 'Line') -> None:

@overload
def __init__(self, point1: Vector, point2: Vector) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Evidence: public stub `Part/__init__.pyi` line(s) 3037, 3041, 3045.

