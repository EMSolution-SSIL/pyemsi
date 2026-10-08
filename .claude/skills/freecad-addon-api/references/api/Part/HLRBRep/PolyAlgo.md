# `Part.HLRBRep.PolyAlgo`

[Module](index.md)

```python
class PolyAlgo:
```

PolyAlgo() -> HLRBRep_PolyAlgo

A framework to compute the shape as seen in a projection
plane. This is done by calculating the visible and the hidden parts of the
shape. HLRBRep_PolyAlgo works with three types of entity:

- shapes to be visualized (these shapes must have already been triangulated.)
- edges in these shapes (these edges are defined as polygonal lines on the
  triangulation of the shape, and are the basic entities which will be visualized
  or hidden), and
- triangles in these shapes which hide the edges.

HLRBRep_PolyAlgo is based on the principle of comparing each edge of the shape
to be visualized with each of the triangles produced by the triangulation of
the shape, and calculating the visible and the hidden parts of each edge. For a
given projection, HLRBRep_PolyAlgo calculates a set of lines characteristic of
the object being represented. It is also used in conjunction with the
HLRBRep_PolyHLRToShape extraction utilities, which reconstruct a new,
simplified shape from a selection of calculation results. This new shape is
made up of edges, which represent the shape visualized in the
projection. HLRBRep_PolyAlgo works with a polyhedral simplification of the
shape whereas HLRBRep_Algo takes the shape itself into account. When you use
HLRBRep_Algo, you obtain an exact result, whereas, when you use
HLRBRep_PolyAlgo, you reduce computation time but obtain polygonal segments. An
HLRBRep_PolyAlgo object provides a framework for:

- defining the point of view
- identifying the shape or shapes to be visualized
- calculating the outlines
- calculating the visible and hidden lines of the shape. Warning
- Superimposed lines are not eliminated by this algorithm.
- There must be no unfinished objects inside the shape you wish to visualize.
- Points are not treated.
- Note that this is not the sort of algorithm used in generating shading, which
  calculates the visible and hidden parts of each face in a shape to be
  visualized by comparing each face in the shape with every other face in the
  same shape.

Evidence: public stub `Part/HLRBRep.pyi` line 182. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.HLRBRep.PolyAlgo.load`

```python
def load(self, S: TopoShape, /) -> None:
```

load(S)

Loads the shape S into this framework. Warning S must have already been triangulated.

Evidence: public stub `Part/HLRBRep.pyi` line(s) 223.

## `Part.HLRBRep.PolyAlgo.remove`

```python
def remove(self, i: int, /) -> None:
```

remove(i)

Remove the shape of index i from this framework.

Evidence: public stub `Part/HLRBRep.pyi` line(s) 231.

## `Part.HLRBRep.PolyAlgo.nbShapes`

```python
def nbShapes(self) -> int:
```

nbShapes()

Returns the number of shapes in the collection.  It does not modify the
object's state and is used to retrieve the count of shapes.

Evidence: public stub `Part/HLRBRep.pyi` line(s) 239.

## `Part.HLRBRep.PolyAlgo.shape`

```python
def shape(self, i: int, /) -> TopoShape:
```

shape(i) -> TopoShape

Return the shape of index i.

Evidence: public stub `Part/HLRBRep.pyi` line(s) 248.

## `Part.HLRBRep.PolyAlgo.index`

```python
def index(self, S: TopoShape, /) -> int:
```

index(S) ->  int

Return the index of the Shape S.

Evidence: public stub `Part/HLRBRep.pyi` line(s) 256.

## `Part.HLRBRep.PolyAlgo.setProjector`

```python
def setProjector(self, Origin: tuple[float, float, float]=(0.0, 0.0, 0.0), ZDir: tuple[float, float, float]=(0.0, 0.0, 0.0), XDir: tuple[float, float, float]=(0.0, 0.0, 0.0), focus: float=float('nan')) -> None:
```

setProjector(Origin=(0, 0, 0), ZDir=(0,0,0), XDir=(0,0,0), focus=NaN)

Set the projector.  With focus left to NaN, an axonometric projector is
created.  Otherwise, a perspective projector is created with focus focus.

Evidence: public stub `Part/HLRBRep.pyi` line(s) 264.

## `Part.HLRBRep.PolyAlgo.update`

```python
def update(self) -> None:
```

update()

Launches calculation of outlines of the shape visualized by this
framework. Used after setting the point of view and defining the shape or
shapes to be visualized.

Evidence: public stub `Part/HLRBRep.pyi` line(s) 273.

## `Part.HLRBRep.PolyAlgo.initHide`

```python
def initHide(self) -> None:
```

initHide()

Evidence: public stub `Part/HLRBRep.pyi` line(s) 283.

## `Part.HLRBRep.PolyAlgo.moreHide`

```python
def moreHide(self) -> bool:
```

moreHide()

Evidence: public stub `Part/HLRBRep.pyi` line(s) 289.

## `Part.HLRBRep.PolyAlgo.nextHide`

```python
def nextHide(self) -> None:
```

nextHide()

Evidence: public stub `Part/HLRBRep.pyi` line(s) 295.

## `Part.HLRBRep.PolyAlgo.initShow`

```python
def initShow(self) -> None:
```

initShow()

Evidence: public stub `Part/HLRBRep.pyi` line(s) 301.

## `Part.HLRBRep.PolyAlgo.moreShow`

```python
def moreShow(self) -> bool:
```

moreShow()

Evidence: public stub `Part/HLRBRep.pyi` line(s) 307.

## `Part.HLRBRep.PolyAlgo.nextShow`

```python
def nextShow(self) -> None:
```

nextShow()

Evidence: public stub `Part/HLRBRep.pyi` line(s) 313.

## `Part.HLRBRep.PolyAlgo.outLinedShape`

```python
def outLinedShape(self, S: TopoShape, /) -> TopoShape:
```

outLinedShape(S) -> TopoShape

Make a shape with the internal outlines in each face of shape S.

Evidence: public stub `Part/HLRBRep.pyi` line(s) 319.

## `Part.HLRBRep.PolyAlgo.TolAngular`

```python
TolAngular: float = ...
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/HLRBRep.pyi` line(s) 326.

## `Part.HLRBRep.PolyAlgo.TolCoef`

```python
TolCoef: float = ...
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/HLRBRep.pyi` line(s) 327.

