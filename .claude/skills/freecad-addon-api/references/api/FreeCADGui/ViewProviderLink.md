# `FreeCADGui.ViewProviderLink`

[Module](index.md)

```python
class ViewProviderLink(ViewProviderDocumentObject):
```

This is the ViewProviderLink class

Author: Zheng, Lei (realthunder.dev@gmail.com)
Licence: LGPL

Evidence: public stub `FreeCADGui/__init__.pyi` line 3003. Inherited members are on the named base's reference; aliases keep their imported identity.

## `FreeCADGui.ViewProviderLink.DraggingPlacement`

```python
DraggingPlacement: Any = ...
```

Get/set dragger placement during dragging

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 3010.

## `FreeCADGui.ViewProviderLink.LinkView`

```python
LinkView: Final[Any] = ...
```

Get the associated LinkView object

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 3012.

## `FreeCADGui.ViewProviderLink.ChildViewProvider`

```python
@property
def ChildViewProvider(self) -> object:

@ChildViewProvider.setter
def ChildViewProvider(self, value: str) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 3016, 3020.

## `FreeCADGui.ViewProviderLink.DrawStyle`

```python
@property
def DrawStyle(self) -> str:

@DrawStyle.setter
def DrawStyle(self, value: str | list[str]) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 3024, 3028.

## `FreeCADGui.ViewProviderLink.LineWidth`

```python
@property
def LineWidth(self) -> float:

@LineWidth.setter
def LineWidth(self, value: float | int | dict[str, float] | tuple[float, float, float, float]) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 3032, 3036.

## `FreeCADGui.ViewProviderLink.OverrideMaterial`

```python
@property
def OverrideMaterial(self) -> bool:

@OverrideMaterial.setter
def OverrideMaterial(self, value: bool | int) -> None:
```

Override linked object's material

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 3040, 3045.

## `FreeCADGui.ViewProviderLink.PointSize`

```python
@property
def PointSize(self) -> float:

@PointSize.setter
def PointSize(self, value: float | int | dict[str, float] | tuple[float, float, float, float]) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 3049, 3053.

## `FreeCADGui.ViewProviderLink.Selectable`

```python
@property
def Selectable(self) -> bool:

@Selectable.setter
def Selectable(self, value: bool | int) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 3057, 3061.

