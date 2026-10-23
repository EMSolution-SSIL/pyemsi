# Python source module `draftmake.make_ellipse`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftmake/make_ellipse.py`. Import path is source-routed; installed availability is unverified.

Provides functions to create Ellipse objects.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_ellipse.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_ellipse.py:33`.

### from draftobjects.ellipse import Ellipse

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_ellipse.Ellipse` -> `draftobjects.ellipse.Ellipse`.

[Source module `draftobjects.ellipse`](../../draftobjects/ellipse/index.md).

Evidence: `src/Mod/Draft/draftmake/make_ellipse.py:34`.

### from draftutils import gui_utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_ellipse.gui_utils` -> `draftutils.gui_utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_ellipse.py:35`.

### from freecad.deprecation import deprecated

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_ellipse.deprecated` -> `freecad.deprecation.deprecated`.

[Source module `freecad.deprecation`](../../freecad/deprecation/index.md).

Evidence: `src/Mod/Draft/draftmake/make_ellipse.py:36`.

### from draftviewproviders.view_base import ViewProviderDraft

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if App.GuiUp`.

Bound source name `draftmake.make_ellipse.ViewProviderDraft` -> `draftviewproviders.view_base.ViewProviderDraft`.

[Source module `draftviewproviders.view_base`](../../draftviewproviders/view_base/index.md).

Evidence: `src/Mod/Draft/draftmake/make_ellipse.py:39`.

## `draftmake.make_ellipse.make_ellipse`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def make_ellipse(majradius, minradius, placement=None, face=None, support=None):
```

make_ellipse(majradius, minradius, [placement], [face], [support])

Makes an ellipse with the given major and minor radius, and optionally
a placement.

Parameters
----------
majradius :
    Major radius of the ellipse.

minradius :
    Minor radius of the ellipse.

placement : Base.Placement
    If a placement is given, it is used.

face : Bool
    If face is False, the rectangle is shown as a wireframe,
    otherwise as a face.

support :
    TODO: Describe.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_ellipse.py:42`. Decorators are copied as source expressions and have not been executed.

## `draftmake.make_ellipse.makeEllipse`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@deprecated(deprecated_in='26.3', removed_in='28.3', replacement='Draft.make_ellipse()')
def makeEllipse(*args, **kwarg):
```

DEPRECATED. Use 'make_ellipse'.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_ellipse.py:99`. Decorators are copied as source expressions and have not been executed.

