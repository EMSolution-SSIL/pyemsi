# `Path.Main.Job.ObjectJob`

[Source module](index.md)

```python
class ObjectJob:
```

No class source docstring.

Evidence: `src/Mod/CAM/Path/Main/Job.py:111`. Source-defined class; runtime behavior and support status unverified.

## `Path.Main.Job.ObjectJob.__init__`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def __init__(self, obj, models, templateFile=None):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Main/Job.py:112`. Decorators are copied as source expressions and have not been executed.

## `Path.Main.Job.ObjectJob.propertyEnumerations`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@classmethod
def propertyEnumerations(self, dataType='data'):
```

propertyEnumerations(dataType="data")... return property enumeration lists of specified dataType.
Args:
    dataType = 'data', 'raw', 'translated'
Notes:
'data' is list of internal string literals used in code
'raw' is list of (translated_text, data_string) tuples
'translated' is list of translated string literals

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Main/Job.py:266`. Decorators are copied as source expressions and have not been executed.

## `Path.Main.Job.ObjectJob.setupOperations`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def setupOperations(self, obj):
```

setupOperations(obj)... setup the Operations group for the Job object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Main/Job.py:304`. Decorators are copied as source expressions and have not been executed.

## `Path.Main.Job.ObjectJob.setupWorkplanes`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def setupWorkplanes(self, obj):
```

setupWorkplanes(obj) ... set up the Workplanes group for the Job.

Holds the named frames operations can share. A workplane is a plain
Part::LocalCoordinateSystem: it already carries an attachment to the
geometry it was derived from, the map modes that describe a plane from
a face or three points, an editable offset, and a placement that
recomputes when the model moves. None of that needs reimplementing
here.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Main/Job.py:318`. Decorators are copied as source expressions and have not been executed.

## `Path.Main.Job.ObjectJob.adoptOrphanWorkplanes`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def adoptOrphanWorkplanes(self, obj):
```

adoptOrphanWorkplanes(obj) ... file any work plane an operation links
to but the group does not hold.

An operation migrating from an older document may create its work
plane before the Job is far enough restored to have a group. Restore
order across objects is not guaranteed, so the Job picks them up.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Main/Job.py:344`. Decorators are copied as source expressions and have not been executed.

## `Path.Main.Job.ObjectJob.setupSetupSheet`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def setupSetupSheet(self, obj):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Main/Job.py:361`. Decorators are copied as source expressions and have not been executed.

## `Path.Main.Job.ObjectJob.setupBaseModel`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def setupBaseModel(self, obj, models=None):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Main/Job.py:380`. Decorators are copied as source expressions and have not been executed.

## `Path.Main.Job.ObjectJob.setupToolTable`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def setupToolTable(self, obj):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Main/Job.py:410`. Decorators are copied as source expressions and have not been executed.

## `Path.Main.Job.ObjectJob.setupStock`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def setupStock(self, obj):
```

setupStock(obj)... setup the Stock for the Job object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Main/Job.py:435`. Decorators are copied as source expressions and have not been executed.

## `Path.Main.Job.ObjectJob.removeBase`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def removeBase(self, obj, base, removeFromModel):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Main/Job.py:449`. Decorators are copied as source expressions and have not been executed.

## `Path.Main.Job.ObjectJob.modelBoundBox`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def modelBoundBox(self, obj):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Main/Job.py:456`. Decorators are copied as source expressions and have not been executed.

## `Path.Main.Job.ObjectJob.onDelete`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def onDelete(self, obj, arg2=None):
```

Called by the view provider, there doesn't seem to be a callback on the obj itself.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Main/Job.py:459`. Decorators are copied as source expressions and have not been executed.

## `Path.Main.Job.ObjectJob.fixupOperations`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def fixupOperations(self, obj):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Main/Job.py:530`. Decorators are copied as source expressions and have not been executed.

## `Path.Main.Job.ObjectJob.ensureMachineProperty`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def ensureMachineProperty(self, obj):
```

Ensure the Machine property exists as a String.
Migrates from Enumeration to String if needed (legacy documents).

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Main/Job.py:548`. Decorators are copied as source expressions and have not been executed.

## `Path.Main.Job.ObjectJob.onDocumentRestored`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def onDocumentRestored(self, obj):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Main/Job.py:569`. Decorators are copied as source expressions and have not been executed.

## `Path.Main.Job.ObjectJob.onChanged`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def onChanged(self, obj, prop):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Main/Job.py:685`. Decorators are copied as source expressions and have not been executed.

## `Path.Main.Job.ObjectJob.baseObject`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def baseObject(self, obj, base):
```

Return the base object, not its clone.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Main/Job.py:691`. Decorators are copied as source expressions and have not been executed.

## `Path.Main.Job.ObjectJob.baseObjects`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def baseObjects(self, obj):
```

Return the base objects, not their clones.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Main/Job.py:698`. Decorators are copied as source expressions and have not been executed.

## `Path.Main.Job.ObjectJob.resourceClone`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def resourceClone(self, obj, base):
```

resourceClone(obj, base) ... Return the resource clone for base if it exists.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Main/Job.py:702`. Decorators are copied as source expressions and have not been executed.

## `Path.Main.Job.ObjectJob.setFromTemplateFile`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def setFromTemplateFile(self, obj, template):
```

setFromTemplateFile(obj, template) ... extract the properties from the given template file and assign to receiver.
This will also create any TCs stored in the template.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Main/Job.py:711`. Decorators are copied as source expressions and have not been executed.

## `Path.Main.Job.ObjectJob.templateAttrs`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def templateAttrs(self, obj):
```

templateAttrs(obj) ... answer a dictionary with all properties of the receiver that should be stored in a template file.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Main/Job.py:782`. Decorators are copied as source expressions and have not been executed.

## `Path.Main.Job.ObjectJob.dumps`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def dumps(self):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Main/Job.py:809`. Decorators are copied as source expressions and have not been executed.

## `Path.Main.Job.ObjectJob.loads`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def loads(self, state):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Main/Job.py:812`. Decorators are copied as source expressions and have not been executed.

## `Path.Main.Job.ObjectJob.execute`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def execute(self, obj):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Main/Job.py:819`. Decorators are copied as source expressions and have not been executed.

## `Path.Main.Job.ObjectJob.getCycleTime`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getCycleTime(self):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Main/Job.py:829`. Decorators are copied as source expressions and have not been executed.

## `Path.Main.Job.ObjectJob.addOperation`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def addOperation(self, op, before=None, removeBefore=False):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Main/Job.py:841`. Decorators are copied as source expressions and have not been executed.

## `Path.Main.Job.ObjectJob.getMachine`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getMachine(self):
```

getMachine() ... returns an instantiated Machine object for this job.
Returns None if no machine is configured or if the machine cannot be loaded.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Main/Job.py:857`. Decorators are copied as source expressions and have not been executed.

## `Path.Main.Job.ObjectJob.nextToolNumber`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def nextToolNumber(self):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Main/Job.py:878`. Decorators are copied as source expressions and have not been executed.

## `Path.Main.Job.ObjectJob.addToolController`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def addToolController(self, tc):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Main/Job.py:886`. Decorators are copied as source expressions and have not been executed.

## `Path.Main.Job.ObjectJob.allOperations`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def allOperations(self):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Main/Job.py:909`. Decorators are copied as source expressions and have not been executed.

## `Path.Main.Job.ObjectJob.setCenterOfRotation`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def setCenterOfRotation(self, center):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Main/Job.py:929`. Decorators are copied as source expressions and have not been executed.

## `Path.Main.Job.ObjectJob.integrityCheck`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def integrityCheck(self, job):
```

integrityCheck(job)... Return True if job has all expected children objects.  Attempts to restore any missing children.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Main/Job.py:935`. Decorators are copied as source expressions and have not been executed.

## `Path.Main.Job.ObjectJob.baseCandidates`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@classmethod
def baseCandidates(cls):
```

Answer all objects in the current document which could serve as a Base for a job.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Main/Job.py:977`. Decorators are copied as source expressions and have not been executed.

## `Path.Main.Job.ObjectJob.isBaseCandidate`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@classmethod
def isBaseCandidate(cls, obj):
```

Answer true if the given object can be used as a Base for a job.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Main/Job.py:985`. Decorators are copied as source expressions and have not been executed.

