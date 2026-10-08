# `Part.ArcOfParabola`

[Module](index.md)

```python
class ArcOfParabola(ArcOfConic):
```

Describes a portion of a parabola

Author: Abdullah Tahiri (abdullah.tahiri.yo@gmail.com)
Licence: LGPL

Evidence: public stub `Part/__init__.pyi` line 361. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.ArcOfParabola.Focal`

```python
Focal: float = ...
```

The focal length of the parabola.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 368.

## `Part.ArcOfParabola.Parabola`

```python
Parabola: Final[object] = ...
```

The internal parabola representation

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 370.

