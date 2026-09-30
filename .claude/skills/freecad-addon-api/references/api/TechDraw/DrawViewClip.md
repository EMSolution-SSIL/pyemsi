# `TechDraw.DrawViewClip`

[Module](index.md)

```python
class DrawViewClip(DrawView):
```

Feature for creating and manipulating Technical Drawing Clip Views

Author: WandererFan (wandererfan@gmail.com)
License: LGPL-2.1-or-later

Evidence: public stub `TechDraw/__init__.pyi` line 1102. Inherited members are on the named base's reference; aliases keep their imported identity.

## `TechDraw.DrawViewClip.Height`

```python
@property
def Height(self) -> Base.Quantity:

@Height.setter
def Height(self, value: float | str | Base.Quantity) -> None:
```

The height of the view area of this clip

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1111, 1116.

## `TechDraw.DrawViewClip.ShowFrame`

```python
@property
def ShowFrame(self) -> bool:

@ShowFrame.setter
def ShowFrame(self, value: bool | int) -> None:
```

Specifies if the clip frame appears on the page or not

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1120, 1125.

## `TechDraw.DrawViewClip.Views`

```python
@property
def Views(self) -> list[DocumentObject | None]:

@Views.setter
def Views(self, value: Sequence[DocumentObject]) -> None:
```

The Views in this Clip group

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1129, 1134.

## `TechDraw.DrawViewClip.Width`

```python
@property
def Width(self) -> Base.Quantity:

@Width.setter
def Width(self, value: float | str | Base.Quantity) -> None:
```

The width of the view area of this clip

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1138, 1143.

## `TechDraw.DrawViewClip.addView`

```python
def addView(self, view: DrawView, /) -> None:
```

addView(DrawView) - Add a View to this ClipView

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1146.

## `TechDraw.DrawViewClip.removeView`

```python
def removeView(self, view: DrawView, /) -> None:
```

removeView(DrawView) - Remove specified View to this ClipView

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1150.

## `TechDraw.DrawViewClip.getChildViewNames`

```python
def getChildViewNames(self) -> Any:
```

getChildViewNames() - get a list of the DrawViews in this ClipView

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1154.

