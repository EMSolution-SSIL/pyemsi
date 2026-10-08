# Python source module `draftfunctions.mirror`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftfunctions/mirror.py`. Import path is source-routed; installed availability is unverified.

Provides functions to produce a mirrored object.

It just creates a `Part::Mirroring` object, and sets the appropriate
`Source` and `Normal` properties.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.mirror.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/mirror.py:38`.

### import WorkingPlane

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.mirror.WorkingPlane` -> `WorkingPlane`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/mirror.py:39`.

### from draftutils import gui_utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.mirror.gui_utils` -> `draftutils.gui_utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/mirror.py:41`.

### from draftutils import utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.mirror.utils` -> `draftutils.utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/mirror.py:42`.

### from draftutils.messages import _err

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.mirror._err` -> `draftutils.messages._err`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/mirror.py:43`.

### from draftutils.translate import translate

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.mirror.translate` -> `draftutils.translate.translate`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/mirror.py:44`.

### import FreeCADGui as Gui

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if App.GuiUp`.

Bound source name `draftfunctions.mirror.Gui` -> `FreeCADGui`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/mirror.py:47`.

## `draftfunctions.mirror.mirror`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def mirror(objlist, p1, p2):
```

Create a mirror object from the provided list and line.

It creates a `Part::Mirroring` object from the given `objlist` using
a plane that is defined by the two given points `p1` and `p2`,
and the Draft working plane normal.

Parameters
----------
objlist: single object or a list of objects
    A single object or a list of objects.

p1: Base::Vector3
    Point 1 of the mirror plane. It is also used as the `Placement.Base`
    of the resulting object.

p2: Base::Vector3
    Point 2 of the mirror plane.

Returns
-------
None
    If the operation fails.

list
    List of `Part::Mirroring` objects, or a single one
    depending on the input `objlist`.

To Do
-----
Implement a mirror tool specific to the workbench that does not
just use `Part::Mirroring`. It should create a derived object,
that is, it should work similar to `Draft.offset`.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/mirror.py:50`. Decorators are copied as source expressions and have not been executed.

