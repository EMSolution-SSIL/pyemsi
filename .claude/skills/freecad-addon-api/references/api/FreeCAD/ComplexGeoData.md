# `FreeCAD.ComplexGeoData`

[Module](index.md)

```python
class ComplexGeoData(Persistence):
```

Father of all complex geometric data types.

Evidence: public stub `FreeCAD/__init__.pyi` line 822. Inherited members are on the named base's reference; aliases keep their imported identity.

## `FreeCAD.ComplexGeoData.getElementTypes`

```python
def getElementTypes(self) -> list[str]:
```

Return a list of element types present in the complex geometric data.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 827.

## `FreeCAD.ComplexGeoData.countSubElements`

```python
def countSubElements(self, type: str, /) -> int:
```

Return the number of elements of a type.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 833.

## `FreeCAD.ComplexGeoData.getFacesFromSubElement`

```python
def getFacesFromSubElement(self, type: str, index: int, /) -> tuple[list[Vector], list[tuple[int, int, int]]]:
```

Return vertexes and faces from a sub-element.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 839.

## `FreeCAD.ComplexGeoData.getLinesFromSubElement`

```python
def getLinesFromSubElement(self, type: str, index: int, /) -> tuple[list[Vector], list[tuple[int, int]]]:
```

Return vertexes and lines from a sub-element.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 845.

## `FreeCAD.ComplexGeoData.getPoints`

```python
def getPoints(self, accuracy: float, /) -> tuple[list[Vector], list[Vector]]:
```

Return a tuple of points and normals with a given accuracy

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 851.

## `FreeCAD.ComplexGeoData.getLines`

```python
def getLines(self, accuracy: float, /) -> tuple[list[Vector], list[tuple[int, int]]]:
```

Return a tuple of points and lines with a given accuracy

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 857.

## `FreeCAD.ComplexGeoData.getFaces`

```python
def getFaces(self, accuracy: float, /) -> tuple[list[Vector], list[tuple[int, int, int]]]:
```

Return a tuple of points and triangles with a given accuracy

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 863.

## `FreeCAD.ComplexGeoData.applyTranslation`

```python
def applyTranslation(self, translation: Vector, /) -> None:
```

Apply an additional translation to the placement

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 869.

## `FreeCAD.ComplexGeoData.applyRotation`

```python
def applyRotation(self, rotation: Rotation, /) -> None:
```

Apply an additional rotation to the placement

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 875.

## `FreeCAD.ComplexGeoData.transformGeometry`

```python
def transformGeometry(self, transformation: Matrix, /) -> None:
```

Apply a transformation to the underlying geometry

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 881.

## `FreeCAD.ComplexGeoData.setElementName`

```python
def setElementName(self, *, element: str, name: str=..., postfix: str=..., overwrite: bool=..., sid: Any=..., tag: int=...) -> str:
```

Set an element name.

Args:
    element  : the original element name, e.g. Edge1, Vertex2
    name     : the new name for the element, None to remove the mapping
    postfix  : postfix of the name that will not be hashed
    overwrite: if true, it will overwrite exiting name
    sid      : to hash the name any way you want, provide your own string id(s) in this parameter

An element can have multiple mapped names. However, a name can only be mapped
to one element

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 887.

## `FreeCAD.ComplexGeoData.getElementName`

```python
def getElementName(self, name: str, direction: int=0, /) -> str:
```

Return a mapped element name or reverse.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 903.

## `FreeCAD.ComplexGeoData.getElementIndexedName`

```python
def getElementIndexedName(self, name: str, return_id: bool=..., /) -> str | tuple[str, list[int]]:
```

Return the indexed element name.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 909.

## `FreeCAD.ComplexGeoData.getElementMappedName`

```python
def getElementMappedName(self, name: str, return_id: bool=..., /) -> str | tuple[str, list[int]]:
```

Return the mapped element name

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 915.

## `FreeCAD.ComplexGeoData.BoundBox`

```python
BoundBox: 'Final[FreeCAD.BoundBox]' = ...
```

Get the bounding box (BoundBox) of the complex geometric data.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 920.

## `FreeCAD.ComplexGeoData.CenterOfGravity`

```python
CenterOfGravity: Final[Vector] = ...
```

Get the center of gravity

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 922.

## `FreeCAD.ComplexGeoData.Placement`

```python
Placement: 'FreeCAD.Placement' = ...
```

Get the current transformation of the object as placement

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 924.

## `FreeCAD.ComplexGeoData.Tag`

```python
Tag: int = 0
```

Geometry Tag

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 926.

## `FreeCAD.ComplexGeoData.Hasher`

```python
Hasher: StringHasher = ...
```

Get/Set the string hasher of this object

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 928.

## `FreeCAD.ComplexGeoData.ElementMapSize`

```python
ElementMapSize: Final[int] = 0
```

Get the current element map size

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 930.

## `FreeCAD.ComplexGeoData.ElementMap`

```python
ElementMap: dict[str, str] = {}
```

Get/Set a dict of element mapping

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 932.

## `FreeCAD.ComplexGeoData.ElementReverseMap`

```python
ElementReverseMap: Final[dict[str, str | list[str]]] = {}
```

Get a dict of element reverse mapping

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 934.

## `FreeCAD.ComplexGeoData.ElementMapVersion`

```python
ElementMapVersion: Final[str] = ''
```

Element map version

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 936.

