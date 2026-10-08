# Python source module `draftutils.utils`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftutils/utils.py`. Import path is source-routed; installed availability is unverified.

Provides general utility functions used throughout the workbench.

This module contains auxiliary functions which can be used
in other modules of the workbench, and which don't require
the graphical user interface (GUI).

Literal `__all__`: not available; source names do not imply supported public API.

[part 1](index.md) | [part 2](index-2.md)

## Imports, aliases and conditional reexports

### import os

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftutils.utils.os` -> `os`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftutils/utils.py:41`.

### import PySide.QtCore as QtCore

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftutils.utils.QtCore` -> `PySide.QtCore`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftutils/utils.py:42`.

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftutils.utils.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftutils/utils.py:44`.

### from draftutils import params

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftutils.utils.params` -> `draftutils.params`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftutils/utils.py:45`.

### from draftutils.messages import _wrn, _err, _log

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftutils.utils._wrn` -> `draftutils.messages._wrn`.

Bound source name `draftutils.utils._err` -> `draftutils.messages._err`.

Bound source name `draftutils.utils._log` -> `draftutils.messages._log`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftutils/utils.py:46`.

### from draftutils.translate import translate

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftutils.utils.translate` -> `draftutils.translate.translate`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftutils/utils.py:47`.

### from builtins import open

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftutils.utils.open` -> `builtins.open`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftutils/utils.py:48`.

### import FreeCADGui as Gui

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if App.GuiUp`.

Bound source name `draftutils.utils.Gui` -> `FreeCADGui`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftutils/utils.py:54`.

### import Draft_rc

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if App.GuiUp`.

Bound source name `draftutils.utils.Draft_rc` -> `Draft_rc`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftutils/utils.py:55`.

## `draftutils.utils.ARROW_TYPES`

Status: source-defined name; no independently verified stability/export guarantee.

```python
ARROW_TYPES = ['Dot', 'Circle', 'Arrow', 'Tick', 'Tick-2', 'None']
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/Draft/draftutils/utils.py:61`. Decorators are copied as source expressions and have not been executed.

## `draftutils.utils.DISPLAY_MODES`

Status: source-defined name; no independently verified stability/export guarantee.

```python
DISPLAY_MODES = ['Flat Lines', 'Shaded', 'Wireframe', 'Points']
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/Draft/draftutils/utils.py:62`. Decorators are copied as source expressions and have not been executed.

## `draftutils.utils.DRAW_STYLES`

Status: source-defined name; no independently verified stability/export guarantee.

```python
DRAW_STYLES = ['Solid', 'Dashed', 'Dotted', 'Dashdot']
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/Draft/draftutils/utils.py:63`. Decorators are copied as source expressions and have not been executed.

## `draftutils.utils.arrowtypes`

Status: source-defined name; no independently verified stability/export guarantee.

```python
arrowtypes = ARROW_TYPES
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/Draft/draftutils/utils.py:64`. Decorators are copied as source expressions and have not been executed.

## `draftutils.utils.get_default_annotation_style`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_default_annotation_style():
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/utils.py:67`. Decorators are copied as source expressions and have not been executed.

## `draftutils.utils.repair_annotation_style`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def repair_annotation_style(style):
```

Repair a V0.19, V0.20 or < V1.1 style.

V0.19 and V0.20:
Some properties were missing or misspelled.
Some float values were wrongly stored as strings.

V1.0 -> V1.1:
ArrowSize has been replaced by ArrowSizeStart and ArrowSizeEnd.
ArrowType has been replaced by ArrowTypeStart and ArrowTypeEnd.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/utils.py:93`. Decorators are copied as source expressions and have not been executed.

## `draftutils.utils.get_default_shape_style`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_default_shape_style():
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/utils.py:126`. Decorators are copied as source expressions and have not been executed.

## `draftutils.utils.get_view_material`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_view_material():
```

Return a ShapeAppearance material with properties based on the preferences.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/utils.py:141`. Decorators are copied as source expressions and have not been executed.

## `draftutils.utils.string_encode_coin`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def string_encode_coin(ustr):
```

Encode a unicode object to be used as a string in coin.

Parameters
----------
ustr : str
    A string to be encoded

Returns
-------
str
    Encoded string. If the coin version is >= 4
    it will encode the string to `'utf-8'`, otherwise
    it will encode it to `'latin-1'`.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/utils.py:153`. Decorators are copied as source expressions and have not been executed.

## `draftutils.utils.stringencodecoin`

Status: source-defined name; no independently verified stability/export guarantee.

```python
stringencodecoin = string_encode_coin
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/Draft/draftutils/utils.py:180`. Decorators are copied as source expressions and have not been executed.

## `draftutils.utils.type_check`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def type_check(args_and_types, name='?'):
```

Check that the arguments are instances of certain types.

Parameters
----------
args_and_types : list
    A list of tuples. The first element of a tuple is tested as being
    an instance of the second element.
    ::
        args_and_types = [(a, Type), (b, Type2), ...]

    Then
    ::
        isinstance(a, Type)
        isinstance(b, Type2)

    A `Type` can also be a tuple of many types, in which case
    the check is done for any of them.
    ::
        args_and_types = [(a, (Type3, int, float)), ...]

        isinstance(a, (Type3, int, float))

name : str, optional
    Defaults to `'?'`. The name of the check.

Raises
------
TypeError
    If the first element in the tuple is not an instance of the second
    element, it raises `Draft.name`.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/utils.py:183`. Decorators are copied as source expressions and have not been executed.

## `draftutils.utils.typecheck`

Status: source-defined name; no independently verified stability/export guarantee.

```python
typecheck = type_check
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/Draft/draftutils/utils.py:222`. Decorators are copied as source expressions and have not been executed.

## `draftutils.utils.precision`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def precision():
```

Return the precision value from the parameter database.

It is the number of decimal places that a float will have.
Example
::
    precision=6, 0.123456
    precision=5, 0.12345
    precision=4, 0.1234

Due to floating point operations there may be rounding errors.
Therefore, this precision number is used to round up values
so that all operations are consistent.
By default the precision is 6 decimal places.

Returns
-------
int
    params.get_param("precision")

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/utils.py:225`. Decorators are copied as source expressions and have not been executed.

## `draftutils.utils.svg_precision`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def svg_precision():
```

Return the precision value for SVG import from the parameter database.

It is the number of decimal places that a float will have.
Example
::
    precision=5, 0.12345
    precision=4, 0.1234
    precision=3, 0.123

Due to floating point operations there may be rounding errors.
Therefore, this precision number is used to round up values
so that all operations are consistent.
By default the precision is 3 decimal places.

Returns
-------
int
    params.get_param("svgPrecision")

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/utils.py:248`. Decorators are copied as source expressions and have not been executed.

## `draftutils.utils.tolerance`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def tolerance():
```

Return a tolerance based on the precision() value

Returns
-------
float
    10 ** -precision()

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/utils.py:271`. Decorators are copied as source expressions and have not been executed.

## `draftutils.utils.is_deleted`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def is_deleted(obj):
```

Return `True` if obj is deleted.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/utils.py:282`. Decorators are copied as source expressions and have not been executed.

## `draftutils.utils.get_real_name`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_real_name(name):
```

Strip the trailing numbers from a string to get only the letters.

Parameters
----------
name : str
    A string that may have a number at the end, `Line001`.

Returns
-------
str
    A string without the numbers at the end, `Line`.
    The returned string cannot be empty; it will have
    at least one letter.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/utils.py:290`. Decorators are copied as source expressions and have not been executed.

## `draftutils.utils.getRealName`

Status: source-defined name; no independently verified stability/export guarantee.

```python
getRealName = get_real_name
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/Draft/draftutils/utils.py:311`. Decorators are copied as source expressions and have not been executed.

## `draftutils.utils.get_type`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_type(obj):
```

Return a string indicating the type of the given object.

Parameters
----------
obj : App::DocumentObject
    Any type of scripted object created with Draft,
    or any other workbench.

Returns
-------
str
    If `obj` has a `Proxy`, it will return the value of `obj.Proxy.Type`.

    * If `obj` is a `Part.Shape`, returns `'Shape'`

    * If `obj` has a `TypeId`, returns `obj.TypeId`

    In other cases, it will return `'Unknown'`,
    or `None` if `obj` is `None`.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/utils.py:314`. Decorators are copied as source expressions and have not been executed.

## `draftutils.utils.getType`

Status: source-defined name; no independently verified stability/export guarantee.

```python
getType = get_type
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/Draft/draftutils/utils.py:350`. Decorators are copied as source expressions and have not been executed.

## `draftutils.utils.get_trimex_unsupported_reason`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_trimex_unsupported_reason(obj, subobjects=None):
```

Return a translated Trimex error message for unsupported objects.

Parameters
----------
obj : App::DocumentObject
    Object that Trimex should operate on.
subobjects : list, optional
    Retained for compatibility.

Returns
-------
str or None
    `None` if the object is supported by Trimex, otherwise
    a translated error message explaining why it is rejected.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/utils.py:353`. Decorators are copied as source expressions and have not been executed.

## `draftutils.utils.get_objects_of_type`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_objects_of_type(objects, typ):
```

Return only the objects that match the type in the list of objects.

Parameters
----------
objects : list of App::DocumentObject
    A list of objects which will be tested.

typ : str
    A string that indicates a type. This should be one of the types
    that can be returned by `get_type`.

Returns
-------
list of objects
    Only the objects that match `typ` will be added to the output list.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/utils.py:417`. Decorators are copied as source expressions and have not been executed.

## `draftutils.utils.getObjectsOfType`

Status: source-defined name; no independently verified stability/export guarantee.

```python
getObjectsOfType = get_objects_of_type
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/Draft/draftutils/utils.py:441`. Decorators are copied as source expressions and have not been executed.

## `draftutils.utils.is_clone`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def is_clone(obj, objtype=None, recursive=False):
```

Return True if the given object is a clone of a certain type.

A clone is of type `'Clone'`, and has a reference
to the original object inside its `Objects` attribute,
which is an `'App::PropertyLinkListGlobal'`.

The `Objects` attribute can point to another `'Clone'` object.
If `recursive` is `True`, the function will be called recursively
to further test this clone, until the type of the original object
can be compared to `objtype`.

Parameters
----------
obj : App::DocumentObject
    The clone object that will be tested for a certain type.

objtype : str or list of str
    A type string such as one obtained from `get_type`.
    Or a list of such types.

recursive : bool, optional
    It defaults to `False`.
    If it is `True`, this same function will be called recursively
    with `obj.Object[0]` as input.

    This option only works if `obj.Object[0]` is of type `'Clone'`,
    that is, if `obj` is a clone of a clone.

Returns
-------
bool
    Returns `True` if `obj` is of type `'Clone'`,
    and `obj.Object[0]` is of type `objtype`.

    If `objtype` is a list, then `obj.Objects[0]`
    will be tested against each of the elements in the list,
    and it will return `True` if at least one element matches the type.

    If `obj` isn't of type `'Clone'` but has the `CloneOf` attribute,
    it will also return `True`.

    It returns `False` otherwise, for example,
    if `obj` is not even a clone.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/utils.py:444`. Decorators are copied as source expressions and have not been executed.

## `draftutils.utils.isClone`

Status: source-defined name; no independently verified stability/export guarantee.

```python
isClone = is_clone
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/Draft/draftutils/utils.py:508`. Decorators are copied as source expressions and have not been executed.

## `draftutils.utils.get_clone_base`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_clone_base(obj, strict=False, recursive=True):
```

Return the object cloned by this object, if any.

Parameters
----------
obj: App::DocumentObject
    Any type of object.

strict: bool, optional
    It defaults to `False`.
    If it is `True`, and this object is not a clone,
    this function will return `False`.

recursive: bool, optional
    It defaults to `True`
    If it is `True`, it call recursively to itself to
    get base object and if it is `False` then it just
    return base object, not call recursively to find
    base object.

Returns
-------
App::DocumentObject
    It `obj` is a `Draft Clone`, it will return the first object
    that is in its `Objects` property.

    If `obj` has a `CloneOf` property, it will search iteratively
    inside the object pointed to by this property.

obj
    If `obj` is not a `Draft Clone`, nor it has a `CloneOf` property,
    it will return the same `obj`, as long as `strict` is `False`.

False
    It will return `False` if `obj` is not a clone,
    and `strict` is `True`.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/utils.py:511`. Decorators are copied as source expressions and have not been executed.

## `draftutils.utils.getCloneBase`

Status: source-defined name; no independently verified stability/export guarantee.

```python
getCloneBase = get_clone_base
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/Draft/draftutils/utils.py:561`. Decorators are copied as source expressions and have not been executed.

## `draftutils.utils.shapify`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def shapify(obj, delete=True):
```

Transform a parametric object into a static, non-parametric shape.

Parameters
----------
obj : App::DocumentObject
    Any type of scripted object.

    This object will be removed, and a non-parametric object
    with the same topological shape (`Part::TopoShape`)
    will be created.

delete: bool, optional
    It defaults to `False`.
    If it is `True`, the original object is deleted.

Returns
-------
Part::Feature
    The new object that takes `obj.Shape` as its own.

    Depending on the contents of the Shape, the resulting object
    will be named `'Face'`, `'Solid'`, `'Compound'`,
    `'Shell'`, `'Wire'`, `'Line'`, `'Circle'`,
    or the name returned by `get_real_name(obj.Name)`.

    If there is a problem with `obj.Shape`, it will return `None`,
    and the original object will not be modified.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/utils.py:564`. Decorators are copied as source expressions and have not been executed.

## `draftutils.utils.print_shape`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def print_shape(shape):
```

Print detailed information of a topological shape.

Parameters
----------
shape : Part::TopoShape
    Any topological shape in an object, usually obtained from `obj.Shape`.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/utils.py:621`. Decorators are copied as source expressions and have not been executed.

## `draftutils.utils.printShape`

Status: source-defined name; no independently verified stability/export guarantee.

```python
printShape = print_shape
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/Draft/draftutils/utils.py:650`. Decorators are copied as source expressions and have not been executed.

