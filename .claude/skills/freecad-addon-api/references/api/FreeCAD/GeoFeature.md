# `FreeCAD.GeoFeature`

[Module](index.md)

```python
class GeoFeature(DocumentObject):
```

App.GeoFeature class.

Base class of all geometric document objects.
This class does the whole placement and position handling.
With the method `getPropertyOfGeometry` is possible to obtain
the main geometric property in general form, without reference
to any particular property name.

Evidence: public stub `FreeCAD/__init__.pyi` line 2181. Inherited members are on the named base's reference; aliases keep their imported identity.

## `FreeCAD.GeoFeature.ElementMapVersion`

```python
ElementMapVersion: Final[str] = ''
```

Element map version

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2191.

## `FreeCAD.GeoFeature.Placement`

```python
@property
def Placement(self) -> Base.Placement:

@Placement.setter
def Placement(self, value: Base.Placement | Base.Matrix) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2195, 2199.

## `FreeCAD.GeoFeature.getPaths`

```python
def getPaths(self) -> Any:
```

Returns all possible paths to the root of the document.
Note: Not implemented.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2202.

## `FreeCAD.GeoFeature.getGlobalPlacement`

```python
@deprecated('since FreeCAD 26.3 and will be removed in FreeCAD 27.2; use getGlobalPlacementOf instead; This method does not handle Links correctly.')
def getGlobalPlacement(self) -> Placement:
```

Deprecated: This function does not handle Links correctly. Use getGlobalPlacementOf instead.

Returns the placement of the object in the global coordinate space, respecting all stacked
relationships.
Note: This function is not available during recompute, as there the placements of parents
can change after the execution of this object, rendering the result wrong.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2210.

## `FreeCAD.GeoFeature.getGlobalPlacementOf`

```python
@staticmethod
def getGlobalPlacementOf(targetObj: Any, rootObj: Any, subname: str, /) -> Placement:
```

Examples:
    obj = "part1"
    sub = "linkToPart2.LinkToBody.Pad.face1"

    Global placement of Pad in this context:
    getGlobalPlacementOf(pad, part1, "linkToPart2.LinkToBody.Pad.face1")


    Global placement of linkToPart2 in this context:
    getGlobalPlacementOf(linkToPart2, part1, "linkToPart2.LinkToBody.Pad.face1")

Returns the placement of the object in the global coordinate space, respecting all stacked
relationships.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2222.

## `FreeCAD.GeoFeature.getPropertyNameOfGeometry`

```python
def getPropertyNameOfGeometry(self) -> Optional[str]:
```

Returns the property name of the actual geometry.
For example for a Part feature it returns the value 'Shape', for a mesh feature the value
'Mesh' and so on.
If an object has no such property then None is returned.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2240.

## `FreeCAD.GeoFeature.getPropertyOfGeometry`

```python
def getPropertyOfGeometry(self) -> Optional[Any]:
```

Returns the property of the actual geometry.
For example for a Part feature it returns its Shape property, for a Mesh feature its
Mesh property and so on.
If an object has no such property then None is returned.
Unlike to getPropertyNameOfGeometry this function returns the geometry, not its name.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2249.

