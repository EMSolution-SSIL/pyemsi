# `JtReader`

[Catalogue index](../index.md)

Evidence: import-shaped public stub `JtReader/__init__.pyi`; generated binding/typing declarations, runtime unverified.

## Imports and aliases

These preserve stub type context and reexports. Imported typing helpers and underscored names are not a promise of supported runtime API.

```python
from __future__ import annotations
from typing import Any
```

## `JtReader.read`

```python
def read(name: str, /) -> None:
```

Read one JT file through the reader backend without returning public geometry.

Evidence: public stub `JtReader/__init__.pyi` line(s) 6.

## `JtReader.open`

```python
def open(name: str, /) -> None:
```

Open one JT file into a new document.

Evidence: public stub `JtReader/__init__.pyi` line(s) 9.

## `JtReader.insert`

```python
def insert(name: str, doc_name: str, /) -> None:
```

Insert one JT file into the named document.

Evidence: public stub `JtReader/__init__.pyi` line(s) 12.

