# Python source module `draftgeoutils.wires`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftgeoutils/wires.py`. Import path is source-routed; installed availability is unverified.

Provides various functions to work with wires.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import math

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.wires.math` -> `math`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/wires.py:32`.

### import lazy_loader.lazy_loader as lz

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.wires.lz` -> `lazy_loader.lazy_loader`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/wires.py:33`.

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.wires.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/wires.py:35`.

### import DraftVecUtils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.wires.DraftVecUtils` -> `DraftVecUtils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/wires.py:36`.

### import WorkingPlane

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.wires.WorkingPlane` -> `WorkingPlane`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/wires.py:37`.

### from draftgeoutils.general import geomType, vec, precision

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.wires.geomType` -> `draftgeoutils.general.geomType`.

Bound source name `draftgeoutils.wires.vec` -> `draftgeoutils.general.vec`.

Bound source name `draftgeoutils.wires.precision` -> `draftgeoutils.general.precision`.

[Source module `draftgeoutils.general`](../general/index.md).

Evidence: `src/Mod/Draft/draftgeoutils/wires.py:39`.

### from draftgeoutils.geometry import get_normal

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.wires.get_normal` -> `draftgeoutils.geometry.get_normal`.

[Source module `draftgeoutils.geometry`](../geometry/index.md).

Evidence: `src/Mod/Draft/draftgeoutils/wires.py:40`.

### from draftgeoutils.geometry import project_point_on_plane

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.wires.project_point_on_plane` -> `draftgeoutils.geometry.project_point_on_plane`.

[Source module `draftgeoutils.geometry`](../geometry/index.md).

Evidence: `src/Mod/Draft/draftgeoutils/wires.py:41`.

### from draftgeoutils.edges import findMidpoint, isLine

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.wires.findMidpoint` -> `draftgeoutils.edges.findMidpoint`.

Bound source name `draftgeoutils.wires.isLine` -> `draftgeoutils.edges.isLine`.

[Source module `draftgeoutils.edges`](../edges/index.md).

Evidence: `src/Mod/Draft/draftgeoutils/wires.py:42`.

## `draftgeoutils.wires.findWires`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def findWires(edgeslist):
```

Find wires in a list of edges.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/wires.py:51`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.wires.findWiresOld2`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def findWiresOld2(edgeslist):
```

Find connected wires in the given list of edges.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/wires.py:56`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.wires.findWiresOld`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def findWiresOld(edges):
```

Return a list of lists containing edges that can be connected.

Find connected edges in the list.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/wires.py:116`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.wires.flattenWire`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def flattenWire(wire, origin=None, normal=None):
```

Force a wire to be flat on a plane defined by an origin and a normal.

If origin or normal are None they are derived from the wire.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/wires.py:158`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.wires.superWire`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def superWire(edgeslist, closed=False):
```

Force a wire between edges that don't have coincident endpoints.

Forces a wire between edges that don't necessarily
have coincident endpoints. If closed=True, the wire will always be closed.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/wires.py:179`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.wires.isReallyClosed`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def isReallyClosed(wire):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/wires.py:246`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.wires.curvetowire`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def curvetowire(obj, steps):
```

Discretize the object and return a list of edges.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/wires.py:252`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.wires.curvetosegment`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def curvetosegment(curve, seglen):
```

Discretize the curve and return a list of edges.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/wires.py:264`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.wires.rebaseWire`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def rebaseWire(wire, vidx=0):
```

Return a copy of the wire with the first vertex indicated by the index.

Return a new wire which is a copy of the current wire,
but where the first vertex is the vertex indicated by the given
index vidx, starting from 1.
0 will return an exact copy of the wire.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/wires.py:276`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.wires.removeInterVertices`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def removeInterVertices(wire):
```

Remove middle vertices from a straight wire and return a new wire.

Remove unneeded vertices, those that are in the middle of a straight line,
from a wire, return a new wire.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/wires.py:295`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.wires.cleanProjection`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def cleanProjection(shape, tessellate=True, seglength=0.05):
```

Return a compound of edges, optionally tessellate ellipses, splines
and bezcurves.

The function was formerly used to workaround bugs in the projection
algorithm. These bugs have since been fixed. Now the function is only
used when tessellation of ellipses, splines and bezcurves is required
(DXF output and Draft_Shape2DView).

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/wires.py:327`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.wires.tessellateProjection`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def tessellateProjection(shape, seglen):
```

Return projection with BSplines and Ellipses broken into line segments.

Useful for exporting projected views to DXF files.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/wires.py:364`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.wires.get_placement_perpendicular_to_wire`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_placement_perpendicular_to_wire(wire):
```

Return the placement whose base is the wire's first vertex and it's z axis aligned to the wire's tangent.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/wires.py:389`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.wires.get_extended_wire`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_extended_wire(wire, offset_start, offset_end):
```

Return a wire trimmed (negative offset) or extended (positive offset) at its first vertex, last vertex or both ends.

get_extended_wire(wire, -100.0, 0.0) -> returns a copy of the wire with its first 100 mm removed
get_extended_wire(wire, 0.0, 100.0) -> returns a copy of the wire extended by 100 mm after it's last vertex

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/wires.py:407`. Decorators are copied as source expressions and have not been executed.

