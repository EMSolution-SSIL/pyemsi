# `Part.ArcOfCircle`

[Module](index.md)

```python
class ArcOfCircle(ArcOfConic):
```

Author: Werner Mayer (wmayer[at]users.sourceforge.net)
Licence: LGPL
Describes a portion of a circle

Evidence: public stub `Part/__init__.pyi` line 288. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.ArcOfCircle.Radius`

```python
Radius: float = ...
```

The radius of the circle.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 294.

## `Part.ArcOfCircle.Circle`

```python
Circle: Final[object] = ...
```

The internal circle representation

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 296.

