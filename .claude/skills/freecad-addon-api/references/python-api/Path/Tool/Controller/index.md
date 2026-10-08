# Python source module `Path.Tool.Controller`

[Python catalogue](../../../index.md)

Evidence: `src/Mod/CAM/Path/Tool/Controller.py`. Import path is source-routed; installed availability is unverified.

Tool Controller defines tool, spindle speed and feed rates for CAM Operations

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### from PySide.QtCore import QT_TRANSLATE_NOOP

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Path.Tool.Controller.QT_TRANSLATE_NOOP` -> `PySide.QtCore.QT_TRANSLATE_NOOP`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/CAM/Path/Tool/Controller.py:27`.

### import FreeCAD

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Path.Tool.Controller.FreeCAD` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/CAM/Path/Tool/Controller.py:28`.

### import Path

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Path.Tool.Controller.Path` -> `Path`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/CAM/Path/Tool/Controller.py:29`.

### from Path.Tool.toolbit import ToolBit

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Path.Tool.Controller.ToolBit` -> `Path.Tool.toolbit.ToolBit`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/CAM/Path/Tool/Controller.py:30`.

### import Path.Base.Generator.toolchange as toolchange

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Path.Tool.Controller.toolchange` -> `Path.Base.Generator.toolchange`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/CAM/Path/Tool/Controller.py:31`.

### import Path.Dressup.Utils as PathDressup

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Path.Tool.Controller.PathDressup` -> `Path.Dressup.Utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/CAM/Path/Tool/Controller.py:32`.

## Classes

- [Path.Tool.Controller.ToolControllerTemplate](ToolControllerTemplate.md)
- [Path.Tool.Controller.ToolController](ToolController.md)

## `Path.Tool.Controller.translate`

Status: source-defined name; no independently verified stability/export guarantee.

```python
translate = FreeCAD.Qt.translate
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/CAM/Path/Tool/Controller.py:40`. Decorators are copied as source expressions and have not been executed.

## `Path.Tool.Controller.Create`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def Create(name='TC: 5mm Endmill', tool=None, toolNumber=1, assignViewProvider=True, assignTool=True):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Tool/Controller.py:468`. Decorators are copied as source expressions and have not been executed.

## `Path.Tool.Controller.copyTC`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def copyTC(tc, job):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Tool/Controller.py:504`. Decorators are copied as source expressions and have not been executed.

## `Path.Tool.Controller.FromTemplate`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def FromTemplate(template, assignViewProvider=True):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Tool/Controller.py:524`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`Path.Tool.Controller._migrateRampDressups`. These are source internals unless an explicit export establishes otherwise.

