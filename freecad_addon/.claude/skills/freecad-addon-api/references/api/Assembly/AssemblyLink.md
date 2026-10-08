# `Assembly.AssemblyLink`

[Module](index.md)

```python
class AssemblyLink(Part):
```

This class handles document objects in Assembly

Author: Ondsel (development@ondsel.com)
License: LGPL-2.1-or-later

Evidence: public stub `Assembly/__init__.pyi` line 13. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Assembly.AssemblyLink.Joints`

```python
Joints: Final[list]
```

A list of all joints this assembly link has.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Assembly/__init__.pyi` line(s) 20.

## `Assembly.AssemblyLink.LinkedObject`

```python
@property
def LinkedObject(self) -> DocumentObject | tuple[DocumentObject, str | list[str]] | None:

@LinkedObject.setter
def LinkedObject(self, value: DocumentObject | None | tuple[DocumentObject, str | Sequence[str]] | list[DocumentObject | str | Sequence[str]]) -> None:
```

The linked assembly.

Access: getter and setter declared in the stub.

Evidence: public stub `Assembly/__init__.pyi` line(s) 24, 29.

## `Assembly.AssemblyLink.Rigid`

```python
@property
def Rigid(self) -> bool:

@Rigid.setter
def Rigid(self, value: bool | int) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: getter and setter declared in the stub.

Evidence: public stub `Assembly/__init__.pyi` line(s) 33, 37.

