# Python source module `draftobjects.dimension`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftobjects/dimension.py`. Import path is source-routed; installed availability is unverified.

Provides the object code for the dimension objects.

This includes the `LinearDimension` and `AgularDimension`.
The first one measures a distance between two points or vertices
in an object; it includes radial dimensions of circular arcs.
The second one creates an arc between two straight lines to measure
the angle between both.

To Do
-----
1. Currently the angular dimension does not use linked geometrical
elements, meaning that it cannot update its `Angle` by picking lines or edges
from objects. If fact, `LinkedGeometry` is hidden to prevent the user
from picking any object.

At the moment the user must manually modify `FirstAngle` and `LastAngle`
to obtain a new `Angle`, but since the values are manually entered
the result is not parametrically tied to any actual object in the document.

We introduced a function `measure_two_obj_angles` to calculate
the corresponding parameters from a pair of objects and their edges.
Currently this function is deactivated because we don't consider it
to be ready; it is there for testing purposes only.
This needs to be improved because at the moment it only gives
one possible angle. We should be able to get the four angles
of a two-line intersection. Maybe a new property is required
to indicate the quadrant to choose and display.

2. In general, the `LinkedGeometry` property must be changed in type,
as it does not need to be an `App::PropertyLinkSubList`.
A `LinkSubList` is to select multiple subelements (vertices, edges)
from multiple objects (two lines). However, since we typically measure
a single object, for example, a single line or circle, the subelements
that we can choose must belong to this object only.

Therefore, just like in the case of the `PathArray` class the best property
that could be used is `App::PropertyLinkSub`.
Then in the property editor we will be unable to select more than one object
thus preventing errors of the subelements not matching the measured object.

3. Currently the `LinearDimension` class is able to measure the distance
between two arbitrary vertices in two distinct objects.
For this case `App::PropertyLinkSubList` is in fact the right property
to use, however, neither the `make_dimension` functions
nor the Gui Command are set up to use this type of information.
This has to be done manually by picking the two objects and the two vertices
in the property editor. That is, this functionality is not entirely intuitive,
so it is somewhat 'hidden' from the user.

So, the make function and the Gui Command should be expanded to consider
this case.

Another possibility would be to use one property (LinkSub) for single-object
measurements (linear, radial), and a second property (LinkSubList)
for two-object measurements (linear, angular). This would require adjustments
to the `execute` method to handle both cases properly. It may be necessary
to have another property to control which type to use.

4. The `Support` property is not used at all, so it should be removed.
It is just set at creation time by the `make_dimension` function
but it actually isn't used in the `execute` code.

5. In fact the `DimensionBase` class is not the best base class
than can be used as parent for all dimensions because it defines `Normal`,
`Support`, and `LinkedGeometry`, which aren't used in all cases.
In some of the derived classes, these properties are hidden.

So, together with what is explained in point 3, we probably need to use
a more generic base class, while at the same time improve the way
the link properties are used.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import math

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftobjects.dimension.math` -> `math`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftobjects/dimension.py:105`.

### from PySide.QtCore import QT_TRANSLATE_NOOP

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftobjects.dimension.QT_TRANSLATE_NOOP` -> `PySide.QtCore.QT_TRANSLATE_NOOP`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftobjects/dimension.py:106`.

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftobjects.dimension.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftobjects/dimension.py:108`.

### import DraftVecUtils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftobjects.dimension.DraftVecUtils` -> `DraftVecUtils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftobjects/dimension.py:109`.

### import WorkingPlane

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftobjects.dimension.WorkingPlane` -> `WorkingPlane`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftobjects/dimension.py:110`.

### from draftgeoutils import general as geo_general

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftobjects.dimension.geo_general` -> `draftgeoutils.general`.

[Source module `draftgeoutils`](../../draftgeoutils/index.md).

Evidence: `src/Mod/Draft/draftobjects/dimension.py:111`.

### from draftobjects.draft_annotation import DraftAnnotation

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftobjects.dimension.DraftAnnotation` -> `draftobjects.draft_annotation.DraftAnnotation`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftobjects/dimension.py:112`.

### from draftutils import gui_utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftobjects.dimension.gui_utils` -> `draftutils.gui_utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftobjects/dimension.py:113`.

### from draftutils import utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftobjects.dimension.utils` -> `draftutils.utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftobjects/dimension.py:114`.

### from draftutils.messages import _log

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftobjects.dimension._log` -> `draftutils.messages._log`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftobjects/dimension.py:115`.

## Classes

- [draftobjects.dimension.DimensionBase](DimensionBase.md)
- [draftobjects.dimension.LinearDimension](LinearDimension.md)
- [draftobjects.dimension.AngularDimension](AngularDimension.md)

## `draftobjects.dimension.measure_one_obj_edge`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def measure_one_obj_edge(obj, subelement, dim_point, diameter=False):
```

Measure one object with one subelement, a straight or circular edge.

Parameters
----------
obj: Part::Feature
    The object that is measured.

subelement: str
    The subelement that is measured, for example, `'Edge1'`.

dim_line: Base::Vector3
    A point through which the dimension goes through.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/dimension.py:377`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.dimension.measure_one_obj_vertices`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def measure_one_obj_vertices(obj, subelements):
```

Measure two vertices in the same object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/dimension.py:432`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.dimension.measure_two_objects`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def measure_two_objects(link_sub_1, link_sub_2):
```

Measure two vertices from two different objects.

Parameters
----------
link_sub_1: tuple
    A tuple containing one object and a list of subelement strings,
    which may be empty. Only the first subelement is considered, which
    must be a vertex.
    ::
        link_sub_1 = (obj1, ['VertexN', ...])

link_sub_2: tuple
    Same.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/dimension.py:449`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.dimension.measure_two_obj_angles`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def measure_two_obj_angles(link_sub_1, link_sub_2):
```

Measure two edges from two different objects to measure the angle.

This function is a prototype because it does not determine all possible
starting and ending angles that could be used to draw the dimension line,
which is a circular arc.

Parameters
----------
link_sub_1: tuple
    A tuple containing one object and a list of subelement strings,
    which may be empty. Only the first subelement is considered, which
    must be an edge.
    ::
        link_sub_1 = (obj1, ['EdgeN', ...])

link_sub_2: tuple
    Same.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/dimension.py:642`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`draftobjects.dimension._Dimension`, `draftobjects.dimension._AngularDimension`. These are source internals unless an explicit export establishes otherwise.

