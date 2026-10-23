# `Materials.Model`

[Module](index.md)

```python
class Model(BaseClass):
```

Material model descriptions.

Author: DavidCarter (dcarter@davidcarter.ca)
Licence: LGPL

Evidence: public stub `Materials/__init__.pyi` line 370. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Materials.Model.LibraryName`

```python
LibraryName: Final[str] = ''
```

Model library name.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 377.

## `Materials.Model.LibraryRoot`

```python
LibraryRoot: Final[str] = ''
```

Model library path.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 379.

## `Materials.Model.LibraryIcon`

```python
LibraryIcon: Final[bytes] = ''
```

Model icon.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 381.

## `Materials.Model.Name`

```python
Name: str = ''
```

Model name.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 383.

## `Materials.Model.Type`

```python
Type: str = ''
```

Model type.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 385.

## `Materials.Model.Directory`

```python
Directory: str = ''
```

Model directory.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 387.

## `Materials.Model.UUID`

```python
UUID: Final[str] = ''
```

Unique model identifier.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 389.

## `Materials.Model.Description`

```python
Description: str = ''
```

Description of the model.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 391.

## `Materials.Model.URL`

```python
URL: str = ''
```

URL to a detailed description of the model.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 393.

## `Materials.Model.DOI`

```python
DOI: str = ''
```

Digital Object Identifier (see https://doi.org/)

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 395.

## `Materials.Model.Inherited`

```python
Inherited: Final[List[str]] = []
```

List of inherited models identified by UUID.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 397.

## `Materials.Model.Properties`

```python
Properties: Final[Dict[str, str]] = {}
```

Dictionary of model properties.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 399.

## `Materials.Model.addInheritance`

```python
def addInheritance(self, uuid: str, /) -> None:
```

Add an inherited model.

Evidence: public stub `Materials/__init__.pyi` line(s) 402.

## `Materials.Model.addProperty`

```python
def addProperty(self, property: ModelProperty, /) -> None:
```

Add a model property.

Evidence: public stub `Materials/__init__.pyi` line(s) 408.

