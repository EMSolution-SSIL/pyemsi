# Python source module `draftgeoutils.linear_algebra`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftgeoutils/linear_algebra.py`. Import path is source-routed; installed availability is unverified.

Provides various functions for linear algebra.

This includes calculating linear equation parameters, and matrix determinants.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.linear_algebra.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/linear_algebra.py:37`.

## `draftgeoutils.linear_algebra.linearFromPoints`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def linearFromPoints(p1, p2):
```

Calculate linear equation from points.

Calculate the slope and offset parameters of the linear equation
of a line defined by two points.

Linear equation:
y = m * x + b
m = dy / dx
m ... Slope
b ... Offset (point where the line intersects the y axis)
dx/dy ... Delta x and y. Using both as a vector results
in a non-offset direction vector.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/linear_algebra.py:40`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.linear_algebra.determinant`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def determinant(mat, n):
```

Return the determinant of an N-matrix.

It recursively expands the minors.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/linear_algebra.py:65`. Decorators are copied as source expressions and have not been executed.

