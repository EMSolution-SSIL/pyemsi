# `Part.ShapeFix.WireVertex`

[Module](index.md)

```python
class WireVertex:
```

Fixing disconnected edges in the wire

Author: Werner Mayer (wmayer@users.sourceforge.net)
Licence: LGPL

Evidence: public stub `Part/ShapeFix.pyi` line 1130. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.ShapeFix.WireVertex.init`

```python
def init(self, wire: TopoShapeWire, precision: float, /) -> None:
```

Loads the wire, ininializes internal analyzer with the given precision

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1138.

## `Part.ShapeFix.WireVertex.wire`

```python
def wire(self) -> object:
```

Returns resulting wire

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1144.

## `Part.ShapeFix.WireVertex.fixSame`

```python
def fixSame(self) -> int:
```

Returns the count of fixed vertices, 0 if none

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1150.

## `Part.ShapeFix.WireVertex.fix`

```python
def fix(self) -> int:
```

Fixes all statuses except Disjoined, i.e. the cases in which a
common value has been set, with or without changing parameters
Returns the count of fixed vertices, 0 if none

Evidence: public stub `Part/ShapeFix.pyi` line(s) 1156.

