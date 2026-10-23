# `FreeCADGui.LinkView`

[Module](index.md)

```python
class LinkView(BaseClass):
```

Helper class to link to a view object

Author: Zheng, Lei (realthunder.dev@gmail.com)
Licence: LGPL

Evidence: public stub `FreeCADGui/__init__.pyi` line 2212. Inherited members are on the named base's reference; aliases keep their imported identity.

## `FreeCADGui.LinkView.reset`

```python
def reset(self) -> None:
```

Reset the link view and clear the links

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2220.

## `FreeCADGui.LinkView.setMaterial`

```python
@overload
def setMaterial(self, material: None, /) -> None:

@overload
def setMaterial(self, material: Any, /) -> None:

@overload
def setMaterial(self, material: List[Any], /) -> None:

@overload
def setMaterial(self, material: Dict[int, Any], /) -> None:

def setMaterial(self, material: Any, /) -> None:
```

setMaterial(Material): set the override material of the entire linked object

setMaterial([Material,...]): set the materials for the elements of the link
                             array/group.

setMaterial({Int:Material,...}): set the material for the elements of the
                                 link array/group by index.

If material is None, then the material is unset. If the material of an element
is unset, it defaults to the override material of the linked object, if there
is one

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2227, 2231, 2235, 2239, 2242.

## `FreeCADGui.LinkView.setType`

```python
@overload
def setType(self, type: int, /) -> None:

@overload
def setType(self, type: int, sublink: bool, /) -> None:

def setType(self, type: int, sublink: bool=True, /) -> None:
```

set the link type.

type=0:  override transformation and visibility
type=1:  override visibility
type=2:  no override
type=-1: sub-object link with override visibility
type=-2: sub-object link with override transformation and visibility

sublink: auto delegate to the sub-object references in the link, if there is
         one and only one.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2259, 2263, 2266.

## `FreeCADGui.LinkView.setTransform`

```python
@overload
def setTransform(self, matrix: Any, /) -> None:

@overload
def setTransform(self, matrix: List[Any], /) -> None:

@overload
def setTransform(self, matrix: Dict[int, Any], /) -> None:

def setTransform(self, matrix: Any, /) -> None:
```

set transformation of the linked object

set transformation for the elements of the link
                            array/group

set transformation for elements of the link
                                  array/group by index

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2282, 2286, 2290, 2293.

## `FreeCADGui.LinkView.setChildren`

```python
def setChildren(self, children: List[Any], vis: List[Any]=[], type: int=0, /) -> None:
```

Group a list of children objects. Note, this mode of operation is incompatible
with link array. Calling this function will deactivate link array. And calling
setSize() will reset all linked children.

vis: initial visibility status of the children

type: children linking type,
   0: override transformation and visibility,
   1: override visibility,
   2: override none.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2305.

## `FreeCADGui.LinkView.setLink`

```python
@overload
def setLink(self, obj: Any, /) -> None:

@overload
def setLink(self, obj: Any, subname: str, /) -> None:

@overload
def setLink(self, obj: Any, subname: List[str], /) -> None:

def setLink(self, obj: Any, subname: Any=None, /) -> None:
```

Set the link

Set the link with a sub-object reference

Set the link with a list of sub object references

object: The linked document object or its view object

subname: a string or tuple/list of strings sub-name references to sub object
         or sub elements (e.g. Face1, Edge2) belonging to the linked object.
         The sub-name must end with a '.' if it is referencing an sub-object,
         or else it is considered a sub-element reference.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2321, 2325, 2329, 2332.

## `FreeCADGui.LinkView.getDetailPath`

```python
def getDetailPath(self, sub: str, path: Any, /) -> Tuple[Any, Any]:
```

get the 3d path an detail of an element.

Return a tuple(path,detail) for the coin3D SoPath and SoDetail of the element

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2349.

## `FreeCADGui.LinkView.getElementPicked`

```python
def getElementPicked(self, pickPoint: Any, /) -> str | None:
```

get the element under a 3d pick point.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2357.

## `FreeCADGui.LinkView.getBoundBox`

```python
def getBoundBox(self, vobj: ViewProviderDocumentObject, /) -> BoundBox:
```

get the bounding box.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2363.

## `FreeCADGui.LinkView.getChildren`

```python
def getChildren(self) -> Tuple[ViewProviderDocumentObject, ...] | None:
```

Get children view objects

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2369.

## `FreeCADGui.LinkView.LinkedView`

```python
LinkedView: Final[Any] = ...
```

The linked view object

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2374.

## `FreeCADGui.LinkView.SubNames`

```python
SubNames: Final[Any] = ...
```

The sub-object reference of the link

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2376.

## `FreeCADGui.LinkView.RootNode`

```python
RootNode: Final[Any] = ...
```

A pivy node holding the cloned representation of the linked view object

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2378.

## `FreeCADGui.LinkView.Owner`

```python
Owner: Any = ...
```

The owner view object of this link handle

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2380.

## `FreeCADGui.LinkView.Visibilities`

```python
Visibilities: Any = ...
```

Get/set the child element visibility

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2382.

## `FreeCADGui.LinkView.Count`

```python
Count: int = 0
```

Set the element size to create an array of linked object

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2384.

