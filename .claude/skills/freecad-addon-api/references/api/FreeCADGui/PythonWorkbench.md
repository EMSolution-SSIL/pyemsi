# `FreeCADGui.PythonWorkbench`

[Module](index.md)

```python
class PythonWorkbench(Workbench):
```

This is the class for Python workbenches

Author: Werner Mayer (wmayer@users.sourceforge.net)
Licence: LGPL

Evidence: public stub `FreeCADGui/__init__.pyi` line 2407. Inherited members are on the named base's reference; aliases keep their imported identity.

## `FreeCADGui.PythonWorkbench.appendMenu`

```python
def appendMenu(self, path: str | list[str], items: str | list[str], /) -> None:
```

Append a new menu

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2415.

## `FreeCADGui.PythonWorkbench.removeMenu`

```python
def removeMenu(self, name: str, /) -> None:
```

Remove a menu

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2421.

## `FreeCADGui.PythonWorkbench.appendContextMenu`

```python
def appendContextMenu(self, path: str | list[str], items: str | list[str], /) -> None:
```

Append a new context menu item

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2427.

## `FreeCADGui.PythonWorkbench.removeContextMenu`

```python
def removeContextMenu(self, name: str, /) -> None:
```

Remove a context menu item

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2433.

## `FreeCADGui.PythonWorkbench.appendToolbar`

```python
def appendToolbar(self, name: str, commands: list[str], /) -> None:
```

Append a new toolbar

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2439.

## `FreeCADGui.PythonWorkbench.removeToolbar`

```python
def removeToolbar(self, name: str, /) -> None:
```

Remove a toolbar

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2445.

## `FreeCADGui.PythonWorkbench.appendCommandbar`

```python
def appendCommandbar(self, name: str, commands: list[str], /) -> None:
```

Append a new command bar

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2451.

## `FreeCADGui.PythonWorkbench.removeCommandbar`

```python
def removeCommandbar(self, name: str, /) -> None:
```

Remove a command bar

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2457.

## `FreeCADGui.PythonWorkbench.AppendMenu`

```python
@deprecated('since FreeCAD 26.3 and will be removed in FreeCAD 27.2; use appendMenu instead.')
def AppendMenu(self, path: str | list[str], items: str | list[str], /) -> None:
```

deprecated -- use appendMenu

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2464.

## `FreeCADGui.PythonWorkbench.RemoveMenu`

```python
@deprecated('since FreeCAD 26.3 and will be removed in FreeCAD 27.2; use removeMenu instead.')
def RemoveMenu(self, name: str, /) -> None:
```

deprecated -- use removeMenu

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2471.

## `FreeCADGui.PythonWorkbench.ListMenus`

```python
@deprecated('since FreeCAD 26.3 and will be removed in FreeCAD 27.2; use listMenus instead.')
def ListMenus(self) -> List[Any]:
```

deprecated -- use listMenus

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2478.

## `FreeCADGui.PythonWorkbench.AppendContextMenu`

```python
@deprecated('since FreeCAD 26.3 and will be removed in FreeCAD 27.2; use appendContextMenu instead.')
def AppendContextMenu(self, path: str | list[str], items: str | list[str], /) -> None:
```

deprecated -- use appendContextMenu

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2485.

## `FreeCADGui.PythonWorkbench.RemoveContextMenu`

```python
@deprecated('since FreeCAD 26.3 and will be removed in FreeCAD 27.2; use removeContextMenu instead.')
def RemoveContextMenu(self, name: str, /) -> None:
```

deprecated -- use removeContextMenu

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2492.

## `FreeCADGui.PythonWorkbench.AppendToolbar`

```python
@deprecated('since FreeCAD 26.3 and will be removed in FreeCAD 27.2; use appendToolbar instead.')
def AppendToolbar(self, name: str, commands: list[str], /) -> None:
```

deprecated -- use appendToolbar

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2499.

## `FreeCADGui.PythonWorkbench.RemoveToolbar`

```python
@deprecated('since FreeCAD 26.3 and will be removed in FreeCAD 27.2; use removeToolbar instead.')
def RemoveToolbar(self, name: str, /) -> None:
```

deprecated -- use removeToolbar

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2506.

## `FreeCADGui.PythonWorkbench.ListToolbars`

```python
@deprecated('since FreeCAD 26.3 and will be removed in FreeCAD 27.2; use listToolbars instead.')
def ListToolbars(self) -> List[Any]:
```

deprecated -- use listToolbars

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2513.

## `FreeCADGui.PythonWorkbench.AppendCommandbar`

```python
@deprecated('since FreeCAD 26.3 and will be removed in FreeCAD 27.2; use appendCommandbar instead.')
def AppendCommandbar(self, name: str, commands: list[str], /) -> None:
```

deprecated -- use appendCommandbar

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2520.

## `FreeCADGui.PythonWorkbench.RemoveCommandbar`

```python
@deprecated('since FreeCAD 26.3 and will be removed in FreeCAD 27.2; use removeCommandbar instead.')
def RemoveCommandbar(self, name: str, /) -> None:
```

deprecated -- use removeCommandbar

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2527.

## `FreeCADGui.PythonWorkbench.ListCommandbars`

```python
@deprecated('since FreeCAD 26.3 and will be removed in FreeCAD 27.2; use listCommandbars instead.')
def ListCommandbars(self) -> List[Any]:
```

deprecated -- use listCommandbars

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2534.

