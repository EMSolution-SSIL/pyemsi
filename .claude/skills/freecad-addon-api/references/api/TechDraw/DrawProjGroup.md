# `TechDraw.DrawProjGroup`

[Module](index.md)

```python
class DrawProjGroup(DrawViewCollection):
```

Feature for creating and manipulating Technical Drawing Projection Groups

Author: WandererFan (wandererfan@gmail.com)
License: LGPL-2.1-or-later

Evidence: public stub `TechDraw/__init__.pyi` line 565. Inherited members are on the named base's reference; aliases keep their imported identity.

## `TechDraw.DrawProjGroup.Anchor`

```python
@property
def Anchor(self) -> DocumentObject | None:

@Anchor.setter
def Anchor(self, value: DocumentObject | None) -> None:
```

The root view to align projections with

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 574, 579.

## `TechDraw.DrawProjGroup.AutoDistribute`

```python
@property
def AutoDistribute(self) -> bool:

@AutoDistribute.setter
def AutoDistribute(self, value: bool | int) -> None:
```

Distribute views automatically or manually

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 583, 588.

## `TechDraw.DrawProjGroup.ProjectionType`

```python
@property
def ProjectionType(self) -> str:

@ProjectionType.setter
def ProjectionType(self, value: str | list[str]) -> None:
```

First or Third angle projection

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 592, 597.

## `TechDraw.DrawProjGroup.Source`

```python
@property
def Source(self) -> list[DocumentObject | None]:

@Source.setter
def Source(self, value: Sequence[DocumentObject]) -> None:
```

Shape to view

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 601, 606.

## `TechDraw.DrawProjGroup.XSource`

```python
@property
def XSource(self) -> _DocumentObjectList | _DocumentObjectSubLinkList:

@XSource.setter
def XSource(self, value: _DocumentObjectListInput | _DocumentObjectSubLinkListInput) -> None:
```

External 3D Shape to view

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 610, 615.

## `TechDraw.DrawProjGroup.spacingX`

```python
@property
def spacingX(self) -> Base.Quantity:

@spacingX.setter
def spacingX(self, value: float | str | Base.Quantity) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 619, 623.

## `TechDraw.DrawProjGroup.spacingY`

```python
@property
def spacingY(self) -> Base.Quantity:

@spacingY.setter
def spacingY(self, value: float | str | Base.Quantity) -> None:
```

If AutoDistribute is on, this is the vertical 
spacing between the borders of views

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 627, 633.

## `TechDraw.DrawProjGroup.addProjection`

```python
def addProjection(self, projection_type: str, /) -> DrawProjGroupItem:
```

addProjection(string projectionType) - Add a new Projection Item to this Group. Returns DocObj.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 636.

## `TechDraw.DrawProjGroup.removeProjection`

```python
def removeProjection(self, projection_type: str, /) -> int:
```

removeProjection(string projectionType) - Remove specified Projection Item from this Group. Returns int number of views in Group.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 640.

## `TechDraw.DrawProjGroup.purgeProjections`

```python
def purgeProjections(self) -> Any:
```

purgeProjections() - Remove all Projection Items from this Group. Returns int number of views in Group (0).

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 644.

## `TechDraw.DrawProjGroup.getItemByLabel`

```python
def getItemByLabel(self, projection_type: str, /) -> DrawProjGroupItem:
```

getItemByLabel(string projectionType) - return specified Projection Item

Evidence: public stub `TechDraw/__init__.pyi` line(s) 648.

## `TechDraw.DrawProjGroup.getXYPosition`

```python
def getXYPosition(self, projection_type: str, /) -> Vector:
```

getXYPosition(string projectionType) - return the AutoDistribute position for specified Projection Item

Evidence: public stub `TechDraw/__init__.pyi` line(s) 652.

