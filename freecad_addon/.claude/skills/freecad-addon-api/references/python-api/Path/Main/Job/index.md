# Python source module `Path.Main.Job`

[Python catalogue](../../../index.md)

Evidence: `src/Mod/CAM/Path/Main/Job.py`. Import path is source-routed; installed availability is unverified.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### from Path.Op.Util import getCycleTimeEstimate

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Path.Main.Job.getCycleTimeEstimate` -> `Path.Op.Util.getCycleTimeEstimate`.

[Source module `Path.Op.Util`](../../Op/Util/index.md).

Evidence: `src/Mod/CAM/Path/Main/Job.py:24`.

### from Path.Post.Processor import PostProcessorFactory

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Path.Main.Job.PostProcessorFactory` -> `Path.Post.Processor.PostProcessorFactory`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/CAM/Path/Main/Job.py:25`.

### from PySide import QtCore

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Path.Main.Job.QtCore` -> `PySide.QtCore`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/CAM/Path/Main/Job.py:26`.

### from PySide.QtCore import QT_TRANSLATE_NOOP

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Path.Main.Job.QT_TRANSLATE_NOOP` -> `PySide.QtCore.QT_TRANSLATE_NOOP`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/CAM/Path/Main/Job.py:27`.

### import FreeCAD

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Path.Main.Job.FreeCAD` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/CAM/Path/Main/Job.py:28`.

### import Path

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Path.Main.Job.Path` -> `Path`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/CAM/Path/Main/Job.py:29`.

### import Path.Base.SetupSheet as PathSetupSheet

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Path.Main.Job.PathSetupSheet` -> `Path.Base.SetupSheet`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/CAM/Path/Main/Job.py:30`.

### import Path.Base.Util as PathUtil

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Path.Main.Job.PathUtil` -> `Path.Base.Util`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/CAM/Path/Main/Job.py:31`.

### import Path.Main.Stock as PathStock

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Path.Main.Job.PathStock` -> `Path.Main.Stock`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/CAM/Path/Main/Job.py:32`.

### import Path.Tool.Controller as PathToolController

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Path.Main.Job.PathToolController` -> `Path.Tool.Controller`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/CAM/Path/Main/Job.py:33`.

### import json

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Path.Main.Job.json` -> `json`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/CAM/Path/Main/Job.py:34`.

### import time

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Path.Main.Job.time` -> `time`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/CAM/Path/Main/Job.py:35`.

### from lazy_loader.lazy_loader import LazyLoader

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Path.Main.Job.LazyLoader` -> `lazy_loader.lazy_loader.LazyLoader`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/CAM/Path/Main/Job.py:38`.

## Classes

- [Path.Main.Job.JobTemplate](JobTemplate.md)
- [Path.Main.Job.NotificationClass](NotificationClass.md)
- [Path.Main.Job.ObjectJob](ObjectJob.md)

## `Path.Main.Job.translate`

Status: source-defined name; no independently verified stability/export guarantee.

```python
translate = FreeCAD.Qt.translate
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/CAM/Path/Main/Job.py:49`. Decorators are copied as source expressions and have not been executed.

## `Path.Main.Job.isResourceClone`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def isResourceClone(obj, propLink, resourceName):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Main/Job.py:73`. Decorators are copied as source expressions and have not been executed.

## `Path.Main.Job.createResourceClone`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def createResourceClone(obj, orig, name, icon):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Main/Job.py:81`. Decorators are copied as source expressions and have not been executed.

## `Path.Main.Job.createModelResourceClone`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def createModelResourceClone(obj, orig):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Main/Job.py:100`. Decorators are copied as source expressions and have not been executed.

## `Path.Main.Job.Instances`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def Instances():
```

Instances() ... Return all Jobs in the current active document.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Main/Job.py:990`. Decorators are copied as source expressions and have not been executed.

## `Path.Main.Job.Create`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def Create(name, base, templateFile=None):
```

Create(name, base, templateFile=None) ... creates a new job and all it's resources.
If a template file is specified the new job is initialized with the values from the template.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Main/Job.py:1001`. Decorators are copied as source expressions and have not been executed.

