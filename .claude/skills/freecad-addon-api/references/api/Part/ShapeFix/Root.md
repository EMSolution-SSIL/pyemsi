# `Part.ShapeFix.Root`

[Module](index.md)

```python
class Root:
```

Root class for fixing operations

Author: Werner Mayer (wmayer@users.sourceforge.net)
Licence: LGPL

Evidence: public stub `Part/ShapeFix.pyi` line 576. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.ShapeFix.Root.Precision`

```python
Precision: float = ...
```

Basic precision value

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 583.

## `Part.ShapeFix.Root.MinTolerance`

```python
MinTolerance: float = ...
```

Minimal allowed tolerance

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 585.

## `Part.ShapeFix.Root.MaxTolerance`

```python
MaxTolerance: float = ...
```

Maximal allowed tolerance

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 587.

## `Part.ShapeFix.Root.limitTolerance`

```python
def limitTolerance(self, tolerance: float, /) -> float:
```

Returns tolerance limited by [MinTolerance,MaxTolerance]

Evidence: public stub `Part/ShapeFix.pyi` line(s) 590.

