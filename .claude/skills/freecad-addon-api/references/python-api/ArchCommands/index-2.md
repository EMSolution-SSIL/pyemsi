# Python source module `ArchCommands`

[Python catalogue](../index.md)

Evidence: `src/Mod/BIM/ArchCommands.py`. Import path is source-routed; installed availability is unverified.

Literal `__all__`: not available; source names do not imply supported public API.

[part 1](index.md) | [part 2](index-2.md)

## `ArchCommands.getExtrusionData`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getExtrusionData(shape, sortmethod='area'):
```

If a shape has been extruded, returns the base face, and extrusion vector.

Determines if a shape appears to have been extruded from some base face, and
extruded at the normal from that base face. IE: it looks like a cuboid.
https://en.wikipedia.org/wiki/Cuboid#Rectangular_cuboid

If this is the case, returns what appears to be the base face, and the vector
used to make that extrusion.

The base face is determined based on the sortmethod parameter, which can either
be:

"area" = Of the faces with the smallest area, the one with the lowest z coordinate.
"z" = The face with the lowest z coordinate.
a 3D vector = the face which center is closest to the given 3D point

Parameters
----------
shape: <Part.Shape>
    Shape to examine.
sortmethod: {"area", "z"}
    Which sorting algorithm to use to determine the base face.

Returns
-------
Extrusion data: list
    Two item list containing the base face, and the vector used to create the
    extrusion. In that order.
Failure: None
    Returns None if the object does not appear to be an extrusion.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchCommands.py:1610`. Decorators are copied as source expressions and have not been executed.

## `ArchCommands.printMessage`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def printMessage(message):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchCommands.py:1704`. Decorators are copied as source expressions and have not been executed.

## `ArchCommands.printWarning`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def printWarning(message):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchCommands.py:1710`. Decorators are copied as source expressions and have not been executed.

## `ArchCommands.makeIfcSpreadsheet`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeIfcSpreadsheet(archobj=None):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchCommands.py:1716`. Decorators are copied as source expressions and have not been executed.

## `ArchCommands.override_link_properties`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def override_link_properties(link_obj, prop_names):
```

Injects local properties into a Link object to 'shadow' its source's properties.

By creating a local property, the Link can then to hold instance-specific data (like a Window's
'Hosts' list) without modifying the source and without triggering the heavy CopyOnChange
deep-copy mechanism of App::Link.

This function must be called before the Link's first recompute, which is when the core merges
the source's properties into the Link. This is typically achieved by calling it from within the
`appLinkExecute` method of the source object, or by forcefully calling it via
`ensure_link_overrides` if the user interacts with an unrecomputed Link.

See: https://wiki.freecad.org/Std_LinkMake#Copy_on_Change

Parameters
----------
link_obj : <App::DocumentObject>
    The newly created Link object (`App::Link`) that will receive the overridden properties.
prop_names : list of str
    A list of property names (e.g., `["Hosts"]`) to extract from the source object and
    recreate locally on the Link object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchCommands.py:1752`. Decorators are copied as source expressions and have not been executed.

## `ArchCommands.ensure_link_overrides`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def ensure_link_overrides(obj):
```

Ensures that a Link object has its required override properties set up. This acts as a safeguard
if a user modifies a Link before it has been recomputed for the first time (which normally
triggers appLinkExecute).

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchCommands.py:1806`. Decorators are copied as source expressions and have not been executed.

## `ArchCommands.resolve_pd_object`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def resolve_pd_object(obj):
```

Normalizes a PartDesign feature selection to its parent Body.

Selections and links on a PartDesign feature (e.g. a Pad or Pocket) point to the feature, not
its Body. Returns the parent Body if ``obj`` belongs to one, otherwise ``obj`` itself.

Parameters
----------
obj : App::DocumentObject
    The selected object to normalize.

Returns
-------
App::DocumentObject
    The parent PartDesign::Body if ``obj`` is a member of one, otherwise ``obj`` unchanged.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchCommands.py:1819`. Decorators are copied as source expressions and have not been executed.

## `ArchCommands.pickMainFaceName`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def pickMainFaceName(shape, view_vector=None):
```

Returns the name of the best candidate planar face (e.g. ``"Face1"``) for a given shape.

Filters the shape's faces down to the largest planar ones (within 5% of the largest face's area)
and, if a view direction is supplied, picks the one most opposed to it.

Parameters
----------
shape : Part.Shape or App::DocumentObject
    The shape to scan. If a document object is passed, its ``Shape`` attribute is used.
view_vector : FreeCAD.Vector, optional
    A camera view direction, as an interactive face selection aid. When given, the returned face
    is the one whose normal most directly opposes this vector. That is, the one facing the
    camera.

Returns
-------
str or None
    The face name (e.g. ``"Face1"``), or ``None`` if the shape has no planar faces.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchCommands.py:1842`. Decorators are copied as source expressions and have not been executed.

## `ArchCommands.resolveFace`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def resolveFace(face_ref, subname=None):
```

Resolves a face reference to a planar ``Part.Face``.

Accepts either a plain document object or a ``(object, [subname])`` tuple as produced by a
``LinkSub`` property. Resolution order: named sub-element, bare face shape, main
face of a solid, face built from closed wires.

Parameters
----------
face_ref : App::DocumentObject or tuple
    The reference to resolve. Either a plain document object or a ``(object, [subname])``
    ``LinkSub`` tuple. If the tuple's sub-element list contains more than one name, only
    the first is used; the remainder are ignored with a warning.
subname : str, optional
    Name of the sub-element to extract (e.g. ``"Face3"``). Ignored if ``face_ref`` is a
    tuple, in which case the subname is taken from the tuple instead.

Returns
-------
Part.Face or None
    The resolved planar face, or ``None`` if no planar face could be determined.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchCommands.py:1898`. Decorators are copied as source expressions and have not been executed.

## `ArchCommands.getFaceFrame`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getFaceFrame(face, reference_direction=None):
```

Given a planar face, creates a stable frame (U, V, Normal) anchored at the face's center.

Stable in this context means that one same face always produces the same axes, regardless of how
it was constructed. The goal is to avoid unexpected flips or rotations when editing the source
geometry.

Parameters
----------
face : Part.Face
    The face whose local frame is required.
reference_direction : FreeCAD.Vector or None
    A previously stored U direction. When provided, U is aligned with it instead of being
    derived from the face geometry. Falls back to the longest-edge heuristic if the reference
    is parallel to the face normal.

Returns
-------
tuple[FreeCAD.Vector, FreeCAD.Vector, FreeCAD.Vector, FreeCAD.Vector]
    ``(u_vec, v_vec, normal, center_point)``. The U and V tangents and the face normal are unit
    vectors, and the face center is a world-space position.

Notes
-----
Without a ``reference_direction``, U is derived from the longest edge of the face's outer
boundary, so the tiling grid aligns with the substrate geometry rather than world axes (e.g.
a rectangular slab gets a grid parallel to its long side).

When a ``reference_direction`` is supplied (typically from a stored property), it is projected
onto the face plane to remove any normal component. This keeps U stable across recomputes even
when the base geometry changes length or orientation, avoiding discontinuous 90° jumps.

If ``face.Orientation == "Reversed"``, the frame is flipped so N points outward.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchCommands.py:1975`. Decorators are copied as source expressions and have not been executed.

## `ArchCommands.read_pat_pattern_names`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def read_pat_pattern_names(filename):
```

Iterate over the pattern names declared in a PAT file.

PAT files declare each pattern with a header line of the form ``*Name, Description``.
Missing or unreadable files produce no names.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchCommands.py:2081`. Decorators are copied as source expressions and have not been executed.

## `ArchCommands.first_pat_pattern_name`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def first_pat_pattern_name(filename):
```

Return the first pattern name in a PAT file, or ``""`` if none is found.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchCommands.py:2100`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`ArchCommands.__title__`, `ArchCommands.__author__`, `ArchCommands.__url__`, `ArchCommands._usedForAttachment`, `ArchCommands._derive_u_from_reference`, `ArchCommands._derive_u_from_longest_edge`. These are source internals unless an explicit export establishes otherwise.

