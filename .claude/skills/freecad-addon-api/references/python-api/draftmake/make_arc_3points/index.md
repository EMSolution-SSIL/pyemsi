# Python source module `draftmake.make_arc_3points`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftmake/make_arc_3points.py`. Import path is source-routed; installed availability is unverified.

Provides functions to create Arc objects by using 3 points.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import math

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_arc_3points.math` -> `math`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_arc_3points.py:33`.

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_arc_3points.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_arc_3points.py:35`.

### import Part

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_arc_3points.Part` -> `Part`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_arc_3points.py:36`.

### from draftmake import make_circle

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_arc_3points.make_circle` -> `draftmake.make_circle`.

[Source module `draftmake`](../index.md).

Evidence: `src/Mod/Draft/draftmake/make_arc_3points.py:37`.

### from draftutils import utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_arc_3points.utils` -> `draftutils.utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_arc_3points.py:38`.

### from draftutils.messages import _err

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_arc_3points._err` -> `draftutils.messages._err`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_arc_3points.py:39`.

### from draftutils.translate import translate

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_arc_3points.translate` -> `draftutils.translate.translate`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_arc_3points.py:40`.

### from freecad.deprecation import deprecated

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_arc_3points.deprecated` -> `freecad.deprecation.deprecated`.

[Source module `freecad.deprecation`](../../freecad/deprecation/index.md).

Evidence: `src/Mod/Draft/draftmake/make_arc_3points.py:41`.

## `draftmake.make_arc_3points.make_arc_3_points`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def make_arc_3_points(points, placement=None, face=False, support=None, primitive=False):
```

Draw a circular arc defined by three points on the circumference.

Parameters
----------
points: list of Base::Vector3
    A list that must be three points.

placement: Base::Placement, optional
    It is adjusted to match the geometry of the created edge.
    The Z axis of the adjusted placement will be parallel to the
    (negative) edge axis. Its Base will match the edge center.

face: bool, optional
    It defaults to `False`.
    If it is `True` it will create a face in the closed arc.
    Otherwise only the circumference edge will be shown.

support: App::PropertyLinkSubList, optional
    It defaults to `None`.
    It is a list containing tuples to define the attachment
    of the new object.

    This parameter sets the `Support` property but it only really
    affects the position of the new object if its `MapMode` is
    set to other than `'Deactivated'`.

primitive: bool, optional
    It defaults to `False`. If it is `True`, it will create a Part
    primitive instead of a Draft object.
    In this case, `placement`, `face` and `support` are ignored.

Returns
-------
Part::Part2DObject or Part::Feature
    The new arc object.
    Normally it returns a parametric Draft object (`Part::Part2DObject`).
    If `primitive` is `True`, it returns a basic `Part::Feature`.

None
    Returns `None` if there is a problem and the object cannot be created.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_arc_3points.py:44`. Decorators are copied as source expressions and have not been executed.

## `draftmake.make_arc_3points.make_arc_3points`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@deprecated(deprecated_in='26.3', removed_in='28.3', replacement='Draft.make_arc_3_points()')
def make_arc_3points(*args, **kwarg):
```

DEPRECATED. Use 'make_arc_3_points'.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_arc_3points.py:135`. Decorators are copied as source expressions and have not been executed.

