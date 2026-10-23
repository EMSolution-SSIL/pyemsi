# `WorkingPlane.PlaneGui`

[Source module](index.md)

```python
class PlaneGui(PlaneBase):
```

The PlaneGui class.
The class handles several GUI related aspects of the WP including a history.

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

auto: bool, optional
    Defaults to `True`.
    If `True` the WP is in "Auto" mode and will adapt to the current view.

icon: str, optional
    Defaults to ":/icons/view-axonometric.svg".
    Path to the icon for the draftToolBar.

label: str, optional
    Defaults to "Auto".
    Label for the draftToolBar.

tip: str, optional
    Defaults to "Current working plane: Auto".
    Tooltip for the draftToolBar.

Note that the u, v and w vectors are not checked for validity.

Other attributes
----------------
_view: Gui::View3DInventor
    Reference to a 3D view.

_stored: dict
    Dictionary for a temporary stored state.

_history: dict
    Dictionary that holds up to 10 stored states.

Evidence: `src/Mod/Draft/WorkingPlane.py:1272`. Source-defined class; runtime behavior and support status unverified.

## `WorkingPlane.PlaneGui.__init__`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def __init__(self, u=Vector(1, 0, 0), v=Vector(0, 1, 0), w=Vector(0, 0, 1), pos=Vector(0, 0, 0), auto=True, icon=':/icons/view-axonometric.svg', label=QT_TRANSLATE_NOOP('draft', 'Auto'), tip=QT_TRANSLATE_NOOP('draft', 'Current working plane: Auto')):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:1327`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneGui.copy`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def copy(self):
```

Return a new plane that is a copy of the present object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:1351`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneGui.align_to_selection`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def align_to_selection(self, offset=0, _hist_add=True):
```

Align the WP to a selection with an optional offset.

For a single face the WP is aligned to that face. For a single curved
edge or wire the WP is aligned to the plane of that shape. For a
single straight edge the WP u-axis is aligned along the edge while the
WP axis (normal) is preserved. For a single vertex the WP origin is
moved to that point while the orientation is preserved. For two
vertices the direction from the first to the second defines the WP
u-axis; selection order matters.

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

Evidence: `src/Mod/Draft/WorkingPlane.py:1368`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneGui.align_to_3_points`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def align_to_3_points(self, p1, p2, p3, offset=0, _hist_add=True):
```

See PlaneBase.align_to_3_points.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:1466`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneGui.align_to_edges_vertexes`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def align_to_edges_vertexes(self, shapes, offset=0, _hist_add=True):
```

See PlaneBase.align_to_edges_vertexes.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:1473`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneGui.align_to_edge_or_wire`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def align_to_edge_or_wire(self, shape, offset=0, _hist_add=True):
```

See PlaneBase.align_to_edge_or_wire.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:1480`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneGui.align_to_straight_edge`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def align_to_straight_edge(self, edge, offset=0, _hist_add=True):
```

See PlaneBase.align_to_straight_edge.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:1487`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneGui.align_to_vertex`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def align_to_vertex(self, vertex, offset=0, _hist_add=True):
```

See PlaneBase.align_to_vertex.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:1494`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneGui.align_to_two_vertices`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def align_to_two_vertices(self, v1, v2, offset=0, _hist_add=True):
```

See PlaneBase.align_to_two_vertices.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:1500`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneGui.align_to_face`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def align_to_face(self, face, offset=0, _hist_add=True):
```

See PlaneBase.align_to_face.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:1507`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneGui.align_to_face_and_edge`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def align_to_face_and_edge(self, face, edge, offset=0, _hist_add=True):
```

See PlaneBase.align_to_face.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:1514`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneGui.align_to_placement`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def align_to_placement(self, place, offset=0, _hist_add=True):
```

See PlaneBase.align_to_placement.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:1521`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneGui.align_to_point_and_axis`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def align_to_point_and_axis(self, point, axis, offset=0, upvec=Vector(1, 0, 0), _hist_add=True):
```

See PlaneBase.align_to_point_and_axis.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:1527`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneGui.align_to_obj_placement`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def align_to_obj_placement(self, obj, offset=0, place=None, _hist_add=True):
```

Align the WP to an object placement with an optional offset.

Parameters
----------
obj: App::DocumentObject
    Object to derive the Placement (if place is `None`), the icon and
    the label from.
offset: float, optional
    Defaults to zero.
    Offset along the WP `axis`.
place: Base.Placement, optional
    Defaults to `None`.
    If `None` the Placement from obj is used.
    Argument to be used if obj is inside a container.

Returns
-------
`True`/`False`
    `True` if successful.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:1534`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneGui.align_to_wp_proxy`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def align_to_wp_proxy(self, obj, offset=0, place=None, _hist_add=True):
```

Align the WP to a WPProxy with an optional offset.

See align_to_obj_placement.

Also handles several WPProxy related features.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:1577`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneGui.auto_align`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def auto_align(self):
```

Align the WP to the current view if self.auto is True.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:1641`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneGui.set_to_default`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def set_to_default(self):
```

Set the WP to the default from the preferences.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:1652`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneGui.set_to_auto`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def set_to_auto(self):
```

Set the WP to auto.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:1664`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneGui.set_to_top`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def set_to_top(self, offset=0, center_on_view=False):
```

Set the WP to the top position with an optional offset.

Parameters
----------
offset: float, optional
    Defaults to zero.
    Offset along the WP `axis`.
center_on_view: bool, optional
    Defaults to `False`.
    If `True` the WP `position` is moved along the (offset) WP to the
    center of the view

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:1673`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneGui.set_to_front`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def set_to_front(self, offset=0, center_on_view=False):
```

Set the WP to the front position with an optional offset.

Parameters
----------
offset: float, optional
    Defaults to zero.
    Offset along the WP `axis`.
center_on_view: bool, optional
    Defaults to `False`.
    If `True` the WP `position` is moved along the (offset) WP to the
    center of the view

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:1695`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneGui.set_to_side`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def set_to_side(self, offset=0, center_on_view=False):
```

Set the WP to the right side position with an optional offset.

Parameters
----------
offset: float, optional
    Defaults to zero.
    Offset along the WP `axis`.
center_on_view: bool, optional
    Defaults to `False`.
    If `True` the WP `position` is moved along the (offset) WP to the
    center of the view

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:1717`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneGui.set_to_view`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def set_to_view(self, offset=0, center_on_view=False):
```

Align the WP to the view with an optional offset.

Parameters
----------
offset: float, optional
    Defaults to zero.
    Offset along the WP `axis`.
center_on_view: bool, optional
    Defaults to `False`.
    If `True` the WP `position` is moved along the (offset) WP to the
    center of the view

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:1739`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneGui.set_to_position`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def set_to_position(self, pos):
```

Set the `position` of the WP.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:1768`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneGui.center_on_view`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def center_on_view(self):
```

Move the WP `position` along the WP to the center of the view.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:1776`. Decorators are copied as source expressions and have not been executed.

## `WorkingPlane.PlaneGui.align_view`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def align_view(self):
```

Align the view to the WP.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/WorkingPlane.py:1798`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`WorkingPlane.PlaneGui._save`, `WorkingPlane.PlaneGui._restore`, `WorkingPlane.PlaneGui._handle_custom`, `WorkingPlane.PlaneGui._center_on_view`, `WorkingPlane.PlaneGui._previous`, `WorkingPlane.PlaneGui._next`, `WorkingPlane.PlaneGui._has_previous`, `WorkingPlane.PlaneGui._has_next`, `WorkingPlane.PlaneGui._get_prop_list`, `WorkingPlane.PlaneGui._get_label`, `WorkingPlane.PlaneGui._get_tip`, `WorkingPlane.PlaneGui._format_coord`, `WorkingPlane.PlaneGui._format_vector`, `WorkingPlane.PlaneGui._update_all`, `WorkingPlane.PlaneGui._update_history`, `WorkingPlane.PlaneGui._update_old_plane`, `WorkingPlane.PlaneGui._update_grid`, `WorkingPlane.PlaneGui._update_gui`. These are source internals unless an explicit export establishes otherwise.

