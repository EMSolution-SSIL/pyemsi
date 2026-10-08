# `Part.HLRBRep.HLRToShape`

[Module](index.md)

```python
class HLRToShape:
```

HLRToShape(algo: HLRBRep_Algo) -> HLRBRep_HLRToShape

A framework for filtering the computation results of an HLRBRep_Algo algorithm
by extraction. From the results calculated by the algorithm on a shape, a
filter returns the type of edge you want to identify. You can choose any of the
following types of output:
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
new computation of the algorithm, but only reads its internal results. The
methods of this shape are almost identic to those of the HLRBrep_PolyHLRToShape
class.

Evidence: public stub `Part/HLRBRep.pyi` line 330. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.HLRBRep.HLRToShape.__init__`

```python
@overload
def __init__(self, algo: Algo, /) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Evidence: public stub `Part/HLRBRep.pyi` line(s) 361.

## `Part.HLRBRep.HLRToShape.vCompound`

```python
def vCompound(self, shape: TopoShape=..., /) -> TopoShape:
```

vCompound(shape=None) -> TopoShape

Sets the extraction filter for visible sharp edges for either the given shape or
for all added shapes (shape=None).

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/HLRBRep.pyi` line(s) 364.

## `Part.HLRBRep.HLRToShape.Rg1LineVCompound`

```python
def Rg1LineVCompound(self, shape: TopoShape=..., /) -> TopoShape:
```

Rg1LineVCompound(shape=None) -> TopoShape

Sets the extraction filter for visible smooth edges for either the given shape or
for all added shapes (shape=None).

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/HLRBRep.pyi` line(s) 373.

## `Part.HLRBRep.HLRToShape.RgNLineVCompound`

```python
def RgNLineVCompound(self, shape: TopoShape=..., /) -> TopoShape:
```

RgNLineVCompound(shape=None) -> TopoShape

Sets the extraction filter for visible sewn edges for either the given shape or for
all added shapes (shape=None).

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/HLRBRep.pyi` line(s) 382.

## `Part.HLRBRep.HLRToShape.outLineVCompound`

```python
def outLineVCompound(self, shape: TopoShape=..., /) -> TopoShape:
```

outLineVCompound(shape=None) -> TopoShape

Sets the extraction filter for visible outline edges for either the given shape or
for all added shapes (shape=None).

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/HLRBRep.pyi` line(s) 391.

## `Part.HLRBRep.HLRToShape.outLineVCompound3d`

```python
def outLineVCompound3d(self) -> TopoShape:
```

outLineVCompound3d() -> TopoShape

Sets the extraction filter for visible outline edges in 3D for all added shapes.

Evidence: public stub `Part/HLRBRep.pyi` line(s) 400.

## `Part.HLRBRep.HLRToShape.isoLineVCompound`

```python
def isoLineVCompound(self, shape: TopoShape=..., /) -> TopoShape:
```

isoLineVCompound(shape=None) -> TopoShape

Sets the extraction filter for visible isoparameters for either the given shape or
for all added shapes (shape=None).

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/HLRBRep.pyi` line(s) 408.

## `Part.HLRBRep.HLRToShape.hCompound`

```python
def hCompound(self, shape: TopoShape=..., /) -> TopoShape:
```

hCompound(shape=None) -> TopoShape

Sets the extraction filter for hidden sharp edges for either the given shape or for
all added shapes (shape=None).

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/HLRBRep.pyi` line(s) 417.

## `Part.HLRBRep.HLRToShape.Rg1LineHCompound`

```python
def Rg1LineHCompound(self, shape: TopoShape=..., /) -> TopoShape:
```

Rg1LineHCompound(shape=None) -> TopoShape

Sets the extraction filter for hidden smooth edges for either the given shape or
for all added shapes (shape=None).

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/HLRBRep.pyi` line(s) 426.

## `Part.HLRBRep.HLRToShape.RgNLineHCompound`

```python
def RgNLineHCompound(self, shape: TopoShape=..., /) -> TopoShape:
```

RgNLineHCompound(shape=None) -> TopoShape

Sets the extraction filter for hidden sewn edges for either the given shape or for
all added shapes (shape=None).

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/HLRBRep.pyi` line(s) 435.

## `Part.HLRBRep.HLRToShape.outLineHCompound`

```python
def outLineHCompound(self, shape: TopoShape=..., /) -> TopoShape:
```

outLineHCompound(shape=None) -> TopoShape

Sets the extraction filter for hidden outline edges for either the given shape or
for all added shapes (shape=None).

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/HLRBRep.pyi` line(s) 444.

## `Part.HLRBRep.HLRToShape.isoLineHCompound`

```python
def isoLineHCompound(self, shape: TopoShape=..., /) -> TopoShape:
```

isoLineHCompound(shape=None) -> TopoShape

Sets the extraction filter for hidden isoparameters for either the given shape or
for all added shapes (shape=None).

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/HLRBRep.pyi` line(s) 453.

## `Part.HLRBRep.HLRToShape.compoundOfEdges`

```python
def compoundOfEdges(self, Type: int, Visible: bool, In3D: bool, Shape: Optional[TopoShape]=None) -> TopoShape:
```

compoundOfEdges(Type: int, Visible: bool, In3D: bool, Shape=None) -> TopoShape

Returns compound of resulting edges of required type and visibility, taking
into account the kind of space (2d or 3d).  If Shape=None, return it for all
added shapes, otherwise return it for shape Shape.

Evidence: public stub `Part/HLRBRep.pyi` line(s) 462.

