# `FreeCADGui`

[Catalogue index](../index.md)

Evidence: import-shaped public stub `FreeCADGui/__init__.pyi`; generated binding/typing declarations, runtime unverified.

[part 1](index.md) | [part 2](index-2.md)

## `FreeCADGui.show`

```python
@deprecated('since FreeCAD 26.3 and will be removed in FreeCAD 27.2; use showObject instead.')
def show(name: str, /) -> None:
```

Show one named object in the active GUI document. Deprecated.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 648.

## `FreeCADGui.showDownloads`

```python
def showDownloads() -> None:
```

Open the downloads manager window.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 652.

## `FreeCADGui.showMainWindow`

```python
def showMainWindow(inThread: bool=False, /) -> None:
```

Create the main application window if needed, then show it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 656.

## `FreeCADGui.showObject`

```python
def showObject(obj: DocumentObject, /) -> None:
```

Show one document object in the GUI.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 660.

## `FreeCADGui.showPreferences`

```python
def showPreferences(grp: str='', index: int=0, /) -> None:
```

Open the preferences dialog to one group and page index.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 664.

## `FreeCADGui.showPreferencesByName`

```python
def showPreferencesByName(grp: str, pagename: str='', /) -> None:
```

Open the preferences dialog to one group and page name.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 668.

## `FreeCADGui.subgraphFromObject`

```python
def subgraphFromObject(obj: DocumentObject, /) -> object | None:
```

Return the Coin/Inventor scene subgraph that represents one document object.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 672.

## `FreeCADGui.supportedLocales`

```python
def supportedLocales() -> dict[str, str]:
```

Return supported GUI locales, mapping language names to domain codes.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 676.

## `FreeCADGui.suspendWaitCursor`

```python
def suspendWaitCursor() -> None:
```

Temporarily suspend the application's wait cursor and event filter.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 680.

## `FreeCADGui.updateGui`

```python
def updateGui() -> None:
```

Process pending GUI updates.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 684.

## `FreeCADGui.updateLocale`

```python
def updateLocale() -> None:
```

Reload GUI translation state after locale changes.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 688.

## `FreeCADGui.Control`

```python
Control: _Control
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 797.

