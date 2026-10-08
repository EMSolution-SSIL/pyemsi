# `FreeCADGui._PyResource`

[Module](index.md)

```python
class _PyResource:
```

Class purpose undocumented in this stub.

Evidence: public stub `FreeCADGui/__init__.pyi` line 898. Inherited members are on the named base's reference; aliases keep their imported identity.

Underscored typing/support name: verify runtime exposure and support status before using it.

## `FreeCADGui._PyResource.value`

```python
def value(self, object_name: str, property_name: str, /) -> _PyResourceValue | None:
```

Return one property value from a named child object.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 900.

## `FreeCADGui._PyResource.setValue`

```python
def setValue(self, object_name: str, property_name: str, value: _PyResourceValue, /) -> None:
```

Set one property value on a named child object.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 904.

## `FreeCADGui._PyResource.show`

```python
def show(self) -> None:
```

Show the root resource widget.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 908.

## `FreeCADGui._PyResource.connect`

```python
def connect(self, sender: str, signal: str, callback: Callable[..., object], /) -> None:
```

Connect one named child signal to a Python callback.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 912.

