# `TechDraw`

[Catalogue index](../index.md)

Evidence: import-shaped public stub `TechDraw/__init__.pyi`; generated binding/typing declarations, runtime unverified.

## Classes

- [TechDraw.CenterLine](CenterLine.md)
- [TechDraw.CosmeticEdge](CosmeticEdge.md)
- [TechDraw.CosmeticExtension](CosmeticExtension.md)
- [TechDraw.CosmeticVertex](CosmeticVertex.md)
- [TechDraw.DrawBrokenView](DrawBrokenView.md)
- [TechDraw.DrawGeomHatch](DrawGeomHatch.md)
- [TechDraw.DrawHatch](DrawHatch.md)
- [TechDraw.DrawLeaderLine](DrawLeaderLine.md)
- [TechDraw.DrawPage](DrawPage.md)
- [TechDraw.DrawParametricTemplate](DrawParametricTemplate.md)
- [TechDraw.DrawProjGroup](DrawProjGroup.md)
- [TechDraw.DrawProjGroupItem](DrawProjGroupItem.md)
- [TechDraw.DrawRichAnno](DrawRichAnno.md)
- [TechDraw.DrawSVGTemplate](DrawSVGTemplate.md)
- [TechDraw.DrawTemplate](DrawTemplate.md)
- [TechDraw.DrawTile](DrawTile.md)
- [TechDraw.DrawTileWeld](DrawTileWeld.md)
- [TechDraw.DrawView](DrawView.md)
- [TechDraw.DrawViewAnnotation](DrawViewAnnotation.md)
- [TechDraw.DrawViewClip](DrawViewClip.md)
- [TechDraw.DrawViewCollection](DrawViewCollection.md)
- [TechDraw.DrawViewDimExtent](DrawViewDimExtent.md)
- [TechDraw.DrawViewDimension](DrawViewDimension.md)
- [TechDraw.DrawViewPart](DrawViewPart.md)
- [TechDraw.DrawViewSymbol](DrawViewSymbol.md)
- [TechDraw.DrawWeldSymbol](DrawWeldSymbol.md)
- [TechDraw.GeomFormat](GeomFormat.md)

## Imports and aliases

These preserve stub type context and reexports. Imported typing helpers and underscored names are not a promise of supported runtime API.

```python
from __future__ import annotations
from typing import Any, overload
from collections.abc import Mapping, Sequence
from typing import Literal, TypeAlias
from FreeCAD.Base import Vector
from Part import Compound, Edge, Face, Shape, Wire
from FreeCAD import Base as Base
import Part as Part
from typing import Final
from FreeCAD import DocumentObjectExtension
from FreeCAD import DocumentObject
from Part import Edge as TopoShapeEdge
from Part import Vertex as TopoShapeVertex
```

## `TechDraw._ExtentDirection`

```python
_ExtentDirection: TypeAlias = Literal[0, 1]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 10.

## `TechDraw._ProjectionSvgStyle`

```python
_ProjectionSvgStyle: TypeAlias = Mapping[str, str]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 11.

## `TechDraw._ProjectedParts`

```python
_ProjectedParts: TypeAlias = tuple[Shape, Shape, Shape, Shape]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 12.

## `TechDraw._ProjectedPartsEx`

```python
_ProjectedPartsEx: TypeAlias = tuple[Shape, Shape, Shape, Shape, Shape, Shape, Shape, Shape, Shape, Shape]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 13.

## `TechDraw.edgeWalker`

```python
def edgeWalker(edgePile: Sequence[Edge], inclBiggest: bool=True, /) -> list[Wire] | None:
```

Partition one edge pile into one or more planar wires.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 17.

## `TechDraw.findOuterWire`

```python
def findOuterWire(edgeList: Sequence[Edge], /) -> Wire | None:
```

Return the outer wire detected in one planar edge pile.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 21.

## `TechDraw.findShapeOutline`

```python
def findShapeOutline(shape: Shape, scale: float, direction: Vector, /) -> Wire | None:
```

Project one shape and return the outer wire of the resulting outline.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 25.

## `TechDraw.viewPartAsDxf`

```python
def viewPartAsDxf(view: DrawViewPart, /) -> str:
```

Return the projected edges of one view part as DXF text.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 29.

## `TechDraw.viewPartAsSvg`

```python
def viewPartAsSvg(view: DrawViewPart, /) -> str:
```

Return the projected edges of one view part as SVG markup.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 33.

## `TechDraw.writeDXFView`

```python
def writeDXFView(view: DrawViewPart, filename: str, alignPage: bool=True, /) -> None:
```

Export one view part directly to one DXF file.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 37.

## `TechDraw.writeDXFPage`

```python
def writeDXFPage(page: DrawPage, filename: str, /) -> None:
```

Export one TechDraw page and its supported child views to one DXF file.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 41.

## `TechDraw.findCentroid`

```python
def findCentroid(shape: Shape, direction: Vector, /) -> Vector | None:
```

Return the projected geometric centroid of one shape in one view direction.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 45.

## `TechDraw.makeExtentDim`

```python
def makeExtentDim(view: DrawViewPart, edges: Sequence[str], direction: _ExtentDirection | int, /) -> DrawViewDimension | None:
```

Create one horizontal or vertical extent dimension on a view part.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 49.

## `TechDraw.makeDistanceDim`

```python
def makeDistanceDim(view: DrawViewPart, dimType: str, fromPoint: Vector, toPoint: Vector, /) -> DrawViewDimension:
```

Create one 2D distance dimension between two view-space points.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 53.

## `TechDraw.makeDistanceDim3d`

```python
def makeDistanceDim3d(view: DrawViewPart, dimType: str, fromPoint: Vector, toPoint: Vector, /) -> None:
```

Create one distance dimension from two 3D model-space points.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 57.

## `TechDraw.makeGeomHatch`

```python
def makeGeomHatch(face: Face, scale: float=1.0, patName: str='', patFile: str='', /) -> Compound | None:
```

Create a compound of hatch edges trimmed to one face.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 61.

## `TechDraw.project`

```python
@overload
def project(shape: Shape, /) -> _ProjectedParts:

@overload
def project(shape: Shape, direction: Vector, /) -> _ProjectedParts:
```

Project one shape with the default direction and return four result classes.

Project one shape in one explicit direction and return four result classes.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 66, 71.

## `TechDraw.projectEx`

```python
@overload
def projectEx(shape: Shape, /) -> _ProjectedPartsEx:

@overload
def projectEx(shape: Shape, direction: Vector, /) -> _ProjectedPartsEx:
```

Project one shape with the default direction and return ten result classes.

Project one shape in one explicit direction and return ten result classes.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 76, 81.

## `TechDraw.projectToSVG`

```python
def projectToSVG(topoShape: Shape, direction: Vector | None=None, type: str | None=None, tolerance: float=0.1, vStyle: _ProjectionSvgStyle | None=None, v0Style: _ProjectionSvgStyle | None=None, v1Style: _ProjectionSvgStyle | None=None, hStyle: _ProjectionSvgStyle | None=None, h0Style: _ProjectionSvgStyle | None=None, h1Style: _ProjectionSvgStyle | None=None) -> str:
```

Project one shape and return its SVG representation.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 85.

## `TechDraw.projectToDXF`

```python
def projectToDXF(topoShape: Shape, direction: Vector | None=None, type: str | None=None, scale: float=1.0, tolerance: float=0.1, /) -> str:
```

Project one shape and return its DXF representation.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 89.

## `TechDraw.removeSvgTags`

```python
def removeSvgTags(svgcode: str, /) -> str:
```

Strip outer SVG and metadata tags from one SVG fragment.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 93.

## `TechDraw.exportSVGEdges`

```python
def exportSVGEdges(topoShape: Shape, /) -> str:
```

Export one shape's edges as SVG path content.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 97.

## `TechDraw.build3dCurves`

```python
def build3dCurves(topoShape: Shape, /) -> Shape:
```

Rebuild 3D curves on one shape and return the updated shape.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 101.

## `TechDraw.makeCanonicalPoint`

```python
def makeCanonicalPoint(view: DrawViewPart, point: Vector, unscale: bool=True, /) -> Vector | None:
```

Convert one point into the canonical unrotated TechDraw view-space location.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 105.

## `TechDraw.makeLeader`

```python
def makeLeader(parent: DrawViewPart, points: Sequence[Vector], startSymbol: int=0, endSymbol: int=0, /) -> DrawLeaderLine:
```

Create one leader line attached to a view part from page-space points.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 109.

## `TechDraw.nearestFraction`

```python
def nearestFraction(valueWithDecimals: float, /) -> tuple[int, int]:
```

Return the nearest numerator and denominator pair for one decimal value.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 113.

## `TechDraw.scrubEdges`

```python
def scrubEdges(*args: Any) -> Any:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 117.

