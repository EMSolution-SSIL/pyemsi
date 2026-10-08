# `Materials.Array2D`

[Module](index.md)

```python
class Array2D(BaseClass):
```

2D Array of material properties.

Author: DavidCarter (dcarter@davidcarter.ca)
Licence: LGPL

Evidence: public stub `Materials/__init__.pyi` line 12. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Materials.Array2D.Array`

```python
Array: Final[List] = ...
```

The 2 dimensional array.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 19.

## `Materials.Array2D.Dimensions`

```python
Dimensions: Final[int] = ...
```

The number of dimensions in the array, in this case 2.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 21.

## `Materials.Array2D.Rows`

```python
Rows: int = ...
```

The number of rows in the array.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 23.

## `Materials.Array2D.Columns`

```python
Columns: int = ...
```

The number of columns in the array.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 25.

## `Materials.Array2D.getRow`

```python
def getRow(self, value: int, /) -> List[Quantity]:
```

Get the row given the first column value

Evidence: public stub `Materials/__init__.pyi` line(s) 28.

## `Materials.Array2D.getValue`

```python
def getValue(self, row: int, column: int, /) -> Quantity:
```

Get the value at the given row and column

Evidence: public stub `Materials/__init__.pyi` line(s) 34.

## `Materials.Array2D.setValue`

```python
def setValue(self, row: int, column: int, value: str, /) -> None:
```

Set the value at the given row and column

Evidence: public stub `Materials/__init__.pyi` line(s) 40.

