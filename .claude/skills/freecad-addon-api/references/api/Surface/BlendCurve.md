# `Surface.BlendCurve`

[Module](index.md)

```python
class BlendCurve:
```

Create a BlendCurve that interpolate 2 BlendPoints.
    curve = BlendCurve(BlendPoint1, BlendPoint2)

Author: Mattéo Grellier (matteogrellier@gmail.com)
License: LGPL-2.1-or-later

Evidence: public stub `Surface/__init__.pyi` line 10. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Surface.BlendCurve.compute`

```python
def compute(self) -> Any:
```

Return the BezierCurve that interpolate the input BlendPoints.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Surface/__init__.pyi` line(s) 19.

## `Surface.BlendCurve.setSize`

```python
def setSize(self, index: int, size: float, relative: bool, /) -> None:
```

Set the tangent size of the blendpoint at given index.

If relative is true, the size is considered relative to the distance between the two blendpoints.
myBlendCurve.setSize(idx, size, relative)

Evidence: public stub `Surface/__init__.pyi` line(s) 25.

