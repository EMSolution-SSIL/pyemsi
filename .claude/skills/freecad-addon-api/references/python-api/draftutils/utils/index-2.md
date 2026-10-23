# Python source module `draftutils.utils`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftutils/utils.py`. Import path is source-routed; installed availability is unverified.

Provides general utility functions used throughout the workbench.

This module contains auxiliary functions which can be used
in other modules of the workbench, and which don't require
the graphical user interface (GUI).

Literal `__all__`: not available; source names do not imply supported public API.

[part 1](index.md) | [part 2](index-2.md)

## `draftutils.utils.compare_objects`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def compare_objects(obj1, obj2):
```

Print the differences between 2 objects.

The two objects are compared through their `TypeId` attribute,
or by using the `get_type` function.

If they are the same type their properties are compared
looking for differences.

Neither `Shape` nor `Label` attributes are compared.

Parameters
----------
obj1 : App::DocumentObject
    Any type of scripted object.
obj2 : App::DocumentObject
    Any type of scripted object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/utils.py:653`. Decorators are copied as source expressions and have not been executed.

## `draftutils.utils.compareObjects`

Status: source-defined name; no independently verified stability/export guarantee.

```python
compareObjects = compare_objects
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/Draft/draftutils/utils.py:705`. Decorators are copied as source expressions and have not been executed.

## `draftutils.utils.load_svg_patterns`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def load_svg_patterns():
```

Load the default Draft SVG patterns and user defined patterns.

The SVG patterns are added as a dictionary to the `App.svgpatterns`
attribute.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/utils.py:708`. Decorators are copied as source expressions and have not been executed.

## `draftutils.utils.loadSvgPatterns`

Status: source-defined name; no independently verified stability/export guarantee.

```python
loadSvgPatterns = load_svg_patterns
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/Draft/draftutils/utils.py:758`. Decorators are copied as source expressions and have not been executed.

## `draftutils.utils.svg_patterns`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def svg_patterns():
```

Return a dictionary with installed SVG patterns.

Returns
-------
dict
    Returns `App.svgpatterns` if it exists.
    Otherwise it calls `load_svg_patterns` to create it
    before returning it.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/utils.py:761`. Decorators are copied as source expressions and have not been executed.

## `draftutils.utils.svgpatterns`

Status: source-defined name; no independently verified stability/export guarantee.

```python
svgpatterns = svg_patterns
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/Draft/draftutils/utils.py:780`. Decorators are copied as source expressions and have not been executed.

## `draftutils.utils.get_rgb`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_rgb(color, testbw=True):
```

Return an RRGGBB value #000000 from a FreeCAD color.

Parameters
----------
color : list or tuple with RGB values
    The values must be in the 0.0-1.0 range.
testbw : bool (default = True)
    Pure white will be converted into pure black.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/utils.py:783`. Decorators are copied as source expressions and have not been executed.

## `draftutils.utils.getrgb`

Status: source-defined name; no independently verified stability/export guarantee.

```python
getrgb = get_rgb
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/Draft/draftutils/utils.py:805`. Decorators are copied as source expressions and have not been executed.

## `draftutils.utils.argb_to_rgba`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def argb_to_rgba(color):
```

Change byte order of a 4 byte color int from ARGB (Qt) to RGBA (FreeCAD).

Alpha in both integers should always be 255.

Alpha in color properties is not used in the 3D view, but is shown in the
color swatches in the Property editor. It therefore better to ensure alpha
is 255 (version 1.1 dev cycle).

Usage:

    qt_int = self.form.ShapeColor.property("color").rgba() # Note: returns ARGB int
    qt_int = self.form.ShapeColor.property("color").rgb()  # Note: returns ARGB int
    fc_int = argb_to_rgba(qt_int)

    FreeCAD.ParamGet("User parameter:BaseApp/Preferences/View")            .SetUnsigned("DefaultShapeColor", fc_int)

    obj.ViewObject.ShapeColor = fc_int | 0x000000FF

Related:

    getRgbF() returns an RGBA tuple. 4 floats in the range 0.0 - 1.0. Alpha is always 1.0.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/utils.py:808`. Decorators are copied as source expressions and have not been executed.

## `draftutils.utils.rgba_to_argb`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def rgba_to_argb(color):
```

Change byte order of a 4 byte color int from RGBA (FreeCAD) to ARGB (Qt).

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/utils.py:835`. Decorators are copied as source expressions and have not been executed.

## `draftutils.utils.get_rgba_tuple`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_rgba_tuple(color, typ=1.0):
```

Return an RGBA tuple.

Parameters
----------
color: int
    RGBA integer.
typ: any float (default = 1.0) or int (use 255)
    If float the values in the returned tuple are in the 0.0-1.0 range.
    Else the values are in the 0-255 range.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/utils.py:840`. Decorators are copied as source expressions and have not been executed.

## `draftutils.utils.is_closed_edge`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def is_closed_edge(edge_index, object):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/utils.py:968`. Decorators are copied as source expressions and have not been executed.

## `draftutils.utils.utf8_decode`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def utf8_decode(text):
```

Decode the input string and return a unicode string.

Python 2:
::
    str -> unicode
    unicode -> unicode

Python 3:
::
    str -> str
    bytes -> str

It runs
::
    try:
        return text.decode("utf-8")
    except AttributeError:
        return text

Parameters
----------
text : str, unicode or bytes
    A str, unicode, or bytes object that may have unicode characters
    like accented characters.

    In Python 2, a `bytes` object can include accented characters,
    but in Python 3 it must only contain ASCII literal characters.

Returns
-------
unicode or str
    In Python 2 it will try decoding the `bytes` string
    and return a `'utf-8'` decoded string.

    >>> "Aá".decode("utf-8")
    >>> b"Aá".decode("utf-8")
    u'A\xe1'

    In Python 2 the unicode string is prefixed with `u`,
    and unicode characters are replaced by their two-digit hexadecimal
    representation, or four digit unicode escape.

    >>> "AáBẃCñ".decode("utf-8")
    u'A\xe1B\u1e83C\xf1'

    In Python 2 it will always return a `unicode` object.

    In Python 3 a regular string is already unicode encoded,
    so strings have no `decode` method. In this case, `text`
    will be returned as is.

    In Python 3, if `text` is a `bytes` object, then it will be converted
    to `str`; in this case, the `bytes` object cannot have accents,
    it must only contain ASCII literal characters.

    >>> b"ABC".decode("utf-8")
    'ABC'

    In Python 3 it will always return a `str` object, with no prefix.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/utils.py:972`. Decorators are copied as source expressions and have not been executed.

## `draftutils.utils.print_header`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def print_header(name, description, debug=True):
```

Print a line to the console when something is called, and log it.

Parameters
----------
name: str
    The name of the function or class that is being called.
    This `name` will be logged in the log file, so if there are problems
    the log file can be investigated for clues.

description: str
    Arbitrary text that will be printed to the console
    when the function or class is called.

debug: bool, optional
    It defaults to `True`.
    If it is `False` the `description` will not be printed
    to the console.
    On the other hand the `name` will always be logged.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/utils.py:1039`. Decorators are copied as source expressions and have not been executed.

## `draftutils.utils.find_doc`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def find_doc(doc=None):
```

Return the active document or find a document by name.

Parameters
----------
doc: App::Document or str, optional
    The document that will be searched in the session.
    It defaults to `None`, in which case it tries to find
    the active document.
    If `doc` is a string, it will try to get the document by `Name`.

Returns
-------
bool, App::Document
    A tuple containing the information on whether the search
    was successful. In this case, the boolean is `True`,
    and the second value is the document instance.

False, None
    If there is no active document, or the string in `doc`
    doesn't correspond to an open document in the session.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/utils.py:1065`. Decorators are copied as source expressions and have not been executed.

## `draftutils.utils.find_object`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def find_object(obj, doc=None):
```

Find object in the document, inclusive by Label.

Parameters
----------
obj: App::DocumentObject or str
    The object to search in `doc`.
    Or if the `obj` is a string, it will search the object by `Label`.
    Since Labels are not guaranteed to be unique, it will get the first
    object with that label in the document.

doc: App::Document or str, optional
    The document in which the object will be searched.
    It defaults to `None`, in which case it tries to search in the
    active document.
    If `doc` is a string, it will search the document by `Name`.

Returns
-------
bool, App::DocumentObject
    A tuple containing the information on whether the search
    was successful. In this case, the boolean is `True`,
    and the second value is the object found.

False, None
    If the object doesn't exist in the document.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/utils.py:1104`. Decorators are copied as source expressions and have not been executed.

## `draftutils.utils.use_instead`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def use_instead(function, version=''):
```

Print a deprecation message and suggest another function.

This function must be used inside the definition of a function
that has been considered for deprecation, so we must provide
an alternative.
::
    def old_function():
        use_instead('new_function', 1.0)

    def someFunction():
        use_instead('some_function')

Parameters
----------
function: str
    The name of the function to use instead of the current one.

version: float or str, optional
    It defaults to the empty string `''`.
    The version where this command is to be deprecated, if it is known.
    If we don't know when this command will be deprecated
    then we should not give a version.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/utils.py:1150`. Decorators are copied as source expressions and have not been executed.

## `draftutils.utils.pyopen`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def pyopen(file, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True, opener=None):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/utils.py:1188`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`draftutils.utils._modifiers_process_subselection`, `draftutils.utils._modifiers_process_selection`, `draftutils.utils._modifiers_get_group_contents`, `draftutils.utils._modifiers_get_movable_children`, `draftutils.utils._modifiers_filter_objects`. These are source internals unless an explicit export establishes otherwise.

