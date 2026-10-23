# `FreeCADGui.AxisOrigin`

[Module](index.md)

```python
class AxisOrigin(BaseClass):
```

Gui.AxisOrigin class.

Class for creating a Coin3D representation of a coordinate system.

Author: Zheng, Lei (realthunder.dev@gmail.com)
Licence: LGPL

Evidence: public stub `FreeCADGui/__init__.pyi` line 1583. Inherited members are on the named base's reference; aliases keep their imported identity.

## `FreeCADGui.AxisOrigin.getElementPicked`

```python
def getElementPicked(self, pickedPoint: Any, /) -> str | None:
```

Returns the picked element name.

pickedPoint : coin.SoPickedPoint

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1593.

## `FreeCADGui.AxisOrigin.getDetailPath`

```python
def getDetailPath(self, subname: str, path: Any, /) -> Any:
```

Returns Coin detail of a subelement.
Note: Not fully implemented. Currently only returns None.

subname : str
    String reference to the subelement.
path: coin.SoPath
    Output Coin path leading to the returned element detail.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1601.

## `FreeCADGui.AxisOrigin.AxisLength`

```python
AxisLength: float = 0.0
```

Get/set the axis length.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1612.

## `FreeCADGui.AxisOrigin.LineWidth`

```python
LineWidth: float = 0.0
```

Get/set the axis line width for rendering.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1614.

## `FreeCADGui.AxisOrigin.PointSize`

```python
PointSize: float = 0.0
```

Get/set the origin point size for rendering.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1616.

## `FreeCADGui.AxisOrigin.Scale`

```python
Scale: float = 0.0
```

Get/set auto scaling factor, 0 to disable.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1618.

## `FreeCADGui.AxisOrigin.Plane`

```python
Plane: Tuple[Any, ...] = ()
```

Get/set axis plane size and distance to axis line.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1620.

## `FreeCADGui.AxisOrigin.Labels`

```python
Labels: Dict[str, str] = {}
```


    Get/set axis component names as a dictionary.
    Available keys are:
    'O': origin
    'X': x axis
    'Y': y axis
    'Z': z axis
    'XY': xy plane
    'XZ': xz plane
    'YZ': yz plane
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1622.

## `FreeCADGui.AxisOrigin.Node`

```python
Node: Final[Any] = ...
```

Get the Coin3D node.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1624.

