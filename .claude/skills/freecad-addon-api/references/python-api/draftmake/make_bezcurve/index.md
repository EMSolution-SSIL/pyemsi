# Python source module `draftmake.make_bezcurve`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftmake/make_bezcurve.py`. Import path is source-routed; installed availability is unverified.

Provides functions to create BezCurve objects.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_bezcurve.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_bezcurve.py:33`.

### from draftobjects.bezcurve import BezCurve

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_bezcurve.BezCurve` -> `draftobjects.bezcurve.BezCurve`.

[Source module `draftobjects.bezcurve`](../../draftobjects/bezcurve/index.md).

Evidence: `src/Mod/Draft/draftmake/make_bezcurve.py:34`.

### from draftutils import gui_utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_bezcurve.gui_utils` -> `draftutils.gui_utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_bezcurve.py:35`.

### from draftutils import utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_bezcurve.utils` -> `draftutils.utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_bezcurve.py:36`.

### from freecad.deprecation import deprecated

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_bezcurve.deprecated` -> `freecad.deprecation.deprecated`.

[Source module `freecad.deprecation`](../../freecad/deprecation/index.md).

Evidence: `src/Mod/Draft/draftmake/make_bezcurve.py:37`.

### from draftviewproviders.view_bezcurve import ViewProviderBezCurve

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if App.GuiUp`.

Bound source name `draftmake.make_bezcurve.ViewProviderBezCurve` -> `draftviewproviders.view_bezcurve.ViewProviderBezCurve`.

[Source module `draftviewproviders.view_bezcurve`](../../draftviewproviders/view_bezcurve/index.md).

Evidence: `src/Mod/Draft/draftmake/make_bezcurve.py:40`.

## `draftmake.make_bezcurve.make_bez_curve`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def make_bez_curve(pointslist, closed=False, placement=None, face=None, support=None, degree=None):
```

make_bez_curve(pointslist, [closed], [placement])

Creates a Bezier Curve object from the given list of vectors.

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

degree : int
    Degree of the BezCurve

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_bezcurve.py:43`. Decorators are copied as source expressions and have not been executed.

## `draftmake.make_bezcurve.make_bezcurve`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@deprecated(deprecated_in='26.3', removed_in='28.3', replacement='Draft.make_bez_curve()')
def make_bezcurve(*args, **kwarg):
```

DEPRECATED. Use 'make_bez_curve'.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_bezcurve.py:118`. Decorators are copied as source expressions and have not been executed.

## `draftmake.make_bezcurve.makeBezCurve`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@deprecated(deprecated_in='26.3', removed_in='28.3', replacement='Draft.make_bez_curve()')
def makeBezCurve(*args, **kwarg):
```

DEPRECATED. Use 'make_bez_curve'.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_bezcurve.py:128`. Decorators are copied as source expressions and have not been executed.

