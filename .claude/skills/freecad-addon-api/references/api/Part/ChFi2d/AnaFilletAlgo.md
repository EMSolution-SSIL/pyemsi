# `Part.ChFi2d.AnaFilletAlgo`

[Module](index.md)

```python
class AnaFilletAlgo:
```

An analytical algorithm for calculation of the fillets.
It is implemented for segments and arcs of circle only.

Evidence: public stub `Part/ChFi2d.pyi` line 12. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.ChFi2d.AnaFilletAlgo.init`

```python
@overload
def init(self, wire: TopoShapeWire, plane: Plane, /) -> None:

@overload
def init(self, edge1: TopoShapeEdge, edge2: TopoShapeEdge, plane: Plane, /) -> None:

def init(self, *args) -> None:
```

Initializes a fillet algorithm: accepts a wire consisting of two edges in a plane

Evidence: public stub `Part/ChFi2d.pyi` line(s) 19, 23, 26.

## `Part.ChFi2d.AnaFilletAlgo.perform`

```python
def perform(self, radius: float, /) -> bool:
```

perform(radius) -> bool

Constructs a fillet edge

Evidence: public stub `Part/ChFi2d.pyi` line(s) 32.

## `Part.ChFi2d.AnaFilletAlgo.result`

```python
def result(self) -> Tuple[PyObjectBase, PyObjectBase, PyObjectBase]:
```

result()

Returns result (fillet edge, modified edge1, modified edge2)

Evidence: public stub `Part/ChFi2d.pyi` line(s) 40.

