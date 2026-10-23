# `FreeCAD.ExtensionContainer`

[Module](index.md)

```python
class ExtensionContainer(PropertyContainer):
```

Base class for all objects which can be extended
Author: Stefan Troeger (stefantroeger@gmx.net)
Licence: LGPL

Evidence: public stub `FreeCAD/__init__.pyi` line 2162. Inherited members are on the named base's reference; aliases keep their imported identity.

## `FreeCAD.ExtensionContainer.addExtension`

```python
def addExtension(self, identifier: str, proxy: object=None, /) -> None:
```

Adds an extension to the object. Requires the string identifier for the python extension as argument

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2169.

## `FreeCAD.ExtensionContainer.hasExtension`

```python
def hasExtension(self, identifier: str, derived: bool=True, /) -> bool:
```

Returns if this object has the specified extension

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2175.

