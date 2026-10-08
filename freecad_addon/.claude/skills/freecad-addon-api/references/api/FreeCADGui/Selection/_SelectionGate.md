# `FreeCADGui.Selection._SelectionGate`

[Module](index.md)

```python
class _SelectionGate(Protocol):
```

Protocol for custom selection-gate objects.

Evidence: public stub `FreeCADGui/Selection.pyi` line 26. Inherited members are on the named base's reference; aliases keep their imported identity.

Underscored typing/support name: verify runtime exposure and support status before using it.

## `FreeCADGui.Selection._SelectionGate.allow`

```python
def allow(self, doc: object, obj: DocumentObject, sub: str, /) -> bool:
```

Return whether one candidate selection should be accepted.

Evidence: public stub `FreeCADGui/Selection.pyi` line(s) 29.

