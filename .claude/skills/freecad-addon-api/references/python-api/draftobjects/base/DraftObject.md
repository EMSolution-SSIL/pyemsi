# `draftobjects.base.DraftObject`

[Source module](index.md)

```python
class DraftObject(object):
```

The base class for Draft objects.

Parameters
----------
obj : a base C++ object
    The base object instantiated during creation,
    which commonly may be of types `Part::Part2DObjectPython`,
    `Part::FeaturePython`, or `App::FeaturePython`.

        >>> obj = App.ActiveDocument.addObject('Part::Part2DObjectPython')
        >>> DraftObject(obj)

    This class instance is stored in the `Proxy` attribute
    of the base object.
    ::
        obj.Proxy = self

tp : str, optional
    It defaults to `'Unknown'`.
    It indicates the type of this scripted object,
    which will be assigned to the Proxy's `Type` attribute.

    This is useful to distinguish different types of scripted objects
    that may be derived from the same C++ class.

Attributes
----------
Type : str
    It indicates the type of scripted object.
    Normally `Type = tp`.

    All objects have a `TypeId` attribute, but this attribute
    refers to the C++ class only. Using the `Type` attribute
    allows distinguishing among various types of objects
    derived from the same C++ class.

        >>> print(obj.TypeId, "->", obj.Proxy.Type)
        Part::Part2DObjectPython -> Circle

This class attribute is accessible through the `Proxy` object:
`obj.Proxy.Type`.

Evidence: `src/Mod/Draft/draftobjects/base.py:35`. Source-defined class; runtime behavior and support status unverified.

## `draftobjects.base.DraftObject.__init__`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def __init__(self, obj, tp='Unknown'):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/base.py:79`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.base.DraftObject.onDocumentRestored`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def onDocumentRestored(self, obj):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/base.py:85`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.base.DraftObject.dumps`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def dumps(self):
```

Return a tuple of all serializable objects or None.

When saving the document this object gets stored
using Python's `json` module.

Override this method to define the serializable objects to return.

By default it returns the `Type` attribute.

Returns
-------
str
    Returns the value of `Type`

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/base.py:89`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.base.DraftObject.loads`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def loads(self, state):
```

Set some internal properties for all restored objects.

When a document is restored this method is used to set some properties
for the objects stored with `json`.

Override this method to define the properties to change for the
restored serialized objects.

By default the `Type` was serialized, so `state` holds this value,
which is re-assigned to the `Type` attribute.
::
    self.Type = state

Parameters
----------
state : state
    A serialized object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/base.py:106`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.base.DraftObject.execute`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def execute(self, obj):
```

Run this method when the object is created or recomputed.

Override this method to produce effects when the object
is newly created, and whenever the document is recomputed.

By default it does nothing.

Parameters
----------
obj : the scripted object.
    This commonly may be of types `Part::Part2DObjectPython`,
    `Part::FeaturePython`, or `App::FeaturePython`.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/base.py:128`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.base.DraftObject.onChanged`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def onChanged(self, obj, prop):
```

Run this method when a property is changed.

Override this method to handle the behavior
of the object depending on changes that occur to its properties.

By default it does nothing.

Parameters
----------
obj : the scripted object.
    This commonly may be of types `Part::Part2DObjectPython`,
    `Part::FeaturePython`, or `App::FeaturePython`.

prop : str
    Name of the property that was modified.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/base.py:144`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.base.DraftObject.props_changed_store`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def props_changed_store(self, prop):
```

Store the name of the property that will be changed in the
self.props_changed list.

The function should be called at the start of onChanged or onBeforeChange.

The list is used to detect Placement-only changes. In such cases the
Shape of an object does not need to be updated. Not updating the Shape
avoids Uno/Redo issues for the Windows version and is also more efficient.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/base.py:163`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.base.DraftObject.props_changed_clear`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def props_changed_clear(self):
```

Remove the self.props_changed attribute if it exists.

The function should be called just before execute returns.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/base.py:178`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.base.DraftObject.props_changed_placement_only`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def props_changed_placement_only(self, obj=None):
```

Return `True` if the self.props_changed list, after removing
`_LinkTouched`, `Shape`, `Density`, `Volume` and `Mass` items,
only contains `Placement` items.

Parameters
----------
obj : the scripted object. Need only be supplied if the Shape of obj
    is, or can be, derived from other objects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/base.py:186`. Decorators are copied as source expressions and have not been executed.

