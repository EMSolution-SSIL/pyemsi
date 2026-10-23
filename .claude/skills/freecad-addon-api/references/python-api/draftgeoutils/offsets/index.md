# Python source module `draftgeoutils.offsets`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftgeoutils/offsets.py`. Import path is source-routed; installed availability is unverified.

Provides various functions to work with offsets.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import lazy_loader.lazy_loader as lz

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.offsets.lz` -> `lazy_loader.lazy_loader`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/offsets.py:32`.

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.offsets.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/offsets.py:34`.

### import DraftVecUtils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.offsets.DraftVecUtils` -> `DraftVecUtils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/offsets.py:35`.

### from draftgeoutils.general import geomType, vec

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.offsets.geomType` -> `draftgeoutils.general.geomType`.

Bound source name `draftgeoutils.offsets.vec` -> `draftgeoutils.general.vec`.

[Source module `draftgeoutils.general`](../general/index.md).

Evidence: `src/Mod/Draft/draftgeoutils/offsets.py:37`.

### from draftgeoutils.geometry import get_normal

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.offsets.get_normal` -> `draftgeoutils.geometry.get_normal`.

[Source module `draftgeoutils.geometry`](../geometry/index.md).

Evidence: `src/Mod/Draft/draftgeoutils/offsets.py:38`.

### from draftgeoutils.wires import isReallyClosed

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.offsets.isReallyClosed` -> `draftgeoutils.wires.isReallyClosed`.

[Source module `draftgeoutils.wires`](../wires/index.md).

Evidence: `src/Mod/Draft/draftgeoutils/offsets.py:39`.

### from draftgeoutils.intersections import wiresIntersect, connect

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.offsets.wiresIntersect` -> `draftgeoutils.intersections.wiresIntersect`.

Bound source name `draftgeoutils.offsets.connect` -> `draftgeoutils.intersections.connect`.

[Source module `draftgeoutils.intersections`](../intersections/index.md).

Evidence: `src/Mod/Draft/draftgeoutils/offsets.py:40`.

## `draftgeoutils.offsets.pocket2d`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def pocket2d(shape, offset):
```

Return a list of wires obtained from offsetting wires from the shape.

Return a list of wires obtained from offsetting the wires
from the given shape by the given offset, and intersection if needed.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/offsets.py:49`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.offsets.offset`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def offset(edge, vector, trim=False):
```

Return a copy of the edge at a certain vector offset.

If the edge is an arc, the vector will be added at its first point
and a complete circle will be returned.

None if there is a problem.

Parameters
----------
edge: Part.Shape
    the edge to offset
vector: Base::Vector3
    the vector by which the edge is to be offset
trim: bool, optional
    If `edge` is an arc and `trim` is `True`, the resulting
    arc will be trimmed to the proper angle

Returns
-------
Part.Shape
    The offset shape

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/offsets.py:134`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.offsets.offsetWire`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def offsetWire(wire, dvec, bind=False, occ=False, widthList=None, offsetMode=None, alignList=[], normal=None, basewireOffset=0, wireNedge=False):
```

Offset the wire along the given vector.

Parameters
----------
wire as a sorted list of edges (the list is used directly), or as a
wire or a face (Draft Wire with MakeFace True or False supported).

The vector will be applied at the first vertex of the wire. If bind
is True (and the shape is open), the original wire and the offsetted one
are bound by 2 edges, forming a face.

If widthList is provided (values only, not lengths - i.e. no unit),
each value will be used to offset each corresponding edge in the wire.

The 1st value overrides 'dvec' for 1st segment of wire;
if a value is zero, value of 'widthList[0]' will follow;
if widthList[0]' == 0, but dvec still provided, dvec will be followed

offsetMode="BasewireMode" or None

If alignList is provided,
each value will be used to offset each corresponding edge
in the wire with corresponding index.

'basewireOffset' corresponds to 'offset' in ArchWall which offset
the basewire before creating the wall outline; or
it can be a list, e.g. corresponds to 'overrideOffset' in ArchWall, so
offset can be 'per segment' of wire, or 'per wall segment' in ArchWall

OffsetWire() is now aware of width and align per edge
Primarily for use with ArchWall based on Sketch object

To Do
-----
`dvec` vector to offset is now derived (and can be ignored)
in this function if widthList and alignList are provided
- 'dvec' to be obsolete in future?

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/offsets.py:185`. Decorators are copied as source expressions and have not been executed.

