# `FreeCAD.LinkBaseExtension`

[Module](index.md)

```python
class LinkBaseExtension(DocumentObjectExtension):
```

Link extension base class
Author: Zheng, Lei (realthunder.dev@gmail.com)
Licence: LGPL

Evidence: public stub `FreeCAD/__init__.pyi` line 2343. Inherited members are on the named base's reference; aliases keep their imported identity.

## `FreeCAD.LinkBaseExtension.LinkedChildren`

```python
LinkedChildren: Final[List[Any]] = []
```

Return a flattened (in case grouped by plain group) list of linked children

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2349.

## `FreeCAD.LinkBaseExtension.configLinkProperty`

```python
def configLinkProperty(self, *args, **kwargs) -> Any:
```

Examples:
    Called with default names:
        configLinkProperty(prop1, prop2, ..., propN)
    Called with custom names:
        configLinkProperty(prop1=val1, prop2=val2, ..., propN=valN)

This method is here to implement what I called Property Design
Pattern. The extension operates on a predefined set of properties,
but it relies on the extended object to supply the actual property by
calling this method. You can choose a sub set of functionality of
this extension by supplying only some of the supported properties.

The 'key' are names used to refer to properties supported by this
extension, and 'val' is the actual name of the property of your
object. You can obtain the key names and expected types using
getLinkPropertyInfo().  You can use property of derived type when
calling configLinkProperty().  Other types will cause exception to
ben thrown. The actual properties supported may be different
depending on the actual extension object underlying this python
object.

If 'val' is omitted, i.e. calling configLinkProperty(key,...), then
it is assumed that the actual property name is the same as 'key'

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2352.

## `FreeCAD.LinkBaseExtension.getLinkExtProperty`

```python
def getLinkExtProperty(self, name: str, /) -> Any:
```

return the property value by its predefined name

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2380.

## `FreeCAD.LinkBaseExtension.getLinkExtPropertyName`

```python
def getLinkExtPropertyName(self, name: str, /) -> str:
```

lookup the property name by its predefined name

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2386.

## `FreeCAD.LinkBaseExtension.getLinkPropertyInfo`

```python
@overload
def getLinkPropertyInfo(self, /) -> tuple[tuple[str, str, str]]:

@overload
def getLinkPropertyInfo(self, index: int, /) -> tuple[str, str, str]:

@overload
def getLinkPropertyInfo(self, name: str, /) -> tuple[str, str]:

def getLinkPropertyInfo(self, arg: Any=None, /) -> tuple:
```

Overloads:
    (): return (name,type,doc) for all supported properties.
    (index): return (name,type,doc) of a specific property
    (name): return (type,doc) of a specific property

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2393, 2397, 2401, 2404.

## `FreeCAD.LinkBaseExtension.setLink`

```python
def setLink(self, obj: Any, subName: Optional[str]=None, subElements: Optional[Union[str, Tuple[str, ...]]]=None, /) -> None:
```

Called with only obj, set link object, otherwise set link element of a link group.

obj (DocumentObject): the object to link to. If this is None, then the link is cleared

subName (String): Dot separated object path.

subElements (String|tuple(String)): non-object sub-elements, e.g. Face1, Edge2.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2413.

## `FreeCAD.LinkBaseExtension.cacheChildLabel`

```python
def cacheChildLabel(self, enable: bool=True, /) -> None:
```

enable/disable child label cache

The cache is not updated on child label change for performance reason. You must
call this function on any child label change

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2425.

## `FreeCAD.LinkBaseExtension.flattenSubname`

```python
def flattenSubname(self, subname: str, /) -> str:
```

Return a flattened subname in case it references an object inside a linked plain group

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2434.

## `FreeCAD.LinkBaseExtension.expandSubname`

```python
def expandSubname(self, subname: str, /) -> str:
```

Return an expanded subname in case it references an object inside a linked plain group

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2440.

