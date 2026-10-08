# Python source module `draftgeoutils.edges`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftgeoutils/edges.py`. Import path is source-routed; installed availability is unverified.

Provides various functions to work with edges.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import lazy_loader.lazy_loader as lz

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.edges.lz` -> `lazy_loader.lazy_loader`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/edges.py:32`.

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.edges.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/edges.py:34`.

### import DraftVecUtils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.edges.DraftVecUtils` -> `DraftVecUtils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/edges.py:35`.

### from draftgeoutils.general import geomType, vec

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.edges.geomType` -> `draftgeoutils.general.geomType`.

Bound source name `draftgeoutils.edges.vec` -> `draftgeoutils.general.vec`.

[Source module `draftgeoutils.general`](../general/index.md).

Evidence: `src/Mod/Draft/draftgeoutils/edges.py:37`.

## `draftgeoutils.edges.findEdge`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def findEdge(anEdge, aList):
```

Return True if edge is found in list of edges.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/edges.py:46`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.edges.orientEdge`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def orientEdge(edge, normal=None, make_arc=False):
```

Re-orient the edge such that it is in the XY plane.

Re-orients `edge` such that it is in the XY plane.
If `normal` is passed, this is used as the basis for the rotation,
otherwise the placement of `edge` is used.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/edges.py:56`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.edges.isSameLine`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def isSameLine(e1, e2):
```

Return True if the 2 edges are lines and have the same points.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/edges.py:91`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.edges.is_line`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def is_line(bspline):
```

Return True if the given BSpline curve is a straight line.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/edges.py:109`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.edges.invert`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def invert(shape):
```

Return an inverted copy of the edge or wire contained in the shape.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/edges.py:131`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.edges.findMidpoint`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def findMidpoint(edge):
```

Return the midpoint of an edge.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/edges.py:156`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.edges.getTangent`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getTangent(edge, from_point=None):
```

Return the tangent to an edge, including BSpline and circular arcs.

If from_point is given, it is used to calculate the tangent,
only useful for a circular arc.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/edges.py:164`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.edges.get_referenced_edges`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_referenced_edges(property_value):
```

Return the Edges referenced by the value of a App:PropertyLink, App::PropertyLinkList,
App::PropertyLinkSub or App::PropertyLinkSubList property.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/edges.py:189`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.edges.isLine`

Status: source-defined name; no independently verified stability/export guarantee.

```python
isLine = is_line
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/Draft/draftgeoutils/edges.py:214`. Decorators are copied as source expressions and have not been executed.

