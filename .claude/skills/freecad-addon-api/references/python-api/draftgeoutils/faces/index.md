# Python source module `draftgeoutils.faces`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftgeoutils/faces.py`. Import path is source-routed; installed availability is unverified.

Provides various functions to work with faces.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import lazy_loader.lazy_loader as lz

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.faces.lz` -> `lazy_loader.lazy_loader`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/faces.py:32`.

### import DraftVecUtils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.faces.DraftVecUtils` -> `DraftVecUtils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/faces.py:34`.

### from FreeCAD import Base

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.faces.Base` -> `FreeCAD.Base`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/faces.py:35`.

### from draftgeoutils.geometry import are_coplanar

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.faces.are_coplanar` -> `draftgeoutils.geometry.are_coplanar`.

[Source module `draftgeoutils.geometry`](../geometry/index.md).

Evidence: `src/Mod/Draft/draftgeoutils/faces.py:36`.

### from draftutils.messages import _err, _wrn

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.faces._err` -> `draftutils.messages._err`.

Bound source name `draftgeoutils.faces._wrn` -> `draftutils.messages._wrn`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/faces.py:37`.

## `draftgeoutils.faces.concatenate`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def concatenate(shape):
```

Turn several faces into one.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/faces.py:46`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.faces.getBoundary`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getBoundary(shape):
```

Return the boundary edges of a group of faces.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/faces.py:67`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.faces.is_coplanar`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def is_coplanar(faces, tol=-1):
```

Return True if all faces in the given list are coplanar.

Parameters
----------
faces: list
    List of faces to check coplanarity.
tol: float, optional
    It defaults to `-1`, the tolerance of confusion, equal to 1e-7.
    Is the maximum deviation to be considered coplanar.

Returns
-------
out: bool
    True if all face are coplanar. False in other case.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/faces.py:91`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.faces.isCoplanar`

Status: source-defined name; no independently verified stability/export guarantee.

```python
isCoplanar = is_coplanar
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/Draft/draftgeoutils/faces.py:116`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.faces.bind`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def bind(w1, w2, per_segment=False):
```

Bind 2 wires by their endpoints and returns a face / compound of faces.

If per_segment is True and the wires have the same number of edges, the
wires are processed per segment: a separate face is created for each pair
of edges (one from w1 and one from w2), and the faces are then fused. This
avoids problems with walls based on wires that selfintersect, or that have
a loop that ends in a T-connection (f.e. a wire shaped like a number 6).

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/faces.py:171`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.faces.cleanFaces`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def cleanFaces(shape):
```

Remove inner edges from coplanar faces.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/faces.py:309`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.faces.removeSplitter`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def removeSplitter(shape):
```

Return a face from removing the splitter in a list of faces.

This is an alternative, shared edge-based version of Part.removeSplitter.
Returns a face, or `None` if the operation failed.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/faces.py:417`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`draftgeoutils.faces._make_segment_face`. These are source internals unless an explicit export establishes otherwise.

