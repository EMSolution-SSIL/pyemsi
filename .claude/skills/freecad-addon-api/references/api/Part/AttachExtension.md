# `Part.AttachExtension`

[Module](index.md)

```python
class AttachExtension(DocumentObjectExtension):
```

This object represents an attachable object with OCC shape.

Author: DeepSOIC (vv.titov@gmail.com)
Licence: LGPL

Evidence: public stub `Part/__init__.pyi` line 499. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.AttachExtension.Attacher`

```python
Attacher: Final[Any] = ...
```

AttachEngine object driving this AttachableObject. Returns a copy.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Part/__init__.pyi` line(s) 506.

## `Part.AttachExtension.positionBySupport`

```python
def positionBySupport(self) -> bool:
```

positionBySupport() -> bool

Reposition object based on AttachmentSupport, MapMode and MapPathParameter properties.
Returns True if attachment calculation was successful, false if object is not attached and Placement wasn't updated,
and raises an exception if attachment calculation fails.

Evidence: public stub `Part/__init__.pyi` line(s) 509.

## `Part.AttachExtension.changeAttacherType`

```python
def changeAttacherType(self, typename: str, /) -> bool:
```

changeAttacherType(typename) -> None

Changes Attacher class of this object.
typename: string. The following are accepted so far:
'Attacher::AttachEngine3D'
'Attacher::AttachEnginePlane'
'Attacher::AttachEngineLine'
'Attacher::AttachEnginePoint'

Evidence: public stub `Part/__init__.pyi` line(s) 519.

