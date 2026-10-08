# Python source module `draftfunctions.fuse`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftfunctions/fuse.py`. Import path is source-routed; installed availability is unverified.

Provides functions to create a fusion of two shapes.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.fuse.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/fuse.py:33`.

### from draftgeoutils import faces as geo_faces

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.fuse.geo_faces` -> `draftgeoutils.faces`.

[Source module `draftgeoutils`](../../draftgeoutils/index.md).

Evidence: `src/Mod/Draft/draftfunctions/fuse.py:34`.

### from draftmake.make_wire import Wire

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.fuse.Wire` -> `draftmake.make_wire.Wire`.

[Source module `draftmake.make_wire`](../../draftmake/make_wire/index.md).

Evidence: `src/Mod/Draft/draftfunctions/fuse.py:35`.

### from draftutils import gui_utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.fuse.gui_utils` -> `draftutils.gui_utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/fuse.py:36`.

### from draftviewproviders.view_wire import ViewProviderWire

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if App.GuiUp`.

Bound source name `draftfunctions.fuse.ViewProviderWire` -> `draftviewproviders.view_wire.ViewProviderWire`.

[Source module `draftviewproviders.view_wire`](../../draftviewproviders/view_wire/index.md).

Evidence: `src/Mod/Draft/draftfunctions/fuse.py:39`.

## `draftfunctions.fuse.fuse`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def fuse(object1, object2):
```

fuse(oject1, object2)

Returns an object made from the union of the 2 given objects.
If the objects are coplanar, a special Draft Wire is used, otherwise we use
a standard Part fuse.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/fuse.py:42`. Decorators are copied as source expressions and have not been executed.

