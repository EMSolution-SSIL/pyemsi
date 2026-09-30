# Python source module `draftgeoutils.arcs`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftgeoutils/arcs.py`. Import path is source-routed; installed availability is unverified.

Provides various functions to work with arcs.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import math

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.arcs.math` -> `math`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/arcs.py:32`.

### import lazy_loader.lazy_loader as lz

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.arcs.lz` -> `lazy_loader.lazy_loader`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/arcs.py:33`.

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.arcs.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/arcs.py:35`.

### import DraftVecUtils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.arcs.DraftVecUtils` -> `DraftVecUtils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/arcs.py:36`.

### from draftgeoutils.general import geomType

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.arcs.geomType` -> `draftgeoutils.general.geomType`.

[Source module `draftgeoutils.general`](../general/index.md).

Evidence: `src/Mod/Draft/draftgeoutils/arcs.py:38`.

### from draftgeoutils.edges import findMidpoint

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.arcs.findMidpoint` -> `draftgeoutils.edges.findMidpoint`.

[Source module `draftgeoutils.edges`](../edges/index.md).

Evidence: `src/Mod/Draft/draftgeoutils/arcs.py:39`.

## `draftgeoutils.arcs.isClockwise`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def isClockwise(edge, ref=None):
```

Return True if a circle-based edge has a clockwise direction.

Parameters
----------
edge :
    The edge to be analyzed.

ref : Vector, optional
    The normal around which the direction of the edge is to be determined.
    Defaults to the Z normal vector.

Returns
-------
bool
    Returns True if the edge is clockwise oriented around the ref Vector
    or not.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/arcs.py:48`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.arcs.isWideAngle`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def isWideAngle(edge):
```

Return True if the given edge is an arc with angle > 180 degrees.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/arcs.py:92`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.arcs.arcFrom2Pts`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def arcFrom2Pts(firstPt, lastPt, center, axis=None):
```

Build an arc with center and 2 points, can be oriented with axis.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/arcs.py:106`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.arcs.arcFromSpline`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def arcFromSpline(edge):
```

Turn given edge into a circular arc from three points.

Takes its first point, midpoint and endpoint. It works best with bspline
segments such as those from imported svg files. Use this only
if you are sure your edge is really an arc.

It returns None if there is a problem, including passing straight edges.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/arcs.py:130`. Decorators are copied as source expressions and have not been executed.

