# `FreeCAD.Base.BaseClass`

[Module](index.md)

```python
class BaseClass:
```

This is the base class

Author: Juergen Riegel (FreeCAD@juergen-riegel.net)
Licence: LGPL

Evidence: public stub `FreeCAD/Base.pyi` line 92. Inherited members are on the named base's reference; aliases keep their imported identity.

## `FreeCAD.Base.BaseClass.TypeId`

```python
TypeId: Final[str] = ''
```

Is the type of the FreeCAD object with module domain

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 99.

## `FreeCAD.Base.BaseClass.Module`

```python
Module: Final[str] = ''
```

Module in which this class is defined

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 101.

## `FreeCAD.Base.BaseClass.isDerivedFrom`

```python
def isDerivedFrom(self, typeName: str, /) -> bool:
```

Returns true if given type is a father

Evidence: public stub `FreeCAD/Base.pyi` line(s) 104.

## `FreeCAD.Base.BaseClass.getAllDerivedFrom`

```python
def getAllDerivedFrom(self) -> List[object]:
```

Returns all descendants

Evidence: public stub `FreeCAD/Base.pyi` line(s) 110.

