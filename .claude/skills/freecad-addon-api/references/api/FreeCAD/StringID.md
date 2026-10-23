# `FreeCAD.StringID`

[Module](index.md)

```python
class StringID(BaseClass):
```

This is the StringID class

Author: Zheng, Lei (realthunder.dev@gmail.com)
Licence: LGPL

Evidence: public stub `FreeCAD/__init__.pyi` line 3084. Inherited members are on the named base's reference; aliases keep their imported identity.

## `FreeCAD.StringID.isSame`

```python
def isSame(self, other: 'StringID', /) -> bool:
```

Check if two StringIDs are the same

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 3092.

## `FreeCAD.StringID.Value`

```python
Value: Final[int] = 0
```

Return the integer value of this ID

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 3097.

## `FreeCAD.StringID.Related`

```python
Related: Final[List[Any]] = []
```

Return the related string IDs

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 3099.

## `FreeCAD.StringID.Data`

```python
Data: Final[str] = ''
```

Return the data associated with this ID

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 3101.

## `FreeCAD.StringID.IsBinary`

```python
IsBinary: Final[bool] = False
```

Check if the data is binary,

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 3103.

## `FreeCAD.StringID.IsHashed`

```python
IsHashed: Final[bool] = False
```

Check if the data is hash, if so 'Data' returns a base64 encoded string of the raw hash

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 3105.

## `FreeCAD.StringID.Index`

```python
Index: int = 0
```

Geometry index. Only meaningful for geometry element name

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 3107.

