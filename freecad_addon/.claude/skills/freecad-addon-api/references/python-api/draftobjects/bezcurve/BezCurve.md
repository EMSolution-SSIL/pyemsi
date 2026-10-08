# `draftobjects.bezcurve.BezCurve`

[Source module](index.md)

```python
class BezCurve(DraftObject):
```

The BezCurve object

Evidence: `src/Mod/Draft/draftobjects/bezcurve.py:41`. Source-defined class; runtime behavior and support status unverified.

## `draftobjects.bezcurve.BezCurve.__init__`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def __init__(self, obj):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/bezcurve.py:44`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.bezcurve.BezCurve.onDocumentRestored`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def onDocumentRestored(self, obj):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/bezcurve.py:75`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.bezcurve.BezCurve.execute`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def execute(self, fp):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/bezcurve.py:81`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.bezcurve.BezCurve.resetcontinuity`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def resetcontinuity(self, fp):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/bezcurve.py:102`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.bezcurve.BezCurve.onChanged`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def onChanged(self, fp, prop):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/bezcurve.py:108`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.bezcurve.BezCurve.createGeometry`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def createGeometry(self, fp):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/bezcurve.py:136`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.bezcurve.BezCurve.symmetricpoles`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@classmethod
def symmetricpoles(cls, knot, p1, p2):
```

Make two poles symmetric respective to the knot.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/bezcurve.py:168`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.bezcurve.BezCurve.tangentpoles`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@classmethod
def tangentpoles(cls, knot, p1, p2, allowsameside=False):
```

Make two poles have the same tangent at knot.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/bezcurve.py:177`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.bezcurve.BezCurve.modifysymmetricpole`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@staticmethod
def modifysymmetricpole(knot, p1):
```

calculate the coordinates of the opposite pole
of a symmetric knot

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/bezcurve.py:193`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.bezcurve.BezCurve.modifytangentpole`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@staticmethod
def modifytangentpole(knot, p1, oldp2):
```

calculate the coordinates of the opposite pole
of a tangent knot

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/bezcurve.py:199`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`draftobjects.bezcurve.BezCurve._segpoleslst`. These are source internals unless an explicit export establishes otherwise.

