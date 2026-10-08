# `draftobjects.fillet.Fillet`

[Source module](index.md)

```python
class Fillet(DraftObject):
```

Proxy class for the Fillet object.

Evidence: `src/Mod/Draft/draftobjects/fillet.py:38`. Source-defined class; runtime behavior and support status unverified.

## `draftobjects.fillet.Fillet.__init__`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def __init__(self, obj):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/fillet.py:41`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.fillet.Fillet.onDocumentRestored`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def onDocumentRestored(self, obj):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/fillet.py:45`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.fillet.Fillet.execute`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def execute(self, obj):
```

Run when the object is created or recomputed.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/fillet.py:97`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.fillet.Fillet.onChanged`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def onChanged(self, obj, prop):
```

Change the radius of fillet. NOT IMPLEMENTED.

This should automatically recalculate the new fillet
based on the new value of `FilletRadius`.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/fillet.py:112`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`draftobjects.fillet.Fillet._set_properties`, `draftobjects.fillet.Fillet._update_radius`. These are source internals unless an explicit export establishes otherwise.

