# Python source module `draftmake.make_fillet`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftmake/make_fillet.py`. Import path is source-routed; installed availability is unverified.

Provides functions to create Fillet objects between two lines.

This creates a `Part::Part2DObjectPython`, and then assigns the Proxy class
`Fillet`, and the `ViewProviderFillet` for the view provider.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import lazy_loader.lazy_loader as lz

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_fillet.lz` -> `lazy_loader.lazy_loader`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_fillet.py:34`.

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_fillet.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_fillet.py:36`.

### from draftgeoutils import fillets as geo_fillets

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_fillet.geo_fillets` -> `draftgeoutils.fillets`.

[Source module `draftgeoutils`](../../draftgeoutils/index.md).

Evidence: `src/Mod/Draft/draftmake/make_fillet.py:37`.

### from draftobjects import fillet

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_fillet.fillet` -> `draftobjects.fillet`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_fillet.py:38`.

### from draftutils import gui_utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_fillet.gui_utils` -> `draftutils.gui_utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_fillet.py:39`.

### from draftutils.messages import _err

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_fillet._err` -> `draftutils.messages._err`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_fillet.py:40`.

### from draftutils.translate import translate

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_fillet.translate` -> `draftutils.translate.translate`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_fillet.py:41`.

### import draftviewproviders.view_fillet as view_fillet

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if App.GuiUp`.

Bound source name `draftmake.make_fillet.view_fillet` -> `draftviewproviders.view_fillet`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_fillet.py:44`.

## `draftmake.make_fillet.make_fillet`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def make_fillet(objs, radius=100, chamfer=False, delete=False):
```

Create a fillet between two edges.

Parameters
----------
objs: list
    A list of two objects or shapes of type wire (1st edge is used) or edge,
    or a 2 edge selection set:`FreeCADGui.Selection.getSelectionEx("", 0)`.

radius: float, optional
    It defaults to 100. The curvature of the fillet.

chamfer: bool, optional
    It defaults to `False`. If it is `True` it no longer produces
    a rounded fillet but a chamfer (straight edge)
    with the value of the `radius`.

delete: bool, optional
    It defaults to `False`. If `True` the source objects are deleted.
    Ignored for shapes.

Returns
-------
Part::Part2DObjectPython
    The object of Proxy type `'Fillet'`.
    It returns `None` if it fails producing the object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_fillet.py:87`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`draftmake.make_fillet._preprocess`. These are source internals unless an explicit export establishes otherwise.

