# Python source module `draftmake.make_patharray`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftmake/make_patharray.py`. Import path is source-routed; installed availability is unverified.

Provides functions to create PathArray objects.

The copies will be placed along a path like a polyline, spline, or bezier
curve.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_patharray.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_patharray.py:42`.

### from draftobjects.patharray import PathArray

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_patharray.PathArray` -> `draftobjects.patharray.PathArray`.

[Source module `draftobjects.patharray`](../../draftobjects/patharray/index.md).

Evidence: `src/Mod/Draft/draftmake/make_patharray.py:43`.

### from draftobjects.pathtwistedarray import PathTwistedArray

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_patharray.PathTwistedArray` -> `draftobjects.pathtwistedarray.PathTwistedArray`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_patharray.py:44`.

### from draftutils import gui_utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_patharray.gui_utils` -> `draftutils.gui_utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_patharray.py:45`.

### from draftutils import utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_patharray.utils` -> `draftutils.utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_patharray.py:46`.

### from draftutils.messages import _err

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_patharray._err` -> `draftutils.messages._err`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_patharray.py:47`.

### from draftutils.translate import translate

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_patharray.translate` -> `draftutils.translate.translate`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_patharray.py:48`.

### from freecad.deprecation import deprecated

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_patharray.deprecated` -> `freecad.deprecation.deprecated`.

[Source module `freecad.deprecation`](../../freecad/deprecation/index.md).

Evidence: `src/Mod/Draft/draftmake/make_patharray.py:49`.

### from draftviewproviders.view_array import ViewProviderDraftArray

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if App.GuiUp`.

Bound source name `draftmake.make_patharray.ViewProviderDraftArray` -> `draftviewproviders.view_array.ViewProviderDraftArray`.

[Source module `draftviewproviders.view_array`](../../draftviewproviders/view_array/index.md).

Evidence: `src/Mod/Draft/draftmake/make_patharray.py:52`.

### from draftviewproviders.view_draftlink import ViewProviderDraftLink

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if App.GuiUp`.

Bound source name `draftmake.make_patharray.ViewProviderDraftLink` -> `draftviewproviders.view_draftlink.ViewProviderDraftLink`.

[Source module `draftviewproviders.view_draftlink`](../../draftviewproviders/view_draftlink/index.md).

Evidence: `src/Mod/Draft/draftmake/make_patharray.py:53`.

## `draftmake.make_patharray.make_path_array`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def make_path_array(base_object, path_object, count=4, extra=App.Vector(0, 0, 0), subelements=None, align=False, align_mode='Original', tan_vector=App.Vector(1, 0, 0), force_vertical=False, vertical_vector=App.Vector(0, 0, 1), start_offset=0.0, end_offset=0.0, use_link=True):
```

Make a Draft PathArray object.

Distribute copies of a `base_object` along `path_object`
or `subelements` from `path_object`.

Parameters
----------
base_object: Part::Feature or str
    Any of object that has a `Part::TopoShape` that can be duplicated.
    This means most 2D and 3D objects produced with any workbench.
    If it is a string, it must be the `Label` of that object.
    Since a label is not guaranteed to be unique in a document,
    it will use the first object found with this label.

path_object: Part::Feature or str
    Path object like a polyline, B-Spline, or bezier curve that should
    contain edges.
    Just like `base_object` it can also be `Label`.

count: int, float, optional
    It defaults to 4.
    Number of copies to create along the `path_object`.
    It must be at least 2.
    If a `float` is provided, it will be truncated by `int(count)`.

extra: Base.Vector3, optional
    It defaults to `App.Vector(0, 0, 0)`.
    It translates each copy by the value of `extra`.
    This is useful to adjust for the difference between shape centre
    and shape reference point.

subelements: list or tuple of str, optional
    It defaults to `None`.
    It should be a list of names of edges that must exist in `path_object`.
    Then the path array will be created along these edges only,
    and not the entire `path_object`.
    ::
        subelements = ['Edge1', 'Edge2']

    The edges must be contiguous, meaning that it is not allowed to
    input `'Edge1'` and `'Edge3'` if they do not touch each other.

    A single string value is also allowed.
    ::
        subelements = 'Edge1'

align: bool, optional
    It defaults to `False`.
    If it is `True` it will align `base_object` to tangent, normal,
    or binormal to the `path_object`, depending on the value
    of `tan_vector`.

align_mode: str, optional
    It defaults to `'Original'` which is the traditional alignment.
    It can also be `'Frenet'` or `'Tangent'`.

    - Original. It does not calculate curve normal.
      `X` is curve tangent, `Y` is normal parameter, Z is the cross
      product `X` x `Y`.
    - Frenet. It defines a local coordinate system along the path.
      `X` is tangent to curve, `Y` is curve normal, `Z` is curve binormal.
      If normal cannot be computed, for example, in a straight path,
      a default is used.
    - Tangent. It is similar to `'Original'` but includes a pre-rotation
      to align the base object's `X` to the value of `tan_vector`,
      then `X` follows curve tangent.

tan_vector: Base::Vector3, optional
    It defaults to `App.Vector(1, 0, 0)` or the +X axis.
    It aligns the tangent of the path to this local unit vector
    of the object.

force_vertical: Base::Vector3, optional
    It defaults to `False`.
    If it is `True`, the value of `vertical_vector`
    will be used when `align_mode` is `'Original'` or `'Tangent'`.

vertical_vector: Base::Vector3, optional
    It defaults to `App.Vector(0, 0, 1)` or the +Z axis.
    It will force this vector to be the vertical direction
    when `force_vertical` is `True`.

start_offset: float, optional
    It defaults to 0.0.
    It is the length from the start of the path to the first copy.

end_offset: float, optional
    It defaults to 0.0.
    It is the length from the end of the path to the last copy.

use_link: bool, optional
    It defaults to `True`, in which case the copies are `App::Link`
    elements. Otherwise, the copies are shape copies which makes
    the resulting array heavier.

Returns
-------
Part::FeaturePython
    The scripted object of type `'PathArray'`.
    Its `Shape` is a compound of the copies of the original object.

None
    If there is a problem it will return `None`.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_patharray.py:56`. Decorators are copied as source expressions and have not been executed.

## `draftmake.make_patharray.makePathArray`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@deprecated(deprecated_in='26.3', removed_in='28.3', replacement='Draft.make_path_array()')
def makePathArray(baseobject, pathobject, count, xlate=None, align=False, pathobjsubs=[], use_link=False):
```

DEPRECATED. Use 'make_path_array'.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_patharray.py:318`. Decorators are copied as source expressions and have not been executed.

## `draftmake.make_patharray.make_path_twisted_array`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def make_path_twisted_array(base_object, path_object, count=15, rot_factor=0.25, use_link=True):
```

Create a Path twisted array.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_patharray.py:333`. Decorators are copied as source expressions and have not been executed.

