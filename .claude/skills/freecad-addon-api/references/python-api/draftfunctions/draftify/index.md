# Python source module `draftfunctions.draftify`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftfunctions/draftify.py`. Import path is source-routed; installed availability is unverified.

Provides functions to transform sketches into Draft objects.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import lazy_loader.lazy_loader as lz

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.draftify.lz` -> `lazy_loader.lazy_loader`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/draftify.py:34`.

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.draftify.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/draftify.py:36`.

### from draftgeoutils import general as geo_general

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.draftify.geo_general` -> `draftgeoutils.general`.

[Source module `draftgeoutils`](../../draftgeoutils/index.md).

Evidence: `src/Mod/Draft/draftfunctions/draftify.py:37`.

### from draftmake import make_block

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.draftify.make_block` -> `draftmake.make_block`.

[Source module `draftmake`](../../draftmake/index.md).

Evidence: `src/Mod/Draft/draftfunctions/draftify.py:38`.

### from draftmake import make_wire

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.draftify.make_wire` -> `draftmake.make_wire`.

[Source module `draftmake`](../../draftmake/index.md).

Evidence: `src/Mod/Draft/draftfunctions/draftify.py:39`.

### from draftmake import make_circle

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.draftify.make_circle` -> `draftmake.make_circle`.

[Source module `draftmake`](../../draftmake/index.md).

Evidence: `src/Mod/Draft/draftfunctions/draftify.py:40`.

### from draftmake import make_arc_3points

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.draftify.make_arc_3points` -> `draftmake.make_arc_3points`.

[Source module `draftmake`](../../draftmake/index.md).

Evidence: `src/Mod/Draft/draftfunctions/draftify.py:44`.

### from draftutils import gui_utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.draftify.gui_utils` -> `draftutils.gui_utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/draftify.py:45`.

## `draftfunctions.draftify.draftify`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def draftify(objectslist, makeblock=False, delete=True):
```

draftify(objectslist,[makeblock],[delete])

Turn each object of the given list (objectslist can also be a single
object) into a Draft parametric wire.

TODO: support more objects

Parameters
----------
objectslist :

makeblock : bool
    If makeblock is True, multiple objects will be grouped in a block.

delete : bool
    If delete = False, old objects are not deleted

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/draftify.py:51`. Decorators are copied as source expressions and have not been executed.

## `draftfunctions.draftify.draftify_shape`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def draftify_shape(shape):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/draftify.py:97`. Decorators are copied as source expressions and have not been executed.

