# `DraftUtils`

[Catalogue index](../index.md)

Evidence: import-shaped public stub `DraftUtils/__init__.pyi`; generated binding/typing declarations, runtime unverified.

## Imports and aliases

These preserve stub type context and reexports. Imported typing helpers and underscored names are not a promise of supported runtime API.

```python
from __future__ import annotations
from typing import Any
from typing_extensions import deprecated
```

## `DraftUtils.readDXF`

```python
@deprecated('since FreeCAD 26.3 and will be removed in FreeCAD 28.3; use Import.readDXF instead; This compatibility entry point no longer imports files.')
def readDXF(filename: str, document: str | None=None, ignore_errors: bool=True, /) -> None:
```

Warn that the legacy Draft DXF helper is removed and return `None`.

Evidence: public stub `DraftUtils/__init__.pyi` line(s) 8.

