# Python source module `ArchCommands`

[Python catalogue](../index.md)

Evidence: `src/Mod/BIM/ArchCommands.py`. Import path is source-routed; installed availability is unverified.

Literal `__all__`: not available; source names do not imply supported public API.

[part 1](index.md) | [part 2](index-2.md)

## Imports, aliases and conditional reexports

### import FreeCAD

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `ArchCommands.FreeCAD` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/BIM/ArchCommands.py:36`.

### import ArchComponent

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `ArchCommands.ArchComponent` -> `ArchComponent`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/BIM/ArchCommands.py:37`.

### import Draft

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `ArchCommands.Draft` -> `Draft`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/BIM/ArchCommands.py:38`.

### import DraftVecUtils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `ArchCommands.DraftVecUtils` -> `DraftVecUtils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/BIM/ArchCommands.py:39`.

### from FreeCAD import Vector

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `ArchCommands.Vector` -> `FreeCAD.Vector`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/BIM/ArchCommands.py:41`.

### from draftutils import params

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `ArchCommands.params` -> `draftutils.params`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/BIM/ArchCommands.py:42`.

### from draftutils.groups import is_group

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `ArchCommands.is_group` -> `draftutils.groups.is_group`.

[Source module `draftutils.groups`](../draftutils/groups/index.md).

Evidence: `src/Mod/BIM/ArchCommands.py:43`.

### from PySide import QtGui, QtCore

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if FreeCAD.GuiUp`.

Bound source name `ArchCommands.QtGui` -> `PySide.QtGui`.

Bound source name `ArchCommands.QtCore` -> `PySide.QtCore`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/BIM/ArchCommands.py:46`.

### import FreeCADGui

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if FreeCAD.GuiUp`.

Bound source name `ArchCommands.FreeCADGui` -> `FreeCADGui`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/BIM/ArchCommands.py:47`.

### from draftutils.translate import translate

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if FreeCAD.GuiUp`.

Bound source name `ArchCommands.translate` -> `draftutils.translate.translate`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/BIM/ArchCommands.py:48`.

## Classes

Internal class `ArchCommands._SurveyObserver` at `src/Mod/BIM/ArchCommands.py:1289` is not expanded.

- [ArchCommands.SurveyTaskPanel](SurveyTaskPanel.md)

## `ArchCommands.translate`

Status: source-defined name; no independently verified stability/export guarantee.

Conditions: `else of (FreeCAD.GuiUp)`.

```python
def translate(ctxt, txt):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchCommands.py:51`. Decorators are copied as source expressions and have not been executed.

## `ArchCommands.is_type_or_link`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def is_type_or_link(obj, type_name):
```

Checks if the given object or its linked object is of the specified type.

Parameters
----------
obj: <App::DocumentObject>
    The object to check.
type_name: str
    The type to check against (e.g., 'Window', 'Wall').

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchCommands.py:60`. Decorators are copied as source expressions and have not been executed.

## `ArchCommands.getStringList`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getStringList(objects):
```

getStringList(objects): returns a string defining a list
of objects

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchCommands.py:78`. Decorators are copied as source expressions and have not been executed.

## `ArchCommands.getDefaultColor`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getDefaultColor(objectType):
```

getDefaultColor(string): returns a color value for the given object
type (Wall, Structure, Window, WindowGlass)

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchCommands.py:90`. Decorators are copied as source expressions and have not been executed.

## `ArchCommands.addComponents`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def addComponents(objectsList, host):
```

addComponents(objectsList,hostObject): adds the given object or the objects
from the given list as components to the given host Object. Use this for
example to add windows to a wall, or to add walls to a cell or floor.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchCommands.py:127`. Decorators are copied as source expressions and have not been executed.

## `ArchCommands.removeComponents`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def removeComponents(objectsList, host=None):
```

removeComponents(objectsList,[hostObject]): removes the given component or
the components from the given list from their parents. If a host object is
specified, this function will try adding the components as holes to the host
object instead.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchCommands.py:193`. Decorators are copied as source expressions and have not been executed.

## `ArchCommands.makeComponent`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeComponent(baseobj=None, name=None, delete=False):
```

makeComponent([baseobj],[name],[delete]): creates an undefined, non-parametric BIM
component from the given base object

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchCommands.py:307`. Decorators are copied as source expressions and have not been executed.

## `ArchCommands.cloneComponent`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def cloneComponent(obj):
```

cloneComponent(obj): Creates a clone of an object as an undefined component

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchCommands.py:336`. Decorators are copied as source expressions and have not been executed.

## `ArchCommands.setAsSubcomponent`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def setAsSubcomponent(obj):
```

Sets the given object properly to become a subcomponent (addition, subtraction)
of an Arch component

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchCommands.py:352`. Decorators are copied as source expressions and have not been executed.

## `ArchCommands.copyProperties`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def copyProperties(obj1, obj2):
```

copyProperties(obj1,obj2): Copies properties values from obj1 to obj2,
when that property exists in both objects

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchCommands.py:370`. Decorators are copied as source expressions and have not been executed.

## `ArchCommands.splitMesh`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def splitMesh(obj, mark=True):
```

splitMesh(object,[mark]): splits the given mesh object into separated components.
If mark is False, nothing else is done. If True (default), non-manifold components
will be painted in red.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchCommands.py:384`. Decorators are copied as source expressions and have not been executed.

## `ArchCommands.makeFace`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeFace(wires, method=2, cleanup=False):
```

makeFace(wires): makes a face from a list of wires, finding which ones are holes

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchCommands.py:406`. Decorators are copied as source expressions and have not been executed.

## `ArchCommands.closeHole`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def closeHole(shape):
```

closeHole(shape): closes a hole in an open shape

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchCommands.py:465`. Decorators are copied as source expressions and have not been executed.

## `ArchCommands.getCutVolume`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getCutVolume(cutplane, shapes, clip=False, depth=None):
```

getCutVolume(cutplane,shapes,[clip,depth]): returns a cut face and a cut volume
from the given shapes and the given cutting plane. If clip is True, the cutvolume will
also cut off everything outside the cutplane projection. If depth is non-zero, geometry
further than this distance will be clipped off

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchCommands.py:495`. Decorators are copied as source expressions and have not been executed.

## `ArchCommands.getShapeFromMesh`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getShapeFromMesh(mesh, fast=True, tolerance=0.001, flat=False, cut=True):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchCommands.py:581`. Decorators are copied as source expressions and have not been executed.

## `ArchCommands.projectToVector`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def projectToVector(shape, vector):
```

projectToVector(shape,vector): projects the given shape on the given
vector

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchCommands.py:659`. Decorators are copied as source expressions and have not been executed.

## `ArchCommands.meshToShape`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def meshToShape(obj, mark=True, fast=True, tol=0.001, flat=False, cut=True):
```

meshToShape(object,[mark,fast,tol,flat,cut]): turns a mesh into a shape, joining coplanar facets. If
mark is True (default), non-solid objects will be marked in red. Fast uses a faster algorithm by
building a shell from the facets then removing splitter, tol is the tolerance used when converting
mesh segments to wires, flat will force the wires to be perfectly planar, to be sure they can be
turned into faces, but this might leave gaps in the final shell. If cut is true, holes in faces are
made by subtraction (default)

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchCommands.py:678`. Decorators are copied as source expressions and have not been executed.

## `ArchCommands.removeCurves`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def removeCurves(shape, dae=False, tolerance=5):
```

removeCurves(shape,dae,tolerance=5): replaces curved faces in a shape
with faceted segments. If dae is True, DAE triangulation options are used

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchCommands.py:704`. Decorators are copied as source expressions and have not been executed.

## `ArchCommands.removeShape`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def removeShape(objs, mark=True):
```

removeShape(objs, mark=True): takes an arch object (wall or structure) built on a cubic shape, and removes
the inner shape, keeping its length, width and height as parameters. If mark is True, objects that cannot
be processed by this function will become red.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchCommands.py:719`. Decorators are copied as source expressions and have not been executed.

## `ArchCommands.mergeCells`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def mergeCells(objectslist):
```

mergeCells(objectslist): merges the objects in the given list
into one. All objects must be of the same type and based on the Cell
object (cells, floors, buildings, or sites).

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchCommands.py:759`. Decorators are copied as source expressions and have not been executed.

## `ArchCommands.download`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def download(url, force=False):
```

download(url,force=False): downloads a file from the given URL and saves it in the
macro path. Returns the path to the saved file. If force is True, the file will be
downloaded again evn if it already exists.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchCommands.py:787`. Decorators are copied as source expressions and have not been executed.

## `ArchCommands.check`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def check(objectslist, includehidden=False):
```

check(objectslist,includehidden=False): checks if the given objects contain only solids

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchCommands.py:812`. Decorators are copied as source expressions and have not been executed.

## `ArchCommands.getHost`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getHost(obj, strict=True):
```

getHost(obj,[strict]): returns the host of the current object. If strict is true (default),
the host can only be an object of a higher level than the given one, or in other words, if a wall
is contained in another wall which is part of a floor, the floor is returned instead of the parent wall

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchCommands.py:842`. Decorators are copied as source expressions and have not been executed.

## `ArchCommands.pruneIncluded`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def pruneIncluded(objectslist, strict=False, silent=False):
```

pruneIncluded(objectslist,[strict]): removes from a list of Arch objects, those that are subcomponents of
another shape-based object, leaving only the top-level shapes. If strict is True, the object
is removed only if the parent is also part of the selection.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchCommands.py:862`. Decorators are copied as source expressions and have not been executed.

## `ArchCommands.getAllChildren`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getAllChildren(objectlist):
```

getAllChildren(objectlist): returns all the children of all the object sin the list

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchCommands.py:928`. Decorators are copied as source expressions and have not been executed.

## `ArchCommands.get_architectural_contents`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_architectural_contents(initial_objects, recursive=True, discover_hosted_elements=True, include_components_from_additions=False, include_initial_objects_in_result=True):
```

Retrieves a flat list of unique architectural objects that are considered "contents" of or are
related to the given initial_objects.

This includes:
- Children from .Group properties (hierarchical traversal if recursive=True).
- Architecturally hosted elements (e.g., windows in walls, rebars in structures)
  if discover_hosted_elements=True.
- Optionally, components from .Additions properties.

The traversal uses a queue and ensures objects are processed only once.

Parameters:
-----------
initial_objects : App::DocumentObject or list of App::DocumentObject
    The starting object(s) from which to discover contents.
recursive : bool, optional
    If True (default), recursively find contents of discovered group-like
    objects (those with a .Group property and identified by draftutils.groups.is_group()).
discover_hosted_elements : bool, optional
    If True (default), try to find elements like windows, doors, rebars
    that are architecturally hosted by other elements encountered during traversal.
    This relies on Draft.getType() and common Arch properties like .Hosts or .Host.
include_components_from_additions : bool, optional
    If False (default), objects found in .Additions lists are not added.
    Set to True if these components should be part of the discovered contents.
include_initial_objects_in_result : bool, optional
    If True (default), the objects in initial_objects themselves will be
    included in the output list (if not already discovered as a child of another).
    If False, only their "descendant" contents are returned.

Returns:
--------
list of App::DocumentObject
    A flat list of unique architectural document objects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchCommands.py:942`. Decorators are copied as source expressions and have not been executed.

## `ArchCommands.survey`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def survey(callback=False):
```

survey(): starts survey mode, where you can click edges and faces to get their lengths or area.
Clicking on no object (on an empty area) resets the count.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchCommands.py:1079`. Decorators are copied as source expressions and have not been executed.

## `ArchCommands.toggleIfcBrepFlag`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def toggleIfcBrepFlag(obj):
```

toggleIfcBrepFlag(obj): toggles the IFC brep flag of the given object, forcing it
to be exported as brep geometry or not.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchCommands.py:1491`. Decorators are copied as source expressions and have not been executed.

## `ArchCommands.makeCompoundFromSelected`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeCompoundFromSelected(objects=None):
```

makeCompoundFromSelected([objects]): Creates a new compound object from the given
subobjects (faces, edges) or from the selection if objects is None

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchCommands.py:1525`. Decorators are copied as source expressions and have not been executed.

## `ArchCommands.cleanArchSplitter`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def cleanArchSplitter(objects=None):
```

cleanArchSplitter([objects]): removes the splitters from the base shapes
of the given Arch objects or selected Arch objects if objects is None

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchCommands.py:1543`. Decorators are copied as source expressions and have not been executed.

## `ArchCommands.rebuildArchShape`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def rebuildArchShape(objects=None):
```

rebuildArchShape([objects]): takes the faces from the base shape of the given (or selected
if objects is None) Arch objects, and tries to rebuild a valid solid from them.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchCommands.py:1565`. Decorators are copied as source expressions and have not been executed.

