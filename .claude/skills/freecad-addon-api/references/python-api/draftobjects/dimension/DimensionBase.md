# `draftobjects.dimension.DimensionBase`

[Source module](index.md)

```python
class DimensionBase(DraftAnnotation):
```

The base objects for dimension objects.

This class inherits `DraftAnnotation` to define the basic properties
of all annotation type objects, like a scaling multiplier.

This class is not used directly, but inherited by all dimension
objects.

Evidence: `src/Mod/Draft/draftobjects/dimension.py:118`. Source-defined class; runtime behavior and support status unverified.

## `draftobjects.dimension.DimensionBase.set_properties`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def set_properties(self, obj):
```

Set basic properties only if they don't exist.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/dimension.py:128`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.dimension.DimensionBase.update_properties_0v21`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def update_properties_0v21(self, obj, vobj):
```

Update view properties.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/dimension.py:189`. Decorators are copied as source expressions and have not been executed.

