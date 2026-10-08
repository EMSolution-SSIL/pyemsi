# `PathApp.Area`

[Module](index.md)

```python
class Area(BaseClass):
```

FreeCAD python wrapper of libarea

Path.Area(key=value ...)

The constructor accepts the same parameters as setParams(...) to configure the object
All arguments are optional.

Author: Zheng, Lei (realthunder.dev@gmail.com)
License: LGPL-2.1-or-later

Evidence: public stub `PathApp/__init__.pyi` line 74. Inherited members are on the named base's reference; aliases keep their imported identity.

## `PathApp.Area.add`

```python
def add(self, shape: TopoShape, Operation: int=0) -> Area:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Evidence: public stub `PathApp/__init__.pyi` line(s) 87.

## `PathApp.Area.setPlane`

```python
def setPlane(self, shape: TopoShape, /) -> Area:
```

Set the working plane.

The supplied shape does not need to be planar. Area will try to find planar
sub-shape (face, wire or edge). If more than one planar sub-shape is found, it
will prefer the top plane parallel to XY0 plane. If no working plane are set,
Area will try to find a working plane from the added children shape using the
same algorithm

Evidence: public stub `PathApp/__init__.pyi` line(s) 91.

## `PathApp.Area.getShape`

```python
def getShape(self, index: int=-1, rebuild: bool=False) -> TopoShape:
```

Return the resulting shape

* index (-1): the index of the section. -1 means all sections. No effect on planar shape.
* rebuild: clean the internal cache and rebuild

Evidence: public stub `PathApp/__init__.pyi` line(s) 103.

## `PathApp.Area.makeOffset`

```python
def makeOffset(self, index: int=-1, Offset: float=0.0, ExtraPass: int=0, Stepover: float=0.0) -> TopoShape:
```

Make an offset of the shape.

Evidence: public stub `PathApp/__init__.pyi` line(s) 112.

## `PathApp.Area.makePocket`

```python
def makePocket(self, index: int=-1, PocketMode: int=0, ToolRadius: float=1.0, PocketExtraOffset: float=0.0, PocketStepover: float=0.0, FromCenter: bool=False, Angle: float=45, AngleShift: float=0.0, Shift: float=0.0, ForceMaxStepover: bool=False) -> TopoShape:
```

Generate pocket toolpath of the shape.

Evidence: public stub `PathApp/__init__.pyi` line(s) 116.

## `PathApp.Area.makeSections`

```python
def makeSections(self, SectionMode: int=2, Project: bool=False, heights: object=None, plane: TopoShape=None) -> list[Area]:
```

Make a list of area holding the sectioned children shapes on given heights.

Evidence: public stub `PathApp/__init__.pyi` line(s) 120.

## `PathApp.Area.getRestArea`

```python
def getRestArea(self, clearedAreas: list[Area], diameter: float, /) -> Area | None:
```

Rest machining: Gets the area left to be machined, assuming some of this area has already been cleared by previous tool paths.

Evidence: public stub `PathApp/__init__.pyi` line(s) 124.

## `PathApp.Area.toTopoShape`

```python
def toTopoShape(self) -> Any:
```

Convert the Area object to a TopoShape.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `PathApp/__init__.pyi` line(s) 128.

## `PathApp.Area.setParams`

```python
def setParams(self, **kwargs) -> Any:
```

Set algorithm parameters.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `PathApp/__init__.pyi` line(s) 132.

## `PathApp.Area.setDefaultParams`

```python
def setDefaultParams(self, **kwargs) -> Any:
```

Static method to set the default parameters of all following Path.Area, plus the following additional parameters.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `PathApp/__init__.pyi` line(s) 136.

## `PathApp.Area.getDefaultParams`

```python
def getDefaultParams(self) -> Any:
```

Static method to return the current default parameters.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `PathApp/__init__.pyi` line(s) 140.

## `PathApp.Area.getParamsDesc`

```python
def getParamsDesc(self, **kwargs) -> Any:
```

Returns a list of supported parameters and their descriptions.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `PathApp/__init__.pyi` line(s) 144.

## `PathApp.Area.getParams`

```python
def getParams(self) -> Any:
```

Get current algorithm parameters as a dictionary.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `PathApp/__init__.pyi` line(s) 148.

## `PathApp.Area.abort`

```python
def abort(self, **kwargs) -> Any:
```

Abort the current operation.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `PathApp/__init__.pyi` line(s) 152.

## `PathApp.Area.Sections`

```python
Sections: Final[list]
```

List of sections in this area.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `PathApp/__init__.pyi` line(s) 155.

## `PathApp.Area.Workplane`

```python
Workplane: Any
```

The current workplane. If no plane is set, it is derived from the added shapes.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `PathApp/__init__.pyi` line(s) 157.

## `PathApp.Area.Shapes`

```python
Shapes: Final[list]
```

A list of tuple: [(shape,op), ...] containing the added shapes together with their operation code

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `PathApp/__init__.pyi` line(s) 159.

