# `MeshGui.ViewProviderMesh`

[Module](index.md)

```python
class ViewProviderMesh(ViewProviderGeometryObject):
```

This is the ViewProvider base class

Author: Werner Mayer (wmayer@users.sourceforge.net)
License: LGPL-2.1-or-later

Evidence: public stub `MeshGui/__init__.pyi` line 11. Inherited members are on the named base's reference; aliases keep their imported identity.

## `MeshGui.ViewProviderMesh.Coloring`

```python
@property
def Coloring(self) -> bool:

@Coloring.setter
def Coloring(self, value: bool | int) -> None:
```

Set coloring.

Access: getter and setter declared in the stub.

Evidence: public stub `MeshGui/__init__.pyi` line(s) 20, 25.

## `MeshGui.ViewProviderMesh.CreaseAngle`

```python
@property
def CreaseAngle(self) -> float:

@CreaseAngle.setter
def CreaseAngle(self, value: float | int | dict[str, float] | tuple[float, float, float, float]) -> None:
```

Set crease angle.

Access: getter and setter declared in the stub.

Evidence: public stub `MeshGui/__init__.pyi` line(s) 29, 34.

## `MeshGui.ViewProviderMesh.Lighting`

```python
@property
def Lighting(self) -> str:

@Lighting.setter
def Lighting(self, value: str | list[str]) -> None:
```

Set if the illumination comes from two sides
or one side in the 3D view.

Access: getter and setter declared in the stub.

Evidence: public stub `MeshGui/__init__.pyi` line(s) 38, 44.

## `MeshGui.ViewProviderMesh.LineColor`

```python
@property
def LineColor(self) -> tuple[float, float, float, float]:

@LineColor.setter
def LineColor(self, value: int | tuple[float, float, float] | tuple[float, float, float, float] | tuple[int, int, int] | tuple[int, int, int, int]) -> None:
```

Set line color.

Access: getter and setter declared in the stub.

Evidence: public stub `MeshGui/__init__.pyi` line(s) 48, 53.

## `MeshGui.ViewProviderMesh.LineTransparency`

```python
@property
def LineTransparency(self) -> int:

@LineTransparency.setter
def LineTransparency(self, value: int | dict[str, int] | tuple[int, int, int, int]) -> None:
```

Set line transparency.

Access: getter and setter declared in the stub.

Evidence: public stub `MeshGui/__init__.pyi` line(s) 57, 62.

## `MeshGui.ViewProviderMesh.LineWidth`

```python
@property
def LineWidth(self) -> float:

@LineWidth.setter
def LineWidth(self, value: float | int | dict[str, float] | tuple[float, float, float, float]) -> None:
```

Set line width.

Access: getter and setter declared in the stub.

Evidence: public stub `MeshGui/__init__.pyi` line(s) 66, 71.

## `MeshGui.ViewProviderMesh.OpenEdges`

```python
@property
def OpenEdges(self) -> bool:

@OpenEdges.setter
def OpenEdges(self, value: bool | int) -> None:
```

Set open edges.

Access: getter and setter declared in the stub.

Evidence: public stub `MeshGui/__init__.pyi` line(s) 75, 80.

## `MeshGui.ViewProviderMesh.PointSize`

```python
@property
def PointSize(self) -> float:

@PointSize.setter
def PointSize(self, value: float | int | dict[str, float] | tuple[float, float, float, float]) -> None:
```

Set point size.

Access: getter and setter declared in the stub.

Evidence: public stub `MeshGui/__init__.pyi` line(s) 84, 89.

## `MeshGui.ViewProviderMesh.setSelection`

```python
def setSelection(self, indices: list[int], /) -> None:
```

Select list of facets

Evidence: public stub `MeshGui/__init__.pyi` line(s) 92.

## `MeshGui.ViewProviderMesh.addSelection`

```python
def addSelection(self, indices: list[int], /) -> None:
```

Add list of facets to selection

Evidence: public stub `MeshGui/__init__.pyi` line(s) 96.

## `MeshGui.ViewProviderMesh.removeSelection`

```python
def removeSelection(self, indices: list[int], /) -> None:
```

Remove list of facets from selection

Evidence: public stub `MeshGui/__init__.pyi` line(s) 100.

## `MeshGui.ViewProviderMesh.invertSelection`

```python
def invertSelection(self) -> None:
```

Invert the selection

Evidence: public stub `MeshGui/__init__.pyi` line(s) 104.

## `MeshGui.ViewProviderMesh.clearSelection`

```python
def clearSelection(self) -> None:
```

Clear the selection

Evidence: public stub `MeshGui/__init__.pyi` line(s) 108.

## `MeshGui.ViewProviderMesh.highlightSegments`

```python
def highlightSegments(self, colors: list, /) -> None:
```

Highlights the segments of a mesh with a given list of colors.
The number of elements of this list must be equal to the number of mesh segments.

Evidence: public stub `MeshGui/__init__.pyi` line(s) 112.

