# `TechDraw.DrawLeaderLine`

[Module](index.md)

```python
class DrawLeaderLine(DrawView):
```

Feature for adding leaders to Technical Drawings

Author: WandererFan (wandererfan@gmail.com)
License: LGPL-2.1-or-later

Evidence: public stub `TechDraw/__init__.pyi` line 379. Inherited members are on the named base's reference; aliases keep their imported identity.

## `TechDraw.DrawLeaderLine.AutoHorizontal`

```python
@property
def AutoHorizontal(self) -> bool:

@AutoHorizontal.setter
def AutoHorizontal(self, value: bool | int) -> None:
```

Forces last line segment to be horizontal

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 388, 393.

## `TechDraw.DrawLeaderLine.EndSymbol`

```python
@property
def EndSymbol(self) -> str:

@EndSymbol.setter
def EndSymbol(self, value: str | list[str]) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 397, 401.

## `TechDraw.DrawLeaderLine.LeaderParent`

```python
@property
def LeaderParent(self) -> DocumentObject | None:

@LeaderParent.setter
def LeaderParent(self, value: DocumentObject | None) -> None:
```

View to which this leader is attached

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 405, 410.

## `TechDraw.DrawLeaderLine.RotatesWithParent`

```python
@property
def RotatesWithParent(self) -> bool:

@RotatesWithParent.setter
def RotatesWithParent(self, value: bool | int) -> None:
```

If true, leader rotates around parent.  If false, only first segment of leader changes with parent rotation.

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 414, 419.

## `TechDraw.DrawLeaderLine.Scalable`

```python
@property
def Scalable(self) -> bool:

@Scalable.setter
def Scalable(self, value: bool | int) -> None:
```

Scale line with LeaderParent

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 423, 428.

## `TechDraw.DrawLeaderLine.StartSymbol`

```python
@property
def StartSymbol(self) -> str:

@StartSymbol.setter
def StartSymbol(self, value: str | list[str]) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 432, 436.

## `TechDraw.DrawLeaderLine.WayPoints`

```python
@property
def WayPoints(self) -> list[Base.Vector]:

@WayPoints.setter
def WayPoints(self, value: Sequence[_VectorInput]) -> None:
```

Intermediate points for Leader line

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 440, 445.

