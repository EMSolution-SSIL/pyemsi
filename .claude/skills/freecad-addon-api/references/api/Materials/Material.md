# `Materials.Material`

[Module](index.md)

```python
class Material(BaseClass):
```

Material descriptions.

Author: David Carter (dcarter@davidcarter.ca)
Licence: LGPL

Evidence: public stub `Materials/__init__.pyi` line 100. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Materials.Material.LibraryName`

```python
LibraryName: Final[str] = ...
```

Material library name.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 107.

## `Materials.Material.LibraryRoot`

```python
LibraryRoot: Final[str] = ...
```

Material library path.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 109.

## `Materials.Material.LibraryIcon`

```python
LibraryIcon: Final[bytes] = ...
```

Material icon.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 111.

## `Materials.Material.Name`

```python
Name: str = ...
```

Material name.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 113.

## `Materials.Material.Directory`

```python
Directory: str = ...
```

Material directory relative to the library root.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 115.

## `Materials.Material.UUID`

```python
UUID: Final[str] = ...
```

Unique material identifier. This is only valid after the material is saved.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 117.

## `Materials.Material.Description`

```python
Description: str = ...
```

Description of the material.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 119.

## `Materials.Material.URL`

```python
URL: str = ...
```

URL to a material reference.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 121.

## `Materials.Material.Reference`

```python
Reference: str = ...
```

Reference for material data.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 123.

## `Materials.Material.Parent`

```python
Parent: str = ...
```

Parent material UUID.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 125.

## `Materials.Material.AuthorAndLicense`

```python
@property
@deprecated('since FreeCAD 26.3 and will be removed in FreeCAD 27.2; use Author and License instead.')
def AuthorAndLicense(self) -> str:
```

deprecated -- Author and license information.

Access: getter only declared in the stub.

Evidence: public stub `Materials/__init__.pyi` line(s) 130.

## `Materials.Material.Author`

```python
Author: str = ...
```

Author information.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 133.

## `Materials.Material.License`

```python
License: str = ...
```

License information.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 135.

## `Materials.Material.PhysicalModels`

```python
PhysicalModels: Final[list] = ...
```

List of implemented models.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 137.

## `Materials.Material.AppearanceModels`

```python
AppearanceModels: Final[list] = ...
```

List of implemented models.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 139.

## `Materials.Material.Tags`

```python
Tags: Final[list] = ...
```

List of searchable tags.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 141.

## `Materials.Material.Properties`

```python
@property
@deprecated('since FreeCAD 26.3 and will be removed in FreeCAD 27.2; use PropertyObjects instead; Legacy compatibility API.')
def Properties(self) -> dict:
```

deprecated -- Dictionary of all material properties.

Access: getter only declared in the stub.

Evidence: public stub `Materials/__init__.pyi` line(s) 146.

## `Materials.Material.PhysicalProperties`

```python
@property
@deprecated('since FreeCAD 26.3 and will be removed in FreeCAD 27.2; use PropertyObjects instead; Legacy compatibility API.')
def PhysicalProperties(self) -> dict:
```

deprecated -- Dictionary of material physical properties.

Access: getter only declared in the stub.

Evidence: public stub `Materials/__init__.pyi` line(s) 152.

## `Materials.Material.AppearanceProperties`

```python
@property
@deprecated('since FreeCAD 26.3 and will be removed in FreeCAD 27.2; use PropertyObjects instead; Legacy compatibility API.')
def AppearanceProperties(self) -> dict:
```

deprecated -- Dictionary of material appearance properties.

Access: getter only declared in the stub.

Evidence: public stub `Materials/__init__.pyi` line(s) 158.

## `Materials.Material.LegacyProperties`

```python
@property
@deprecated('since FreeCAD 26.3 and will be removed in FreeCAD 27.2; use PropertyObjects instead; Legacy compatibility API.')
def LegacyProperties(self) -> dict:
```

deprecated -- Dictionary of material legacy properties.

Access: getter only declared in the stub.

Evidence: public stub `Materials/__init__.pyi` line(s) 164.

## `Materials.Material.PropertyObjects`

```python
PropertyObjects: Final[dict] = ...
```

Dictionary of MaterialProperty objects.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Materials/__init__.pyi` line(s) 167.

## `Materials.Material.addPhysicalModel`

```python
def addPhysicalModel(self, uuid: str, /) -> None:
```

Add the physical model with the given UUID

Evidence: public stub `Materials/__init__.pyi` line(s) 170.

## `Materials.Material.removePhysicalModel`

```python
def removePhysicalModel(self, uuid: str, /) -> None:
```

Remove the physical model with the given UUID

Evidence: public stub `Materials/__init__.pyi` line(s) 174.

## `Materials.Material.hasPhysicalModel`

```python
def hasPhysicalModel(self, uuid: str, /) -> bool:
```

Check if the material implements the physical model with the given UUID

Evidence: public stub `Materials/__init__.pyi` line(s) 178.

## `Materials.Material.addAppearanceModel`

```python
def addAppearanceModel(self, uuid: str, /) -> None:
```

Add the appearance model with the given UUID

Evidence: public stub `Materials/__init__.pyi` line(s) 182.

## `Materials.Material.removeAppearanceModel`

```python
def removeAppearanceModel(self, uuid: str, /) -> None:
```

Remove the appearance model with the given UUID

Evidence: public stub `Materials/__init__.pyi` line(s) 186.

## `Materials.Material.hasAppearanceModel`

```python
def hasAppearanceModel(self, uuid: str, /) -> bool:
```

Check if the material implements the appearance model with the given UUID

Evidence: public stub `Materials/__init__.pyi` line(s) 190.

## `Materials.Material.isPhysicalModelComplete`

```python
def isPhysicalModelComplete(self, uuid: str, /) -> bool:
```

Check if the material implements the physical model with the given UUID, and has values defined for each property

Evidence: public stub `Materials/__init__.pyi` line(s) 194.

## `Materials.Material.isAppearanceModelComplete`

```python
def isAppearanceModelComplete(self, uuid: str, /) -> bool:
```

Check if the material implements the appearance model with the given UUID, and has values defined for each property

Evidence: public stub `Materials/__init__.pyi` line(s) 198.

## `Materials.Material.hasPhysicalProperty`

```python
def hasPhysicalProperty(self, name: str, /) -> bool:
```

Check if the material implements the physical property with the given name

Evidence: public stub `Materials/__init__.pyi` line(s) 202.

## `Materials.Material.hasAppearanceProperty`

```python
def hasAppearanceProperty(self, name: str, /) -> bool:
```

Check if the material implements the appearance property with the given name

Evidence: public stub `Materials/__init__.pyi` line(s) 206.

## `Materials.Material.hasLegacyProperties`

```python
def hasLegacyProperties(self) -> bool:
```

Returns true of there are legacy properties

Evidence: public stub `Materials/__init__.pyi` line(s) 210.

## `Materials.Material.getPhysicalValue`

```python
def getPhysicalValue(self, name: str, /) -> Quantity | float | int | bool | str | list | Array2D | Array3D | None:
```

Get the value of the named physical property, or None if the material does not have it

Evidence: public stub `Materials/__init__.pyi` line(s) 214.

## `Materials.Material.setPhysicalValue`

```python
def setPhysicalValue(self, name: str, value: str, /) -> None:
```

Set the value of the named physical property

Evidence: public stub `Materials/__init__.pyi` line(s) 218.

## `Materials.Material.getAppearanceValue`

```python
def getAppearanceValue(self, name: str, /) -> Quantity | float | int | bool | str | list | Array2D | Array3D | None:
```

Get the value of the named appearance property, or None if the material does not have it

Evidence: public stub `Materials/__init__.pyi` line(s) 222.

## `Materials.Material.setAppearanceValue`

```python
def setAppearanceValue(self, name: str, value: str, /) -> None:
```

Set the value of the named appearance property

Evidence: public stub `Materials/__init__.pyi` line(s) 226.

## `Materials.Material.setValue`

```python
def setValue(self, name: str, value: str | list[str] | Array2D | Array3D, /) -> None:
```

Set the value of the named property

Evidence: public stub `Materials/__init__.pyi` line(s) 230.

## `Materials.Material.keys`

```python
def keys(self) -> list:
```

Property keys

Evidence: public stub `Materials/__init__.pyi` line(s) 234.

## `Materials.Material.values`

```python
def values(self) -> list:
```

Property values

Evidence: public stub `Materials/__init__.pyi` line(s) 238.

