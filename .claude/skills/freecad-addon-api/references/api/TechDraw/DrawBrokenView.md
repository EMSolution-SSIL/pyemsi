# `TechDraw.DrawBrokenView`

[Module](index.md)

```python
class DrawBrokenView(DrawViewPart):
```

Feature for creating and manipulating Technical Drawing broken views

Author: WandererFan (wandererfan@gmail.com)
License: LGPL-2.1-or-later

Evidence: public stub `TechDraw/__init__.pyi` line 221. Inherited members are on the named base's reference; aliases keep their imported identity.

## `TechDraw.DrawBrokenView.Breaks`

```python
@property
def Breaks(self) -> list[DocumentObject | None]:

@Breaks.setter
def Breaks(self, value: Sequence[DocumentObject]) -> None:
```

Objects in the 3D view that define the start/end points and direction of breaks in this view.

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 230, 235.

## `TechDraw.DrawBrokenView.Gap`

```python
@property
def Gap(self) -> Base.Quantity:

@Gap.setter
def Gap(self, value: float | str | Base.Quantity) -> None:
```

The separation distance for breaks in this view (unscaled 3D length).

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 239, 244.

## `TechDraw.DrawBrokenView.mapPoint3dToView`

```python
def mapPoint3dToView(self, point: Vector, /) -> Vector:
```

point2d = mapPoint3dToView(point3d) - returns the position of the 3d point within the broken view.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 247.

## `TechDraw.DrawBrokenView.mapPoint2dFromView`

```python
def mapPoint2dFromView(self, point: Vector, /) -> Vector:
```

point2d = mapPoint2dFromView(point3d) - returns the position of the 2d point within an unbroken view.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 251.

## `TechDraw.DrawBrokenView.getCompressedCenter`

```python
def getCompressedCenter(self) -> Any:
```

point3d = getCompressedCenter() - returns the geometric center of the source shapes after break cuts and gap compression.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 255.

