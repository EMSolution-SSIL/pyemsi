# `Sketcher`

[Catalogue index](../index.md)

Evidence: import-shaped public stub `Sketcher/__init__.pyi`; generated binding/typing declarations, runtime unverified.

## Classes

- [Sketcher.Constraint](Constraint.md)
- [Sketcher.ExternalGeometryExtension](ExternalGeometryExtension.md)
- [Sketcher.ExternalGeometryFacade](ExternalGeometryFacade.md)
- [Sketcher.GeometryFacade](GeometryFacade.md)
- [Sketcher.Sketch](Sketch.md)
- [Sketcher.SketchGeometryExtension](SketchGeometryExtension.md)
- [Sketcher.SketchObject](SketchObject.md)
- [Sketcher.SketchObjectSF](SketchObjectSF.md)

## Imports and aliases

These preserve stub type context and reexports. Imported typing helpers and underscored names are not a promise of supported runtime API.

```python
from __future__ import annotations
from typing import Any
from collections.abc import Sequence
import Part as Part
from FreeCAD.Base import Persistence
from typing import overload
from typing import Final
from FreeCAD.Base import Quantity
from Part import GeometryExtension
from FreeCAD.Base import BaseClass
from typing import List
from FreeCAD.Base import Vector
from FreeCAD.Base import Placement
from FreeCAD.Base import Matrix
import Sketcher
from typing import Tuple
from typing import Union
from Part import Geometry
from Part import Part2DObject
from FreeCAD.Base import Axis
from typing_extensions import deprecated
```

## `Sketcher.open`

```python
def open(name: str, /) -> None:
```

Open one sketch import file through the Sketcher module entry point.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 9.

## `Sketcher.insert`

```python
def insert(name: str, doc_name: str, /) -> None:
```

Insert one `.skf` sketch flat file into the named document.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 13.

