# Python source module `draftfunctions.rotate`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftfunctions/rotate.py`. Import path is source-routed; installed availability is unverified.

Provides functions to rotate shapes around a center and axis.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import math

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.rotate.math` -> `math`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/rotate.py:34`.

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.rotate.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/rotate.py:36`.

### import DraftVecUtils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.rotate.DraftVecUtils` -> `DraftVecUtils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/rotate.py:37`.

### from draftfunctions import join

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.rotate.join` -> `draftfunctions.join`.

[Source module `draftfunctions`](../index.md).

Evidence: `src/Mod/Draft/draftfunctions/rotate.py:38`.

### from draftmake import make_copy

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.rotate.make_copy` -> `draftmake.make_copy`.

[Source module `draftmake`](../../draftmake/index.md).

Evidence: `src/Mod/Draft/draftfunctions/rotate.py:39`.

### from draftmake import make_line

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.rotate.make_line` -> `draftmake.make_line`.

[Source module `draftmake`](../../draftmake/index.md).

Evidence: `src/Mod/Draft/draftfunctions/rotate.py:40`.

### from draftobjects import layer

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.rotate.layer` -> `draftobjects.layer`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/rotate.py:41`.

### from draftutils import groups

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.rotate.groups` -> `draftutils.groups`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/rotate.py:42`.

### from draftutils import gui_utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.rotate.gui_utils` -> `draftutils.gui_utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/rotate.py:43`.

### from draftutils import params

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.rotate.params` -> `draftutils.params`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/rotate.py:44`.

### from draftutils import utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.rotate.utils` -> `draftutils.utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/rotate.py:45`.

## `draftfunctions.rotate.rotate`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def rotate(selection, angle, center=App.Vector(0, 0, 0), axis=App.Vector(0, 0, 1), copy=False, subelements=False):
```

rotate(selection, angle, [center], [axis], [copy], [subelements])

Rotates or copies selected objects.

Parameters
----------
selection: single object / list of objects / selection set
    When dealing with nested objects, use `Gui.Selection.getSelectionEx("", 0)`
    to create the selection set.

angle: float / integer
    Rotation angle (in degrees).

center: App.Vector, optional
    Defaults to `App.Vector(0, 0, 0)`.
    Rotation center.

axis: App.Vector, optional
    Defaults to `App.Vector(0, 0, 1)`.
    Rotation axis.

copy: bool, optional
    Defaults to `False`.
    If `True` the selected objects are not rotated, but rotated copies are
    created instead.

subelements: bool, optional
    Defaults to `False`.
    If `True` subelements instead of whole objects are processed.
    Only used if selection is a selection set.

Returns
-------
single object / list with 2 or more objects / empty list
    The objects (or their copies).

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/rotate.py:48`. Decorators are copied as source expressions and have not been executed.

## `draftfunctions.rotate.rotate_vector_from_center`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def rotate_vector_from_center(vector, angle, axis, center):
```

Needed for SubObjects modifiers.
Implemented by Dion Moult during 0.19 dev cycle (works only with Draft Wire).

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/rotate.py:231`. Decorators are copied as source expressions and have not been executed.

## `draftfunctions.rotate.rotate_vertex`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def rotate_vertex(obj, vert_idx, angle, center, axis, global_place=None):
```

Needed for SubObjects modifiers.
Implemented by Dion Moult during 0.19 dev cycle (works only with Draft Wire).

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/rotate.py:241`. Decorators are copied as source expressions and have not been executed.

## `draftfunctions.rotate.rotate_edge`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def rotate_edge(obj, edge_idx, angle, center, axis, global_place=None):
```

Needed for SubObjects modifiers.
Implemented by Dion Moult during 0.19 dev cycle (works only with Draft Wire).

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/rotate.py:257`. Decorators are copied as source expressions and have not been executed.

## `draftfunctions.rotate.copy_rotated_edge`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def copy_rotated_edge(obj, edge_idx, angle, center, axis, global_place=None):
```

Needed for SubObjects modifiers.
Implemented by Dion Moult during 0.19 dev cycle (works only with Draft Wire).

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/rotate.py:269`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`draftfunctions.rotate._rotate_subelements`. These are source internals unless an explicit export establishes otherwise.

