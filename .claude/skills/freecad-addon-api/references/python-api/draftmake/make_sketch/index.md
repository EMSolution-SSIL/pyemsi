# Python source module `draftmake.make_sketch`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftmake/make_sketch.py`. Import path is source-routed; installed availability is unverified.

Provides functions to create Sketch objects from Draft objects.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import math

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_sketch.math` -> `math`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_sketch.py:34`.

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_sketch.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_sketch.py:36`.

### import DraftVecUtils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_sketch.DraftVecUtils` -> `DraftVecUtils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_sketch.py:37`.

### from draftgeoutils import edges as geo_edges

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_sketch.geo_edges` -> `draftgeoutils.edges`.

[Source module `draftgeoutils`](../../draftgeoutils/index.md).

Evidence: `src/Mod/Draft/draftmake/make_sketch.py:38`.

### from draftgeoutils import general as geo_general

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_sketch.geo_general` -> `draftgeoutils.general`.

[Source module `draftgeoutils`](../../draftgeoutils/index.md).

Evidence: `src/Mod/Draft/draftmake/make_sketch.py:39`.

### from draftgeoutils import geometry as geo_geometry

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_sketch.geo_geometry` -> `draftgeoutils.geometry`.

[Source module `draftgeoutils`](../../draftgeoutils/index.md).

Evidence: `src/Mod/Draft/draftmake/make_sketch.py:40`.

### from draftutils import gui_utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_sketch.gui_utils` -> `draftutils.gui_utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_sketch.py:41`.

### from draftutils import utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_sketch.utils` -> `draftutils.utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_sketch.py:42`.

### from draftutils.translate import translate

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_sketch.translate` -> `draftutils.translate.translate`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_sketch.py:43`.

### from freecad.deprecation import deprecated

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_sketch.deprecated` -> `freecad.deprecation.deprecated`.

[Source module `freecad.deprecation`](../../freecad/deprecation/index.md).

Evidence: `src/Mod/Draft/draftmake/make_sketch.py:44`.

## `draftmake.make_sketch.make_sketch`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def make_sketch(objects_list, autoconstraints=False, addTo=None, delete=False, name='Sketch', radiusPrecision=-1, tol=0.001):
```

make_sketch(objects_list, [autoconstraints], [addTo], [delete],
               [name], [radiusPrecision], [tol])

Makes a Sketch objects_list with the given Draft objects.

Parameters
----------
objects_list: can be single or list of objects of Draft type objects,
    Part::Feature, Part.Shape, or mix of them.

autoconstraints(False): if True, coincident, horizontal and vertical
    constraints will be added automatically.

addTo(None): if set to an existing sketch, geometry will be added to it
    instead of creating a new one.

delete(False): if True, the original object will be deleted.
    If set to a string "all" the object and all its linked object will be
    deleted.

name("Sketch"): the name for the new sketch object.

radiusPrecision(-1): If <0, disable radius constraint. If =0, add individual
    radius constraint. If >0, the radius will be rounded according to this
    precision, and "Equal" constraint will be added to curve with equal
    radius within precision.

tol(1e-3): Tolerance used to check if the shapes are planar and coplanar.
    Consider change to tol=-1 for a more accurate analysis.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_sketch.py:47`. Decorators are copied as source expressions and have not been executed.

## `draftmake.make_sketch.makeSketch`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@deprecated(deprecated_in='26.3', removed_in='28.3', replacement='Draft.make_sketch()')
def makeSketch(*args, **kwarg):
```

DEPRECATED. Use 'make_sketch'.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_sketch.py:274`. Decorators are copied as source expressions and have not been executed.

