# `FreeCADGui.TaskPlacement`

[Module](index.md)

```python
class TaskPlacement:
```

Class purpose undocumented in this stub.

Evidence: public stub `FreeCADGui/__init__.pyi` line 988. Inherited members are on the named base's reference; aliases keep their imported identity.

## `FreeCADGui.TaskPlacement.setPropertyName`

```python
def setPropertyName(self, name: str, /) -> None:
```

Set the placement property name that the dialog edits.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 990.

## `FreeCADGui.TaskPlacement.setPlacement`

```python
def setPlacement(self, placement: Placement, /) -> None:
```

Set the placement currently shown by the dialog.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 994.

## `FreeCADGui.TaskPlacement.setSelection`

```python
def setSelection(self, selection: Sequence[DocumentObject], /) -> None:
```

Set the document-object selection used by the dialog.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 998.

## `FreeCADGui.TaskPlacement.bindObject`

```python
def bindObject(self) -> None:
```

Bind the current placement to the selected object.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1002.

## `FreeCADGui.TaskPlacement.setPlacementAndBindObject`

```python
def setPlacementAndBindObject(self, document_object: DocumentObject, property_name: str, /) -> None:
```

Bind the dialog directly to one object and placement property.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1006.

## `FreeCADGui.TaskPlacement.setIgnoreTransactions`

```python
def setIgnoreTransactions(self, ignore: bool, /) -> None:
```

Enable or disable transaction handling for placement edits.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1010.

## `FreeCADGui.TaskPlacement.showDefaultButtons`

```python
def showDefaultButtons(self, show: bool, /) -> None:
```

Show or hide the default task-panel buttons.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1014.

## `FreeCADGui.TaskPlacement.accept`

```python
def accept(self) -> bool:
```

Accept the current placement edits.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1018.

## `FreeCADGui.TaskPlacement.reject`

```python
def reject(self) -> bool:
```

Reject the current placement edits.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1022.

## `FreeCADGui.TaskPlacement.clicked`

```python
def clicked(self, button: int, /) -> None:
```

Handle one clicked task-panel button.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1026.

## `FreeCADGui.TaskPlacement.open`

```python
def open(self) -> None:
```

Open or initialize the task dialog.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1030.

## `FreeCADGui.TaskPlacement.isAllowedAlterDocument`

```python
def isAllowedAlterDocument(self) -> bool:
```

Return whether the dialog may alter the active document.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1034.

## `FreeCADGui.TaskPlacement.isAllowedAlterView`

```python
def isAllowedAlterView(self) -> bool:
```

Return whether the dialog may alter the active view.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1038.

## `FreeCADGui.TaskPlacement.isAllowedAlterSelection`

```python
def isAllowedAlterSelection(self) -> bool:
```

Return whether the dialog may alter the active selection.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1042.

## `FreeCADGui.TaskPlacement.getStandardButtons`

```python
def getStandardButtons(self) -> int:
```

Return the standard button mask exposed by the dialog.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1046.

