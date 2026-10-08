# `Materials.ModelProperty`

[Module](index.md)

```python
class ModelProperty(BaseClass):
```

Material property descriptions.

Author: DavidCarter (dcarter@davidcarter.ca)
Licence: LGPL

Evidence: public stub `Materials/__init__.pyi` line 442. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Materials.ModelProperty.Name`

```python
Name: str = ...
```

Property name.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 449.

## `Materials.ModelProperty.DisplayName`

```python
DisplayName: str = ...
```

Property display friendly name.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 451.

## `Materials.ModelProperty.Type`

```python
Type: str = ...
```

Property type.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 453.

## `Materials.ModelProperty.Units`

```python
Units: str = ...
```

Property units category.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 455.

## `Materials.ModelProperty.URL`

```python
URL: str = ...
```

URL to a detailed description of the property.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 457.

## `Materials.ModelProperty.Description`

```python
Description: str = ...
```

Property description.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 459.

## `Materials.ModelProperty.Columns`

```python
Columns: Final[list] = ...
```

List of array columns.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 461.

## `Materials.ModelProperty.Inheritance`

```python
Inheritance: Final[str] = ...
```

UUID of the model in which the property is defined.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 463.

## `Materials.ModelProperty.Inherited`

```python
Inherited: Final[bool] = ...
```

True if the property is inherited.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 465.

## `Materials.ModelProperty.addColumn`

```python
def addColumn(self, column: ModelProperty, /) -> None:
```

Add a model property column.

Evidence: public stub `Materials/__init__.pyi` line(s) 468.

