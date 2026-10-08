# `FreeCADGui._MainWindow`

[Module](index.md)

```python
class _MainWindow(QtWidgets.QMainWindow):
```

Class purpose undocumented in this stub.

Evidence: public stub `FreeCADGui/__init__.pyi` line 858. Inherited members are on the named base's reference; aliases keep their imported identity.

Underscored typing/support name: verify runtime exposure and support status before using it.

## `FreeCADGui._MainWindow.getWindows`

```python
def getWindows(self) -> list[_MDIView]:
```

Return the currently open MDI views.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 860.

## `FreeCADGui._MainWindow.getWindowsOfType`

```python
def getWindowsOfType(self, type_id: object, /) -> list[_MDIView]:
```

Return the open MDI views of one runtime type.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 864.

## `FreeCADGui._MainWindow.setActiveWindow`

```python
def setActiveWindow(self, view: _MDIView, /) -> None:
```

Make one MDI view the active window.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 868.

## `FreeCADGui._MainWindow.getActiveWindow`

```python
def getActiveWindow(self) -> _MDIView | None:
```

Return the active MDI view, if any.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 872.

## `FreeCADGui._MainWindow.addWindow`

```python
def addWindow(self, window: object, /) -> _MDIView | None:
```

Add one window object to the MDI area.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 876.

## `FreeCADGui._MainWindow.removeWindow`

```python
def removeWindow(self, view: _MDIView, /) -> None:
```

Remove one MDI view from the main window.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 880.

## `FreeCADGui._MainWindow.showHint`

```python
def showHint(self, *hints: InputHint) -> None:
```

Show one or more input hints in the main window.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 884.

## `FreeCADGui._MainWindow.hideHint`

```python
def hideHint(self) -> None:
```

Hide the currently visible input hints.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 888.

## `FreeCADGui._MainWindow.addStatusBarItem`

```python
def addStatusBarItem(self, *args: Any, **kwargs: Any) -> Any:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 892.

## `FreeCADGui._MainWindow.removeStatusBarItem`

```python
def removeStatusBarItem(self, *args: Any) -> Any:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 895.

