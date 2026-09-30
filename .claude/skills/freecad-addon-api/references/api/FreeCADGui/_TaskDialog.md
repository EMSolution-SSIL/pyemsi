# `FreeCADGui._TaskDialog`

[Module](index.md)

```python
class _TaskDialog:
```

Class purpose undocumented in this stub.

Evidence: public stub `FreeCADGui/__init__.pyi` line 916. Inherited members are on the named base's reference; aliases keep their imported identity.

Underscored typing/support name: verify runtime exposure and support status before using it.

## `FreeCADGui._TaskDialog.getDialogContent`

```python
def getDialogContent(self) -> list[object]:
```

Return the content widgets hosted by the dialog.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 918.

## `FreeCADGui._TaskDialog.getStandardButtons`

```python
def getStandardButtons(self) -> int:
```

Return the standard button mask for the dialog.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 922.

## `FreeCADGui._TaskDialog.setEscapeButtonEnabled`

```python
def setEscapeButtonEnabled(self, enabled: bool, /) -> None:
```

Enable or disable the escape button behavior.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 926.

## `FreeCADGui._TaskDialog.isEscapeButtonEnabled`

```python
def isEscapeButtonEnabled(self) -> bool:
```

Return whether the escape button is enabled.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 930.

## `FreeCADGui._TaskDialog.setAutoCloseOnTransactionChange`

```python
def setAutoCloseOnTransactionChange(self, enabled: bool, /) -> None:
```

Set whether transaction changes auto-close the dialog.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 934.

## `FreeCADGui._TaskDialog.isAutoCloseOnTransactionChange`

```python
def isAutoCloseOnTransactionChange(self) -> bool:
```

Return whether transaction changes auto-close the dialog.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 938.

## `FreeCADGui._TaskDialog.setAutoCloseOnResetEdit`

```python
def setAutoCloseOnResetEdit(self, *args: Any) -> Any:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 942.

## `FreeCADGui._TaskDialog.isAutoCloseOnResetEdit`

```python
def isAutoCloseOnResetEdit(self, *args: Any) -> Any:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 945.

## `FreeCADGui._TaskDialog.setAutoCloseOnDeletedDocument`

```python
def setAutoCloseOnDeletedDocument(self, enabled: bool, /) -> None:
```

Set whether document deletion auto-closes the dialog.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 948.

## `FreeCADGui._TaskDialog.isAutoCloseOnDeletedDocument`

```python
def isAutoCloseOnDeletedDocument(self) -> bool:
```

Return whether document deletion auto-closes the dialog.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 952.

## `FreeCADGui._TaskDialog.getDocumentName`

```python
def getDocumentName(self) -> str:
```

Return the document name associated with the dialog.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 956.

## `FreeCADGui._TaskDialog.setDocumentName`

```python
def setDocumentName(self, name: str, /) -> None:
```

Associate the dialog with one document name.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 960.

## `FreeCADGui._TaskDialog.isAllowedAlterDocument`

```python
def isAllowedAlterDocument(self) -> bool:
```

Return whether the dialog may alter the document.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 964.

## `FreeCADGui._TaskDialog.isAllowedAlterView`

```python
def isAllowedAlterView(self) -> bool:
```

Return whether the dialog may alter the view.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 968.

## `FreeCADGui._TaskDialog.isAllowedAlterSelection`

```python
def isAllowedAlterSelection(self) -> bool:
```

Return whether the dialog may alter the selection.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 972.

## `FreeCADGui._TaskDialog.needsFullSpace`

```python
def needsFullSpace(self) -> bool:
```

Return whether the dialog prefers the full task-panel space.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 976.

## `FreeCADGui._TaskDialog.accept`

```python
def accept(self) -> None:
```

Accept the dialog.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 980.

## `FreeCADGui._TaskDialog.reject`

```python
def reject(self) -> None:
```

Reject the dialog.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 984.

