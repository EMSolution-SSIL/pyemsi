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

## `Arch.makeRebar`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeRebar(baseobj: Optional[FreeCAD.DocumentObject]=None, sketch: Optional[FreeCAD.DocumentObject]=None, diameter: Optional[float]=None, amount: int=1, offset: Optional[float]=None, name: Optional[str]=None) -> Optional[FreeCAD.DocumentObject]:
```

Creates a reinforcement bar (rebar) object.

The rebar's geometry is typically defined by a `sketch` object (e.g., a Sketcher::SketchObject
or a Draft.Wire). This sketch represents the path of a single bar. The `amount` and `spacing`
(calculated by the object) properties then determine how many such bars are created and
distributed.

The `baseobj` usually acts as the structural host for the rebar. The rebar's distribution (e.g.,
spacing, direction) can be calculated relative to this host object's dimensions if a `Host` is
assigned and the rebar logic uses it.

Parameters
----------
baseobj : FreeCAD.DocumentObject, optional
    The structural object to host the rebar (e.g., an ArchStructure._Structure created with
    `Arch.makeStructure()`). If provided with `sketch`, it's set as `rebar.Host`. If provided
    *without* a `sketch`, `rebar.Shape` is set from `baseobj.Shape`, and `rebar.Host` remains
    None. Defaults to None.
sketch : FreeCAD.DocumentObject, optional
    An object (e.g., "Sketcher::SketchObject") whose shape defines the rebar's path. Assigned to
    `rebar.Base`. If the sketch is attached to `baseobj` before calling this function (e.g. for
    positioning purposes), this function may clear that specific attachment to avoid conflicts,
    as the rebar itself will be hosted. Defaults to None.
diameter : float, optional
    The diameter of the rebar. If None, uses Arch preferences ("RebarDiameter"). Defaults to
    None.
amount : int, optional
    The number of rebar instances. Defaults to 1.
offset : float, optional
    Concrete cover distance, sets `rebar.OffsetStart` and `rebar.OffsetEnd`. If None, uses Arch
    preferences ("RebarOffset"). Defaults to None.
name : str, optional
    The user-visible name (Label) for the rebar. If None, defaults to "Rebar". Defaults to None.

Returns
-------
FreeCAD.DocumentObject or None
    The created rebar object, or None if creation fails.

Examples
--------
>>> import FreeCAD, Arch, Part, Sketcher
>>> doc = FreeCAD.newDocument()
>>> # Create a host structure (e.g., a concrete beam)
>>> beam = Arch.makeStructure(length=2000, width=200, height=300)
>>> doc.recompute() # Ensure beam's shape is ready
>>>
>>> # Create a sketch for the rebar path
>>> rebar_sketch = doc.addObject('Sketcher::SketchObject')
>>> # For positioning, attach the sketch to a face of the beam *before* makeRebar
>>> # Programmatically select a face (e.g., the first one)
>>> # For stable scripts, select faces by more reliable means
>>> rebar_sketch.AttachmentSupport = (beam, ['Face1']) # Faces are 1-indexed
>>> rebar_sketch.MapMode = "FlatFace"
>>> # Define sketch geometry relative to the attached face's plane
>>> rebar_sketch.addGeometry(Part.LineSegment(FreeCAD.Vector(25, 25, 0),
...                                         FreeCAD.Vector(1975, 25, 0)), False)
>>> doc.recompute() # Recompute sketch after geometry and attachment
>>>
>>> # Create the rebar object, linking it to the beam and using the sketch
>>> rebar_obj = Arch.makeRebar(baseobj=beam, sketch=rebar_sketch, diameter=12,
...                            amount=4, offset=25)
>>> doc.recompute() # Trigger rebar's geometry calculation

Evidence: `src/Mod/BIM/Arch.py:936`. Decorators are copied as source expressions and have not been executed.

## `Arch.makeReference`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeReference(filepath=None, partname=None, name=None):
```

Creates an Arch reference object.

Parameters
----------
filepath : str, optional
    The file path of the external reference. Defaults to None.
partname : str, optional
    The name of the part in the external file. Defaults to None.
name : str, optional
    The name to assign to the created reference. Defaults to None.

Returns
-------
Part::FeaturePython
    The created reference object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/Arch.py:1064`. Decorators are copied as source expressions and have not been executed.

## `Arch.makeRoof`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeRoof(baseobj=None, facenr=0, angles=[45.0], run=[250.0], idrel=[-1], thickness=[50.0], overhang=[100.0], name=None):
```

Creates a roof object based on a closed wire or an object.

Parameters
----------
baseobj : Part::FeaturePython, optional
    The base object for the roof. Defaults to None.
facenr : int, optional
    The face number to use as the base. Defaults to 0.
angles : list of float, optional
    The angles for each edge of the roof. Defaults to [45.0].
run : list of float, optional
    The run distances for each edge. Defaults to [250.0].
idrel : list of int, optional
    The relative IDs for each edge. Defaults to [-1].
thickness : list of float, optional
    The thickness of the roof for each edge. Defaults to [50.0].
overhang : list of float, optional
    The overhang distances for each edge. Defaults to [100.0].
name : str, optional
    The name to assign to the created roof. Defaults to None.

Returns
-------
Part::FeaturePython
    The created roof object.

Notes
-----
1. If the base object is a solid the roof uses its shape.
2. The angles, run, idrel, thickness, and overhang lists are automatically
   completed to match the number of edges in the wire.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/Arch.py:1103`. Decorators are copied as source expressions and have not been executed.

## `Arch.makeSchedule`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeSchedule():
```

Creates a schedule object in the active document.

Returns
-------
App::FeaturePython
    The created schedule object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/Arch.py:1193`. Decorators are copied as source expressions and have not been executed.

## `Arch.makeSectionPlane`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeSectionPlane(objectslist=None, name=None):
```

Creates a section plane object including the given objects.

Parameters
----------
objectslist : list of Part::FeaturePython, optional
    A list of objects to include in the section plane. If no object is given, the whole
    document will be considered. Defaults to None.
name : str, optional
    The name to assign to the created section plane. Defaults to None.

Returns
-------
App::FeaturePython
    The created section plane object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/Arch.py:1216`. Decorators are copied as source expressions and have not been executed.

## `Arch.makeSite`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeSite(objectslist=None, baseobj=None, name=None):
```

Creates a site object including the given objects.

Parameters
----------
objectslist : list of Part::FeaturePython, optional
    A list of objects to include in the site. Defaults to None.
baseobj : Part::FeaturePython, optional
    The base object for the site. Defaults to None.
name : str, optional
    The name to assign to the created site. Defaults to None.

Returns
-------
Part::FeaturePython
    The created site object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/Arch.py:1259`. Decorators are copied as source expressions and have not been executed.

## `Arch.makeSpace`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeSpace(objects=None, baseobj=None, name=None):
```

Creates a space object from the given objects.

Parameters
----------
objects : object or List(<SelectionObject>) or App::PropertyLinkSubList, optional
    The object or selection set that defines the space. If a single object is given,
    it becomes the base shape for the object. If the object or selection set contains
    subelements, these will be used as the boundaries to create the space. By default None.
baseobj : object or List(<SelectionObject>) or App::PropertyLinkSubList, optional
    Currently unimplemented, it replaces and behaves in the same way as the objects parameter
    if defined. By default None.
name : str, optional
    The user-facing name to assign to the space object's label. By default None, in
    which case the label is set to "Space".

Returns
-------
Part::FeaturePython
    The created space object.

Notes
-----
The objects parameter can be passed using either of these different formats:

1. Single object (e.g. a Part::Feature document object). Will be used as the space's base
   shape.::
        objects = <Part::Feature>
2. List of selection objects, as provided by ``Gui.Selection.getSelectionEx()``. This
   requires the GUI to be active. The `SubObjects` property of each selection object in the
   list defines the space's boundaries. If the list contains a single selection object without
   subobjects, or with only one subobject, the object in its ``Object`` property is used as
   the base shape.::
        objects = [<SelectionObject>, ...]
3. A list of tuples that can be assigned to an ``App::PropertyLinkSubList`` property. Each
   tuple contains a document object and a nested tuple of subobjects that define the boundaries.
   If the list contains a single tuple without a nested subobjects tuple, or a subobjects tuple
   with only one subobject, the object in the tuple is used as the base shape.::
        objects = [(obj1, ("Face1")), (obj2, ("Face1")), ...]
        objects = [(obj, ("Face1", "Face2", "Face3", "Face4"))]

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/Arch.py:1298`. Decorators are copied as source expressions and have not been executed.

## `Arch.addSpaceBoundaries`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def addSpaceBoundaries(space, subobjects):
```

Adds the given subobjects as defining boundaries of the given space.

Parameters
----------
space : ArchSpace._Space
    Arch space object to add the boundaries to.
subobjects : List(<SelectionObject>) or App::PropertyLinkSubList
    List of boundaries to add to the space.

Notes
-----
The subobjects parameter can be passed using either of these different formats:

1. List of selection objects, as provided by ``Gui.Selection.getSelectionEx()``. This
   requires the GUI to be active. The `SubObjects` property of each selection object in the
   list defines the boundaries to add to the space.::
        subobjects = [<SelectionObject>, ...]
2. A list of tuples that can be assigned to an ``App::PropertyLinkSubList`` property. Each
   tuple contains a document object and a nested tuple of subobjects that define the boundaries
   to add.::
        subobjects = [(obj1, ("Face1")), (obj2, ("Face1")), ...]
        subobjects = [(obj, ("Face1", "Face2", "Face3", "Face4"))]

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/Arch.py:1391`. Decorators are copied as source expressions and have not been executed.

## `Arch.removeSpaceBoundaries`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def removeSpaceBoundaries(space, subobjects):
```

Remove the given subobjects as defining boundaries of the given space.

Parameters
----------
space : ArchSpace._Space
    Arch space object to remove the boundaries from.
subobjects : List(<SelectionObject>) or App::PropertyLinkSubList
    List of boundaries to remove from the space.

Notes
-----
The subobjects parameter can be passed using either of these different formats:

1. List of selection objects, as provided by ``Gui.Selection.getSelectionEx()``. This
   requires the GUI to be active. The `SubObjects` property of each selection object in the
   list defines the boundaries to remove from the space.::
        subobjects = [<SelectionObject>, ...]
2. A list of tuples that can be assigned to an ``App::PropertyLinkSubList`` property. Each
   tuple contains a document object and a nested tuple of subobjects that define the boundaries
   to remove.::
        subobjects = [(obj1, ("Face1")), (obj2, ("Face1")), ...]
        subobjects = [(obj, ("Face1", "Face2", "Face3", "Face4"))]

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/Arch.py:1421`. Decorators are copied as source expressions and have not been executed.

## `Arch.makeStairs`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeStairs(baseobj=None, length=None, width=None, height=None, steps=None, name=None):
```

Creates a stairs object with the given attributes.

Parameters
----------
baseobj : Part::FeaturePython, optional
    The base object for the stairs. Defaults to None.
length : float, optional
    The length of the stairs. Defaults to None.
width : float, optional
    The width of the stairs. Defaults to None.
height : float, optional
    The height of the stairs. Defaults to None.
steps : int, optional
    The number of steps. Defaults to None.
name : str, optional
    The name to assign to the created stairs. Defaults to None.

Returns
-------
Part::FeaturePython
    The created stairs object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/Arch.py:1451`. Decorators are copied as source expressions and have not been executed.

## `Arch.makeRailing`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeRailing(stairs):
```

Creates railings for the given stairs.

Parameters
----------
stairs : list of Part::FeaturePython
    The stairs objects to add railings to.

Returns
-------
None

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/Arch.py:1577`. Decorators are copied as source expressions and have not been executed.

## `Arch.makeTruss`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeTruss(baseobj=None, name=None):
```

Creates a truss object from the given base object.

Parameters
----------
baseobj : Part::FeaturePython, optional
    The base object for the truss. Defaults to None.
name : str, optional
    The name to assign to the created truss. Defaults to None.

Returns
-------
Part::FeaturePython
    The created truss object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/Arch.py:1643`. Decorators are copied as source expressions and have not been executed.

## `Arch.makeWall`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeWall(baseobj=None, height=None, length=None, width=None, align=None, offset=None, face=None, name=None):
```

Create a wall based on a given object, and returns the generated wall.

TODO: It is unclear what defines which units this function uses.

Parameters
----------
baseobj: <Part::Feature>, optional
    The base object with which to build the wall. This can be a sketch, a
    draft object, a face, or a solid. It can also be left as None.
height: float, optional
    The height of the wall.
length: float, optional
    The length of the wall. Not used if the wall is based off an object.
    Will use Arch default if left empty.
width: float, optional
    The width of the wall. Not used if the base object is a face.  Will use
    Arch default if left empty.
align: str, optional
    Either "Center", "Left", or "Right". Effects the alignment of the wall
    on its baseline.
face: int, optional
    The index number of a face on the given baseobj, to base the wall on.
name: str, optional
    The name to give to the created wall.

Returns
-------
<Part::FeaturePython>
    Returns the generated wall.

Notes
-----
1. Creates a new <Part::FeaturePython> object, and turns it into a parametric wall
   object. This <Part::FeaturePython> object does not yet have any shape.
2. The wall then uses the baseobj.Shape as the basis to extrude out a wall shape,
   giving the new <Part::FeaturePython> object a shape.
3. It then hides the original baseobj.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/Arch.py:1677`. Decorators are copied as source expressions and have not been executed.

## `Arch.joinWalls`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def joinWalls(walls, delete=False, deletebase=False):
```

Join the given list of walls into one sketch-based wall.

Take the first wall in the list, and adds on the other walls in the list.
Return the modified first wall.

Setting delete to True, will delete the other walls. Only join walls
if the walls have the same width, height and alignment.

Parameters
----------
walls : list of <Part::FeaturePython>
    List containing the walls to add to the first wall in the list. Walls must
    be based off a base object.
delete : bool, optional
    If True, deletes the other walls in the list. Defaults to False.
deletebase : bool, optional
    If True, and delete is True, the base of the other walls is also deleted
    Defaults to False.

Returns
-------
Part::FeaturePython
    The joined wall object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/Arch.py:1762`. Decorators are copied as source expressions and have not been executed.

