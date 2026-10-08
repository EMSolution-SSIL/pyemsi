# Python source module `draftmake.make_polararray`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftmake/make_polararray.py`. Import path is source-routed; installed availability is unverified.

Provides functions to create polar Array objects.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_polararray.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_polararray.py:33`.

### import WorkingPlane

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_polararray.WorkingPlane` -> `WorkingPlane`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_polararray.py:34`.

### import draftutils.utils as utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_polararray.utils` -> `draftutils.utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_polararray.py:35`.

### import draftmake.make_array as make_array

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_polararray.make_array` -> `draftmake.make_array`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_polararray.py:36`.

### from draftutils.messages import _err

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_polararray._err` -> `draftutils.messages._err`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_polararray.py:38`.

### from draftutils.translate import translate

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_polararray.translate` -> `draftutils.translate.translate`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_polararray.py:39`.

## `draftmake.make_polararray.make_polar_array`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def make_polar_array(base_object, number=5, angle=360, center=App.Vector(0, 0, 0), axis=None, use_link=True):
```

Create a polar array from the given object.

Parameters
----------
base_object: Part::Feature or str
    Any of object that has a `Part::TopoShape` that can be duplicated.
    This means most 2D and 3D objects produced with any workbench.
    If it is a string, it must be the `Label` of that object.
    Since a label is not guaranteed to be unique in a document,
    it will use the first object found with this label.

number: int, optional
    It defaults to 5.
    The number of copies produced in the polar pattern.

angle: float, optional
    It defaults to 360.
    The magnitude in degrees swept by the polar pattern.

center: Base::Vector3, optional
    It defaults to the origin `App.Vector(0, 0, 0)`.
    The vector indicating the center of rotation of the array.

axis: Base::Vector3, optional
    It defaults to the active Draft working plane axis if available,
    otherwise to `App.Vector(0, 0, 1)` or the `+Z` axis.
    The unit vector indicating the axis of rotation.

use_link: bool, optional
    It defaults to `True`.
    If it is `True` the produced copies are not `Part::TopoShape` copies,
    but rather `App::Link` objects.
    The Links repeat the shape of the original `obj` exactly,
    and therefore the resulting array is more memory efficient.

    Also, when `use_link` is `True`, the `Fuse` property
    of the resulting array does not work; the array doesn't
    contain separate shapes, it only has the original shape repeated
    many times, so there is nothing to fuse together.

    If `use_link` is `False` the original shape is copied many times.
    In this case the `Fuse` property is able to fuse
    all copies into a single object, if they touch each other.

Returns
-------
Part::FeaturePython
    A scripted object of type `'Array'`.
    Its `Shape` is a compound of the copies of the original object.

None
    If there is a problem it will return `None`.

See Also
--------
make_ortho_array, make_circular_array, make_path_array, make_point_array

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_polararray.py:42`. Decorators are copied as source expressions and have not been executed.

