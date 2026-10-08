# Python source module `draftmake.make_line`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftmake/make_line.py`. Import path is source-routed; installed availability is unverified.

Provides functions to create two-point Wire objects.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_line.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_line.py:33`.

### import draftmake.make_wire as make_wire

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_line.make_wire` -> `draftmake.make_wire`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_line.py:34`.

### from freecad.deprecation import deprecated

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_line.deprecated` -> `freecad.deprecation.deprecated`.

[Source module `freecad.deprecation`](../../freecad/deprecation/index.md).

Evidence: `src/Mod/Draft/draftmake/make_line.py:35`.

## `draftmake.make_line.make_line`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def make_line(first_param, last_param=None):
```

make_line(first_param, p2)

Creates a line from 2 points or from a given object.

Parameters
----------
first_param :
    Base.Vector -> First point of the line (if p2 is None)
    Part.LineSegment -> Line is created from the given Linesegment
    Shape -> Line is created from the give Shape

last_param : Base.Vector
    Second point of the line, if not set the function evaluates
    the first_param to look for a Part.LineSegment or a Shape

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_line.py:38`. Decorators are copied as source expressions and have not been executed.

## `draftmake.make_line.makeLine`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@deprecated(deprecated_in='26.3', removed_in='28.3', replacement='Draft.make_line()')
def makeLine(*args, **kwarg):
```

DEPRECATED. Use 'make_line'.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_line.py:78`. Decorators are copied as source expressions and have not been executed.

