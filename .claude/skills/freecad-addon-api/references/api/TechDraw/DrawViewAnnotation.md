# `TechDraw.DrawViewAnnotation`

[Module](index.md)

```python
class DrawViewAnnotation(DrawView):
```

Feature for creating and manipulating Technical Drawing Annotation Views

Author: WandererFan (wandererfan@gmail.com)
License: LGPL-2.1-or-later

Evidence: public stub `TechDraw/__init__.pyi` line 1020. Inherited members are on the named base's reference; aliases keep their imported identity.

## `TechDraw.DrawViewAnnotation.Font`

```python
@property
def Font(self) -> str:

@Font.setter
def Font(self, value: str) -> None:
```

Font name

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1029, 1034.

## `TechDraw.DrawViewAnnotation.LineSpace`

```python
@property
def LineSpace(self) -> int:

@LineSpace.setter
def LineSpace(self, value: int) -> None:
```

Line spacing in %. 100 means single spaced,
200 would be double spaced.

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1038, 1044.

## `TechDraw.DrawViewAnnotation.MaxWidth`

```python
@property
def MaxWidth(self) -> float:

@MaxWidth.setter
def MaxWidth(self, value: float) -> None:
```

Maximum width of the annotation block (in mm).
-1 means no maximum width.

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1048, 1054.

## `TechDraw.DrawViewAnnotation.Owner`

```python
@property
def Owner(self) -> DocumentObject | None:

@Owner.setter
def Owner(self, value: DocumentObject | None) -> None:
```

Feature to which this annotation is attached, if any

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1058, 1063.

## `TechDraw.DrawViewAnnotation.Text`

```python
@property
def Text(self) -> list[str]:

@Text.setter
def Text(self, value: Sequence[str]) -> None:
```

Annotation text

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1067, 1072.

## `TechDraw.DrawViewAnnotation.TextColor`

```python
@property
def TextColor(self) -> tuple[float, float, float, float]:

@TextColor.setter
def TextColor(self, value: int | tuple[float, float, float] | tuple[float, float, float, float] | tuple[int, int, int] | tuple[int, int, int, int]) -> None:
```

Text color

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1076, 1081.

## `TechDraw.DrawViewAnnotation.TextSize`

```python
@property
def TextSize(self) -> Base.Quantity:

@TextSize.setter
def TextSize(self, value: float | str | Base.Quantity) -> None:
```

Text size

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1085, 1090.

## `TechDraw.DrawViewAnnotation.TextStyle`

```python
@property
def TextStyle(self) -> str:

@TextStyle.setter
def TextStyle(self, value: str | list[str]) -> None:
```

Text style

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1094, 1099.

