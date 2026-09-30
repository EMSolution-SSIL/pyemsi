# `PathGui`

[Catalogue index](../index.md)

Evidence: import-shaped public stub `PathGui/__init__.pyi`; generated binding/typing declarations, runtime unverified.

## Imports and aliases

These preserve stub type context and reexports. Imported typing helpers and underscored names are not a promise of supported runtime API.

```python
from __future__ import annotations
from typing import Any, overload
from collections.abc import Sequence
from FreeCAD import DocumentObject
```

## `PathGui.open`

```python
def open(filename: str, /) -> None:
```

Open one G-code file through the GUI processor chooser.

Evidence: public stub `PathGui/__init__.pyi` line(s) 9.

## `PathGui.insert`

```python
@overload
def insert(filename: str, /) -> None:

@overload
def insert(filename: str, doc_name: str, /) -> None:
```

Insert one G-code file into the active document through the GUI processor chooser.

Insert one G-code file into the named document through the GUI processor chooser.

Evidence: public stub `PathGui/__init__.pyi` line(s) 14, 19.

## `PathGui.export`

```python
def export(objects: Sequence[DocumentObject], filename: str, /) -> None:
```

Export selected path objects through the GUI post-processor chooser.

Evidence: public stub `PathGui/__init__.pyi` line(s) 23.

