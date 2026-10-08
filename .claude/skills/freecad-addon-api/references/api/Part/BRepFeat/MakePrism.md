# `Part.BRepFeat.MakePrism`

[Module](index.md)

```python
class MakePrism:
```

Describes functions to build prism features.

Author: Werner Mayer (wmayer[at]users.sourceforge.net)
Licence: LGPL

Evidence: public stub `Part/BRepFeat.pyi` line 13. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.BRepFeat.MakePrism.init`

```python
def init(self, Sbase: TopoShape, Pbase: TopoShape, Skface: TopoShapeFace, Direction: Vector, Fuse: int, Modify: bool) -> None:
```

Initializes this algorithm for building prisms along surfaces.
A face Pbase is selected in the shape Sbase
to serve as the basis for the prism. The orientation
of the prism will be defined by the vector Direction.

Fuse offers a choice between:
-   removing matter with a Boolean cut using the setting 0
-   adding matter with Boolean fusion using the setting 1.
The sketch face Skface serves to determine
the type of operation. If it is inside the basis
shape, a local operation such as glueing can be performed.

Evidence: public stub `Part/BRepFeat.pyi` line(s) 21.

## `Part.BRepFeat.MakePrism.add`

```python
def add(self, Edge: TopoShapeEdge, Face: TopoShapeFace) -> None:
```

Indicates that the edge will slide on the face.
Raises ConstructionError if the  face does not belong to the
basis shape, or the edge to the prismed shape.

Evidence: public stub `Part/BRepFeat.pyi` line(s) 37.

## `Part.BRepFeat.MakePrism.perform`

```python
@overload
def perform(self, From: TopoShape, Until: TopoShape) -> None:

@overload
def perform(self, Until: TopoShape) -> None:

@overload
def perform(self, Length: float) -> None:

def perform(self, *args) -> None:
```

Assigns one of the following semantics.
1. to a height Length
2. to a face Until
3. from a face From to a height Until. Reconstructs the feature topologically according to the semantic option chosen.

Evidence: public stub `Part/BRepFeat.pyi` line(s) 46, 50, 54, 57.

## `Part.BRepFeat.MakePrism.performUntilEnd`

```python
def performUntilEnd(self) -> None:
```

Realizes a semi-infinite prism, limited by the
position of the prism base. All other faces extend infinitely.

Evidence: public stub `Part/BRepFeat.pyi` line(s) 66.

## `Part.BRepFeat.MakePrism.performFromEnd`

```python
def performFromEnd(self, until: TopoShape, /) -> None:
```

Realizes a semi-infinite prism, limited by the face Funtil.

Evidence: public stub `Part/BRepFeat.pyi` line(s) 73.

## `Part.BRepFeat.MakePrism.performThruAll`

```python
def performThruAll(self) -> None:
```

Builds an infinite prism. The infinite descendants will not be kept in the result.

Evidence: public stub `Part/BRepFeat.pyi` line(s) 79.

## `Part.BRepFeat.MakePrism.performUntilHeight`

```python
def performUntilHeight(self, until: TopoShape, length: float, /) -> None:
```

Assigns both a limiting shape, Until from TopoDS_Shape
and a height, Length at which to stop generation of the prism feature.

Evidence: public stub `Part/BRepFeat.pyi` line(s) 85.

## `Part.BRepFeat.MakePrism.curves`

```python
def curves(self) -> List:
```

Returns the list of curves S parallel to the axis of the prism.

Evidence: public stub `Part/BRepFeat.pyi` line(s) 92.

## `Part.BRepFeat.MakePrism.barycCurve`

```python
def barycCurve(self) -> GeometryCurve | None:
```

Generates a curve along the center of mass of the primitive.

Evidence: public stub `Part/BRepFeat.pyi` line(s) 98.

## `Part.BRepFeat.MakePrism.shape`

```python
def shape(self) -> object:
```

Returns a shape built by the shape construction algorithm.

Evidence: public stub `Part/BRepFeat.pyi` line(s) 104.

