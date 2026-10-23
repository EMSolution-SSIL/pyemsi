# `FreeCADGui._MDIView`

[Module](index.md)

```python
class _MDIView:
```

Class purpose undocumented in this stub.

Evidence: public stub `FreeCADGui/__init__.pyi` line 799. Inherited members are on the named base's reference; aliases keep their imported identity.

Underscored typing/support name: verify runtime exposure and support status before using it.

## `FreeCADGui._MDIView.printView`

```python
def printView(self) -> None:
```

Print the current view.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 801.

## `FreeCADGui._MDIView.printPdf`

```python
def printPdf(self) -> None:
```

Export the current view to PDF.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 805.

## `FreeCADGui._MDIView.printPreview`

```python
def printPreview(self) -> None:
```

Open a print preview for the current view.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 809.

## `FreeCADGui._MDIView.undoActions`

```python
def undoActions(self) -> list[str]:
```

Return the undo actions exposed by the view.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 813.

## `FreeCADGui._MDIView.redoActions`

```python
def redoActions(self) -> list[str]:
```

Return the redo actions exposed by the view.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 817.

## `FreeCADGui._MDIView.message`

```python
@deprecated('since FreeCAD 26.3 and will be removed in FreeCAD 27.2; use sendMessage instead.')
def message(self, message: str, /) -> bool:
```

Handle one generic message in the view.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 822.

## `FreeCADGui._MDIView.sendMessage`

```python
def sendMessage(self, message: str, /) -> bool:
```

Send one generic message to the view.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 826.

## `FreeCADGui._MDIView.supportMessage`

```python
def supportMessage(self, message: str, /) -> bool:
```

Return whether the view supports one generic message.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 830.

## `FreeCADGui._MDIView.fitAll`

```python
def fitAll(self) -> None:
```

Fit the full visible content in the view.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 834.

## `FreeCADGui._MDIView.setActiveObject`

```python
def setActiveObject(self, name: str, document_object: DocumentObject | None=None, subname: str | None=None, /) -> None:
```

Set one active object slot for the view.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 838.

## `FreeCADGui._MDIView.getActiveObject`

```python
@overload
def getActiveObject(self, name: str, resolve: Literal[True]=True, /) -> DocumentObject | None:

@overload
def getActiveObject(self, name: str, resolve: Literal[False], /) -> _ActiveObjectReference | _EmptyActiveObjectReference:
```

Return the resolved active object for one slot name.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 843, 848.

## `FreeCADGui._MDIView.cast_to_base`

```python
def cast_to_base(self) -> _MDIView:
```

Return this view as the base MDI view wrapper.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 851.

## `FreeCADGui._MDIView.getTypeId`

```python
def getTypeId(self, *args: Any) -> Any:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 855.

