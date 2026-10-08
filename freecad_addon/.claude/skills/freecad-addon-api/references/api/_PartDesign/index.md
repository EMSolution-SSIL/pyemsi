# `_PartDesign`

[Catalogue index](../index.md)

Evidence: import-shaped public stub `_PartDesign/__init__.pyi`; generated binding/typing declarations, runtime unverified.

## Imports and aliases

These preserve stub type context and reexports. Imported typing helpers and underscored names are not a promise of supported runtime API.

```python
from __future__ import annotations
from typing import Any
from typing import TypeAlias
from FreeCAD.Base import Vector
```

## `_PartDesign._FilletArcConstruction`

```python
_FilletArcConstruction: TypeAlias = tuple[Vector, Vector, Vector]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `_PartDesign/__init__.pyi` line(s) 8.

## `_PartDesign.makeFilletArc`

```python
def makeFilletArc(m1: Vector, p: Vector, q: Vector, n: Vector, radius: float, ccw: bool | int, /) -> _FilletArcConstruction:
```

Return the tangent points and arc center for one fillet-arc construction.

Evidence: public stub `_PartDesign/__init__.pyi` line(s) 10.

