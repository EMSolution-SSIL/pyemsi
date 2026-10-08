# Python source module `draftfunctions.upgrade`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftfunctions/upgrade.py`. Import path is source-routed; installed availability is unverified.

Provides functions to upgrade objects by different methods.

See also the `downgrade` function.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import math

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.upgrade.math` -> `math`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/upgrade.py:35`.

### import re

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.upgrade.re` -> `re`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/upgrade.py:36`.

### import lazy_loader.lazy_loader as lz

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.upgrade.lz` -> `lazy_loader.lazy_loader`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/upgrade.py:37`.

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.upgrade.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/upgrade.py:39`.

### from draftfunctions import draftify

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.upgrade.draftify` -> `draftfunctions.draftify`.

[Source module `draftfunctions`](../index.md).

Evidence: `src/Mod/Draft/draftfunctions/upgrade.py:40`.

### from draftgeoutils import faces as geo_faces

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.upgrade.geo_faces` -> `draftgeoutils.faces`.

[Source module `draftgeoutils`](../../draftgeoutils/index.md).

Evidence: `src/Mod/Draft/draftfunctions/upgrade.py:41`.

### from draftgeoutils import general as geo_general

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.upgrade.geo_general` -> `draftgeoutils.general`.

[Source module `draftgeoutils`](../../draftgeoutils/index.md).

Evidence: `src/Mod/Draft/draftfunctions/upgrade.py:42`.

### from draftgeoutils import geometry as geo_geometry

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.upgrade.geo_geometry` -> `draftgeoutils.geometry`.

[Source module `draftgeoutils`](../../draftgeoutils/index.md).

Evidence: `src/Mod/Draft/draftfunctions/upgrade.py:43`.

### from draftmake import make_block

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.upgrade.make_block` -> `draftmake.make_block`.

[Source module `draftmake`](../../draftmake/index.md).

Evidence: `src/Mod/Draft/draftfunctions/upgrade.py:44`.

### from draftmake import make_wire

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.upgrade.make_wire` -> `draftmake.make_wire`.

[Source module `draftmake`](../../draftmake/index.md).

Evidence: `src/Mod/Draft/draftfunctions/upgrade.py:45`.

### from draftutils import gui_utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.upgrade.gui_utils` -> `draftutils.gui_utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/upgrade.py:46`.

### from draftutils import params

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.upgrade.params` -> `draftutils.params`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/upgrade.py:47`.

### from draftutils import utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.upgrade.utils` -> `draftutils.utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/upgrade.py:48`.

### from draftutils.groups import is_group

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.upgrade.is_group` -> `draftutils.groups.is_group`.

[Source module `draftutils.groups`](../../draftutils/groups/index.md).

Evidence: `src/Mod/Draft/draftfunctions/upgrade.py:49`.

### from draftutils.messages import _msg

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.upgrade._msg` -> `draftutils.messages._msg`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/upgrade.py:50`.

### from draftutils.translate import translate

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.upgrade.translate` -> `draftutils.translate.translate`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/upgrade.py:51`.

## `draftfunctions.upgrade.upgrade`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def upgrade(objects, delete=False, force=None):
```

Upgrade the given objects.

This is a counterpart to `downgrade`.

Parameters
----------
objects: Part::Feature or list
    A single object to upgrade or a list
    containing various such objects.

delete: bool, optional
    It defaults to `False`.
    If it is `True`, the old objects are deleted, and only the resulting
    object is kept.

force: str, optional
    It defaults to `None`.
    Its value can be used to force a certain method of upgrading.
    It can be any of: `'makeCompound'`, `'closeGroupWires'`,
    `'makeSolid'`, `'closeWire'`, `'turnToParts'`, `'makeFusion'`,
    `'makeShell'`, `'makeFaces'`, `'draftify'`, `'joinFaces'`,
    `'makeSketchFace'`, `'makeWires'`.

Returns
-------
tuple
    A tuple containing two lists, a list of new objects
    and a list of objects to be deleted.

See Also
--------
downgrade

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/upgrade.py:63`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`draftfunctions.upgrade._DEBUG`. These are source internals unless an explicit export establishes otherwise.

