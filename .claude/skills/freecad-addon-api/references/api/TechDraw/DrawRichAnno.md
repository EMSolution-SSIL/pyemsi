# `TechDraw.DrawRichAnno`

[Module](index.md)

```python
class DrawRichAnno(DrawView):
```

Feature for adding rich annotation blocks to Technical Drawings

Author: WandererFan (wandererfan@gmail.com)
License: LGPL-2.1-or-later

Evidence: public stub `TechDraw/__init__.pyi` line 685. Inherited members are on the named base's reference; aliases keep their imported identity.

## `TechDraw.DrawRichAnno.AnnoParent`

```python
@property
def AnnoParent(self) -> DocumentObject | None:

@AnnoParent.setter
def AnnoParent(self, value: DocumentObject | None) -> None:
```

Object to which this annontation is attached

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 694, 699.

## `TechDraw.DrawRichAnno.AnnoText`

```python
@property
def AnnoText(self) -> str:

@AnnoText.setter
def AnnoText(self, value: str) -> None:
```

Annotation text

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 703, 708.

## `TechDraw.DrawRichAnno.MaxWidth`

```python
@property
def MaxWidth(self) -> float:

@MaxWidth.setter
def MaxWidth(self, value: float) -> None:
```

Width limit before auto wrap

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 712, 717.

## `TechDraw.DrawRichAnno.OriginCentered`

```python
@property
def OriginCentered(self) -> bool:

@OriginCentered.setter
def OriginCentered(self, value: bool | int) -> None:
```

Center the annotation on it's origin.

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 721, 726.

## `TechDraw.DrawRichAnno.ShowFrame`

```python
@property
def ShowFrame(self) -> bool:

@ShowFrame.setter
def ShowFrame(self, value: bool | int) -> None:
```

Outline rectangle on/off

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 730, 735.

