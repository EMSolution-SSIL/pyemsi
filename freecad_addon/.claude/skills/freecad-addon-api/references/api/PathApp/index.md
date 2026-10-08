# `PathApp`

[Catalogue index](../index.md)

Evidence: import-shaped public stub `PathApp/__init__.pyi`; generated binding/typing declarations, runtime unverified.

## Classes

- [PathApp.Area](Area.md)
- [PathApp.Command](Command.md)
- [PathApp.Path](Path.md)

## Imports and aliases

These preserve stub type context and reexports. Imported typing helpers and underscored names are not a promise of supported runtime API.

```python
from __future__ import annotations
from typing import Any, overload
from typing_extensions import deprecated
from collections.abc import Sequence
from typing import Literal, TypeAlias
from FreeCAD import DocumentObject
from FreeCAD.Base import Vector
from Part import Shape, Wire
from FreeCAD.Base import BaseClass
from Part import Shape as TopoShape
from typing import Final
import PathApp
from FreeCAD.Base import Persistence
from typing import overload
from typing import Union
```

## `PathApp._ShapeInput`

```python
_ShapeInput: TypeAlias = Shape | Sequence[Shape]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `PathApp/__init__.pyi` line(s) 12.

## `PathApp._ArcPlane`

```python
_ArcPlane: TypeAlias = Literal[0, 1, 2, 3, 4, 5] | int
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `PathApp/__init__.pyi` line(s) 13.

## `PathApp._SortMode`

```python
_SortMode: TypeAlias = Literal[0, 1, 2, 3] | int
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `PathApp/__init__.pyi` line(s) 14.

## `PathApp._Orientation`

```python
_Orientation: TypeAlias = Literal[0, 1] | int
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `PathApp/__init__.pyi` line(s) 15.

## `PathApp._Direction`

```python
_Direction: TypeAlias = Literal[0, 1, 2, 3, 4, 5, 6] | int
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `PathApp/__init__.pyi` line(s) 16.

## `PathApp._RetractAxis`

```python
_RetractAxis: TypeAlias = Literal[0, 1, 2] | int
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `PathApp/__init__.pyi` line(s) 17.

## `PathApp._WireSortResult`

```python
_WireSortResult: TypeAlias = tuple[list[Wire], Vector] | tuple[list[Wire], Vector, int]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `PathApp/__init__.pyi` line(s) 18.

## `PathApp.write`

```python
def write(obj: DocumentObject, filename: str, /) -> None:
```

Export one Path feature document object to one G-code file.

Evidence: public stub `PathApp/__init__.pyi` line(s) 20.

## `PathApp.read`

```python
@overload
def read(filename: str, /) -> None:

@overload
def read(filename: str, doc_name: str, /) -> None:
```

Import one G-code file into the active document, creating one if needed.

Import one G-code file into the named document, creating it if needed.

Evidence: public stub `PathApp/__init__.pyi` line(s) 25, 30.

## `PathApp.show`

```python
def show(toolpath: Path, name: str='Path', /) -> None:
```

Create one document path feature from one standalone `Path` object.

Evidence: public stub `PathApp/__init__.pyi` line(s) 34.

## `PathApp.fromShape`

```python
@deprecated('since FreeCAD 26.3 and will be removed in FreeCAD 27.2; use fromShapes instead.')
def fromShape(shape: Shape, /) -> Path:
```

Convert one wire shape into one basic path object.

Evidence: public stub `PathApp/__init__.pyi` line(s) 39.

## `PathApp.fromShapes`

```python
@overload
def fromShapes(shapes: _ShapeInput, start: Vector | None=None, return_end: Literal[False]=False, arc_plane: _ArcPlane=1, sort_mode: _SortMode=1, abscissa: float=3.0, nearest_k: int=3, orientation: _Orientation=0, direction: _Direction=0, threshold: float=0.0, retract_axis: _RetractAxis=2, retraction: float=0.0, resume_height: float=0.0, segmentation: float=0.0, feedrate: float=0.0, feedrate_v: float=0.0, verbose: bool=True, abs_center: bool=False, preamble: bool=True, deflection: float=0.01) -> Path:

@overload
def fromShapes(shapes: _ShapeInput, start: Vector | None=None, return_end: Literal[True]=True, arc_plane: _ArcPlane=1, sort_mode: _SortMode=1, abscissa: float=3.0, nearest_k: int=3, orientation: _Orientation=0, direction: _Direction=0, threshold: float=0.0, retract_axis: _RetractAxis=2, retraction: float=0.0, resume_height: float=0.0, segmentation: float=0.0, feedrate: float=0.0, feedrate_v: float=0.0, verbose: bool=True, abs_center: bool=False, preamble: bool=True, deflection: float=0.01) -> tuple[Path, Vector]:
```

Convert one shape or shape sequence into one path object.

Convert one shape or shape sequence into one path object and return its end position.

Evidence: public stub `PathApp/__init__.pyi` line(s) 44, 49.

## `PathApp.sortWires`

```python
@overload
def sortWires(shapes: _ShapeInput, start: Vector | None=None, arc_plane: Literal[1]=1, sort_mode: _SortMode=1, abscissa: float=3.0, nearest_k: int=3, orientation: _Orientation=0, direction: _Direction=0, threshold: float=0.0, retract_axis: _RetractAxis=2) -> tuple[list[Wire], Vector, int]:

@overload
def sortWires(shapes: _ShapeInput, start: Vector | None=None, arc_plane: _ArcPlane=1, sort_mode: _SortMode=1, abscissa: float=3.0, nearest_k: int=3, orientation: _Orientation=0, direction: _Direction=0, threshold: float=0.0, retract_axis: _RetractAxis=2) -> _WireSortResult:
```

Sort one wire set and also return the resolved arc plane when auto-plane mode is used.

Sort one wire set and return the sorted wires plus their final end position.

Evidence: public stub `PathApp/__init__.pyi` line(s) 54, 59.

