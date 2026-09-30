# `FreeCADGui._View3DInventorViewer`

[Module](index.md)

```python
class _View3DInventorViewer:
```

Class purpose undocumented in this stub.

Evidence: public stub `FreeCADGui/__init__.pyi` line 1448. Inherited members are on the named base's reference; aliases keep their imported identity.

Underscored typing/support name: verify runtime exposure and support status before using it.

## `FreeCADGui._View3DInventorViewer.getSoRenderManager`

```python
def getSoRenderManager(self) -> Any:
```

Return the underlying Coin render manager.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1450.

## `FreeCADGui._View3DInventorViewer.getSoEventManager`

```python
def getSoEventManager(self) -> Any:
```

Return the underlying Coin event manager.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1454.

## `FreeCADGui._View3DInventorViewer.getSceneGraph`

```python
def getSceneGraph(self) -> Any:
```

Return the current root scene graph.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1458.

## `FreeCADGui._View3DInventorViewer.setSceneGraph`

```python
def setSceneGraph(self, node: object, /) -> None:
```

Replace the root scene graph.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1462.

## `FreeCADGui._View3DInventorViewer.seekToPoint`

```python
def seekToPoint(self, point: _Point2 | _Point3, /) -> None:
```

Center the viewer on one screen or world point.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1466.

## `FreeCADGui._View3DInventorViewer.setFocalDistance`

```python
def setFocalDistance(self, distance: float, /) -> None:
```

Set the camera focal distance.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1470.

## `FreeCADGui._View3DInventorViewer.getFocalDistance`

```python
def getFocalDistance(self) -> float:
```

Return the camera focal distance.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1474.

## `FreeCADGui._View3DInventorViewer.getPoint`

```python
@overload
def getPoint(self, x: int, y: int, /) -> Vector:

@overload
def getPoint(self, point: _Point2, /) -> Vector:
```

Project one screen-space point into world coordinates.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1479, 1484.

## `FreeCADGui._View3DInventorViewer.getPointOnFocalPlane`

```python
@overload
def getPointOnFocalPlane(self, x: int, y: int, /) -> Vector:

@overload
def getPointOnFocalPlane(self, point: _Point2, /) -> Vector:
```

Project one screen-space point onto the focal plane.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1488, 1493.

## `FreeCADGui._View3DInventorViewer.getPickRadius`

```python
def getPickRadius(self) -> float:
```

Return the current pick radius.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1496.

## `FreeCADGui._View3DInventorViewer.setPickRadius`

```python
def setPickRadius(self, radius: float, /) -> None:
```

Set the pick radius used for hit-testing.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1500.

## `FreeCADGui._View3DInventorViewer.setupEditingRoot`

```python
def setupEditingRoot(self, node: object | None=None, matrix: Matrix | None=None, /) -> None:
```

Install one temporary editing root node.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1504.

## `FreeCADGui._View3DInventorViewer.resetEditingRoot`

```python
def resetEditingRoot(self, update_links: bool=True, /) -> None:
```

Remove the temporary editing root node.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1508.

## `FreeCADGui._View3DInventorViewer.setBackgroundColor`

```python
def setBackgroundColor(self, red: float, green: float, blue: float, /) -> None:
```

Set a solid background color.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1512.

## `FreeCADGui._View3DInventorViewer.setGradientBackground`

```python
def setGradientBackground(self, background: str, /) -> None:
```

Set the predefined gradient background mode.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1516.

## `FreeCADGui._View3DInventorViewer.setGradientBackgroundColor`

```python
def setGradientBackgroundColor(self, from_color: _Color, to_color: _Color, mid_color: _Color | None=None, /) -> None:
```

Set explicit gradient background colors.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1520.

## `FreeCADGui._View3DInventorViewer.setRedirectToSceneGraph`

```python
def setRedirectToSceneGraph(self, redirect: bool, /) -> None:
```

Enable or disable redirection to the scene graph.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1524.

## `FreeCADGui._View3DInventorViewer.isRedirectedToSceneGraph`

```python
def isRedirectedToSceneGraph(self) -> bool:
```

Return whether rendering is redirected to the scene graph.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1528.

## `FreeCADGui._View3DInventorViewer.renderToImage`

```python
def renderToImage(self, width: int=0, height: int=0, samples: int=-1, includeViewerLighting: bool=True) -> Any:
```

Render a fresh image without viewer decorations.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1532.

## `FreeCADGui._View3DInventorViewer.grabFramebuffer`

```python
def grabFramebuffer(self) -> Any:
```

Capture the live viewport framebuffer as a raster-oriented image.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1536.

## `FreeCADGui._View3DInventorViewer.setOverrideMode`

```python
def setOverrideMode(self, mode: str, /) -> None:
```

Set the viewer override rendering mode.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1540.

## `FreeCADGui._View3DInventorViewer.setEnabledNaviCube`

```python
def setEnabledNaviCube(self, enabled: bool, /) -> None:
```

Enable or disable the navigation cube.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1544.

## `FreeCADGui._View3DInventorViewer.isEnabledNaviCube`

```python
def isEnabledNaviCube(self) -> bool:
```

Return whether the navigation cube is enabled.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1548.

## `FreeCADGui._View3DInventorViewer.setNaviCubeCorner`

```python
def setNaviCubeCorner(self, corner: int, /) -> None:
```

Set the navigation-cube corner.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1552.

## `FreeCADGui._View3DInventorViewer.isSpinning`

```python
def isSpinning(self) -> Any:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1556.

## `FreeCADGui._View3DInventorViewer.getNavigationStyle`

```python
def getNavigationStyle(self) -> NavigationStyle | None:
```

Return the current navigation-style object, if any.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1559.

