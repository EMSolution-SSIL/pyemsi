# `Part`

[Catalogue index](../index.md)

Evidence: import-shaped public stub `Part/__init__.pyi`; generated binding/typing declarations, runtime unverified.

## Classes

- [Part.Arc](Arc.md)
- [Part.ArcOfCircle](ArcOfCircle.md)
- [Part.ArcOfConic](ArcOfConic.md)
- [Part.ArcOfEllipse](ArcOfEllipse.md)
- [Part.ArcOfHyperbola](ArcOfHyperbola.md)
- [Part.ArcOfParabola](ArcOfParabola.md)
- [Part.AttachEngine](AttachEngine.md)
- [Part.AttachExtension](AttachExtension.md)
- [Part.BSplineCurve](BSplineCurve.md)
- [Part.BSplineSurface](BSplineSurface.md)
- [Part.BezierCurve](BezierCurve.md)
- [Part.BezierSurface](BezierSurface.md)
- [Part.BodyBase](BodyBase.md)
- [Part.BoundedCurve](BoundedCurve.md)
- [Part.Circle](Circle.md)
- [Part.Cone](Cone.md)
- [Part.Conic](Conic.md)
- [Part.Cylinder](Cylinder.md)
- [Part.Ellipse](Ellipse.md)
- [Part.Geometry](Geometry.md)
- [Part.GeometryBoolExtension](GeometryBoolExtension.md)
- [Part.Curve](Curve.md)
- [Part.GeometryDoubleExtension](GeometryDoubleExtension.md)
- [Part.GeometryExtension](GeometryExtension.md)
- [Part.GeometryIntExtension](GeometryIntExtension.md)
- [Part.GeometryStringExtension](GeometryStringExtension.md)
- [Part.GeometrySurface](GeometrySurface.md)
- [Part.Hyperbola](Hyperbola.md)
- [Part.Line](Line.md)
- [Part.LineSegment](LineSegment.md)
- [Part.OffsetCurve](OffsetCurve.md)
- [Part.OffsetSurface](OffsetSurface.md)
- [Part.Parabola](Parabola.md)
- [Part.Part2DObject](Part2DObject.md)
- [Part.Feature](Feature.md)
- [Part.Plane](Plane.md)
- [Part.PlateSurface](PlateSurface.md)
- [Part.Point](Point.md)
- [Part.PreviewExtension](PreviewExtension.md)
- [Part.RectangularTrimmedSurface](RectangularTrimmedSurface.md)
- [Part.Sphere](Sphere.md)
- [Part.SurfaceOfExtrusion](SurfaceOfExtrusion.md)
- [Part.SurfaceOfRevolution](SurfaceOfRevolution.md)
- [Part.Shape](Shape.md)
- [Part.CompSolid](CompSolid.md)
- [Part.Compound](Compound.md)
- [Part.Edge](Edge.md)
- [Part.Face](Face.md)
- [Part.Shell](Shell.md)
- [Part.Solid](Solid.md)
- [Part.Vertex](Vertex.md)
- [Part.Wire](Wire.md)
- [Part.Toroid](Toroid.md)
- [Part.TrimmedCurve](TrimmedCurve.md)

## Imports and aliases

These preserve stub type context and reexports. Imported typing helpers and underscored names are not a promise of supported runtime API.

```python
from __future__ import annotations
from typing import Any, overload
from typing_extensions import deprecated
from collections.abc import Sequence
from typing import Literal, TypeAlias, TypedDict
import Materials as Materials
from typing import overload
from FreeCAD.Base import Vector
from typing import Final
from FreeCAD.Base import BaseClass
from typing import Optional
from FreeCAD.Base import Placement
from FreeCAD import DocumentObject
from FreeCAD import DocumentObjectExtension
from typing import List
from typing import Tuple
from FreeCAD.Base import Axis as AxisPy
from FreeCAD.Base import Persistence
from FreeCAD import Extension
from FreeCAD.Base import Matrix
from typing import Union
from FreeCAD.Base import Rotation as RotationPy
from FreeCAD.Base import TypeId as Type
from FreeCAD import GeoFeature
from FreeCAD import ComplexGeoData
from FreeCAD.Base import BoundBox
from FreeCAD import StringHasher
from typing import Sequence
from typing import Dict
import Part
from FreeCAD.Base import Precision as Precision
```

## `Part.Point3`

```python
Point3: TypeAlias = tuple[float, float, float]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 9.

## `Part.ShapeSequence`

```python
ShapeSequence: TypeAlias = Sequence[Shape] | Shape
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 10.

## `Part.EdgeSequence`

```python
EdgeSequence: TypeAlias = Sequence[Edge]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 11.

## `Part.OCCError`

```python
OCCError: type[Exception]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 12.

## `Part.OCCDomainError`

```python
OCCDomainError: type[Exception]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 13.

## `Part.OCCRangeError`

```python
OCCRangeError: type[Exception]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 14.

## `Part.OCCConstructionError`

```python
OCCConstructionError: type[Exception]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 15.

## `Part.OCCDimensionError`

```python
OCCDimensionError: type[Exception]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 16.

## `Part._RevolutionShapeClass`

```python
_RevolutionShapeClass: TypeAlias = type[Shape]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 17.

## `Part._SingleShapeCompoundCreationPolicy`

```python
_SingleShapeCompoundCreationPolicy: TypeAlias = int
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 18.

## `Part._FilledSupportPairs`

```python
_FilledSupportPairs: TypeAlias = Sequence[tuple[Shape, Shape]]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 19.

## `Part._FilledOrderPairs`

```python
_FilledOrderPairs: TypeAlias = Sequence[tuple[Shape, int]]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 20.

## `Part.ExportUnits`

```python
ExportUnits = TypedDict('ExportUnits', {'write.iges.unit': str, 'write.step.unit': str})
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Evidence: public stub `Part/__init__.pyi` line(s) 21.

## `Part.open`

```python
@deprecated('since FreeCAD 26.3 and will be removed in FreeCAD 27.2; use Import.open instead.')
def open(name: str, /) -> None:
```

Open one Part-supported file into the active document context.

Evidence: public stub `Part/__init__.pyi` line(s) 25.

## `Part.insert`

```python
@deprecated('since FreeCAD 26.3 and will be removed in FreeCAD 27.2; use Import.insert instead.')
def insert(name: str, doc_name: str, /) -> None:
```

Insert one Part-supported file into an existing document.

Evidence: public stub `Part/__init__.pyi` line(s) 30.

## `Part.export`

```python
def export(objects: Sequence[DocumentObject], name: str, /) -> None:
```

Export document objects to one Part-supported file.

Evidence: public stub `Part/__init__.pyi` line(s) 34.

## `Part.read`

```python
def read(name: str, /) -> Shape:
```

Read one Part-supported file and return the resulting shape.

Evidence: public stub `Part/__init__.pyi` line(s) 38.

## `Part.show`

```python
def show(shape: Shape, name: str='Shape', /) -> Feature:
```

Create a document feature that shows one shape.

Evidence: public stub `Part/__init__.pyi` line(s) 42.

## `Part.getFacets`

```python
def getFacets(shape: Shape, /) -> list[tuple[Point3, Point3, Point3]]:
```

Return the triangulated facet vertices of one shape.

Evidence: public stub `Part/__init__.pyi` line(s) 46.

## `Part.makeCompound`

```python
def makeCompound(shapes: ShapeSequence, force: _SingleShapeCompoundCreationPolicy=..., op: str | None=None) -> Compound:
```

Build a compound from one shape or a shape sequence.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 50.

## `Part.makeShell`

```python
def makeShell(shapes: ShapeSequence, op: str | None=None) -> Shell:
```

Build a shell from one shape or a shape sequence.

Evidence: public stub `Part/__init__.pyi` line(s) 54.

## `Part.makeFace`

```python
def makeFace(shapes: ShapeSequence, class_name: str | None=None, op: str | None=None, *, noElementMap: bool=False) -> Face:
```

Build a face from one shape or a compatible shape sequence.

Evidence: public stub `Part/__init__.pyi` line(s) 58.

## `Part.makeFilledSurface`

```python
def makeFilledSurface(shapes: ShapeSequence, surface: Shape | None=None, supports: _FilledSupportPairs | None=None, orders: _FilledOrderPairs | None=None, degree: int=..., ptsOnCurve: int=..., numIter: int=..., anisotropy: bool=..., tol2d: float=..., tol3d: float=..., tolG1: float=..., tolG2: float=..., maxDegree: int=..., maxSegments: int=..., op: str | None=None) -> Face:
```

Build a filled surface face from boundary shapes and optional supports.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 62.

## `Part.makeFilledFace`

```python
def makeFilledFace(shapes: ShapeSequence, surface: Shape | None=None, supports: _FilledSupportPairs | None=None, orders: _FilledOrderPairs | None=None, degree: int=..., ptsOnCurve: int=..., numIter: int=..., anisotropy: bool=..., tol2d: float=..., tol3d: float=..., tolG1: float=..., tolG2: float=..., maxDegree: int=..., maxSegments: int=..., op: str | None=None) -> Face:
```

Build a filled face from boundary shapes and optional supports.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 66.

## `Part.makeSolid`

```python
def makeSolid(shape: Shape, op: str | None=None) -> Solid:
```

Convert one shell-like shape into a solid.

Evidence: public stub `Part/__init__.pyi` line(s) 70.

## `Part.makePlane`

```python
def makePlane(length: float, width: float, pPnt: Vector | None=None, pDirZ: Vector | None=None, pDirX: Vector | None=None, /) -> Face:
```

Create a planar face from dimensions and optional orientation vectors.

Evidence: public stub `Part/__init__.pyi` line(s) 74.

## `Part.makeBox`

```python
def makeBox(length: float, width: float, height: float, pPnt: Vector | None=None, pDir: Vector | None=None, /) -> Solid:
```

Create a box solid from dimensions and optional placement.

Evidence: public stub `Part/__init__.pyi` line(s) 78.

## `Part.makeWedge`

```python
def makeWedge(xmin: float, ymin: float, zmin: float, z2min: float, x2min: float, xmax: float, ymax: float, zmax: float, z2max: float, x2max: float, pPnt: Vector | None=None, pDir: Vector | None=None, /) -> Solid:
```

Create a wedge solid from the OCC wedge parameters.

Evidence: public stub `Part/__init__.pyi` line(s) 82.

## `Part.makeLine`

```python
def makeLine(obj1: Vector | Point3, obj2: Vector | Point3, /) -> Edge:
```

Create a line edge between two points.

Evidence: public stub `Part/__init__.pyi` line(s) 86.

## `Part.makePolygon`

```python
def makePolygon(pcObj: Sequence[Vector | Point3], pclosed: bool=False, /) -> Wire:
```

Create a polygon wire from a point sequence.

Evidence: public stub `Part/__init__.pyi` line(s) 90.

## `Part.makeCircle`

```python
def makeCircle(radius: float, pPnt: Vector | None=None, pDir: Vector | None=None, angle1: float=0.0, angle2: float=360, /) -> Edge:
```

Create a circular edge or arc.

Evidence: public stub `Part/__init__.pyi` line(s) 94.

## `Part.makeSphere`

```python
def makeSphere(radius: float, pPnt: Vector | None=None, pDir: Vector | None=None, angle1: float=-90, angle2: float=90, angle3: float=360, /) -> Solid:
```

Create a sphere solid or spherical segment.

Evidence: public stub `Part/__init__.pyi` line(s) 98.

## `Part.makeCylinder`

```python
def makeCylinder(radius: float, height: float, pPnt: Vector | None=None, pDir: Vector | None=None, angle: float=360, /) -> Solid:
```

Create a cylinder solid or cylindrical segment.

Evidence: public stub `Part/__init__.pyi` line(s) 102.

## `Part.makeCone`

```python
def makeCone(radius1: float, radius2: float, height: float, pPnt: Vector | None=None, pDir: Vector | None=None, angle: float=360, /) -> Solid:
```

Create a cone or frustum solid.

Evidence: public stub `Part/__init__.pyi` line(s) 106.

## `Part.makeTorus`

```python
def makeTorus(radius1: float, radius2: float, pPnt: Vector | None=None, pDir: Vector | None=None, angle1: float=0.0, angle2: float=360, angle: float=360, /) -> Solid:
```

Create a torus solid or toroidal segment.

Evidence: public stub `Part/__init__.pyi` line(s) 110.

## `Part.makeHelix`

```python
def makeHelix(pitch: float, height: float, radius: float, angle: float=-1.0, pleft: bool=False, pvertHeight: bool=False, /) -> Wire:
```

Create a helix wire.

Evidence: public stub `Part/__init__.pyi` line(s) 114.

## `Part.makeLongHelix`

```python
def makeLongHelix(pitch: float, height: float, radius: float, angle: float=-1.0, pleft: bool=False, /) -> Wire:
```

Create a long helix wire using the extended implementation.

Evidence: public stub `Part/__init__.pyi` line(s) 118.

## `Part.makeThread`

```python
def makeThread(pitch: float, depth: float, height: float, radius: float, /) -> Wire:
```

Create a thread-profile wire.

Evidence: public stub `Part/__init__.pyi` line(s) 122.

## `Part.makeRevolution`

```python
@overload
def makeRevolution(curve: Geometry, vmin: float=..., vmax: float=..., angle: float=360, point: Vector | None=None, direction: Vector | None=None, type: _RevolutionShapeClass | None=None, /) -> Shape:

@overload
def makeRevolution(edge: Edge, vmin: float=..., vmax: float=..., angle: float=360, point: Vector | None=None, direction: Vector | None=None, type: _RevolutionShapeClass | None=None, /) -> Shape:
```

Revolve a curve geometry into a shape, optionally choosing the result class.

Revolve an edge into a shape, optionally choosing the result class.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 127, 132.

## `Part.makeRuledSurface`

```python
def makeRuledSurface(path: Edge | Wire, profile: Edge | Wire, orientation: int=0, op: str | None=None) -> Face | Shell:
```

Create a ruled surface between two path shapes.

Evidence: public stub `Part/__init__.pyi` line(s) 136.

## `Part.makeShellFromWires`

```python
def makeShellFromWires(shape: ShapeSequence, op: str | None=None) -> Shell:
```

Create a shell from a compatible wire sequence.

Evidence: public stub `Part/__init__.pyi` line(s) 140.

## `Part.makeLoft`

```python
def makeLoft(shapes: list[Shape], solid: bool=False, ruled: bool=False, closed: bool=False, max_degree: int=5, op: str | None=None) -> Shape:
```

Loft a sequence of section shapes into a new shape.

Evidence: public stub `Part/__init__.pyi` line(s) 144.

## `Part.makeTube`

```python
def makeTube(pshape: Shape, radius: float, scont: str='C0', maxdegree: int=3, maxsegment: int=30, /) -> Face:
```

Create a tube surface around one path shape.

Evidence: public stub `Part/__init__.pyi` line(s) 148.

## `Part.makeSweepSurface`

```python
def makeSweepSurface(path: Shape, profile: Shape, tolerance: float=0.001, fillMode: int=0, /) -> Shape:
```

Sweep one profile along one path and return the resulting shape.

Evidence: public stub `Part/__init__.pyi` line(s) 152.

## `Part.makeWireString`

```python
@overload
def makeWireString(intext: str | bytes, dir: str, fontfile: str, height: float, track: float=0, /) -> list[list[Wire]]:

@overload
def makeWireString(intext: str | bytes, fontspec: str, height: float, track: float=0, /) -> list[list[Wire]]:
```

Use the legacy ``(text, fontdir, fontfile, ...)`` calling convention.

Use the newer ``(text, fontspec, ...)`` calling convention.

Evidence: public stub `Part/__init__.pyi` line(s) 157, 162.

## `Part.makeSplitShape`

```python
def makeSplitShape(shape: Shape, splits: Sequence[tuple[Shape, Shape]], checkInterior: bool=True, /) -> tuple[list[Shape], list[Shape]]:
```

Split a shape by splitter pairs and return outside and inside fragments.

Evidence: public stub `Part/__init__.pyi` line(s) 166.

## `Part.exportUnits`

```python
def exportUnits(unit: str | None=None, /) -> ExportUnits:
```

Return the current Part export-unit configuration.

Evidence: public stub `Part/__init__.pyi` line(s) 170.

## `Part.setStaticValue`

```python
@overload
def setStaticValue(name: str, cval: str, /) -> None:

@overload
def setStaticValue(name: str, value: int | float, /) -> None:
```

Set an OCC interface static from a string value.

Set an OCC interface static from an integer or floating-point value.

Evidence: public stub `Part/__init__.pyi` line(s) 175, 180.

## `Part.cast_to_shape`

```python
def cast_to_shape(shape: Shape, /) -> Shape:
```

Normalize a shape-like proxy to the public `Shape` wrapper.

Evidence: public stub `Part/__init__.pyi` line(s) 184.

## `Part.getSortedClusters`

```python
def getSortedClusters(obj: EdgeSequence, /) -> list[list[Edge]]:
```

Group edges into connected clusters.

Evidence: public stub `Part/__init__.pyi` line(s) 188.

## `Part.__sortEdges__`

```python
def __sortEdges__(obj: EdgeSequence, /) -> list[Edge]:
```

Return one legacy sorted edge sequence.

Evidence: public stub `Part/__init__.pyi` line(s) 192.

## `Part.sortEdges`

```python
def sortEdges(obj: EdgeSequence, tol3d: float | None=None, /) -> list[list[Edge]]:
```

Group and order connected edges with an optional tolerance override.

Evidence: public stub `Part/__init__.pyi` line(s) 196.

## `Part.__toPythonOCC__`

```python
def __toPythonOCC__(shape: Shape, /) -> object:
```

Convert one Part shape to a PythonOCC proxy object.

Evidence: public stub `Part/__init__.pyi` line(s) 200.

## `Part.__fromPythonOCC__`

```python
def __fromPythonOCC__(proxy: object, /) -> Shape:
```

Convert one PythonOCC proxy object to a Part shape.

Evidence: public stub `Part/__init__.pyi` line(s) 204.

## `Part.clearShapeCache`

```python
def clearShapeCache() -> None:
```

Clear the process-wide Part shape conversion cache.

Evidence: public stub `Part/__init__.pyi` line(s) 208.

## `Part.getShape`

```python
@overload
def getShape(obj: DocumentObject, subname: str | None=None, mat: Matrix | None=None, needSubElement: bool=False, transform: bool=True, retType: Literal[0]=0, noElementMap: bool=False, refine: bool=False) -> Shape:

@overload
def getShape(obj: DocumentObject, subname: str | None, mat: Matrix | None, needSubElement: bool, transform: bool, retType: Literal[1, 2], noElementMap: bool=False, refine: bool=False) -> tuple[Shape, Matrix, DocumentObject | None]:

@overload
def getShape(obj: DocumentObject, subname: str | None=None, mat: Matrix | None=None, needSubElement: bool=False, transform: bool=True, retType: int=0, noElementMap: bool=False, refine: bool=False) -> Shape | tuple[Shape, Matrix, DocumentObject | None]:
```

Return only the resolved shape.

Return the shape together with placement and resolved subobject context.

Accept any retType and reflect the broad union used at runtime.

Evidence: public stub `Part/__init__.pyi` line(s) 213, 218, 223.

## `Part.splitSubname`

```python
def splitSubname(subname: str, /) -> list[str]:
```

Split one mapped subname string into its path components.

Evidence: public stub `Part/__init__.pyi` line(s) 227.

## `Part.joinSubname`

```python
def joinSubname(sub: str, mapped: str, element: str, /) -> str:
```

Join mapped subname components into one canonical string.

Evidence: public stub `Part/__init__.pyi` line(s) 231.

