# `draftobjects.draftlink.DraftLink`

[Source module](index.md)

```python
class DraftLink(DraftObject):
```

New class to use the App::Link objects in arrays.

Introduced by realthunder.
This is subclassed by `draftobjects.array.Array`
and by `draftobjects.patharray.PathArray`.

Evidence: `src/Mod/Draft/draftobjects/draftlink.py:56`. Source-defined class; runtime behavior and support status unverified.

## `draftobjects.draftlink.DraftLink.__init__`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def __init__(self, obj, tp):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/draftlink.py:64`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.draftlink.DraftLink.dumps`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def dumps(self):
```

Return a tuple of all serializable objects or None.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/draftlink.py:70`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.draftlink.DraftLink.loads`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def loads(self, state):
```

Set some internal properties for all restored objects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/draftlink.py:74`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.draftlink.DraftLink.attach`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def attach(self, obj):
```

Set up the properties when the object is attached.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/draftlink.py:82`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.draftlink.DraftLink.canLinkProperties`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def canLinkProperties(self, _obj):
```

Link properties.

TODO: add more explanation. Overrides a C++ method?

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/draftlink.py:88`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.draftlink.DraftLink.linkSetup`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def linkSetup(self, obj):
```

Set up the link properties on attachment.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/draftlink.py:95`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.draftlink.DraftLink.getViewProviderName`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getViewProviderName(self, _obj):
```

Override the view provider name.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/draftlink.py:141`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.draftlink.DraftLink.migrate_attributes`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def migrate_attributes(self, obj):
```

Migrate old attribute names to new names if they exist.

This is done to comply with Python guidelines or fix small issues
in older code.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/draftlink.py:147`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.draftlink.DraftLink.onDocumentRestored`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def onDocumentRestored(self, obj):
```

Execute code when the document in restored.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/draftlink.py:162`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.draftlink.DraftLink.buildShape`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def buildShape(self, obj, pl, pls):
```

Build the shape of the link object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/draftlink.py:187`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.draftlink.DraftLink.onChanged`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def onChanged(self, obj, prop):
```

Execute when a property changes.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/draftlink.py:237`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.draftlink.DraftLink.getPlacementOf`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getPlacementOf(self, fp, subname, targetObj=None):
```

Return the placement of the sub-object relative to the link object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/draftlink.py:256`. Decorators are copied as source expressions and have not been executed.

