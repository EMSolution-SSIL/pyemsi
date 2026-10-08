# Python source module `draftutils.gui_utils`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftutils/gui_utils.py`. Import path is source-routed; installed availability is unverified.

Provides utility functions that deal with GUI interactions.

This module contains auxiliary functions which can be used
in other modules of the workbench, and which require
the graphical user interface (GUI), as they access the view providers
of the objects or the 3D view.

Literal `__all__`: not available; source names do not imply supported public API.

[part 1](index.md) | [part 2](index-2.md)

## Imports, aliases and conditional reexports

### import importlib

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftutils.gui_utils.importlib` -> `importlib`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftutils/gui_utils.py:42`.

### import math

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftutils.gui_utils.math` -> `math`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftutils/gui_utils.py:43`.

### import os

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftutils.gui_utils.os` -> `os`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftutils/gui_utils.py:44`.

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftutils.gui_utils.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftutils/gui_utils.py:46`.

### from draftutils import params

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftutils.gui_utils.params` -> `draftutils.params`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftutils/gui_utils.py:47`.

### from draftutils import utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftutils.gui_utils.utils` -> `draftutils.utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftutils/gui_utils.py:48`.

### from draftutils.messages import _err, _wrn

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftutils.gui_utils._err` -> `draftutils.messages._err`.

Bound source name `draftutils.gui_utils._wrn` -> `draftutils.messages._wrn`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftutils/gui_utils.py:49`.

### from draftutils.translate import translate

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftutils.gui_utils.translate` -> `draftutils.translate.translate`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftutils/gui_utils.py:50`.

### import FreeCADGui as Gui

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if App.GuiUp`.

Bound source name `draftutils.gui_utils.Gui` -> `FreeCADGui`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftutils/gui_utils.py:53`.

### from pivy import coin

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if App.GuiUp`.

Bound source name `draftutils.gui_utils.coin` -> `pivy.coin`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftutils/gui_utils.py:54`.

### from PySide import QtCore

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if App.GuiUp`.

Bound source name `draftutils.gui_utils.QtCore` -> `PySide.QtCore`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftutils/gui_utils.py:55`.

### from PySide import QtGui

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if App.GuiUp`.

Bound source name `draftutils.gui_utils.QtGui` -> `PySide.QtGui`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftutils/gui_utils.py:56`.

## `draftutils.gui_utils.get_3d_view`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_3d_view():
```

Return the current 3D view.

Returns
-------
Gui::View3DInventor
    The Active 3D View or `None`.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/gui_utils.py:61`. Decorators are copied as source expressions and have not been executed.

## `draftutils.gui_utils.get3DView`

Status: source-defined name; no independently verified stability/export guarantee.

```python
get3DView = get_3d_view
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/Draft/draftutils/gui_utils.py:86`. Decorators are copied as source expressions and have not been executed.

## `draftutils.gui_utils.autogroup`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def autogroup(obj):
```

Add a given object to the defined Draft autogroup, if applicable.

This function only works if the graphical interface is available.
It checks that the `App.draftToolBar` class is available,
which contains the group to use to automatically store
new created objects.

Originally, it worked with standard groups (`App::DocumentObjectGroup`),
and Arch Workbench containers like `'Site'`, `'Building'`, `'Floor'`,
and `'BuildingPart'`.

Now it works with Draft Layers.

Parameters
----------
obj: App::DocumentObject
    Any type of object that will be stored in the group.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/gui_utils.py:89`. Decorators are copied as source expressions and have not been executed.

## `draftutils.gui_utils.dim_symbol`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def dim_symbol(symbol=None, invert=False):
```

Return the specified dimension symbol.

Parameters
----------
symbol: int, optional
    It defaults to `None`, in which it gets the value from the parameter
    database, `get_param("dimsymbolend")`.

    A numerical value defines different markers
     * 0, `SoSphere`
     * 1, `SoSeparator` with a `SoLineSet`, a circle (in fact a 24 sided polygon)
     * 2, `SoSeparator` with a `soCone`
     * 3, `SoSeparator` with a `SoFaceSet`
     * 4, `SoSeparator` with a `SoLineSet`, calling `dim_dash`
     * 5, Nothing
     * Otherwise, `SoSphere`

invert: bool, optional
    It defaults to `False`.
    If it is `True` and `symbol=2`, the cone will be rotated
    -90 degrees around the Z axis, otherwise the rotation is positive,
    +90 degrees.

Returns
-------
Coin.SoNode
    A `Coin.SoSphere`, or `Coin.SoSeparator` (circle, cone, face, line)
    that will be used as a dimension symbol.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/gui_utils.py:201`. Decorators are copied as source expressions and have not been executed.

## `draftutils.gui_utils.dimSymbol`

Status: source-defined name; no independently verified stability/export guarantee.

```python
dimSymbol = dim_symbol
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/Draft/draftutils/gui_utils.py:288`. Decorators are copied as source expressions and have not been executed.

## `draftutils.gui_utils.dim_dash`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def dim_dash(p1, p2):
```

Return a SoSeparator with a line used to make dimension dashes.

It is used by `dim_symbol` to create line end symbols
like `'Tick-2'`, `'DimOvershoot'`, and `'ExtOvershoot'` dashes.

Parameters
----------
p1: tuple of three floats or Base::Vector3
    A point to define a line vertex.

p2: tuple of three floats or Base::Vector3
    A point to define a line vertex.

Returns
-------
Coin.SoSeparator
    A Coin object with a `SoLineSet` created from `p1` and `p2`
    as vertices.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/gui_utils.py:291`. Decorators are copied as source expressions and have not been executed.

## `draftutils.gui_utils.dimDash`

Status: source-defined name; no independently verified stability/export guarantee.

```python
dimDash = dim_dash
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/Draft/draftutils/gui_utils.py:321`. Decorators are copied as source expressions and have not been executed.

## `draftutils.gui_utils.remove_hidden`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def remove_hidden(objectslist):
```

Return only the visible objects in the list.

This function only works if the graphical interface is available
as the `Visibility` attribute is a property of the view provider
(`obj.ViewObject`).

Parameters
----------
objectslist: list of App::DocumentObject
    List of any type of object.

Returns
-------
list
    Return a copy of the input list without those objects
    for which `obj.ViewObject.Visibility` is `False`.

    If the graphical interface is not loaded
    the returned list is just a copy of the input list.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/gui_utils.py:324`. Decorators are copied as source expressions and have not been executed.

## `draftutils.gui_utils.removeHidden`

Status: source-defined name; no independently verified stability/export guarantee.

```python
removeHidden = remove_hidden
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/Draft/draftutils/gui_utils.py:353`. Decorators are copied as source expressions and have not been executed.

## `draftutils.gui_utils.get_diffuse_color`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_diffuse_color(objs):
```

Get a (cumulative) diffuse color from one or more objects.

If all tuples in the result are identical a list with a single tuple is
returned. In theory all faces of an object can be set to the same diffuse
color that is different from its shape color, but that seems rare. The
function does not take that into account.

Parameters
----------
objs: a single object or an iterable with objects.

Returns
-------
list of tuples
    The list will be empty if no valid object is found.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/gui_utils.py:356`. Decorators are copied as source expressions and have not been executed.

## `draftutils.gui_utils.apply_current_style`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def apply_current_style(objs):
```

Apply the current style to one or more objects.

Parameters
----------
objs: a single object or an iterable with objects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/gui_utils.py:465`. Decorators are copied as source expressions and have not been executed.

## `draftutils.gui_utils.restore_view_object`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def restore_view_object(obj, vp_module, vp_class, format=True, format_ref=None):
```

Restore the ViewObject if the object was saved without the GUI.

Parameters
----------
obj: App::DocumentObject
    Object whose ViewObject needs to be restored.

vp_module: string
    View provider module. Must be in the draftviewproviders directory.

vp_class: string
    View provider class.

format: bool, optional
    Defaults to `True`.
    If `True` the `format_object` function is called to update the
    properties of the ViewObject.

format_ref: App::DocumentObject, optional
    Defaults to `None`.
    Reference object to copy ViewObject properties from.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/gui_utils.py:491`. Decorators are copied as source expressions and have not been executed.

## `draftutils.gui_utils.format_object`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def format_object(target, origin=None, ignore_construction=False):
```

Apply visual properties to an object.

This function only works if the graphical interface is available.

If origin is `None` and target is not an annotation, the DefaultDrawStyle
and DefaultDisplayMode preferences are applied. Else, the properties of
origin are applied to target.

If construction mode is active target is then placed in the construction
group and the `constr` color is applied to its applicable color properties:
TextColor, PointColor, LineColor, and ShapeColor.

Parameters
----------
target: App::DocumentObject

origin: App::DocumentObject, optional
    Defaults to `None`.
    If construction mode is not active, its visual properties are assigned
    to `target`, with the exception of `BoundingBox`, `Proxy`, `RootNode`
    and `Visibility`.

ignore_construction: bool, optional
    Defaults to `False`.
    Set to `True` to ignore construction mode.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/gui_utils.py:524`. Decorators are copied as source expressions and have not been executed.

## `draftutils.gui_utils.formatObject`

Status: source-defined name; no independently verified stability/export guarantee.

```python
formatObject = format_object
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/Draft/draftutils/gui_utils.py:628`. Decorators are copied as source expressions and have not been executed.

## `draftutils.gui_utils.get_selection`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_selection(gui=App.GuiUp):
```

Return the current selected objects.

This function only works if the graphical interface is available
as the selection module only works on the 3D view.

It wraps around `Gui.Selection.getSelection`

Parameters
----------
gui: bool, optional
    It defaults to the value of `App.GuiUp`, which is `True`
    when the interface exists, and `False` otherwise.

    This value can be set to `False` to simulate
    when the interface is not available.

Returns
-------
list of App::DocumentObject
    Returns a list of objects in the current selection.
    It can be an empty list if no object is selected.

    If the interface is not available, it returns `None`.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/gui_utils.py:631`. Decorators are copied as source expressions and have not been executed.

## `draftutils.gui_utils.getSelection`

Status: source-defined name; no independently verified stability/export guarantee.

```python
getSelection = get_selection
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/Draft/draftutils/gui_utils.py:661`. Decorators are copied as source expressions and have not been executed.

## `draftutils.gui_utils.get_selection_ex`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_selection_ex(gui=App.GuiUp):
```

Return the current selected objects together with their subelements.

This function only works if the graphical interface is available
as the selection module only works on the 3D view.

It wraps around `Gui.Selection.getSelectionEx`

Parameters
----------
gui: bool, optional
    It defaults to the value of `App.GuiUp`, which is `True`
    when the interface exists, and `False` otherwise.

    This value can be set to `False` to simulate
    when the interface is not available.

Returns
-------
list of Gui::SelectionObject
    Returns a list of `Gui::SelectionObject` in the current selection.
    It can be an empty list if no object is selected.

    If the interface is not available, it returns `None`.

Selection objects
-----------------
One `Gui::SelectionObject` has attributes that indicate which specific
subelements, that is, vertices, wires, and faces, were selected.
This can be useful to operate on the subelements themselves.
If `G` is a `Gui::SelectionObject`
 * `G.Object` is the selected object
 * `G.ObjectName` is the name of the selected object
 * `G.HasSubObjects` is `True` if there are subelements in the selection
 * `G.SubObjects` is a tuple of the subelements' shapes
 * `G.SubElementNames` is a tuple of the subelements' names

`SubObjects` and `SubElementNames` should be empty tuples
if `HasSubObjects` is `False`.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/gui_utils.py:664`. Decorators are copied as source expressions and have not been executed.

## `draftutils.gui_utils.getSelectionEx`

Status: source-defined name; no independently verified stability/export guarantee.

```python
getSelectionEx = get_selection_ex
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/Draft/draftutils/gui_utils.py:709`. Decorators are copied as source expressions and have not been executed.

## `draftutils.gui_utils.select`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def select(objs=None, gui=App.GuiUp):
```

Unselects everything and selects only the given list of objects.

This function only works if the graphical interface is available
as the selection module only works on the 3D view.

Parameters
----------
objs: list of App::DocumentObjects or tuples, or a single object or tuple, optional
    It defaults to `None`.
    Format for tuples:
    `(doc.Name or "", sel.Object.Name, sel.SubElementName or "")`
    For example (Box nested in Part):
    `("", "Part", "Box.Edge1")`

gui: bool, optional
    It defaults to the value of `App.GuiUp`, which is `True`
    when the interface exists, and `False` otherwise.

    This value can be set to `False` to simulate
    when the interface is not available.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/gui_utils.py:712`. Decorators are copied as source expressions and have not been executed.

## `draftutils.gui_utils.load_texture`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def load_texture(filename, size=None, gui=App.GuiUp):
```

Return a Coin.SoSFImage to use as a texture for a 2D plane.

This function only works if the graphical interface is available
as the visual properties that can be applied to a shape
are attributes of the view provider (`obj.ViewObject`).

Parameters
----------
filename: str
    A path to a pixel image file (PNG) that can be used as a texture
    on the face of an object.

size: tuple of two int, or a single int, optional
    It defaults to `None`.
    If a tuple is given, the two values define the width and height
    in pixels to which the loaded image will be scaled.
    If it is a single value, it is used for both dimensions.

    If it is `None`, the size will be determined from the `QImage`
    created from `filename`.

    CURRENTLY the input `size` parameter IS NOT USED.
    It always uses the `QImage` to determine this information.

gui: bool, optional
    It defaults to the value of `App.GuiUp`, which is `True`
    when the interface exists, and `False` otherwise.

    This value can be set to `False` to simulate
    when the interface is not available.

Returns
-------
coin.SoSFImage
    An image object with the appropriate size, number of components
    (grayscale, grayscale and transparency, color,
    color and transparency), and byte data.

    It returns `None` if the interface is not available,
    or if there is a problem creating the image.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/gui_utils.py:757`. Decorators are copied as source expressions and have not been executed.

## `draftutils.gui_utils.loadTexture`

Status: source-defined name; no independently verified stability/export guarantee.

```python
loadTexture = load_texture
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/Draft/draftutils/gui_utils.py:880`. Decorators are copied as source expressions and have not been executed.

## `draftutils.gui_utils.migrate_text_display_mode`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def migrate_text_display_mode(obj_type='Text', mode='3D text', doc=None):
```

Migrate the display mode of objects of certain type.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/gui_utils.py:883`. Decorators are copied as source expressions and have not been executed.

## `draftutils.gui_utils.get_bbox`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_bbox(obj, debug=False):
```

Return a BoundBox from any object that has a Coin RootNode.

Normally the bounding box of an object can be taken
from its `Part::TopoShape`.
::
    >>> print(obj.Shape.BoundBox)

However, for objects without a `Shape`, such as those
derived from `App::FeaturePython` like `Draft Text` and `Draft Dimension`,
the bounding box can be calculated from the `RootNode` of the viewprovider.

Parameters
----------
obj: App::DocumentObject
    Any object that has a `ViewObject.RootNode`.

Returns
-------
Base::BoundBox
    It returns a `BoundBox` object which has information like
    minimum and maximum values of X, Y, and Z, as well as bounding box
    center.

None
    If there is a problem it will return `None`.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftutils/gui_utils.py:893`. Decorators are copied as source expressions and have not been executed.

