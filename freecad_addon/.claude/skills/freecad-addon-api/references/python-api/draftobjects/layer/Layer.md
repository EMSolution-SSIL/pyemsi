# `draftobjects.layer.Layer`

[Source module](index.md)

```python
class Layer:
```

The Layer object.

This class is normally used to extend a base `App::FeaturePython` object.

Evidence: `src/Mod/Draft/draftobjects/layer.py:42`. Source-defined class; runtime behavior and support status unverified.

## `draftobjects.layer.Layer.__init__`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def __init__(self, obj):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/layer.py:48`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.layer.Layer.set_properties`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def set_properties(self, obj):
```

Set properties only if they don't exist.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/layer.py:55`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.layer.Layer.onDocumentRestored`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def onDocumentRestored(self, obj):
```

Execute code when the document is restored.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/layer.py:64`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.layer.Layer.dumps`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def dumps(self):
```

Return a tuple of objects to save or None.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/layer.py:101`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.layer.Layer.loads`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def loads(self, state):
```

Set the internal properties from the restored state.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/layer.py:105`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.layer.Layer.execute`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def execute(self, obj):
```

Execute when the object is created or recomputed. Do nothing.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/layer.py:110`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.layer.Layer.onBeforeChange`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def onBeforeChange(self, obj, prop):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/layer.py:121`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.layer.Layer.onChanged`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def onChanged(self, obj, prop):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/layer.py:125`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.layer.Layer.addObject`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def addObject(self, obj, child):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/layer.py:142`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.layer.Layer.removeObject`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def removeObject(self, obj, child):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/layer.py:151`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`draftobjects.layer.Layer._get_other_layers`. These are source internals unless an explicit export establishes otherwise.

