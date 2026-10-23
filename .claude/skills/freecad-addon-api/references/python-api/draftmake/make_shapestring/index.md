# Python source module `draftmake.make_shapestring`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftmake/make_shapestring.py`. Import path is source-routed; installed availability is unverified.

Provides functions to create ShapeString objects.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_shapestring.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_shapestring.py:33`.

### from draftobjects.shapestring import ShapeString

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_shapestring.ShapeString` -> `draftobjects.shapestring.ShapeString`.

[Source module `draftobjects.shapestring`](../../draftobjects/shapestring/index.md).

Evidence: `src/Mod/Draft/draftmake/make_shapestring.py:34`.

### from draftutils import gui_utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_shapestring.gui_utils` -> `draftutils.gui_utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_shapestring.py:35`.

### from freecad.deprecation import deprecated

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_shapestring.deprecated` -> `freecad.deprecation.deprecated`.

[Source module `freecad.deprecation`](../../freecad/deprecation/index.md).

Evidence: `src/Mod/Draft/draftmake/make_shapestring.py:36`.

### from draftviewproviders.view_shapestring import ViewProviderShapeString

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if App.GuiUp`.

Bound source name `draftmake.make_shapestring.ViewProviderShapeString` -> `draftviewproviders.view_shapestring.ViewProviderShapeString`.

[Source module `draftviewproviders.view_shapestring`](../../draftviewproviders/view_shapestring/index.md).

Evidence: `src/Mod/Draft/draftmake/make_shapestring.py:39`.

## `draftmake.make_shapestring.make_shape_string`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def make_shape_string(string, fontfile, size=100, tracking=0):
```

make_shape_string(string, fontfile, [size], [tracking])

Turns a text string into a Compound Shape

Parameters
----------
majradius :
    Major radius of the ellipse.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_shapestring.py:42`. Decorators are copied as source expressions and have not been executed.

## `draftmake.make_shapestring.make_shapestring`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@deprecated(deprecated_in='26.3', removed_in='28.3', replacement='Draft.make_shape_string()')
def make_shapestring(String, FontFile, Size=100, Tracking=0):
```

DEPRECATED. Use 'make_shape_string'.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_shapestring.py:80`. Decorators are copied as source expressions and have not been executed.

## `draftmake.make_shapestring.makeShapeString`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@deprecated(deprecated_in='26.3', removed_in='28.3', replacement='Draft.make_shape_string()')
def makeShapeString(String, FontFile, Size=100, Tracking=0):
```

DEPRECATED. Use 'make_shape_string'.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_shapestring.py:90`. Decorators are copied as source expressions and have not been executed.

