# Python source module `draftgeoutils.circles_apollonius`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftgeoutils/circles_apollonius.py`. Import path is source-routed; installed availability is unverified.

Provides various functions for Apollonius and Soddy circle operations.

The 'problem of Appollonius' consists of finding a circle that is
simultaneously tangent to three circles on a plane.

- http://en.wikipedia.org/wiki/Problem_of_Apollonius#Inversive_methods
- http://mathworld.wolfram.com/ApolloniusCircle.html
- http://mathworld.wolfram.com/ApolloniusProblem.html

If each circle only has one intersection with each other, the problem is that
of finding a 'Soddy circle', which has two solutions, and inner circle
and an outer circle.

- http://en.wikipedia.org/wiki/Problem_of_Apollonius#Mutually_tangent_given_circles:_Soddy.27s_circles_and_Descartes.27_theorem
- http://mathworld.wolfram.com/SoddyCircles.html
- http://mathworld.wolfram.com/InnerSoddyCenter.html
- http://mathworld.wolfram.com/OuterSoddyCenter.html

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import cmath

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.circles_apollonius.cmath` -> `cmath`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/circles_apollonius.py:49`.

### import math

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.circles_apollonius.math` -> `math`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/circles_apollonius.py:50`.

### import lazy_loader.lazy_loader as lz

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.circles_apollonius.lz` -> `lazy_loader.lazy_loader`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/circles_apollonius.py:51`.

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.circles_apollonius.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/circles_apollonius.py:53`.

### from draftgeoutils.general import geomType, NORM

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.circles_apollonius.geomType` -> `draftgeoutils.general.geomType`.

Bound source name `draftgeoutils.circles_apollonius.NORM` -> `draftgeoutils.general.NORM`.

[Source module `draftgeoutils.general`](../general/index.md).

Evidence: `src/Mod/Draft/draftgeoutils/circles_apollonius.py:55`.

### from draftgeoutils.intersections import findIntersection

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.circles_apollonius.findIntersection` -> `draftgeoutils.intersections.findIntersection`.

[Source module `draftgeoutils.intersections`](../intersections/index.md).

Evidence: `src/Mod/Draft/draftgeoutils/circles_apollonius.py:56`.

## `draftgeoutils.circles_apollonius.outerSoddyCircle`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def outerSoddyCircle(circle1, circle2, circle3):
```

Compute the outer soddy circle for three tightly packed circles.

Original Java code Copyright (rc) 2008 Werner Randelshofer
Converted to python by Martin Buerbaum 2009
http://www.randelshofer.ch/treeviz/
Either Creative Commons Attribution 3.0, the MIT license,
or the GNU Lesser General License LGPL.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/circles_apollonius.py:65`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.circles_apollonius.innerSoddyCircle`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def innerSoddyCircle(circle1, circle2, circle3):
```

Compute the inner soddy circle for three tightly packed circles.

Original Java code Copyright (rc) 2008 Werner Randelshofer
Converted to python by Martin Buerbaum 2009
http://www.randelshofer.ch/treeviz/

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/circles_apollonius.py:122`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.circles_apollonius.circleFrom3CircleTangents`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def circleFrom3CircleTangents(circle1, circle2, circle3):
```

Return the circle that is tangent to three other circles.

This problem is called the 'Problem of Appollonius'.

A special case is that of 'Soddy circles'.

To Do
-----
Currently not all possible solutions are found, only the Soddy circles.

* Calc all 6 homothetic centers.
* Create 3 lines from the inner and 4 from the outer h. center.
* Calc. the 4 inversion poles of these lines for each circle.
* Calc. the radical center of the 3 circles.
* Calc. the intersection points (max. 8) of 4 lines (through each
  inversion pole and the radical center) with the circle.
* This gives us all the tangent points.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/circles_apollonius.py:177`. Decorators are copied as source expressions and have not been executed.

