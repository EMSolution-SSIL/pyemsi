# `FreeCAD.Base.Persistence`

[Module](index.md)

```python
class Persistence(BaseClass):
```

Base.Persistence class.

Class to dump and restore the content of an object.

Author: Juergen Riegel (FreeCAD@juergen-riegel.net)
Licence: LGPL

Evidence: public stub `FreeCAD/Base.pyi` line 874. Inherited members are on the named base's reference; aliases keep their imported identity.

## `FreeCAD.Base.Persistence.Content`

```python
Content: Final[str] = ''
```

Content of the object in XML representation.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 883.

## `FreeCAD.Base.Persistence.MemSize`

```python
MemSize: Final[int] = 0
```

Memory size of the object in bytes.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 885.

## `FreeCAD.Base.Persistence.dumpContent`

```python
def dumpContent(self, Compression: int=3) -> bytearray:
```

Dumps the content of the object, both the XML representation and the additional
data files required, into a byte representation.

Compression : int
    Set the data compression level in the range [0,9]. Set to 0 for no compression.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 888.

## `FreeCAD.Base.Persistence.restoreContent`

```python
def restoreContent(self, obj: object, /) -> None:
```

Restore the content of the object from a byte representation as stored by `dumpContent`.
It could be restored from any Python object implementing the buffer protocol.

obj : buffer
    Object with buffer protocol support.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 898.

