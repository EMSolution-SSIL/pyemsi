# Python source module `Path.Log`

[Python catalogue](../../index.md)

Evidence: `src/Mod/CAM/Path/Log.py`. Import path is source-routed; installed availability is unverified.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import FreeCAD

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Path.Log.FreeCAD` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/CAM/Path/Log.py:24`.

### from freecad.deprecation import deprecated, _unwrap_deprecated_frame

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Path.Log.deprecated` -> `freecad.deprecation.deprecated`.

Bound source name `Path.Log._unwrap_deprecated_frame` -> `freecad.deprecation._unwrap_deprecated_frame`.

[Source module `freecad.deprecation`](../../freecad/deprecation/index.md).

Evidence: `src/Mod/CAM/Path/Log.py:25`.

### import inspect

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Path.Log.inspect` -> `inspect`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/CAM/Path/Log.py:26`.

### import os

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Path.Log.os` -> `os`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/CAM/Path/Log.py:27`.

## Classes

- [Path.Log.Level](Level.md)
- [Path.Log.ModuleLogger](ModuleLogger.md)

## `Path.Log.logToConsole`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def logToConsole(yes):
```

(boolean) - if set to True (default behaviour) log messages are printed to the console. Otherwise they are printed to stdout.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Log.py:53`. Decorators are copied as source expressions and have not been executed.

## `Path.Log.thisModule`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def thisModule():
```

returns the module id of the caller please use logger.getModule instead if possible

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Log.py:59`. Decorators are copied as source expressions and have not been executed.

## `Path.Log.getModuleLoggerWithLevelOrDebug`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getModuleLoggerWithLevelOrDebug(level, debug, module=None):
```

(level, debug, module=None)

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Log.py:193`. Decorators are copied as source expressions and have not been executed.

## `Path.Log.getModuleLogger`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getModuleLogger(module=None, withLevel=None, enableTracking=None):
```

(module=None, withLevel=None, enableTracking=None)

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Log.py:203`. Decorators are copied as source expressions and have not been executed.

## `Path.Log.trackAllModules`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def trackAllModules(boolean):
```

(boolean) - if True all modules will be tracked, otherwise tracking is up to the module setting.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Log.py:222`. Decorators are copied as source expressions and have not been executed.

## `Path.Log.untrackAllModules`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def untrackAllModules():
```

In addition to stop tracking all modules it also clears the tracking flag for all individual modules.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Log.py:228`. Decorators are copied as source expressions and have not been executed.

## `Path.Log.setLevel`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@deprecated(deprecated_in='26.3', removed_in='27.2', replacement='logger.setLevel')
def setLevel(level, module=None):
```

(level, module = None)

deprecated - use logger.setLevel instead

if no module is specified the default log level is set.
Otherwise the module specific log level is changed (use RESET to clear).

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Log.py:243`. Decorators are copied as source expressions and have not been executed.

## `Path.Log.getLevel`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@deprecated(deprecated_in='26.3', removed_in='27.2', replacement='logger.getLevel')
def getLevel(module=None):
```

(module = None) - return the global (None) or module specific log level.

deprecated - use logger.getLevel instead

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Log.py:265`. Decorators are copied as source expressions and have not been executed.

## `Path.Log.trackModule`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@deprecated(deprecated_in='26.3', removed_in='27.2', replacement='logger.enableTracking')
def trackModule(module=None):
```

(module = None) - start tracking given module, current module if not set.

deprecated - use logger.enableTracking instead

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Log.py:277`. Decorators are copied as source expressions and have not been executed.

## `Path.Log.untrackModule`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@deprecated(deprecated_in='26.3', removed_in='27.2', replacement='logger.disableTracking')
def untrackModule(module=None):
```

(module = None) - stop tracking given module, current module if not set.

deprecated - use logger.disableTracking instead

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Log.py:290`. Decorators are copied as source expressions and have not been executed.

## `Path.Log.debug`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@deprecated(deprecated_in='26.3', removed_in='27.2', replacement='logger.debug(format, *args)')
def debug(msg):
```

(msg)

deprecated - use logger.debug(format, *args) instead

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Log.py:307`. Decorators are copied as source expressions and have not been executed.

## `Path.Log.info`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@deprecated(deprecated_in='26.3', removed_in='27.2', replacement='logger.info(format, *args)')
def info(msg):
```

(msg)

deprecated - use logger.info(format, *args) instead

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Log.py:317`. Decorators are copied as source expressions and have not been executed.

## `Path.Log.notice`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@deprecated(deprecated_in='26.3', removed_in='27.2', replacement='logger.notice(format, *args)')
def notice(msg):
```

(msg)

deprecated - use logger.notice(format, *args) instead

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Log.py:326`. Decorators are copied as source expressions and have not been executed.

## `Path.Log.warning`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@deprecated(deprecated_in='26.3', removed_in='27.2', replacement='logger.warning(format, *args)')
def warning(msg):
```

(msg)

deprecated - use logger.warning(format, *args) instead

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Log.py:335`. Decorators are copied as source expressions and have not been executed.

## `Path.Log.error`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@deprecated(deprecated_in='26.3', removed_in='27.2', replacement='logger.error(format, *args)')
def error(msg):
```

(msg)

deprecated - use logger.error(format, *args) instead

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Log.py:344`. Decorators are copied as source expressions and have not been executed.

## `Path.Log.track`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@deprecated(deprecated_in='26.3', removed_in='27.2', replacement='logger.track(format, *args)')
def track(*args):
```

(*args)

deprecated - use logger.track(format, *args) instead

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Log.py:353`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`Path.Log._caller`, `Path.Log._defaultLogLevel`, `Path.Log._useConsole`, `Path.Log._trackAll`, `Path.Log._moduleLoggers`. These are source internals unless an explicit export establishes otherwise.

