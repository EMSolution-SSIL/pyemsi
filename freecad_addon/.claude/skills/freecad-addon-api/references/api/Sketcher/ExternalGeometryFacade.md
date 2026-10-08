# `Sketcher.ExternalGeometryFacade`

[Module](index.md)

```python
class ExternalGeometryFacade(BaseClass):
```

Describes a GeometryFacade

Author: Abdullah Tahiri (abdullah.tahiri.yo@gmail.com)
Licence: LGPL

Evidence: public stub `Sketcher/__init__.pyi` line 128. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Sketcher.ExternalGeometryFacade.Ref`

```python
Ref: str = ''
```

Returns the reference string of this external geometry.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 135.

## `Sketcher.ExternalGeometryFacade.Id`

```python
Id: int = 0
```

Sets/returns the Internal Alignment Type of the Geometry.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 137.

## `Sketcher.ExternalGeometryFacade.Construction`

```python
Construction: bool = False
```

Sets/returns this geometry as a construction one, which will not be part of a later built shape.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 139.

## `Sketcher.ExternalGeometryFacade.GeometryLayerId`

```python
GeometryLayerId: int = 0
```

Returns the Id of the geometry Layer in which the geometry is located.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 141.

## `Sketcher.ExternalGeometryFacade.InternalType`

```python
InternalType: str = ''
```

Sets/returns the Internal Alignment Type of the Geometry.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 143.

## `Sketcher.ExternalGeometryFacade.Blocked`

```python
Blocked: bool = False
```

Sets/returns whether the geometry is blocked or not.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 145.

## `Sketcher.ExternalGeometryFacade.Tag`

```python
Tag: Final[str] = ''
```

Gives the tag of the geometry as string.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 147.

## `Sketcher.ExternalGeometryFacade.Geometry`

```python
Geometry: object = ...
```

Returns the underlying geometry object.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 149.

## `Sketcher.ExternalGeometryFacade.testFlag`

```python
def testFlag(self, flag: str, /) -> bool:
```

Returns a boolean indicating whether the given bit is set.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 152.

## `Sketcher.ExternalGeometryFacade.setFlag`

```python
def setFlag(self, flag: str, on: bool=..., /) -> None:
```

Sets the given bit to true/false.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 158.

## `Sketcher.ExternalGeometryFacade.mirror`

```python
def mirror(self, point: Vector, axis: Vector=..., /) -> None:
```

Performs the symmetrical transformation of this geometric object

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 164.

## `Sketcher.ExternalGeometryFacade.rotate`

```python
def rotate(self, placement: Placement, /) -> None:
```

Rotates this geometric object at angle Ang (in radians) about axis

Evidence: public stub `Sketcher/__init__.pyi` line(s) 170.

## `Sketcher.ExternalGeometryFacade.scale`

```python
def scale(self, center: Vector | tuple[float, float, float], factor: float, /) -> None:
```

Applies a scaling transformation on this geometric object with a center and scaling factor

Evidence: public stub `Sketcher/__init__.pyi` line(s) 176.

## `Sketcher.ExternalGeometryFacade.transform`

```python
def transform(self, transformation: Matrix, /) -> None:
```

Applies a transformation to this geometric object

Evidence: public stub `Sketcher/__init__.pyi` line(s) 182.

## `Sketcher.ExternalGeometryFacade.translate`

```python
def translate(self, offset: Vector | tuple[float, float, float], /) -> None:
```

Translates this geometric object

Evidence: public stub `Sketcher/__init__.pyi` line(s) 188.

## `Sketcher.ExternalGeometryFacade.hasExtensionOfType`

```python
def hasExtensionOfType(self, type_str: str, /) -> bool:
```

Returns a boolean indicating whether a geometry extension of the type indicated as a string exists.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 194.

## `Sketcher.ExternalGeometryFacade.hasExtensionOfName`

```python
def hasExtensionOfName(self, name: str, /) -> bool:
```

Returns a boolean indicating whether a geometry extension with the name indicated as a string exists.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 200.

## `Sketcher.ExternalGeometryFacade.getExtensionOfType`

```python
def getExtensionOfType(self, type_str: str, /) -> GeometryExtension:
```

Gets the first geometry extension of the type indicated by the string.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 206.

## `Sketcher.ExternalGeometryFacade.getExtensionOfName`

```python
def getExtensionOfName(self, name: str, /) -> GeometryExtension:
```

Gets the first geometry extension of the name indicated by the string.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 212.

## `Sketcher.ExternalGeometryFacade.setExtension`

```python
def setExtension(self, extension: GeometryExtension, /) -> None:
```

Sets a geometry extension of the indicated type.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 218.

## `Sketcher.ExternalGeometryFacade.deleteExtensionOfType`

```python
def deleteExtensionOfType(self, type_str: str, /) -> None:
```

Deletes all extensions of the indicated type.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 224.

## `Sketcher.ExternalGeometryFacade.deleteExtensionOfName`

```python
def deleteExtensionOfName(self, name: str, /) -> None:
```

Deletes all extensions of the indicated name.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 230.

## `Sketcher.ExternalGeometryFacade.getExtensions`

```python
def getExtensions(self) -> List[GeometryExtension]:
```

Returns a list with information about the geometry extensions.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 236.

