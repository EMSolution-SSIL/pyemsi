# Python source module `draftfunctions.heal`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftfunctions/heal.py`. Import path is source-routed; installed availability is unverified.

Provides functions to repair certain objects created with old versions.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.heal.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/heal.py:33`.

### import draftutils.utils as utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.heal.utils` -> `draftutils.utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/heal.py:34`.

### from draftmake.make_copy import make_copy

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.heal.make_copy` -> `draftmake.make_copy.make_copy`.

[Source module `draftmake.make_copy`](../../draftmake/make_copy/index.md).

Evidence: `src/Mod/Draft/draftfunctions/heal.py:36`.

## `draftfunctions.heal.heal`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def heal(objlist=None, delete=True, reparent=True):
```

heal([objlist],[delete],[reparent])

Recreate Draft objects that are damaged, for example if created from an
earlier version. If ran without arguments, all the objects in the document
will be healed if they are damaged.

Parameters
----------
objlist : list

delete : Base.Vector or list of Base.Vector
    If delete is True, the damaged objects are deleted (default).

reparent : bool
    If reparent is True (default), new objects go at the very same place
    in the tree than their original.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/heal.py:39`. Decorators are copied as source expressions and have not been executed.

