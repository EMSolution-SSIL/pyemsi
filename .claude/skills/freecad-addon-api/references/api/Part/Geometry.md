# `Part.Geometry`

[Module](index.md)

```python
class Geometry(Persistence):
```

The abstract class Geometry for 3D space is the root class of all geometric objects.
It describes the common behavior of these objects when:
- applying geometric transformations to objects, and
- constructing objects by geometric transformation (including copying).

Evidence: public stub `Part/__init__.pyi` line 2246. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.Geometry.Tag`

```python
Tag: Final[str]
```

Gives the tag of the geometry as string.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 2253.

## `Part.Geometry.mirror`

```python
def mirror(self, point: Vector, axis: Vector=..., /) -> None:
```

Performs the symmetrical transformation of this geometric object, either
about a point or about a plane defined by a point and an axis.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 2256.

## `Part.Geometry.rotate`

```python
def rotate(self, placement: Placement, /) -> None:
```

Rotates this geometric object by the given placement

Evidence: public stub `Part/__init__.pyi` line(s) 2263.

## `Part.Geometry.scale`

```python
def scale(self, center: Union[Vector, tuple], factor: float, /) -> None:
```

Applies a scaling transformation on this geometric object with a center and scaling factor

Evidence: public stub `Part/__init__.pyi` line(s) 2269.

## `Part.Geometry.transform`

```python
def transform(self, transformation: Matrix, /) -> None:
```

Applies a transformation to this geometric object

Evidence: public stub `Part/__init__.pyi` line(s) 2275.

## `Part.Geometry.translate`

```python
def translate(self, vector: Union[Vector, tuple], /) -> None:
```

Translates this geometric object

Evidence: public stub `Part/__init__.pyi` line(s) 2281.

## `Part.Geometry.copy`

```python
def copy(self) -> 'Geometry':
```

Create a copy of this geometry

Evidence: public stub `Part/__init__.pyi` line(s) 2287.

## `Part.Geometry.clone`

```python
def clone(self) -> 'Geometry':
```

Create a clone of this geometry with the same Tag

Evidence: public stub `Part/__init__.pyi` line(s) 2293.

## `Part.Geometry.isSame`

```python
def isSame(self, geom: 'Geometry', tol: float, angulartol: float, /) -> bool:
```

isSame(geom, tol, angulartol) -> boolean

Compare this geometry to another one

Evidence: public stub `Part/__init__.pyi` line(s) 2299.

## `Part.Geometry.hasExtensionOfType`

```python
def hasExtensionOfType(self, type_name: str, /) -> bool:
```

Returns a boolean indicating whether a geometry extension of the type indicated as a string exists.

Evidence: public stub `Part/__init__.pyi` line(s) 2307.

## `Part.Geometry.hasExtensionOfName`

```python
def hasExtensionOfName(self, name: str, /) -> bool:
```

Returns a boolean indicating whether a geometry extension with the name indicated as a string exists.

Evidence: public stub `Part/__init__.pyi` line(s) 2313.

## `Part.Geometry.getExtensionOfType`

```python
def getExtensionOfType(self, type_name: str, /) -> Extension:
```

Gets the first geometry extension of the type indicated by the string.

Evidence: public stub `Part/__init__.pyi` line(s) 2319.

## `Part.Geometry.getExtensionOfName`

```python
def getExtensionOfName(self, name: str, /) -> Extension:
```

Gets the first geometry extension of the name indicated by the string.

Evidence: public stub `Part/__init__.pyi` line(s) 2325.

## `Part.Geometry.setExtension`

```python
def setExtension(self, extension: Extension, /) -> None:
```

Sets a geometry extension of the indicated type.

Evidence: public stub `Part/__init__.pyi` line(s) 2331.

## `Part.Geometry.deleteExtensionOfType`

```python
def deleteExtensionOfType(self, type_name: str, /) -> None:
```

Deletes all extensions of the indicated type.

Evidence: public stub `Part/__init__.pyi` line(s) 2337.

## `Part.Geometry.deleteExtensionOfName`

```python
def deleteExtensionOfName(self, name: str, /) -> None:
```

Deletes all extensions of the indicated name.

Evidence: public stub `Part/__init__.pyi` line(s) 2343.

## `Part.Geometry.getExtensions`

```python
def getExtensions(self) -> List[Extension]:
```

Returns a list with information about the geometry extensions.

Evidence: public stub `Part/__init__.pyi` line(s) 2349.

