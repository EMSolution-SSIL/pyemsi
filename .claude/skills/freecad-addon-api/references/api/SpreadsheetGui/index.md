# `SpreadsheetGui`

[Catalogue index](../index.md)

Evidence: import-shaped public stub `SpreadsheetGui/__init__.pyi`; generated binding/typing declarations, runtime unverified.

## Classes

- [SpreadsheetGui._SheetView](_SheetView.md)
- [SpreadsheetGui.ViewProviderSpreadsheet](ViewProviderSpreadsheet.md)

## Imports and aliases

These preserve stub type context and reexports. Imported typing helpers and underscored names are not a promise of supported runtime API.

```python
from __future__ import annotations
from typing import Any, overload
from typing import Any
from FreeCADGui import ViewProviderDocumentObject
```

## `SpreadsheetGui.open`

```python
@overload
def open(name: str, /) -> None:

@overload
def open(name: str, doc_name: str, /) -> None:
```

Open one tab-delimited text file into a new spreadsheet document.

Open one tab-delimited text file into a newly created named document.

Evidence: public stub `SpreadsheetGui/__init__.pyi` line(s) 7, 11.

## `SpreadsheetGui.insert`

```python
@overload
def insert(name: str, /) -> None:

@overload
def insert(name: str, doc_name: str, /) -> None:
```

Insert one tab-delimited text file into the active document, creating one if needed.

Insert one tab-delimited text file into the named document, creating it if needed.

Evidence: public stub `SpreadsheetGui/__init__.pyi` line(s) 15, 19.

