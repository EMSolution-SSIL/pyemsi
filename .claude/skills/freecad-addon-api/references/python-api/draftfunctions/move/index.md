# Python source module `draftfunctions.move`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftfunctions/move.py`. Import path is source-routed; installed availability is unverified.

Provides functions to move objects from one position to another.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.move.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/move.py:34`.

### from draftfunctions import join

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.move.join` -> `draftfunctions.join`.

[Source module `draftfunctions`](../index.md).

Evidence: `src/Mod/Draft/draftfunctions/move.py:35`.

### from draftmake import make_copy

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.move.make_copy` -> `draftmake.make_copy`.

[Source module `draftmake`](../../draftmake/index.md).

Evidence: `src/Mod/Draft/draftfunctions/move.py:36`.

### from draftmake import make_line

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.move.make_line` -> `draftmake.make_line`.

[Source module `draftmake`](../../draftmake/index.md).

Evidence: `src/Mod/Draft/draftfunctions/move.py:37`.

### from draftobjects import layer

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.move.layer` -> `draftobjects.layer`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/move.py:38`.

### from draftutils import gui_utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.move.gui_utils` -> `draftutils.gui_utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/move.py:39`.

### from draftutils import params

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.move.params` -> `draftutils.params`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/move.py:40`.

### from draftutils import utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.move.utils` -> `draftutils.utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/move.py:41`.

## `draftfunctions.move.move`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def move(selection, vector, copy=False, subelements=False):
```

move(selection, vector, [copy], [subelements])

Moves or copies selected objects.

Parameters
----------
selection: single object / list of objects / selection set
    When dealing with nested objects, use `Gui.Selection.getSelectionEx("", 0)`
    to create the selection set.

vector: App.Vector
    Delta vector.

copy: bool, optional
    Defaults to `False`.
    If `True` the selected objects are not moved, but moved copies are
    created instead.

subelements: bool, optional
    Defaults to `False`.
    If `True` subelements instead of whole objects are processed.
    Only used if selection is a selection set.

Returns
-------
single object / list with 2 or more objects / empty list
    The objects (or their copies)

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/move.py:44`. Decorators are copied as source expressions and have not been executed.

## `draftfunctions.move.move_vertex`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def move_vertex(obj, vert_idx, vector, global_place=None):
```

Needed for SubObjects modifiers.
Implemented by Dion Moult during 0.19 dev cycle (works only with Draft Wire).

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/move.py:201`. Decorators are copied as source expressions and have not been executed.

## `draftfunctions.move.move_edge`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def move_edge(obj, edge_idx, vector, global_place=None):
```

Needed for SubObjects modifiers.
Implemented by Dion Moult during 0.19 dev cycle (works only with Draft Wire).

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/move.py:216`. Decorators are copied as source expressions and have not been executed.

## `draftfunctions.move.copy_moved_edge`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def copy_moved_edge(obj, edge_idx, vector, global_place=None):
```

Needed for SubObjects modifiers.
Implemented by Dion Moult during 0.19 dev cycle (works only with Draft Wire).

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/move.py:228`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`draftfunctions.move._move_subelements`. These are source internals unless an explicit export establishes otherwise.

