# `FreeCAD._ParameterObserver`

[Module](index.md)

```python
class _ParameterObserver(Protocol):
```

Observer protocol for parameter changes inside one parameter group.

Evidence: public stub `FreeCAD/__init__.pyi` line 258. Inherited members are on the named base's reference; aliases keep their imported identity.

Underscored typing/support name: verify runtime exposure and support status before using it.

## `FreeCAD._ParameterObserver.onChange`

```python
def onChange(self, group: ParameterGrp, param_type: str, name: str, value: str, /) -> object:
```

Handle one parameter change notification.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 261.

