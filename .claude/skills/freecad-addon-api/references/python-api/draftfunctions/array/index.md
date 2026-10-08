# Python source module `draftfunctions.array`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftfunctions/array.py`. Import path is source-routed; installed availability is unverified.

Provides functions to create non-parametric arrayed copies.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.array.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/array.py:35`.

### import draftutils.utils as utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.array.utils` -> `draftutils.utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/array.py:36`.

### import draftfunctions.move as move

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.array.move` -> `draftfunctions.move`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/array.py:37`.

### import draftfunctions.rotate as rotate

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.array.rotate` -> `draftfunctions.rotate`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/array.py:38`.

## `draftfunctions.array.array`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def array(objectslist, arg1, arg2, arg3, arg4=None, arg5=None, arg6=None):
```

This function creates an array of independent objects.
Use make_array() to create a parametric array object.

Creates an array of the given objects (that can be an object or a list
of objects).

In case of rectangular array, xnum of iterations in the x direction
at xvector distance between iterations, and same for y and z directions
with yvector and ynum and zvector and znum.

In case of polar array, center is a vector, totalangle is the angle
to cover (in degrees) and totalnum is the number of objects, including
the original.

Use
---
array(objectslist, xvector, yvector, xnum, ynum) for rectangular array

array(objectslist, xvector, yvector, zvector, xnum, ynum, znum) for rectangular array

array(objectslist, center, totalangle, totalnum) for polar array

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/array.py:41`. Decorators are copied as source expressions and have not been executed.

## `draftfunctions.array.rectArray`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def rectArray(objectslist, xvector, yvector, xnum, ynum):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/array.py:74`. Decorators are copied as source expressions and have not been executed.

## `draftfunctions.array.rectArray2`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def rectArray2(objectslist, xvector, yvector, zvector, xnum, ynum, znum):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/array.py:91`. Decorators are copied as source expressions and have not been executed.

## `draftfunctions.array.polarArray`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def polarArray(objectslist, center, angle, num):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/array.py:120`. Decorators are copied as source expressions and have not been executed.

