# Python source module `draftobjects.patharray`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftobjects/patharray.py`. Import path is source-routed; installed availability is unverified.

Provides the object code for the PathArray object.

The copies will be placed along a path like a polyline, spline, or bezier
curve, and along the selected subelements.

To Do
-----
The `'PathSubelements'` property must be changed in type, as it does not need
to be an `App::PropertyLinkSubList`.
A `LinkSubList` is to select multiple subelements (edges) from multiple
objects. However, since we need to select a `'Path Object'` already,
which is a single object, the subelements that we can choose must belong
to this `'Path Object'` only.

Therefore, the correct property that must be used is `App::PropertyLinkSub`.
Then in the property editor we will be unable to select more than one object
thus preventing errors of the subelements not matching the `'PathObject'`.

In fact, both `'PathObject'` and `'PathSubelements'`
could be handled with a single `App::PropertyLinkSub` property,
as this property can be used to select a single object,
or a single object with its subelements.

In the future, we could migrate the properties, or outright break
compatibility with older objects by changing both properties
`'PathObject'` and `'PathSubelements'`.

An alternative to this would be to use a single `App::PropertyLinkSubList`.
This would allow us to build PathArrays on multiple objects and multiple
subelements (edges) of those objects at the same time. However, to do this,
the logic in `execute` would have to be changed to account for multiple
objects. Therefore, the first solution is simpler, that is, using
a single property of type `App::PropertyLinkSub`.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import lazy_loader.lazy_loader as lz

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftobjects.patharray.lz` -> `lazy_loader.lazy_loader`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftobjects/patharray.py:69`.

### from PySide.QtCore import QT_TRANSLATE_NOOP

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftobjects.patharray.QT_TRANSLATE_NOOP` -> `PySide.QtCore.QT_TRANSLATE_NOOP`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftobjects/patharray.py:70`.

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftobjects.patharray.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftobjects/patharray.py:72`.

### import DraftVecUtils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftobjects.patharray.DraftVecUtils` -> `DraftVecUtils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftobjects/patharray.py:73`.

### from draftgeoutils import geometry as geo_geometry

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftobjects.patharray.geo_geometry` -> `draftgeoutils.geometry`.

[Source module `draftgeoutils`](../../draftgeoutils/index.md).

Evidence: `src/Mod/Draft/draftobjects/patharray.py:74`.

### from draftgeoutils import wires as geo_wires

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftobjects.patharray.geo_wires` -> `draftgeoutils.wires`.

[Source module `draftgeoutils`](../../draftgeoutils/index.md).

Evidence: `src/Mod/Draft/draftobjects/patharray.py:75`.

### from draftobjects.base import DraftObject

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftobjects.patharray.DraftObject` -> `draftobjects.base.DraftObject`.

[Source module `draftobjects.base`](../base/index.md).

Evidence: `src/Mod/Draft/draftobjects/patharray.py:76`.

### from draftobjects.draftlink import DraftLink

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftobjects.patharray.DraftLink` -> `draftobjects.draftlink.DraftLink`.

[Source module `draftobjects.draftlink`](../draftlink/index.md).

Evidence: `src/Mod/Draft/draftobjects/patharray.py:77`.

### from draftutils.messages import _err, _log, _wrn

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftobjects.patharray._err` -> `draftutils.messages._err`.

Bound source name `draftobjects.patharray._log` -> `draftutils.messages._log`.

Bound source name `draftobjects.patharray._wrn` -> `draftutils.messages._wrn`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftobjects/patharray.py:78`.

### from draftutils.translate import translate

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftobjects.patharray.translate` -> `draftutils.translate.translate`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftobjects/patharray.py:79`.

## Classes

- [draftobjects.patharray.PathArray](PathArray.md)

## `draftobjects.patharray.placements_on_path`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def placements_on_path(shapeRotation, pathwire, count, xlate, align, mode='Original', forceNormal=False, normalOverride=None, startOffset=0.0, endOffset=0.0, reversePath=False, spacingMode='Fixed count', spacingUnit=20.0, useSpacingPattern=False, spacingPattern=[1, 1, 1, 1]):
```

Calculate the placements of a shape along a given path.

Copies will be distributed according to spacing mode - evenly or in fixed offsets.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/patharray.py:576`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.patharray.calculatePlacementsOnPath`

Status: source-defined name; no independently verified stability/export guarantee.

```python
calculatePlacementsOnPath = placements_on_path
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/Draft/draftobjects/patharray.py:742`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.patharray.calculate_placement`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def calculate_placement(globalRotation, edge, offset, RefPt, xlate, align, normal=App.Vector(0.0, 0.0, 1.0), mode='Original', overrideNormal=False, reversePath=False):
```

Orient shape in the local coordinate system at parameter offset.

http://en.wikipedia.org/wiki/Euler_angles (previous version)
http://en.wikipedia.org/wiki/Quaternions

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/patharray.py:745`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.patharray.calculatePlacement`

Status: source-defined name; no independently verified stability/export guarantee.

```python
calculatePlacement = calculate_placement
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/Draft/draftobjects/patharray.py:850`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.patharray.get_parameter_from_v0`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_parameter_from_v0(edge, offset):
```

Return parameter at distance offset from edge.Vertexes[0].

sb method in Part.TopoShapeEdge???

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/patharray.py:853`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.patharray.getParameterFromV0`

Status: source-defined name; no independently verified stability/export guarantee.

```python
getParameterFromV0 = get_parameter_from_v0
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/Draft/draftobjects/patharray.py:871`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`draftobjects.patharray._PathArray`. These are source internals unless an explicit export establishes otherwise.

