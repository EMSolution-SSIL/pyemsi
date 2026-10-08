# Python source module `femtools.femutils`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Fem/femtools/femutils.py`. Import path is source-routed; installed availability is unverified.

Collection of functions for the Fem module.

This module contains function for extracting relevant parts of geometry and
a few unrelated function useful at various places in the Fem module.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import os

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `femtools.femutils.os` -> `os`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Fem/femtools/femutils.py:37`.

### import subprocess

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `femtools.femutils.subprocess` -> `subprocess`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Fem/femtools/femutils.py:38`.

### from platform import system

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `femtools.femutils.system` -> `platform.system`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Fem/femtools/femutils.py:39`.

### import FreeCAD

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `femtools.femutils.FreeCAD` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Fem/femtools/femutils.py:41`.

### import FreeCADGui

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if FreeCAD.GuiUp`.

Bound source name `femtools.femutils.FreeCADGui` -> `FreeCADGui`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Fem/femtools/femutils.py:44`.

### from PySide import QtGui

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if FreeCAD.GuiUp`.

Bound source name `femtools.femutils.QtGui` -> `PySide.QtGui`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Fem/femtools/femutils.py:45`.

## `femtools.femutils.createObject`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def createObject(doc, name, proxy, viewProxy=None):
```

Add python object to document using python type string.

Add a document object suitable for the *proxy* and the *viewProxy* to *doc*
and attach it to the *proxy* and the *viewProxy*. This function can only be
used with python proxies that specify their C++ type via the BaseType class
member (e.g. Cube.BaseType). If there already exists a object with *name* a
suitable unique name is generated. To auto generate a name pass ``""``.

:param doc:         document object to which the object is added
:param name:        string of the name of new object in *doc*, use
                    ``""`` to generate a name
:param proxy:       python proxy for new object
:param viewProxy:   view proxy for new object

:returns:           reference to new object

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femtools/femutils.py:50`. Decorators are copied as source expressions and have not been executed.

## `femtools.femutils.type_of_obj`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def type_of_obj(obj):
```

Return type of *obj* honoring the special typesystem of Fem.

Python objects of the Fem workbench define their type via a class member
``<Class>.Type``. Return this type if the property exists. If not return
the conventional ``TypeId`` value.

:para obj: a document object

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femtools/femutils.py:75`. Decorators are copied as source expressions and have not been executed.

## `femtools.femutils.is_of_type`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def is_of_type(obj, ty):
```

Compare type of *obj* with *ty* honoring Fems typesystem.

See :py:func:`type_of_obj` for more info about the special typesystem of
the Fem module.

:returns:
 ``True`` if *obj* is of type *ty*, ``False`` otherwise. Type must match
 exactly: Derived objects are not considered to be of type of one of their
 super classes.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femtools/femutils.py:89`. Decorators are copied as source expressions and have not been executed.

## `femtools.femutils.is_derived_from`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def is_derived_from(obj, t):
```

Check if *obj* is derived from *t* honoring Fems typesystem.

Essentially just call ``obj.isDerivedFrom(t)`` and return it's value. For
objects using Fems typesystem (see :py:func:`type_of_obj`) return always
True if the Fem type is equal to *t*.

:note:
 Inheritance of Fem types is not checked. If *obj* uses Fems typesystem the
 type is just checked for equality. If the type doesn't match
 ``obj.isDerivedFrom`` is called as usual. See
 https://forum.freecad.org/viewtopic.php?f=10&t=32625

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femtools/femutils.py:103`. Decorators are copied as source expressions and have not been executed.

## `femtools.femutils.get_pref_working_dir`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_pref_working_dir(solver_obj):
```

Return working directory for solver honoring user settings.

:throws femtools.errors.MustSaveError:
 If user setting is set to BESIDE and the document isn't saved.

:note:
 Not working correctly for most cases because this circumvents directory
 caching of the solver framework. For solver use getMachine from run.py
 instead.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femtools/femutils.py:123`. Decorators are copied as source expressions and have not been executed.

## `femtools.femutils.get_temp_dir`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_temp_dir(obj=None):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femtools/femutils.py:151`. Decorators are copied as source expressions and have not been executed.

## `femtools.femutils.get_beside_dir`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_beside_dir(obj):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femtools/femutils.py:157`. Decorators are copied as source expressions and have not been executed.

## `femtools.femutils.get_custom_dir`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_custom_dir(obj):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femtools/femutils.py:165`. Decorators are copied as source expressions and have not been executed.

## `femtools.femutils.get_beside_base`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_beside_base(obj):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femtools/femutils.py:173`. Decorators are copied as source expressions and have not been executed.

## `femtools.femutils.get_custom_base`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_custom_base(solver):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femtools/femutils.py:192`. Decorators are copied as source expressions and have not been executed.

## `femtools.femutils.check_working_dir`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def check_working_dir(wdir):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femtools/femutils.py:209`. Decorators are copied as source expressions and have not been executed.

## `femtools.femutils.make_dir`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def make_dir(specific_path):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femtools/femutils.py:220`. Decorators are copied as source expressions and have not been executed.

## `femtools.femutils.getBoundBoxOfAllDocumentShapes`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getBoundBoxOfAllDocumentShapes(doc):
```

Calculate bounding box containing all objects inside *doc*.

:returns:
 A bounding box containing all objects that have a *Shape* attribute (all
 Part and PartDesign objects). If the document contains no such objects or
 no objects at all return ``None``.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femtools/femutils.py:238`. Decorators are copied as source expressions and have not been executed.

## `femtools.femutils.getSelectedFace`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getSelectedFace(selectionex):
```

Return selected face if exactly one face is selected.

:returns:
 The selected face as a ``Part::TopoShape`` if exactly one face is selected.
 Otherwise return ``None``.

:param selectionex:
 A list of selection object like the one Gui.Selection.getSelectionEx()
 returns.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femtools/femutils.py:285`. Decorators are copied as source expressions and have not been executed.

## `femtools.femutils.get_refshape_type`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_refshape_type(fem_doc_object):
```

Return shape type the constraints references.

Determine single shape type of references of *fem_doc_object* which must be
a constraint (=have a *References* property). All references must be of the
same type which is than returned as a string. A type can be "Vertex",
"Edge", "Face" or "Solid".

:param fem_doc_object:
 A constraint object with a *References* property.

:returns:
 A string representing the shape type ("Vertex", "Edge", "Face" or
 "Solid"). If *fem_doc_object* isn't a constraint ``""`` is returned.

:note:
 Undefined behaviour if the type of the references of one object are
 not all the same.

:note:
 Undefined behaviour if constraint contains no references (empty list).

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femtools/femutils.py:314`. Decorators are copied as source expressions and have not been executed.

## `femtools.femutils.pydecode`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def pydecode(bytestring):
```

Return *bytestring* as a unicode string

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femtools/femutils.py:353`. Decorators are copied as source expressions and have not been executed.

## `femtools.femutils.startProgramInfo`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def startProgramInfo(code):
```

starts a program under Windows minimized, hidden or normal

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femtools/femutils.py:358`. Decorators are copied as source expressions and have not been executed.

## `femtools.femutils.expandParentObject`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def expandParentObject():
```

expands parent and selected obj in tree view

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femtools/femutils.py:377`. Decorators are copied as source expressions and have not been executed.

## `femtools.femutils.getOutputWinColor`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getOutputWinColor(type):
```

type: 'Error', 'Warning', 'Logging', 'Text'

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femtools/femutils.py:388`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`femtools.femutils.__title__`, `femtools.femutils.__author__`, `femtools.femutils.__url__`. These are source internals unless an explicit export establishes otherwise.

