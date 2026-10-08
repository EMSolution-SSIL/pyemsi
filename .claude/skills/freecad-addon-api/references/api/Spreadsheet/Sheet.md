# `Spreadsheet.Sheet`

[Module](index.md)

```python
class Sheet(DocumentObject):
```

With this object you can manipulate spreadsheets

Author: Eivind Kvedalen (eivind@kvedalen.name)
License: LGPL-2.1-or-later

Evidence: public stub `Spreadsheet/__init__.pyi` line 38. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Spreadsheet.Sheet.cells`

```python
@property
def cells(self) -> PropertySheet:

@cells.setter
def cells(self, value: PropertySheet) -> None:
```

Cell contents

Access: getter and setter declared in the stub.

Evidence: public stub `Spreadsheet/__init__.pyi` line(s) 47, 52.

## `Spreadsheet.Sheet.columnWidths`

```python
@property
def columnWidths(self) -> PropertyColumnWidths:
```

Column widths

Access: getter only declared in the stub.

Evidence: public stub `Spreadsheet/__init__.pyi` line(s) 56.

## `Spreadsheet.Sheet.rowHeights`

```python
@property
def rowHeights(self) -> PropertyRowHeights:
```

Row heights

Access: getter only declared in the stub.

Evidence: public stub `Spreadsheet/__init__.pyi` line(s) 61.

## `Spreadsheet.Sheet.set`

```python
def set(self, address: str, contents: str, /) -> None:
```

Set data into a cell

Evidence: public stub `Spreadsheet/__init__.pyi` line(s) 65.

## `Spreadsheet.Sheet.get`

```python
def get(self, address: str, address_to: str | None=..., /) -> Any:
```

Get evaluated cell contents

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Spreadsheet/__init__.pyi` line(s) 69.

## `Spreadsheet.Sheet.getContents`

```python
def getContents(self, address: str, /) -> str:
```

Get cell contents

Evidence: public stub `Spreadsheet/__init__.pyi` line(s) 73.

## `Spreadsheet.Sheet.clear`

```python
def clear(self, address: str, all: bool=..., /) -> None:
```

Clear a cell

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Spreadsheet/__init__.pyi` line(s) 77.

## `Spreadsheet.Sheet.clearAll`

```python
def clearAll(self) -> None:
```

Clear all cells in the spreadsheet

Evidence: public stub `Spreadsheet/__init__.pyi` line(s) 81.

## `Spreadsheet.Sheet.importFile`

```python
def importFile(self, filename: str, delimiter: str=..., quote_char: str=..., escape_char: str=..., /) -> bool:
```

Import file into spreadsheet

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Spreadsheet/__init__.pyi` line(s) 85.

## `Spreadsheet.Sheet.exportFile`

```python
def exportFile(self, filename: str, delimiter: str=..., quote_char: str=..., escape_char: str=..., /) -> bool:
```

Export file from spreadsheet

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Spreadsheet/__init__.pyi` line(s) 89.

## `Spreadsheet.Sheet.mergeCells`

```python
def mergeCells(self, range: str, /) -> None:
```

Merge given cell area into one cell

Evidence: public stub `Spreadsheet/__init__.pyi` line(s) 93.

## `Spreadsheet.Sheet.splitCell`

```python
def splitCell(self, address: str, /) -> None:
```

Split a previously merged cell

Evidence: public stub `Spreadsheet/__init__.pyi` line(s) 97.

## `Spreadsheet.Sheet.insertColumns`

```python
def insertColumns(self, column: str, count: int, /) -> None:
```

Insert a given number of columns into the spreadsheet.

Evidence: public stub `Spreadsheet/__init__.pyi` line(s) 101.

## `Spreadsheet.Sheet.removeColumns`

```python
def removeColumns(self, column: str, count: int, /) -> None:
```

Remove a given number of columns from the spreadsheet.

Evidence: public stub `Spreadsheet/__init__.pyi` line(s) 105.

## `Spreadsheet.Sheet.insertRows`

```python
def insertRows(self, row: str, count: int, /) -> None:
```

Insert a given number of rows into the spreadsheet.

Evidence: public stub `Spreadsheet/__init__.pyi` line(s) 109.

## `Spreadsheet.Sheet.removeRows`

```python
def removeRows(self, row: str, count: int, /) -> None:
```

Remove a given number of rows from the spreadsheet.

Evidence: public stub `Spreadsheet/__init__.pyi` line(s) 113.

## `Spreadsheet.Sheet.setAlignment`

```python
def setAlignment(self, cell: str, value: 'str | Spreadsheet.set[str]', options: str=..., /) -> None:
```

Set alignment of the cell

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Spreadsheet/__init__.pyi` line(s) 117.

## `Spreadsheet.Sheet.getAlignment`

```python
def getAlignment(self, address: str, /) -> 'Spreadsheet.set[str] | None':
```

Get alignment of the cell

Evidence: public stub `Spreadsheet/__init__.pyi` line(s) 121.

## `Spreadsheet.Sheet.setStyle`

```python
def setStyle(self, cell: str, value: 'str | Spreadsheet.set[str]', options: str=..., /) -> None:
```

Set style of the cell

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Spreadsheet/__init__.pyi` line(s) 125.

## `Spreadsheet.Sheet.getStyle`

```python
def getStyle(self, address: str, /) -> 'Spreadsheet.set[str] | None':
```

Get style of the cell

Evidence: public stub `Spreadsheet/__init__.pyi` line(s) 129.

## `Spreadsheet.Sheet.setDisplayUnit`

```python
def setDisplayUnit(self, cell: str, value: str, /) -> None:
```

Set display unit for cell

Evidence: public stub `Spreadsheet/__init__.pyi` line(s) 133.

## `Spreadsheet.Sheet.setAlias`

```python
def setAlias(self, address: str, value: str | None, /) -> None:
```

Set alias for cell address

Evidence: public stub `Spreadsheet/__init__.pyi` line(s) 137.

## `Spreadsheet.Sheet.getAlias`

```python
def getAlias(self, address: str, /) -> str | None:
```

Get alias for cell address

Evidence: public stub `Spreadsheet/__init__.pyi` line(s) 141.

## `Spreadsheet.Sheet.getCellFromAlias`

```python
def getCellFromAlias(self, alias: str, /) -> str | None:
```

Get cell address given an alias

Evidence: public stub `Spreadsheet/__init__.pyi` line(s) 145.

## `Spreadsheet.Sheet.getDisplayUnit`

```python
def getDisplayUnit(self, address: str, /) -> str | None:
```

Get display unit for cell

Evidence: public stub `Spreadsheet/__init__.pyi` line(s) 149.

## `Spreadsheet.Sheet.setForeground`

```python
def setForeground(self, address: str, value: tuple[float, ...], /) -> None:
```

Set foreground color of the cell

Evidence: public stub `Spreadsheet/__init__.pyi` line(s) 153.

## `Spreadsheet.Sheet.clearForeground`

```python
def clearForeground(self, address: str, /) -> None:
```

Clears foreground color of the cell

Evidence: public stub `Spreadsheet/__init__.pyi` line(s) 157.

## `Spreadsheet.Sheet.getForeground`

```python
def getForeground(self, address: str, /) -> tuple[float, float, float, float] | None:
```

Get foreground color of the cell

Evidence: public stub `Spreadsheet/__init__.pyi` line(s) 161.

## `Spreadsheet.Sheet.setBackground`

```python
def setBackground(self, address: str, value: tuple[float, ...], /) -> None:
```

Set background color of the cell

Evidence: public stub `Spreadsheet/__init__.pyi` line(s) 165.

## `Spreadsheet.Sheet.clearBackground`

```python
def clearBackground(self, address: str, /) -> None:
```

Clears background color of the cell

Evidence: public stub `Spreadsheet/__init__.pyi` line(s) 169.

## `Spreadsheet.Sheet.getBackground`

```python
def getBackground(self, address: str, /) -> tuple[float, float, float, float] | None:
```

Get background color of the cell

Evidence: public stub `Spreadsheet/__init__.pyi` line(s) 173.

## `Spreadsheet.Sheet.setColumnWidth`

```python
def setColumnWidth(self, column: str, width: int, /) -> None:
```

Set given spreadsheet column to given width

Evidence: public stub `Spreadsheet/__init__.pyi` line(s) 177.

## `Spreadsheet.Sheet.getColumnWidth`

```python
def getColumnWidth(self, column: str, /) -> int:
```

Get given spreadsheet column width

Evidence: public stub `Spreadsheet/__init__.pyi` line(s) 181.

## `Spreadsheet.Sheet.setRowHeight`

```python
def setRowHeight(self, row: str, height: int, /) -> None:
```

Set given spreadsheet row to given height

Evidence: public stub `Spreadsheet/__init__.pyi` line(s) 185.

## `Spreadsheet.Sheet.getRowHeight`

```python
def getRowHeight(self, row: str, /) -> int:
```

Get given spreadsheet row height

Evidence: public stub `Spreadsheet/__init__.pyi` line(s) 189.

## `Spreadsheet.Sheet.touchCells`

```python
def touchCells(self, address: str, address_to: str | None=None, /) -> None:
```

touch cells in the given range

Evidence: public stub `Spreadsheet/__init__.pyi` line(s) 193.

## `Spreadsheet.Sheet.recomputeCells`

```python
def recomputeCells(self, address: str, address_to: str | None=..., /) -> None:
```

Manually recompute cells in the given range with the given order without
following dependency order.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Spreadsheet/__init__.pyi` line(s) 197.

## `Spreadsheet.Sheet.getUsedCells`

```python
def getUsedCells(self) -> list[str]:
```

Get a list of the names of all cells that are marked as used. These cells may
or may not have a non-empty string content.

Evidence: public stub `Spreadsheet/__init__.pyi` line(s) 204.

## `Spreadsheet.Sheet.getNonEmptyCells`

```python
def getNonEmptyCells(self) -> list[str]:
```

Get a list of the names of all cells with data in them.

Evidence: public stub `Spreadsheet/__init__.pyi` line(s) 211.

## `Spreadsheet.Sheet.getUsedRange`

```python
def getUsedRange(self) -> tuple[str, str] | None:
```

Get a the total range of the used cells in a sheet, as a pair of strings
representing the lowest row and column that are used, and the highest row and
column that are used (inclusive). Note that the actual first and last cell
of the block are not necessarily used.

Evidence: public stub `Spreadsheet/__init__.pyi` line(s) 217.

## `Spreadsheet.Sheet.getNonEmptyRange`

```python
def getNonEmptyRange(self) -> tuple[str, str]:
```

Get a the total range of the used cells in a sheet, as a pair of cell addresses
representing the lowest row and column that contain data, and the highest row and
column that contain data (inclusive). Note that the actual first and last cell
of the block do not necessarily contain anything.

Evidence: public stub `Spreadsheet/__init__.pyi` line(s) 226.

