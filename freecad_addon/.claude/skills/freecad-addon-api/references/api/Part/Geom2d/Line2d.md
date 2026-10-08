# `Part.Geom2d.Line2d`

[Module](index.md)

```python
class Line2d(Curve2d):
```

Describes an infinite line in 2D space
To create a line there are several ways:
Part.Geom2d.Line2d()
    Creates a default line.

Part.Geom2d.Line2d(Line)
    Creates a copy of the given line.

Part.Geom2d.Line2d(Point,Dir)
    Creates a line that goes through two given points.

Author: Werner Mayer (wmayer@users.sourceforge.net)
Licence: LGPL

Evidence: public stub `Part/Geom2d.pyi` line 1113. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.Geom2d.Line2d.Location`

```python
Location: object = ...
```

Returns the location of this line.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/Geom2d.pyi` line(s) 1129.

## `Part.Geom2d.Line2d.Direction`

```python
Direction: object = ...
```

Returns the direction of this line.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/Geom2d.pyi` line(s) 1131.

