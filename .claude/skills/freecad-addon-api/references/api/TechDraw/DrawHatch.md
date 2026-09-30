# `TechDraw.DrawHatch`

[Module](index.md)

```python
class DrawHatch(DocumentObject):
```

Feature for creating and manipulating Technical Drawing Hatch areas

Author: WandererFan (wandererfan@gmail.com)
License: LGPL-2.1-or-later

Evidence: public stub `TechDraw/__init__.pyi` line 337. Inherited members are on the named base's reference; aliases keep their imported identity.

## `TechDraw.DrawHatch.HatchPattern`

```python
@property
def HatchPattern(self) -> str:

@HatchPattern.setter
def HatchPattern(self, value: str | dict[str, str]) -> None:
```

The hatch pattern file for this area

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 346, 351.

## `TechDraw.DrawHatch.Source`

```python
@property
def Source(self) -> tuple[DocumentObject, list[str]] | None:

@Source.setter
def Source(self, value: DocumentObject | None | _DocumentObjectSubLinkPairInput) -> None:
```

The View + Face to be hatched

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 355, 360.

## `TechDraw.DrawHatch.SvgIncluded`

```python
@property
def SvgIncluded(self) -> str:

@SvgIncluded.setter
def SvgIncluded(self, value: _FileInput | dict[str, str] | tuple[str | bytes, str | bytes]) -> None:
```

Embedded SVG hatch file. System use only.

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 364, 369.

## `TechDraw.DrawHatch.translateLabel`

```python
def translateLabel(self, context: str, base_name: str, unique_name: str, /) -> None:
```

translateLabel(translationContext, objectBaseName, objectUniqueName).
No return value.  Replace the current label with a translated version where possible.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 372.

