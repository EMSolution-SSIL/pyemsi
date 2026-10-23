# `Part.Edge`

[Module](index.md)

```python
class Edge(Shape):
```

TopoShapeEdge is the OpenCasCade topological edge wrapper

Author: Juergen Riegel (Juergen.Riegel@web.de)
Licence: LGPL

Evidence: public stub `Part/__init__.pyi` line 4500. Inherited members are on the named base's reference; aliases keep their imported identity.

[part 1](Edge.md) | [part 2](Edge-2.md)

## `Part.Edge.curveOnSurface`

```python
def curveOnSurface(self, idx: int, /) -> Tuple[object, object, object, float, float] | None:
```

Returns the 2D curve, the surface, the placement and the parameter range of index idx.
curveOnSurface(idx) -> None or tuple
--
Returns None if index idx is out of range.
Returns a 5-items tuple of a curve, a surface, a placement, first parameter and last parameter.

Evidence: public stub `Part/__init__.pyi` line(s) 4938.

