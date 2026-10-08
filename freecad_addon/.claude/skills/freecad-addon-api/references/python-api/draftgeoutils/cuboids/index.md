# Python source module `draftgeoutils.cuboids`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftgeoutils/cuboids.py`. Import path is source-routed; installed availability is unverified.

Provides various functions to work with cubic shapes (parallelepipeds).

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import math

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.cuboids.math` -> `math`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/cuboids.py:32`.

### import sys

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.cuboids.sys` -> `sys`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/cuboids.py:33`.

### import lazy_loader.lazy_loader as lz

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.cuboids.lz` -> `lazy_loader.lazy_loader`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/cuboids.py:34`.

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.cuboids.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/cuboids.py:36`.

### from draftgeoutils.general import geomType, vec, precision

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.cuboids.geomType` -> `draftgeoutils.general.geomType`.

Bound source name `draftgeoutils.cuboids.vec` -> `draftgeoutils.general.vec`.

Bound source name `draftgeoutils.cuboids.precision` -> `draftgeoutils.general.precision`.

[Source module `draftgeoutils.general`](../general/index.md).

Evidence: `src/Mod/Draft/draftgeoutils/cuboids.py:38`.

## `draftgeoutils.cuboids.isCubic`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def isCubic(shape):
```

Return True if the shape is a parallelepiped (cuboid).

A parallelepiped of cube-like shape has 8 vertices, 6 faces, 12 edges,
and all angles are 90 degrees between its edges.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/cuboids.py:47`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.cuboids.getCubicDimensions`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getCubicDimensions(shape):
```

Return a list containing the placement, and dimensions of the shape.

The dimensions are length, width and height of a the parallelepiped, rounded to
the value indicated by `precision`. With the length larger than or equal to width.
The placement point is the center of the lowest face.

If it is not a parallelepiped (cuboid), return None.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/cuboids.py:79`. Decorators are copied as source expressions and have not been executed.

