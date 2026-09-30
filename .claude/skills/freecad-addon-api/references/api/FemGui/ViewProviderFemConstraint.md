# `FemGui.ViewProviderFemConstraint`

[Module](index.md)

```python
class ViewProviderFemConstraint(ViewProviderGeometryObject):
```

This is the ViewProviderFemConstraint class

Author: Mario Passaglia (mpassaglia@cbc.uba.ar)
License: LGPL-2.1-or-later

Evidence: public stub `FemGui/__init__.pyi` line 47. Inherited members are on the named base's reference; aliases keep their imported identity.

## `FemGui.ViewProviderFemConstraint.loadSymbol`

```python
def loadSymbol(self, file_name: str, /) -> Any:
```

Load constraint symbol from Open Inventor file.
The file structure should be as follows:
A separator containing a separator with the symbol used in
multiple copies at points on the surface and an optional
separator with a symbol excluded from multiple copies.

file_name : str
    Open Inventor file.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FemGui/__init__.pyi` line(s) 55.

## `FemGui.ViewProviderFemConstraint.SymbolNode`

```python
SymbolNode: Final[Any]
```

A pivy SoSeparator with the nodes of the constraint symbols

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FemGui/__init__.pyi` line(s) 67.

## `FemGui.ViewProviderFemConstraint.ExtraSymbolNode`

```python
ExtraSymbolNode: Final[Any]
```

A pivy SoSeparator with the nodes of the constraint extra symbols

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FemGui/__init__.pyi` line(s) 69.

## `FemGui.ViewProviderFemConstraint.RotateSymbol`

```python
RotateSymbol: bool
```

Apply rotation on copies of the constraint symbol

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FemGui/__init__.pyi` line(s) 71.

## `FemGui.ViewProviderFemConstraint.ResourceSymbolDir`

```python
ResourceSymbolDir: Final[str] = ''
```

Path to system resource symbol directory

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FemGui/__init__.pyi` line(s) 73.

