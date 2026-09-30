# `FreeCADGui.Selection.Filter`

[Module](index.md)

```python
class Filter:
```

Selection filter helper that wraps the GUI filter expression language.

Evidence: public stub `FreeCADGui/Selection.pyi` line 33. Inherited members are on the named base's reference; aliases keep their imported identity.

## `FreeCADGui.Selection.Filter.__init__`

```python
def __init__(self, filter: str, /) -> None:
```

Create one selection filter from its expression string.

Evidence: public stub `FreeCADGui/Selection.pyi` line(s) 36.

## `FreeCADGui.Selection.Filter.match`

```python
def match(self) -> bool:
```

Return whether the current filter matches the current selection state.

Evidence: public stub `FreeCADGui/Selection.pyi` line(s) 40.

## `FreeCADGui.Selection.Filter.test`

```python
def test(self, obj: DocumentObject, sub_name: str='', /) -> bool:
```

Return whether one object and optional subname matches the filter.

Evidence: public stub `FreeCADGui/Selection.pyi` line(s) 44.

## `FreeCADGui.Selection.Filter.result`

```python
def result(self) -> list[tuple[SelectionObject, ...]]:
```

Return the current filter match result set.

Evidence: public stub `FreeCADGui/Selection.pyi` line(s) 48.

## `FreeCADGui.Selection.Filter.setFilter`

```python
def setFilter(self, filter: str, /) -> None:
```

Replace the filter expression string.

Evidence: public stub `FreeCADGui/Selection.pyi` line(s) 52.

## `FreeCADGui.Selection.Filter.getFilter`

```python
def getFilter(self) -> str:
```

Return the current filter expression string.

Evidence: public stub `FreeCADGui/Selection.pyi` line(s) 56.

