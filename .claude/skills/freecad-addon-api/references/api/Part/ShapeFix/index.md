# `Part.ShapeFix`

[Catalogue index](../../index.md)

Evidence: import-shaped public stub `Part/ShapeFix.pyi`; generated binding/typing declarations, runtime unverified.

## Classes

- [Part.ShapeFix.Edge](Edge.md)
- [Part.ShapeFix.EdgeConnect](EdgeConnect.md)
- [Part.ShapeFix.Face](Face.md)
- [Part.ShapeFix.FaceConnect](FaceConnect.md)
- [Part.ShapeFix.FixSmallFace](FixSmallFace.md)
- [Part.ShapeFix.FixSmallSolid](FixSmallSolid.md)
- [Part.ShapeFix.FreeBounds](FreeBounds.md)
- [Part.ShapeFix.Root](Root.md)
- [Part.ShapeFix.ShapeTolerance](ShapeTolerance.md)
- [Part.ShapeFix.Shell](Shell.md)
- [Part.ShapeFix.Solid](Solid.md)
- [Part.ShapeFix.SplitCommonVertex](SplitCommonVertex.md)
- [Part.ShapeFix.SplitTool](SplitTool.md)
- [Part.ShapeFix.Wire](Wire.md)
- [Part.ShapeFix.WireVertex](WireVertex.md)
- [Part.ShapeFix.Wireframe](Wireframe.md)

## Imports and aliases

These preserve stub type context and reexports. Imported typing helpers and underscored names are not a promise of supported runtime API.

```python
from __future__ import annotations
from typing import Any
from Part import Shape
from typing import overload
from Part import Edge as TopoShapeEdge
from Part import Face as TopoShapeFace
from Part import GeometrySurface
from FreeCAD.Base import Placement
from Part import Shape as TopoShape
from typing import Union
from Part import Wire as TopoShapeWire
from Part import Shell as TopoShapeShell
from Part import Compound as TopoShapeCompound
from Part import Solid as TopoShapeSolid
from Part import Vertex as TopoShapeVertex
```

## `Part.ShapeFix.sameParameter`

```python
def sameParameter(shape: Shape, enforce: bool, prec: float=0.0, /) -> bool:
```

Recompute same-parameter consistency on one shape and report whether it succeeded.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 8.

## `Part.ShapeFix.encodeRegularity`

```python
def encodeRegularity(shape: Shape, tolerance: float=1e-10, /) -> None:
```

Encode one shape's edge regularity relationships using the given angular tolerance.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 12.

## `Part.ShapeFix.removeSmallEdges`

```python
def removeSmallEdges(shape: Shape, tolerance: float, /) -> Shape:
```

Return one copy of the shape with edges smaller than the given tolerance removed.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 16.

## `Part.ShapeFix.fixVertexPosition`

```python
def fixVertexPosition(shape: Shape, tolerance: float, /) -> bool:
```

Adjust vertex positions on one shape when their stored tolerances exceed the limit.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 20.

## `Part.ShapeFix.leastEdgeSize`

```python
def leastEdgeSize(shape: Shape, /) -> float:
```

Return the length of the smallest edge contained in one shape.

Evidence: public stub `Part/ShapeFix.pyi` line(s) 24.

