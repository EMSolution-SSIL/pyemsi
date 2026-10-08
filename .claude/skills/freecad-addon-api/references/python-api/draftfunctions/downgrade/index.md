# Python source module `draftfunctions.downgrade`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftfunctions/downgrade.py`. Import path is source-routed; installed availability is unverified.

Provides functions to downgrade objects by different methods.

See also the `upgrade` function.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.downgrade.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/downgrade.py:37`.

### from draftmake import make_copy

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.downgrade.make_copy` -> `draftmake.make_copy`.

[Source module `draftmake`](../../draftmake/index.md).

Evidence: `src/Mod/Draft/draftfunctions/downgrade.py:38`.

### from draftutils import utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.downgrade.utils` -> `draftutils.utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/downgrade.py:39`.

### from draftutils import params

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.downgrade.params` -> `draftutils.params`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/downgrade.py:40`.

### from draftutils import gui_utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.downgrade.gui_utils` -> `draftutils.gui_utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/downgrade.py:41`.

### from draftutils.groups import is_group

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.downgrade.is_group` -> `draftutils.groups.is_group`.

[Source module `draftutils.groups`](../../draftutils/groups/index.md).

Evidence: `src/Mod/Draft/draftfunctions/downgrade.py:42`.

### from draftutils.messages import _msg

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.downgrade._msg` -> `draftutils.messages._msg`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/downgrade.py:43`.

### from draftutils.translate import translate

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.downgrade.translate` -> `draftutils.translate.translate`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/downgrade.py:44`.

## `draftfunctions.downgrade.downgrade`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def downgrade(objects, delete=False, force=None):
```

Downgrade the given objects.

This is a counterpart to `upgrade`.

Parameters
----------
objects: Part::Feature or list
    A single object to downgrade or a list
    containing various such objects.

delete: bool, optional
    It defaults to `False`.
    If it is `True`, the old objects are deleted, and only the resulting
    object is kept.

force: str, optional
    It defaults to `None`.
    Its value can be used to force a certain method of downgrading.
    It can be any of: `'explode'`, `'shapify'`, `'subtr'`, `'splitFaces'`,
    `'cut2'`, `'getWire'`, `'splitWires'`, or `'splitCompounds'`.

Returns
-------
tuple
    A tuple containing two lists, a list of new objects
    and a list of objects to be deleted.

See Also
--------
upgrade

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/downgrade.py:47`. Decorators are copied as source expressions and have not been executed.

