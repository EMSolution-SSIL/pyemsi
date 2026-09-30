# Python source module `draftmake.make_array`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftmake/make_array.py`. Import path is source-routed; installed availability is unverified.

Provides functions to create Array objects.

This includes orthogonal arrays, polar arrays, and circular arrays.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_array.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_array.py:36`.

### from draftobjects.array import Array

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_array.Array` -> `draftobjects.array.Array`.

[Source module `draftobjects.array`](../../draftobjects/array/index.md).

Evidence: `src/Mod/Draft/draftmake/make_array.py:37`.

### from draftutils import gui_utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_array.gui_utils` -> `draftutils.gui_utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_array.py:38`.

### from draftutils import utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_array.utils` -> `draftutils.utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_array.py:39`.

### from draftutils.messages import _err

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_array._err` -> `draftutils.messages._err`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_array.py:40`.

### from draftutils.translate import translate

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_array.translate` -> `draftutils.translate.translate`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_array.py:41`.

### from freecad.deprecation import deprecated

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_array.deprecated` -> `freecad.deprecation.deprecated`.

[Source module `freecad.deprecation`](../../freecad/deprecation/index.md).

Evidence: `src/Mod/Draft/draftmake/make_array.py:42`.

### from draftviewproviders.view_array import ViewProviderDraftArray

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if App.GuiUp`.

Bound source name `draftmake.make_array.ViewProviderDraftArray` -> `draftviewproviders.view_array.ViewProviderDraftArray`.

[Source module `draftviewproviders.view_array`](../../draftviewproviders/view_array/index.md).

Evidence: `src/Mod/Draft/draftmake/make_array.py:45`.

### from draftviewproviders.view_draftlink import ViewProviderDraftLink

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if App.GuiUp`.

Bound source name `draftmake.make_array.ViewProviderDraftLink` -> `draftviewproviders.view_draftlink.ViewProviderDraftLink`.

[Source module `draftviewproviders.view_draftlink`](../../draftviewproviders/view_draftlink/index.md).

Evidence: `src/Mod/Draft/draftmake/make_array.py:46`.

## `draftmake.make_array.make_array`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def make_array(base_object, arg1, arg2, arg3, arg4=None, arg5=None, arg6=None, use_link=True):
```

Create a Draft Array of the given object.

Rectangular array
-----------------
make_array(object, xvector, yvector, xnum, ynum)
make_array(object, xvector, yvector, zvector, xnum, ynum, znum)

xnum of iterations in the x direction
at xvector distance between iterations, same for y direction
with yvector and ynum, same for z direction with zvector and znum.

Polar array
-----------
make_array(object, center, totalangle, totalnum) for polar array, or

center is a vector, totalangle is the angle to cover (in degrees)
and totalnum is the number of objects, including the original.

Circular array
--------------
make_array(object, rdistance, tdistance, axis, center, ncircles, symmetry)

In case of a circular array, rdistance is the distance of the
circles, tdistance is the distance within circles, axis the rotation-axis,
center the center of rotation, ncircles the number of circles
and symmetry the number of symmetry-axis of the distribution.

To Do
-----
The `Array` class currently handles three types of arrays,
orthogonal, polar, and circular. In the future, probably they should be
split in separate classes so that they are easier to manage.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_array.py:49`. Decorators are copied as source expressions and have not been executed.

## `draftmake.make_array.makeArray`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@deprecated(deprecated_in='26.3', removed_in='28.3', replacement='Draft.make_array()')
def makeArray(baseobject, arg1, arg2, arg3, arg4=None, arg5=None, arg6=None, name='Array', use_link=False):
```

DEPRECATED. Use 'make_array'.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_array.py:148`. Decorators are copied as source expressions and have not been executed.

