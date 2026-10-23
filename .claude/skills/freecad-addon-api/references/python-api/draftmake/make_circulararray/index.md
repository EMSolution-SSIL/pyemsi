# Python source module `draftmake.make_circulararray`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftmake/make_circulararray.py`. Import path is source-routed; installed availability is unverified.

Provides functions to create circular Array objects.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_circulararray.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_circulararray.py:33`.

### import WorkingPlane

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_circulararray.WorkingPlane` -> `WorkingPlane`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_circulararray.py:34`.

### import draftmake.make_array as make_array

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_circulararray.make_array` -> `draftmake.make_array`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_circulararray.py:35`.

### import draftutils.utils as utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_circulararray.utils` -> `draftutils.utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_circulararray.py:36`.

### from draftutils.messages import _err

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_circulararray._err` -> `draftutils.messages._err`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_circulararray.py:38`.

### from draftutils.translate import translate

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_circulararray.translate` -> `draftutils.translate.translate`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_circulararray.py:39`.

## `draftmake.make_circulararray.make_circular_array`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def make_circular_array(base_object, r_distance=100, tan_distance=50, number=3, symmetry=1, axis=None, center=App.Vector(0, 0, 0), use_link=True):
```

Create a circular array from the given object.

Parameters
----------
base_object: Part::Feature or str
    Any of object that has a `Part::TopoShape` that can be duplicated.
    This means most 2D and 3D objects produced with any workbench.
    If it is a string, it must be the `Label` of that object.
    Since a label is not guaranteed to be unique in a document,
    it will use the first object found with this label.

r_distance: float, optional
    It defaults to `100`.
    Radial distance to the next ring of circular arrays.

tan_distance: float, optional
    It defaults to `50`.
    The tangential distance between two elements located
    in the same circular ring.
    The tangential distance together with the radial distance
    determine how many copies are created.

number: int, optional
    It defaults to 3.
    The number of layers or rings of repeated objects.
    The original object stays at the center, and is counted
    as a layer itself. So, if you want at least one layer of circular
    copies, this number must be at least 2.

symmetry: int, optional
    It defaults to 1.
    It indicates how many lines of symmetry the entire circular pattern
    has. That is, with 1, the array is symmetric only after a full
    360 degrees rotation.

    When it is 2, the array is symmetric at 0 and 180 degrees.
    When it is 3, the array is symmetric at 0, 120, and 240 degrees.
    When it is 4, the array is symmetric at 0, 90, 180, and 270 degrees.
    Et cetera.

axis: Base::Vector3, optional
    It defaults to the active Draft working plane axis if available,
    otherwise to `App.Vector(0, 0, 1)` or the `+Z` axis.
    The unit vector indicating the axis of rotation.

center: Base::Vector3, optional
    It defaults to `App.Vector(0, 0, 0)` or the global origin.
    The point through which the `axis` passes to define
    the axis of rotation.

use_link: bool, optional
    It defaults to `True`.
    If it is `True` the produced copies are not `Part::TopoShape` copies,
    but rather `App::Link` objects.
    The Links repeat the shape of the original `base_object` exactly,
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
make_ortho_array, make_polar_array, make_path_array, make_point_array

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_circulararray.py:42`. Decorators are copied as source expressions and have not been executed.

