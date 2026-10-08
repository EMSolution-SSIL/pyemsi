# `TechDraw.DrawViewDimExtent`

[Module](index.md)

```python
class DrawViewDimExtent(DrawViewDimension):
```

Feature for creating and manipulating Technical Drawing DimExtents

Author: WandererFan (wandererfan@gmail.com)
License: LGPL-2.1-or-later

Evidence: public stub `TechDraw/__init__.pyi` line 1183. Inherited members are on the named base's reference; aliases keep their imported identity.

## `TechDraw.DrawViewDimExtent.CosmeticTags`

```python
@property
def CosmeticTags(self) -> list[str]:

@CosmeticTags.setter
def CosmeticTags(self, value: Sequence[str]) -> None:
```

Id of cosmetic endpoints

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1192, 1197.

## `TechDraw.DrawViewDimExtent.DirExtent`

```python
@property
def DirExtent(self) -> int:

@DirExtent.setter
def DirExtent(self, value: int) -> None:
```

Horizontal / Vertical

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1201, 1206.

## `TechDraw.DrawViewDimExtent.Source`

```python
@property
def Source(self) -> list[tuple[DocumentObject, tuple[str, ...]]]:

@Source.setter
def Source(self, value: _DocumentObjectSubLinkInput | Sequence[_DocumentObjectSubLinkListItemInput]) -> None:
```

View containing the  dimension

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1210, 1215.

## `TechDraw.DrawViewDimExtent.Source3d`

```python
@property
def Source3d(self) -> list[tuple[DocumentObject, tuple[str, ...]]]:

@Source3d.setter
def Source3d(self, value: _DocumentObjectSubLinkInput | Sequence[_DocumentObjectSubLinkListItemInput]) -> None:
```

3D geometry to be dimensioned

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1219, 1224.

## `TechDraw.DrawViewDimExtent.tbd`

```python
def tbd(self) -> Any:
```

tbd() - returns tbd.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1227.

