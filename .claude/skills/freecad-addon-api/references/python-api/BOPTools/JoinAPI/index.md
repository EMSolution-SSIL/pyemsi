# Python source module `BOPTools.JoinAPI`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Part/BOPTools/JoinAPI.py`. Import path is source-routed; installed availability is unverified.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import Part

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `BOPTools.JoinAPI.Part` -> `Part`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Part/BOPTools/JoinAPI.py:30`.

### from . import ShapeMerge

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `BOPTools.JoinAPI.ShapeMerge` -> `BOPTools.ShapeMerge`.

[Source module `BOPTools`](../index.md).

Evidence: `src/Mod/Part/BOPTools/JoinAPI.py:31`.

### from .GeneralFuseResult import GeneralFuseResult

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `BOPTools.JoinAPI.GeneralFuseResult` -> `BOPTools.GeneralFuseResult.GeneralFuseResult`.

[Source module `BOPTools.GeneralFuseResult`](../GeneralFuseResult/index.md).

Evidence: `src/Mod/Part/BOPTools/JoinAPI.py:32`.

### from .Utils import compoundLeaves

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `BOPTools.JoinAPI.compoundLeaves` -> `BOPTools.Utils.compoundLeaves`.

[Source module `BOPTools.Utils`](../Utils/index.md).

Evidence: `src/Mod/Part/BOPTools/JoinAPI.py:33`.

## `BOPTools.JoinAPI.shapeOfMaxSize`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def shapeOfMaxSize(list_of_shapes):
```

shapeOfMaxSize(list_of_shapes): finds the shape that has the largest "
"mass in the list and returns it. The shapes in the list must be of same dimension.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/JoinAPI.py:36`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.JoinAPI.connect`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def connect(list_of_shapes, tolerance=0.0):
```

connect(list_of_shapes, tolerance = 0.0): connects solids (walled objects), shells and
wires by throwing off small parts that result when splitting them at intersections.

Compounds in list_of_shapes are automatically exploded, so self-intersecting compounds
are valid for connect.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/JoinAPI.py:61`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.JoinAPI.connect_legacy`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def connect_legacy(shape1, shape2, tolerance=0.0):
```

connect_legacy(shape1, shape2, tolerance = 0.0): alternative implementation of
connect, without use of generalFuse. Slow. Provided for backwards compatibility, and
for older OCC.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/JoinAPI.py:118`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.JoinAPI.embed_legacy`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def embed_legacy(shape_base, shape_tool, tolerance=0.0):
```

embed_legacy(shape_base, shape_tool, tolerance = 0.0): alternative implementation of
embed, without use of generalFuse. Slow. Provided for backwards compatibility, and
for older OCC.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/JoinAPI.py:138`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.JoinAPI.cutout_legacy`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def cutout_legacy(shape_base, shape_tool, tolerance=0.0):
```

cutout_legacy(shape_base, shape_tool, tolerance = 0.0): alternative implementation of
cutout, without use of generalFuse. Slow. Provided for backwards compatibility, and
for older OCC.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/JoinAPI.py:160`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`BOPTools.JoinAPI.__title__`, `BOPTools.JoinAPI.__author__`, `BOPTools.JoinAPI.__url__`, `BOPTools.JoinAPI.__doc__`. These are source internals unless an explicit export establishes otherwise.

