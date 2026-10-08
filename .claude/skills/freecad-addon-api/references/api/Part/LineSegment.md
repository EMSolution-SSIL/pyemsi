# `Part.LineSegment`

[Module](index.md)

```python
class LineSegment(TrimmedCurve):
```

Describes a line segment
To create a line segment there are several ways:
Part.LineSegment()
    Creates a default line segment

Part.LineSegment(LineSegment)
    Creates a copy of the given line segment

Part.LineSegment(Vector1,Vector2)
    Creates a line segment that goes through two given points

Evidence: public stub `Part/__init__.pyi` line 3048. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.LineSegment.StartPoint`

```python
StartPoint: Type = ...
```

Returns the start point of this line.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 3061.

## `Part.LineSegment.EndPoint`

```python
EndPoint: Type = ...
```

Returns the end point point of this line.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 3063.

## `Part.LineSegment.__init__`

```python
@overload
def __init__(self) -> None:

@overload
def __init__(self, line_segment: 'LineSegment', /) -> None:

@overload
def __init__(self, line_segment: 'LineSegment', first: float, last: float, /) -> None:

@overload
def __init__(self, line: Line, first: float, last: float, /) -> None:

@overload
def __init__(self, point1: Vector, point2: Vector, /) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Evidence: public stub `Part/__init__.pyi` line(s) 3067, 3071, 3075, 3079, 3083.

## `Part.LineSegment.setParameterRange`

```python
def setParameterRange(self, first: float, last: float, /) -> None:
```

Set the parameter range of the underlying line geometry

Evidence: public stub `Part/__init__.pyi` line(s) 3086.

