# Python source module `draftfunctions.extrude`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftfunctions/extrude.py`. Import path is source-routed; installed availability is unverified.

Provides functions to create an extrusion object from a profile.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.extrude.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/extrude.py:33`.

### import draftutils.gui_utils as gui_utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.extrude.gui_utils` -> `draftutils.gui_utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/extrude.py:34`.

## `draftfunctions.extrude.extrude`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def extrude(obj, vector, solid=False):
```

extrude(object, vector, [solid])

Create a Part::Extrusion object from a given object.

Parameters
----------
obj :

vector : Base.Vector
    The extrusion direction and module.

solid : bool
    TODO: describe.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/extrude.py:37`. Decorators are copied as source expressions and have not been executed.

