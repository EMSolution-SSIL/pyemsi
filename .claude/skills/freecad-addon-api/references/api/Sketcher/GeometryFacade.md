# `Sketcher.GeometryFacade`

[Module](index.md)

```python
class GeometryFacade(BaseClass):
```

Describes a GeometryFacade

Author: Abdullah Tahiri (abdullah.tahiri.yo@gmail.com)
Licence: LGPL

Evidence: public stub `Sketcher/__init__.pyi` line 242. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Sketcher.GeometryFacade.Id`

```python
Id: int = ...
```

Sets/returns the Id of the SketchGeometryExtension.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 249.

## `Sketcher.GeometryFacade.InternalType`

```python
InternalType: str = ...
```

Sets/returns the Internal Alignment Type of the Geometry.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 251.

## `Sketcher.GeometryFacade.Blocked`

```python
Blocked: bool = ...
```

Sets/returns whether the geometry is blocked or not.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 253.

## `Sketcher.GeometryFacade.Construction`

```python
Construction: bool = ...
```

Sets/returns this geometry as a construction one, which will not be part of a later built shape.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 255.

## `Sketcher.GeometryFacade.GeometryLayerId`

```python
GeometryLayerId: int = ...
```

Returns the Id of the geometry Layer in which the geometry is located.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 257.

## `Sketcher.GeometryFacade.Tag`

```python
Tag: Final[str] = ...
```

Gives the tag of the geometry as string.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 259.

## `Sketcher.GeometryFacade.Geometry`

```python
Geometry: object = ...
```

Returns the underlying geometry object.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 261.

## `Sketcher.GeometryFacade.testGeometryMode`

```python
def testGeometryMode(self, mode: str, /) -> bool:
```

Returns a boolean indicating whether the given bit is set.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 264.

## `Sketcher.GeometryFacade.setGeometryMode`

```python
def setGeometryMode(self, mode: str, on: bool=..., /) -> None:
```

Sets the given bit to true/false.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 270.

## `Sketcher.GeometryFacade.mirror`

```python
def mirror(self, point: Vector, axis: Vector=..., /) -> None:
```

Performs the symmetrical transformation of this geometric object

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 276.

## `Sketcher.GeometryFacade.rotate`

```python
def rotate(self, placement: Placement, /) -> None:
```

Rotates this geometric object at angle Ang (in radians) about axis

Evidence: public stub `Sketcher/__init__.pyi` line(s) 282.

## `Sketcher.GeometryFacade.scale`

```python
def scale(self, center: Vector | tuple[float, float, float], factor: float, /) -> None:
```

Applies a scaling transformation on this geometric object with a center and scaling factor

Evidence: public stub `Sketcher/__init__.pyi` line(s) 288.

## `Sketcher.GeometryFacade.transform`

```python
def transform(self, transformation: Matrix, /) -> None:
```

Applies a transformation to this geometric object

Evidence: public stub `Sketcher/__init__.pyi` line(s) 294.

## `Sketcher.GeometryFacade.translate`

```python
def translate(self, offset: Vector | tuple[float, float, float], /) -> None:
```

Translates this geometric object

Evidence: public stub `Sketcher/__init__.pyi` line(s) 300.

## `Sketcher.GeometryFacade.hasExtensionOfType`

```python
def hasExtensionOfType(self, type_str: str, /) -> bool:
```

Returns a boolean indicating whether a geometry extension of the type indicated as a string exists.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 306.

## `Sketcher.GeometryFacade.hasExtensionOfName`

```python
def hasExtensionOfName(self, name: str, /) -> bool:
```

Returns a boolean indicating whether a geometry extension with the name indicated as a string exists.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 312.

## `Sketcher.GeometryFacade.getExtensionOfType`

```python
def getExtensionOfType(self, type_str: str, /) -> GeometryExtension:
```

Gets the first geometry extension of the type indicated by the string.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 318.

## `Sketcher.GeometryFacade.getExtensionOfName`

```python
def getExtensionOfName(self, name: str, /) -> GeometryExtension:
```

Gets the first geometry extension of the name indicated by the string.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 324.

## `Sketcher.GeometryFacade.setExtension`

```python
def setExtension(self, extension: GeometryExtension, /) -> None:
```

Sets a geometry extension of the indicated type.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 330.

## `Sketcher.GeometryFacade.deleteExtensionOfType`

```python
def deleteExtensionOfType(self, type_str: str, /) -> None:
```

Deletes all extensions of the indicated type.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 336.

## `Sketcher.GeometryFacade.deleteExtensionOfName`

```python
def deleteExtensionOfName(self, name: str, /) -> None:
```

Deletes all extensions of the indicated name.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 342.

## `Sketcher.GeometryFacade.getExtensions`

```python
def getExtensions(self) -> List[GeometryExtension]:
```

Returns a list with information about the geometry extensions.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 348.

