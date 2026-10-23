# `draftviewproviders.view_layer.ViewProviderLayer`

[Source module](index.md)

```python
class ViewProviderLayer:
```

The viewprovider for the Layer object.

Evidence: `src/Mod/Draft/draftviewproviders/view_layer.py:48`. Source-defined class; runtime behavior and support status unverified.

## `draftviewproviders.view_layer.ViewProviderLayer.__init__`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def __init__(self, vobj):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_layer.py:51`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_layer.ViewProviderLayer.set_properties`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def set_properties(self, vobj):
```

Set the properties only if they don't already exist.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_layer.py:57`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_layer.ViewProviderLayer.set_override_options`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def set_override_options(self, vobj, properties):
```

Set property options only if they don't already exist.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_layer.py:63`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_layer.ViewProviderLayer.set_visual_properties`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def set_visual_properties(self, vobj, properties):
```

Set visual properties only if they don't already exist.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_layer.py:98`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_layer.ViewProviderLayer.getIcon`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getIcon(self):
```

Return the path to the icon used by the viewprovider.

Normally it returns the basic Layer icon, but if `icondata` exists
it is the modified icon with the line and shape colors of the layer.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_layer.py:160`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_layer.ViewProviderLayer.attach`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def attach(self, vobj):
```

Set up the scene sub-graph of the viewprovider.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_layer.py:170`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_layer.ViewProviderLayer.claimChildren`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def claimChildren(self):
```

Return objects that will be placed under it in the tree view.

These are the elements of the `Group` property of the Proxy object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_layer.py:176`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_layer.ViewProviderLayer.getDisplayModes`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getDisplayModes(self, vobj):
```

Return the display modes that this viewprovider supports.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_layer.py:186`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_layer.ViewProviderLayer.getDefaultDisplayMode`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getDefaultDisplayMode(self):
```

Return the default display mode.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_layer.py:190`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_layer.ViewProviderLayer.setDisplayMode`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def setDisplayMode(self, mode):
```

Return the saved display mode.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_layer.py:194`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_layer.ViewProviderLayer.dumps`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def dumps(self):
```

Return a tuple of objects to save or None.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_layer.py:198`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_layer.ViewProviderLayer.loads`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def loads(self, state):
```

Set the internal properties from the restored state.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_layer.py:202`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_layer.ViewProviderLayer.updateData`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def updateData(self, obj, prop):
```

Execute when a property from the Proxy class is changed.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_layer.py:206`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_layer.ViewProviderLayer.change_view_properties`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def change_view_properties(self, vobj, prop, old_prop=None, targets=None):
```

Change the properties of the targets, or of all objects in the layer group.

A child's property is only changed if it is not overridden (if its value
matches old_prop).

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_layer.py:211`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_layer.ViewProviderLayer.onBeforeChange`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def onBeforeChange(self, vobj, prop):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_layer.py:273`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_layer.ViewProviderLayer.onChanged`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def onChanged(self, vobj, prop):
```

Execute when a view property is changed.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_layer.py:277`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_layer.ViewProviderLayer.canDragObject`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def canDragObject(self, obj):
```

Return True to allow dragging one object from the Layer.

Also store parent group data for update_groups_after_drag_drop and
trigger that function.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_layer.py:359`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_layer.ViewProviderLayer.canDragObjects`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def canDragObjects(self):
```

Return True to allow dragging many objects from the Layer.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_layer.py:381`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_layer.ViewProviderLayer.dragObject`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def dragObject(self, vobj, child):
```

Remove the object that was dragged from the layer.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_layer.py:385`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_layer.ViewProviderLayer.canDropObject`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def canDropObject(self, obj):
```

Return true to allow dropping one object.

If the object being dropped is itself a `'Layer'`, return `False`
to prevent dropping a layer inside a layer, at least for now.

Also store parent group data for update_groups_after_drag_drop and
trigger that function.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_layer.py:391`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_layer.ViewProviderLayer.canDropObjects`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def canDropObjects(self):
```

Return true to allow dropping many objects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_layer.py:404`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_layer.ViewProviderLayer.dropObject`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def dropObject(self, vobj, child):
```

Add the object that was dropped on the Layer to the group.

This also results in a call to `change_view_properties` to update the
view properties of the child.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_layer.py:408`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_layer.ViewProviderLayer.update_groups_after_drag_drop`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def update_groups_after_drag_drop(self):
```

Workaround function to improve the drag and drop behavior of Layer
objects.

The function processes the parent group data stored in the
old_parent_data dictionary by canDragObject and canDropObject.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_layer.py:418`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_layer.ViewProviderLayer.replaceObject`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def replaceObject(self, old_obj, new_obj):
```

Return immediately to prevent replacement of children.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_layer.py:483`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_layer.ViewProviderLayer.setupContextMenu`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def setupContextMenu(self, vobj, menu):
```

Set up actions to perform in the context menu.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_layer.py:487`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_layer.ViewProviderLayer.activate`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def activate(self):
```

Activate the selected layer, it becomes the Autogroup.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_layer.py:511`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_layer.ViewProviderLayer.reassign_props`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def reassign_props(self):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_layer.py:519`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_layer.ViewProviderLayer.select_contents`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def select_contents(self):
```

Select the contents of the layer.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_layer.py:523`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`draftviewproviders.view_layer.ViewProviderLayer._paint_tree_icon`. These are source internals unless an explicit export establishes otherwise.

