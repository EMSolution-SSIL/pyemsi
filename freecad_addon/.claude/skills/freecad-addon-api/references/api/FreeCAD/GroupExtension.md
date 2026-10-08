# `FreeCAD.GroupExtension`

[Module](index.md)

```python
class GroupExtension(DocumentObjectExtension):
```

Extension class which allows grouping of document objects
Author: Werner Mayer (wmayer@users.sourceforge.net)
Licence: LGPL

Evidence: public stub `FreeCAD/__init__.pyi` line 2267. Inherited members are on the named base's reference; aliases keep their imported identity.

## `FreeCAD.GroupExtension.newObject`

```python
def newObject(self, type: str, name: str=..., /) -> Any:
```

Create and add an object with given type and name to the group

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2274.

## `FreeCAD.GroupExtension.addObject`

```python
def addObject(self, obj: Any, /) -> List[Any]:
```

Add an object to the group. Returns all objects that have been added.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2280.

## `FreeCAD.GroupExtension.addObjects`

```python
def addObjects(self, objects: List[Any], /) -> List[Any]:
```

Adds multiple objects to the group. Expects a list and returns all objects that have been added.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2286.

## `FreeCAD.GroupExtension.setObjects`

```python
def setObjects(self, objects: List[Any], /) -> List[Any]:
```

Sets the objects of the group. Expects a list and returns all objects that are now in the group.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2292.

## `FreeCAD.GroupExtension.removeObject`

```python
def removeObject(self, obj: Any, /) -> List[Any]:
```

Remove an object from the group and returns all objects that have been removed.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2298.

## `FreeCAD.GroupExtension.removeObjects`

```python
def removeObjects(self, objects: List[Any], /) -> List[Any]:
```

Remove multiple objects from the group. Expects a list and returns all objects that have been removed.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2304.

## `FreeCAD.GroupExtension.removeObjectsFromDocument`

```python
def removeObjectsFromDocument(self) -> None:
```

Remove all child objects from the group and document

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2310.

## `FreeCAD.GroupExtension.getObject`

```python
def getObject(self, name: str, /) -> DocumentObject | None:
```

Return the object with the given name

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2316.

## `FreeCAD.GroupExtension.getObjectsOfType`

```python
def getObjectsOfType(self, typename: str, /) -> List[Any]:
```

Returns all object in the group of given type
@param typename     The Freecad type identifier

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2322.

## `FreeCAD.GroupExtension.hasObject`

```python
def hasObject(self, obj: Any, recursive: bool=False, /) -> bool:
```

Checks if the group has a given object
@param obj        the object to check for.
@param recursive  if true check also if the obj is child of some sub group (default is false).

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2329.

## `FreeCAD.GroupExtension.allowObject`

```python
def allowObject(self, obj: Any, /) -> bool:
```

Returns true if obj is allowed in the group extension.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2337.

