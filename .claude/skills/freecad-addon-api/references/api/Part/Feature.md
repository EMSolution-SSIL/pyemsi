# `Part.Feature`

[Module](index.md)

```python
class Feature(GeoFeature):
```

This is the father of all shape object classes

Author: Juergen Riegel (FreeCAD@juergen-riegel.net)
Licence: LGPL

Evidence: public stub `Part/__init__.pyi` line 3142. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.Feature.Shape`

```python
@property
def Shape(self) -> Shape:

@Shape.setter
def Shape(self, value: Shape) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: getter and setter declared in the stub.

Evidence: public stub `Part/__init__.pyi` line(s) 3151, 3155.

## `Part.Feature.ShapeMaterial`

```python
@property
def ShapeMaterial(self) -> Materials.Material:

@ShapeMaterial.setter
def ShapeMaterial(self, value: Materials.Material) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: getter and setter declared in the stub.

Evidence: public stub `Part/__init__.pyi` line(s) 3159, 3163.

## `Part.Feature.getElementHistory`

```python
def getElementHistory(self, elementName: str, *, recursive: bool=True, sameType: bool=False, showName: bool=False) -> Union[Tuple[DocumentObject, str, List[str]], List[Tuple[DocumentObject, str, List[str]]]]:
```

getElementHistory(elementName,recursive=True,sameType=False,showName=False) - returns the element mapped name history

name: mapped element name belonging to this shape
recursive: if True, then track back the history through other objects till the origin
sameType: if True, then stop trace back when element type changes
showName: if False, return the owner object, or else return a tuple of object name and label

If not recursive, then return tuple(sourceObject, sourceElementName, [intermediateNames...]),
otherwise return a list of tuple.

Evidence: public stub `Part/__init__.pyi` line(s) 3166.

