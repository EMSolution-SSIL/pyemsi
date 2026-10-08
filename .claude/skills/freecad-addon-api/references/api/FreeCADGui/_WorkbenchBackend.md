# `FreeCADGui._WorkbenchBackend`

[Module](index.md)

```python
class _WorkbenchBackend(Protocol):
```

Protocol for the mutable backend object behind one GUI workbench.

Evidence: public stub `FreeCADGui/__init__.pyi` line 215. Inherited members are on the named base's reference; aliases keep their imported identity.

Underscored typing/support name: verify runtime exposure and support status before using it.

## `FreeCADGui._WorkbenchBackend.appendToolbar`

```python
def appendToolbar(self, name: str, cmds: Sequence[str], /) -> None:
```

Add one toolbar definition to the workbench.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 218.

## `FreeCADGui._WorkbenchBackend.removeToolbar`

```python
def removeToolbar(self, name: str, /) -> None:
```

Remove one toolbar definition from the workbench.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 222.

## `FreeCADGui._WorkbenchBackend.listToolbars`

```python
def listToolbars(self) -> list[str]:
```

Return the toolbar names registered on the workbench.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 226.

## `FreeCADGui._WorkbenchBackend.getToolbarItems`

```python
def getToolbarItems(self) -> dict[str, list[str]]:
```

Return toolbar contents keyed by toolbar name.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 230.

## `FreeCADGui._WorkbenchBackend.appendCommandbar`

```python
def appendCommandbar(self, name: str, cmds: Sequence[str], /) -> None:
```

Add one command bar definition to the workbench.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 234.

## `FreeCADGui._WorkbenchBackend.removeCommandbar`

```python
def removeCommandbar(self, name: str, /) -> None:
```

Remove one command bar definition from the workbench.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 238.

## `FreeCADGui._WorkbenchBackend.listCommandbars`

```python
def listCommandbars(self) -> list[str]:
```

Return the command bar names registered on the workbench.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 242.

## `FreeCADGui._WorkbenchBackend.appendMenu`

```python
def appendMenu(self, name: _WorkbenchMenu, cmds: _WorkbenchCommands, /) -> None:
```

Add one menu definition to the workbench.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 246.

## `FreeCADGui._WorkbenchBackend.removeMenu`

```python
def removeMenu(self, name: _WorkbenchMenu, /) -> None:
```

Remove one menu definition from the workbench.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 250.

## `FreeCADGui._WorkbenchBackend.listMenus`

```python
def listMenus(self) -> list[str]:
```

Return the menu labels registered on the workbench.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 254.

## `FreeCADGui._WorkbenchBackend.appendContextMenu`

```python
def appendContextMenu(self, name: str, cmds: _WorkbenchCommands, /) -> None:
```

Add one context-menu definition to the workbench.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 258.

## `FreeCADGui._WorkbenchBackend.removeContextMenu`

```python
def removeContextMenu(self, name: str, /) -> None:
```

Remove one context-menu definition from the workbench.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 262.

## `FreeCADGui._WorkbenchBackend.reloadActive`

```python
def reloadActive(self) -> None:
```

Reload the active workbench presentation.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 266.

## `FreeCADGui._WorkbenchBackend.name`

```python
def name(self) -> str:
```

Return the internal backend name of the workbench.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 270.

