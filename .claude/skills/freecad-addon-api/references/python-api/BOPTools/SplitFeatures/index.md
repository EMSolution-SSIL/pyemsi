# Python source module `BOPTools.SplitFeatures`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Part/BOPTools/SplitFeatures.py`. Import path is source-routed; installed availability is unverified.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### from . import SplitAPI

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `BOPTools.SplitFeatures.SplitAPI` -> `BOPTools.SplitAPI`.

[Source module `BOPTools`](../index.md).

Evidence: `src/Mod/Part/BOPTools/SplitFeatures.py:30`.

### import FreeCAD

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `BOPTools.SplitFeatures.FreeCAD` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Part/BOPTools/SplitFeatures.py:31`.

### import Part

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `BOPTools.SplitFeatures.Part` -> `Part`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Part/BOPTools/SplitFeatures.py:32`.

### import FreeCADGui

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if FreeCAD.GuiUp`.

Bound source name `BOPTools.SplitFeatures.FreeCADGui` -> `FreeCADGui`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Part/BOPTools/SplitFeatures.py:35`.

### from PySide import QtCore, QtGui

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if FreeCAD.GuiUp`.

Bound source name `BOPTools.SplitFeatures.QtCore` -> `PySide.QtCore`.

Bound source name `BOPTools.SplitFeatures.QtGui` -> `PySide.QtGui`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Part/BOPTools/SplitFeatures.py:36`.

## Classes

- [BOPTools.SplitFeatures.FeatureBooleanFragments](FeatureBooleanFragments.md)
- [BOPTools.SplitFeatures.ViewProviderBooleanFragments](ViewProviderBooleanFragments.md)
- [BOPTools.SplitFeatures.CommandBooleanFragments](CommandBooleanFragments.md)
- [BOPTools.SplitFeatures.FeatureSlice](FeatureSlice.md)
- [BOPTools.SplitFeatures.ViewProviderSlice](ViewProviderSlice.md)
- [BOPTools.SplitFeatures.CommandSlice](CommandSlice.md)
- [BOPTools.SplitFeatures.CommandSliceApart](CommandSliceApart.md)
- [BOPTools.SplitFeatures.FeatureXOR](FeatureXOR.md)
- [BOPTools.SplitFeatures.ViewProviderXOR](ViewProviderXOR.md)
- [BOPTools.SplitFeatures.CommandXOR](CommandXOR.md)

## `BOPTools.SplitFeatures.translate`

Status: source-defined name; no independently verified stability/export guarantee.

Conditions: `if FreeCAD.GuiUp`.

```python
translate = FreeCAD.Qt.translate
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/Part/BOPTools/SplitFeatures.py:48`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.SplitFeatures.getIconPath`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getIconPath(icon_dot_svg):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/SplitFeatures.py:52`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.SplitFeatures.makeBooleanFragments`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeBooleanFragments(name):
```

makeBooleanFragments(name): makes an BooleanFragments object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/SplitFeatures.py:61`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.SplitFeatures.cmdCreateBooleanFragmentsFeature`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def cmdCreateBooleanFragmentsFeature(name, mode):
```

cmdCreateBooleanFragmentsFeature(name, mode): implementation of GUI command to create
BooleanFragments feature (GFA). Mode can be "Standard", "Split", or "CompSolid".

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/SplitFeatures.py:167`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.SplitFeatures.makeSlice`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeSlice(name):
```

makeSlice(name): makes an Slice object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/SplitFeatures.py:260`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.SplitFeatures.cmdCreateSliceFeature`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def cmdCreateSliceFeature(name, mode, transaction=True):
```

cmdCreateSliceFeature(name, mode): implementation of GUI command to create
Slice feature. Mode can be "Standard", "Split", or "CompSolid".

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/SplitFeatures.py:371`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.SplitFeatures.cmdSliceApart`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def cmdSliceApart():
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/SplitFeatures.py:423`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.SplitFeatures.makeXOR`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeXOR(name):
```

makeXOR(name): makes an XOR object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/SplitFeatures.py:520`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.SplitFeatures.cmdCreateXORFeature`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def cmdCreateXORFeature(name):
```

cmdCreateXORFeature(name): implementation of GUI command to create
XOR feature (GFA). Mode can be "Standard", "Split", or "CompSolid".

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/SplitFeatures.py:616`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.SplitFeatures.addCommands`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def addCommands():
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/SplitFeatures.py:706`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`BOPTools.SplitFeatures.__title__`, `BOPTools.SplitFeatures.__author__`, `BOPTools.SplitFeatures.__url__`, `BOPTools.SplitFeatures.__doc__`, `BOPTools.SplitFeatures._fromUtf8`. These are source internals unless an explicit export establishes otherwise.

