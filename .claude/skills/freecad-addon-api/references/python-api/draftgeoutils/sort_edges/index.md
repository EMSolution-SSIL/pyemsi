# Python source module `draftgeoutils.sort_edges`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftgeoutils/sort_edges.py`. Import path is source-routed; installed availability is unverified.

Provides various functions to sort lists of edges.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import lazy_loader.lazy_loader as lz

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.sort_edges.lz` -> `lazy_loader.lazy_loader`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/sort_edges.py:32`.

### from draftgeoutils.general import geomType

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.sort_edges.geomType` -> `draftgeoutils.general.geomType`.

[Source module `draftgeoutils.general`](../general/index.md).

Evidence: `src/Mod/Draft/draftgeoutils/sort_edges.py:34`.

### from draftgeoutils.edges import findMidpoint, isLine, invert

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.sort_edges.findMidpoint` -> `draftgeoutils.edges.findMidpoint`.

Bound source name `draftgeoutils.sort_edges.isLine` -> `draftgeoutils.edges.isLine`.

Bound source name `draftgeoutils.sort_edges.invert` -> `draftgeoutils.edges.invert`.

[Source module `draftgeoutils.edges`](../edges/index.md).

Evidence: `src/Mod/Draft/draftgeoutils/sort_edges.py:35`.

## `draftgeoutils.sort_edges.sortEdges`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def sortEdges(edges):
```

Sort edges. Deprecated. Use Part.__sortEdges__ instead.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/sort_edges.py:44`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.sort_edges.sortEdgesOld`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def sortEdgesOld(lEdges, aVertex=None):
```

Sort edges. Deprecated. Use Part.__sortEdges__ instead.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/sort_edges.py:127`. Decorators are copied as source expressions and have not been executed.

