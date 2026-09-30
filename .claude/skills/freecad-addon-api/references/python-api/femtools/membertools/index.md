# Python source module `femtools.membertools`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Fem/femtools/membertools.py`. Import path is source-routed; installed availability is unverified.

Collection of functions for the Fem module.

This module contains function for managing a analysis and all the different
types of objects it contains, helper for executing a simulation.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### from FreeCAD import Base

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `femtools.membertools.Base` -> `FreeCAD.Base`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Fem/femtools/membertools.py:37`.

### from . import femutils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `femtools.membertools.femutils` -> `femtools.femutils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Fem/femtools/membertools.py:38`.

## Classes

- [femtools.membertools.AnalysisMember](AnalysisMember.md)

## `femtools.membertools.get_member`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_member(analysis, t):
```

Return list of all members of *analysis* of type *t*.

Search *analysis* for members of type *t*. This method checks the custom
python typesystem (BaseType class property) used by the Fem module if
possible. If the object does not use the python typesystem the usual
isDerivedFrom from the C++ dynamic type system is used.

:param analysis: only objects part of this analysis are considered
:param t:        only objects of this type are returned

:note:
 Inheritance of Fem types is not checked. If *obj* uses Fems typesystem the
 type is just checked for equality. If the type doesn't match
 ``obj.isDerivedFrom`` is called as usual. See
 https://forum.freecad.org/viewtopic.php?f=10&t=32625

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femtools/membertools.py:41`. Decorators are copied as source expressions and have not been executed.

## `femtools.membertools.get_single_member`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_single_member(analysis, t):
```

Return one object of type *t* and part of *analysis*.

Search *analysis* for members of type *t* and return the first one that's
found. This method checks the custom python typesystem (BaseType class
property) used by the Fem module if possible. If the object doesn't use the
python typesystem the usual isDerivedFrom from the C++ dynamic type system
is used.

:param analysis: only objects part of this analysis are considered
:param t:        only a object of this type is returned

:note:
 Inheritance of Fem types is not checked. If *obj* uses Fems typesystem the
 type is just checked for equality. If the type doesn't match
 ``obj.isDerivedFrom`` is called as usual. See
 https://forum.freecad.org/viewtopic.php?f=10&t=32625

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femtools/membertools.py:71`. Decorators are copied as source expressions and have not been executed.

## `femtools.membertools.get_several_member`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_several_member(analysis, t):
```

Get members and pack them for Calculix/Z88.

Collect members by calling :py:func:`get_member` and pack them into a
data structure that can be consumed by calculix and Z88 solver modules.

:param analysis: see :py:func:`get_member`
:param t: see :py:func:`get_member`

:returns:
 A list containing one dict per member. Each dict has two entries:
 ``"Object"`` and ``"RefShapeType"``. ``dict["Object"]`` contains the
 member document object. ``dict["RefShapeType"]`` contains the shape type
 of the *References* property of the member (used by constraints) as a
 string ("Vertex", "Edge", "Face" or "Solid"). If the member doesn't have a
 *References* property ``dict["RefShapeType"]`` is the empty string ``""``.

:note:
 Undefined behaviour if one of the members has a *References* property
 which is empty.

:note:
 Undefined behaviour if the type of the references of one object are not
 all the same.

:note:
 Inheritance of Fem types is not checked. If *obj* uses Fems typesystem the
 type is just checked for equality. If the type doesn't match
 ``obj.isDerivedFrom`` is called as usual. See
 https://forum.freecad.org/viewtopic.php?f=10&t=32625

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femtools/membertools.py:93`. Decorators are copied as source expressions and have not been executed.

## `femtools.membertools.get_mesh_to_solve`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_mesh_to_solve(analysis):
```

Find one and only mesh object of *analysis*.

:returns:
 A tuple ``(object, message)``. If and only if the analysis contains
 exactly one mesh object the first value of the tuple is the mesh document
 object. Otherwise the first value is ``None`` and the second value is a
 error message indicating what went wrong.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femtools/membertools.py:135`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`femtools.membertools.__title__`, `femtools.membertools.__author__`, `femtools.membertools.__url__`. These are source internals unless an explicit export establishes otherwise.

