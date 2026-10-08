# Python source module `draftutils.groups`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftutils/groups.py`. Import path is source-routed; installed availability is unverified.

Provides utility functions to do operations with groups.

The functions here are also used in the Arch Workbench as some of
the objects created with this workbench work like groups.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftutils.groups.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftutils/groups.py:39`.

### import draftutils.utils as utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftutils.groups.utils` -> `draftutils.utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftutils/groups.py:40`.

### from draftutils.translate import translate

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftutils.groups.translate` -> `draftutils.translate.translate`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftutils/groups.py:42`.

### from draftutils.messages import _err

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftutils.groups._err` -> `draftutils.messages._err`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftutils/groups.py:43`.

## `draftutils.groups.is_group`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def is_group(obj):
```

Return True if the given object is considered a group.

Parameters
----------
obj : App::DocumentObject
    The object to check.

Returns
-------
bool
    Returns `True` if `obj` is considered a group:

    The object is derived from `App::DocumentObjectGroup` but not
    a `'LayerContainer'`.

    Or the object is of the type `'Project'`, `'Site'`, `'Building'`,
    `'Floor'`, `'BuildingPart'` or `'Space'` from the Arch Workbench.
    Note that `'Floor'` and `'Building'` are obsolete types.

    Otherwise returns `False`.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/groups.py:46`. Decorators are copied as source expressions and have not been executed.

## `draftutils.groups.get_group_names`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_group_names(doc=None):
```

Return a list of names of existing groups in the document.

Parameters
----------
doc: App::Document, optional
    It defaults to `None`.
    A document on which to search group names.
    It if is `None` it will search the current document.

Returns
-------
list of str
    A list of names of objects that are considered groups.
    See the is_group function.

    Otherwise returns an empty list.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/groups.py:79`. Decorators are copied as source expressions and have not been executed.

## `draftutils.groups.getGroupNames`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getGroupNames():
```

Return a list of group names. DEPRECATED.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/groups.py:113`. Decorators are copied as source expressions and have not been executed.

## `draftutils.groups.ungroup`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def ungroup(obj):
```

Remove the object from any group to which it belongs.

A "group" is any object returned by `get_group_names`.

Parameters
----------
obj: App::DocumentObject or str
    Any type of object.
    If it is a string, it must be the `Label` of that object.
    Since a label is not guaranteed to be unique in a document,
    it will use the first object found with this label.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/groups.py:119`. Decorators are copied as source expressions and have not been executed.

## `draftutils.groups.get_windows`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_windows(obj):
```

Return the windows and rebars inside a host.

Parameters
----------
obj: App::DocumentObject
    A scripted object of type `'Wall'`, `'Roof'`, `'Structure'` or
    `'CurtainWall'` (BIM Workbench).
    This will be searched for objects of type `'Window'` and `'Rebar'`,
    and clones of them, and the found elements will be added
    to the output list.

    The function will search recursively all elements under `obj.OutList`,
    in case the windows and rebars are nested under other hosts.

Returns
-------
list
    A list of all found windows and rebars in `obj`.
    If `obj` is itself a `'Window'` or a `'Rebar'`, or a clone of them,
    it will return the same `obj` element.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/groups.py:153`. Decorators are copied as source expressions and have not been executed.

## `draftutils.groups.get_group_contents`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_group_contents(objectslist, walls=False, addgroups=False, spaces=False, noarchchild=False, exclude_names=None):
```

Return a list of objects from expanding the input groups.

The function accepts any type of object, although it is most useful
with "groups", as it is meant to unpack the objects inside these groups.

Parameters
----------
objectslist: list
    If any object in the list is considered a group, see the `is_group`
    function, its contents (`obj.Group`) are extracted and added to the
    output list.

    Single items that aren't groups are added to the output list
    as is.

walls: bool, optional
    It defaults to `False`.
    If it is `True`, Wall, Roof, Structure and CurtainWall objects
    (BIM Workbench) are treated as groups; they are scanned for Window,
    Door, and Rebar objects, and these are added to the output list.

addgroups: bool, optional
    It defaults to `False`.
    If it is `True`, the group itself is kept as part of the output list.

spaces: bool, optional
    It defaults to `False`.
    If it is `True`, Arch Spaces are added to the output list even
    when addgroups is False (their contents are always added).

noarchchild: bool, optional
    It defaults to `False`.
    If it is `True`, the objects inside Building and BuildingParts
    (Arch Workbench) aren't added to the output list.

exclude_names: list/tuple/set, optional
    It defaults to `None`.
    If an iterable of object names is given, any object whose `Name` is
    in this iterable will be excluded from the output list.

Returns
-------
list
    The list of objects from each group present in `objectslist`,
    plus any other individual object given in `objectslist`.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/groups.py:196`. Decorators are copied as source expressions and have not been executed.

## `draftutils.groups.getGroupContents`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getGroupContents(objectslist, walls=False, addgroups=False, spaces=False, noarchchild=False):
```

Return a list of objects from groups. DEPRECATED.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/groups.py:277`. Decorators are copied as source expressions and have not been executed.

## `draftutils.groups.get_movable_children`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_movable_children(objectslist, recursive=True, _donelist=[]):
```

Return a list of objects with child objects that move with a host.

Builds a list of objects with all child objects (`obj.OutList`)
that have their `MoveWithHost` attribute set to `True`.
This function is mostly useful for Arch Workbench objects.

Parameters
----------
objectslist: list of App::DocumentObject
    A single scripted object or list of objects.

recursive: bool, optional
    It defaults to `True`, in which case the function
    is called recursively to also extract the children of children
    objects.
    Otherwise, only direct children of the input objects
    are added to the output list.

_donelist: list
    List of object names. Used internally to prevent an endless loop.

Returns
-------
list
    List of children objects that have their `MoveWithHost` attribute
    set to `True`.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/groups.py:284`. Decorators are copied as source expressions and have not been executed.

## `draftutils.groups.getMovableChildren`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getMovableChildren(objectslist, recursive=True):
```

Return a list of objects with child objects. DEPRECATED.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/groups.py:356`. Decorators are copied as source expressions and have not been executed.

