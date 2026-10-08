# `FemGui.ViewProviderFemMesh`

[Module](index.md)

```python
class ViewProviderFemMesh(ViewProviderGeometryObject):
```

ViewProviderFemMesh class

Author: Juergen Riegel (Juergen.Riegel@web.de)
License: LGPL-2.1-or-later

Evidence: public stub `FemGui/__init__.pyi` line 76. Inherited members are on the named base's reference; aliases keep their imported identity.

## `FemGui.ViewProviderFemMesh.BackfaceCulling`

```python
@property
def BackfaceCulling(self) -> bool:

@BackfaceCulling.setter
def BackfaceCulling(self, value: bool | int) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: getter and setter declared in the stub.

Evidence: public stub `FemGui/__init__.pyi` line(s) 85, 89.

## `FemGui.ViewProviderFemMesh.ColorMode`

```python
@property
def ColorMode(self) -> str:

@ColorMode.setter
def ColorMode(self, value: str | list[str]) -> None:
```

Set the color mode

Access: getter and setter declared in the stub.

Evidence: public stub `FemGui/__init__.pyi` line(s) 93, 98.

## `FemGui.ViewProviderFemMesh.LineWidth`

```python
@property
def LineWidth(self) -> float:

@LineWidth.setter
def LineWidth(self, value: float | int | dict[str, float] | tuple[float, float, float, float]) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: getter and setter declared in the stub.

Evidence: public stub `FemGui/__init__.pyi` line(s) 102, 106.

## `FemGui.ViewProviderFemMesh.MaxFacesShowInner`

```python
@property
def MaxFacesShowInner(self) -> int:

@MaxFacesShowInner.setter
def MaxFacesShowInner(self, value: int) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: getter and setter declared in the stub.

Evidence: public stub `FemGui/__init__.pyi` line(s) 110, 114.

## `FemGui.ViewProviderFemMesh.PointColor`

```python
@property
def PointColor(self) -> tuple[float, float, float, float]:

@PointColor.setter
def PointColor(self, value: int | tuple[float, float, float] | tuple[float, float, float, float] | tuple[int, int, int] | tuple[int, int, int, int]) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: getter and setter declared in the stub.

Evidence: public stub `FemGui/__init__.pyi` line(s) 118, 122.

## `FemGui.ViewProviderFemMesh.PointSize`

```python
@property
def PointSize(self) -> float:

@PointSize.setter
def PointSize(self, value: float | int | dict[str, float] | tuple[float, float, float, float]) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: getter and setter declared in the stub.

Evidence: public stub `FemGui/__init__.pyi` line(s) 126, 130.

## `FemGui.ViewProviderFemMesh.ShowInner`

```python
@property
def ShowInner(self) -> bool:

@ShowInner.setter
def ShowInner(self, value: bool | int) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: getter and setter declared in the stub.

Evidence: public stub `FemGui/__init__.pyi` line(s) 134, 138.

## `FemGui.ViewProviderFemMesh.applyDisplacement`

```python
def applyDisplacement(self, factor: float, /) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Evidence: public stub `FemGui/__init__.pyi` line(s) 141.

## `FemGui.ViewProviderFemMesh.resetNodeColor`

```python
def resetNodeColor(self) -> None:
```

Reset color set by method setNodeColorByScalars.

Evidence: public stub `FemGui/__init__.pyi` line(s) 145.

## `FemGui.ViewProviderFemMesh.resetNodeDisplacement`

```python
def resetNodeDisplacement(self) -> None:
```

Reset displacements set by method setNodeDisplacementByVectors.

Evidence: public stub `FemGui/__init__.pyi` line(s) 149.

## `FemGui.ViewProviderFemMesh.resetHighlightedNodes`

```python
def resetHighlightedNodes(self) -> None:
```

Reset highlighted nodes.

Evidence: public stub `FemGui/__init__.pyi` line(s) 153.

## `FemGui.ViewProviderFemMesh.setNodeColorByScalars`

```python
def setNodeColorByScalars(self, node_ids: list[int], values: list[float], /) -> None:
```

Sets mesh node colors using element list and value list.

Evidence: public stub `FemGui/__init__.pyi` line(s) 157.

## `FemGui.ViewProviderFemMesh.setNodeDisplacementByVectors`

```python
def setNodeDisplacementByVectors(self, node_ids: list[int], vectors: list[Vector | tuple[float, float, float]], /) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Evidence: public stub `FemGui/__init__.pyi` line(s) 161.

## `FemGui.ViewProviderFemMesh.NodeColor`

```python
NodeColor: dict
```

Postprocessing color of the nodes. The faces between the nodes get interpolated.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FemGui/__init__.pyi` line(s) 164.

## `FemGui.ViewProviderFemMesh.ElementColor`

```python
ElementColor: dict
```

Postprocessing color of the elements. All faces of the element get the same color.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FemGui/__init__.pyi` line(s) 166.

## `FemGui.ViewProviderFemMesh.NodeDisplacement`

```python
NodeDisplacement: dict
```

Postprocessing color of the nodes. The faces between the nodes get interpolated.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FemGui/__init__.pyi` line(s) 168.

## `FemGui.ViewProviderFemMesh.HighlightedNodes`

```python
HighlightedNodes: list
```

List of nodes which get highlighted.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FemGui/__init__.pyi` line(s) 170.

## `FemGui.ViewProviderFemMesh.VisibleElementFaces`

```python
VisibleElementFaces: Final[list]
```

List of elements and faces which are actually shown. These are all surface faces of the mesh.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FemGui/__init__.pyi` line(s) 172.

