# `TechDraw.DrawGeomHatch`

[Module](index.md)

```python
class DrawGeomHatch(DocumentObject):
```

Feature for creating and manipulating Technical Drawing GeomHatch areas

Author: WandererFan (wandererfan@gmail.com)
License: LGPL-2.1-or-later

Evidence: public stub `TechDraw/__init__.pyi` line 259. Inherited members are on the named base's reference; aliases keep their imported identity.

## `TechDraw.DrawGeomHatch.FilePattern`

```python
@property
def FilePattern(self) -> str:

@FilePattern.setter
def FilePattern(self, value: str | dict[str, str]) -> None:
```

The crosshatch pattern file for this area

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 268, 273.

## `TechDraw.DrawGeomHatch.NamePattern`

```python
@property
def NamePattern(self) -> str:

@NamePattern.setter
def NamePattern(self, value: str) -> None:
```

The name of the pattern

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 277, 282.

## `TechDraw.DrawGeomHatch.PatIncluded`

```python
@property
def PatIncluded(self) -> str:

@PatIncluded.setter
def PatIncluded(self, value: _FileInput | dict[str, str] | tuple[str | bytes, str | bytes]) -> None:
```

Embedded Pat hatch file. System use only.

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 286, 291.

## `TechDraw.DrawGeomHatch.PatternOffset`

```python
@property
def PatternOffset(self) -> Base.Vector:

@PatternOffset.setter
def PatternOffset(self, value: Base.Vector | tuple[float, float, float]) -> None:
```

Pattern offset

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 295, 300.

## `TechDraw.DrawGeomHatch.PatternRotation`

```python
@property
def PatternRotation(self) -> float:

@PatternRotation.setter
def PatternRotation(self, value: float) -> None:
```

Pattern rotation in degrees anticlockwise

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 304, 309.

## `TechDraw.DrawGeomHatch.ScalePattern`

```python
@property
def ScalePattern(self) -> float:

@ScalePattern.setter
def ScalePattern(self, value: float | int | dict[str, float] | tuple[float, float, float, float]) -> None:
```

GeomHatch pattern size adjustment

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 313, 318.

## `TechDraw.DrawGeomHatch.Source`

```python
@property
def Source(self) -> tuple[DocumentObject, list[str]] | None:

@Source.setter
def Source(self, value: DocumentObject | None | _DocumentObjectSubLinkPairInput) -> None:
```

The View + Face to be crosshatched

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 322, 327.

## `TechDraw.DrawGeomHatch.translateLabel`

```python
def translateLabel(self, context: str, base_name: str, unique_name: str, /) -> None:
```

translateLabel(translationContext, objectBaseName, objectUniqueName).
No return value.  Replace the current label with a translated version where possible.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 330.

