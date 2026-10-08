# `TechDraw.DrawTemplate`

[Module](index.md)

```python
class DrawTemplate(DocumentObject):
```

Feature for creating and manipulating Technical Drawing Templates

Author: Luke Parry (l.parry@warwick.ac.uk)
License: LGPL-2.1-or-later

Evidence: public stub `TechDraw/__init__.pyi` line 779. Inherited members are on the named base's reference; aliases keep their imported identity.

## `TechDraw.DrawTemplate.EditableTexts`

```python
@property
def EditableTexts(self) -> dict[str, str]:

@EditableTexts.setter
def EditableTexts(self, value: dict[str, str]) -> None:
```

Editable strings in the template

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 788, 793.

## `TechDraw.DrawTemplate.Height`

```python
@property
def Height(self) -> Base.Quantity:

@Height.setter
def Height(self, value: float | str | Base.Quantity) -> None:
```

Height of page

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 797, 802.

## `TechDraw.DrawTemplate.Orientation`

```python
@property
def Orientation(self) -> str:

@Orientation.setter
def Orientation(self, value: str | list[str]) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 806, 810.

## `TechDraw.DrawTemplate.Width`

```python
@property
def Width(self) -> Base.Quantity:

@Width.setter
def Width(self, value: float | str | Base.Quantity) -> None:
```

Width of page

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 814, 819.

