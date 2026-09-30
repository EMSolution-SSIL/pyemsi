# `FreeCAD.StringHasher`

[Module](index.md)

```python
class StringHasher(BaseClass):
```

This is the StringHasher class

Author: Zheng, Lei (realthunder.dev@gmail.com)
Licence: LGPL

Evidence: public stub `FreeCAD/__init__.pyi` line 3040. Inherited members are on the named base's reference; aliases keep their imported identity.

## `FreeCAD.StringHasher.getID`

```python
@overload
def getID(self, txt: str, base64: bool=False, /) -> StringID | None:

@overload
def getID(self, id: int, index: int=0, /) -> StringID | None:

def getID(self, arg: Any, base64: bool=False, /) -> StringID | None:
```

If the input is text, return a StringID object that is unique within this hasher. This
StringID object is reference counted. The hasher may only save hash ID's that are used.

If the input is an integer, then the hasher will try to find the StringID object stored
with the same integer value.

base64: indicate if the input 'txt' is base64 encoded binary data

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 3049, 3053, 3056.

## `FreeCAD.StringHasher.isSame`

```python
def isSame(self, other: 'StringHasher', /) -> bool:
```

Check if two hasher are the same

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 3068.

## `FreeCAD.StringHasher.Count`

```python
Count: Final[int] = 0
```

Return count of used hashes

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 3073.

## `FreeCAD.StringHasher.Size`

```python
Size: Final[int] = 0
```

Return the size of the hashes

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 3075.

## `FreeCAD.StringHasher.SaveAll`

```python
SaveAll: bool = False
```

Whether to save all string hashes regardless of its use count

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 3077.

## `FreeCAD.StringHasher.Threshold`

```python
Threshold: int = 0
```

Data length exceed this threshold will be hashed before storing

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 3079.

## `FreeCAD.StringHasher.Table`

```python
Table: Final[Dict[int, str]] = {}
```

Return the entire string table as Int->String dictionary

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 3081.

