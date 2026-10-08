# `TechDraw.DrawTile`

[Module](index.md)

```python
class DrawTile(DocumentObject):
```

Feature for adding tiles to leader lines

Author: WandererFan (wandererfan@gmail.com)
License: LGPL-2.1-or-later

Evidence: public stub `TechDraw/__init__.pyi` line 822. Inherited members are on the named base's reference; aliases keep their imported identity.

## `TechDraw.DrawTile.TileColumn`

```python
@property
def TileColumn(self) -> int:

@TileColumn.setter
def TileColumn(self, value: int) -> None:
```

Column in parent object

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 831, 836.

## `TechDraw.DrawTile.TileParent`

```python
@property
def TileParent(self) -> DocumentObject | None:

@TileParent.setter
def TileParent(self, value: DocumentObject | None) -> None:
```

Object to which this tile is attached

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 840, 845.

## `TechDraw.DrawTile.TileRow`

```python
@property
def TileRow(self) -> int:

@TileRow.setter
def TileRow(self, value: int | dict[str, int] | tuple[int, int, int, int]) -> None:
```

Row in parent object
0 for arrow side, -1 for other side

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 849, 855.

