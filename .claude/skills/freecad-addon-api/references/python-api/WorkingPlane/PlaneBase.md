# `WorkingPlane.PlaneBase`

[Source module](index.md)

```python
class PlaneBase:
```

PlaneBase is the base class for the Plane class and the PlaneGui class.

Parameters
----------
u: Base.Vector or WorkingPlane.PlaneBase, optional
    Defaults to Vector(1, 0, 0).
    If a WP is provided:
        A copy of the WP is created, all other parameters are then ignored.
    If a vector is provided:
        Unit vector for the `u` attribute (+X axis).

v: Base.Vector, optional
    Defaults to Vector(0, 1, 0).
    Unit vector for the `v` attribute (+Y axis).

w: Base.Vector, optional
    Defaults to Vector(0, 0, 1).
    Unit vector for the `axis` attribute (+Z axis).

pos: Base.Vector, optional
    Defaults to Vector(0, 0, 0).
    Vector for the `position` attribute (origin).

Note that the u, v and w vectors are not checked for validity.

Evidence: `src/Mod/Draft/WorkingPlane.py:62`. Source-defined class; runtime behavior and support status unverified.

## `WorkingPlane.PlaneBase.__init__`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def __init__(self, u=Vector(1, 0, 0), v=Vector(0, 1, 0), w=Vector(0, 0, 1), pos=Vector(0, 0, 0)):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:89`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneBase.copy`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def copy(self):
```

Return a new WP that is a copy of the present object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:109`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneBase.match`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def match(self, source, target=None):
```

Match the main properties of two working planes.

Parameters
----------
source: WP object
    WP to copy properties from.
target: WP object, optional
    Defaults to `None`.
    WP to copy properties to. If `None` the present object is used.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:119`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneBase.get_parameters`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_parameters(self):
```

Return a data dictionary with the main properties of the WP.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:135`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneBase.set_parameters`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def set_parameters(self, data):
```

Set the main properties of the WP according to a data dictionary.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:142`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneBase.align_to_3_points`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def align_to_3_points(self, p1, p2, p3, offset=0):
```

Align the WP to 3 points with an optional offset.

The points must define a plane.

Parameters
----------
p1: Base.Vector
    New WP `position`.
p2: Base.Vector
    Point on the +X axis. (p2 - p1) defines the WP `u` axis.
p3: Base.Vector
    Defines the plane.
offset: float, optional
    Defaults to zero.
    Offset along the WP `axis`.

Returns
-------
`True`/`False`
    `True` if successful.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:147`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneBase.align_to_edges_vertexes`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def align_to_edges_vertexes(self, shapes, offset=0):
```

Align the WP to the endpoints of edges and/or the points of vertexes
with an optional offset.

The points must define a plane.

The first 2 points define the WP `position` and `u` axis.

Parameters
----------
shapes: iterable
    One or more edges and/or vertexes.
offset: float, optional
    Defaults to zero.
    Offset along the WP `axis`.

Returns
-------
`True`/`False`
    `True` if successful.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:171`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneBase.align_to_edge_or_wire`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def align_to_edge_or_wire(self, shape, offset=0):
```

Align the WP to an edge or wire with an optional offset.

The shape must define a plane.

If the shape is an edge with a `Center` then that defines the WP
`position`. The vector between the center and its start point then
defines the WP `u` axis.

In other cases the start point of the first edge defines the WP
`position` and the 1st derivative at that point the WP `u` axis.

Parameters
----------
shape: Part.Edge or Part.Wire
    Edge or wire.
offset: float, optional
    Defaults to zero.
    Offset along the WP `axis`.

Returns
-------
`True`/`False`
    `True` if successful.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:197`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneBase.align_to_straight_edge`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def align_to_straight_edge(self, edge, offset=0):
```

Align the WP to a straight edge.

Used when a single straight edge is selected and does not define a
plane. The edge direction becomes the WP `u` axis. All three axes are
recomputed using XZY priority so the result is always a valid
orthonormal frame.

Parameters
----------
edge: Part.Edge
    A straight edge.
offset: float, optional
    Defaults to zero.
    Offset along the WP `axis`.

Returns
-------
`True`/`False`
    `True` if successful.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:247`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneBase.align_to_vertex`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def align_to_vertex(self, vertex, offset=0):
```

Move the WP origin to a vertex, keeping the current orientation.

Parameters
----------
vertex: Part.Vertex
    A vertex.
offset: float, optional
    Defaults to zero.
    Offset along the WP `axis`.

Returns
-------
`True`
    Always successful.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:277`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneBase.align_to_two_vertices`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def align_to_two_vertices(self, v1, v2, offset=0):
```

Align the WP to two vertices.

The direction from `v1` to `v2` defines the WP `u` axis. The `v` and
`axis` vectors are recomputed using XZY priority. The WP origin is set
to `v1`.

Parameters
----------
v1: Part.Vertex
    First vertex (WP origin).
v2: Part.Vertex
    Second vertex (defines u axis direction).
offset: float, optional
    Defaults to zero.
    Offset along the WP `axis`.

Returns
-------
`True`/`False`
    `True` if successful.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:296`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneBase.align_to_face`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def align_to_face(self, face, offset=0):
```

Align the WP to a face with an optional offset.

The face must be planar.

The center of gravity of the face defines the WP `position` and the
normal of the face the WP `axis`. The WP `u` and `v` vectors are
determined by the draftgeoutils.geometry.uv_vectors_from_face function.
See there.

Parameters
----------
face: Part.Face
    Face.
offset: float, optional
    Defaults to zero.
    Offset along the WP `axis`.

Returns
-------
`True`/`False`
    `True` if successful.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:328`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneBase.align_to_face_and_edge`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def align_to_face_and_edge(self, face, edge, offset=0):
```

Align the WP to a face and an edge.

The face must be planar.

The normal of the face defines the WP `axis`, the first vertex of the
edge its `position`, and its `u` vector is determined by the second
vertex of the edge.

Parameters
----------
face: Part.Face
    Face.
edge: Part.Edge
    Edge, need not be an edge of the face.
offset: float, optional
    Defaults to zero.
    Offset along the WP `axis`.

Returns
-------
`True`/`False`
    `True` if successful.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:358`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneBase.align_to_placement`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def align_to_placement(self, place, offset=0):
```

Align the WP to a placement with an optional offset.

Parameters
----------
place: Base.Placement
    Placement.
offset: float, optional
    Defaults to zero.
    Offset along the WP `axis`.

Returns
-------
`True`

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:389`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneBase.align_to_point_and_axis`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def align_to_point_and_axis(self, point, axis, offset=0, upvec=Vector(1, 0, 0)):
```

Align the WP to a point and an axis with an optional offset and an
optional up-vector.

If the axis and up-vector are parallel the FreeCAD.Rotation algorithm
will replace the up-vector: Vector(0, 0, 1) is tried first, then
Vector(0, 1, 0), and finally Vector(1, 0, 0).

Parameters
----------
point: Base.Vector
    New WP `position`.
axis: Base.Vector
    New WP `axis`.
offset: float, optional
    Defaults to zero.
    Offset along the WP `axis`.
upvec: Base.Vector, optional
    Defaults to Vector(1, 0, 0).
    Up-vector.

Returns
-------
`True`

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:408`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneBase.align_to_point_and_axis_svg`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def align_to_point_and_axis_svg(self, point, axis, offset=0):
```

Align the WP to a point and an axis with an optional offset.

It aligns `u` and `v` based on the magnitude of the components
of `axis`.

Parameters
----------
point: Base.Vector
    The new `position` of the plane, adjusted by
    the `offset`.
axis: Base.Vector
    A vector whose unit vector will be used as the new `axis`
    of the plane.
    The magnitudes of the `x`, `y`, `z` components of the axis
    determine the orientation of `u` and `v` of the plane.
offset: float, optional
    Defaults to zero. A value which will be used to offset
    the plane in the direction of its `axis`.

Returns
-------
`True`

Cases
-----
The `u` and `v` are always calculated the same

    * `u` is the cross product of the positive or negative of `axis`
      with a `reference vector`.
      ::
          u = [+1|-1] axis.cross(ref_vec)
    * `v` is `u` rotated 90 degrees around `axis`.

Whether the `axis` is positive or negative, and which reference
vector is used, depends on the absolute values of the `x`, `y`, `z`
components of the `axis` unit vector.

 #. If `x > y`, and `y > z`
     The reference vector is +Z
     ::
         u = -1 axis.cross(+Z)
 #. If `y > z`, and `z >= x`
     The reference vector is +X.
     ::
         u = -1 axis.cross(+X)
 #. If `y >= x`, and `x > z`
     The reference vector is +Z.
     ::
         u = +1 axis.cross(+Z)
 #. If `x > z`, and `z >= y`
     The reference vector is +Y.
     ::
         u = +1 axis.cross(+Y)
 #. If `z >= y`, and `y > x`
     The reference vector is +X.
     ::
         u = +1 axis.cross(+X)
 #. otherwise
     The reference vector is +Y.
     ::
         u = -1 axis.cross(+Y)

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:447`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneBase.align_to_rotation`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def align_to_rotation(self, rot):
```

Align the WP to a rotation.

Parameter
---------
rot: Base.Rotation
    Rotation.

Returns
-------
`True`

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:563`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneBase.get_global_coords`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_global_coords(self, point, as_vector=False):
```

Translate a point or vector from the local (WP) coordinate system to
the global coordinate system.

Parameters
----------
point: Base.Vector
    Point.
as_vector: bool, optional
    Defaults to `False`.
    If `True` treat point as a vector.

Returns
-------
Base.Vector

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:578`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneBase.get_local_coords`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_local_coords(self, point, as_vector=False):
```

Translate a point or vector from the global coordinate system to
the local (WP) coordinate system.

Parameters
----------
point: Base.Vector
    Point.
as_vector: bool, optional
    Defaults to `False`.
    If `True` treat point as a vector.

Returns
-------
Base.Vector

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:598`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneBase.get_closest_axis`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_closest_axis(self, vec):
```

Return a string indicating the positive or negative WP axis closest
to a vector.

Parameters
----------
vec: Base.Vector
    Vector.

Returns
-------
str
    `"x"`, `"y"` or `"z"`.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:618`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneBase.get_placement`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_placement(self):
```

Return a placement calculated from the WP.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:641`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneBase.is_global`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def is_global(self):
```

Return `True` if the WP matches the global coordinate system exactly.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:645`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneBase.is_ortho`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def is_ortho(self):
```

Return `True` if all WP axes are  parallel to a global axis.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:654`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneBase.project_point`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def project_point(self, point, direction=None, force_projection=True):
```

Project a point onto the WP and return the global coordinates of the
projected point.

Parameters
----------
point: Base.Vector
    Point to project.
direction: Base.Vector, optional
    Defaults to `None` in which case the WP `axis` is used.
    Direction of projection.
force_projection: bool, optional
    Defaults to `True`.
    See draftgeoutils.geometry.project_point_on_plane

Returns
-------
Base.Vector

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:660`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneBase.set_to_top`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def set_to_top(self, offset=0):
```

Set the WP to the top position with an optional offset.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:683`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneBase.set_to_front`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def set_to_front(self, offset=0):
```

Set the WP to the front position with an optional offset.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:690`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneBase.set_to_side`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def set_to_side(self, offset=0):
```

Set the WP to the right side position with an optional offset.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:697`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`WorkingPlane.PlaneBase.__repr__`, `WorkingPlane.PlaneBase._copy_value`, `WorkingPlane.PlaneBase._axes_from_rotation`, `WorkingPlane.PlaneBase._axes_from_view_rotation`, `WorkingPlane.PlaneBase._get_prop_list`. These are source internals unless an explicit export establishes otherwise.

