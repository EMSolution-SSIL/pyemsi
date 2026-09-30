# `FreeCADGui.ViewProvider`

[Module](index.md)

```python
class ViewProvider(ExtensionContainer):
```

This is the ViewProvider base class

Author: Werner Mayer (wmayer@users.sourceforge.net)
Licence: LGPL

Evidence: public stub `FreeCADGui/__init__.pyi` line 2583. Inherited members are on the named base's reference; aliases keep their imported identity.

## Nested classes

- [FreeCADGui.ViewProvider.ToggleVisibilityMode](ViewProvider.ToggleVisibilityMode.md)

## `FreeCADGui.ViewProvider.addProperty`

```python
def addProperty(self, type: str, name: str, group: str='', doc: str='', attr: int=0, read_only: bool=False, hidden: bool=False, locked: bool=False, enum_vals: list[str] | None=None) -> 'ViewProvider':
```

Add a generic property.

type : str
    Property type.
name : str
    Property name.
group : str
    Property group. Defaults to "".
doc : str
    Property documentation. Defaults to "".
attr : int
    Property attributes. Defaults to 0.
read_only : bool
    Whether the property is read-only. Defaults to False.
hidden : bool
    Whether the property is hidden. Defaults to False.
locked : bool
    Whether the property is locked. Defaults to False.
enum_vals : list[str] | None
    Initial values for an enumeration property. Defaults to None.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2595.

## `FreeCADGui.ViewProvider.removeProperty`

```python
def removeProperty(self, name: str, /) -> bool:
```

Remove a generic property.
Only user-defined properties can be removed, not built-in ones.

name : str
    Property name.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2620.

## `FreeCADGui.ViewProvider.supportedProperties`

```python
def supportedProperties(self) -> list:
```

A list of supported property types.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2630.

## `FreeCADGui.ViewProvider.show`

```python
def show(self) -> None:
```

Show the object.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2636.

## `FreeCADGui.ViewProvider.hide`

```python
def hide(self) -> None:
```

Hide the object.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2642.

## `FreeCADGui.ViewProvider.isVisible`

```python
def isVisible(self) -> bool:
```

Check if the object is visible.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2648.

## `FreeCADGui.ViewProvider.canDragObject`

```python
def canDragObject(self, obj: Any=None, /) -> bool:
```

Check whether the child object can be removed by dragging.
If 'obj' is not given, check without filter by any particular object.

obj : App.DocumentObject
    Object to be dragged.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2654.

## `FreeCADGui.ViewProvider.dragObject`

```python
def dragObject(self, obj: Any, /) -> None:
```

Remove a child object by dropping.

obj : App.DocumentObject
    Object to be dragged.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2664.

## `FreeCADGui.ViewProvider.canDropObject`

```python
def canDropObject(self, obj: Any=None, owner: Any=None, subname: str=..., elem: Optional[List[str]]=None) -> bool:
```

Check whether the child object can be added by dropping.
If 'obj' is not given, check without filter by any particular object.

obj : App.DocumentObject
    Object to be dropped.
owner : App.DocumentObject
    Parent object of the dropping object.
subname : str
    Subname reference to the dropping object. Optional.
elem : sequence of str
    Non-objects subelements selected when the object is
    being dropped.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2673.

## `FreeCADGui.ViewProvider.dropObject`

```python
def dropObject(self, obj: Any, owner: Any=None, subname: str=..., elem: Optional[List[str]]=None) -> str:
```

Add a child object by dropping.

obj : App.DocumentObject
    Object to be dropped.
owner : App.DocumentObject
    Parent object of the dropping object.
subname : str
    Subname reference to the dropping object. Optional.
elem : sequence of str
    Non-objects subelements selected when the object is
    being dropped.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2690.

## `FreeCADGui.ViewProvider.canDragAndDropObject`

```python
def canDragAndDropObject(self, obj: Any, /) -> bool:
```

Check whether the child object can be removed from
other parent and added here by drag and drop.

obj : App.DocumentObject
    Object to be dragged and dropped.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2706.

## `FreeCADGui.ViewProvider.replaceObject`

```python
def replaceObject(self, oldObj: Any, newObj: Any, /) -> int:
```

Replace a child object.
Returns 1 if succeeded, 0 if not found, -1 if not supported.

oldObj : App.DocumentObject
    Old object.
newObj : App.DocumentObject
    New object.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2716.

## `FreeCADGui.ViewProvider.doubleClicked`

```python
@overload
def doubleClicked(self) -> bool:

@overload
def doubleClicked(self, root: DocumentObject, subname: str='', /) -> bool:
```

Trigger double clicking this view object, optionally specifying its root and subobject path.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2729, 2733.

## `FreeCADGui.ViewProvider.addDisplayMode`

```python
def addDisplayMode(self, obj: Any, mode: str, /) -> None:
```

Add a new display mode to the view provider.

obj : coin.SoNode
    Display mode.
mode : str
    Name of the display mode.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2739.

## `FreeCADGui.ViewProvider.listDisplayModes`

```python
def listDisplayModes(self) -> list:
```

Show a list of all display modes.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2750.

## `FreeCADGui.ViewProvider.toString`

```python
def toString(self) -> str:
```

Return a string representation of the Inventor node.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2756.

## `FreeCADGui.ViewProvider.setTransformation`

```python
def setTransformation(self, trans: Any, /) -> None:
```

Set a transformation on the Inventor node.

trans : Base.Placement, Base.Matrix

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2762.

## `FreeCADGui.ViewProvider.claimChildren`

```python
def claimChildren(self) -> list:
```

Returns list of objects that are to be grouped in tree under this object.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2770.

## `FreeCADGui.ViewProvider.claimChildrenRecursive`

```python
def claimChildrenRecursive(self) -> list:
```

Returns list of objects that are to be grouped in tree under this object recursively.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2776.

## `FreeCADGui.ViewProvider.partialRender`

```python
def partialRender(self, sub: Any=None, clear: bool=False, /) -> int:
```

Render only part of the object.

sub: None, str, sequence of str
    Refer to the subelement. If it is None then reset the partial rendering.
clear: bool
    True to add, or False to remove the subelement(s) for rendering.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2782.

## `FreeCADGui.ViewProvider.getElementColors`

```python
def getElementColors(self, elementName: Optional[str]=None, /) -> dict:
```

Get a dictionary of the form {elementName : (r,g,b,a)}.
If no element name is given a dictionary with all the elements is returned.

elementName : str
    Name of the element. Optional.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2793.

## `FreeCADGui.ViewProvider.setElementColors`

```python
def setElementColors(self, colors: dict, /) -> None:
```

Set element colors.

colors: dict
    Color dictionary of the form {elementName:(r,g,b,a)}.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2803.

## `FreeCADGui.ViewProvider.getElementPicked`

```python
def getElementPicked(self, pickPoint: Any, /) -> str | None:
```

Return the picked subelement.

pickPoint : coin.SoPickedPoint

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2812.

## `FreeCADGui.ViewProvider.getDetailPath`

```python
def getDetailPath(self, subelement: str, path: Any, append: bool=True, /) -> Any:
```

Return Coin detail and path of an subelement.

subname: str
    Dot separated string reference to the sub element.
pPath: coin.SoPath
    Output coin path leading to the returned element detail.
append: bool
    If True, path will be first appended with the root node and the mode
    switch node of this view provider.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2820.

## `FreeCADGui.ViewProvider.signalChangeIcon`

```python
def signalChangeIcon(self) -> None:
```

Trigger icon changed signal.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2834.

## `FreeCADGui.ViewProvider.getBoundingBox`

```python
def getBoundingBox(self, subname: Optional[str]=None, transform: bool=True, view: Any=None, mat: Any=None, depth: int=0) -> BoundBox:
```

Obtain the bounding box of this view object.

subname : str, optional
    Name referring a sub-object.
transform: bool
    Whether to apply the transformation matrix of this view provider.
view: View3DInventorPy, optional
    The view to use. Defaults to active view.
mat: Matrix, optional
    Initial transformation matrix.
depth: int
    Current recursion depth.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2840.

## `FreeCADGui.ViewProvider.Annotation`

```python
Annotation: Any = ...
```

A pivy Separator to add a custom scenegraph to this ViewProvider.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2856.

## `FreeCADGui.ViewProvider.Icon`

```python
Icon: Final[Any] = ...
```

The icon of this ViewProvider.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2858.

## `FreeCADGui.ViewProvider.RootNode`

```python
RootNode: Any = ...
```

A pivy Separator with the root of this ViewProvider.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2860.

## `FreeCADGui.ViewProvider.SwitchNode`

```python
SwitchNode: Any = ...
```

A pivy SoSwitch for the display mode switch of this ViewProvider.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2862.

## `FreeCADGui.ViewProvider.DefaultMode`

```python
DefaultMode: int = 0
```

Get/Set the default display mode in turns of coin node index.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2864.

## `FreeCADGui.ViewProvider.IV`

```python
IV: Final[str] = ''
```

Represents the whole ViewProvider as an Inventor string.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2866.

## `FreeCADGui.ViewProvider.CanRemoveChildrenFromRoot`

```python
CanRemoveChildrenFromRoot: Final[bool] = False
```

Tells the tree view whether to remove the children item from root or not.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2868.

## `FreeCADGui.ViewProvider.LinkVisibility`

```python
LinkVisibility: bool = False
```

Get/set visibilities of all links to this view object.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2870.

## `FreeCADGui.ViewProvider.DropPrefix`

```python
DropPrefix: Final[str] = ''
```

Subname referencing the sub-object for holding dropped object.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2872.

## `FreeCADGui.ViewProvider.ToggleVisibility`

```python
ToggleVisibility: 'FreeCADGui.ToggleVisibilityMode' = ToggleVisibilityMode.CanToggleVisibility
```

Get/set whether the viewprovider can toggle the visibility of
    the object.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 2874.

