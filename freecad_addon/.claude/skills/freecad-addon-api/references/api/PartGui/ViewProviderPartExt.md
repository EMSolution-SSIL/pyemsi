# `PartGui.ViewProviderPartExt`

[Module](index.md)

```python
class ViewProviderPartExt(ViewProviderGeometryObject):
```

This is the ViewProvider geometry class

Author: David Carter (dcarter@davidcarter.ca)
Licence: LGPL

Evidence: public stub `PartGui/__init__.pyi` line 11. Inherited members are on the named base's reference; aliases keep their imported identity.

## `PartGui.ViewProviderPartExt.AngularDeflection`

```python
@property
def AngularDeflection(self) -> Base.Quantity:

@AngularDeflection.setter
def AngularDeflection(self, value: float | str | Base.Quantity) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: getter and setter declared in the stub.

Evidence: public stub `PartGui/__init__.pyi` line(s) 21, 25.

## `PartGui.ViewProviderPartExt.Deviation`

```python
@property
def Deviation(self) -> float:

@Deviation.setter
def Deviation(self, value: float | int | dict[str, float] | tuple[float, float, float, float]) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: getter and setter declared in the stub.

Evidence: public stub `PartGui/__init__.pyi` line(s) 29, 33.

## `PartGui.ViewProviderPartExt.DrawStyle`

```python
@property
def DrawStyle(self) -> str:

@DrawStyle.setter
def DrawStyle(self, value: str | list[str]) -> None:
```

Defines the style of the edges in the 3D view.

Access: getter and setter declared in the stub.

Evidence: public stub `PartGui/__init__.pyi` line(s) 37, 42.

## `PartGui.ViewProviderPartExt.Lighting`

```python
@property
def Lighting(self) -> str:

@Lighting.setter
def Lighting(self, value: str | list[str]) -> None:
```

Set object lighting.

Access: getter and setter declared in the stub.

Evidence: public stub `PartGui/__init__.pyi` line(s) 46, 51.

## `PartGui.ViewProviderPartExt.LineColor`

```python
@property
def LineColor(self) -> tuple[float, float, float, float]:

@LineColor.setter
def LineColor(self, value: int | tuple[float, float, float] | tuple[float, float, float, float] | tuple[int, int, int] | tuple[int, int, int, int]) -> None:
```

Set object line color.

Access: getter and setter declared in the stub.

Evidence: public stub `PartGui/__init__.pyi` line(s) 55, 60.

## `PartGui.ViewProviderPartExt.LineWidth`

```python
@property
def LineWidth(self) -> float:

@LineWidth.setter
def LineWidth(self, value: float | int | dict[str, float] | tuple[float, float, float, float]) -> None:
```

Set object line width.

Access: getter and setter declared in the stub.

Evidence: public stub `PartGui/__init__.pyi` line(s) 64, 69.

## `PartGui.ViewProviderPartExt.PointColor`

```python
@property
def PointColor(self) -> tuple[float, float, float, float]:

@PointColor.setter
def PointColor(self, value: int | tuple[float, float, float] | tuple[float, float, float, float] | tuple[int, int, int] | tuple[int, int, int, int]) -> None:
```

Set object point color

Access: getter and setter declared in the stub.

Evidence: public stub `PartGui/__init__.pyi` line(s) 73, 78.

## `PartGui.ViewProviderPartExt.PointSize`

```python
@property
def PointSize(self) -> float:

@PointSize.setter
def PointSize(self, value: float | int | dict[str, float] | tuple[float, float, float, float]) -> None:
```

Set object point size.

Access: getter and setter declared in the stub.

Evidence: public stub `PartGui/__init__.pyi` line(s) 82, 87.

