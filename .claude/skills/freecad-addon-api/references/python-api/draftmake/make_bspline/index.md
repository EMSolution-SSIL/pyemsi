# Python source module `draftmake.make_bspline`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftmake/make_bspline.py`. Import path is source-routed; installed availability is unverified.

Provides functions to create BSpline objects.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_bspline.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_bspline.py:33`.

### from draftobjects.bspline import BSpline

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_bspline.BSpline` -> `draftobjects.bspline.BSpline`.

[Source module `draftobjects.bspline`](../../draftobjects/bspline/index.md).

Evidence: `src/Mod/Draft/draftmake/make_bspline.py:34`.

### from draftutils import gui_utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_bspline.gui_utils` -> `draftutils.gui_utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_bspline.py:35`.

### from draftutils import utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_bspline.utils` -> `draftutils.utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_bspline.py:36`.

### from draftutils.translate import translate

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_bspline.translate` -> `draftutils.translate.translate`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_bspline.py:37`.

### from freecad.deprecation import deprecated

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_bspline.deprecated` -> `freecad.deprecation.deprecated`.

[Source module `freecad.deprecation`](../../freecad/deprecation/index.md).

Evidence: `src/Mod/Draft/draftmake/make_bspline.py:38`.

### from draftviewproviders.view_bspline import ViewProviderBSpline

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if App.GuiUp`.

Bound source name `draftmake.make_bspline.ViewProviderBSpline` -> `draftviewproviders.view_bspline.ViewProviderBSpline`.

[Source module `draftviewproviders.view_bspline`](../../draftviewproviders/view_bspline/index.md).

Evidence: `src/Mod/Draft/draftmake/make_bspline.py:41`.

## `draftmake.make_bspline.make_bspline`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def make_bspline(pointslist, closed=False, placement=None, face=None, support=None):
```

make_bspline(pointslist, [closed], [placement])

Creates a B-Spline object from the given list of vectors.

Parameters
----------
pointslist : [Base.Vector]
    List of points to create the polyline.
    Instead of a pointslist, you can also pass a Part Wire.
    TODO: Change the name so!

closed : bool
    If closed is True or first and last points are identical,
    the created BSpline will be closed.

placement : Base.Placement
    If a placement is given, it is used.

face : Bool
    If face is False, the rectangle is shown as a wireframe,
    otherwise as a face.

support :
    TODO: Describe

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_bspline.py:44`. Decorators are copied as source expressions and have not been executed.

## `draftmake.make_bspline.makeBSpline`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@deprecated(deprecated_in='26.3', removed_in='28.3', replacement='Draft.make_bspline()')
def makeBSpline(*args, **kwarg):
```

DEPRECATED. Use 'make_bspline'.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_bspline.py:123`. Decorators are copied as source expressions and have not been executed.

