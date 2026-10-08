# `draftobjects.array.Array`

[Source module](index.md)

```python
class Array(DraftLink):
```

The Draft Array object.

To Do
-----
The `Array` class currently handles three types of arrays,
orthogonal, polar, and circular. In the future, probably they should be
split in separate classes so that they are easier to manage.

Evidence: `src/Mod/Draft/draftobjects/array.py:50`. Source-defined class; runtime behavior and support status unverified.

## `draftobjects.array.Array.__init__`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def __init__(self, obj):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/array.py:60`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.array.Array.attach`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def attach(self, obj):
```

Set up the properties when the object is attached.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/array.py:63`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.array.Array.onDocumentRestored`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def onDocumentRestored(self, obj):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/array.py:68`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.array.Array.set_properties`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def set_properties(self, obj):
```

Set properties only if they don't exist.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/array.py:83`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.array.Array.set_general_properties`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def set_general_properties(self, obj):
```

Set general properties only if they don't exist.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/array.py:95`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.array.Array.set_ortho_properties`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def set_ortho_properties(self, obj):
```

Set orthogonal properties only if they don't exist.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/array.py:153`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.array.Array.set_polar_circular_properties`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def set_polar_circular_properties(self, obj):
```

Set general polar and circular properties if they don't exist.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/array.py:205`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.array.Array.set_polar_properties`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def set_polar_properties(self, obj):
```

Set polar properties only if they don't exist.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/array.py:253`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.array.Array.set_circular_properties`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def set_circular_properties(self, obj):
```

Set circular properties only if they don't exist.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/array.py:276`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.array.Array.set_link_properties`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def set_link_properties(self, obj):
```

Set link properties only if they don't exist.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/array.py:316`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.array.Array.linkSetup`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def linkSetup(self, obj):
```

Set up the object as a link object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/array.py:328`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.array.Array.onChanged`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def onChanged(self, obj, prop):
```

Execute when a property is changed.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/array.py:334`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.array.Array.show_and_hide`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def show_and_hide(self, obj, prop):
```

Show and hide the properties depending on the touched property.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/array.py:340`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.array.Array.execute`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def execute(self, obj):
```

Execute when the object is created or recomputed.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/array.py:410`. Decorators are copied as source expressions and have not been executed.

