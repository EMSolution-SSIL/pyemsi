# `Part.ShapeUpgrade.UnifySameDomain`

[Module](index.md)

```python
class UnifySameDomain:
```

This tool tries to unify faces and edges of the shape which lie on the same geometry.

Author: Werner Mayer (wmayer@users.sourceforge.net)
Licence: LGPL

Evidence: public stub `Part/ShapeUpgrade.pyi` line 7. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.ShapeUpgrade.UnifySameDomain.initialize`

```python
def initialize(self, Shape: TopoShape, UnifyEdges: bool=True, UnifyFaces: bool=True, ConcatBSplines: bool=False) -> None:
```

Initializes with a shape and necessary flags

Evidence: public stub `Part/ShapeUpgrade.pyi` line(s) 15.

## `Part.ShapeUpgrade.UnifySameDomain.allowInternalEdges`

```python
def allowInternalEdges(self, allow: bool, /) -> None:
```

Sets the flag defining whether it is allowed to create
internal edges inside merged faces in the case of non-manifold
topology. Without this flag merging through multi connected edge
is forbidden. Default value is false.

Evidence: public stub `Part/ShapeUpgrade.pyi` line(s) 21.

## `Part.ShapeUpgrade.UnifySameDomain.keepShape`

```python
def keepShape(self, shape: TopoShape, /) -> None:
```

Sets the shape for avoid merging of the faces/edges.

Evidence: public stub `Part/ShapeUpgrade.pyi` line(s) 30.

## `Part.ShapeUpgrade.UnifySameDomain.keepShapes`

```python
def keepShapes(self, shapes: list[TopoShape], /) -> None:
```

Sets the map of shapes for avoid merging of the faces/edges.

Evidence: public stub `Part/ShapeUpgrade.pyi` line(s) 36.

## `Part.ShapeUpgrade.UnifySameDomain.setSafeInputMode`

```python
def setSafeInputMode(self, mode: bool, /) -> None:
```

Sets the flag defining the behavior of the algorithm regarding
modification of input shape.
If this flag is equal to True then the input (original) shape can't be
modified during modification process. Default value is true.

Evidence: public stub `Part/ShapeUpgrade.pyi` line(s) 42.

## `Part.ShapeUpgrade.UnifySameDomain.setLinearTolerance`

```python
def setLinearTolerance(self, tolerance: float, /) -> None:
```

Sets the linear tolerance

Evidence: public stub `Part/ShapeUpgrade.pyi` line(s) 51.

## `Part.ShapeUpgrade.UnifySameDomain.setAngularTolerance`

```python
def setAngularTolerance(self, tolerance: float, /) -> None:
```

Sets the angular tolerance

Evidence: public stub `Part/ShapeUpgrade.pyi` line(s) 57.

## `Part.ShapeUpgrade.UnifySameDomain.build`

```python
def build(self) -> None:
```

Performs unification and builds the resulting shape

Evidence: public stub `Part/ShapeUpgrade.pyi` line(s) 63.

## `Part.ShapeUpgrade.UnifySameDomain.shape`

```python
def shape(self) -> TopoShape:
```

Gives the resulting shape

Evidence: public stub `Part/ShapeUpgrade.pyi` line(s) 69.

