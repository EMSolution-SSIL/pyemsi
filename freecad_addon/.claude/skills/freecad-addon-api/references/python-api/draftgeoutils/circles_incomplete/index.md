# Python source module `draftgeoutils.circles_incomplete`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftgeoutils/circles_incomplete.py`. Import path is source-routed; installed availability is unverified.

Provides various incomplete functions for creating circles.

These functions cannot be used because they require that certain functions
to calculate shapes exist first.

These functions are meant to create circles starting from three values,
either a tangent edge, a point, or a radius. Various combinations
are possible.

- Two tangents and a point.
- Two tangents and a radius.
- A tangent and two points.
- A tangent, a point, and a radius.
- Three tangents.

In this case, the word 'tangent' refers to either a straight line
or to a circular edge, so even more combinations are possible.

- Two tangents and a point.
  * Line, line, and point.
  * Circle, line, and point.
  * Line, circle, and point.
  * Circle, circle, and point.

And so on, with the other combinations.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import FreeCAD

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.circles_incomplete.FreeCAD` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/circles_incomplete.py:59`.

### from draftutils.messages import _wrn

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.circles_incomplete._wrn` -> `draftutils.messages._wrn`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/circles_incomplete.py:61`.

### from draftgeoutils.general import geomType

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.circles_incomplete.geomType` -> `draftgeoutils.general.geomType`.

[Source module `draftgeoutils.general`](../general/index.md).

Evidence: `src/Mod/Draft/draftgeoutils/circles_incomplete.py:62`.

### from draftgeoutils.circles import circlefrom2Lines1Point, circleFrom2LinesRadius, circlefrom1Line2Points, circleFromPointLineRadius, circleFrom3LineTangents

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.circles_incomplete.circlefrom2Lines1Point` -> `draftgeoutils.circles.circlefrom2Lines1Point`.

Bound source name `draftgeoutils.circles_incomplete.circleFrom2LinesRadius` -> `draftgeoutils.circles.circleFrom2LinesRadius`.

Bound source name `draftgeoutils.circles_incomplete.circlefrom1Line2Points` -> `draftgeoutils.circles.circlefrom1Line2Points`.

Bound source name `draftgeoutils.circles_incomplete.circleFromPointLineRadius` -> `draftgeoutils.circles.circleFromPointLineRadius`.

Bound source name `draftgeoutils.circles_incomplete.circleFrom3LineTangents` -> `draftgeoutils.circles.circleFrom3LineTangents`.

[Source module `draftgeoutils.circles`](../circles/index.md).

Evidence: `src/Mod/Draft/draftgeoutils/circles_incomplete.py:63`.

### from draftgeoutils.circles_apollonius import circleFrom3CircleTangents

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.circles_incomplete.circleFrom3CircleTangents` -> `draftgeoutils.circles_apollonius.circleFrom3CircleTangents`.

[Source module `draftgeoutils.circles_apollonius`](../circles_apollonius/index.md).

Evidence: `src/Mod/Draft/draftgeoutils/circles_incomplete.py:70`.

## `draftgeoutils.circles_incomplete.circlefromCircleLinePoint`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def circlefromCircleLinePoint(circle, line, point):
```

Do nothing. Placeholder function. Needs to be implemented.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/circles_incomplete.py:73`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.circles_incomplete.circlefrom2Circles1Point`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def circlefrom2Circles1Point(circle1, circle2, point):
```

Do nothing. Placeholder function. Needs to be implemented.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/circles_incomplete.py:78`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.circles_incomplete.circleFrom2tan1pt`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def circleFrom2tan1pt(tan1, tan2, point):
```

Circle from two tangents and one point.

The tangents should be edges, and they may be either straight line edges
or circular edges, so four combinations are possible.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/circles_incomplete.py:83`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.circles_incomplete.circleFromCircleLineRadius`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def circleFromCircleLineRadius(circle, line, radius):
```

Do nothing. Placeholder function. Needs to be implemented.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/circles_incomplete.py:114`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.circles_incomplete.circleFrom2CirclesRadius`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def circleFrom2CirclesRadius(circle1, circle2, radius):
```

Do nothing. Placeholder function. Needs to be implemented.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/circles_incomplete.py:119`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.circles_incomplete.circleFrom2tan1rad`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def circleFrom2tan1rad(tan1, tan2, rad):
```

Circle from two tangents and one radius.

The tangents should be edges, and they may be either straight line edges
or circular edges, so four combinations are possible.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/circles_incomplete.py:124`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.circles_incomplete.circlefrom1Circle2Points`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def circlefrom1Circle2Points(circle, point1, point2):
```

Do nothing. Placeholder function. Needs to be implemented.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/circles_incomplete.py:143`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.circles_incomplete.circleFrom1tan2pt`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def circleFrom1tan2pt(tan1, p1, p2):
```

Circle from one tangent and two points.

The tangents should be edges, and they may be either straight line edges
or circular edges, so two combinations are possible.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/circles_incomplete.py:148`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.circles_incomplete.circleFromPointCircleRadius`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def circleFromPointCircleRadius(point, circle, radius):
```

Do nothing. Placeholder function. Needs to be implemented.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/circles_incomplete.py:169`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.circles_incomplete.circleFrom1tan1pt1rad`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def circleFrom1tan1pt1rad(tan1, p1, rad):
```

Circle from one tangent, one point, and radius.

The tangents should be edges, and they may be either straight line edges
or circular edges, so two combinations are possible.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/circles_incomplete.py:174`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.circles_incomplete.circleFrom1Circle2Lines`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def circleFrom1Circle2Lines(circle, line1, line2):
```

Do nothing. Placeholder function. Needs to be implemented.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/circles_incomplete.py:187`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.circles_incomplete.circleFrom2Circle1Lines`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def circleFrom2Circle1Lines(circle1, circle2, line):
```

Do nothing. Placeholder function. Needs to be implemented.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/circles_incomplete.py:192`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.circles_incomplete.circleFrom3tan`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def circleFrom3tan(tan1, tan2, tan3):
```

Circle from three tangents.

The tangents should be edges, and they may be either straight line edges
or circular edges, so eight combinations are possible.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/circles_incomplete.py:197`. Decorators are copied as source expressions and have not been executed.

