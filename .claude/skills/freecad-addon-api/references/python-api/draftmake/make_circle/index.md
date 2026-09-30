# Python source module `draftmake.make_circle`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftmake/make_circle.py`. Import path is source-routed; installed availability is unverified.

Provides functions to create Circle objects.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import math

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_circle.math` -> `math`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_circle.py:33`.

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_circle.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_circle.py:35`.

### import Part

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_circle.Part` -> `Part`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_circle.py:36`.

### import DraftVecUtils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_circle.DraftVecUtils` -> `DraftVecUtils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_circle.py:37`.

### from draftgeoutils import general as geo_general

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_circle.geo_general` -> `draftgeoutils.general`.

[Source module `draftgeoutils`](../../draftgeoutils/index.md).

Evidence: `src/Mod/Draft/draftmake/make_circle.py:38`.

### from draftobjects.circle import Circle

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_circle.Circle` -> `draftobjects.circle.Circle`.

[Source module `draftobjects.circle`](../../draftobjects/circle/index.md).

Evidence: `src/Mod/Draft/draftmake/make_circle.py:39`.

### from draftutils import utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_circle.utils` -> `draftutils.utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_circle.py:40`.

### from draftutils import gui_utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_circle.gui_utils` -> `draftutils.gui_utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_circle.py:41`.

### from freecad.deprecation import deprecated

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_circle.deprecated` -> `freecad.deprecation.deprecated`.

[Source module `freecad.deprecation`](../../freecad/deprecation/index.md).

Evidence: `src/Mod/Draft/draftmake/make_circle.py:42`.

### from draftviewproviders.view_base import ViewProviderDraft

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if App.GuiUp`.

Bound source name `draftmake.make_circle.ViewProviderDraft` -> `draftviewproviders.view_base.ViewProviderDraft`.

[Source module `draftviewproviders.view_base`](../../draftviewproviders/view_base/index.md).

Evidence: `src/Mod/Draft/draftmake/make_circle.py:45`.

## `draftmake.make_circle.make_circle`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def make_circle(radius, placement=None, face=None, startangle=None, endangle=None, support=None):
```

make_circle(radius, [placement], [face], [startangle], [endangle])
or make_circle(edge, [placement], [face]):

Creates a circle object with given parameters.

If startangle and endangle are provided and not equal, the object will be
an arc instead of a full circle.

Parameters
----------
radius: the radius of the circle or the shape of a circular edge
    If it is an edge, startangle and endangle are ignored.
    edge.Curve must be a Part.Circle.

placement: optional
    If radius is an edge, placement is adjusted to match the geometry
    of the edge. The Z axis of the adjusted placement will be parallel
    to the (negative) edge axis. Its Base will match the edge center.

face: Bool
    If face is False, the circle is shown as a wireframe,
    otherwise as a face.

startangle: start angle of the circle (in degrees)
    Recalculated if not in the -360 to 360 range.

endangle: end angle of the circle (in degrees)
    Recalculated if not in the -360 to 360 range.

support: App::PropertyLinkSubList, optional
    It defaults to `None`.
    It is a list containing tuples to define the attachment
    of the new object.

    This parameter sets the `Support` property but it only really
    affects the position of the new object if its `MapMode` is
    set to other than `'Deactivated'`.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_circle.py:65`. Decorators are copied as source expressions and have not been executed.

## `draftmake.make_circle.makeCircle`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@deprecated(deprecated_in='26.3', removed_in='28.3', replacement='Draft.make_circle()')
def makeCircle(*args, **kwarg):
```

DEPRECATED. Use 'make_circle'.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_circle.py:166`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`draftmake.make_circle._get_normal`. These are source internals unless an explicit export establishes otherwise.

