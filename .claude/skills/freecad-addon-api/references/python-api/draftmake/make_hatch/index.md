# Python source module `draftmake.make_hatch`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftmake/make_hatch.py`. Import path is source-routed; installed availability is unverified.

This module contains FreeCAD commands for the Draft workbench

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import FreeCAD

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_hatch.FreeCAD` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_hatch.py:27`.

### from draftobjects.hatch import Hatch

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_hatch.Hatch` -> `draftobjects.hatch.Hatch`.

[Source module `draftobjects.hatch`](../../draftobjects/hatch/index.md).

Evidence: `src/Mod/Draft/draftmake/make_hatch.py:28`.

### from draftviewproviders.view_hatch import ViewProviderDraftHatch

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if FreeCAD.GuiUp`.

Bound source name `draftmake.make_hatch.ViewProviderDraftHatch` -> `draftviewproviders.view_hatch.ViewProviderDraftHatch`.

[Source module `draftviewproviders.view_hatch`](../../draftviewproviders/view_hatch/index.md).

Evidence: `src/Mod/Draft/draftmake/make_hatch.py:31`.

### import draftutils.gui_utils as gui_utils

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if FreeCAD.GuiUp`.

Bound source name `draftmake.make_hatch.gui_utils` -> `draftutils.gui_utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_hatch.py:32`.

## `draftmake.make_hatch.make_hatch`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def make_hatch(selection, filename, pattern, scale, rotation, translate=True):
```

make_hatch(selection, filename, pattern, scale, rotation, translate)

Creates a hatch object by applying a pattern from a PAT file to faces.

Parameters
----------
selection: single object / list of objects / selection set / LinkSubList-like iterable
    Examples:
    App.ActiveDocument.Box
    Gui.Selection.getSelection()
    Gui.Selection.getSelectionEx("", 0)
    [(App.ActiveDocument.Box, ("Face1",))]
    [[App.ActiveDocument.Box, ["Face1", "Face2"]]]

filename: string
    Filename of the PAT file with relative or absolute path.
    To use a relative path the FreeCAD document must have been saved.

pattern: string
    Case-sensitive name of the hatch pattern. Must exist in the PAT file.

scale: float
    The pattern scale.

rotation: float
    The pattern rotation in degrees.

translate: Bool
    Specifies if the faces are temporarily translated to the global
    XY-plane during the hatching process. Setting it to `False` may
    give wrong results for non-XY faces.
    See https://wiki.freecad.org/Draft_Hatch.

Returns
-------
Part::FeaturePython object
    A scripted object of the Proxy type `"Hatch"`.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_hatch.py:35`. Decorators are copied as source expressions and have not been executed.

