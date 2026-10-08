# `Part.ShapeFix.FixSmallFace`

[Module](index.md)

```python
class FixSmallFace(Root):
```

Class for fixing operations on faces

Author: Werner Mayer (wmayer@users.sourceforge.net)
Licence: LGPL

Evidence: public stub `Part/ShapeFix.pyi` line 430. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.ShapeFix.FixSmallFace.init`

```python
def init(self, shape: TopoShape, /) -> None:
```

Initializes by shape

Evidence: public stub `Part/ShapeFix.pyi` line(s) 438.

## `Part.ShapeFix.FixSmallFace.perform`

```python
def perform(self) -> None:
```

Fixing case of spot face

Evidence: public stub `Part/ShapeFix.pyi` line(s) 444.

## `Part.ShapeFix.FixSmallFace.fixSpotFace`

```python
def fixSpotFace(self) -> TopoShape:
```

Fixing case of spot face, if tol = -1 used local tolerance

Evidence: public stub `Part/ShapeFix.pyi` line(s) 450.

## `Part.ShapeFix.FixSmallFace.replaceVerticesInCaseOfSpot`

```python
def replaceVerticesInCaseOfSpot(self, face: TopoShapeFace, /) -> TopoShape:
```

Compute average vertex and replacing vertices by new one

Evidence: public stub `Part/ShapeFix.pyi` line(s) 456.

## `Part.ShapeFix.FixSmallFace.removeFacesInCaseOfSpot`

```python
def removeFacesInCaseOfSpot(self, face: TopoShapeFace, /) -> bool:
```

Remove spot face from compound

Evidence: public stub `Part/ShapeFix.pyi` line(s) 462.

## `Part.ShapeFix.FixSmallFace.fixStripFace`

```python
def fixStripFace(self, wasdone: bool=False, /) -> TopoShape:
```

Fixing case of strip face, if tol = -1 used local tolerance

Evidence: public stub `Part/ShapeFix.pyi` line(s) 468.

## `Part.ShapeFix.FixSmallFace.removeFacesInCaseOfStrip`

```python
def removeFacesInCaseOfStrip(self, face: TopoShapeFace, /) -> bool:
```

Remove strip face from compound

Evidence: public stub `Part/ShapeFix.pyi` line(s) 474.

## `Part.ShapeFix.FixSmallFace.fixSplitFace`

```python
def fixSplitFace(self, shape: TopoShape, /) -> TopoShape:
```

Fixes cases related to split faces within the given shape.
It may return a modified shape after fixing the issues.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 480.

## `Part.ShapeFix.FixSmallFace.fixFace`

```python
def fixFace(self, face: TopoShapeFace, /) -> TopoShape:
```

Fixes issues related to the specified face and returns the modified face.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 487.

## `Part.ShapeFix.FixSmallFace.fixShape`

```python
def fixShape(self) -> TopoShape:
```

Fixes issues in the overall geometric shape.
This function likely encapsulates higher-level fixes that involve multiple faces or elements.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 493.

## `Part.ShapeFix.FixSmallFace.shape`

```python
def shape(self) -> TopoShape:
```

Returns the current state of the geometric shape after potential modifications.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 500.

