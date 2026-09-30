# `Part.Geom2d.Line2dSegment`

[Module](index.md)

```python
class Line2dSegment(Curve2d):
```

Describes a line segment in 2D space.

To create a line there are several ways:
Part.Geom2d.Line2dSegment()
    Creates a default line

Part.Geom2d.Line2dSegment(Line)
    Creates a copy of the given line

Part.Geom2d.Line2dSegment(Point1,Point2)
    Creates a line that goes through two given points.

Evidence: public stub `Part/Geom2d.pyi` line 1135. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.Geom2d.Line2dSegment.StartPoint`

```python
StartPoint: object = ...
```

Returns the start point of this line segment.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/Geom2d.pyi` line(s) 1149.

## `Part.Geom2d.Line2dSegment.EndPoint`

```python
EndPoint: object = ...
```

Returns the end point of this line segment.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/Geom2d.pyi` line(s) 1151.

## `Part.Geom2d.Line2dSegment.__init__`

```python
@overload
def __init__(self) -> None:

@overload
def __init__(self, Line: 'Line2dSegment') -> None:

@overload
def __init__(self, Point1: object, Point2: object) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Evidence: public stub `Part/Geom2d.pyi` line(s) 1155, 1159, 1163.

## `Part.Geom2d.Line2dSegment.setParameterRange`

```python
def setParameterRange(self, first: float, last: float, /) -> None:
```

Set the parameter range of the underlying line segment geometry.

Evidence: public stub `Part/Geom2d.pyi` line(s) 1166.

