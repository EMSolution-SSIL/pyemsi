# Python source module `WorkingPlane`

[Python catalogue](../index.md)

Evidence: `src/Mod/Draft/WorkingPlane.py`. Import path is source-routed; installed availability is unverified.

Provide the working plane code and utilities for the Draft Workbench.

This module provides the plane class which provides a virtual working plane
in FreeCAD and a couple of utility functions.
The working plane is mostly intended to be used in the Draft Workbench
to draw 2D objects in various orientations, not only in the standard XY,
YZ, and XZ planes.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import math

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `WorkingPlane.math` -> `math`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/WorkingPlane.py:40`.

### import lazy_loader.lazy_loader as lz

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `WorkingPlane.lz` -> `lazy_loader.lazy_loader`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/WorkingPlane.py:41`.

### from PySide.QtCore import QT_TRANSLATE_NOOP

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `WorkingPlane.QT_TRANSLATE_NOOP` -> `PySide.QtCore.QT_TRANSLATE_NOOP`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/WorkingPlane.py:42`.

### import FreeCAD

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `WorkingPlane.FreeCAD` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/WorkingPlane.py:44`.

### import DraftVecUtils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `WorkingPlane.DraftVecUtils` -> `DraftVecUtils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/WorkingPlane.py:45`.

### from FreeCAD import Vector

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `WorkingPlane.Vector` -> `FreeCAD.Vector`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/WorkingPlane.py:46`.

### from draftgeoutils import geometry as geo_geometry

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `WorkingPlane.geo_geometry` -> `draftgeoutils.geometry`.

[Source module `draftgeoutils`](../draftgeoutils/index.md).

Evidence: `src/Mod/Draft/WorkingPlane.py:47`.

### from draftutils import gui_utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `WorkingPlane.gui_utils` -> `draftutils.gui_utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/WorkingPlane.py:48`.

### from draftutils import params

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `WorkingPlane.params` -> `draftutils.params`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/WorkingPlane.py:49`.

### from draftutils import utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `WorkingPlane.utils` -> `draftutils.utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/WorkingPlane.py:50`.

### from draftutils.messages import _wrn

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `WorkingPlane._wrn` -> `draftutils.messages._wrn`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/WorkingPlane.py:51`.

### from draftutils.translate import translate

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `WorkingPlane.translate` -> `draftutils.translate.translate`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/WorkingPlane.py:52`.

### from PySide import QtWidgets

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if FreeCAD.GuiUp`.

Bound source name `WorkingPlane.QtWidgets` -> `PySide.QtWidgets`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/WorkingPlane.py:1964`.

### from draftutils.todo import ToDo

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if FreeCAD.GuiUp`.

Bound source name `WorkingPlane.ToDo` -> `draftutils.todo.ToDo`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/WorkingPlane.py:1965`.

## Classes

- [WorkingPlane.PlaneBase](PlaneBase.md)
- [WorkingPlane.Plane](Plane.md)
- [WorkingPlane.PlaneGui](PlaneGui.md)

## `WorkingPlane.plane`

Status: source-defined name; no independently verified stability/export guarantee.

```python
plane = Plane
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/Draft/WorkingPlane.py:1269`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.get_working_plane`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_working_plane(update=True):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:1932`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.getPlacementFromPoints`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getPlacementFromPoints(points):
```

Return a placement from a list of 3 or 4 points. The 4th point is no longer used.

Calls draftgeoutils.geometry.placement_from_points(). See there.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:2007`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.getPlacementFromFace`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getPlacementFromFace(face, rotated=False):
```

Return a placement from a face.

Calls draftgeoutils.geometry.placement_from_face(). See there.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:2017`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`WorkingPlane.__title__`, `WorkingPlane.__author__`, `WorkingPlane.__url__`, `WorkingPlane._update_gui`, `WorkingPlane._view_observer_callback`, `WorkingPlane._view_observer_active`, `WorkingPlane._view_observer_start`, `WorkingPlane._view_observer_stop`. These are source internals unless an explicit export establishes otherwise.

