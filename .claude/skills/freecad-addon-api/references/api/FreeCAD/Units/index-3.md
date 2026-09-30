# `FreeCAD.Units`

[Catalogue index](../../index.md)

Evidence: import-shaped public stub `FreeCAD/Units.pyi`; generated binding/typing declarations, runtime unverified.

[part 1](index.md) | [part 2](index-2.md) | [part 3](index-3.md)

## `FreeCAD.Units.YieldStrength`

```python
YieldStrength: Unit
```

Predefined dimensional unit for yield strength.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Units.pyi` line(s) 363.

## `FreeCAD.Units.YoungsModulus`

```python
YoungsModulus: Unit
```

Predefined dimensional unit for youngs modulus.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Units.pyi` line(s) 365.

## `FreeCAD.Units.getSchema`

```python
def getSchema() -> int:
```

Return the active unit-schema index into the tuple returned by ``listSchemas``.

Evidence: public stub `FreeCAD/Units.pyi` line(s) 368.

## `FreeCAD.Units.listSchemas`

```python
@overload
def listSchemas() -> tuple[str, ...]:

@overload
def listSchemas(index: int, /) -> str:
```

Return the full ordered schema list.

Return one schema name by numeric index.

Evidence: public stub `FreeCAD/Units.pyi` line(s) 373, 378.

## `FreeCAD.Units.parseQuantity`

```python
def parseQuantity(expression: str, /) -> Quantity:
```

Parse one unit expression into a Quantity.

The expression may be a simple value with units, such as ``"1m"``, or a
compound unit expression that FreeCAD's quantity parser understands.

Evidence: public stub `FreeCAD/Units.pyi` line(s) 382.

## `FreeCAD.Units.schemaTranslate`

```python
def schemaTranslate(quantity: Quantity, schema: int, /) -> tuple[str, float, str]:
```

Translate one quantity into the textual pieces used by another schema.

Evidence: public stub `FreeCAD/Units.pyi` line(s) 391.

## `FreeCAD.Units.setSchema`

```python
def setSchema(index: int, /) -> None:
```

Set the active unit-schema index.

Evidence: public stub `FreeCAD/Units.pyi` line(s) 395.

## `FreeCAD.Units.toNumber`

```python
@overload
def toNumber(value: Quantity, format: _NumberFormat=..., decimals: int=..., /) -> str:

@overload
def toNumber(value: float, format: _NumberFormat=..., decimals: int=..., /) -> str:
```

Format an existing Quantity value using the current unit schema.

Format a plain numeric value using the current unit schema.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `FreeCAD/Units.pyi` line(s) 400, 405.

