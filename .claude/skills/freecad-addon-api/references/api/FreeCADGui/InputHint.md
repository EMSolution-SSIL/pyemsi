# `FreeCADGui.InputHint`

[Module](index.md)

```python
class InputHint:
```

One user-facing message together with the input sequence that triggers it.

Evidence: public stub `FreeCADGui/__init__.pyi` line 349. Inherited members are on the named base's reference; aliases keep their imported identity.

## `FreeCADGui.InputHint.InputSequence`

```python
InputSequence: ClassVar[object]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 351.

## `FreeCADGui.InputHint.message`

```python
message: str
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 352.

## `FreeCADGui.InputHint.sequences`

```python
sequences: list[_InputSequence]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 353.

## `FreeCADGui.InputHint.__init__`

```python
def __init__(self, message: str, *sequences: _InputSequence) -> None:
```

Create one input hint with one or more accepted input sequences.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 355.

