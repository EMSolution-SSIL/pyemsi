# Python source module `BOPTools.ToleranceFeatures`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Part/BOPTools/ToleranceFeatures.py`. Import path is source-routed; installed availability is unverified.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import FreeCAD

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `BOPTools.ToleranceFeatures.FreeCAD` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Part/BOPTools/ToleranceFeatures.py:29`.

### import Part

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `BOPTools.ToleranceFeatures.Part` -> `Part`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Part/BOPTools/ToleranceFeatures.py:30`.

### import FreeCADGui

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if FreeCAD.GuiUp`.

Bound source name `BOPTools.ToleranceFeatures.FreeCADGui` -> `FreeCADGui`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Part/BOPTools/ToleranceFeatures.py:33`.

### from PySide import QtCore, QtGui

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if FreeCAD.GuiUp`.

Bound source name `BOPTools.ToleranceFeatures.QtCore` -> `PySide.QtCore`.

Bound source name `BOPTools.ToleranceFeatures.QtGui` -> `PySide.QtGui`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Part/BOPTools/ToleranceFeatures.py:34`.

## Classes

- [BOPTools.ToleranceFeatures.FeatureToleranceSet](FeatureToleranceSet.md)
- [BOPTools.ToleranceFeatures.ViewProviderToleranceSet](ViewProviderToleranceSet.md)
- [BOPTools.ToleranceFeatures.CommandToleranceSet](CommandToleranceSet.md)

## `BOPTools.ToleranceFeatures.translate`

Status: source-defined name; no independently verified stability/export guarantee.

Conditions: `if FreeCAD.GuiUp`.

```python
translate = FreeCAD.Qt.translate
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/Part/BOPTools/ToleranceFeatures.py:47`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.ToleranceFeatures.getParamRefine`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getParamRefine():
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/ToleranceFeatures.py:51`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.ToleranceFeatures.cmdCreateToleranceSetFeature`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def cmdCreateToleranceSetFeature(name, minTolerance=1e-07, maxTolerance=0):
```

cmdCreateToleranceSetFeature(name, minTolerance, maxTolerance): generalized implementation of GUI commands.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/ToleranceFeatures.py:57`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.ToleranceFeatures.getIconPath`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getIconPath(icon_dot_svg):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/ToleranceFeatures.py:108`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.ToleranceFeatures.makeToleranceSet`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeToleranceSet(name):
```

makeToleranceSet(name): makes an ToleranceSet object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/ToleranceFeatures.py:117`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.ToleranceFeatures.addCommands`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def addCommands():
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/ToleranceFeatures.py:262`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`BOPTools.ToleranceFeatures.__title__`, `BOPTools.ToleranceFeatures.__author__`, `BOPTools.ToleranceFeatures.__url__`, `BOPTools.ToleranceFeatures.__doc__`, `BOPTools.ToleranceFeatures._fromUtf8`. These are source internals unless an explicit export establishes otherwise.

