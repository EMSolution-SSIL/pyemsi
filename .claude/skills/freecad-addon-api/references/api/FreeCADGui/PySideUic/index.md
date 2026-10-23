# `FreeCADGui.PySideUic`

[Catalogue index](../../index.md)

Evidence: import-shaped public stub `FreeCADGui/PySideUic.pyi`; generated binding/typing declarations, runtime unverified.

## Imports and aliases

These preserve stub type context and reexports. Imported typing helpers and underscored names are not a promise of supported runtime API.

```python
from __future__ import annotations
from typing import Any
from os import PathLike
from typing import TypeAlias
from Base.Metadata import module
```

## `FreeCADGui.PySideUic._UiPath`

```python
_UiPath: TypeAlias = str | PathLike[str]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/PySideUic.pyi` line(s) 9.

## `FreeCADGui.PySideUic.createCustomWidget`

```python
def createCustomWidget(class_name: str, parent: object | None=None, name: str='', /) -> object | None:
```

Create one FreeCAD custom widget by class name.

Evidence: public stub `FreeCADGui/PySideUic.pyi` line(s) 11.

## `FreeCADGui.PySideUic.loadUi`

```python
def loadUi(ui_file: _UiPath, base: object | None=None, /) -> object | None:
```

Load one Qt Designer `.ui` file and return the created widget tree.

Evidence: public stub `FreeCADGui/PySideUic.pyi` line(s) 15.

## `FreeCADGui.PySideUic.loadUiType`

```python
def loadUiType(ui_file: _UiPath, /) -> tuple[type[object], type[object]] | None:
```

Compile one Qt Designer `.ui` file in memory and return its form and base classes.

Evidence: public stub `FreeCADGui/PySideUic.pyi` line(s) 19.

