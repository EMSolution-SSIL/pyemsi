# Python source module `draftmake.make_shape2dview`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftmake/make_shape2dview.py`. Import path is source-routed; installed availability is unverified.

Provides functions to create Shape2DView objects.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_shape2dview.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_shape2dview.py:33`.

### from draftobjects.shape2dview import Shape2DView

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_shape2dview.Shape2DView` -> `draftobjects.shape2dview.Shape2DView`.

[Source module `draftobjects.shape2dview`](../../draftobjects/shape2dview/index.md).

Evidence: `src/Mod/Draft/draftmake/make_shape2dview.py:34`.

### from draftutils import gui_utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_shape2dview.gui_utils` -> `draftutils.gui_utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_shape2dview.py:35`.

### from freecad.deprecation import deprecated

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_shape2dview.deprecated` -> `freecad.deprecation.deprecated`.

[Source module `freecad.deprecation`](../../freecad/deprecation/index.md).

Evidence: `src/Mod/Draft/draftmake/make_shape2dview.py:36`.

### from draftviewproviders.view_base import ViewProviderDraftAlt

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if App.GuiUp`.

Bound source name `draftmake.make_shape2dview.ViewProviderDraftAlt` -> `draftviewproviders.view_base.ViewProviderDraftAlt`.

[Source module `draftviewproviders.view_base`](../../draftviewproviders/view_base/index.md).

Evidence: `src/Mod/Draft/draftmake/make_shape2dview.py:39`.

## `draftmake.make_shape2dview.make_shape_2d_view`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def make_shape_2d_view(baseobj, projection=None, facenumbers=[]):
```

make_shape_2d_view(baseobj, [projection], [facenumbers])

Add a 2D shape to the document, which is a 2D projection of the given object.

Parameters
----------
baseobj :
    TODO: Describe

projection : Base.Vector
    Custom vector for the projection

facenumbers : [] TODO: Describe
    A list of face numbers to be considered in individual faces mode.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_shape2dview.py:42`. Decorators are copied as source expressions and have not been executed.

## `draftmake.make_shape2dview.make_shape2dview`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@deprecated(deprecated_in='26.3', removed_in='28.3', replacement='Draft.make_shape_2d_view()')
def make_shape2dview(baseobj, projectionVector=None, facenumbers=[]):
```

DEPRECATED. Use 'make_shape_2d_view'.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_shape2dview.py:80`. Decorators are copied as source expressions and have not been executed.

## `draftmake.make_shape2dview.makeShape2DView`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@deprecated(deprecated_in='26.3', removed_in='28.3', replacement='Draft.make_shape_2d_view()')
def makeShape2DView(baseobj, projectionVector=None, facenumbers=[]):
```

DEPRECATED. Use 'make_shape_2d_view'.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_shape2dview.py:90`. Decorators are copied as source expressions and have not been executed.

