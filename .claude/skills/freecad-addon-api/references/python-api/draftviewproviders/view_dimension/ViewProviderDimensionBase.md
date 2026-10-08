# `draftviewproviders.view_dimension.ViewProviderDimensionBase`

[Source module](index.md)

```python
class ViewProviderDimensionBase(ViewProviderDraftAnnotation):
```

The base viewprovider for the Draft Dimensions object.

This class is not used directly, but inherited by dimension
viewproviders like linear, radial, and angular.

Dimension nomeclature
---------------------
The dimension object depends on various variables to draw the lines
that are drawn on 3D view.
::
        |              txt               |      e
    ----b---------a----------------------b----
        |                                |
        |                                |      d
        |                                |

    c  (t)                              (t)   c

From the object class

* `a`, `Dimline`, point through which the dimension line goes through

From the viewprovider class

* `b`, `ArrowTypeStart`, `ArrowTypeEnd`, `ArrowSizeStart`, `ArrowSizeEnd`, the symbol shown on the endpoints
* `c`, `DimOvershoot`, extension to the dimension line going through `a`
* `d`, `ExtLines`, distance to target `(t)`
* `e`, `ExtOvershoot`, extension in the opposite direction to `(t)`
* `txt`, text label showing the value of the measurement

Coin object structure
---------------------
The scenegraph is set from two main nodes.
::
    vobj.node_wld.linecolor
                 .drawstyle
                 .lineswitch_wld.coords
                                .line
                                .marks
                                .marksDimOvershoot
                                .marksExtOvershoot
                 .label_wld.textpos
                           .textcolor
                           .font
                           .text_wld

    vobj.node_scr.linecolor
                 .drawstyle
                 .lineswitch_scr.coords
                                .line
                                .marks
                                .marksDimOvershoot
                                .marksExtOvershoot
                 .label_scr.textpos
                           .textcolor
                           .font
                           .text_scr

Evidence: `src/Mod/Draft/draftviewproviders/view_dimension.py:62`. Source-defined class; runtime behavior and support status unverified.

## `draftviewproviders.view_dimension.ViewProviderDimensionBase.set_text_properties`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def set_text_properties(self, vobj, properties):
```

Set text properties only if they don't already exist.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_dimension.py:122`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_dimension.ViewProviderDimensionBase.set_units_properties`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def set_units_properties(self, vobj, properties):
```

Set unit properties only if they don't already exist.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_dimension.py:155`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_dimension.ViewProviderDimensionBase.set_graphics_properties`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def set_graphics_properties(self, vobj, properties):
```

Set graphics properties only if they don't already exist.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_dimension.py:179`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_dimension.ViewProviderDimensionBase.getIcon`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getIcon(self):
```

Return the path to the icon used by the viewprovider.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_dimension.py:213`. Decorators are copied as source expressions and have not been executed.

