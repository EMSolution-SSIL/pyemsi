# Python source module `draftgeoutils.general`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftgeoutils/general.py`. Import path is source-routed; installed availability is unverified.

Provides general functions to work with topological shapes.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import math

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.general.math` -> `math`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/general.py:32`.

### import sys

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.general.sys` -> `sys`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/general.py:33`.

### import lazy_loader.lazy_loader as lz

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.general.lz` -> `lazy_loader.lazy_loader`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/general.py:34`.

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.general.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/general.py:36`.

### import DraftVecUtils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.general.DraftVecUtils` -> `DraftVecUtils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/general.py:37`.

### from draftutils import params

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.general.params` -> `draftutils.params`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/general.py:38`.

## `draftgeoutils.general.precision`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def precision():
```

Return the Draft precision setting.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/general.py:50`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.general.vec`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def vec(edge, use_orientation=False):
```

Return a vector from an edge or a Part.LineSegment.

If use_orientation is True, it takes into account the edges orientation.
If edge is not straight, you'll get strange results!

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/general.py:66`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.general.edg`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def edg(p1, p2):
```

Return an edge from 2 vectors.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/general.py:83`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.general.getVerts`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getVerts(shape):
```

Return a list containing vectors of each vertex of the shape.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/general.py:92`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.general.v1`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def v1(edge):
```

Return the first point of an edge.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/general.py:103`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.general.isNull`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def isNull(something):
```

Return True if the given shape, vector, or placement is Null.

If the vector is (0, 0, 0), it will return True.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/general.py:108`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.general.isPtOnEdge`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def isPtOnEdge(pt, edge):
```

Test if a point lies on an edge.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/general.py:127`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.general.hasCurves`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def hasCurves(shape):
```

Check if the given shape has curves.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/general.py:141`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.general.isAligned`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def isAligned(edge, axis='x'):
```

Check if the given edge or line is aligned to the given axis.

The axis can be 'x', 'y' or 'z'.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/general.py:149`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.general.getQuad`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getQuad(face):
```

Return a list of 3 vectors if the face is a quad, otherwise None.

Returns
-------
basepoint, Xdir, Ydir
    If the face is a quad.

None
    If the face is not a quad.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/general.py:182`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.general.areColinear`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def areColinear(e1, e2):
```

Return True if both edges are colinear.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/general.py:214`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.general.hasOnlyWires`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def hasOnlyWires(shape):
```

Return True if all edges are inside a wire.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/general.py:235`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.general.geomType`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def geomType(edge):
```

Return the type of geometry this edge is based on.

Parameters
----------
edge: the edge whose `Curve` attribute is to be checked.

Returns
-------
str
    Return the type of the edge's Curve attribute or "Unknown",
    if the parameter is missing.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/general.py:245`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.general.isValidPath`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def isValidPath(shape):
```

Return True if the shape can be used as an extrusion path.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/general.py:275`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.general.findClosest`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def findClosest(base_point, point_list):
```

Find closest point in a list of points to the base point.

Returns
-------
int
    An index from the list of points is returned.

None
    If point_list is empty.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/general.py:291`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.general.getBoundaryAngles`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getBoundaryAngles(angle, alist):
```

Return the 2 closest angles that encompass the given angle.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/general.py:316`. Decorators are copied as source expressions and have not been executed.

