# `Measure`

[Catalogue index](../index.md)

Evidence: import-shaped public stub `Measure/__init__.pyi`; generated binding/typing declarations, runtime unverified.

## Classes

- [Measure.MeasureBase](MeasureBase.md)
- [Measure.Measurement](Measurement.md)

## Imports and aliases

These preserve stub type context and reexports. Imported typing helpers and underscored names are not a promise of supported runtime API.

```python
from __future__ import annotations
from typing import Any
from FreeCAD import DocumentObject
from Part import Shape
from FreeCAD import Base as Base
from FreeCAD.Base import BaseClass
```

## `Measure.getLocatedTopoShape`

```python
def getLocatedTopoShape(root_object: DocumentObject, subname: str, /) -> Shape | None:
```

Resolve one document object subshape with its accumulated placement applied.

Evidence: public stub `Measure/__init__.pyi` line(s) 10.

