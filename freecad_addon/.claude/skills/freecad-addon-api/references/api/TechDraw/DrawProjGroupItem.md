# `TechDraw.DrawProjGroupItem`

[Module](index.md)

```python
class DrawProjGroupItem(DrawViewPart):
```

Feature for creating and manipulating component Views Technical Drawing Projection Groups

Author: WandererFan (wandererfan@gmail.com)
License: LGPL-2.1-or-later

Evidence: public stub `TechDraw/__init__.pyi` line 656. Inherited members are on the named base's reference; aliases keep their imported identity.

## `TechDraw.DrawProjGroupItem.RotationVector`

```python
@property
def RotationVector(self) -> Base.Vector:

@RotationVector.setter
def RotationVector(self, value: Base.Vector | tuple[float, float, float]) -> None:
```

Deprecated. Use XDirection.

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 665, 670.

## `TechDraw.DrawProjGroupItem.Type`

```python
@property
def Type(self) -> str:

@Type.setter
def Type(self, value: str | list[str]) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 674, 678.

## `TechDraw.DrawProjGroupItem.autoPosition`

```python
def autoPosition(self) -> Any:
```

autoPosition() - Move to AutoDistribute/Unlocked position on Page. Returns none.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 681.

