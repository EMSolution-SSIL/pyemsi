# `TechDraw.DrawViewPart`

[Module](index.md)

```python
class DrawViewPart(DrawView):
```

Feature for creating and manipulating Technical Drawing Part Views

Author: WandererFan (wandererfan@gmail.com)
License: LGPL-2.1-or-later

Evidence: public stub `TechDraw/__init__.pyi` line 1480. Inherited members are on the named base's reference; aliases keep their imported identity.

## `TechDraw.DrawViewPart.CoarseView`

```python
@property
def CoarseView(self) -> bool:

@CoarseView.setter
def CoarseView(self, value: bool | int) -> None:
```

Coarse View on/off

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1489, 1494.

## `TechDraw.DrawViewPart.Direction`

```python
@property
def Direction(self) -> Base.Vector:

@Direction.setter
def Direction(self, value: Base.Vector | tuple[float, float, float]) -> None:
```

Projection Plane normal. View direction for the projection plane

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1498, 1503.

## `TechDraw.DrawViewPart.Focus`

```python
@property
def Focus(self) -> Base.Quantity:

@Focus.setter
def Focus(self, value: float | str | Base.Quantity | Base.Unit) -> None:
```

Perspective view focus distance

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1507, 1512.

## `TechDraw.DrawViewPart.HardHidden`

```python
@property
def HardHidden(self) -> bool:

@HardHidden.setter
def HardHidden(self, value: bool | int) -> None:
```

Show Hidden Hard lines

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1516, 1521.

## `TechDraw.DrawViewPart.IsoCount`

```python
@property
def IsoCount(self) -> int:

@IsoCount.setter
def IsoCount(self, value: int) -> None:
```

Number of iso parameters lines

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1525, 1530.

## `TechDraw.DrawViewPart.IsoHidden`

```python
@property
def IsoHidden(self) -> bool:

@IsoHidden.setter
def IsoHidden(self, value: bool | int) -> None:
```

Show Hidden Iso u, v lines

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1534, 1539.

## `TechDraw.DrawViewPart.IsoVisible`

```python
@property
def IsoVisible(self) -> bool:

@IsoVisible.setter
def IsoVisible(self, value: bool | int) -> None:
```

Show Visible Iso u, v lines

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1543, 1548.

## `TechDraw.DrawViewPart.Perspective`

```python
@property
def Perspective(self) -> bool:

@Perspective.setter
def Perspective(self, value: bool | int) -> None:
```

Perspective(true) or Orthographic(false) projection

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1552, 1557.

## `TechDraw.DrawViewPart.ScrubCount`

```python
@property
def ScrubCount(self) -> int:

@ScrubCount.setter
def ScrubCount(self, value: int) -> None:
```

The number of times FreeCAD should try to clean the HLR result.

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1561, 1566.

## `TechDraw.DrawViewPart.SeamHidden`

```python
@property
def SeamHidden(self) -> bool:

@SeamHidden.setter
def SeamHidden(self, value: bool | int) -> None:
```

Show Hidden Seam lines

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1570, 1575.

## `TechDraw.DrawViewPart.SeamVisible`

```python
@property
def SeamVisible(self) -> bool:

@SeamVisible.setter
def SeamVisible(self, value: bool | int) -> None:
```

Show Visible Seam lines

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1579, 1584.

## `TechDraw.DrawViewPart.SmoothHidden`

```python
@property
def SmoothHidden(self) -> bool:

@SmoothHidden.setter
def SmoothHidden(self, value: bool | int) -> None:
```

Show Hidden Smooth lines

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1588, 1593.

## `TechDraw.DrawViewPart.SmoothVisible`

```python
@property
def SmoothVisible(self) -> bool:

@SmoothVisible.setter
def SmoothVisible(self, value: bool | int) -> None:
```

Show Visible Smooth lines

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1597, 1602.

## `TechDraw.DrawViewPart.Source`

```python
@property
def Source(self) -> list[DocumentObject | None]:

@Source.setter
def Source(self, value: Sequence[DocumentObject]) -> None:
```

3D Shape to view

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1606, 1611.

## `TechDraw.DrawViewPart.XDirection`

```python
@property
def XDirection(self) -> Base.Vector:

@XDirection.setter
def XDirection(self, value: Base.Vector | tuple[float, float, float]) -> None:
```

Projection Plane X Axis in R3. Rotates/Mirrors View

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1615, 1620.

## `TechDraw.DrawViewPart.XSource`

```python
@property
def XSource(self) -> _DocumentObjectList | _DocumentObjectSubLinkList:

@XSource.setter
def XSource(self, value: _DocumentObjectListInput | _DocumentObjectSubLinkListInput) -> None:
```

External 3D Shape to view

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1624, 1629.

## `TechDraw.DrawViewPart.getVisibleEdges`

```python
def getVisibleEdges(self, conventional_coords: bool=False, /) -> Any:
```

getVisibleEdges([conventionalCoords]) - get the visible edges in the View as Part::TopoShapeEdges. Edges are returned
in conventional coordinates if conventionalCoords is True.  The default is to return Qt inverted Y coordinates.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1632.

## `TechDraw.DrawViewPart.getVisibleVertexes`

```python
def getVisibleVertexes(self, conventional_coords: bool=False, /) -> Any:
```

getVisibleVertexes() - get the visible vertexes as App.Vector in the View's coordinate system.  App.Vectors are returned
in conventional coordinates if conventionalCoords is True.  The default is to return Qt inverted Y coordinates.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1639.

## `TechDraw.DrawViewPart.getHiddenEdges`

```python
def getHiddenEdges(self, conventional_coords: bool=False, /) -> Any:
```

getHiddenEdges([conventionalCoords]) - get the hidden edges in the View as Part::TopoShapeEdges.  Edges are returned
in conventional coordinates if conventionalCoords is True.  The default is to return Qt inverted Y coordinates.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1646.

## `TechDraw.DrawViewPart.getHiddenVertexes`

```python
def getHiddenVertexes(self, conventional_coords: bool=False, /) -> Any:
```

getHiddenVertexes() - get the hidden vertexes as App.Vector in the View's coordinate system.  App.Vectors are returned
in conventional coordinates if conventionalCoords is True.  The default is to return Qt inverted Y coordinates.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1653.

## `TechDraw.DrawViewPart.makeCosmeticVertex`

```python
def makeCosmeticVertex(self, point: Vector, /) -> str | None:
```

id = makeCosmeticVertex(p1) - add a CosmeticVertex at p1 (View coordinates). Returns unique id vertex.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1660.

## `TechDraw.DrawViewPart.makeCosmeticVertex3d`

```python
def makeCosmeticVertex3d(self, point: Vector, /) -> str | None:
```

id = makeCosmeticVertex3d(p1) - add a CosmeticVertex at p1 (3d model coordinates). Returns unique id vertex.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1664.

## `TechDraw.DrawViewPart.getCosmeticVertex`

```python
def getCosmeticVertex(self, tag: str, /) -> CosmeticVertex | None:
```

cv = getCosmeticVertex(id) - returns CosmeticVertex with unique id.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1668.

## `TechDraw.DrawViewPart.getCosmeticVertexBySelection`

```python
def getCosmeticVertexBySelection(self, selection_name: str, /) -> CosmeticVertex | None:
```

cv = getCosmeticVertexBySelection(name) - returns CosmeticVertex with name (Vertex6).  Used in selections.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1672.

## `TechDraw.DrawViewPart.removeCosmeticVertex`

```python
def removeCosmeticVertex(self, cv: str | CosmeticVertex | list[CosmeticVertex], /) -> None:
```

removeCosmeticVertex(cv) - remove CosmeticVertex from View. Returns None.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1676.

## `TechDraw.DrawViewPart.clearCosmeticVertices`

```python
def clearCosmeticVertices(self) -> Any:
```

clearCosmeticVertices() - remove all CosmeticVertices from the View. Returns None.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1680.

## `TechDraw.DrawViewPart.makeCosmeticLine`

```python
def makeCosmeticLine(self, point1: Vector, point2: Vector, style: int=..., weight: float=..., color: tuple=..., /) -> str | None:
```

tag = makeCosmeticLine(p1, p2) - add a CosmeticEdge from p1 to p2(View coordinates). Returns tag of new CosmeticEdge.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1684.

## `TechDraw.DrawViewPart.makeCosmeticLine3D`

```python
def makeCosmeticLine3D(self, point1: Vector, point2: Vector, style: int=..., weight: float=..., color: tuple=..., /) -> str | None:
```

tag = makeCosmeticLine3D(p1, p2) - add a CosmeticEdge from p1 to p2(3D coordinates). Returns tag of new CosmeticEdge.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1688.

## `TechDraw.DrawViewPart.makeCosmeticCircle`

```python
def makeCosmeticCircle(self, point: Vector, radius: float, style: int=..., weight: float=..., color: tuple=..., /) -> str | None:
```

tag = makeCosmeticCircle(center, radius) - add a CosmeticEdge at center with radius radius(View coordinates). Returns tag of new CosmeticEdge.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1692.

## `TechDraw.DrawViewPart.makeCosmeticCircleArc`

```python
def makeCosmeticCircleArc(self, point: Vector, radius: float, angle1: float, angle2: float, style: int=..., weight: float=..., color: tuple=..., /) -> str | None:
```

tag = makeCosmeticCircleArc(center, radius, start, end) - add a CosmeticEdge at center with radius radius(View coordinates) from start angle to end angle. Returns tag of new CosmeticEdge.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1696.

## `TechDraw.DrawViewPart.makeCosmeticCircle3d`

```python
def makeCosmeticCircle3d(self, point: Vector, radius: float, style: int=..., weight: float=..., color: tuple=..., /) -> str | None:
```

tag = makeCosmeticCircle3d(center, radius) - add a CosmeticEdge at center (3d point) with radius. Returns tag of new CosmeticEdge.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1700.

## `TechDraw.DrawViewPart.makeCosmeticCircleArc3d`

```python
def makeCosmeticCircleArc3d(self, point: Vector, radius: float, angle1: float, angle2: float, style: int=..., weight: float=..., color: tuple=..., /) -> str | None:
```

tag = makeCosmeticCircleArc3d(center, radius, start, end) - add a CosmeticEdge at center (3d point) with radius from start angle to end angle. Returns tag of new CosmeticEdge.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1704.

## `TechDraw.DrawViewPart.getCosmeticEdge`

```python
def getCosmeticEdge(self, tag: str, /) -> CosmeticEdge:
```

ce = getCosmeticEdge(id) - returns CosmeticEdge with unique id.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1708.

## `TechDraw.DrawViewPart.getCosmeticEdgeBySelection`

```python
def getCosmeticEdgeBySelection(self, selection_name: str, /) -> CosmeticEdge:
```

ce = getCosmeticEdgeBySelection(name) - returns CosmeticEdge by name (Edge25).  Used in selections

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1712.

## `TechDraw.DrawViewPart.removeCosmeticEdge`

```python
def removeCosmeticEdge(self, tag: str, /) -> None:
```

removeCosmeticEdge(ce) - remove CosmeticEdge ce from View. Returns None.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1716.

## `TechDraw.DrawViewPart.makeCenterLine`

```python
def makeCenterLine(self, sub_elements: list[str], mode: int, /) -> str | None:
```

makeCenterLine(subNames, mode) - draw a center line on this viewPart. SubNames is a list of n Faces, 2 Edges or 2 Vertices (ex [Face1,Face2,Face3]. Returns unique tag of added CenterLine.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1720.

## `TechDraw.DrawViewPart.getCenterLine`

```python
def getCenterLine(self, tag: str, /) -> CenterLine:
```

cl = getCenterLine(id) - returns CenterLine with unique id.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1724.

## `TechDraw.DrawViewPart.getCenterLineBySelection`

```python
def getCenterLineBySelection(self, selection_name: str, /) -> CenterLine:
```

cl = getCenterLineBySelection(name) - returns CenterLine by name (Edge25).  Used in selections

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1728.

## `TechDraw.DrawViewPart.removeCenterLine`

```python
def removeCenterLine(self, tag: str, /) -> None:
```

removeCenterLine(cl) - remove CenterLine cl from View. Returns None.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1732.

## `TechDraw.DrawViewPart.clearCosmeticEdges`

```python
def clearCosmeticEdges(self) -> Any:
```

clearCosmeticEdges() - remove all CosmeticLines from the View. Returns None.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1736.

## `TechDraw.DrawViewPart.clearCenterLines`

```python
def clearCenterLines(self) -> Any:
```

clearCenterLines() - remove all CenterLines from the View. Returns None.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1740.

## `TechDraw.DrawViewPart.clearGeomFormats`

```python
def clearGeomFormats(self) -> Any:
```

clearGeomFormats() - remove all GeomFormats from the View. Returns None.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1744.

## `TechDraw.DrawViewPart.formatGeometricEdge`

```python
def formatGeometricEdge(self, index: int, style: int, weight: float, color: tuple, visible: int, /) -> None:
```

formatGeometricEdge(index, style, weight, color, visible). Returns None.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1748.

## `TechDraw.DrawViewPart.getEdgeByIndex`

```python
def getEdgeByIndex(self, index: int, /) -> TopoShapeEdge:
```

getEdgeByIndex(edgeIndex). Returns Part.TopoShape.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1752.

## `TechDraw.DrawViewPart.getEdgeBySelection`

```python
def getEdgeBySelection(self, selection_name: str, /) -> TopoShapeEdge:
```

getEdgeBySelection(edgeName). Returns Part.TopoShape.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1756.

## `TechDraw.DrawViewPart.getVertexByIndex`

```python
def getVertexByIndex(self, index: int, /) -> TopoShapeVertex:
```

getVertexByIndex(vertexIndex). Returns Part.TopoShape.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1760.

## `TechDraw.DrawViewPart.getVertexBySelection`

```python
def getVertexBySelection(self, selection_name: str, /) -> TopoShapeVertex:
```

getVertexBySelection(vertexName). Returns Part.TopoShape.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1764.

## `TechDraw.DrawViewPart.projectPoint`

```python
def projectPoint(self, point: Vector, invert: bool=..., /) -> Vector:
```

projectPoint(vector3d point, [bool invert]). Returns the projection of point in the
projection coordinate system of this DrawViewPart. Optionally inverts the Y coordinate of the
result.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1768.

## `TechDraw.DrawViewPart.getGeometricCenter`

```python
def getGeometricCenter(self) -> Any:
```

point3d = getGeometricCenter() - returns the geometric center of the source shapes.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1776.

## `TechDraw.DrawViewPart.requestPaint`

```python
def requestPaint(self) -> Any:
```

requestPaint(). Redraw the graphic for this View.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1780.

