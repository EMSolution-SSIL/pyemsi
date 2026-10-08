# `Part.BoundedCurve`

[Module](index.md)

```python
class BoundedCurve(Curve):
```

The abstract class BoundedCurve is the root class of all bounded curve objects.

Author: Abdullah Tahiri (abdullah.tahiri.yo@gmail.com)
Licence: LGPL

Evidence: public stub `Part/__init__.pyi` line 2013. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.BoundedCurve.StartPoint`

```python
StartPoint: Final[Any] = ...
```

Returns the starting point of the bounded curve.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Part/__init__.pyi` line(s) 2020.

## `Part.BoundedCurve.EndPoint`

```python
EndPoint: Final[Any] = ...
```

Returns the end point of the bounded curve.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Part/__init__.pyi` line(s) 2022.

