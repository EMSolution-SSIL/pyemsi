# `Materials.Array3D`

[Module](index.md)

```python
class Array3D(BaseClass):
```

3D Array of material properties.

Author: DavidCarter (dcarter@davidcarter.ca)
Licence: LGPL

Evidence: public stub `Materials/__init__.pyi` line 47. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Materials.Array3D.Array`

```python
Array: Final[List] = ...
```

The 3 dimensional array.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 54.

## `Materials.Array3D.Dimensions`

```python
Dimensions: Final[int] = ...
```

The number of dimensions in the array, in this case 3.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 56.

## `Materials.Array3D.Columns`

```python
Columns: int = ...
```

The number of columns in the array.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 58.

## `Materials.Array3D.Depth`

```python
Depth: int = ...
```

The depth of the array (3rd dimension).

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 60.

## `Materials.Array3D.getRows`

```python
def getRows(self, depth: int=..., /) -> int:
```

Get the number of rows in the array at the specified depth.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Materials/__init__.pyi` line(s) 63.

## `Materials.Array3D.getValue`

```python
def getValue(self, depth: int, row: int, column: int, /) -> Quantity:
```

Get the value at the given row and column

Evidence: public stub `Materials/__init__.pyi` line(s) 69.

## `Materials.Array3D.getDepthValue`

```python
def getDepthValue(self, depth: int, /) -> Quantity:
```

Get the column value at the given depth

Evidence: public stub `Materials/__init__.pyi` line(s) 75.

## `Materials.Array3D.setDepthValue`

```python
def setDepthValue(self, depth: int, value: str, /) -> None:
```

Set the column value at the given depth

Evidence: public stub `Materials/__init__.pyi` line(s) 81.

## `Materials.Array3D.setValue`

```python
def setValue(self, depth: int, row: int, column: int, value: str, /) -> None:
```

Set the value at the given depth, row, and column

Evidence: public stub `Materials/__init__.pyi` line(s) 87.

## `Materials.Array3D.setRows`

```python
def setRows(self, depth: int, rows: int, /) -> None:
```

Set the number of rows at the given depth

Evidence: public stub `Materials/__init__.pyi` line(s) 93.

