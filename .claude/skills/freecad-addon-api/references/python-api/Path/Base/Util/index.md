# Python source module `Path.Base.Util`

[Python catalogue](../../../index.md)

Evidence: `src/Mod/CAM/Path/Base/Util.py`. Import path is source-routed; installed availability is unverified.

The purpose of this file is to collect some handy functions. The reason they
are not in Path.Base.Utils (and there is this confusing naming going on) is that
PathUtils depends on PathJob. Which makes it impossible to use the functions
and classes defined there in PathJob.

So if you add to this file and think about importing anything from PathScripts
other than Path.Log, then it probably doesn't belong here.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import FreeCAD

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Path.Base.Util.FreeCAD` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/CAM/Path/Base/Util.py:33`.

### import Part

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Path.Base.Util.Part` -> `Part`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/CAM/Path/Base/Util.py:34`.

### import Path

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Path.Base.Util.Path` -> `Path`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/CAM/Path/Base/Util.py:35`.

### import Path.Geom

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Path.Base.Util.Path` -> `Path.Geom`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/CAM/Path/Base/Util.py:36`.

## `Path.Base.Util.translate`

Status: source-defined name; no independently verified stability/export guarantee.

```python
translate = FreeCAD.Qt.translate
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/CAM/Path/Base/Util.py:38`. Decorators are copied as source expressions and have not been executed.

## `Path.Base.Util.getProperty`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getProperty(obj, prop):
```

getProperty(obj, prop) ... answer obj's property defined by its canonical name.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Base/Util.py:65`. Decorators are copied as source expressions and have not been executed.

## `Path.Base.Util.getPropertyValueString`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getPropertyValueString(obj, prop):
```

getPropertyValueString(obj, prop) ... answer a string representation of an object's property's value.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Base/Util.py:71`. Decorators are copied as source expressions and have not been executed.

## `Path.Base.Util.setProperty`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def setProperty(obj, prop, value):
```

setProperty(obj, prop, value) ... set the property value of obj's property defined by its canonical name.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Base/Util.py:79`. Decorators are copied as source expressions and have not been executed.

## `Path.Base.Util.NotValidBaseTypeIds`

Status: source-defined name; no independently verified stability/export guarantee.

```python
NotValidBaseTypeIds = []
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/CAM/Path/Base/Util.py:94`. Decorators are copied as source expressions and have not been executed.

## `Path.Base.Util.isValidBaseObject`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def isValidBaseObject(obj):
```

isValidBaseObject(obj) ... returns true if the object can be used as a base for a job.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Base/Util.py:97`. Decorators are copied as source expressions and have not been executed.

## `Path.Base.Util.isSolid`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def isSolid(obj):
```

isSolid(obj) ... return True if the object is a valid solid.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Base/Util.py:121`. Decorators are copied as source expressions and have not been executed.

## `Path.Base.Util.opProperty`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def opProperty(op, prop, default=None):
```

opProperty(op, prop) ... return the value of property prop of the underlying operation (or None if prop does not exist)

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Base/Util.py:129`. Decorators are copied as source expressions and have not been executed.

## `Path.Base.Util.toolControllerForOp`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def toolControllerForOp(op):
```

toolControllerForOp(op) ... return the tool controller used by the op.
If the op doesn't have its own tool controller but has a Base object, return its tool controller.
Otherwise return None.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Base/Util.py:138`. Decorators are copied as source expressions and have not been executed.

## `Path.Base.Util.coolantModeForOp`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def coolantModeForOp(op):
```

coolantModeForOp(op) ... return the coolant mode used by the op.
If the op doesn't have its own coolant mode but has a Base object, return its coolant mode.
Otherwise return "None".

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Base/Util.py:145`. Decorators are copied as source expressions and have not been executed.

## `Path.Base.Util.activeForOp`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def activeForOp(op):
```

activeForOp(op) ... return the active property used by the op.
If the op doesn't have its own active property but has a Base object, return its active property.
Otherwise return True.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Base/Util.py:152`. Decorators are copied as source expressions and have not been executed.

## `Path.Base.Util.getPublicObject`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getPublicObject(obj):
```

getPublicObject(obj) ... returns the object which should be used to reference a feature of the given object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Base/Util.py:159`. Decorators are copied as source expressions and have not been executed.

## `Path.Base.Util.clearExpressionEngine`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def clearExpressionEngine(obj):
```

clearExpressionEngine(obj) ... removes all expressions from obj.

There is currently a bug that invalidates the DAG if an object
is deleted that still has one or more expressions attached to it.
Use this function to remove all expressions before deletion.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Base/Util.py:168`. Decorators are copied as source expressions and have not been executed.

## `Path.Base.Util.workplaneForOp`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def workplaneForOp(op):
```

workplaneForOp(op) ... returns the effective Workplane of op as a Placement.

This is the single accessor for an operation's frame. Nothing outside this
module should read ``op.Workplane`` directly: the property has changed
shape twice already, and beyond indexed machining the tool axis stops being
a property of the operation at all. One accessor can absorb those changes;
scattered reads cannot.

``Workplane`` is a link to a named work plane held by the Job. No link
means the Job's own XY, which is ordinary Z-up milling. A document
restored but not yet migrated may still carry the older vector or
placement forms; those are read as they were.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Base/Util.py:179`. Decorators are copied as source expressions and have not been executed.

## `Path.Base.Util.toolAxisForOp`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def toolAxisForOp(op):
```

toolAxisForOp(op) ... returns the effective tool axis of op as a unit Vector.

The direction the tool points, from the part toward the tool - the
Workplane's local +Z. Constant for the whole operation, which is true for
indexed machining and is the assumption that simultaneous motion removes.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Base/Util.py:204`. Decorators are copied as source expressions and have not been executed.

## `Path.Base.Util.placementFromToolAxis`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def placementFromToolAxis(axis, origin=None):
```

placementFromToolAxis(axis, origin=None) ... builds a Workplane placement
whose local +Z is axis.

The rotation about that axis is not determined by the axis alone. The
convention here is FreeCAD.Rotation(Vector(0,0,1), axis), the minimal
rotation carrying global +Z onto axis, which is what the vector form of the
property implied and so is what document migration must reproduce.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Base/Util.py:213`. Decorators are copied as source expressions and have not been executed.

## `Path.Base.Util.sameWorkplane`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def sameWorkplane(a, b, tol=1e-06):
```

sameWorkplane(a, b, tol=1e-6) ... True if two Workplane placements name
the same frame for the purpose of reusing generated toolpath geometry.

Today this compares tool axes only, because an operation's path is
generated in a frame derived from the machine's solved rotary angles and
the Workplane's origin and in-plane X are recorded but not consumed
(see the Workplane property documentation). Two operations that share a
tool axis therefore share a frame.

When origins are consumed this has to compare full frames, and callers
that reuse geometry between operations - rest machining in particular -
become wrong if it is not changed at the same time. That is the reason
this is a named predicate rather than an inline comparison.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Base/Util.py:231`. Decorators are copied as source expressions and have not been executed.

## `Path.Base.Util.liesInPlanePerpendicularTo`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def liesInPlanePerpendicularTo(sub, axis, tol=1e-06):
```

liesInPlanePerpendicularTo(sub, axis) ... True if every point of sub is
at the same distance along axis, so the feature names a single depth.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Base/Util.py:250`. Decorators are copied as source expressions and have not been executed.

## `Path.Base.Util.depthOfFeature`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def depthOfFeature(sub, axis):
```

depthOfFeature(sub, axis) ... the depth named by a selected feature,
measured along axis, or None if it does not name one.

A depth is a coordinate in the frame an operation generates in, and that
frame's up direction is the tool axis. So the useful selection is a feature
lying in a plane perpendicular to the tool axis, and the depth it names is
its projection onto that axis.

For the default work plane the tool axis is +Z and this is the Z level it
has always been. That path is kept verbatim rather than expressed through
the general one, because Path.Geom.isHorizontal() accepts shapes - a
sphere, a surface of revolution - for which a bounding box maximum and a
maximum over vertices are not the same number, and three-axis behaviour
must not drift.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Base/Util.py:275`. Decorators are copied as source expressions and have not been executed.

## `Path.Base.Util.isPlanarFace`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def isPlanarFace(shape):
```

isPlanarFace(shape) ... True if shape is a face lying in a plane.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Base/Util.py:307`. Decorators are copied as source expressions and have not been executed.

## `Path.Base.Util.jobHasRotaryMachine`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def jobHasRotaryMachine(job):
```

jobHasRotaryMachine(job) ... True if job's machine has rotary axes.

Work planes are available on every Job; this decides what a plane may be.
Without rotary axes a plane must be parallel to the table: a datum for
depths and a turned X, which any three-axis machine can cut. A tilted
plane needs rotary axes to point the tool along it.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Base/Util.py:312`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`Path.Base.Util._getProperty`. These are source internals unless an explicit export establishes otherwise.

