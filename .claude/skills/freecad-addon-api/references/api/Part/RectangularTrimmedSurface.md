# `Part.RectangularTrimmedSurface`

[Module](index.md)

```python
class RectangularTrimmedSurface(GeometrySurface):
```

Describes a portion of a surface (a patch) limited by two values of the
u parameter in the u parametric direction, and two values of the v parameter in the v parametric
direction. The domain of the trimmed surface must be within the domain of the surface being trimmed.

The trimmed surface is defined by:
- the basis surface, and
- the values (umin, umax) and (vmin, vmax) which limit it in the u and v parametric directions.

The trimmed surface is built from a copy of the basis surface. Therefore, when the basis surface
is modified the trimmed surface is not changed. Consequently, the trimmed surface does not
necessarily have the same orientation as the basis surface.

Author: Werner Mayer (wmayer@users.sourceforge.net)
Licence: LGPL

Evidence: public stub `Part/__init__.pyi` line 3287. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.RectangularTrimmedSurface.BasisSurface`

```python
BasisSurface: Final[Any] = ...
```

Represents the basis surface from which the trimmed surface is derived.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Part/__init__.pyi` line(s) 3304.

## `Part.RectangularTrimmedSurface.setTrim`

```python
def setTrim(self, u1: float, u2: float, v1: float, v2: float, /) -> None:
```

setTrim(self, u1, u2, v1, v2) -> None

Modifies this patch by changing the trim values applied to the original surface

Evidence: public stub `Part/__init__.pyi` line(s) 3307.

