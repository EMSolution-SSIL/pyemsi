# `Part.HLRBRep.PolyHLRToShape`

[Module](index.md)

```python
class PolyHLRToShape:
```

PolyHLRToShape(algo: HLRBRep_PolyAlgo) -> HLRBRep_PolyHLRToShape

A framework for filtering the computation results of an HLRBRep_PolyAlgo
algorithm by extraction.  From the results calculated by the algorithm on a
shape, a filter returns the type of edge you want to identify.  You can choose
any of the following types of output:
- visible sharp edges
- hidden sharp edges
- visible smooth edges
- hidden smooth edges
- visible sewn edges
- hidden sewn edges
- visible outline edges
- hidden outline edges
- visible isoparameters and
- hidden isoparameters.

Sharp edges present a C0 continuity (non G1). Smooth edges present a G1
continuity (non G2). Sewn edges present a C2 continuity. The result is composed
of 2D edges in the projection plane of the view which the algorithm has worked
with. These 2D edges are not included in the data structure of the visualized
shape. In order to obtain a complete image, you must combine the shapes given
by each of the chosen filters. The construction of the shape does not call a
new computation of the algorithm, but only reads its internal results.

Evidence: public stub `Part/HLRBRep.pyi` line 473. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.HLRBRep.PolyHLRToShape.update`

```python
def update(self, algo: PolyAlgo, /) -> None:
```

update(algo: HLRBRep_PolyAlgo)

Evidence: public stub `Part/HLRBRep.pyi` line(s) 501.

## `Part.HLRBRep.PolyHLRToShape.show`

```python
def show(self) -> None:
```

show()

Evidence: public stub `Part/HLRBRep.pyi` line(s) 507.

## `Part.HLRBRep.PolyHLRToShape.hide`

```python
def hide(self) -> None:
```

hide()

Evidence: public stub `Part/HLRBRep.pyi` line(s) 513.

## `Part.HLRBRep.PolyHLRToShape.vCompound`

```python
def vCompound(self, Shape: Optional[TopoShape]=None, /) -> TopoShape:
```

vCompound(Shape=None) -> TopoShape

Sets the extraction filter for visible sharp edges for either shape Shape or
for all added shapes (Shape=None).

Evidence: public stub `Part/HLRBRep.pyi` line(s) 519.

## `Part.HLRBRep.PolyHLRToShape.Rg1LineVCompound`

```python
def Rg1LineVCompound(self, Shape: Optional[TopoShape]=None, /) -> TopoShape:
```

Rg1LineVCompound(Shape=None) -> TopoShape

Sets the extraction filter for visible smooth edges for either shape Shape or
for all added shapes (Shape=None).

Evidence: public stub `Part/HLRBRep.pyi` line(s) 528.

## `Part.HLRBRep.PolyHLRToShape.RgNLineVCompound`

```python
def RgNLineVCompound(self, Shape: Optional[TopoShape]=None, /) -> TopoShape:
```

RgNLineVCompound(Shape=None) -> TopoShape

Sets the extraction filter for visible sewn edges for either shape Shape or for
all added shapes (Shape=None).

Evidence: public stub `Part/HLRBRep.pyi` line(s) 537.

## `Part.HLRBRep.PolyHLRToShape.outLineVCompound`

```python
def outLineVCompound(self, Shape: Optional[TopoShape]=None, /) -> TopoShape:
```

outLineVCompound(Shape=None) -> TopoShape

Sets the extraction filter for visible outline edges for either shape Shape or
for all added shapes (Shape=None).

Evidence: public stub `Part/HLRBRep.pyi` line(s) 546.

## `Part.HLRBRep.PolyHLRToShape.hCompound`

```python
def hCompound(self, Shape: Optional[TopoShape]=None, /) -> TopoShape:
```

hCompound(Shape=None) -> TopoShape

Sets the extraction filter for hidden sharp edges for either shape Shape or for
all added shapes (Shape=None).

Evidence: public stub `Part/HLRBRep.pyi` line(s) 555.

## `Part.HLRBRep.PolyHLRToShape.Rg1LineHCompound`

```python
def Rg1LineHCompound(self, Shape: Optional[TopoShape]=None, /) -> TopoShape:
```

Rg1LineHCompound(Shape=None) -> TopoShape

Sets the extraction filter for hidden smooth edges for either shape Shape or
for all added shapes (Shape=None).

Evidence: public stub `Part/HLRBRep.pyi` line(s) 564.

## `Part.HLRBRep.PolyHLRToShape.RgNLineHCompound`

```python
def RgNLineHCompound(self, Shape: Optional[TopoShape]=None, /) -> TopoShape:
```

RgNLineHCompound(Shape=None) -> TopoShape

Sets the extraction filter for hidden sewn edges for either shape Shape or for
all added shapes (Shape=None).

Evidence: public stub `Part/HLRBRep.pyi` line(s) 573.

## `Part.HLRBRep.PolyHLRToShape.outLineHCompound`

```python
def outLineHCompound(self, Shape: Optional[TopoShape]=None, /) -> TopoShape:
```

outLineHCompound(Shape=None) -> TopoShape

Sets the extraction filter for hidden outline edges for either shape Shape or
for all added shapes (Shape=None).

Evidence: public stub `Part/HLRBRep.pyi` line(s) 582.

