# `WorkingPlane.Plane`

[Source module](index.md)

```python
class Plane(PlaneBase):
```

The old Plane class.

Parameters
----------
u: Base.Vector or WorkingPlane.Plane, optional
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

weak: bool, optional
    Defaults to `True`.
    If `True` the WP is in "Auto" mode and will adapt to the current view.

Note that the u, v and w vectors are not checked for validity.

Other attributes
----------------
stored: None/list
    Placeholder for a stored state.

Evidence: `src/Mod/Draft/WorkingPlane.py:723`. Source-defined class; runtime behavior and support status unverified.

## `WorkingPlane.Plane.__init__`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def __init__(self, u=Vector(1, 0, 0), v=Vector(0, 1, 0), w=Vector(0, 0, 1), pos=Vector(0, 0, 0), weak=True):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:759`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.Plane.copy`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def copy(self):
```

See PlaneBase.copy.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:776`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.Plane.offsetToPoint`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def offsetToPoint(self, point, direction=None):
```

Return the signed distance from a point to the plane. The direction
argument is ignored.

The returned value is the negative of the local Z coordinate of the point.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:782`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.Plane.projectPoint`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def projectPoint(self, point, direction=None, force_projection=True):
```

See PlaneBase.project_point.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:790`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.Plane.alignToPointAndAxis`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def alignToPointAndAxis(self, point, axis, offset=0, upvec=None):
```

See PlaneBase.align_to_point_and_axis.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:794`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.Plane.alignToPointAndAxis_SVG`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def alignToPointAndAxis_SVG(self, point, axis, offset=0):
```

See PlaneBase.align_to_point_and_axis_svg.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:802`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.Plane.alignToCurve`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def alignToCurve(self, shape, offset=0):
```

Align the WP to a curve. NOT IMPLEMENTED.

Parameters
----------
shape: Part.Shape
    Edge or Wire.
offset: float, optional
    Defaults to zero.
    Offset along the WP `axis`.

Returns
-------
`False`

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:808`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.Plane.alignToEdges`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def alignToEdges(self, shapes, offset=0):
```

Align the WP to edges with an optional offset.

The eges must define a plane.

The endpoints of the first edge defines the WP `position` and `u` axis.

Parameters
----------
shapes: iterable
    Two edges.
offset: float, optional
    Defaults to zero.
    Offset along the WP `axis`.

Returns
-------
`True`/`False`
    `True` if successful.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:825`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.Plane.alignToFace`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def alignToFace(self, shape, offset=0, parent=None):
```

Align the WP to a face with an optional offset.

The face must be planar.

The center of gravity of the face defines the WP `position` and the
normal of the face the WP `axis`. The WP `u` and `v` vectors are
determined by the draftgeoutils.geometry.uv_vectors_from_face function.
See there.

Parameters
----------
shape: Part.Face
    Face.
offset: float, optional
    Defaults to zero.
    Offset along the WP `axis`.
parent: object
    Defaults to `None`.
    The ParentGeoFeatureGroup of the object the face belongs to.

Returns
-------
`True`/`False`
    `True` if successful.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:850`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.Plane.alignTo3Points`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def alignTo3Points(self, p1, p2, p3, offset=0):
```

Align the plane to a temporary face created from three points.

Parameters
----------
p1: Base.Vector
    First point.
p2: Base.Vector
    Second point.
p3: Base.Vector
    Third point.
offset: float, optional
    Defaults to zero.
    Offset along the WP `axis`

Returns
-------
`True`/`False`
    `True` if successful.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:886`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.Plane.alignToSelection`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def alignToSelection(self, offset=0):
```

Align the plane to a selection with an optional offset.

The selection must define a plane.

Parameter
---------
offset: float, optional
    Defaults to zero.
    Offset along the WP `axis`

Returns
-------
`True`/`False`
    `True` if successful.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:910`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.Plane.setup`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def setup(self, direction=None, point=None, upvec=None, force=False):
```

Set up the working plane if it exists but is undefined.

If `direction` and `point` are present,
it calls `align_to_point_and_axis(point, direction, 0, upvec)`.

Otherwise, it gets the camera orientation to define
a working plane that is perpendicular to the current view,
centered at the origin, and with `v` pointing up on the screen.

This method only works when the `weak` attribute is `True`.
This method also sets `weak` to `True`.

This method only works when `FreeCAD.GuiUp` is `True`,
that is, when the graphical interface is loaded.
Otherwise it fails silently.

Parameters
----------
direction: Base.Vector, optional
    It defaults to `None`. It is the new `axis` of the plane.
point: Base.Vector, optional
    It defaults to `None`. It is the new `position` of the plane.
upvec: Base.Vector, optional
    It defaults to `None`. It is the new `v` orientation of the plane.
force: bool
    If True, it sets the plane even if the plane is not in weak mode

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:1018`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.Plane.reset`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def reset(self):
```

Reset the WP.

Sets the `weak` attribute to `True`.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:1064`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.Plane.setTop`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def setTop(self):
```

Set the WP to the top position and updates the GUI.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:1071`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.Plane.setFront`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def setFront(self):
```

Set the WP to the front position and updates the GUI.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:1083`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.Plane.setSide`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def setSide(self):
```

Set the WP to the left side position and updates the GUI.

Note that set_to_side from the parent class sets the WP to the right side position.
Which matches the Side option from Draft_SelectPlane.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:1095`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.Plane.getRotation`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getRotation(self):
```

Return a placement describing the WP orientation only.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:1114`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.Plane.getPlacement`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getPlacement(self, rotated=False):
```

Return a placement calculated from the WP. The rotated argument is ignored.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:1118`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.Plane.getNormal`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getNormal(self):
```

Return the normal vector (axis) of the WP.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:1122`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.Plane.setFromPlacement`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def setFromPlacement(self, place, rebase=False):
```

Align the WP to a placement.

Parameters
----------
place: Base.Placement
    Placement.
rebase: bool, optional
    Defaults to `False`.
    If `False` the `position` of the WP is not changed.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:1126`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.Plane.inverse`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def inverse(self):
```

Invert the direction of the plane.

It inverts the `u` and `axis` vectors.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:1142`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.Plane.save`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def save(self):
```

Store the plane attributes.

Store `u`, `v`, `axis`, `position` and `weak`
in a list in `stored`.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:1150`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.Plane.restore`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def restore(self):
```

Restore the plane attributes that were saved.

Restores the attributes `u`, `v`, `axis`, `position` and `weak`
from `stored`, and set `stored` to `None`.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:1158`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.Plane.getLocalCoords`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getLocalCoords(self, point):
```

Translate a point from the global coordinate system to
the local (WP) coordinate system.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:1168`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.Plane.getGlobalCoords`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getGlobalCoords(self, point):
```

Translate a point from the local (WP) coordinate system to
the global coordinate system.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:1174`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.Plane.getLocalRot`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getLocalRot(self, vec):
```

Translate a vector from the global coordinate system to
the local (WP) coordinate system.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:1180`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.Plane.getGlobalRot`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getGlobalRot(self, vec):
```

Translate a vector from the local (WP) coordinate system to
the global coordinate system.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:1186`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.Plane.getClosestAxis`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getClosestAxis(self, vec):
```

Return the closest WP axis to a vector.

Parameters
----------
vec: Base.Vector
    Vector.

Returns
-------
str
    `'x'`, `'y'` or `'z'`.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:1192`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.Plane.isGlobal`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def isGlobal(self):
```

Return `True` if the WP matches the global coordinate system.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:1207`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.Plane.isOrtho`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def isOrtho(self):
```

Return `True` if the WP axes are orthogonal to the global axes.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:1211`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.Plane.getDeviation`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getDeviation(self):
```

Return the angle between the u axis and the horizontal plane.

It defines a projection of `u` on the horizontal plane
(without a Z component), and then measures the angle between
this projection and `u`.

It also considers the cross product of the projection
and `u` to determine the sign of the angle.

Returns
-------
float
    Angle between the `u` vector, and a projected vector
    on the global horizontal plane.

See Also
--------
DraftVecUtils.angle

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:1215`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.Plane.getParameters`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getParameters(self):
```

Return a dictionary with the data which define the plane:
`u`, `v`, `axis`, `position`, `weak`.

Returns
-------
dict
    dictionary of the form:
    {"u":x, "v":v, "axis":axis, "position":position, "weak":weak}

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:1242`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.Plane.setFromParameters`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def setFromParameters(self, data):
```

Set the plane according to data.

Parameters
----------
data: dict
    dictionary of the form:
    {"u":x, "v":v, "axis":axis, "position":position, "weak":weak}

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:1254`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`WorkingPlane.Plane._get_prop_list`. These are source internals unless an explicit export establishes otherwise.

