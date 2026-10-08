# Python source module `TechDrawTools.TDToolsUtil`

[Python catalogue](../../index.md)

Evidence: `src/Mod/TechDraw/TechDrawTools/TDToolsUtil.py`. Import path is source-routed; installed availability is unverified.

Provides utility functions for TD Tools.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `TechDrawTools.TDToolsUtil.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/TechDraw/TechDrawTools/TDToolsUtil.py:25`.

### import FreeCADGui as Gui

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `TechDrawTools.TDToolsUtil.Gui` -> `FreeCADGui`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/TechDraw/TechDrawTools/TDToolsUtil.py:26`.

### import Part

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `TechDrawTools.TDToolsUtil.Part` -> `Part`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/TechDraw/TechDrawTools/TDToolsUtil.py:27`.

### from PySide.QtCore import QT_TRANSLATE_NOOP

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `TechDrawTools.TDToolsUtil.QT_TRANSLATE_NOOP` -> `PySide.QtCore.QT_TRANSLATE_NOOP`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/TechDraw/TechDrawTools/TDToolsUtil.py:28`.

### from PySide import QtGui

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `TechDrawTools.TDToolsUtil.QtGui` -> `PySide.QtGui`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/TechDraw/TechDrawTools/TDToolsUtil.py:29`.

### from PySide.QtGui import QMessageBox

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `TechDrawTools.TDToolsUtil.QMessageBox` -> `PySide.QtGui.QMessageBox`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/TechDraw/TechDrawTools/TDToolsUtil.py:30`.

## `TechDrawTools.TDToolsUtil.havePage`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def havePage():
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/TechDraw/TechDrawTools/TDToolsUtil.py:32`. Decorators are copied as source expressions and have not been executed.

## `TechDrawTools.TDToolsUtil.haveView`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def haveView():
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/TechDraw/TechDrawTools/TDToolsUtil.py:39`. Decorators are copied as source expressions and have not been executed.

## `TechDrawTools.TDToolsUtil.displayMessage`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def displayMessage(title, message):
```

displayMessage('Title','Messagetext')

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/TechDraw/TechDrawTools/TDToolsUtil.py:46`. Decorators are copied as source expressions and have not been executed.

## `TechDrawTools.TDToolsUtil.getSelView`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getSelView(nSel=0):
```

view = getSelView()
nSel=0 ... number of selected view, 0 = first selected
Return selected view, otherwise return False

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/TechDraw/TechDrawTools/TDToolsUtil.py:56`. Decorators are copied as source expressions and have not been executed.

## `TechDrawTools.TDToolsUtil.getSelVertexes`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getSelVertexes(nVertex=1, nSel=0):
```

vertexes = getSelVertexes(nVertex)
nVertex=1 ... min. number of selected vertexes
nSel=0 ... number of selected view, 0 = first selected
Return a list of selected vertexes if at least nVertex vertexes are selected, otherwise return False

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/TechDraw/TechDrawTools/TDToolsUtil.py:68`. Decorators are copied as source expressions and have not been executed.

## `TechDrawTools.TDToolsUtil.getSelEdges`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getSelEdges(nEdge=1, nSel=0):
```

edges = getSelEdges(nEdge)
nEdge=1 ... min. number of selected edges
nSel=0 ... number of selected view, 0 = first selected
Return a list of selected edges if at least nedge edges are selected, otherwise return False

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/TechDraw/TechDrawTools/TDToolsUtil.py:99`. Decorators are copied as source expressions and have not been executed.

## `TechDrawTools.TDToolsUtil.getCoordinateVectors`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getCoordinateVectors(view):
```

(px,py,pz) = getCoordinateVectors(view)
view ... selected view
(px,py,pz) ... returned tuple of vectors (App.Vector)
calculate projected vectors of x-, y- and z-axis

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/TechDraw/TechDrawTools/TDToolsUtil.py:130`. Decorators are copied as source expressions and have not been executed.

## `TechDrawTools.TDToolsUtil.getSelVertexNames`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getSelVertexNames(nVertex=1, nSel=0):
```

vertexNames = getSelVertexNames(nVertex)
nVertex=1 ... min. number of selected vertexes
nSel=0 ... number of selected view, 0 = first selected
Return a list of the names of the selected vertexes if at least nVertex vertexes are selected, otherwise return False

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/TechDraw/TechDrawTools/TDToolsUtil.py:163`. Decorators are copied as source expressions and have not been executed.

## `TechDrawTools.TDToolsUtil.getSelEdgeNames`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getSelEdgeNames(nEdge=1, nSel=0):
```

edges = getSelEdgeNames(nEdge)
nEdge=1 ... min. number of selected edges
nSel=0 ... number of selected view, 0 = first selected
Return a list of names for selected edges if at least nedge edges are selected, otherwise return False

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/TechDraw/TechDrawTools/TDToolsUtil.py:195`. Decorators are copied as source expressions and have not been executed.

