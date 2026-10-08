# Python source module `draftmake.make_wire`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftmake/make_wire.py`. Import path is source-routed; installed availability is unverified.

Provides functions to create multipoint Wire objects.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_wire.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_wire.py:32`.

### from draftgeoutils import geometry as geo_geometry

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_wire.geo_geometry` -> `draftgeoutils.geometry`.

[Source module `draftgeoutils`](../../draftgeoutils/index.md).

Evidence: `src/Mod/Draft/draftmake/make_wire.py:33`.

### from draftobjects.wire import Wire

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_wire.Wire` -> `draftobjects.wire.Wire`.

[Source module `draftobjects.wire`](../../draftobjects/wire/index.md).

Evidence: `src/Mod/Draft/draftmake/make_wire.py:34`.

### from draftutils import gui_utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_wire.gui_utils` -> `draftutils.gui_utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_wire.py:35`.

### from draftutils import utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_wire.utils` -> `draftutils.utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_wire.py:36`.

### from freecad.deprecation import deprecated

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_wire.deprecated` -> `freecad.deprecation.deprecated`.

[Source module `freecad.deprecation`](../../freecad/deprecation/index.md).

Evidence: `src/Mod/Draft/draftmake/make_wire.py:37`.

### from draftviewproviders.view_wire import ViewProviderWire

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if App.GuiUp`.

Bound source name `draftmake.make_wire.ViewProviderWire` -> `draftviewproviders.view_wire.ViewProviderWire`.

[Source module `draftviewproviders.view_wire`](../../draftviewproviders/view_wire/index.md).

Evidence: `src/Mod/Draft/draftmake/make_wire.py:40`.

## `draftmake.make_wire.make_wire`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def make_wire(pointslist, closed=False, placement=None, face=None, support=None, bs2wire=False):
```

make_wire(pointslist, [closed], [placement])

Creates a Wire object from the given list of vectors.  If face is
true (and wire is closed), the wire will appear filled. Instead of
a pointslist, you can also pass a Part Wire.

Parameters
----------
pointslist : [Base.Vector]
    List of points to create the polyline

closed : bool
    If closed is True or first and last points are identical,
    the created polyline will be closed.

placement : Base.Placement
    If a placement is given, it is used.

face : Bool
    If face is False, the rectangle is shown as a wireframe,
    otherwise as a face.

support :
    TODO: Describe

bs2wire : bool
    TODO: Describe

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_wire.py:43`. Decorators are copied as source expressions and have not been executed.

## `draftmake.make_wire.makeWire`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@deprecated(deprecated_in='26.3', removed_in='28.3', replacement='Draft.make_wire()')
def makeWire(*args, **kwarg):
```

DEPRECATED. Use 'make_wire'.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_wire.py:138`. Decorators are copied as source expressions and have not been executed.

