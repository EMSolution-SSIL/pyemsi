# `Materials.MaterialFilter`

[Module](index.md)

```python
class MaterialFilter(BaseClass):
```

Material filters.

Author: DavidCarter (dcarter@davidcarter.ca)
Licence: LGPL

Evidence: public stub `Materials/__init__.pyi` line 243. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Materials.MaterialFilter.Name`

```python
Name: str = ...
```

Name of the filter used to select a filter in a list

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 250.

## `Materials.MaterialFilter.RequiredModels`

```python
RequiredModels: List = ...
```

Materials must include the specified models.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 252.

## `Materials.MaterialFilter.RequiredCompleteModels`

```python
RequiredCompleteModels: List = ...
```

Materials must have complete versions of the specified models.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 254.

