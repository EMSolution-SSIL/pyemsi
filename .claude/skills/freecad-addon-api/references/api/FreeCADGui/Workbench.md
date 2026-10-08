# `FreeCADGui.Workbench`

[Module](index.md)

```python
class Workbench:
```

Base class for Python-defined GUI workbenches.

Evidence: public stub `FreeCADGui/__init__.pyi` line 274. Inherited members are on the named base's reference; aliases keep their imported identity.

## `FreeCADGui.Workbench.MenuText`

```python
MenuText: ClassVar[str]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 276.

## `FreeCADGui.Workbench.ToolTip`

```python
ToolTip: ClassVar[str]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 277.

## `FreeCADGui.Workbench.Icon`

```python
Icon: ClassVar[object | None]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 278.

## `FreeCADGui.Workbench.__Workbench__`

```python
__Workbench__: _WorkbenchBackend
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 279.

## `FreeCADGui.Workbench.Initialize`

```python
def Initialize(self) -> None:
```

Initialize the workbench after registration.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 281.

## `FreeCADGui.Workbench.ContextMenu`

```python
def ContextMenu(self, recipient: object, /) -> None:
```

Populate the context menu for one recipient object.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 285.

## `FreeCADGui.Workbench.appendToolbar`

```python
def appendToolbar(self, name: str, cmds: Sequence[str], /) -> None:
```

Add one toolbar definition to the workbench.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 289.

## `FreeCADGui.Workbench.removeToolbar`

```python
def removeToolbar(self, name: str, /) -> None:
```

Remove one toolbar definition from the workbench.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 293.

## `FreeCADGui.Workbench.listToolbars`

```python
def listToolbars(self) -> list[str]:
```

Return the toolbar names registered on the workbench.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 297.

## `FreeCADGui.Workbench.getToolbarItems`

```python
def getToolbarItems(self) -> dict[str, list[str]]:
```

Return toolbar contents keyed by toolbar name.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 301.

## `FreeCADGui.Workbench.appendCommandbar`

```python
def appendCommandbar(self, name: str, cmds: Sequence[str], /) -> None:
```

Add one command bar definition to the workbench.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 305.

## `FreeCADGui.Workbench.removeCommandbar`

```python
def removeCommandbar(self, name: str, /) -> None:
```

Remove one command bar definition from the workbench.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 309.

## `FreeCADGui.Workbench.listCommandbars`

```python
def listCommandbars(self) -> list[str]:
```

Return the command bar names registered on the workbench.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 313.

## `FreeCADGui.Workbench.appendMenu`

```python
def appendMenu(self, name: _WorkbenchMenu, cmds: _WorkbenchCommands, /) -> None:
```

Add one menu definition to the workbench.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 317.

## `FreeCADGui.Workbench.removeMenu`

```python
def removeMenu(self, name: _WorkbenchMenu, /) -> None:
```

Remove one menu definition from the workbench.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 321.

## `FreeCADGui.Workbench.listMenus`

```python
def listMenus(self) -> list[str]:
```

Return the menu labels registered on the workbench.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 325.

## `FreeCADGui.Workbench.appendContextMenu`

```python
def appendContextMenu(self, name: str, cmds: _WorkbenchCommands, /) -> None:
```

Add one context-menu definition to the workbench.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 329.

## `FreeCADGui.Workbench.removeContextMenu`

```python
def removeContextMenu(self, name: str, /) -> None:
```

Remove one context-menu definition from the workbench.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 333.

## `FreeCADGui.Workbench.reloadActive`

```python
def reloadActive(self) -> None:
```

Reload the active workbench presentation.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 337.

## `FreeCADGui.Workbench.name`

```python
def name(self) -> str:
```

Return the exposed name of the workbench.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 341.

## `FreeCADGui.Workbench.GetClassName`

```python
def GetClassName(self) -> str:
```

Return the wrapped runtime class name.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 345.

