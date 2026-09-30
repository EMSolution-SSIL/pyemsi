# `FreeCADGui.UiLoader`

[Module](index.md)

```python
class UiLoader:
```

Class purpose undocumented in this stub.

Evidence: public stub `FreeCADGui/__init__.pyi` line 1050. Inherited members are on the named base's reference; aliases keep their imported identity.

## `FreeCADGui.UiLoader.load`

```python
def load(self, source: str | PathLike[str] | object, parent: object | None=None, /) -> object | None:
```

Load one `.ui` source and return the created widget tree.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1052.

## `FreeCADGui.UiLoader.createWidget`

```python
def createWidget(self, class_name: str, parent: object | None=None, name: str='', /) -> object | None:
```

Create one widget by Qt class name.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1056.

## `FreeCADGui.UiLoader.availableWidgets`

```python
def availableWidgets(self) -> list[str]:
```

Return the widget classes the loader can create.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1060.

## `FreeCADGui.UiLoader.clearPluginPaths`

```python
def clearPluginPaths(self) -> None:
```

Remove all custom plugin search paths.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1064.

## `FreeCADGui.UiLoader.pluginPaths`

```python
def pluginPaths(self) -> list[str]:
```

Return the current custom plugin search paths.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1068.

## `FreeCADGui.UiLoader.addPluginPath`

```python
def addPluginPath(self, path: str | PathLike[str], /) -> None:
```

Add one custom plugin search path.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1072.

## `FreeCADGui.UiLoader.errorString`

```python
def errorString(self) -> str:
```

Return the most recent loader error string.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1076.

## `FreeCADGui.UiLoader.isLanguageChangeEnabled`

```python
def isLanguageChangeEnabled(self) -> bool:
```

Return whether live language-change handling is enabled.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1080.

## `FreeCADGui.UiLoader.setLanguageChangeEnabled`

```python
def setLanguageChangeEnabled(self, enabled: bool, /) -> None:
```

Enable or disable live language-change handling.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1084.

## `FreeCADGui.UiLoader.setWorkingDirectory`

```python
def setWorkingDirectory(self, path: str | PathLike[str], /) -> None:
```

Set the working directory used for relative UI resources.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1088.

## `FreeCADGui.UiLoader.workingDirectory`

```python
def workingDirectory(self) -> str:
```

Return the current working directory used for UI resources.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1092.

