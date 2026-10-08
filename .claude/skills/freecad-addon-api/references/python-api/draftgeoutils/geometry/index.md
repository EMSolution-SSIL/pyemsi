# Python source module `draftgeoutils.geometry`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftgeoutils/geometry.py`. Import path is source-routed; installed availability is unverified.

Provides various functions for general geometrical calculations.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import math

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.geometry.math` -> `math`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/geometry.py:32`.

### import lazy_loader.lazy_loader as lz

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.geometry.lz` -> `lazy_loader.lazy_loader`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/geometry.py:33`.

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.geometry.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/geometry.py:35`.

### import DraftVecUtils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.geometry.DraftVecUtils` -> `DraftVecUtils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/geometry.py:36`.

### import draftutils.gui_utils as gui_utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.geometry.gui_utils` -> `draftutils.gui_utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/geometry.py:38`.

### from draftgeoutils.general import geomType, vec

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.geometry.geomType` -> `draftgeoutils.general.geomType`.

Bound source name `draftgeoutils.geometry.vec` -> `draftgeoutils.general.vec`.

[Source module `draftgeoutils.general`](../general/index.md).

Evidence: `src/Mod/Draft/draftgeoutils/geometry.py:40`.

## `draftgeoutils.geometry.findPerpendicular`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def findPerpendicular(point, edgeslist, force=None):
```

Find the perpendicular distance between a point and a list of edges.

If force is specified, only the edge[force] will be considered,
and it will be considered infinite.

Returns
-------
[vector_from_point_to_closest_edge, edge_index]
    The vector and the index in the list.

None
    If no perpendicular vector could be found.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/geometry.py:49`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.geometry.findDistance`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def findDistance(point, edge, strict=False):
```

Return a vector from the point to its closest point on the edge.

If `strict` is `True`, the vector will be returned
only if its endpoint lies on the `edge`.
Edge can also be a list of 2 points.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/geometry.py:91`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.geometry.get_spline_normal`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_spline_normal(edge, tol=-1):
```

Find the normal of a BSpline edge.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/geometry.py:204`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.geometry.get_shape_normal`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_shape_normal(shape):
```

Find the normal of a shape or list of points or colinear edges, if possible.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/geometry.py:221`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.geometry.get_normal`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_normal(shape, tol=-1):
```

Find the normal of a shape or list of points, if possible.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/geometry.py:284`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.geometry.getRotation`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getRotation(v1, v2=App.Vector(0, 0, 1)):
```

Get the rotation Quaternion between 2 vectors.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/geometry.py:327`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.geometry.is_planar`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def is_planar(shape, tol=-1):
```

Return True if the given shape or list of points is planar.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/geometry.py:340`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.geometry.is_straight_line`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def is_straight_line(shape, tol=-1):
```

Return True if shape is a straight line.
function used in other methods because Part.Shape.findPlane assign a
plane and normal to straight wires creating privileged directions
and to deal with straight wires with overlapped edges.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/geometry.py:376`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.geometry.are_coplanar`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def are_coplanar(shape_a, shape_b, tol=-1):
```

Return True if exist a plane containing both shapes.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/geometry.py:435`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.geometry.get_spline_surface_normal`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_spline_surface_normal(shape, tol=-1):
```

Check if shape formed by BSpline surfaces is planar and get normal.
If shape is not planar return None.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/geometry.py:495`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.geometry.find_plane`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def find_plane(shape, tol=-1):
```

Find the plane containing the shape if possible.
Use this function as a workaround due Part.Shape.findPlane
fail to find plane on BSpline surfaces.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/geometry.py:538`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.geometry.calculatePlacement`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def calculatePlacement(shape):
```

Return a placement located in the center of gravity of the shape.

If the given shape is planar, return a placement located at the center
of gravity of the shape, and oriented towards the shape's normal.
Otherwise, it returns a null placement.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/geometry.py:567`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.geometry.mirror`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def mirror(point, edge):
```

Find mirror point relative to an edge.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/geometry.py:592`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.geometry.mirror_matrix`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def mirror_matrix(mtx, pos, nor):
```

Return a mirrored copy of a matrix.

Parameters
----------
mtx: Base::Matrix
    Matrix.
pos: Base::Vector3
    Point on mirror plane.
nor: Base::Vector3
    Normal of mirror plane.

Returns
-------
Base::Matrix

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/geometry.py:605`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.geometry.uv_vectors_from_face`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def uv_vectors_from_face(face, vec_z=App.Vector(0, 0, 1), tol=-1):
```

Return the u and v vectors of a planar face.

It is up to the calling function to ensure the face is planar.

If the u vector matches +/-vec_z, or the v vector matches -vec_z, the
vectors are rotated to ensure the v vector matches +vec_z.

Parameters
----------
face: Part.Face
    Face.
vec_z: Base::Vector3, optional
    Defaults to Vector(0, 0, 1).
    Z axis vector used for reference.
    Is replaced by Vector(0, 0, 1) if it matches the +/-normal of the face.
tol: float, optional
    Defaults to -1.
    Internal tolerance. 1e-7 is used if tol <=0.

Returns
-------
tuple
    U and v vector (Base::Vector3).

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/geometry.py:631`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.geometry.placement_from_face`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def placement_from_face(face, vec_z=App.Vector(0, 0, 1), rotated=False, tol=-1):
```

Return a placement from the center of gravity, and the u and v vectors of a planar face.

It is up to the calling function to ensure the face is planar.

Parameters
----------
face: Part.Face
    Face.
vec_z: Base::Vector3, optional
    Defaults to Vector(0, 0, 1).
    Z axis vector used for reference.
    Is replaced by Vector(0, 0, 1) if it matches the +/-normal of the face.
rotated: bool, optional
    Defaults to `False`.
    If `False` the v vector of the face defines the Y axis of the placement.
    If `True` the -v vector of the face defines the Z axis of the placement
    (used by Arch_Window).
    The u vector defines the X axis in both cases.
tol: float, optional
    Defaults to -1.
    Internal tolerance. 1e-7 is used if tol <=0.

Returns
-------
Base::Placement

See also
--------
DraftGeomUtils.uv_vectors_from_face

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/geometry.py:673`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.geometry.placement_from_points`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def placement_from_points(pt_pos, pt_x, pt_y, as_vectors=False, tol=-1):
```

Return a placement from 3 points defining an origin, an X axis and a Y axis.

If the vectors calculated from the arguments are too short or parallel,
the returned placement will have a default rotation.

Parameters
----------
pt_pos: Base::Vector3
    Origin (Base of Placement).
pt_x: Base::Vector3
    Point on positive X axis. Or X axis vector if as_vectors is `True`.
pt_y: Base::Vector3
    Point on positive Y axis. Or Y axis vector if as_vectors is `True`.
as_vectors: bool, optional
    Defaults to `False`.
    If `True` treat pt_x and pt_y as axis vectors.
tol: float, optional
    Defaults to -1.
    Internal tolerance. 1e-7 is used if tol <=0.

Returns
-------
Base::Placement

See also
--------
DraftGeomUtils.getRotation
DraftVecUtils.getRotation

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/geometry.py:712`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.geometry.distance_to_plane`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def distance_to_plane(point, base, normal):
```

Return the signed distance from a plane to a point.

The distance is positive if the point lies on the +normal side of the plane.

Parameters
----------
point: Base::Vector3
    Point to project.
base: Base::Vector3
    Point on plane.
normal: Base::Vector3
    Normal of plane.

Returns
-------
float

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/geometry.py:765`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.geometry.project_point_on_plane`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def project_point_on_plane(point, base, normal, direction=None, force_projection=False, tol=-1):
```

Project a point onto a plane.

Parameters
----------
point: Base::Vector3
    Point to project.
base: Base::Vector3
    Point on plane.
normal: Base::Vector3
    Normal of plane.
direction: Base::Vector3, optional
    Defaults to `None` in which case the normal is used.
    Direction of projection.
force_projection: Bool, optional
    Defaults to `False`.
    If `True` forces the projection if the deviation between the direction
    and the normal is less than tol from the orthogonality. The direction
    of projection is then modified to a tol deviation between the direction
    and the orthogonal.
tol: float, optional
    Defaults to -1.
    Internal tolerance. 1e-7 is used if tol <=0.

Returns
-------
Base::Vector3 or `None`

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/geometry.py:788`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.geometry.getSplineNormal`

Status: source-defined name; no independently verified stability/export guarantee.

```python
getSplineNormal = get_spline_normal
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/Draft/draftgeoutils/geometry.py:838`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.geometry.getNormal`

Status: source-defined name; no independently verified stability/export guarantee.

```python
getNormal = get_normal
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/Draft/draftgeoutils/geometry.py:840`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.geometry.isPlanar`

Status: source-defined name; no independently verified stability/export guarantee.

```python
isPlanar = is_planar
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/Draft/draftgeoutils/geometry.py:842`. Decorators are copied as source expressions and have not been executed.

