# `TechDraw.DrawView`

[Module](index.md)

```python
class DrawView(DocumentObject):
```

Feature for creating and manipulating Technical Drawing Views

Author: WandererFan (wandererfan@gmail.com)
License: LGPL-2.1-or-later

Evidence: public stub `TechDraw/__init__.pyi` line 911. Inherited members are on the named base's reference; aliases keep their imported identity.

## `TechDraw.DrawView.Caption`

```python
@property
def Caption(self) -> str:

@Caption.setter
def Caption(self, value: str) -> None:
```

Short text about the view

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 920, 925.

## `TechDraw.DrawView.CaptionLocation`

```python
@property
def CaptionLocation(self) -> Base.Vector:

@CaptionLocation.setter
def CaptionLocation(self, value: Base.Vector | tuple[float, float, float]) -> None:
```

Location of the caption relative to the view

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 929, 934.

## `TechDraw.DrawView.CaptionSnap`

```python
@property
def CaptionSnap(self) -> str:

@CaptionSnap.setter
def CaptionSnap(self, value: str | list[str]) -> None:
```

Snap the caption to the view's top, bottom, left or right edge

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 938, 943.

## `TechDraw.DrawView.LockPosition`

```python
@property
def LockPosition(self) -> bool:

@LockPosition.setter
def LockPosition(self, value: bool | int) -> None:
```

Lock View position to parent Page or Group

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 947, 952.

## `TechDraw.DrawView.Rotation`

```python
@property
def Rotation(self) -> Base.Quantity:

@Rotation.setter
def Rotation(self, value: float | str | Base.Quantity) -> None:
```

Rotation in degrees counterclockwise

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 956, 961.

## `TechDraw.DrawView.Scale`

```python
@property
def Scale(self) -> float:

@Scale.setter
def Scale(self, value: float | int | dict[str, float] | tuple[float, float, float, float]) -> None:
```

Scale factor of the view (decimal value). For fractions, use an expression (e.g. =1/10).

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 965, 970.

## `TechDraw.DrawView.ScaleType`

```python
@property
def ScaleType(self) -> str:

@ScaleType.setter
def ScaleType(self, value: str | list[str]) -> None:
```

Scale Type

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 974, 979.

## `TechDraw.DrawView.X`

```python
@property
def X(self) -> Base.Quantity:

@X.setter
def X(self, value: float | str | Base.Quantity | Base.Unit) -> None:
```

X position

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 983, 988.

## `TechDraw.DrawView.Y`

```python
@property
def Y(self) -> Base.Quantity:

@Y.setter
def Y(self, value: float | str | Base.Quantity | Base.Unit) -> None:
```

Y position

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 992, 997.

## `TechDraw.DrawView.translateLabel`

```python
def translateLabel(self, context: str, base_name: str, unique_name: str, /) -> None:
```

translateLabel(translationContext, objectBaseName, objectUniqueName).
No return value.  Replace the current label with a translated version where possible.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1000.

## `TechDraw.DrawView.getScale`

```python
def getScale(self) -> Any:
```

float scale = getScale().  Returns the correct scale for this view.  Handles whether to
use this view's scale property or a parent's view (as in a projection group).

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1007.

## `TechDraw.DrawView.findParentPage`

```python
def findParentPage(self) -> Any:
```

DrawPage parent = findParentPage().  Returns the parent page that contains this view.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1014.

