# Python source module `draftmake.make_facebinder`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftmake/make_facebinder.py`. Import path is source-routed; installed availability is unverified.

Provides functions to create Facebinder objects.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_facebinder.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_facebinder.py:33`.

### from draftobjects.facebinder import Facebinder

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_facebinder.Facebinder` -> `draftobjects.facebinder.Facebinder`.

[Source module `draftobjects.facebinder`](../../draftobjects/facebinder/index.md).

Evidence: `src/Mod/Draft/draftmake/make_facebinder.py:34`.

### from draftutils import gui_utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_facebinder.gui_utils` -> `draftutils.gui_utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_facebinder.py:35`.

### from freecad.deprecation import deprecated

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_facebinder.deprecated` -> `freecad.deprecation.deprecated`.

[Source module `freecad.deprecation`](../../freecad/deprecation/index.md).

Evidence: `src/Mod/Draft/draftmake/make_facebinder.py:36`.

### from draftviewproviders.view_facebinder import ViewProviderFacebinder

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if App.GuiUp`.

Bound source name `draftmake.make_facebinder.ViewProviderFacebinder` -> `draftviewproviders.view_facebinder.ViewProviderFacebinder`.

[Source module `draftviewproviders.view_facebinder`](../../draftviewproviders/view_facebinder/index.md).

Evidence: `src/Mod/Draft/draftmake/make_facebinder.py:39`.

## `draftmake.make_facebinder.make_facebinder`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def make_facebinder(selectionset, name='Facebinder'):
```

make_facebinder(selectionset, [name])

Creates a Facebinder object from a selection set.

Parameters
----------
selectionset :
    Only faces will be added.

name : string (default = "Facebinder")
    Name of the created object

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_facebinder.py:42`. Decorators are copied as source expressions and have not been executed.

## `draftmake.make_facebinder.makeFacebinder`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@deprecated(deprecated_in='26.3', removed_in='28.3', replacement='Draft.make_facebinder()')
def makeFacebinder(*args, **kwarg):
```

DEPRECATED. Use 'make_facebinder'.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_facebinder.py:75`. Decorators are copied as source expressions and have not been executed.

