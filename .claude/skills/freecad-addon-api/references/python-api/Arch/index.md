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

## Imports, aliases and conditional reexports

### import FreeCAD

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Arch.FreeCAD` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/BIM/Arch.py:55`.

### from freecad.deprecation import deprecated

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Arch.deprecated` -> `freecad.deprecation.deprecated`.

[Source module `freecad.deprecation`](../freecad/deprecation/index.md).

Evidence: `src/Mod/BIM/Arch.py:56`.

### from typing import Optional

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Arch.Optional` -> `typing.Optional`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/BIM/Arch.py:57`.

### import FreeCADGui

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if FreeCAD.GuiUp`.

Bound source name `Arch.FreeCADGui` -> `FreeCADGui`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/BIM/Arch.py:60`.

### from ArchCommands import *

Facade reexport declaration.

[Source module `ArchCommands`](../ArchCommands/index.md).

Wildcard export is retained as a wildcard. Its full runtime member set is not inferred; inspect the target's export declarations and initialization.

Evidence: `src/Mod/BIM/Arch.py:70`.

### from ArchWindowPresets import *

Facade reexport declaration.

[Source module `ArchWindowPresets`](../ArchWindowPresets/index.md).

Wildcard export is retained as a wildcard. Its full runtime member set is not inferred; inspect the target's export declarations and initialization.

Evidence: `src/Mod/BIM/Arch.py:71`.

### from ArchSql import *

Facade reexport declaration.

[Source module `ArchSql`](../ArchSql/index.md).

Wildcard export is retained as a wildcard. Its full runtime member set is not inferred; inspect the target's export declarations and initialization.

Evidence: `src/Mod/BIM/Arch.py:72`.

## `Arch.QT_TRANSLATE_NOOP`

Status: source-defined name; no independently verified stability/export guarantee.

```python
QT_TRANSLATE_NOOP = FreeCAD.Qt.QT_TRANSLATE_NOOP
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/BIM/Arch.py:64`. Decorators are copied as source expressions and have not been executed.

## `Arch.translate`

Status: source-defined name; no independently verified stability/export guarantee.

```python
translate = FreeCAD.Qt.translate
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/BIM/Arch.py:65`. Decorators are copied as source expressions and have not been executed.

## `Arch.makeAxis`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeAxis(num=1, size=1000, name=None):
```

Creates an axis set in the active document.

Parameters
----------
num : int, optional
    The number of axes to create. Defaults to 1.
size : float, optional
    The interval distance between axes. Defaults to 1000.
name : str, optional
    The name to assign to the created axis object. Defaults to None.

Returns
-------
Part::FeaturePython
    The created axis object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/Arch.py:77`. Decorators are copied as source expressions and have not been executed.

## `Arch.makeAxisSystem`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeAxisSystem(axes, name=None):
```

Creates an axis system from the given list of axes.

Parameters
----------
axes : list of Part::FeaturePython
    A list of axis objects to include in the axis system.
name : str, optional
    The name to assign to the created axis system. Defaults to None.

Returns
-------
App::FeaturePython
    The created axis system object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/Arch.py:120`. Decorators are copied as source expressions and have not been executed.

## `Arch.makeBuildingPart`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeBuildingPart(objectslist=None, baseobj=None, name=None):
```

Creates a building part including the given objects in the list.

Parameters
----------
objectslist : list of Part::FeaturePython, optional
    A list of objects to include in the building part. Defaults to None.
baseobj : Part::FeaturePython, optional
    The base object for the building part. Defaults to None.
name : str, optional
    The name to assign to the created building part. Defaults to None.

Returns
-------
App::GeometryPython
    The created building part object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/Arch.py:150`. Decorators are copied as source expressions and have not been executed.

## `Arch.makeFloor`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeFloor(objectslist=None, baseobj=None, name=None):
```

Creates a floor/level in the active document.

Parameters
----------
objectslist : list of Part::FeaturePython, optional
    A list of objects to include in the floor. Defaults to None.
baseobj : Part::FeaturePython, optional
    The base object for the floor. Defaults to None.
name : str, optional
    The name to assign to the created floor. Defaults to None.

Returns
-------
App::GeometryPython
    The created floor object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/Arch.py:185`. Decorators are copied as source expressions and have not been executed.

## `Arch.makeBuilding`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeBuilding(objectslist=None, baseobj=None, name=None):
```

Creates a building in the active document.

Parameters
----------
objectslist : list of Part::FeaturePython, optional
    A list of objects to include in the building. Defaults to None.
baseobj : Part::FeaturePython, optional
    The base object for the building. Defaults to None.
name : str, optional
    The name to assign to the created building. Defaults to None.

Returns
-------
App::GeometryPython
    The created building object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/Arch.py:210`. Decorators are copied as source expressions and have not been executed.

## `Arch.make2DDrawing`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def make2DDrawing(objectslist=None, baseobj=None, name=None):
```

Creates a 2D drawing view in the active document.

Parameters
----------
objectslist : list of Part::FeaturePython, optional
    A list of objects to include in the drawing. Defaults to None.
baseobj : Part::FeaturePython, optional
    The base object for the drawing. Defaults to None.
name : str, optional
    The name to assign to the created drawing. Defaults to None.

Returns
-------
App::GeometryPython
    The created 2D drawing object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/Arch.py:243`. Decorators are copied as source expressions and have not been executed.

## `Arch.convertFloors`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def convertFloors(floor=None):
```

Converts the given floor or building into building parts.

Parameters
----------
floor : Part::FeaturePython, optional
    The floor or building to convert. If None, all Arch floors in the active document
    are converted. Defaults to None.

Returns
-------
None

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/Arch.py:285`. Decorators are copied as source expressions and have not been executed.

## `Arch.makeCurtainWall`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeCurtainWall(baseobj=None, name=None):
```

Creates a curtain wall object in the active document.

Parameters
----------
baseobj : Part::FeaturePython, optional
    The base object for the curtain wall. Defaults to None.
name : str, optional
    The name to assign to the created curtain wall. Defaults to None.

Returns
-------
Part::FeaturePython
    The created curtain wall object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/Arch.py:342`. Decorators are copied as source expressions and have not been executed.

## `Arch.makeEquipment`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeEquipment(baseobj=None, placement=None, name=None):
```

Creates an equipment object from the given base object in the active document.

Parameters
----------
baseobj : Part::FeaturePython or Mesh::Feature, optional
    The base object for the equipment. Defaults to None.
placement : FreeCAD.Placement, optional
    The placement of the equipment. Defaults to None.
name : str, optional
    The name to assign to the created equipment. Defaults to None.

Returns
-------
Part::FeaturePython
    The created equipment object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/Arch.py:375`. Decorators are copied as source expressions and have not been executed.

## `Arch.makeFence`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeFence(section, post, path):
```

Creates a fence object in the active document.

Parameters
----------
section : Part::FeaturePython
    The section profile of the fence.
post : Part::FeaturePython
    The post profile of the fence.
path : Part::FeaturePython
    The path along which the fence is created.

Returns
-------
Part::FeaturePython
    The created fence object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/Arch.py:414`. Decorators are copied as source expressions and have not been executed.

## `Arch.makeFrame`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeFrame(baseobj, profile, name=None):
```

Creates a frame object from a base sketch (or any other object containing wires) and a
profile object (an extrudable 2D object containing faces or closed wires).

Parameters
----------
baseobj : Part::FeaturePython
    The base object containing wires to define the frame.
profile : Part::FeaturePython
    The profile object, an extrudable 2D object containing faces or closed wires.
name : str, optional
    The name to assign to the created frame. Defaults to None.

Returns
-------
Part::FeaturePython
    The created frame object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/Arch.py:450`. Decorators are copied as source expressions and have not been executed.

## `Arch.makeGrid`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeGrid(name=None):
```

Creates a grid object in the active document.

Parameters
----------
name : str, optional
    The name to assign to the created grid. Defaults to None.

Returns
-------
Part::FeaturePython
    The created grid object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/Arch.py:486`. Decorators are copied as source expressions and have not been executed.

## `Arch.makeMaterial`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeMaterial(name=None, color=None, transparency=None):
```

Creates a material object in the active document.

Parameters
----------
name : str, optional
    The name to assign to the created material. Defaults to None.
color : tuple of float, optional
    The RGB color of the material. Defaults to None.
transparency : float, optional
    The transparency level of the material. Defaults to None.

Returns
-------
App::MaterialObjectPython
    The created material object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/Arch.py:518`. Decorators are copied as source expressions and have not been executed.

## `Arch.makeMultiMaterial`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeMultiMaterial(name=None):
```

Creates a multi-material object in the active document.

Parameters
----------
name : str, optional
    The name to assign to the created multi-material. Defaults to None.

Returns
-------
App::FeaturePython
    The created multi-material object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/Arch.py:557`. Decorators are copied as source expressions and have not been executed.

## `Arch.getMaterialContainer`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getMaterialContainer():
```

Returns a group object to store materials in the active document.

Returns
-------
App::DocumentObjectGroupPython
    The material container object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/Arch.py:583`. Decorators are copied as source expressions and have not been executed.

## `Arch.getDocumentMaterials`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getDocumentMaterials():
```

Retrieves all material objects in the active document.

Returns
-------
list of App::MaterialObjectPython
    A list of all material objects in the document.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/Arch.py:609`. Decorators are copied as source expressions and have not been executed.

## `Arch.makePanel`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makePanel(baseobj=None, length=0, width=0, thickness=0, placement=None, name=None):
```

Creates a panel element based on the given profile object and the given
extrusion thickness. If no base object is given, you can also specify
length and width for a simple cubic object.

Parameters
----------
baseobj : Part::FeaturePython, optional
    The base profile object for the panel. Defaults to None.
length : float, optional
    The length of the panel. Defaults to 0.
width : float, optional
    The width of the panel. Defaults to 0.
thickness : float, optional
    The thickness of the panel. Defaults to 0.
placement : FreeCAD.Placement, optional
    The placement of the panel. Defaults to None.
name : str, optional
    The name to assign to the created panel. Defaults to None.

Returns
-------
Part::FeaturePython
    The created panel object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/Arch.py:628`. Decorators are copied as source expressions and have not been executed.

## `Arch.makePanelCut`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makePanelCut(panel, name=None):
```

Creates a 2D view of the given panel in the 3D space, positioned at the origin.

Parameters
----------
panel : Part::FeaturePython
    The panel object to create a 2D view for.
name : str, optional
    The name to assign to the created panel cut. Defaults to None.

Returns
-------
Part::FeaturePython
    The created panel cut object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/Arch.py:676`. Decorators are copied as source expressions and have not been executed.

## `Arch.makePanelSheet`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makePanelSheet(panels=[], name=None):
```

Creates a sheet with the given panel cuts in the 3D space, positioned at the origin.

Parameters
----------
panels : list of Part::FeaturePython, optional
    A list of panel cuts to include in the sheet. Defaults to an empty list.
name : str, optional
    The name to assign to the created panel sheet. Defaults to None.

Returns
-------
Part::FeaturePython
    The created panel sheet object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/Arch.py:704`. Decorators are copied as source expressions and have not been executed.

## `Arch.makePipe`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makePipe(baseobj=None, diameter=0, length=0, placement=None, name=None):
```

Creates a pipe object from the given base object or specified dimensions.

Parameters
----------
baseobj : Part::FeaturePython, optional
    The base object for the pipe. Defaults to None.
diameter : float, optional
    The diameter of the pipe. Defaults to 0.
length : float, optional
    The length of the pipe. Defaults to 0.
placement : FreeCAD.Placement, optional
    The placement of the pipe. Defaults to None.
name : str, optional
    The name to assign to the created pipe. Defaults to None.

Returns
-------
Part::FeaturePython
    The created pipe object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/Arch.py:733`. Decorators are copied as source expressions and have not been executed.

## `Arch.makePipeConnector`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makePipeConnector(pipes, radius=0, name=None):
```

Creates a connector between the given pipes.

Parameters
----------
pipes : list of Part::FeaturePython
    A list of pipe objects to connect.
radius : float, optional
    The curvature radius of the connector. Defaults to 0, which uses the diameter of the first
    pipe.
name : str, optional
    The name to assign to the created connector. Defaults to None.

Returns
-------
Part::FeaturePython
    The created pipe connector object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/Arch.py:783`. Decorators are copied as source expressions and have not been executed.

## `Arch.makeProfile`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeProfile(profile=[0, 'REC', 'REC100x100', 'R', 100, 100]):
```

Creates a profile object based on the given profile data.

Parameters
----------
profile : list, optional
    A list defining the profile data. Defaults to [0, 'REC', 'REC100x100', 'R', 100, 100].
    The list should contain the following elements:

    0. listOrder: str
        The order of the profile data. Currently not used.
    1. profileSubClass: str
        The subclass of a given profile class (e.g. 'REC' for the 'C' class).
    2. profileName: str
        The name of the profile (e.g., 'REC100x100').
    3. profileClass: str
        The class of the profile (e.g., 'REC', 'C', 'H', etc.).
    4. dimensionsList: int
        A variable set of arguments that define the dimensions of the profile. Their
        interpretation and count depends on the type of profile. Not implemented
        as a list, it's a variable number of arguments within the main profile
        argument. For instance, a C profile will define outside diameter and thickness,
        whereas a H profile will define width, height, web thickness, and flange thickness.
        See https://wiki.freecad.org/Arch_Profile for more details on profile presets.

Returns
-------
Part::Part2DObjectPython
    The created profile object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/Arch.py:827`. Decorators are copied as source expressions and have not been executed.

## `Arch.makeProject`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@deprecated(deprecated_in='26.3', removed_in='27.2')
def makeProject(sites=None, name=None):
```

Create an Arch project.

If sites are provided, add them as children of the new project.

.. deprecated:: 26.3

Parameters
----------
sites: list of <Part::FeaturePython>, optional
    Sites to add as children of the project. Ultimately this could be
    anything, however.
name: str, optional
    The label for the project.

Returns
-------
<Part::FeaturePython>
    The created project.

Notes
-----
This function is deprecated and will be removed in a future version.
The NativeIFC project is the new way to create IFC projects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/Arch.py:897`. Decorators are copied as source expressions and have not been executed.

