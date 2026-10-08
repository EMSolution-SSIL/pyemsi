# `Part.ArcOfConic`

[Module](index.md)

```python
class ArcOfConic(TrimmedCurve):
```

Describes a portion of a conic

Author: Abdullah Tahiri (abdullah.tahiri.yo@gmail.com)
Licence: LGPL

Evidence: public stub `Part/__init__.pyi` line 299. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.ArcOfConic.__init__`

```python
@overload
def __init__(self) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Evidence: public stub `Part/__init__.pyi` line(s) 308.

## `Part.ArcOfConic.Location`

```python
Location: Vector = ...
```

Center of the conic.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 310.

## `Part.ArcOfConic.Center`

```python
@property
@deprecated('since FreeCAD 26.3 and will be removed in FreeCAD 27.2; use Location instead.')
def Center(self) -> Vector:

@Center.setter
@deprecated('since FreeCAD 26.3 and will be removed in FreeCAD 27.2; use Location instead.')
def Center(self, value: Vector) -> None:
```

Deprecated -- use Location.

Access: getter and setter declared in the stub.

Evidence: public stub `Part/__init__.pyi` line(s) 315, 321.

## `Part.ArcOfConic.AngleXU`

```python
AngleXU: float = ...
```

The angle between the X axis and the major axis of the conic.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 323.

## `Part.ArcOfConic.Axis`

```python
Axis: Vector = ...
```

The axis direction of the conic

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 325.

## `Part.ArcOfConic.XAxis`

```python
XAxis: Vector = ...
```

The X axis direction of the circle

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 327.

## `Part.ArcOfConic.YAxis`

```python
YAxis: Vector = ...
```

The Y axis direction of the circle

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 329.

