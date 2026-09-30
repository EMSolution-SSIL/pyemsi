# `FreeCAD.Base.TypeId`

[Module](index.md)

```python
class TypeId:
```

BaseTypePy class.

This class provides functionality related to type management in the Base module. It's not intended for direct instantiation but for accessing type information and creating instances of various types. Instantiation is possible for classes that inherit from the Base::BaseClass class and are not abstract.

Author: Juergen Riegel (FreeCAD@juergen-riegel.net)
Licence: LGPL

Evidence: public stub `FreeCAD/Base.pyi` line 1596. Inherited members are on the named base's reference; aliases keep their imported identity.

## `FreeCAD.Base.TypeId.Name`

```python
Name: Final[str] = ''
```

The name of the type id.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1605.

## `FreeCAD.Base.TypeId.Key`

```python
Key: Final[int] = 0
```

The key of the type id.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1607.

## `FreeCAD.Base.TypeId.Module`

```python
Module: Final[str] = ''
```

Module in which this class is defined.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1609.

## `FreeCAD.Base.TypeId.fromName`

```python
@staticmethod
def fromName(name: str, /) -> 'Type':
```

Returns a type object by name.

name : str

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1613.

## `FreeCAD.Base.TypeId.fromKey`

```python
@staticmethod
def fromKey(key: int, /) -> 'Type':
```

Returns a type id object by key.

key : int

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1622.

## `FreeCAD.Base.TypeId.getNumTypes`

```python
@staticmethod
def getNumTypes() -> int:
```

Returns the number of type ids created so far.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1631.

## `FreeCAD.Base.TypeId.getBadType`

```python
@staticmethod
def getBadType() -> 'Type':
```

Returns an invalid type id.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1638.

## `FreeCAD.Base.TypeId.getAllDerivedFrom`

```python
@staticmethod
def getAllDerivedFrom(type: str | 'Type', /) -> List['Type']:
```

Returns all descendants from the given type id.

type : str, Base.BaseType

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1645.

## `FreeCAD.Base.TypeId.getParent`

```python
def getParent(self) -> 'Type':
```

Returns the parent type id.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1653.

## `FreeCAD.Base.TypeId.isBad`

```python
def isBad(self) -> bool:
```

Checks if the type id is invalid.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1659.

## `FreeCAD.Base.TypeId.isDerivedFrom`

```python
def isDerivedFrom(self, type: str | 'Type', /) -> bool:
```

Returns true if given type id is a father of this type id.

type : str, Base.BaseType

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1665.

## `FreeCAD.Base.TypeId.getAllDerived`

```python
def getAllDerived(self) -> List[object]:
```

Returns all descendants from this type id.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1673.

## `FreeCAD.Base.TypeId.createInstance`

```python
def createInstance(self) -> object:
```

Creates an instance of this type id.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1679.

## `FreeCAD.Base.TypeId.createInstanceByName`

```python
@staticmethod
def createInstanceByName(name: str, load: bool=False, /) -> object | None:
```

Creates an instance of the named type id.

name : str
load : bool
    Load named type id module.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1686.

