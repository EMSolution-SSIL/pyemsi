# Python source module `draftmake.make_polygon`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftmake/make_polygon.py`. Import path is source-routed; installed availability is unverified.

Provides functions to create Polygon objects.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_polygon.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_polygon.py:33`.

### from draftobjects.polygon import Polygon

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_polygon.Polygon` -> `draftobjects.polygon.Polygon`.

[Source module `draftobjects.polygon`](../../draftobjects/polygon/index.md).

Evidence: `src/Mod/Draft/draftmake/make_polygon.py:34`.

### from draftutils import gui_utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_polygon.gui_utils` -> `draftutils.gui_utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_polygon.py:35`.

### from freecad.deprecation import deprecated

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_polygon.deprecated` -> `freecad.deprecation.deprecated`.

[Source module `freecad.deprecation`](../../freecad/deprecation/index.md).

Evidence: `src/Mod/Draft/draftmake/make_polygon.py:36`.

### from draftviewproviders.view_base import ViewProviderDraft

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if App.GuiUp`.

Bound source name `draftmake.make_polygon.ViewProviderDraft` -> `draftviewproviders.view_base.ViewProviderDraft`.

[Source module `draftviewproviders.view_base`](../../draftviewproviders/view_base/index.md).

Evidence: `src/Mod/Draft/draftmake/make_polygon.py:39`.

## `draftmake.make_polygon.make_polygon`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def make_polygon(nfaces, radius=1, inscribed=True, placement=None, face=None, support=None):
```

makePolgon(edges,[radius],[inscribed],[placement],[face])

Creates a polygon object with the given number of edges and radius.

Parameters
----------
edges : int
    Number of edges of the polygon.

radius :
    Radius of the control circle.

inscribed : bool
    Defines is the polygon is inscribed or not into the control circle.

placement : Base.Placement
    If placement is given, it is used.

face : bool
    If face is True, the resulting shape is displayed as a face,
    otherwise as a wireframe.

support :
    TODO: Describe

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_polygon.py:42`. Decorators are copied as source expressions and have not been executed.

## `draftmake.make_polygon.makePolygon`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@deprecated(deprecated_in='26.3', removed_in='28.3', replacement='Draft.make_polygon()')
def makePolygon(*args, **kwarg):
```

DEPRECATED. Use 'make_polygon'.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_polygon.py:99`. Decorators are copied as source expressions and have not been executed.

