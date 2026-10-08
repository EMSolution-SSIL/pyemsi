# `draftobjects.dimension.LinearDimension`

[Source module](index.md)

```python
class LinearDimension(DimensionBase):
```

The linear dimension object.

This inherits `DimensionBase` to provide the basic functionality of
a dimension.

This linear dimension includes measurements between two vertices,
but also a radial dimension of a circular edge or arc.

Evidence: `src/Mod/Draft/draftobjects/dimension.py:197`. Source-defined class; runtime behavior and support status unverified.

## `draftobjects.dimension.LinearDimension.__init__`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def __init__(self, obj):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/dimension.py:207`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.dimension.LinearDimension.set_properties`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def set_properties(self, obj):
```

Set basic properties only if they don't exist.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/dimension.py:212`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.dimension.LinearDimension.onDocumentRestored`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def onDocumentRestored(self, obj):
```

Execute code when the document is restored.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/dimension.py:290`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.dimension.LinearDimension.loads`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def loads(self, state):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/dimension.py:304`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.dimension.LinearDimension.onChanged`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def onChanged(self, obj, prop):
```

Execute when a property is changed.

It just sets some properties to be read-only or hidden,
as they aren't used.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/dimension.py:307`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.dimension.LinearDimension.transform`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def transform(self, obj, pla):
```

Transform the object by applying a placement.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/dimension.py:321`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.dimension.LinearDimension.execute`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def execute(self, obj):
```

Execute when the object is created or recomputed.

Set start point and end point according to the linked geometry
and the number of subelements.

If it has one subelement, we assume a straight edge or a circular edge.
If it has two subelements, we assume a straight edge (two vertices).

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/dimension.py:329`. Decorators are copied as source expressions and have not been executed.

