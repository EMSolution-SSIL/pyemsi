# `FreeCADGui._Control`

[Module](index.md)

```python
class _Control:
```

Class purpose undocumented in this stub.

Evidence: public stub `FreeCADGui/__init__.pyi` line 752. Inherited members are on the named base's reference; aliases keep their imported identity.

Underscored typing/support name: verify runtime exposure and support status before using it.

## `FreeCADGui._Control.showDialog`

```python
def showDialog(self, dialog: object, document: Document | None=None, /) -> _TaskDialog:
```

Show one task dialog, optionally for a specific document.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 754.

## `FreeCADGui._Control.activeDialog`

```python
def activeDialog(self, document: Document | None=None, /) -> bool:
```

Return whether a task dialog is active.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 758.

## `FreeCADGui._Control.activeTaskDialog`

```python
def activeTaskDialog(self, document: Document | None=None, /) -> _TaskDialog | None:
```

Return the active task dialog, if any.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 762.

## `FreeCADGui._Control.closeDialog`

```python
def closeDialog(self, document: Document | None=None, /) -> None:
```

Close the active task dialog.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 766.

## `FreeCADGui._Control.addTaskWatcher`

```python
def addTaskWatcher(self, watchers: Sequence[object], /) -> None:
```

Register one sequence of task watcher objects.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 770.

## `FreeCADGui._Control.clearTaskWatcher`

```python
def clearTaskWatcher(self) -> None:
```

Clear the registered task watchers.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 774.

## `FreeCADGui._Control.isAllowedAlterDocument`

```python
def isAllowedAlterDocument(self, document: Document | None=None, /) -> bool:
```

Return whether the active task dialog may alter the document.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 778.

## `FreeCADGui._Control.isAllowedAlterView`

```python
def isAllowedAlterView(self, document: Document | None=None, /) -> bool:
```

Return whether the active task dialog may alter the view.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 782.

## `FreeCADGui._Control.isAllowedAlterSelection`

```python
def isAllowedAlterSelection(self, document: Document | None=None, /) -> bool:
```

Return whether the active task dialog may alter the selection.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 786.

## `FreeCADGui._Control.showTaskView`

```python
def showTaskView(self) -> None:
```

Show the task view pane.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 790.

## `FreeCADGui._Control.showModelView`

```python
def showModelView(self) -> None:
```

Show the model view pane.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 794.

