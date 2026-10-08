# Python source module `BOPTools.SplitAPI`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Part/BOPTools/SplitAPI.py`. Import path is source-routed; installed availability is unverified.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import Part

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `BOPTools.SplitAPI.Part` -> `Part`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Part/BOPTools/SplitAPI.py:30`.

### from . import ShapeMerge

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `BOPTools.SplitAPI.ShapeMerge` -> `BOPTools.ShapeMerge`.

[Source module `BOPTools`](../index.md).

Evidence: `src/Mod/Part/BOPTools/SplitAPI.py:31`.

### from .GeneralFuseResult import GeneralFuseResult

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `BOPTools.SplitAPI.GeneralFuseResult` -> `BOPTools.GeneralFuseResult.GeneralFuseResult`.

[Source module `BOPTools.GeneralFuseResult`](../GeneralFuseResult/index.md).

Evidence: `src/Mod/Part/BOPTools/SplitAPI.py:32`.

### from . import Utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `BOPTools.SplitAPI.Utils` -> `BOPTools.Utils`.

[Source module `BOPTools`](../index.md).

Evidence: `src/Mod/Part/BOPTools/SplitAPI.py:33`.

### import FreeCAD

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `BOPTools.SplitAPI.FreeCAD` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Part/BOPTools/SplitAPI.py:34`.

## `BOPTools.SplitAPI.booleanFragments`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def booleanFragments(list_of_shapes, mode, tolerance=0.0):
```

booleanFragments(list_of_shapes, mode, tolerance = 0.0): functional part of
BooleanFragments feature. It's just result of generalFuse plus a bit of
post-processing.

mode is a string. It can be "Standard", "Split" or "CompSolid".
"Standard" - return generalFuse as is.
"Split" - wires and shells will be split at intersections.
"CompSolid" - solids will be extracted from result of generelFuse, and compsolids will
be made from them; all other stuff is discarded.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/SplitAPI.py:37`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.SplitAPI.slice`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def slice(base_shape, tool_shapes, mode, tolerance=0.0):
```

slice(base_shape, tool_shapes, mode, tolerance = 0.0): functional part of
Slice feature. Splits base_shape into pieces based on intersections with tool_shapes.

mode is a string. It can be "Standard", "Split" or "CompSolid".
"Standard" - return like generalFuse: edges, faces and solids are split, but wires,
shells, compsolids get extra segments but remain in one piece.
"Split" - wires and shells will be split at intersections, too.
"CompSolid" - slice a solid and glue it back together to make a compsolid

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/SplitAPI.py:68`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.SplitAPI.xor`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def xor(list_of_shapes, tolerance=0.0):
```

xor(list_of_shapes, tolerance = 0.0): boolean XOR operation.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/SplitAPI.py:106`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`BOPTools.SplitAPI.__title__`, `BOPTools.SplitAPI.__author__`, `BOPTools.SplitAPI.__url__`, `BOPTools.SplitAPI.__doc__`. These are source internals unless an explicit export establishes otherwise.

