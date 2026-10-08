# `Part.Geom2d.ArcOfCircle2d`

[Module](index.md)

```python
class ArcOfCircle2d(ArcOfConic2d):
```

Describes a portion of a circle

Author: Werner Mayer (wmayer[at]users.sourceforge.net)
Licence: LGPL

Evidence: public stub `Part/Geom2d.pyi` line 14. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.Geom2d.ArcOfCircle2d.Radius`

```python
Radius: float = ...
```

The radius of the circle.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/Geom2d.pyi` line(s) 21.

## `Part.Geom2d.ArcOfCircle2d.Circle`

```python
Circle: Final[object] = ...
```

The internal circle representation

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/Geom2d.pyi` line(s) 23.

## `Part.Geom2d.ArcOfCircle2d.__init__`

```python
@overload
def __init__(self, Radius: float, Circle: object) -> None:
```


    ArcOfCircle2d(Radius, Circle) -> None

    Constructor for ArcOfCircle2d.

    Parameters:
        Radius : float
            The radius of the circle.
        Circle : object
            The internal circle representation.
    

Evidence: public stub `Part/Geom2d.pyi` line(s) 27.

