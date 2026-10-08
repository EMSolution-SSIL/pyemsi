# `Materials.MaterialManager`

[Module](index.md)

```python
class MaterialManager(BaseClass):
```

Material descriptions.

Author: DavidCarter (dcarter@davidcarter.ca)
Licence: LGPL

Evidence: public stub `Materials/__init__.pyi` line 296. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Materials.MaterialManager.MaterialLibraries`

```python
MaterialLibraries: Final[List] = ...
```

List of Material libraries.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 303.

## `Materials.MaterialManager.Materials`

```python
Materials: Final[Dict] = ...
```

List of Materials.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 305.

## `Materials.MaterialManager.getMaterial`

```python
def getMaterial(self, uuid: str, /) -> Material:
```

Get a material object by specifying its UUID

Evidence: public stub `Materials/__init__.pyi` line(s) 308.

## `Materials.MaterialManager.getMaterialByPath`

```python
def getMaterialByPath(self, path: str, library: str='', /) -> Material:
```

Get a material object by specifying its path and library name

Evidence: public stub `Materials/__init__.pyi` line(s) 314.

## `Materials.MaterialManager.inheritMaterial`

```python
def inheritMaterial(self, uuid: str, /) -> Material:
```

Create a new material object by specifying the UUID of its parent

Evidence: public stub `Materials/__init__.pyi` line(s) 320.

## `Materials.MaterialManager.materialsWithModel`

```python
def materialsWithModel(self, uuid: str, /) -> Dict[str, Material]:
```

Get a dictionary of materials implementing the specified model, keyed by material UUID

Evidence: public stub `Materials/__init__.pyi` line(s) 326.

## `Materials.MaterialManager.materialsWithModelComplete`

```python
def materialsWithModelComplete(self, uuid: str, /) -> Dict[str, Material]:
```

Get a dictionary of materials implementing the specified model, with values for all properties, keyed by material UUID

Evidence: public stub `Materials/__init__.pyi` line(s) 332.

## `Materials.MaterialManager.save`

```python
def save(self, library: str, material: Material, path: str, overwrite: bool=False, saveAsCopy: bool=False, saveInherited: bool=False) -> None:
```

Save the material in the specified library

Evidence: public stub `Materials/__init__.pyi` line(s) 338.

## `Materials.MaterialManager.filterMaterials`

```python
def filterMaterials(self, filter: MaterialFilter, includeLegacy: bool=False) -> list:
```

Returns a filtered material list

Evidence: public stub `Materials/__init__.pyi` line(s) 344.

## `Materials.MaterialManager.refresh`

```python
def refresh(self) -> None:
```

Refreshes the material tree. Use sparingly as this is an expensive operation.

Evidence: public stub `Materials/__init__.pyi` line(s) 350.

