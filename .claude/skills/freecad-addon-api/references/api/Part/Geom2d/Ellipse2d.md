# `Part.Geom2d.Ellipse2d`

[Module](index.md)

```python
class Ellipse2d(Conic2d):
```

Describes an ellipse in 2D space
To create an ellipse there are several ways:
Part.Geom2d.Ellipse2d()
    Creates an ellipse with major radius 2 and minor radius 1 with the
    center in (0,0)

Part.Geom2d.Ellipse2d(Ellipse)
    Create a copy of the given ellipse

Part.Geom2d.Ellipse2d(S1,S2,Center)
    Creates an ellipse centered on the point Center,
    its major axis is defined by Center and S1,
    its major radius is the distance between Center and S1, and
    its minor radius is the distance between S2 and the major axis.

Part.Geom2d.Ellipse2d(Center,MajorRadius,MinorRadius)
    Creates an ellipse with major and minor radii MajorRadius and
    MinorRadius

Author: Werner Mayer (wmayer@users.sourceforge.net)
Licence: LGPL

Evidence: public stub `Part/Geom2d.pyi` line 957. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.Geom2d.Ellipse2d.MajorRadius`

```python
MajorRadius: float = ...
```

The major radius of the ellipse.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/Geom2d.pyi` line(s) 981.

## `Part.Geom2d.Ellipse2d.MinorRadius`

```python
MinorRadius: float = ...
```

The minor radius of the ellipse.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/Geom2d.pyi` line(s) 983.

## `Part.Geom2d.Ellipse2d.Focal`

```python
Focal: Final[float] = ...
```

The focal distance of the ellipse.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/Geom2d.pyi` line(s) 985.

## `Part.Geom2d.Ellipse2d.Focus1`

```python
Focus1: Final[object] = ...
```

The first focus is on the positive side of the major axis of the ellipse.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/Geom2d.pyi` line(s) 987.

## `Part.Geom2d.Ellipse2d.Focus2`

```python
Focus2: Final[object] = ...
```

The second focus is on the negative side of the major axis of the ellipse.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/Geom2d.pyi` line(s) 989.

## `Part.Geom2d.Ellipse2d.__init__`

```python
@overload
def __init__(self) -> None:

@overload
def __init__(self, Ellipse: 'Ellipse2d') -> None:

@overload
def __init__(self, S1: object, S2: object, Center: object) -> None:

@overload
def __init__(self, Center: object, MajorRadius: float, MinorRadius: float) -> None:

@overload
def __init__(self, *args, **kwargs) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Evidence: public stub `Part/Geom2d.pyi` line(s) 993, 997, 1001, 1005, 1009.

