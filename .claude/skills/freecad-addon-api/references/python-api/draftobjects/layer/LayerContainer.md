# `draftobjects.layer.LayerContainer`

[Source module](index.md)

```python
class LayerContainer:
```

The container object for layers.

This class is normally used to extend
a base `App::DocumentObjectGroupPython` object.

Evidence: `src/Mod/Draft/draftobjects/layer.py:163`. Source-defined class; runtime behavior and support status unverified.

## `draftobjects.layer.LayerContainer.__init__`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def __init__(self, obj):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/layer.py:170`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.layer.LayerContainer.onDocumentRestored`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def onDocumentRestored(self, obj):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/layer.py:174`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.layer.LayerContainer.execute`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def execute(self, obj):
```

Execute when the object is created or recomputed.

Update the value of `Group` by sorting the contained layers
by `Label`.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/layer.py:179`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.layer.LayerContainer.dumps`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def dumps(self):
```

Return a tuple of objects to save or None.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/layer.py:189`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.layer.LayerContainer.loads`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def loads(self, state):
```

Set the internal properties from the restored state.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/layer.py:194`. Decorators are copied as source expressions and have not been executed.

