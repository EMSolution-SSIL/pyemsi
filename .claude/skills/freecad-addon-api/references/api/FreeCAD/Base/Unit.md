# `FreeCAD.Base.Unit`

[Module](index.md)

```python
class Unit:
```

Unit
defines a unit type, calculate and compare.

The following constructors are supported:
Unit()                        -- empty constructor
Unit(i1,i2,i3,i4,i5,i6,i7,i8) -- unit signature
Unit(Quantity)                -- copy unit from Quantity
Unit(Unit)                    -- copy constructor
Unit(string)                  -- parse the string for units

Author: Juergen Riegel (FreeCAD@juergen-riegel.net)
Licence: LGPL

Evidence: public stub `FreeCAD/Base.pyi` line 1697. Inherited members are on the named base's reference; aliases keep their imported identity.

## `FreeCAD.Base.Unit.__init__`

```python
@overload
def __init__(self, i1: int=0, i2: int=0, i3: int=0, i4: int=0, i5: int=0, i6: int=0, i7: int=0, i8: int=0, /) -> None:

@overload
def __init__(self, quantity: Quantity, /) -> None:

@overload
def __init__(self, unit: Unit, /) -> None:

@overload
def __init__(self, string: str, /) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1714, 1718, 1722, 1726.

## `FreeCAD.Base.Unit.TypeId`

```python
TypeId: Final[str] = ...
```

holds the unit type as a string, e.g. 'Area'.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1728.

## `FreeCAD.Base.Unit.Signature`

```python
Signature: Final[tuple[int, ...]] = ...
```

Returns the signature.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1730.

