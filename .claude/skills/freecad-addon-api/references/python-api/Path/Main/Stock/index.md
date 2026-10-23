# Python source module `Path.Main.Stock`

[Python catalogue](../../../index.md)

Evidence: `src/Mod/CAM/Path/Main/Stock.py`. Import path is source-routed; installed availability is unverified.

Used to create material stock around a machined part - for visualization

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import FreeCAD

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Path.Main.Stock.FreeCAD` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/CAM/Path/Main/Stock.py:26`.

### import Path

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Path.Main.Stock.Path` -> `Path`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/CAM/Path/Main/Stock.py:27`.

### import math

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Path.Main.Stock.math` -> `math`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/CAM/Path/Main/Stock.py:28`.

### from PySide.QtCore import QT_TRANSLATE_NOOP

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Path.Main.Stock.QT_TRANSLATE_NOOP` -> `PySide.QtCore.QT_TRANSLATE_NOOP`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/CAM/Path/Main/Stock.py:29`.

### from PySide import QtCore

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Path.Main.Stock.QtCore` -> `PySide.QtCore`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/CAM/Path/Main/Stock.py:30`.

### from lazy_loader.lazy_loader import LazyLoader

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Path.Main.Stock.LazyLoader` -> `lazy_loader.lazy_loader.LazyLoader`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/CAM/Path/Main/Stock.py:33`.

## Classes

- [Path.Main.Stock.StockType](StockType.md)
- [Path.Main.Stock.Stock](Stock.md)
- [Path.Main.Stock.StockFromBase](StockFromBase.md)
- [Path.Main.Stock.StockCreateBox](StockCreateBox.md)
- [Path.Main.Stock.StockCreateCylinder](StockCreateCylinder.md)
- [Path.Main.Stock.FakeJob](FakeJob.md)

## `Path.Main.Stock.translate`

Status: source-defined name; no independently verified stability/export guarantee.

```python
translate = FreeCAD.Qt.translate
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/CAM/Path/Main/Stock.py:37`. Decorators are copied as source expressions and have not been executed.

## `Path.Main.Stock.shapeBoundBox`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def shapeBoundBox(obj):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Main/Stock.py:72`. Decorators are copied as source expressions and have not been executed.

## `Path.Main.Stock.SetupStockObject`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def SetupStockObject(obj, stockType):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Main/Stock.py:380`. Decorators are copied as source expressions and have not been executed.

## `Path.Main.Stock.CreateFromBase`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def CreateFromBase(job, neg=None, pos=None, placement=None):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Main/Stock.py:428`. Decorators are copied as source expressions and have not been executed.

## `Path.Main.Stock.CreateBox`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def CreateBox(job, extent=None, placement=None):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Main/Stock.py:453`. Decorators are copied as source expressions and have not been executed.

## `Path.Main.Stock.CreateCylinder`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def CreateCylinder(job, radius=None, height=None, placement=None, axis=None):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Main/Stock.py:479`. Decorators are copied as source expressions and have not been executed.

## `Path.Main.Stock.TemplateAttributes`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def TemplateAttributes(stock, includeExtent=True, includePlacement=True):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Main/Stock.py:522`. Decorators are copied as source expressions and have not been executed.

## `Path.Main.Stock.CreateFromTemplate`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def CreateFromTemplate(job, template):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Main/Stock.py:559`. Decorators are copied as source expressions and have not been executed.

## `Path.Main.Stock.ApplyStockViewDefaults`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def ApplyStockViewDefaults(stock):
```

Apply default appearance settings to a stock object's ViewObject.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Main/Stock.py:684`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`Path.Main.Stock._getBase`. These are source internals unless an explicit export establishes otherwise.

