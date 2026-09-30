# Python source module `draftmake.make_point`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftmake/make_point.py`. Import path is source-routed; installed availability is unverified.

Provides functions to create Point objects.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_point.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_point.py:33`.

### from draftobjects.point import Point

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_point.Point` -> `draftobjects.point.Point`.

[Source module `draftobjects.point`](../../draftobjects/point/index.md).

Evidence: `src/Mod/Draft/draftmake/make_point.py:34`.

### from draftutils import gui_utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_point.gui_utils` -> `draftutils.gui_utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_point.py:35`.

### from freecad.deprecation import deprecated

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_point.deprecated` -> `freecad.deprecation.deprecated`.

[Source module `freecad.deprecation`](../../freecad/deprecation/index.md).

Evidence: `src/Mod/Draft/draftmake/make_point.py:36`.

### import FreeCADGui as Gui

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if App.GuiUp`.

Bound source name `draftmake.make_point.Gui` -> `FreeCADGui`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_point.py:39`.

### from draftviewproviders.view_point import ViewProviderPoint

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if App.GuiUp`.

Bound source name `draftmake.make_point.ViewProviderPoint` -> `draftviewproviders.view_point.ViewProviderPoint`.

[Source module `draftviewproviders.view_point`](../../draftviewproviders/view_point/index.md).

Evidence: `src/Mod/Draft/draftmake/make_point.py:40`.

## `draftmake.make_point.make_point`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def make_point(X=0, Y=0, Z=0, color=None, name='Point', point_size=5):
```

make_point(x, y, z, [color(r, g, b), point_size]) or
    make_point(Vector, color(r, g, b), point_size])

Creates a Draft Point in the current document.

Parameters
----------
X :
    float -> X coordinate of the point
    Base.Vector -> Ignore Y and Z coordinates and create the point
        from the vector.

Y : float
    Y coordinate of the point

Z : float
    Z coordinate of the point

color : (R, G, B)
    Point color as RGB
    example to create a colored point:
    make_point(0, 0, 0, (1, 0, 0)) # color = red
    example to change the color, make sure values are floats:
    p1.ViewObject.PointColor = (0.0, 0.0, 1.0)

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_point.py:43`. Decorators are copied as source expressions and have not been executed.

## `draftmake.make_point.makePoint`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@deprecated(deprecated_in='26.3', removed_in='28.3', replacement='Draft.make_point()')
def makePoint(*args, **kwarg):
```

DEPRECATED. Use 'make_point'.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_point.py:99`. Decorators are copied as source expressions and have not been executed.

