# `Part.ArcOfEllipse`

[Module](index.md)

```python
class ArcOfEllipse(ArcOfConic):
```

Describes a portion of an ellipse

Author: Abdullah Tahiri (abdullah.tahiri.yo[at]gmail.com)
Licence: LGPL

Evidence: public stub `Part/__init__.pyi` line 332. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.ArcOfEllipse.MajorRadius`

```python
MajorRadius: float = ...
```

The major radius of the ellipse.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 339.

## `Part.ArcOfEllipse.MinorRadius`

```python
MinorRadius: float = ...
```

The minor radius of the ellipse.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 341.

## `Part.ArcOfEllipse.Ellipse`

```python
Ellipse: Final[object] = ...
```

The internal ellipse representation

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 343.

## `Part.ArcOfEllipse.__init__`

```python
@overload
def __init__(self, ellipse: 'Part.Ellipse', u1: float, u2: float, sense: bool=..., /) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 347.

