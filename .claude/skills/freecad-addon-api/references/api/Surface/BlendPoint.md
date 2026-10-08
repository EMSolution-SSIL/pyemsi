# `Surface.BlendPoint`

[Module](index.md)

```python
class BlendPoint:
```

Create BlendPoint from a point and some derivatives.
myBlendPoint = BlendPoint([Point, D1, D2, ..., DN])
BlendPoint can also be constructed from an edge
myBlendPoint = BlendPoint(Edge, parameter = float, continuity = int)

Author: Mattéo Grellier (matteogrellier@gmail.com)
License: LGPL-2.1-or-later

Evidence: public stub `Surface/__init__.pyi` line 35. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Surface.BlendPoint.getSize`

```python
def getSize(self) -> Any:
```

Return BlendPoint first derivative length.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Surface/__init__.pyi` line(s) 46.

## `Surface.BlendPoint.setSize`

```python
def setSize(self, size: float, /) -> None:
```

Resizes the BlendPoint vectors by setting the length of the first derivative.

Evidence: public stub `Surface/__init__.pyi` line(s) 50.

## `Surface.BlendPoint.setvectors`

```python
def setvectors(self, vectors: Sequence[Vector], /) -> None:
```

Set the vectors of BlendPoint.

Evidence: public stub `Surface/__init__.pyi` line(s) 56.

## `Surface.BlendPoint.Vectors`

```python
Vectors: Final[list]
```

The list of vectors of this BlendPoint.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Surface/__init__.pyi` line(s) 61.

