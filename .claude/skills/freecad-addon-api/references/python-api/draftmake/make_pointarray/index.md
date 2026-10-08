# Python source module `draftmake.make_pointarray`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftmake/make_pointarray.py`. Import path is source-routed; installed availability is unverified.

Provides functions to create PointArray objects.

The copies will be created at the points of a point object.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_pointarray.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_pointarray.py:40`.

### from draftobjects.pointarray import PointArray

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_pointarray.PointArray` -> `draftobjects.pointarray.PointArray`.

[Source module `draftobjects.pointarray`](../../draftobjects/pointarray/index.md).

Evidence: `src/Mod/Draft/draftmake/make_pointarray.py:41`.

### from draftutils import utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_pointarray.utils` -> `draftutils.utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_pointarray.py:42`.

### from draftutils import gui_utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_pointarray.gui_utils` -> `draftutils.gui_utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_pointarray.py:43`.

### from draftutils.messages import _err

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_pointarray._err` -> `draftutils.messages._err`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_pointarray.py:44`.

### from draftutils.translate import translate

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_pointarray.translate` -> `draftutils.translate.translate`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_pointarray.py:45`.

### from freecad.deprecation import deprecated

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_pointarray.deprecated` -> `freecad.deprecation.deprecated`.

[Source module `freecad.deprecation`](../../freecad/deprecation/index.md).

Evidence: `src/Mod/Draft/draftmake/make_pointarray.py:46`.

### from draftviewproviders.view_array import ViewProviderDraftArray

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if App.GuiUp`.

Bound source name `draftmake.make_pointarray.ViewProviderDraftArray` -> `draftviewproviders.view_array.ViewProviderDraftArray`.

[Source module `draftviewproviders.view_array`](../../draftviewproviders/view_array/index.md).

Evidence: `src/Mod/Draft/draftmake/make_pointarray.py:49`.

### from draftviewproviders.view_draftlink import ViewProviderDraftLink

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if App.GuiUp`.

Bound source name `draftmake.make_pointarray.ViewProviderDraftLink` -> `draftviewproviders.view_draftlink.ViewProviderDraftLink`.

[Source module `draftviewproviders.view_draftlink`](../../draftviewproviders/view_draftlink/index.md).

Evidence: `src/Mod/Draft/draftmake/make_pointarray.py:50`.

## `draftmake.make_pointarray.make_point_array`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def make_point_array(base_object, point_object, extra=None, use_link=True):
```

Make a Draft PointArray object.

Create copies of a `base_object` at the points defined by
a `point_object`.

Parameters
----------
base_object: Part::Feature or str
    Any of object that has a `Part::TopoShape` that can be duplicated.
    This means most 2D and 3D objects produced with any workbench.
    If it is a string, it must be the `Label` of that object.
    Since a label is not guaranteed to be unique in a document,
    it will use the first object found with this label.

point_object: Part::Feature, Sketcher::SketchObject, Mesh::Feature,
              Points::FeatureCustom or str
    The object must have vertices and/or points.

extra: Base::Placement, Base::Vector3, or Base::Rotation, optional
    It defaults to `None`.
    If it is provided, it is an additional placement that is applied
    to each copy of the array.
    The input could be a full placement, just a vector indicating
    the additional translation, or just a rotation.

Returns
-------
Part::FeaturePython
    A scripted object of type `'PointArray'`.
    Its `Shape` is a compound of the copies of the original object.

None
    If there is a problem it will return `None`.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_pointarray.py:53`. Decorators are copied as source expressions and have not been executed.

## `draftmake.make_pointarray.makePointArray`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@deprecated(deprecated_in='26.3', removed_in='28.3', replacement='Draft.make_point_array()')
def makePointArray(base, ptlst):
```

DEPRECATED. Use 'make_point_array'.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_pointarray.py:161`. Decorators are copied as source expressions and have not been executed.

