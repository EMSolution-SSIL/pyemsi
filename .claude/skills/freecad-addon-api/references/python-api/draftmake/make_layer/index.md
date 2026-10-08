# Python source module `draftmake.make_layer`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftmake/make_layer.py`. Import path is source-routed; installed availability is unverified.

Provides functions to create Layer objects.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_layer.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_layer.py:34`.

### from draftobjects.layer import Layer, LayerContainer

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_layer.Layer` -> `draftobjects.layer.Layer`.

Bound source name `draftmake.make_layer.LayerContainer` -> `draftobjects.layer.LayerContainer`.

[Source module `draftobjects.layer`](../../draftobjects/layer/index.md).

Evidence: `src/Mod/Draft/draftmake/make_layer.py:35`.

### from draftutils import utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_layer.utils` -> `draftutils.utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_layer.py:36`.

### from draftutils.messages import _err

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_layer._err` -> `draftutils.messages._err`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_layer.py:37`.

### from draftutils.translate import translate

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_layer.translate` -> `draftutils.translate.translate`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_layer.py:38`.

### from freecad.deprecation import deprecated

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_layer.deprecated` -> `freecad.deprecation.deprecated`.

[Source module `freecad.deprecation`](../../freecad/deprecation/index.md).

Evidence: `src/Mod/Draft/draftmake/make_layer.py:39`.

### from draftviewproviders.view_layer import ViewProviderLayer, ViewProviderLayerContainer

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if App.GuiUp`.

Bound source name `draftmake.make_layer.ViewProviderLayer` -> `draftviewproviders.view_layer.ViewProviderLayer`.

Bound source name `draftmake.make_layer.ViewProviderLayerContainer` -> `draftviewproviders.view_layer.ViewProviderLayerContainer`.

[Source module `draftviewproviders.view_layer`](../../draftviewproviders/view_layer/index.md).

Evidence: `src/Mod/Draft/draftmake/make_layer.py:42`.

## `draftmake.make_layer.get_layer_container`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_layer_container():
```

Return a group object to put layers in.

Returns
-------
App::DocumentObjectGroupPython
    The existing group object named `'LayerContainer'`
    of type `LayerContainer`.
    If it doesn't exist it will create it with this default Name.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_layer.py:45`. Decorators are copied as source expressions and have not been executed.

## `draftmake.make_layer.getLayerContainer`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@deprecated(deprecated_in='26.3', removed_in='28.3', replacement='Draft.get_layer_container()')
def getLayerContainer():
```

DEPRECATED. Use 'get_layer_container'.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_layer.py:80`. Decorators are copied as source expressions and have not been executed.

## `draftmake.make_layer.make_layer`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def make_layer(name=None, line_color=(0.0, 0.0, 0.0), shape_color=(0.8, 0.8, 0.8), line_width=2.0, draw_style='Solid', transparency=0):
```

Create a Layer object in the active document.

If a layer container named `'LayerContainer'` does not exist, it is created.

A layer controls the view properties of the objects inside the layer.
All parameters except for `name` only apply if the graphical interface
is up.

All parameters that control view properties can be set to `None`. Their
value, as set by the view provider (matching the current preferences), is
then not changed.

Parameters
----------
name: str or `None`, optional
    It defaults to `None`.
    It is used to set the layer's `Label`. If it is `None` the `Label` is
    set to `'Layer'` or to its translation in the current language.

line_color: tuple or `None`, optional
    It defaults to `(0.0, 0.0, 0.0)`.
    If it is given, it should be a tuple of three floating point values
    from 0.0 to 1.0.

shape_color: tuple or `None`, optional
    It defaults to `(0.8, 0.8, 0.8)`.
    If it is given, it should be a tuple of three floating point values
    from 0.0 to 1.0.

line_width: float or `None`, optional
    It defaults to 2.0.
    It determines the width of the edges of the objects contained in the layer.

draw_style: str or `None`, optional
    It defaults to `'Solid'`.
    It determines the style of the edges of the objects contained in the layer.
    If it is given, it should be 'Solid', 'Dashed', 'Dotted' or 'Dashdot'.

transparency: int or `None`, optional
    It defaults to 0.
    It should be an integer from 0 to 100.

Return
------
App::FeaturePython
    A scripted object of type `'Layer'`.
    This object does not have a `Shape` attribute.
    Modifying the view properties of this object will affect the objects
    inside of it.

None
    If there is a problem it will return `None`.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_layer.py:85`. Decorators are copied as source expressions and have not been executed.

