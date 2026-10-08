# `Points`

[Catalogue index](../index.md)

Evidence: import-shaped public stub `Points/__init__.pyi`; generated binding/typing declarations, runtime unverified.

## Classes

- [Points.Points](Points.md)

## Imports and aliases

These preserve stub type context and reexports. Imported typing helpers and underscored names are not a promise of supported runtime API.

```python
from __future__ import annotations
from typing import Any
from collections.abc import Sequence
from FreeCAD import DocumentObject
import Points
from typing import Final
from typing import Sequence
from FreeCAD.Base import Vector
```

## `Points.open`

```python
def open(name: str, /) -> None:
```

Open one ASC, E57, PLY, or PCD point-cloud file into a new document.

Evidence: public stub `Points/__init__.pyi` line(s) 9.

## `Points.insert`

```python
def insert(name: str, doc_name: str, /) -> None:
```

Insert one ASC, E57, PLY, or PCD point-cloud file into the named document.

Evidence: public stub `Points/__init__.pyi` line(s) 13.

## `Points.export`

```python
def export(objectList: Sequence[DocumentObject], filename: str, /) -> None:
```

Export the first selected points feature to one ASC, PLY, or PCD file.

Evidence: public stub `Points/__init__.pyi` line(s) 17.

## `Points.show`

```python
def show(points: Points, name: str='Points', /) -> DocumentObject:
```

Create one document object from one `Points` kernel in the active document.

Evidence: public stub `Points/__init__.pyi` line(s) 21.

