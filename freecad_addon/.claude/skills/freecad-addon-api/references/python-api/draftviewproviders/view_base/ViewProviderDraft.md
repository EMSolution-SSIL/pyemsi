# `draftviewproviders.view_base.ViewProviderDraft`

[Source module](index.md)

```python
class ViewProviderDraft(object):
```

The base class for Draft view providers.

Parameters
----------
vobj : a base C++ view provider
    The view provider of the scripted object (`obj.ViewObject`),
    which commonly may be of types `PartGui::ViewProvider2DObjectPython`,
    `PartGui::ViewProviderPython`, or `Gui::ViewProviderFeaturePython`.

    A basic view provider is instantiated during the creation
    of the base C++ object, for example,
    `Part::Part2DObjectPython`, `Part::FeaturePython`,
    or `App::FeaturePython`.

        >>> obj = App.ActiveDocument.addObject('Part::Part2DObjectPython')
        >>> vobj = obj.ViewObject
        >>> ViewProviderDraft(vobj)

    This view provider class instance is stored in the `Proxy` attribute
    of the base view provider.
    ::
        vobj.Proxy = self

Attributes
----------
Object : the base C++ object
    The scripted document object that is associated
    with this view provider, which commonly may be of types
    `Part::Part2DObjectPython`, `Part::FeaturePython`,
    or `App::FeaturePython`.

texture : coin.SoTexture2
    A texture that could be added to this object.

texcoords : coin.SoTextureCoordinatePlane
    The coordinates defining a plane to use for aligning the texture.

These class attributes are accessible through the `Proxy` object:
`vobj.Proxy.Object`, `vobj.Proxy.texture`, etc.

Evidence: `src/Mod/Draft/draftviewproviders/view_base.py:55`. Source-defined class; runtime behavior and support status unverified.

## `draftviewproviders.view_base.ViewProviderDraft.__init__`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def __init__(self, vobj):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_base.py:97`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_base.ViewProviderDraft.dumps`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def dumps(self):
```

Return a tuple of all serializable objects or None.

When saving the document this view provider object gets stored
using Python's `json` module.

Since we have some un-serializable objects (Coin objects) in here
we must define this method to return a tuple of all serializable
objects or `None`.

Override this method to define the serializable objects to return.

By default it returns `None`.

Returns
-------
None

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_base.py:130`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_base.ViewProviderDraft.loads`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def loads(self, state):
```

Set some internal properties for all restored objects.

When a document is restored this method is used to set some properties
for the objects stored with `json`.

Override this method to define the properties to change for the
restored serialized objects.

By default no objects were serialized with `dumps`,
so nothing needs to be done here, and it returns `None`.

Parameters
----------
state : state
    A serialized object.

Returns
-------
None

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_base.py:150`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_base.ViewProviderDraft.attach`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def attach(self, vobj):
```

Set up the scene sub-graph of the view provider.

This method should always be defined, even if it does nothing.

Override this method to set up a custom scene.

Parameters
----------
vobj : the view provider of the scripted object.
    This is `obj.ViewObject`.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_base.py:173`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_base.ViewProviderDraft.updateData`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def updateData(self, obj, prop):
```

Run when an object property is changed.

Override this method to handle the behavior of the view provider
depending on changes that occur to the real object's properties.

By default, no property is tested, and it does nothing.

Parameters
----------
obj : the base C++ object
    The scripted document object that is associated
    with this view provider, which commonly may be of types
    `Part::Part2DObjectPython`, `Part::FeaturePython`,
    or `App::FeaturePython`.

prop : str
    Name of the property that was modified.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_base.py:191`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_base.ViewProviderDraft.getDisplayModes`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getDisplayModes(self, vobj):
```

Return a list of display modes.

Override this method to return a list of strings with
display mode styles, such as `'Flat Lines'`, `'Shaded'`,
`'Wireframe'`, `'Points'`.

By default it returns an empty list.

Parameters
----------
vobj : the view provider of the scripted object.
    This is `obj.ViewObject`.

Returns
-------
list
    Empty list `[ ]`

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_base.py:212`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_base.ViewProviderDraft.getDefaultDisplayMode`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getDefaultDisplayMode(self):
```

Return the default mode defined in getDisplayModes.

Override this method to return a string with the default display mode.

By default it returns `'Flat Lines'`.

Returns
-------
str
    `'Flat Lines'`

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_base.py:234`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_base.ViewProviderDraft.setDisplayMode`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def setDisplayMode(self, mode):
```

Map the modes defined in attach with those in getDisplayModes.

This method is optional.

By default since they have the same names nothing needs to be done,
and it just returns the input `mode`.

Parameters
----------
str
    A string defining a display mode such as
    `'Flat Lines'`, `'Shaded'`, `'Wireframe'`, `'Points'`.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_base.py:249`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_base.ViewProviderDraft.onChanged`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def onChanged(self, vobj, prop):
```

Run when a view property is changed.

Override this method to handle the behavior
of the view provider depending on changes that occur to its properties
such as line color, line width, point color, point size,
draw style, shape color, transparency, and others.

This method  updates the texture and pattern if
the properties `TextureImage`, `Pattern`, `ShapeAppearance`,
and `PatternSize` change.

Parameters
----------
vobj : the view provider of the scripted object.
    This is `obj.ViewObject`.

prop : str
    Name of the property that was modified.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_base.py:265`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_base.ViewProviderDraft.execute`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def execute(self, vobj):
```

Run when the object is created or recomputed.

Override this method to produce effects when the object
is newly created, and whenever the document is recomputed.

By default it does nothing.

Parameters
----------
vobj : the view provider of the scripted object.
    This is `obj.ViewObject`.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_base.py:360`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_base.ViewProviderDraft.setEdit`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def setEdit(self, vobj, mode):
```

Enter the edit mode of the object.

Parameters
----------
vobj : the view provider of the scripted object.
    This is `obj.ViewObject`.

mode : int
    0, 1, 2 or 3. See the `Std_UserEditMode` command.

Returns
-------
bool or None
    `False`: NOT USED HERE.
             Do not enter edit mode (unsetEdit is not called).
    `True` : Handled edit mode.
             Handled modes are 0 and 3, and only for certain objects.
             The unsetEdit function should then also return `True`.
    `None` : Unhandled edit mode.
             Handling is left to Part::FeaturePython code.
             The unsetEdit function should then also return `None`.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_base.py:375`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_base.ViewProviderDraft.unsetEdit`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def unsetEdit(self, vobj, mode):
```

Terminate the edit mode of the object.

See setEdit.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_base.py:427`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_base.ViewProviderDraft.setupContextMenu`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def setupContextMenu(self, vobj, menu):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_base.py:454`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_base.ViewProviderDraft.edit`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def edit(self):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_base.py:503`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_base.ViewProviderDraft.getIcon`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getIcon(self):
```

Return the path to the icon used by the view provider.

The path can be a full path in the system, or a relative path
inside the compiled resource file.
It can also be a string that defines the icon in XPM format.

Override this method to provide a specific icon
for the object in the tree view.

By default it returns the path to the `Draft_Draft.svg` icon.

Returns
-------
str
    `':/icons/Draft_Draft.svg'`

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_base.py:506`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_base.ViewProviderDraft.claimChildren`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def claimChildren(self):
```

Return objects that will be placed under it in the tree view.

Override this method to return a list with objects
that will appear under this object in the tree view.
That is, this object becomes the `parent`,
and all those under it are the `children`.

By default the returned list is composed of objects from
`Object.Base`, `Object.Objects`, `Object.Components`,
and `Object.Group`, if they exist.

Returns
-------
list
    List of objects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_base.py:538`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`draftviewproviders.view_base.ViewProviderDraft._set_properties`, `draftviewproviders.view_base.ViewProviderDraft._update_pattern_size`. These are source internals unless an explicit export establishes otherwise.

