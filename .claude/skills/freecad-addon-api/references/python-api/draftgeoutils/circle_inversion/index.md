# Python source module `draftgeoutils.circle_inversion`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftgeoutils/circle_inversion.py`. Import path is source-routed; installed availability is unverified.

Provides various functions for inversive operations using a circle.

http://en.wikipedia.org/wiki/Inversive_geometry

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import lazy_loader.lazy_loader as lz

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.circle_inversion.lz` -> `lazy_loader.lazy_loader`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/circle_inversion.py:35`.

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.circle_inversion.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/circle_inversion.py:37`.

### import DraftVecUtils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.circle_inversion.DraftVecUtils` -> `DraftVecUtils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/circle_inversion.py:38`.

### from draftgeoutils.general import NORM, geomType

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.circle_inversion.NORM` -> `draftgeoutils.general.NORM`.

Bound source name `draftgeoutils.circle_inversion.geomType` -> `draftgeoutils.general.geomType`.

[Source module `draftgeoutils.general`](../general/index.md).

Evidence: `src/Mod/Draft/draftgeoutils/circle_inversion.py:40`.

### from draftgeoutils.geometry import findDistance

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.circle_inversion.findDistance` -> `draftgeoutils.geometry.findDistance`.

[Source module `draftgeoutils.geometry`](../geometry/index.md).

Evidence: `src/Mod/Draft/draftgeoutils/circle_inversion.py:41`.

## `draftgeoutils.circle_inversion.pointInversion`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def pointInversion(circle, point):
```

Return the circle inversion of a point.

It will return `None` if the given point is equal to the center
of the circle.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/circle_inversion.py:50`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.circle_inversion.polarInversion`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def polarInversion(circle, edge):
```

Return the inversion pole of a line. The edge is the polar.

The nearest point on the line is inversed.

http://mathworld.wolfram.com/InversionPole.html

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/circle_inversion.py:79`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.circle_inversion.circleInversion`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def circleInversion(circle, circle2):
```

Circle inversion of a circle, inverting the center point.

Returns the new circle created from the inverted center of circle2.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/circle_inversion.py:99`. Decorators are copied as source expressions and have not been executed.

