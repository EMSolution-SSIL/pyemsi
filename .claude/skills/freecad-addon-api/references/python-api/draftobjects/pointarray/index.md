# Python source module `draftobjects.pointarray`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftobjects/pointarray.py`. Import path is source-routed; installed availability is unverified.

Provides the object code for the PointArray object.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### from PySide.QtCore import QT_TRANSLATE_NOOP

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftobjects.pointarray.QT_TRANSLATE_NOOP` -> `PySide.QtCore.QT_TRANSLATE_NOOP`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftobjects/pointarray.py:33`.

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftobjects.pointarray.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftobjects/pointarray.py:35`.

### import DraftVecUtils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftobjects.pointarray.DraftVecUtils` -> `DraftVecUtils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftobjects/pointarray.py:36`.

### import draftutils.utils as utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftobjects.pointarray.utils` -> `draftutils.utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftobjects/pointarray.py:37`.

### from draftutils.messages import _err, _log

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftobjects.pointarray._err` -> `draftutils.messages._err`.

Bound source name `draftobjects.pointarray._log` -> `draftutils.messages._log`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftobjects/pointarray.py:39`.

### from draftutils.translate import translate

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftobjects.pointarray.translate` -> `draftutils.translate.translate`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftobjects/pointarray.py:40`.

### from draftobjects.draftlink import DraftLink

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftobjects.pointarray.DraftLink` -> `draftobjects.draftlink.DraftLink`.

[Source module `draftobjects.draftlink`](../draftlink/index.md).

Evidence: `src/Mod/Draft/draftobjects/pointarray.py:41`.

## Classes

- [draftobjects.pointarray.PointArray](PointArray.md)

## `draftobjects.pointarray.remove_equal_vecs`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def remove_equal_vecs(vec_list):
```

Remove equal vectors from a list.

Parameters
----------
vec_list: list of App.Vectors

Returns
-------
list of App.Vectors

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/pointarray.py:160`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.pointarray.get_point_list`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_point_list(point_object):
```

Extract a list of points from a point object.

Parameters
----------
point_object: Part::Feature, Sketcher::SketchObject, Mesh::Feature
              or Points::FeatureCustom
    The object must have vertices and/or points.

Returns
-------
list of App.Vectors

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/pointarray.py:181`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.pointarray.build_placements`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def build_placements(base_object, pt_list=None, placement=App.Placement()):
```

Build a placements from the base object and list of points.

Returns
-------
list of App.Placements

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/pointarray.py:212`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`draftobjects.pointarray._PointArray`. These are source internals unless an explicit export establishes otherwise.

