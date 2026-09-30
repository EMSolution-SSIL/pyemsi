# `draftviewproviders.view_dimension.ViewProviderLinearDimension`

[Source module](index.md)

```python
class ViewProviderLinearDimension(ViewProviderDimensionBase):
```

The viewprovider for the Linear Dimension objects.

This includes straight edge measurement, as well as measurement
of circular edges, and circumferences.

Evidence: `src/Mod/Draft/draftviewproviders/view_dimension.py:218`. Source-defined class; runtime behavior and support status unverified.

## `draftviewproviders.view_dimension.ViewProviderLinearDimension.set_graphics_properties`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def set_graphics_properties(self, vobj, properties):
```

Set graphics properties only if they don't already exist.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_dimension.py:225`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_dimension.ViewProviderLinearDimension.attach`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def attach(self, vobj):
```

Set up the scene sub-graph of the viewprovider.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_dimension.py:236`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_dimension.ViewProviderLinearDimension.updateData`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def updateData(self, obj, prop):
```

Execute when a property from the Proxy class is changed.

It only runs if `Start`, `End`, `Dimline`, or `Direction` changed.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_dimension.py:324`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_dimension.ViewProviderLinearDimension.onChanged`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def onChanged(self, vobj, prop):
```

Execute when a view property is changed.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_dimension.py:592`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_dimension.ViewProviderLinearDimension.remove_dim_arrows`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def remove_dim_arrows(self):
```

Remove dimension arrows in the dimension lines.

Remove the existing nodes.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_dimension.py:675`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_dimension.ViewProviderLinearDimension.draw_dim_arrows`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def draw_dim_arrows(self, vobj):
```

Draw dimension arrows.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_dimension.py:683`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_dimension.ViewProviderLinearDimension.remove_dim_overshoot`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def remove_dim_overshoot(self):
```

Remove the dimension overshoot lines.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_dimension.py:726`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_dimension.ViewProviderLinearDimension.draw_dim_overshoot`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def draw_dim_overshoot(self, vobj):
```

Draw dimension overshoot lines.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_dimension.py:731`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_dimension.ViewProviderLinearDimension.remove_ext_overshoot`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def remove_ext_overshoot(self):
```

Remove dimension extension overshoot lines.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_dimension.py:756`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_dimension.ViewProviderLinearDimension.draw_ext_overshoot`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def draw_ext_overshoot(self, vobj):
```

Draw dimension extension overshoot lines.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_dimension.py:761`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_dimension.ViewProviderLinearDimension.is_linked_to_circle`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def is_linked_to_circle(self):
```

Return true if the dimension measures a circular edge.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_dimension.py:785`. Decorators are copied as source expressions and have not been executed.

## `draftviewproviders.view_dimension.ViewProviderLinearDimension.getIcon`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getIcon(self):
```

Return the path to the icon used by the viewprovider.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftviewproviders/view_dimension.py:799`. Decorators are copied as source expressions and have not been executed.

