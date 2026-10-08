# Python source module `draftfunctions.svgtext`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftfunctions/svgtext.py`. Import path is source-routed; installed availability is unverified.

Provides functions to return the SVG representation of text elements.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import math

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.svgtext.math` -> `math`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/svgtext.py:32`.

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.svgtext.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/svgtext.py:34`.

### import DraftVecUtils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.svgtext.DraftVecUtils` -> `DraftVecUtils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/svgtext.py:35`.

### import draftutils.utils as utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.svgtext.utils` -> `draftutils.utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/svgtext.py:36`.

## `draftfunctions.svgtext.get_text`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_text(plane, techdraw, tcolor, fontsize, fontname, angle, base, text, linespacing=0.5, align='center', flip=True):
```

Get the SVG representation of a textual element.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/svgtext.py:109`. Decorators are copied as source expressions and have not been executed.

## `draftfunctions.svgtext.getText`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getText(plane, techdraw, tcolor, fontsize, fontname, angle, base, text, linespacing=0.5, align='center', flip=True):
```

Get the SVG representation of a textual element. DEPRECATED.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/svgtext.py:190`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`draftfunctions.svgtext._get_text_techdraw`, `draftfunctions.svgtext._get_text_header`. These are source internals unless an explicit export establishes otherwise.

