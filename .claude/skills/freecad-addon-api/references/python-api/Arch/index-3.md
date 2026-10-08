# Python source module `Arch`

[Python catalogue](../index.md)

Evidence: `src/Mod/BIM/Arch.py`. Import path is source-routed; installed availability is unverified.

Core API for architectural and Building Information Modeling (BIM) in FreeCAD.

Provides tools for creating parametric architectural elements (walls, windows,
structures) and managing BIM data. Serves as the foundation for both the BIM
Workbench and third-party extensions.

## Features
- Parametric architectural components (walls, floors, roofs, windows)
- BIM data support (materials, IFC properties, classification systems)
- Integration with FreeCAD's core (Part, Draft) and other workbenches
- Object creation utilities for architectural workflows

## Usage
Designed for:
1. Internal API for FreeCAD's built-in BIM commands
2. Public API for add-on developers creating extension macros, workbenches, or
   other specialized BIM tools

## Examples
```python
import Arch
wall = Arch.makeWall(length=5000, width=200, height=3000)  # mm units
wall.recompute()
```

Literal `__all__`: not available; source names do not imply supported public API.

[part 1](index.md) | [part 2](index-2.md) | [part 3](index-3.md) | [part 4](index-4.md)

## `Arch.makeWindow`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeWindow(baseobj: Optional[FreeCAD.DocumentObject]=None, width: Optional[float]=None, height: Optional[float]=None, parts: Optional[list[str]]=None, name: Optional[str]=None) -> FreeCAD.DocumentObject:
```

Creates an Arch Window object, which can represent either a window or a door.

The created object can be based on a 2D profile (e.g., a Sketch), have its
dimensions set directly, or be defined by custom components. It can be
inserted into host objects like Walls, creating openings. The IfcType of
the object can be set to "Window" or "Door" accordingly (presets often
handle this automatically).

Parameters
----------
baseobj : FreeCAD.DocumentObject, optional
    The base object for the window/door.
    If `baseobj` is an existing `Arch.Window` (or Door), it will be cloned.
    If `baseobj` is a 2D object with wires (e.g., `Sketcher::SketchObject`,
    `Draft.Wire`), these wires are used to define the geometry.
    If `parts` is None, default components are generated from `baseobj.Shape.Wires`:
    - If one closed wire: `["Default", "Frame", "Wire0", "1", "0"]` (or "Solid panel").
    - If multiple closed wires (e.g., Wire0 outer, Wire1 inner):
      `["Default", "Frame", "Wire0,Wire1", "1", "0"]` (Wire1 cuts Wire0).
    The `Normal` direction is derived from `baseobj.Placement`.
    Defaults to None.
width : float, optional
    The total width of the window/door.
    If `baseobj` is None, this value is used by `ensureBase()` on first
    recompute to create a default sketch with a "Width" constraint.
    If `baseobj` is a sketch with a "Width" named constraint, setting
    `window_or_door.Width` will drive this sketch constraint. `makeWindow` itself
    does not initially set the object's `Width` *from* a sketch's constraint.
    Defaults to None (or an Arch preference value if `baseobj` is None).
height : float, optional
    The total height of the window/door.
    If `baseobj` is None, this value is used by `ensureBase()` on first
    recompute to create a default sketch with a "Height" constraint.
    If `baseobj` is a sketch with a "Height" named constraint, setting
    `window_or_door.Height` will drive this sketch constraint. `makeWindow` itself
    does not initially set the object's `Height` *from* a sketch's constraint.
    Defaults to None (or an Arch preference value if `baseobj` is None).
parts : list[str], optional
    A list defining custom components for the window/door. The list is flat, with
    every 5 elements describing one component:
    `["Name1", "Type1", "WiresStr1", "ThickStr1", "OffsetStr1", ...]`
    - `Name`: User-defined name (e.g., "OuterFrame").
    - `Type`: Component type (e.g., "Frame", "Glass panel", "Solid panel").
      See `ArchWindow.WindowPartTypes`.
    - `WiresStr`: Comma-separated string defining wire usage from `baseobj.Shape.Wires`
      (0-indexed) and optionally hinge/opening from `baseobj.Shape.Edges` (1-indexed).
      Example: `"Wire0,Wire1,Edge8,Mode1"`.
      - `"WireN"`: Uses Nth wire for the base face.
      - `"WireN,WireM"`: WireN is base, WireM is cutout.
      - `"EdgeK"`: Kth edge is hinge.
      - `"ModeL"`: Lth opening mode from `ArchWindow.WindowOpeningModes`.
    - `ThickStr`: Thickness as string (e.g., `"50.0"`). Appending `"+V"`
      adds the object's `Frame` property value.
    - `OffsetStr`: Offset along normal as string (e.g., `"25.0"`). Appending `"+V"`
      adds the object's `Offset` property value.
    Defaults to None. If None and `baseobj` is a sketch, default parts
    are generated as described under `baseobj`.
name : str, optional
    The name (label) for the created window/door. If None, a default localized
    name ("Window" or "Door", depending on context or subsequent changes) is used.
    Defaults to None.

Returns
-------
FreeCAD.DocumentObject
    The created Arch Window object (which is a `Part::FeaturePython` instance,
    configurable to represent a window or a door).

See Also
--------
ArchWindowPresets.makeWindowPreset : Create window/door from predefined types.
ArchWall.addComponents : Add a window/door to a wall (creates opening).

Notes
-----
- **Dual purpose (window/door)**: despite its name, this function is the primary
  way to programmatically create both windows and doors in the BIM workbench.
  The distinction is often made by setting the `IfcType` property of the
  created object to "Window" or "Door", and by the chosen components or preset.
- **Sketch-based dimensions**: If `baseobj` is a `Sketcher::SketchObject`
  with named constraints "Width" and "Height", these sketch constraints will be
  parametrically driven by the created object's `Width` and `Height` properties
  respectively *after* the object is created and its properties are changed.
  `makeWindow` itself does not initially populate the object's `Width`/`Height` from
  these sketch constraints if `width`/`height` arguments are not passed to it.
  The object's internal `Width` and `Height` properties are the drivers.
- **Object from dimensions (No `baseobj` initially)**: if `baseobj` is `None` but
  `width` and `height` are provided, `makeWindow` creates an Arch Window object.
  Upon the first `doc.recompute()`, the `ensureBase()` mechanism generates
  an internal sketch (`obj.Base`) with "Width" and "Height" constraints
  driven by `obj.Width` and `obj.Height`. However, `obj.WindowParts`
  will remain undefined, resulting in a shapeless object until `WindowParts`
  are manually set.
- **`obj.Frame` and `obj.Offset` properties**: these main properties of the
  created object (e.g., `my_window.Frame = 50.0`) provide the values used when
  `"+V"` is specified in the `ThicknessString` or `OffsetString` of a component
  within the `parts` list.
- **Hosting and openings**: to create an opening in a host object (e.g., `Arch.Wall`),
  set `obj.Hosts = [my_wall]`. The opening's shape is typically derived
  from `obj.HoleWire` (defaulting to the largest wire of `obj.Base`) and
  extruded by `obj.HoleDepth` (if 0, tries to match host thickness).
  A custom `obj.Subvolume` can also define the opening shape.
- **Component management**: components and their geometry are primarily
  managed by the `_Window` class and its methods in `ArchWindow.py`.
- **Initialization from sketch `baseobj`**: when `baseobj` is a sketch
  (e.g., `Sketcher::SketchObject`) and `parts` is `None` or provided:
    - The `window.Shape` (geometric representation) is correctly generated
      at the global position and orientation defined by `baseobj.Placement`.
    - However, the created window object's own `window.Placement` property is
      **not** automatically initialized from `baseobj.Placement` and typically
      remains at the identity placement (origin, no rotation).
    - Similarly, the `window.Width` and `window.Height` properties are **not**
      automatically populated from the dimensions of the `baseobj` sketch.
      These properties will default to 0.0 or values from Arch preferences
      (if `width`/`height` arguments to `makeWindow` are also `None`).
    - If you need the `window` object's `Placement`, `Width`, or `Height`
      properties to reflect the `baseobj` sketch for subsequent operations
      (e.g., if other systems query these specific window properties, or if
      you intend to parametrically drive the sketch via these window properties),
      you may need to set them manually after `makeWindow` is called:
    - The `ArchWindow._Window.execute()` method, when recomputing the window,
      *does* use `window.Base.Shape` (the sketch's shape in its global position)
      to generate the window's geometry. The `ArchWindow._Window.getSubVolume()`
      method also correctly uses `window.Base.Shape` and the window object's
      (identity) `Placement` for creating the cutting volume.

Examples
--------
>>> import FreeCAD as App
>>> import Draft, Arch, Sketcher, Part
>>> doc = App.newDocument("ArchWindowDoorExamples")

>>> # Ex1: Basic window from sketch and parts definition, oriented to XZ (vertical) plane
>>> sketch_ex1 = doc.addObject('Sketcher::SketchObject', 'WindowSketchEx1_Vertical')
>>> # Define geometry in sketch's local XY plane (width along local X, height along local Y)
>>> sketch_ex1.addGeometry(Part.LineSegment(App.Vector(0,0,0), App.Vector(1000,0,0))) # Wire0 - Outer
>>> sketch_ex1.addGeometry(Part.LineSegment(App.Vector(1000,0,0), App.Vector(1000,1200,0)))
>>> sketch_ex1.addGeometry(Part.LineSegment(App.Vector(1000,1200,0), App.Vector(0,1200,0)))
>>> sketch_ex1.addGeometry(Part.LineSegment(App.Vector(0,1200,0), App.Vector(0,0,0)))
>>> sketch_ex1.addGeometry(Part.LineSegment(App.Vector(100,100,0), App.Vector(900,100,0))) # Wire1 - Inner
>>> sketch_ex1.addGeometry(Part.LineSegment(App.Vector(900,100,0), App.Vector(900,1100,0)))
>>> sketch_ex1.addGeometry(Part.LineSegment(App.Vector(900,1100,0), App.Vector(100,1100,0)))
>>> sketch_ex1.addGeometry(Part.LineSegment(App.Vector(100,1100,0), App.Vector(100,100,0)))
>>> doc.recompute() # Update sketch Wires
>>> # Orient sketch: Rotate +90 deg around X-axis to place sketch's XY onto global XZ.
>>> # Sketch's local Y (height) now aligns with global Z. Sketch normal is global -Y.
>>> sketch_ex1.Placement.Rotation = App.Rotation(App.Vector(1,0,0), 90)
>>> doc.recompute() # Apply sketch placement
>>> window_ex1 = Arch.makeWindow(baseobj=sketch_ex1, name="MyWindowEx1_Vertical")
>>> # Window Normal will be derived as global +Y, extrusion along +Y.
>>> window_ex1.WindowParts = [
...     "Frame", "Frame", "Wire0,Wire1", "60", "0",      # Frame from Wire0-Wire1
...     "Glass", "Glass panel", "Wire1", "10", "25"     # Glass from Wire1, offset in Normal dir
... ]
>>> doc.recompute()

>>> # Ex2: Window from sketch with named "Width"/"Height" constraints (on default XY plane)
>>> sketch_ex2 = doc.addObject('Sketcher::SketchObject', 'WindowSketchEx2_Named')
>>> sketch_ex2.addGeometry(Part.LineSegment(App.Vector(0,0,0), App.Vector(800,0,0))) # Edge 0
>>> sketch_ex2.addGeometry(Part.LineSegment(App.Vector(800,0,0), App.Vector(800,600,0))) # Edge 1
>>> sketch_ex2.addGeometry(Part.LineSegment(App.Vector(800,600,0), App.Vector(0,600,0))) # Complete Wire0
>>> sketch_ex2.addGeometry(Part.LineSegment(App.Vector(0,600,0), App.Vector(0,0,0)))
>>> sketch_ex2.addConstraint(Sketcher.Constraint('DistanceX',0,1,0,2, 800))
>>> sketch_ex2.renameConstraint(sketch_ex2.ConstraintCount-1, "Width")
>>> sketch_ex2.addConstraint(Sketcher.Constraint('DistanceY',1,1,1,2, 600))
>>> sketch_ex2.renameConstraint(sketch_ex2.ConstraintCount-1, "Height")
>>> doc.recompute()
>>> window_ex2 = Arch.makeWindow(baseobj=sketch_ex2, name="MyWindowEx2_Parametric")
>>> window_ex2.WindowParts = ["Frame", "Frame", "Wire0", "50", "0"]
>>> doc.recompute()
>>> print(f"Ex2 Initial - Sketch Width: {sketch_ex2.getDatum('Width')}, Window Width: {window_ex2.Width.Value}")
>>> window_ex2.Width = 950 # This drives the sketch constraint
>>> doc.recompute()
>>> print(f"Ex2 Updated - Sketch Width: {sketch_ex2.getDatum('Width')}, Window Width: {window_ex2.Width.Value}")

>>> # Ex3: Window from dimensions only (initially shapeless, sketch on XY plane)
>>> window_ex3 = Arch.makeWindow(width=700, height=900, name="MyWindowEx3_Dims")
>>> print(f"Ex3 Initial - Base: {window_ex3.Base}, Shape isNull: {window_ex3.Shape.isNull()}")
>>> doc.recompute() # ensureBase creates the sketch on XY plane
>>> print(f"Ex3 After Recompute - Base: {window_ex3.Base.Name if window_ex3.Base else 'None'}, Shape isNull: {window_ex3.Shape.isNull()}")
>>> window_ex3.WindowParts = ["SimpleFrame", "Frame", "Wire0", "40", "0"] # Wire0 from auto-generated sketch
>>> doc.recompute()
>>> print(f"Ex3 After Parts - Shape isNull: {window_ex3.Shape.isNull()}")

>>> # Ex4: Door created using an ArchWindowPresets function
>>> # Note: Arch.makeWindowPreset calls Arch.makeWindow internally
>>> door_ex4_preset = makeWindowPreset(
...     "Simple door", width=900, height=2100,
...     h1=50, h2=0, h3=0, w1=70, w2=40, o1=0, o2=0 # Preset-specific params
... )
>>> if door_ex4_preset:
...     door_ex4_preset.Label = "MyDoorEx4_Preset"
...     doc.recompute()

>>> # Ex5: Door created from a sketch, with IfcType manually set (sketch on XY plane)
>>> sketch_ex5_door = doc.addObject('Sketcher::SketchObject', 'DoorSketchEx5')
>>> sketch_ex5_door.addGeometry(Part.LineSegment(App.Vector(0,0,0), App.Vector(850,0,0))) # Wire0
>>> sketch_ex5_door.addGeometry(Part.LineSegment(App.Vector(850,0,0), App.Vector(850,2050,0)))
>>> sketch_ex5_door.addGeometry(Part.LineSegment(App.Vector(850,2050,0), App.Vector(0,2050,0)))
>>> sketch_ex5_door.addGeometry(Part.LineSegment(App.Vector(0,2050,0), App.Vector(0,0,0)))
>>> doc.recompute()
>>> door_ex5_manual = Arch.makeWindow(baseobj=sketch_ex5_door, name="MyDoorEx5_Manual")
>>> door_ex5_manual.WindowParts = ["DoorPanel", "Solid panel", "Wire0", "40", "0"]
>>> door_ex5_manual.IfcType = "Door" # Explicitly define as a Door
>>> doc.recompute()

>>> # Ex6: Hosting the vertical window from Ex1 in an Arch.Wall
>>> wall_ex6 = Arch.makeWall(None, length=4000, width=200, height=2400)
>>> wall_ex6.Label = "WallForOpening_Ex6"
>>> # Window_ex1 is already oriented (its sketch placement was set in Ex1).
>>> # Now, just position the window object itself.
>>> window_ex1.Placement.Base = App.Vector(1500, wall_ex6.Width.Value / 2, 900) # X, Y (center of wall), Z (sill)
>>> window_ex1.HoleDepth = 0 # Use wall's thickness for the opening depth
>>> doc.recompute() # Apply window placement and HoleDepth
>>> window_ex1.Hosts = [wall_ex6]
>>> doc.recompute() # Wall recomputes to create the opening

Evidence: `src/Mod/BIM/Arch.py:1863`. Decorators are copied as source expressions and have not been executed.

## `Arch.is_debasable`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def is_debasable(wall):
```

Determines if an Arch Wall can be cleanly converted to a baseless state.

This function checks if a given wall is a valid candidate for a parametric
"debasing" operation, where its dependency on a Base object is removed and
it becomes driven by its own Length and Placement properties.

Parameters
----------
wall : FreeCAD.DocumentObject
    The Arch Wall object to check.

Returns
-------
bool
    ``True`` if the wall is a valid candidate for debasing, otherwise ``False``.

Notes
-----
A wall is considered debasable if its ``Base`` object's final shape consists
of exactly one single, straight edge. This check is generic and works for
any base object that provides a valid ``.Shape`` property, including
``Draft.Line`` and ``Sketcher::SketchObject`` objects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/Arch.py:2168`. Decorators are copied as source expressions and have not been executed.

## `Arch.debaseWall`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def debaseWall(wall):
```

Converts a line-based Arch Wall to be parametrically driven by its own
properties (Length, Width, Height) and Placement, removing its dependency
on a Base object.

This operation preserves the wall's exact size and global position.
It is only supported for walls based on a single, straight line.

Parameters
----------
wall : FreeCAD.DocumentObject
    The Arch Wall object to debase.

Returns
-------
bool
    True on success, False otherwise.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/Arch.py:2221`. Decorators are copied as source expressions and have not been executed.

## `Arch.makeReport`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeReport(name=None):
```

Creates a BIM Report object in the active document.

Parameters
----------
name : str, optional
    The name to assign to the created report object. Defaults to None.

Returns
-------
App::FeaturePython
    The created report object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/Arch.py:2415`. Decorators are copied as source expressions and have not been executed.

## `Arch.makeStructure`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeStructure(baseobj=None, length=None, width=None, height=None, name=None):
```

Create a parametric structural element (column, beam, or generic structure).

Creates a Structure object by extruding a base profile along its local Z axis. When no base
profile is given, a rectangular cross-section is generated from ``length`` and ``width``. The
element is automatically classified as "Beam" or "Column" based on the aspect ratio of
``length`` vs ``height``.

Parameters
----------
baseobj : App::DocumentObject, optional
    A 2-D profile (sketch, wire, face, etc.) to use as the cross-section. When provided,
    ``length`` and ``width`` are ignored for the cross-section shape, and the profile's own
    dimensions may be used instead. The base object is hidden in the 3-D view after assignment.
length : float, optional
    Cross-section length (X). If *both* ``length`` and ``height`` are omitted, defaults to the
    ``StructureLength`` preference. Ignored when *baseobj* is provided (unless it lacks
    dimension attributes).
width : float, optional
    Cross-section width (Y). Defaults to the ``StructureWidth`` preference when omitted.
height : float, optional
    Extrusion height (Z). Defaults to the ``StructureHeight`` preference when omitted together
    with ``length``.
name : str, optional
    Custom label for the new object. When omitted, the label is set to "Beam" or "Column"
    depending on the aspect ratio.

Returns
-------
App::FeaturePython or None
    The newly created Structure object, or ``None`` if there is no active
    document.

Notes
-----
- If ``length > height``, the element is classified as IFC type "Beam"; if ``height > length``,
  it is classified as "Column".
- When *baseobj* has ``Width``/``Height`` (or ``Length``/``Width``, or ``Length``/``Height``)
  attributes, those values are transferred to the structure's cross-section dimensions.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/Arch.py:2465`. Decorators are copied as source expressions and have not been executed.

## `Arch.makeStructuralSystem`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeStructuralSystem(objects=[], axes=[], name=None):
```

Create a structural system by arraying objects along one or more axes.

A StructuralSystem places a copy of each base object's shape at positions derived from the axes:
at the start point of each axis line when a single axis is given, or at the intersection points
when two or more axes are given. When no objects are provided, a system with no base is created.

Parameters
----------
objects : list of App::DocumentObject, optional
    Structure elements (or other shapes) to be repeated along the axes. Defaults to an empty
    list, which creates one system with no base.
axes : list of App::DocumentObject
    One or more Axis objects that define the repetition grid. At least one axis is required; the
    function returns ``None`` if *axes* is empty.
name : str, optional
    Custom label for the created system(s). Defaults to "StructuralSystem".

Returns
-------
App::FeaturePython or list of App::FeaturePython or None
    A single system when one object is given, a list when multiple objects are given, or
    ``None`` if *axes* is empty or there is no active document.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/Arch.py:2583`. Decorators are copied as source expressions and have not been executed.

## `Arch.placeAlongEdge`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def placeAlongEdge(p1, p2, horizontal=False):
```

Compute a Placement that orients a beam or column along an edge.

Used for both beam and column placement. The edge direction (*p1* to *p2*) defines the element's
span, and a right-handed coordinate frame is constructed around it. The working plane's normal
is used as the "up" reference: the cross product of up with the edge direction gives the
cross-section's sideways axis, and a second cross product completes the frame.

For beams (``horizontal=True``), the local X axis is aligned with the edge direction, so the
element's extrusion (along X) runs from *p1* to *p2*. For columns (``horizontal=False``), the
frame is built with the edge direction along Z, then rotated 90 degrees so the extrusion
(normally along Z) ends up running along the edge.

Parameters
----------
p1 : FreeCAD.Vector
    Start point of the edge. Becomes ``Placement.Base``.
p2 : FreeCAD.Vector
    End point of the edge. Together with *p1*, defines the element's span direction.
horizontal : bool, optional
    If ``True``, beam-style placement: the local X axis points along the edge. If ``False``
    (default), column-style placement: the frame is rotated 90 degrees so the local Z
    extrusion axis ends up along the edge.

Returns
-------
FreeCAD.Placement
    A placement at *p1* with orientation derived from the edge direction. If the edge is
    parallel to the working plane's normal, the cross product is zero and the rotation is left
    at identity (degenerate case).

Notes
-----
The current implementation uses a single cross-product chain to construct the frame, which can
produce unintuitive roll (rotation around the span axis) for non-orthogonal edge directions.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/Arch.py:2651`. Decorators are copied as source expressions and have not been executed.

## `Arch.makeCovering`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeCovering(baseobj=None, name=None):
```

Creates a covering object from the given base object.

Parameters
----------
baseobj : Part::FeaturePython, optional
    The base object for the covering. Defaults to None.
name : str, optional
    The name to assign to the created covering. Defaults to None.

Returns
-------
Part::FeaturePython
    The created covering object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/Arch.py:2713`. Decorators are copied as source expressions and have not been executed.

