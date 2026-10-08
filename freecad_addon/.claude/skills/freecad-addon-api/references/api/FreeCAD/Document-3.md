# `FreeCAD.Document`

[Module](index.md)

```python
class Document(PropertyContainer):
```

This is the Document class.

Evidence: public stub `FreeCAD/__init__.pyi` line 945. Inherited members are on the named base's reference; aliases keep their imported identity.

[part 1](Document.md) | [part 2](Document-2.md) | [part 3](Document-3.md)

## `FreeCAD.Document.undo`

```python
def undo(self) -> None:
```

Undo one transaction

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1591.

## `FreeCAD.Document.redo`

```python
def redo(self) -> None:
```

Redo a previously undone transaction

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1597.

## `FreeCAD.Document.clearUndos`

```python
def clearUndos(self) -> None:
```

Clear the undo stack of the document

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1603.

## `FreeCAD.Document.clearDocument`

```python
def clearDocument(self) -> None:
```

Clear the whole document

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1609.

## `FreeCAD.Document.setClosable`

```python
def setClosable(self, closable: bool, /) -> None:
```

Set a flag that allows or forbids to close a document

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1615.

## `FreeCAD.Document.isClosable`

```python
def isClosable(self) -> bool:
```

Check if the document can be closed. The default value is True

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1621.

## `FreeCAD.Document.setAutoCreated`

```python
def setAutoCreated(self, autoCreated: bool, /) -> None:
```

Set a flag that indicates if a document is autoCreated

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1627.

## `FreeCAD.Document.isAutoCreated`

```python
def isAutoCreated(self) -> bool:
```

Check if the document is autoCreated. The default value is False

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1633.

## `FreeCAD.Document.recompute`

```python
def recompute(self, objs: Sequence[DocumentObject]=None, force: bool=False, check_cycle: bool=False, /) -> int:
```

Recompute the document and returns the amount of recomputed features.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1639.

## `FreeCAD.Document.mustExecute`

```python
def mustExecute(self) -> bool:
```

Check if any object must be recomputed

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1645.

## `FreeCAD.Document.purgeTouched`

```python
def purgeTouched(self) -> None:
```

Purge the touched state of all objects

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1651.

## `FreeCAD.Document.isTouched`

```python
def isTouched(self) -> bool:
```

Check if any object is in touched state

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1657.

## `FreeCAD.Document.getObject`

```python
def getObject(self, name: str | int, /) -> DocumentObject | None:
```

Return the object with the given name or ID, or None if it does not exist.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1663.

## `FreeCAD.Document.getObjectsByLabel`

```python
def getObjectsByLabel(self, label: str, /) -> list[DocumentObject]:
```

Return the objects with the given label name.

NOTE: It's possible that several objects have the same label name.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1669.

## `FreeCAD.Document.findObjects`

```python
def findObjects(self, Type: str=..., Name: str=..., Label: str=...) -> list[DocumentObject]:
```

Return a list of objects that match the specified type, name or label.

Name and label support regular expressions. All parameters are optional.

Args:
    Type: Type of the feature.
    Name: Name
    Label: Label

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1677.

## `FreeCAD.Document.getLinksTo`

```python
def getLinksTo(self, obj: DocumentObject | None=None, options: int=0, maxCount: int=0, /) -> tuple[DocumentObject, ...]:
```

Return objects linked to 'obj'

Args:
    options: 1: recursive, 2: check link array. Options can combine.
    maxCount: to limit the number of links returned.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1690.

## `FreeCAD.Document.supportedTypes`

```python
def supportedTypes(self) -> list[str]:
```

A list of supported types of objects

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1700.

## `FreeCAD.Document.getTempFileName`

```python
def getTempFileName(self, name: str, /) -> str:
```

Returns a unique file name, based on the given name, with a path in the temp directory of
the document.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1706.

## `FreeCAD.Document.getDependentDocuments`

```python
def getDependentDocuments(self, sort: bool=True, /) -> list[Document]:
```

Returns a list of documents that this document directly or indirectly links to including itself.

Args:
    sort: whether to topologically sort the return list

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1713.

## `FreeCAD.Document.getBookedTransactionID`

```python
def getBookedTransactionID(self) -> int:
```

getBookedTransactionID() -> int

Returns the currently booked transaction id, which is the id of the current transaction OR the id
the next transaction will stick to if no change has occurred yet

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1722.

