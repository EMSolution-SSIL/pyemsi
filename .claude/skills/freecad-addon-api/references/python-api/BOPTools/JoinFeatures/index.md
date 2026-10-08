# Python source module `BOPTools.JoinFeatures`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Part/BOPTools/JoinFeatures.py`. Import path is source-routed; installed availability is unverified.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### from . import JoinAPI

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `BOPTools.JoinFeatures.JoinAPI` -> `BOPTools.JoinAPI`.

[Source module `BOPTools`](../index.md).

Evidence: `src/Mod/Part/BOPTools/JoinFeatures.py:30`.

### import FreeCAD

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `BOPTools.JoinFeatures.FreeCAD` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Part/BOPTools/JoinFeatures.py:31`.

### import Part

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `BOPTools.JoinFeatures.Part` -> `Part`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Part/BOPTools/JoinFeatures.py:32`.

### import FreeCADGui

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if FreeCAD.GuiUp`.

Bound source name `BOPTools.JoinFeatures.FreeCADGui` -> `FreeCADGui`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Part/BOPTools/JoinFeatures.py:35`.

### from PySide import QtCore, QtGui

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if FreeCAD.GuiUp`.

Bound source name `BOPTools.JoinFeatures.QtCore` -> `PySide.QtCore`.

Bound source name `BOPTools.JoinFeatures.QtGui` -> `PySide.QtGui`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Part/BOPTools/JoinFeatures.py:36`.

## Classes

- [BOPTools.JoinFeatures.FeatureConnect](FeatureConnect.md)
- [BOPTools.JoinFeatures.ViewProviderConnect](ViewProviderConnect.md)
- [BOPTools.JoinFeatures.CommandConnect](CommandConnect.md)
- [BOPTools.JoinFeatures.FeatureEmbed](FeatureEmbed.md)
- [BOPTools.JoinFeatures.ViewProviderEmbed](ViewProviderEmbed.md)
- [BOPTools.JoinFeatures.CommandEmbed](CommandEmbed.md)
- [BOPTools.JoinFeatures.FeatureCutout](FeatureCutout.md)
- [BOPTools.JoinFeatures.ViewProviderCutout](ViewProviderCutout.md)
- [BOPTools.JoinFeatures.CommandCutout](CommandCutout.md)

## `BOPTools.JoinFeatures.translate`

Status: source-defined name; no independently verified stability/export guarantee.

Conditions: `if FreeCAD.GuiUp`.

```python
translate = FreeCAD.Qt.translate
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/Part/BOPTools/JoinFeatures.py:51`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.JoinFeatures.getParamRefine`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getParamRefine():
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/JoinFeatures.py:55`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.JoinFeatures.cmdCreateJoinFeature`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def cmdCreateJoinFeature(name, mode):
```

cmdCreateJoinFeature(name, mode): generalized implementation of GUI commands.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/JoinFeatures.py:61`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.JoinFeatures.getIconPath`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getIconPath(icon_dot_svg):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/JoinFeatures.py:114`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.JoinFeatures.makeConnect`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeConnect(name):
```

makeConnect(name): makes an Connect object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/JoinFeatures.py:123`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.JoinFeatures.makeEmbed`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeEmbed(name):
```

makeEmbed(name): makes an Embed object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/JoinFeatures.py:259`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.JoinFeatures.makeCutout`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeCutout(name):
```

makeCutout(name): makes an Cutout object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/JoinFeatures.py:374`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.JoinFeatures.addCommands`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def addCommands():
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/JoinFeatures.py:487`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`BOPTools.JoinFeatures.__title__`, `BOPTools.JoinFeatures.__author__`, `BOPTools.JoinFeatures.__url__`, `BOPTools.JoinFeatures.__doc__`, `BOPTools.JoinFeatures._fromUtf8`. These are source internals unless an explicit export establishes otherwise.

