# `TechDraw.DrawViewSymbol`

[Module](index.md)

```python
class DrawViewSymbol(DrawView):
```

Feature for creating and manipulating Drawing SVG Symbol Views

Author: WandererFan (wandererfan@gmail.com)
License: LGPL-2.1-or-later

Evidence: public stub `TechDraw/__init__.pyi` line 1784. Inherited members are on the named base's reference; aliases keep their imported identity.

## `TechDraw.DrawViewSymbol.EditableTexts`

```python
@property
def EditableTexts(self) -> list[str]:

@EditableTexts.setter
def EditableTexts(self, value: Sequence[str]) -> None:
```

Substitution values for the editable strings in this symbol

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1793, 1798.

## `TechDraw.DrawViewSymbol.Owner`

```python
@property
def Owner(self) -> DocumentObject | None:

@Owner.setter
def Owner(self, value: DocumentObject | None) -> None:
```

Feature to which this symbol is attached

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1802, 1807.

## `TechDraw.DrawViewSymbol.Symbol`

```python
@property
def Symbol(self) -> str:

@Symbol.setter
def Symbol(self, value: str) -> None:
```

The SVG code defining this symbol

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1811, 1816.

## `TechDraw.DrawViewSymbol.dumpSymbol`

```python
def dumpSymbol(self, filename: str, /) -> None:
```

dumpSymbol(fileSpec) - dump the contents of Symbol to a file

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1819.

