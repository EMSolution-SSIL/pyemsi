# Python source module `draftfunctions.cut`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftfunctions/cut.py`. Import path is source-routed; installed availability is unverified.

Provides functions to create a cut object from two objects.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.cut.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/cut.py:33`.

### import draftutils.gui_utils as gui_utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.cut.gui_utils` -> `draftutils.gui_utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/cut.py:34`.

### from draftutils.translate import translate

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.cut.translate` -> `draftutils.translate.translate`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/cut.py:36`.

### from draftutils.messages import _err

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.cut._err` -> `draftutils.messages._err`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/cut.py:37`.

## `draftfunctions.cut.cut`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def cut(object1, object2):
```

Return a cut object made from the difference of the 2 given objects.

Parameters
----------
object1: Part::Feature
    Any object with a `Part::TopoShape`.

object2: Part::Feature
    Any object with a `Part::TopoShape`.

Returns
-------
Part::Cut
    The resulting cut object.

None
    If there is a problem and the new object can't be created.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/cut.py:40`. Decorators are copied as source expressions and have not been executed.

