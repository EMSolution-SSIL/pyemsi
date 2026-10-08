# `FemGui.ViewProviderFemPostFilter`

[Module](index.md)

```python
class ViewProviderFemPostFilter(ViewProviderDocumentObject):
```

ViewProviderFemPostPipeline class

Author: Stefan Tröger (stefantroeger@gmx.net)
License: LGPL-2.1-or-later

Evidence: public stub `FemGui/__init__.pyi` line 175. Inherited members are on the named base's reference; aliases keep their imported identity.

## `FemGui.ViewProviderFemPostFilter.Component`

```python
@property
def Component(self) -> str:

@Component.setter
def Component(self, value: str | list[str]) -> None:
```

Select component to display

Access: getter and setter declared in the stub.

Evidence: public stub `FemGui/__init__.pyi` line(s) 184, 189.

## `FemGui.ViewProviderFemPostFilter.EdgeColor`

```python
@property
def EdgeColor(self) -> tuple[float, float, float, float]:

@EdgeColor.setter
def EdgeColor(self, value: int | tuple[float, float, float] | tuple[float, float, float, float] | tuple[int, int, int] | tuple[int, int, int, int]) -> None:
```

Set wireframe line color.

Access: getter and setter declared in the stub.

Evidence: public stub `FemGui/__init__.pyi` line(s) 193, 198.

## `FemGui.ViewProviderFemPostFilter.Field`

```python
@property
def Field(self) -> str:

@Field.setter
def Field(self, value: str | list[str]) -> None:
```

Select the field used for calculating the color

Access: getter and setter declared in the stub.

Evidence: public stub `FemGui/__init__.pyi` line(s) 202, 207.

## `FemGui.ViewProviderFemPostFilter.LineWidth`

```python
@property
def LineWidth(self) -> float:

@LineWidth.setter
def LineWidth(self, value: float | int | dict[str, float] | tuple[float, float, float, float]) -> None:
```

Set wireframe line width.

Access: getter and setter declared in the stub.

Evidence: public stub `FemGui/__init__.pyi` line(s) 211, 216.

## `FemGui.ViewProviderFemPostFilter.NoneFieldColor`

```python
@property
def NoneFieldColor(self) -> tuple[float, float, float, float]:

@NoneFieldColor.setter
def NoneFieldColor(self, value: int | tuple[float, float, float] | tuple[float, float, float, float] | tuple[int, int, int] | tuple[int, int, int, int]) -> None:
```

Shape color used if Field property is None.

Access: getter and setter declared in the stub.

Evidence: public stub `FemGui/__init__.pyi` line(s) 220, 225.

## `FemGui.ViewProviderFemPostFilter.PlainColorEdgeOnSurface`

```python
@property
def PlainColorEdgeOnSurface(self) -> bool:

@PlainColorEdgeOnSurface.setter
def PlainColorEdgeOnSurface(self, value: bool | int) -> None:
```

Use plain color for edges on surface.

Access: getter and setter declared in the stub.

Evidence: public stub `FemGui/__init__.pyi` line(s) 229, 234.

## `FemGui.ViewProviderFemPostFilter.PointSize`

```python
@property
def PointSize(self) -> float:

@PointSize.setter
def PointSize(self, value: float | int | dict[str, float] | tuple[float, float, float, float]) -> None:
```

Set node point size.

Access: getter and setter declared in the stub.

Evidence: public stub `FemGui/__init__.pyi` line(s) 238, 243.

## `FemGui.ViewProviderFemPostFilter.Transparency`

```python
@property
def Transparency(self) -> int:

@Transparency.setter
def Transparency(self, value: int | dict[str, int] | tuple[int, int, int, int]) -> None:
```

Set object transparency.

Access: getter and setter declared in the stub.

Evidence: public stub `FemGui/__init__.pyi` line(s) 247, 252.

## `FemGui.ViewProviderFemPostFilter.createDisplayTaskWidget`

```python
def createDisplayTaskWidget(self) -> Any:
```

Returns the display option task panel for a post processing edit task dialog.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FemGui/__init__.pyi` line(s) 255.

## `FemGui.ViewProviderFemPostFilter.createExtractionTaskWidget`

```python
def createExtractionTaskWidget(self) -> Any:
```

Returns the data extraction task panel for a post processing edit task dialog.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FemGui/__init__.pyi` line(s) 259.

