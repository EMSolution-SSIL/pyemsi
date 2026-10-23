# Python source module `draftgeoutils.intersections`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftgeoutils/intersections.py`. Import path is source-routed; installed availability is unverified.

Provides various functions to calculate intersections of shapes.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import lazy_loader.lazy_loader as lz

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.intersections.lz` -> `lazy_loader.lazy_loader`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/intersections.py:32`.

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.intersections.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/intersections.py:34`.

### import DraftVecUtils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.intersections.DraftVecUtils` -> `DraftVecUtils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/intersections.py:35`.

### from draftgeoutils.general import precision, vec, geomType, isPtOnEdge

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.intersections.precision` -> `draftgeoutils.general.precision`.

Bound source name `draftgeoutils.intersections.vec` -> `draftgeoutils.general.vec`.

Bound source name `draftgeoutils.intersections.geomType` -> `draftgeoutils.general.geomType`.

Bound source name `draftgeoutils.intersections.isPtOnEdge` -> `draftgeoutils.general.isPtOnEdge`.

[Source module `draftgeoutils.general`](../general/index.md).

Evidence: `src/Mod/Draft/draftgeoutils/intersections.py:37`.

### from draftgeoutils.edges import findMidpoint

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.intersections.findMidpoint` -> `draftgeoutils.edges.findMidpoint`.

[Source module `draftgeoutils.edges`](../edges/index.md).

Evidence: `src/Mod/Draft/draftgeoutils/intersections.py:38`.

## `draftgeoutils.intersections.findIntersection`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def findIntersection(edge1, edge2, infinite1=False, infinite2=False, ex1=False, ex2=False, dts=True, findAll=False):
```

Return a list containing the intersection points of 2 edges.

You can also feed 4 points instead of `edge1` and `edge2`.
If `dts` is used, `Shape.section()` is used.

Parameters
----------
edge1
    Part.Edge, Circle, Line -> the first edge.
    Base::Vector3 -> the starting point of the first line. In which case
        `infinite1` must also be a point.
edge2
    Part.Edge, Circle, Line -> the second edge.
    Base::Vector3 -> the ending point of the second line. In which case
        `infinite2` must also be a point.
    the second edge. In case of a point, `infinite2` must also be a point.
infinite1
    bool, optional -> whether `edge1` should be continued to infinity.
    Default to `False`.
    Base::Vector3 -> if `edge1` is a point, must also be a point.
infinite2
    bool, optional -> whether `edge2` should be continued to infinity.
    Default to `False`.
    Base::Vector3 -> if `edge2` is a point, must also be a point.
ex1: bool, optional
    In case `edge1` is a point, indicate whether the line should be
    continued to infinity. Default to `False`
ex2: bool, optional
    In case `edge2` is a point, indicate whether the line should be
    continued to infinity. Default to `False`
dts: bool, optional
    NOT_DOCUMENTED. Default to `True`
findAll: bool, optional
    In case either `edge1` or `edge2` is a circle, indicates whether
    to find all intersection points. Default to `False`

Returns
-------
list
    A list of intersection points

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/intersections.py:47`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.intersections.wiresIntersect`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def wiresIntersect(wire1, wire2):
```

Return True if some of the edges of the wires are intersecting.

Otherwise return `False`.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/intersections.py:357`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.intersections.connect`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def connect(edges, closed=False, wireNedge=False):
```

Connect the edges in the given list by their intersections.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/intersections.py:369`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.intersections.angleBisection`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def angleBisection(edge1, edge2):
```

Return an edge that bisects the angle between the 2 straight edges.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/intersections.py:448`. Decorators are copied as source expressions and have not been executed.

