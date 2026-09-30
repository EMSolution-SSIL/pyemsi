# `Part.HLRBRep.Algo`

[Module](index.md)

```python
class Algo:
```

Algo() -> HLRBRep_Algo

A framework to compute a shape as seen in a projection
plane. This is done by calculating the visible and the hidden parts
of the shape. HLRBRep_Algo works with three types of entity:

- shapes to be visualized
- edges in these shapes (these edges are the basic entities which will be
  visualized or hidden), and
- faces in these shapes which hide the edges.

HLRBRep_Algo is based on the principle of comparing each edge of the shape to
be visualized with each of its faces, and calculating the visible and the
hidden parts of each edge. For a given projection, HLRBRep_Algo calculates a
set of lines characteristic of the object being represented. It is also used in
conjunction with the HLRBRep_HLRToShape extraction utilities, which reconstruct
a new, simplified shape from a selection of calculation results. This new shape
is made up of edges, which represent the shape visualized in the
projection. HLRBRep_Algo takes the shape itself into account whereas
HLRBRep_PolyAlgo works with a polyhedral simplification of the shape. When you
use HLRBRep_Algo, you obtain an exact result, whereas, when you use
HLRBRep_PolyAlgo, you reduce computation time but obtain polygonal segments. In
the case of complicated shapes, HLRBRep_Algo may be time-consuming. An
HLRBRep_Algo object provides a framework for:

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

Author: Werner Mayer (wmayer@users.sourceforge.net)
Licence: LGPL

Evidence: public stub `Part/HLRBRep.pyi` line 8. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.HLRBRep.Algo.add`

```python
def add(self, S, nbIso: int=0, /) -> None:
```

add(S, nbIso=0)

Adds the shape S to this framework, and specifies the number of isoparameters
nbiso desired in visualizing S.  You may add as many shapes as you wish.  Use
the function add once for each shape.

Evidence: public stub `Part/HLRBRep.pyi` line(s) 51.

## `Part.HLRBRep.Algo.remove`

```python
def remove(self, i: int, /) -> None:
```

remove(i)

Remove the shape of index i from this framework.

Evidence: public stub `Part/HLRBRep.pyi` line(s) 61.

## `Part.HLRBRep.Algo.index`

```python
def index(self, S, /) -> int:
```

index(S) ->  int

Return the index of the Shape S and return 0 if the Shape S is not found.

Evidence: public stub `Part/HLRBRep.pyi` line(s) 69.

## `Part.HLRBRep.Algo.outLinedShapeNullify`

```python
def outLinedShapeNullify(self) -> None:
```

outlinedShapeNullify()

Nullify all the results of OutLiner from HLRTopoBRep.

Evidence: public stub `Part/HLRBRep.pyi` line(s) 77.

## `Part.HLRBRep.Algo.setProjector`

```python
def setProjector(self, Origin: tuple[float, float, float]=(0, 0, 0), ZDir: tuple[float, float, float]=(0, 0, 0), XDir: tuple[float, float, float]=(0, 0, 0), focus: float=float('nan')) -> None:
```

setProjector(Origin=(0, 0, 0), ZDir=(0,0,0), XDir=(0,0,0), focus=NaN)

Set the projector.  With focus left to NaN, an axonometric projector is
created.  Otherwise, a perspective projector is created with focus focus.

Evidence: public stub `Part/HLRBRep.pyi` line(s) 85.

## `Part.HLRBRep.Algo.nbShapes`

```python
def nbShapes(self) -> int:
```

nbShapes()

Returns the number of shapes in the collection.  It does not modify the
object's state and is used to retrieve the count of shapes.

Evidence: public stub `Part/HLRBRep.pyi` line(s) 94.

## `Part.HLRBRep.Algo.showAll`

```python
def showAll(self, i: int=-1, /) -> None:
```

showAll(i=-1)

If i < 1, then set all the edges to visible.
Otherwise, set to visible all the edges of the shape of index i.

Evidence: public stub `Part/HLRBRep.pyi` line(s) 103.

## `Part.HLRBRep.Algo.hide`

```python
def hide(self, i: int=-1, j: int=-1, /) -> None:
```

hide(i=-1, j=-1)

If i < 1, hide all of the datastructure.
Otherwise, if j < 1, hide the shape of index i.
Otherwise, hide the shape of index i by the shape of index j.

Evidence: public stub `Part/HLRBRep.pyi` line(s) 112.

## `Part.HLRBRep.Algo.hideAll`

```python
def hideAll(self, i: int=-1, /) -> None:
```

hideAll(i=-1)

If i < 1, hide all the edges.
Otherwise, hide all the edges of shape of index i.

Evidence: public stub `Part/HLRBRep.pyi` line(s) 122.

## `Part.HLRBRep.Algo.partialHide`

```python
def partialHide(self) -> None:
```

partialHide()

Own hiding of all the shapes of the DataStructure without hiding by each other.

Evidence: public stub `Part/HLRBRep.pyi` line(s) 131.

## `Part.HLRBRep.Algo.select`

```python
def select(self, i: int=-1, /) -> None:
```

select(i=-1)

If i < 1, select all the DataStructure.
Otherwise, only select the shape of index i.

Evidence: public stub `Part/HLRBRep.pyi` line(s) 139.

## `Part.HLRBRep.Algo.selectEdge`

```python
def selectEdge(self, i: int, /) -> None:
```

selectEdge(i)

Select only the edges of the shape of index i.

Evidence: public stub `Part/HLRBRep.pyi` line(s) 148.

## `Part.HLRBRep.Algo.selectFace`

```python
def selectFace(self, i: int, /) -> None:
```

selectFace(i)

Select only the faces of the shape of index i.

Evidence: public stub `Part/HLRBRep.pyi` line(s) 156.

## `Part.HLRBRep.Algo.initEdgeStatus`

```python
def initEdgeStatus(self) -> None:
```

initEdgeStatus()

Init the status of the selected edges depending of the back faces of a closed
shell.

Evidence: public stub `Part/HLRBRep.pyi` line(s) 164.

## `Part.HLRBRep.Algo.update`

```python
def update(self) -> None:
```

update()

Update the DataStructure.

Evidence: public stub `Part/HLRBRep.pyi` line(s) 173.

