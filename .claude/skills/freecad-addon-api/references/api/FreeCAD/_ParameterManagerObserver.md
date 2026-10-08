# `FreeCAD._ParameterManagerObserver`

[Module](index.md)

```python
class _ParameterManagerObserver(Protocol):
```

Observer protocol for manager-level parameter change notifications.

Evidence: public stub `FreeCAD/__init__.pyi` line 265. Inherited members are on the named base's reference; aliases keep their imported identity.

Underscored typing/support name: verify runtime exposure and support status before using it.

## `FreeCAD._ParameterManagerObserver.slotParamChanged`

```python
def slotParamChanged(self, group: ParameterGrp, param_type: str, name: str, value: str, /) -> object:
```

Handle one manager-level parameter change notification.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 268.

