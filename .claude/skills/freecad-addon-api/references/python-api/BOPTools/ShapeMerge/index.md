# Python source module `BOPTools.ShapeMerge`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Part/BOPTools/ShapeMerge.py`. Import path is source-routed; installed availability is unverified.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import Part

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `BOPTools.ShapeMerge.Part` -> `Part`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Part/BOPTools/ShapeMerge.py:30`.

### from .Utils import HashableShape

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `BOPTools.ShapeMerge.HashableShape` -> `BOPTools.Utils.HashableShape`.

[Source module `BOPTools.Utils`](../Utils/index.md).

Evidence: `src/Mod/Part/BOPTools/ShapeMerge.py:31`.

## `BOPTools.ShapeMerge.findSharedElements`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def findSharedElements(shape_list, element_extractor):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/ShapeMerge.py:34`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.ShapeMerge.isConnected`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def isConnected(shape1, shape2, shape_dim=-1):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/ShapeMerge.py:54`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.ShapeMerge.splitIntoGroupsBySharing`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def splitIntoGroupsBySharing(list_of_shapes, element_extractor, split_connections=[]):
```

splitIntoGroupsBySharing(list_of_shapes, element_type, split_connections = []): find,
which shapes in list_of_shapes are connected into groups by sharing elements.

element_extractor: function that takes shape as input, and returns list of shapes.

split_connections: list of shapes to exclude when testing for connections. Use to
split groups on purpose.

return: list of lists of shapes. Top-level list is list of groups; bottom level lists
enumerate shapes of a group.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/ShapeMerge.py:66`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.ShapeMerge.mergeSolids`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def mergeSolids(list_of_solids_compsolids, flag_single=False, split_connections=[], bool_compsolid=False):
```

mergeSolids(list_of_solids, flag_single = False): merges touching solids that share
faces. If flag_single is True, it is assumed that all solids touch, and output is a
single solid. If flag_single is False, the output is a compound containing all
resulting solids.

Note. CompSolids are treated as lists of solids - i.e., merged into solids.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/ShapeMerge.py:135`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.ShapeMerge.mergeShells`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def mergeShells(list_of_faces_shells, flag_single=False, split_connections=[]):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/ShapeMerge.py:162`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.ShapeMerge.mergeWires`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def mergeWires(list_of_edges_wires, flag_single=False, split_connections=[]):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/ShapeMerge.py:173`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.ShapeMerge.mergeVertices`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def mergeVertices(list_of_vertices, flag_single=False, split_connections=[]):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/ShapeMerge.py:184`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.ShapeMerge.mergeShapes`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def mergeShapes(list_of_shapes, flag_single=False, split_connections=[], bool_compsolid=False):
```

mergeShapes(list_of_shapes, flag_single = False, split_connections = [], bool_compsolid = False):
merges list of edges/wires into wires, faces/shells into shells, solids/compsolids
into solids or compsolids.

list_of_shapes: shapes to merge. Shapes must share elements in order to be merged.

flag_single: assume all shapes in list are connected. If False, return is a compound.
If True, return is the single piece (e.g. a shell).

split_connections: list of shapes that are excluded when searching for connections.
This can be used for example to split a wire in two by supplying vertices where to
split. If flag_single is True, this argument is ignored.

bool_compsolid: determines behavior when dealing with solids/compsolids. If True,
result is compsolid/compound of compsolids. If False, all touching solids and
compsolids are unified into single solids. If not merging solids/compsolids, this
argument is ignored.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/ShapeMerge.py:189`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.ShapeMerge.removeDuplicates`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def removeDuplicates(list_of_shapes):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/ShapeMerge.py:225`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.ShapeMerge.dimensionOfShapes`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def dimensionOfShapes(list_of_shapes):
```

dimensionOfShapes(list_of_shapes): returns dimension (0D, 1D, 2D, or 3D) of shapes
in the list. If dimension of shapes varies, TypeError is raised.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/ShapeMerge.py:238`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`BOPTools.ShapeMerge.__title__`, `BOPTools.ShapeMerge.__author__`, `BOPTools.ShapeMerge.__url__`, `BOPTools.ShapeMerge.__doc__`. These are source internals unless an explicit export establishes otherwise.

