# `FreeCADGui._View3DInventor`

[Module](index.md)

```python
class _View3DInventor:
```

Class purpose undocumented in this stub.

Evidence: public stub `FreeCADGui/__init__.pyi` line 1096. Inherited members are on the named base's reference; aliases keep their imported identity.

Underscored typing/support name: verify runtime exposure and support status before using it.

## `FreeCADGui._View3DInventor.fitAll`

```python
def fitAll(self, factor: float=1.0, /) -> None:
```

Fit the full scene into view.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1098.

## `FreeCADGui._View3DInventor.boxZoom`

```python
def boxZoom(self, XMin: int, YMin: int, XMax: int, YMax: int) -> None:
```

Zoom to one screen-space rectangle.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1102.

## `FreeCADGui._View3DInventor.viewBottom`

```python
def viewBottom(self) -> None:
```

Orient the camera to the bottom view.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1106.

## `FreeCADGui._View3DInventor.viewFront`

```python
def viewFront(self) -> None:
```

Orient the camera to the front view.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1110.

## `FreeCADGui._View3DInventor.viewLeft`

```python
def viewLeft(self) -> None:
```

Orient the camera to the left view.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1114.

## `FreeCADGui._View3DInventor.viewRear`

```python
def viewRear(self) -> None:
```

Orient the camera to the rear view.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1118.

## `FreeCADGui._View3DInventor.viewRight`

```python
def viewRight(self) -> None:
```

Orient the camera to the right view.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1122.

## `FreeCADGui._View3DInventor.viewTop`

```python
def viewTop(self) -> None:
```

Orient the camera to the top view.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1126.

## `FreeCADGui._View3DInventor.viewAxometric`

```python
def viewAxometric(self) -> None:
```

Orient the camera axometrically.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1130.

## `FreeCADGui._View3DInventor.viewAxonometric`

```python
def viewAxonometric(self) -> None:
```

Orient the camera axonometrically.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1134.

## `FreeCADGui._View3DInventor.viewIsometric`

```python
def viewIsometric(self) -> None:
```

Orient the camera isometrically.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1138.

## `FreeCADGui._View3DInventor.viewDimetric`

```python
def viewDimetric(self) -> None:
```

Orient the camera dimetrically.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1142.

## `FreeCADGui._View3DInventor.viewTrimetric`

```python
def viewTrimetric(self) -> None:
```

Orient the camera trimetrically.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1146.

## `FreeCADGui._View3DInventor.viewDefaultOrientation`

```python
def viewDefaultOrientation(self, view: _ViewOrientation | None=None, scale: float=-1.0, /) -> None:
```

Restore the default camera orientation.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1150.

## `FreeCADGui._View3DInventor.viewRotateLeft`

```python
def viewRotateLeft(self) -> None:
```

Rotate the view left.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1154.

## `FreeCADGui._View3DInventor.viewRotateRight`

```python
def viewRotateRight(self) -> None:
```

Rotate the view right.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1158.

## `FreeCADGui._View3DInventor.zoomIn`

```python
def zoomIn(self) -> None:
```

Zoom the camera in.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1162.

## `FreeCADGui._View3DInventor.zoomOut`

```python
def zoomOut(self) -> None:
```

Zoom the camera out.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1166.

## `FreeCADGui._View3DInventor.viewPosition`

```python
@overload
def viewPosition(self) -> Placement | None:

@overload
def viewPosition(self, placement: Placement, steps: int=0, duration: int=-1, /) -> Placement | None:
```

Return the current view placement.

Return or animate the current view placement.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1171, 1176.

## `FreeCADGui._View3DInventor.startAnimating`

```python
def startAnimating(self, x: float, y: float, z: float, velocity: float, /) -> None:
```

Start continuous camera animation.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1180.

## `FreeCADGui._View3DInventor.stopAnimating`

```python
def stopAnimating(self) -> None:
```

Stop continuous camera animation.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1184.

## `FreeCADGui._View3DInventor.setAnimationEnabled`

```python
def setAnimationEnabled(self, enabled: bool, /) -> None:
```

Enable or disable camera animation support.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1188.

## `FreeCADGui._View3DInventor.isAnimationEnabled`

```python
def isAnimationEnabled(self) -> bool:
```

Return whether camera animation support is enabled.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1192.

## `FreeCADGui._View3DInventor.setPopupMenuEnabled`

```python
def setPopupMenuEnabled(self, enabled: bool, /) -> None:
```

Enable or disable the view popup menu.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1196.

## `FreeCADGui._View3DInventor.isPopupMenuEnabled`

```python
def isPopupMenuEnabled(self) -> bool:
```

Return whether the view popup menu is enabled.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1200.

## `FreeCADGui._View3DInventor.dump`

```python
def dump(self, filename: str, only_visible: bool=False, /) -> None:
```

Dump the scene graph to one file.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1204.

## `FreeCADGui._View3DInventor.dumpNode`

```python
def dumpNode(self, node: object, /) -> str:
```

Return a textual dump of one scene-graph node.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1208.

## `FreeCADGui._View3DInventor.saveImage`

```python
def saveImage(self, filename: str, width: int=-1, height: int=-1, color: str='Current', comment: str='$MIBA', samples: int=0, /) -> None:
```

Save the current view as a raster image.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1212.

## `FreeCADGui._View3DInventor.saveVectorGraphic`

```python
def saveVectorGraphic(self, filename: str, page_size: int=4, background: str='white', /) -> None:
```

Save the current view as a vector graphic.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1216.

## `FreeCADGui._View3DInventor.getCamera`

```python
def getCamera(self) -> str:
```

Return the current camera description.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1220.

## `FreeCADGui._View3DInventor.getCameraNode`

```python
def getCameraNode(self) -> Any | None:
```

Return the underlying camera node.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1224.

## `FreeCADGui._View3DInventor.getViewDirection`

```python
def getViewDirection(self) -> Vector:
```

Return the current camera view direction.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1228.

## `FreeCADGui._View3DInventor.getUpDirection`

```python
def getUpDirection(self) -> Vector:
```

Return the current camera up direction.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1232.

## `FreeCADGui._View3DInventor.setViewDirection`

```python
def setViewDirection(self, direction: _Point3, /) -> None:
```

Set the camera view direction.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1236.

## `FreeCADGui._View3DInventor.setCamera`

```python
def setCamera(self, camera: str, /) -> None:
```

Set the camera from one serialized description.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1240.

## `FreeCADGui._View3DInventor.setCameraOrientation`

```python
def setCameraOrientation(self, rotation: Rotation | tuple[float, float, float, float], move_to_rotation_center: bool=False, /) -> None:
```

Set the camera orientation.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1244.

## `FreeCADGui._View3DInventor.getCameraOrientation`

```python
def getCameraOrientation(self) -> Rotation:
```

Return the current camera orientation.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1248.

## `FreeCADGui._View3DInventor.getCameraType`

```python
def getCameraType(self) -> str:
```

Return the current camera type name.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1252.

## `FreeCADGui._View3DInventor.setCameraType`

```python
def setCameraType(self, camera_type: _CameraType, /) -> None:
```

Set the camera type.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1256.

## `FreeCADGui._View3DInventor.listCameraTypes`

```python
def listCameraTypes(self) -> list[str]:
```

Return the supported camera type names.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1260.

## `FreeCADGui._View3DInventor.getCursorPos`

```python
def getCursorPos(self) -> tuple[int, int]:
```

Return the current cursor position in view coordinates.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1264.

## `FreeCADGui._View3DInventor.getObjectInfo`

```python
def getObjectInfo(self, point: _Point2, radius: float=0.0, /) -> _View3DObjectInfo | None:
```

Return hit-test information for one point.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1268.

## `FreeCADGui._View3DInventor.getObjectsInfo`

```python
def getObjectsInfo(self, point: _Point2, radius: float=0.0, /) -> list[_View3DObjectInfo] | None:
```

Return hit-test information for all objects near one point.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1272.

## `FreeCADGui._View3DInventor.getSize`

```python
def getSize(self) -> tuple[int, int]:
```

Return the current view size in pixels.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1276.

## `FreeCADGui._View3DInventor.getObjectInfoRay`

```python
@overload
def getObjectInfoRay(self, start: Vector, direction: Vector, /) -> _View3DRayInfo | None:

@overload
def getObjectInfoRay(self, start_x: float, start_y: float, start_z: float, direction_x: float, direction_y: float, direction_z: float, /) -> _View3DRayInfo | None:
```

Return hit-test information for one world-space ray.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1281, 1286.

## `FreeCADGui._View3DInventor.getPoint`

```python
@overload
def getPoint(self, x: int, y: int, /) -> Vector:

@overload
def getPoint(self, point: _Point2, /) -> Vector:
```

Project one screen-space point into world coordinates.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1290, 1295.

## `FreeCADGui._View3DInventor.getPointOnFocalPlane`

```python
@overload
def getPointOnFocalPlane(self, x: int, y: int, /) -> Vector:

@overload
def getPointOnFocalPlane(self, point: _Point2, /) -> Vector:
```

Project one screen-space point onto the focal plane.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1299, 1304.

## `FreeCADGui._View3DInventor.getPointOnScreen`

```python
@overload
def getPointOnScreen(self, point: Vector, /) -> _Point2:

@overload
def getPointOnScreen(self, x: float, y: float, z: float, /) -> _Point2:
```

Project one world-space point onto the screen.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1308, 1313.

## `FreeCADGui._View3DInventor.getPointOnViewport`

```python
@overload
def getPointOnViewport(self, point: Vector, /) -> _Point2:

@overload
def getPointOnViewport(self, x: float, y: float, z: float, /) -> _Point2:
```

Project one world-space point into viewport coordinates.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1317, 1322.

## `FreeCADGui._View3DInventor.projectPointToLine`

```python
@overload
def projectPointToLine(self, x: int, y: int, /) -> tuple[Vector, Vector]:

@overload
def projectPointToLine(self, point: _Point2, /) -> tuple[Vector, Vector]:
```

Project one screen-space point to a world-space line.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1326, 1331.

## `FreeCADGui._View3DInventor.addEventCallback`

```python
def addEventCallback(self, event_type: str, callback: _View3DEventCallback, /) -> _View3DEventCallback:
```

Register one event callback.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1334.

## `FreeCADGui._View3DInventor.removeEventCallback`

```python
def removeEventCallback(self, event_type: str, callback: _View3DEventCallback, /) -> None:
```

Remove one event callback.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1338.

## `FreeCADGui._View3DInventor.setAnnotation`

```python
def setAnnotation(self, name: str, buffer: str, /) -> None:
```

Set one named annotation buffer.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1342.

## `FreeCADGui._View3DInventor.removeAnnotation`

```python
def removeAnnotation(self, name: str, /) -> None:
```

Remove one named annotation buffer.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1346.

## `FreeCADGui._View3DInventor.getSceneGraph`

```python
def getSceneGraph(self) -> Any:
```

Return the root scene graph.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1350.

## `FreeCADGui._View3DInventor.getViewer`

```python
def getViewer(self) -> _View3DInventorViewer:
```

Return the low-level viewer wrapper.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1354.

## `FreeCADGui._View3DInventor.addEventCallbackPivy`

```python
def addEventCallbackPivy(self, event_type: object, callback: _View3DProxyCallback, extended: bool | int=1, /) -> _View3DProxyCallback:
```

Register one Pivy event callback.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1358.

## `FreeCADGui._View3DInventor.removeEventCallbackPivy`

```python
def removeEventCallbackPivy(self, event_type: object, callback: _View3DProxyCallback, extended: bool | int=1, /) -> _View3DProxyCallback:
```

Remove one Pivy event callback.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1362.

## `FreeCADGui._View3DInventor.addEventCallbackSWIG`

```python
@deprecated('since FreeCAD 26.3 and will be removed in FreeCAD 27.2; use addEventCallbackPivy instead.')
def addEventCallbackSWIG(self, event_type: object, callback: _View3DProxyCallback, extended: bool | int=1, /) -> _View3DProxyCallback:
```

Register one SWIG event callback.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1367.

## `FreeCADGui._View3DInventor.removeEventCallbackSWIG`

```python
@deprecated('since FreeCAD 26.3 and will be removed in FreeCAD 27.2; use removeEventCallbackPivy instead.')
def removeEventCallbackSWIG(self, event_type: object, callback: _View3DProxyCallback, extended: bool | int=1, /) -> _View3DProxyCallback:
```

Remove one SWIG event callback.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1372.

## `FreeCADGui._View3DInventor.listNavigationTypes`

```python
def listNavigationTypes(self) -> list[str]:
```

Return the supported navigation-style names.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1376.

## `FreeCADGui._View3DInventor.getNavigationType`

```python
def getNavigationType(self) -> str:
```

Return the current navigation-style name.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1380.

## `FreeCADGui._View3DInventor.setNavigationType`

```python
def setNavigationType(self, navigation_type: str, /) -> None:
```

Set the navigation style by name.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1384.

## `FreeCADGui._View3DInventor.setAxisCross`

```python
def setAxisCross(self, enabled: bool, /) -> None:
```

Enable or disable the axis cross.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1388.

## `FreeCADGui._View3DInventor.hasAxisCross`

```python
def hasAxisCross(self) -> bool:
```

Return whether the axis cross is enabled.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1392.

## `FreeCADGui._View3DInventor.addDraggerCallback`

```python
def addDraggerCallback(self, dragger: object, callback_type: _DraggerCallbackType, callback: _View3DProxyCallback, /) -> _View3DProxyCallback:
```

Register one dragger callback.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1396.

## `FreeCADGui._View3DInventor.removeDraggerCallback`

```python
def removeDraggerCallback(self, dragger: object, callback_type: _DraggerCallbackType, callback: _View3DProxyCallback, /) -> _View3DProxyCallback:
```

Remove one dragger callback.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1400.

## `FreeCADGui._View3DInventor.getViewProvidersOfType`

```python
def getViewProvidersOfType(self, type_name: str, /) -> list[object]:
```

Return the view providers of one type name.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1404.

## `FreeCADGui._View3DInventor.redraw`

```python
def redraw(self) -> None:
```

Request a redraw of the view.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1408.

## `FreeCADGui._View3DInventor.setName`

```python
def setName(self, name: str, /) -> None:
```

Set the internal view name.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1412.

## `FreeCADGui._View3DInventor.toggleClippingPlane`

```python
def toggleClippingPlane(self, toggle: int=-1, beforeEditing: bool=False, noManip: bool=True, pla: Placement=...) -> None:
```

Toggle or configure the clipping plane.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1416.

## `FreeCADGui._View3DInventor.hasClippingPlane`

```python
def hasClippingPlane(self) -> bool:
```

Return whether a clipping plane is active.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1420.

## `FreeCADGui._View3DInventor.graphicsView`

```python
def graphicsView(self) -> Any:
```

Return the underlying graphics-view object.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1424.

## `FreeCADGui._View3DInventor.setCornerCrossVisible`

```python
def setCornerCrossVisible(self, visible: bool, /) -> None:
```

Show or hide the corner cross.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1428.

## `FreeCADGui._View3DInventor.isCornerCrossVisible`

```python
def isCornerCrossVisible(self) -> bool:
```

Return whether the corner cross is visible.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1432.

## `FreeCADGui._View3DInventor.setCornerCrossSize`

```python
def setCornerCrossSize(self, size: int, /) -> None:
```

Set the corner-cross size.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1436.

## `FreeCADGui._View3DInventor.getCornerCrossSize`

```python
def getCornerCrossSize(self) -> int:
```

Return the corner-cross size.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1440.

## `FreeCADGui._View3DInventor.cast_to_base`

```python
def cast_to_base(self) -> _MDIView:
```

Return this view as the base MDI view wrapper.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1444.

