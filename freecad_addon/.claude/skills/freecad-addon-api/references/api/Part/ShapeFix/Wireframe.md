# `Part.ShapeFix.Wireframe`

[Module](index.md)

```python
class Wireframe(Root):
```

Provides methods for fixing wireframe of shape

Author: Werner Mayer (wmayer@users.sourceforge.net)
Licence: LGPL

Evidence: public stub `Part/ShapeFix.pyi` line 1165. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.ShapeFix.Wireframe.ModeDropSmallEdges`

```python
ModeDropSmallEdges: bool = ...
```

Returns mode managing removing small edges

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1172.

## `Part.ShapeFix.Wireframe.LimitAngle`

```python
LimitAngle: float = ...
```

Limit angle for merging edges

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1174.

## `Part.ShapeFix.Wireframe.clearStatuses`

```python
def clearStatuses(self) -> None:
```

Clears all statuses

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1177.

## `Part.ShapeFix.Wireframe.load`

```python
def load(self, shape: TopoShape, /) -> None:
```

Loads a shape, resets statuses

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1183.

## `Part.ShapeFix.Wireframe.fixWireGaps`

```python
def fixWireGaps(self) -> bool:
```

Fixes gaps between ends of curves of adjacent edges

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1189.

## `Part.ShapeFix.Wireframe.fixSmallEdges`

```python
def fixSmallEdges(self) -> bool:
```

Fixes small edges in shape by merging adjacent edges

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1195.

## `Part.ShapeFix.Wireframe.shape`

```python
def shape(self) -> TopoShape:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1201.

