# `Part.Arc`

[Module](index.md)

```python
class Arc(TrimmedCurve):
```

Describes a portion of a curve

Author: Werner Mayer (wmayer@users.sourceforge.net)
Licence: LGPL

Evidence: public stub `Part/__init__.pyi` line 260. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.Arc.__init__`

```python
@overload
def __init__(self, circ: Circle, u1: float, u2: float, sense: bool=..., /) -> None:

@overload
def __init__(self, ellipse: Ellipse, u1: float, u2: float, sense: bool=..., /) -> None:

@overload
def __init__(self, parabola: Parabola, u1: float, u2: float, sense: bool=..., /) -> None:

@overload
def __init__(self, hyperbola: Hyperbola, u1: float, u2: float, sense: bool=..., /) -> None:

@overload
def __init__(self, p1: Vector, p2: Vector, p3: Vector, /) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 269, 273, 277, 281, 285.

