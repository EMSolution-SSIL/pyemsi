# `FreeCAD.Base.Quantity`

[Module](index.md)

```python
class Quantity:
```

Quantity
defined by a value and a unit.

The following constructors are supported:
Quantity() -- empty constructor
Quantity(Value) -- empty constructor
Quantity(Value,Unit) -- empty constructor
Quantity(Quantity) -- copy constructor
Quantity(string) -- arbitrary mixture of numbers and chars defining a Quantity

Author: Juergen Riegel (FreeCAD@juergen-riegel.net)
Licence: LGPL

Evidence: public stub `FreeCAD/Base.pyi` line 1229. Inherited members are on the named base's reference; aliases keep their imported identity.

## `FreeCAD.Base.Quantity.Value`

```python
Value: float = ...
```

Numeric Value of the Quantity (in internal system mm,kg,s)

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1244.

## `FreeCAD.Base.Quantity.Unit`

```python
Unit: 'FreeCAD.Base.Unit' = ...
```

Unit of the Quantity

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1246.

## `FreeCAD.Base.Quantity.UserString`

```python
UserString: Final[str] = ...
```

Unit of the Quantity

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1248.

## `FreeCAD.Base.Quantity.Format`

```python
Format: dict[str, int | str] = ...
```

Format of the Quantity

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1250.

## `FreeCAD.Base.Quantity.__init__`

```python
@overload
def __init__(self) -> None:

@overload
def __init__(self, value: float) -> None:

@overload
def __init__(self, value: float, unit: 'FreeCAD.Base.Unit') -> None:

@overload
def __init__(self, quantity: 'Quantity') -> None:

@overload
def __init__(self, string: str) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1254, 1258, 1262, 1266, 1270.

## `FreeCAD.Base.Quantity.toStr`

```python
@overload
def toStr(self, /) -> str:

@overload
def toStr(self, decimals: int, /) -> str:

def toStr(self, decimals: int=..., /) -> str:
```

Returns a string representation rounded to number of decimals. If no decimals are specified then
the internal precision is used

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1274, 1278, 1281.

## `FreeCAD.Base.Quantity.getUserPreferred`

```python
def getUserPreferred(self) -> Tuple['Quantity', str]:
```

Returns a quantity with the translation factor and a string with the prevered unit

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1288.

## `FreeCAD.Base.Quantity.getValueAs`

```python
@overload
def getValueAs(self, unit: str, /) -> float:

@overload
def getValueAs(self, translation: float, i1: int=0, i2: int=0, i3: int=0, i4: int=0, i5: int=0, i6: int=0, i7: int=0, i8: int=0, /) -> float:

@overload
def getValueAs(self, unit: 'FreeCAD.Base.Unit', /) -> float:

@overload
def getValueAs(self, quantity: 'Quantity', /) -> float:

def getValueAs(self, *args) -> float:
```

Returns a floating point value as the provided unit

Following parameters are allowed:
getValueAs('m/s')  # unit string to parse
getValueAs(2.45,1) # translation value and unit signature
getValueAs(FreeCAD.Units.Pascal) # predefined standard units
getValueAs(Qantity('N/m^2')) # a quantity
getValueAs(Unit(0,1,0,0,0,0,0,0)) # a unit

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1295, 1299, 1303, 1307, 1310.

## `FreeCAD.Base.Quantity.__round__`

```python
@overload
def __round__(self, /) -> int:

@overload
def __round__(self, ndigits: int, /) -> float:

def __round__(self, ndigits: int=..., /) -> Union[int, float]:
```

Returns the Integral closest to x, rounding half toward even.
When an argument is passed, work like built-in round(x, ndigits).

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1324, 1328, 1331.

