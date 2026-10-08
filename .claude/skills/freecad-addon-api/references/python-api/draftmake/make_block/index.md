# Python source module `draftmake.make_block`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftmake/make_block.py`. Import path is source-routed; installed availability is unverified.

Provides functions to create Block objects.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_block.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_block.py:33`.

### from draftobjects.block import Block

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_block.Block` -> `draftobjects.block.Block`.

[Source module `draftobjects.block`](../../draftobjects/block/index.md).

Evidence: `src/Mod/Draft/draftmake/make_block.py:34`.

### from draftutils import gui_utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_block.gui_utils` -> `draftutils.gui_utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_block.py:35`.

### from freecad.deprecation import deprecated

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_block.deprecated` -> `freecad.deprecation.deprecated`.

[Source module `freecad.deprecation`](../../freecad/deprecation/index.md).

Evidence: `src/Mod/Draft/draftmake/make_block.py:36`.

### from draftviewproviders.view_base import ViewProviderDraftPart

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if App.GuiUp`.

Bound source name `draftmake.make_block.ViewProviderDraftPart` -> `draftviewproviders.view_base.ViewProviderDraftPart`.

[Source module `draftviewproviders.view_base`](../../draftviewproviders/view_base/index.md).

Evidence: `src/Mod/Draft/draftmake/make_block.py:39`.

## `draftmake.make_block.make_block`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def make_block(objectslist):
```

make_block(objectslist)

Creates a Draft Block from the given objects.

Parameters
----------
objectslist : list
    Major radius of the ellipse.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_block.py:42`. Decorators are copied as source expressions and have not been executed.

## `draftmake.make_block.makeBlock`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@deprecated(deprecated_in='26.3', removed_in='28.3', replacement='Draft.make_block()')
def makeBlock(*args, **kwarg):
```

DEPRECATED. Use 'make_block'.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_block.py:73`. Decorators are copied as source expressions and have not been executed.

