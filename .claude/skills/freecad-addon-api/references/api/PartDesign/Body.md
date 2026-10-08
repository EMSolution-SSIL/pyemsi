# `PartDesign.Body`

[Module](index.md)

```python
class Body(BodyBase):
```

PartDesign body class

Author: Juergen Riegel (FreeCAD@juergen-riegel.net)
Licence: LGPL

Evidence: public stub `PartDesign/__init__.pyi` line 12. Inherited members are on the named base's reference; aliases keep their imported identity.

## `PartDesign.Body.VisibleFeature`

```python
VisibleFeature: Final[object] = ...
```

Return the visible feature of this body

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `PartDesign/__init__.pyi` line(s) 19.

## `PartDesign.Body.AllowCompound`

```python
@property
def AllowCompound(self) -> bool:

@AllowCompound.setter
def AllowCompound(self, value: bool | int) -> None:
```

Allow multiple solids in Body

Access: getter and setter declared in the stub.

Evidence: public stub `PartDesign/__init__.pyi` line(s) 23, 28.

## `PartDesign.Body.insertObject`

```python
def insertObject(self, feature: object, target: object, after: bool=False, /) -> None:
```

Insert the feature into the body after the given feature.

@param feature  The feature to insert into the body
@param target   The feature relative which one should be inserted the given.
  If target is NULL than insert into the end if where is InsertBefore
  and into the begin if where is InsertAfter.
@param after    if true insert the feature after the target. Default is false.

@note the method doesn't modify the Tip unlike addObject()

Evidence: public stub `PartDesign/__init__.pyi` line(s) 31.

