# Python source module `draftfunctions.offset`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftfunctions/offset.py`. Import path is source-routed; installed availability is unverified.

Provides functions to create offsets of different shapes.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import math

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.offset.math` -> `math`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/offset.py:33`.

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.offset.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/offset.py:35`.

### import DraftVecUtils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.offset.DraftVecUtils` -> `DraftVecUtils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/offset.py:36`.

### from draftgeoutils import general as geo_general

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.offset.geo_general` -> `draftgeoutils.general`.

[Source module `draftgeoutils`](../../draftgeoutils/index.md).

Evidence: `src/Mod/Draft/draftfunctions/offset.py:37`.

### from draftgeoutils import offsets as geo_offsets

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.offset.geo_offsets` -> `draftgeoutils.offsets`.

[Source module `draftgeoutils`](../../draftgeoutils/index.md).

Evidence: `src/Mod/Draft/draftfunctions/offset.py:38`.

### from draftgeoutils import wires as geo_wires

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.offset.geo_wires` -> `draftgeoutils.wires`.

[Source module `draftgeoutils`](../../draftgeoutils/index.md).

Evidence: `src/Mod/Draft/draftfunctions/offset.py:39`.

### from draftmake.make_rectangle import make_rectangle

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.offset.make_rectangle` -> `draftmake.make_rectangle.make_rectangle`.

[Source module `draftmake.make_rectangle`](../../draftmake/make_rectangle/index.md).

Evidence: `src/Mod/Draft/draftfunctions/offset.py:40`.

### from draftmake.make_wire import make_wire

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.offset.make_wire` -> `draftmake.make_wire.make_wire`.

[Source module `draftmake.make_wire`](../../draftmake/make_wire/index.md).

Evidence: `src/Mod/Draft/draftfunctions/offset.py:41`.

### from draftmake.make_polygon import make_polygon

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.offset.make_polygon` -> `draftmake.make_polygon.make_polygon`.

[Source module `draftmake.make_polygon`](../../draftmake/make_polygon/index.md).

Evidence: `src/Mod/Draft/draftfunctions/offset.py:42`.

### from draftmake.make_circle import make_circle

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.offset.make_circle` -> `draftmake.make_circle.make_circle`.

[Source module `draftmake.make_circle`](../../draftmake/make_circle/index.md).

Evidence: `src/Mod/Draft/draftfunctions/offset.py:43`.

### from draftmake.make_bspline import make_bspline

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.offset.make_bspline` -> `draftmake.make_bspline.make_bspline`.

[Source module `draftmake.make_bspline`](../../draftmake/make_bspline/index.md).

Evidence: `src/Mod/Draft/draftfunctions/offset.py:44`.

### from draftutils import gui_utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.offset.gui_utils` -> `draftutils.gui_utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/offset.py:45`.

### from draftutils import params

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.offset.params` -> `draftutils.params`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/offset.py:46`.

### from draftutils import utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.offset.utils` -> `draftutils.utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/offset.py:47`.

## `draftfunctions.offset.offset`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def offset(obj, delta, copy=False, bind=False, sym=False, occ=False):
```

offset(object,delta,[copymode],[bind])

Offset the given wire by applying the given delta Vector to its first
vertex.

Parameters
----------
obj :

delta : Base.Vector or list of Base.Vector
    If offsetting a BSpline, the delta must not be a Vector but a list
    of Vectors, one for each node of the spline.

copy : bool
    If copymode is True, another object is created, otherwise the same
    object gets offsetted.

copy : bool
    If bind is True, and provided the wire is open, the original
    and the offset wires will be bound by their endpoints, forming a face.

sym : bool
    if sym is True, bind must be true too, and the offset is made on both
    sides, the total width being the given delta length.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/offset.py:50`. Decorators are copied as source expressions and have not been executed.

