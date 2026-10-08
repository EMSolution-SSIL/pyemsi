# `FreeCAD.DocumentObject`

[Module](index.md)

```python
class DocumentObject(ExtensionContainer):
```

This is the father of all classes handled by the document
Author: Juergen Riegel (FreeCAD@juergen-riegel.net)
Licence: LGPL

Evidence: public stub `FreeCAD/__init__.pyi` line 1731. Inherited members are on the named base's reference; aliases keep their imported identity.

## `FreeCAD.DocumentObject.OutListProp`

```python
OutListProp: Final[List[DepEdge]] = []
```

A list of all objects which link to this object with properties.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1737.

## `FreeCAD.DocumentObject.OutList`

```python
OutList: Final[List['DocumentObject']] = []
```

A list of all objects this object links to.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1739.

## `FreeCAD.DocumentObject.OutListRecursive`

```python
OutListRecursive: Final[List['DocumentObject']] = []
```

A list of all objects this object links to recursively.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1741.

## `FreeCAD.DocumentObject.InList`

```python
InList: Final[List['DocumentObject']] = []
```

A list of all objects which link to this object.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1743.

## `FreeCAD.DocumentObject.InListProp`

```python
InListProp: Final[List[DepEdge]] = []
```

A list of all objects which link to this object with properties.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1745.

## `FreeCAD.DocumentObject.InListRecursive`

```python
InListRecursive: Final[List['DocumentObject']] = []
```

A list of all objects which link to this object recursively.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1747.

## `FreeCAD.DocumentObject.FullName`

```python
FullName: Final[str] = ''
```

Return the document name and internal name of this object

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1749.

## `FreeCAD.DocumentObject.Name`

```python
Name: Final[Optional[str]] = ''
```

Return the internal name of this object

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1751.

## `FreeCAD.DocumentObject.Document`

```python
Document: 'Final[FreeCAD.Document]' = ...
```

Return the document this object is part of

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1753.

## `FreeCAD.DocumentObject.State`

```python
State: Final[List[Any]] = []
```

State of the object in the document

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1755.

## `FreeCAD.DocumentObject.ViewObject`

```python
ViewObject: Final[_ViewProviderDocumentObject | None] = ...
```


    If the GUI is loaded the associated view provider is returned
    or None if the GUI is not up
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1757.

## `FreeCAD.DocumentObject.MustExecute`

```python
MustExecute: Final[bool] = False
```

Check if the object must be recomputed

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1759.

## `FreeCAD.DocumentObject.ID`

```python
ID: Final[int] = 0
```

The unique identifier (among its document) of this object

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1761.

## `FreeCAD.DocumentObject.Removing`

```python
Removing: Final[bool] = False
```

Indicate if the object is being removed

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1763.

## `FreeCAD.DocumentObject.Parents`

```python
Parents: Final[List[Any]] = []
```

A List of tuple(parent,subname) holding all parents to this object

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1765.

## `FreeCAD.DocumentObject.OldLabel`

```python
OldLabel: Final[str] = ''
```

Contains the old label before change

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1767.

## `FreeCAD.DocumentObject.NoTouch`

```python
NoTouch: bool = False
```

Enable/disable no touch on any property change

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1769.

## `FreeCAD.DocumentObject.ExpressionEngine`

```python
@property
def ExpressionEngine(self) -> list[tuple[str, str | None]]:
```

Property expressions

Access: getter only declared in the stub.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1773.

## `FreeCAD.DocumentObject.Label`

```python
@property
def Label(self) -> str:

@Label.setter
def Label(self, value: str) -> None:
```

User name of the object (UTF8)

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1778, 1783.

## `FreeCAD.DocumentObject.Label2`

```python
@property
def Label2(self) -> str:

@Label2.setter
def Label2(self, value: str) -> None:
```

User description of the object (UTF8)

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1787, 1792.

## `FreeCAD.DocumentObject.Visibility`

```python
@property
def Visibility(self) -> bool:

@Visibility.setter
def Visibility(self, value: bool | int) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1796, 1800.

## `FreeCAD.DocumentObject.addProperty`

```python
def addProperty(self, type: str, name: str, group: str='', doc: str='', attr: int=0, read_only: bool=False, hidden: bool=False, locked: bool=False, enum_vals: list[str] | None=None) -> 'DocumentObject':
```

Add a generic property.

Args:
    type: The type of the property to add.
    name: The name of the property.
    group: The group to which the property belongs. Defaults to "".
    doc: The documentation string for the property. Defaults to "".
    attr: Attribute flags for the property. Defaults to 0.
    read_only: Whether the property is read-only. Defaults to False.
    hidden: Whether the property is hidden. Defaults to False.
    locked: Whether the property is locked. Defaults to False.
    enum_vals: Initial values for an enumeration property. Defaults to None.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1803.

## `FreeCAD.DocumentObject.removeProperty`

```python
def removeProperty(self, string: str, /) -> bool:
```

Remove a generic property.

Note, you can only remove user-defined properties but not built-in ones.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1820.

## `FreeCAD.DocumentObject.supportedProperties`

```python
def supportedProperties(self) -> list:
```

A list of supported property types

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1828.

## `FreeCAD.DocumentObject.touch`

```python
def touch(self, property_name: str=..., /) -> None:
```

Mark the object as changed (touched)

With no argument the object is then forced to recompute. With an empty string as the
argument, this marks the object as touched *without* forcing a recompute. Finally, if a
property name is passed, this only touches that property.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1834.

## `FreeCAD.DocumentObject.purgeTouched`

```python
def purgeTouched(self) -> None:
```

Mark the object as unchanged

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1844.

## `FreeCAD.DocumentObject.enforceRecompute`

```python
def enforceRecompute(self) -> None:
```

Mark the object for recompute

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1850.

## `FreeCAD.DocumentObject.setExpression`

```python
def setExpression(self, name: str, expression: str | None, comment: str=..., /) -> None:
```

Register an expression for a property.

Pass None as expression to clear an existing expression.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1856.

## `FreeCAD.DocumentObject.clearExpression`

```python
def clearExpression(self, name: str, /) -> None:
```

Clear the expression for a property

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1864.

## `FreeCAD.DocumentObject.evalExpression`

```python
@classmethod
def evalExpression(cls, expression: str, /) -> Any:
```

Evaluate an expression

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1871.

## `FreeCAD.DocumentObject.recompute`

```python
def recompute(self, recursive: bool=False, /) -> bool:
```

Recomputes this object

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1877.

## `FreeCAD.DocumentObject.getStatusString`

```python
def getStatusString(self) -> str:
```

Returns the status of the object as string.
If the object is invalid its error description will be returned.
If the object is valid but touched then 'Touched' will be returned,
'Valid' otherwise.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1883.

## `FreeCAD.DocumentObject.isValid`

```python
def isValid(self) -> bool:
```

Returns True if the object is valid, False otherwise

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1892.

## `FreeCAD.DocumentObject.getSubObject`

```python
def getSubObject(self, subname: Union[str, List[str], Tuple[str, ...]], *, retType: int=0, matrix: Matrix=None, transform: bool=True, depth: int=0) -> Any:
```

* subname(string|list|tuple): dot separated string or sequence of strings
referencing subobject.

* retType: return type, 0=PyObject, 1=DocObject, 2=DocAndPyObject, 3=Placement

    PyObject: return a python binding object for the (sub)object referenced in
    each 'subname' The actual type of 'PyObject' is implementation dependent.
    For Part::Feature compatible objects, this will be of type TopoShapePy and
    pre-transformed by accumulated transformation matrix along the object path.

    DocObject:  return the document object referenced in subname, if 'matrix' is
    None. Or, return a tuple (object, matrix) for each 'subname' and 'matrix' is
    the accumulated transformation matrix for the sub object.

    DocAndPyObject: return a tuple (object, matrix, pyobj) for each subname

    Placement: return a transformed placement of the sub-object

* matrix: the initial transformation to be applied to the sub object.

* transform: whether to transform the sub object using this object's placement

* depth: current recursive depth

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1898.

## `FreeCAD.DocumentObject.getSubObjectList`

```python
def getSubObjectList(self, subname: str, /) -> list:
```

Return a list of objects referenced by a given subname including this object

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1926.

## `FreeCAD.DocumentObject.getSubObjects`

```python
def getSubObjects(self, reason: int=0, /) -> list:
```

Return subname reference of all sub-objects

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1932.

## `FreeCAD.DocumentObject.getLinkedObject`

```python
def getLinkedObject(self, *, recursive: bool=True, matrix: Matrix=None, transform: bool=True, depth: int=0) -> Any:
```

Returns the linked object if there is one, or else return itself

* recursive: whether to recursively resolve the links

* transform: whether to transform the sub object using this object's placement

* matrix: If not none, this specifies the initial transformation to be applied
to the sub object. And cause the method to return a tuple (object, matrix)
containing the accumulated transformation matrix

* depth: current recursive depth

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1938.

## `FreeCAD.DocumentObject.setElementVisible`

```python
def setElementVisible(self, element: str, visible: bool=True, /) -> int:
```

Set the visibility of a child element
Return -1 if element visibility is not supported, 0 if element not found, 1 if success

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1954.

## `FreeCAD.DocumentObject.isElementVisible`

```python
def isElementVisible(self, element: str, /) -> int:
```

Check if a child element is visible
Return -1 if element visibility is not supported or element not found, 0 if invisible, or else 1

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1961.

## `FreeCAD.DocumentObject.hasChildElement`

```python
def hasChildElement(self) -> bool:
```

Return true to indicate the object having child elements

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1968.

## `FreeCAD.DocumentObject.getParentGroup`

```python
def getParentGroup(self) -> DocumentObjectGroup | None:
```

Returns the group the object is in or None if it is not part of a group.

Note that an object can only be in a single group, hence only a single return value.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1974.

## `FreeCAD.DocumentObject.getParentGeoFeatureGroup`

```python
def getParentGeoFeatureGroup(self) -> Any:
```

Returns the GeoFeatureGroup, and hence the local coordinate system, the object
is in or None if it is not part of a group.

Note that an object can only be in a single group, hence only a single return value.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1982.

## `FreeCAD.DocumentObject.getParent`

```python
def getParent(self) -> Any:
```

Returns the group the object is in or None if it is not part of a group.

Note that an object can only be in a single group, hence only a single return value.
The parent can be a simple group as with getParentGroup() or a GeoFeature group as
with getParentGeoFeatureGroup().

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1991.

## `FreeCAD.DocumentObject.getPathsByOutList`

```python
def getPathsByOutList(self, target: DocumentObject, /) -> list[list[DocumentObject]]:
```

Get all paths from this object to another object following the OutList.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2001.

## `FreeCAD.DocumentObject.resolve`

```python
def resolve(self, subname: str, /) -> tuple:
```

resolve the sub object

Returns a tuple (subobj,parent,elementName,subElement), where 'subobj' is the
last object referenced in 'subname', and 'parent' is the direct parent of
'subobj', and 'elementName' is the name of the subobj, which can be used
to call parent.isElementVisible/setElementVisible(). 'subElement' is the
non-object sub-element name if any.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2007.

## `FreeCAD.DocumentObject.resolveSubElement`

```python
def resolveSubElement(self, subname: str, append: bool=False, type: int=0, /) -> tuple:
```

resolve both new and old style sub element

subname: subname reference containing object hierarchy
append: Whether to append object hierarchy prefix inside subname to returned element name
type: 0: normal, 1: for import, 2: for export

Return tuple(obj,newElementName,oldElementName)

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2019.

## `FreeCAD.DocumentObject.adjustRelativeLinks`

```python
def adjustRelativeLinks(self, parent: DocumentObject, recursive: bool=True, /) -> bool:
```

auto correct potential cyclic dependencies

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2031.

## `FreeCAD.DocumentObject.getElementMapVersion`

```python
def getElementMapVersion(self, property_name: str, restored: bool=False, /) -> str:
```

return element map version of a given geometry property

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2037.

## `FreeCAD.DocumentObject.isAttachedToDocument`

```python
def isAttachedToDocument(self) -> bool:
```

Return true if the object is part of a document, false otherwise.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2043.

## `FreeCAD.DocumentObject.getPlacementOf`

```python
def getPlacementOf(self, subname: str, target: DocumentObject | None=None, /) -> Any:
```

Return the placement of the sub-object relative to the link object.
getPlacementOf(subname, [targetObj]) -> Base.Placement

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2049.

## `FreeCAD.DocumentObject.moveProperty`

```python
def moveProperty(self, name: str, targetObj: DocumentObject, /) -> None:
```

moveProperty(name, targetObj) -> None

Move a property to the target container.

name : str
    The name of the property to move.
targetObj : DocumentObject
    The target object to move the property to.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2056.

