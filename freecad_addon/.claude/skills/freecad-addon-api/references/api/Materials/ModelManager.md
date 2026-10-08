# `Materials.ModelManager`

[Module](index.md)

```python
class ModelManager(BaseClass):
```

Material model descriptions.

Author: DavidCarter (dcarter@davidcarter.ca)
Licence: LGPL

Evidence: public stub `Materials/__init__.pyi` line 415. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Materials.ModelManager.ModelLibraries`

```python
ModelLibraries: Final[List] = ...
```

List of model libraries.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 422.

## `Materials.ModelManager.LocalModelLibraries`

```python
LocalModelLibraries: Final[List] = ...
```

List of local model libraries.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 424.

## `Materials.ModelManager.Models`

```python
Models: Final[Dict] = ...
```

List of model libraries.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 426.

## `Materials.ModelManager.getModel`

```python
def getModel(self, uuid: str, /) -> Model:
```

Get a model object by specifying its UUID

Evidence: public stub `Materials/__init__.pyi` line(s) 429.

## `Materials.ModelManager.getModelByPath`

```python
def getModelByPath(self, path: str, library: str='', /) -> Model:
```

Get a model object by specifying its path and optional library name

Evidence: public stub `Materials/__init__.pyi` line(s) 435.

