# Python source module `draftgeoutils.circles`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftgeoutils/circles.py`. Import path is source-routed; installed availability is unverified.

Provides various functions to work with circles.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import math

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.circles.math` -> `math`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/circles.py:32`.

### import sys

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.circles.sys` -> `sys`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/circles.py:33`.

### import lazy_loader.lazy_loader as lz

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.circles.lz` -> `lazy_loader.lazy_loader`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/circles.py:34`.

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.circles.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/circles.py:36`.

### import DraftVecUtils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.circles.DraftVecUtils` -> `DraftVecUtils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/circles.py:37`.

### from draftgeoutils.general import geomType, edg, vec, NORM, v1

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.circles.geomType` -> `draftgeoutils.general.geomType`.

Bound source name `draftgeoutils.circles.edg` -> `draftgeoutils.general.edg`.

Bound source name `draftgeoutils.circles.vec` -> `draftgeoutils.general.vec`.

Bound source name `draftgeoutils.circles.NORM` -> `draftgeoutils.general.NORM`.

Bound source name `draftgeoutils.circles.v1` -> `draftgeoutils.general.v1`.

[Source module `draftgeoutils.general`](../general/index.md).

Evidence: `src/Mod/Draft/draftgeoutils/circles.py:39`.

### from draftgeoutils.geometry import mirror, findDistance

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.circles.mirror` -> `draftgeoutils.geometry.mirror`.

Bound source name `draftgeoutils.circles.findDistance` -> `draftgeoutils.geometry.findDistance`.

[Source module `draftgeoutils.geometry`](../geometry/index.md).

Evidence: `src/Mod/Draft/draftgeoutils/circles.py:40`.

### from draftgeoutils.edges import findMidpoint

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.circles.findMidpoint` -> `draftgeoutils.edges.findMidpoint`.

[Source module `draftgeoutils.edges`](../edges/index.md).

Evidence: `src/Mod/Draft/draftgeoutils/circles.py:41`.

### from draftgeoutils.intersections import findIntersection, angleBisection

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.circles.findIntersection` -> `draftgeoutils.intersections.findIntersection`.

Bound source name `draftgeoutils.circles.angleBisection` -> `draftgeoutils.intersections.angleBisection`.

[Source module `draftgeoutils.intersections`](../intersections/index.md).

Evidence: `src/Mod/Draft/draftgeoutils/circles.py:42`.

## `draftgeoutils.circles.findClosestCircle`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def findClosestCircle(point, circles):
```

Return the circle with closest center to a given point.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/circles.py:51`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.circles.getCircleFromSpline`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getCircleFromSpline(edge):
```

Return a circle-based edge from a bspline-based edge.

Return None if the edge is not a BSplineCurve.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/circles.py:62`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.circles.circlefrom1Line2Points`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def circlefrom1Line2Points(edge, p1, p2):
```

Return a list of circles created from an edge and two points.

It calculates up to 2 possible centers.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/circles.py:96`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.circles.circlefrom2Lines1Point`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def circlefrom2Lines1Point(edge1, edge2, point):
```

Return a list of circles from two edges and one point.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/circles.py:141`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.circles.circleFrom2LinesRadius`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def circleFrom2LinesRadius(edge1, edge2, radius):
```

Return a list of circles from two edges and one radius.

It calculates 4 centers.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/circles.py:151`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.circles.circleFrom3LineTangents`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def circleFrom3LineTangents(edge1, edge2, edge3):
```

Return a list of circles from three edges.

It calculates up to 6 possible centers.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/circles.py:186`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.circles.circleFromPointLineRadius`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def circleFromPointLineRadius(point, edge, radius):
```

Return a list of circles from one point, one edge, and one radius.

It calculates up to 2 possible centers.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/circles.py:247`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.circles.circleFrom2PointsRadius`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def circleFrom2PointsRadius(p1, p2, radius):
```

Return a list of circles from two points, and one radius.

The two points must not be equal.

It calculates up to 2 possible centers.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/circles.py:302`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.circles.findHomotheticCenterOfCircles`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def findHomotheticCenterOfCircles(circle1, circle2):
```

Calculate the homothetic centers from two circles.

Return None if the objects are not circles, or if they are concentric.

http://en.wikipedia.org/wiki/Homothetic_center
http://mathworld.wolfram.com/HomotheticCenter.html

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/circles.py:343`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.circles.findRadicalAxis`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def findRadicalAxis(circle1, circle2):
```

Calculate the radical axis of two circles.

On the radical axis (also called power line) of two circles any
tangents drawn from a point on the axis to both circles have
the same length.

http://en.wikipedia.org/wiki/Radical_axis
http://mathworld.wolfram.com/RadicalLine.html

See Also
--------
findRadicalCenter

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/circles.py:400`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.circles.findRadicalCenter`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def findRadicalCenter(circle1, circle2, circle3):
```

Calculate the radical center of three circles.

It is also called the power center.
It is the intersection point of the three radical axes of the pairs
of circles.

http://en.wikipedia.org/wiki/Power_center_(geometry)
http://mathworld.wolfram.com/RadicalCenter.html

See Also
--------
findRadicalAxis

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/circles.py:461`. Decorators are copied as source expressions and have not been executed.

