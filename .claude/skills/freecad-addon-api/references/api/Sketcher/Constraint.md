# `Sketcher.Constraint`

[Module](index.md)

```python
class Constraint(Persistence):
```

With this object you can handle sketches

Author: Juergen Riegel (FreeCAD@juergen-riegel.net)
Licence: LGPL

Evidence: public stub `Sketcher/__init__.pyi` line 34. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Sketcher.Constraint.__init__`

```python
@overload
def __init__(self) -> None:

@overload
def __init__(self, constraint_type: str, elements: list[int], /) -> None:

@overload
def __init__(self, constraint_type: str, elements: list[int], text: str, font: str, is_text_height: bool=..., /) -> None:

@overload
def __init__(self, constraint_type: str, first_index: int, /) -> None:

@overload
def __init__(self, constraint_type: str, first_index: int, second: int | float | Quantity, activated: bool=..., driving: bool=..., /) -> None:

@overload
def __init__(self, constraint_type: str, first_index: int, first_position: int, second: int | float | Quantity, activated: bool=..., driving: bool=..., /) -> None:

@overload
def __init__(self, constraint_type: str, first_index: int, first_position: int, second: int, value: int | float | Quantity, activated: bool=..., driving: bool=..., /) -> None:

@overload
def __init__(self, constraint_type: str, first_index: int, first_position: int, second: int, second_position: int, third: int | float | Quantity, activated: bool=..., driving: bool=..., /) -> None:

@overload
def __init__(self, constraint_type: str, first_index: int, first_position: int, second: int, second_position: int, third: int, third_position: int | float | Quantity, activated: bool=..., driving: bool=..., /) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 43, 47, 51, 55, 59, 63, 67, 71, 75.

## `Sketcher.Constraint.Type`

```python
Type: Final[str] = ''
```

Get the constraint type

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 77.

## `Sketcher.Constraint.First`

```python
First: int = 0
```

First geometry index the Constraint refers to

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 79.

## `Sketcher.Constraint.FirstPos`

```python
FirstPos: int = 0
```

Position of first geometry index the Constraint refers to

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 81.

## `Sketcher.Constraint.Second`

```python
Second: int = 0
```

Second geometry index the Constraint refers to

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 83.

## `Sketcher.Constraint.SecondPos`

```python
SecondPos: int = 0
```

Position of second geometry index the Constraint refers to

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 85.

## `Sketcher.Constraint.Third`

```python
Third: int = 0
```

Third geometry index the Constraint refers to

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 87.

## `Sketcher.Constraint.ThirdPos`

```python
ThirdPos: int = 0
```

Position of third geometry index the Constraint refers to

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 89.

## `Sketcher.Constraint.Value`

```python
Value: Final[float] = 0.0
```

Value of the Constraint

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 91.

## `Sketcher.Constraint.Name`

```python
Name: str = ''
```

Name of the constraint

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 93.

## `Sketcher.Constraint.Driving`

```python
Driving: Final[bool] = False
```

Driving Constraint

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 95.

## `Sketcher.Constraint.InVirtualSpace`

```python
InVirtualSpace: Final[bool] = False
```

Constraint in virtual space

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 97.

## `Sketcher.Constraint.IsActive`

```python
IsActive: Final[bool] = False
```

Returns whether the constraint active (enforced) or not

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 99.

## `Sketcher.Constraint.LabelDistance`

```python
LabelDistance: Final[float] = 0.0
```

Label distance

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 101.

## `Sketcher.Constraint.LabelPosition`

```python
LabelPosition: Final[float] = 0.0
```

Label position

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 103.

