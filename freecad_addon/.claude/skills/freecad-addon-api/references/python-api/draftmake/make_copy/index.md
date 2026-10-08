# Python source module `draftmake.make_copy`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftmake/make_copy.py`. Import path is source-routed; installed availability is unverified.

Provides functions to create copies of objects.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_copy.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_copy.py:33`.

### from draftutils import gui_utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_copy.gui_utils` -> `draftutils.gui_utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_copy.py:34`.

### from draftutils import utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_copy.utils` -> `draftutils.utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_copy.py:35`.

### from freecad.deprecation import deprecated

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_copy.deprecated` -> `freecad.deprecation.deprecated`.

[Source module `freecad.deprecation`](../../freecad/deprecation/index.md).

Evidence: `src/Mod/Draft/draftmake/make_copy.py:36`.

## `draftmake.make_copy.make_copy`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def make_copy(obj, force=None, reparent=False, simple_copy=False):
```

make_copy(object, [force], [reparent], [simple_copy])

Make an exact copy of an object and return it.

Parameters
----------
obj :
    Object to copy.

force :
    Obsolete, not used anymore.

reparent :
    Group the new object in the same group of the old one.

simple_copy :
    Create a simple copy of the object (a new non parametric
    Part::Feature with the same Shape as the given object).

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_copy.py:39`. Decorators are copied as source expressions and have not been executed.

## `draftmake.make_copy.makeCopy`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@deprecated(deprecated_in='26.3', removed_in='28.3', replacement='Draft.make_copy()')
def makeCopy(*args, **kwarg):
```

DEPRECATED. Use 'make_copy'.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_copy.py:104`. Decorators are copied as source expressions and have not been executed.

