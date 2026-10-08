# `draftobjects.dimension.AngularDimension`

[Source module](index.md)

```python
class AngularDimension(DimensionBase):
```

The angular dimension object.

This inherits `DimensionBase` to provide the basic functionality of
a dimension.

Evidence: `src/Mod/Draft/draftobjects/dimension.py:492`. Source-defined class; runtime behavior and support status unverified.

## `draftobjects.dimension.AngularDimension.__init__`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def __init__(self, obj):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/dimension.py:499`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.dimension.AngularDimension.set_properties`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def set_properties(self, obj):
```

Set basic properties only if they don't exist.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/dimension.py:504`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.dimension.AngularDimension.onDocumentRestored`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def onDocumentRestored(self, obj):
```

Execute code when the document is restored.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/dimension.py:563`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.dimension.AngularDimension.loads`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def loads(self, state):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/dimension.py:577`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.dimension.AngularDimension.transform`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def transform(self, obj, pla):
```

Transform the object by applying a placement.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/dimension.py:580`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.dimension.AngularDimension.execute`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def execute(self, obj):
```

Execute when the object is created or recomputed.

Nothing is actually done here, except update the viewprovider,
as the lines and text are created in the viewprovider.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/dimension.py:598`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.dimension.AngularDimension.onChanged`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def onChanged(self, obj, prop):
```

Execute when a property is changed.

It just sets some properties to be read-only or hidden,
as they aren't used.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/dimension.py:625`. Decorators are copied as source expressions and have not been executed.

