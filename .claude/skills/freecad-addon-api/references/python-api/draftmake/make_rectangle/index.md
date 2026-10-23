# Python source module `draftmake.make_rectangle`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftmake/make_rectangle.py`. Import path is source-routed; installed availability is unverified.

Provides functions to create Rectangle objects.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_rectangle.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_rectangle.py:33`.

### from draftobjects.rectangle import Rectangle

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_rectangle.Rectangle` -> `draftobjects.rectangle.Rectangle`.

[Source module `draftobjects.rectangle`](../../draftobjects/rectangle/index.md).

Evidence: `src/Mod/Draft/draftmake/make_rectangle.py:34`.

### from draftutils import utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_rectangle.utils` -> `draftutils.utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_rectangle.py:35`.

### from draftutils import gui_utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_rectangle.gui_utils` -> `draftutils.gui_utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_rectangle.py:36`.

### from freecad.deprecation import deprecated

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_rectangle.deprecated` -> `freecad.deprecation.deprecated`.

[Source module `freecad.deprecation`](../../freecad/deprecation/index.md).

Evidence: `src/Mod/Draft/draftmake/make_rectangle.py:37`.

### from draftviewproviders.view_rectangle import ViewProviderRectangle

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if App.GuiUp`.

Bound source name `draftmake.make_rectangle.ViewProviderRectangle` -> `draftviewproviders.view_rectangle.ViewProviderRectangle`.

[Source module `draftviewproviders.view_rectangle`](../../draftviewproviders/view_rectangle/index.md).

Evidence: `src/Mod/Draft/draftmake/make_rectangle.py:40`.

## `draftmake.make_rectangle.make_rectangle`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def make_rectangle(length, height=0, placement=None, face=None, support=None):
```

make_rectangle(length, width, [placement], [face])

Creates a Rectangle object with length in X direction and height in Y
direction.

Parameters
----------
length, height : dimensions of the rectangle

placement : Base.Placement
    If a placement is given, it is used.

face : Bool
    If face is False, the rectangle is shown as a wireframe,
    otherwise as a face.

Rectangles can also be constructed by giving them a list of four vertices
as first argument: make_rectangle(list_of_vertices, face=...)
but you are responsible to check yourself that these 4 vertices are ordered
and actually form a rectangle, otherwise the result might be wrong. Placement
is ignored when constructing a rectangle this way (face argument is kept).

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_rectangle.py:43`. Decorators are copied as source expressions and have not been executed.

## `draftmake.make_rectangle.makeRectangle`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@deprecated(deprecated_in='26.3', removed_in='28.3', replacement='Draft.make_rectangle()')
def makeRectangle(*args, **kwarg):
```

DEPRECATED. Use 'make_rectangle'.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_rectangle.py:109`. Decorators are copied as source expressions and have not been executed.

