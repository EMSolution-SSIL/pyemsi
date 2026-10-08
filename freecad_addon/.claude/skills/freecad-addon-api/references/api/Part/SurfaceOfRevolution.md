# `Part.SurfaceOfRevolution`

[Module](index.md)

```python
class SurfaceOfRevolution(GeometrySurface):
```

Describes a surface of revolution

Author: Werner Mayer (wmayer@users.sourceforge.net)
Licence: LGPL

Evidence: public stub `Part/__init__.pyi` line 3344. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.SurfaceOfRevolution.Location`

```python
Location: Placement
```

Sets or gets the location of revolution.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 3351.

## `Part.SurfaceOfRevolution.Direction`

```python
Direction: Vector
```

Sets or gets the direction of revolution.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 3353.

## `Part.SurfaceOfRevolution.BasisCurve`

```python
BasisCurve: Curve
```

Sets or gets the basic curve.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 3355.

## `Part.SurfaceOfRevolution.__init__`

```python
@overload
def __init__(self, location: Placement, direction: Vector, basis_curve: Curve) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Evidence: public stub `Part/__init__.pyi` line(s) 3359.

