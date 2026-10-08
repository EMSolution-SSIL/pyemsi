# Python source module `draftfunctions.scale`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftfunctions/scale.py`. Import path is source-routed; installed availability is unverified.

Provides functions to scale shapes.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import math

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.scale.math` -> `math`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/scale.py:34`.

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.scale.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/scale.py:36`.

### import DraftVecUtils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.scale.DraftVecUtils` -> `DraftVecUtils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/scale.py:37`.

### from draftfunctions import join

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.scale.join` -> `draftfunctions.join`.

[Source module `draftfunctions`](../index.md).

Evidence: `src/Mod/Draft/draftfunctions/scale.py:38`.

### from draftmake import make_clone

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.scale.make_clone` -> `draftmake.make_clone`.

[Source module `draftmake`](../../draftmake/index.md).

Evidence: `src/Mod/Draft/draftfunctions/scale.py:39`.

### from draftmake import make_copy

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.scale.make_copy` -> `draftmake.make_copy`.

[Source module `draftmake`](../../draftmake/index.md).

Evidence: `src/Mod/Draft/draftfunctions/scale.py:40`.

### from draftmake import make_line

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.scale.make_line` -> `draftmake.make_line`.

[Source module `draftmake`](../../draftmake/index.md).

Evidence: `src/Mod/Draft/draftfunctions/scale.py:41`.

### from draftmake import make_wire

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.scale.make_wire` -> `draftmake.make_wire`.

[Source module `draftmake`](../../draftmake/index.md).

Evidence: `src/Mod/Draft/draftfunctions/scale.py:42`.

### from draftobjects import layer

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.scale.layer` -> `draftobjects.layer`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/scale.py:43`.

### from draftutils import gui_utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.scale.gui_utils` -> `draftutils.gui_utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/scale.py:44`.

### from draftutils import params

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.scale.params` -> `draftutils.params`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/scale.py:45`.

### from draftutils import utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.scale.utils` -> `draftutils.utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/scale.py:46`.

## `draftfunctions.scale.scale`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def scale(selection, scale, center=App.Vector(0, 0, 0), copy=False, clone=False, subelements=False):
```

scale(selection, scale, [center], [copy], [clone], [subelements])

Scales or copies selected objects.

Parameters
----------
selection: single object / list of objects / selection set
    When dealing with nested objects, use `Gui.Selection.getSelectionEx("", 0)`
    to create the selection set.

scale: App.Vector
    The X, Y and Z component of the vector define the scale factors.

center: App.Vector, optional
    Defaults to `App.Vector(0, 0, 0)`.
    Center of the scale operation.

copy: bool, optional
    Defaults to `False`.
    If `True` the selected objects are not scaled, but scaled copies are
    created instead. If clone is `True`, copy is internally set to `False`.

clone: bool, optional
    Defaults to `False`.
    If `True` the selected objects are not scaled, but scaled clones are
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

Evidence: `src/Mod/Draft/draftfunctions/scale.py:49`. Decorators are copied as source expressions and have not been executed.

## `draftfunctions.scale.scale_vector_from_center`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def scale_vector_from_center(vector, scale, center):
```

Needed for SubObjects modifiers.
Implemented by Dion Moult during 0.19 dev cycle (works only with Draft Wire).

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/scale.py:374`. Decorators are copied as source expressions and have not been executed.

## `draftfunctions.scale.scale_vertex`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def scale_vertex(obj, vert_idx, scale, center, global_place=None):
```

Needed for SubObjects modifiers.
Implemented by Dion Moult during 0.19 dev cycle (works only with Draft Wire).

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/scale.py:382`. Decorators are copied as source expressions and have not been executed.

## `draftfunctions.scale.scale_edge`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def scale_edge(obj, edge_idx, scale, center, global_place=None):
```

Needed for SubObjects modifiers.
Implemented by Dion Moult during 0.19 dev cycle (works only with Draft Wire).

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/scale.py:398`. Decorators are copied as source expressions and have not been executed.

## `draftfunctions.scale.copy_scaled_edge`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def copy_scaled_edge(obj, edge_idx, scale, center, global_place=None):
```

Needed for SubObjects modifiers.
Implemented by Dion Moult during 0.19 dev cycle (works only with Draft Wire).

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/scale.py:410`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`draftfunctions.scale._scale_subelements`, `draftfunctions.scale._get_scaled_matrix`. These are source internals unless an explicit export establishes otherwise.

