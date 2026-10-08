# Python source module `freecad`

[Python catalogue](../index.md)

Evidence: `src/Ext/freecad/__init__.py.template`. Import path is source-routed; installed availability is unverified.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import FreeCAD as app

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `try block at line 3`.

Bound source name `freecad.app` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Ext/freecad/__init__.py.template:4`.

### import sys as _sys

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `except ModuleNotFoundError at line 5`.

Bound source name `freecad._sys` -> `sys`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Ext/freecad/__init__.py.template:8`.

### import os as _os

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `except ModuleNotFoundError at line 5`.

Bound source name `freecad._os` -> `os`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Ext/freecad/__init__.py.template:9`.

### import FreeCAD as app

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `except ModuleNotFoundError at line 5`.

Bound source name `freecad.app` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Ext/freecad/__init__.py.template:22`.

### from pkgutil import extend_path as _extend_path

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `freecad._extend_path` -> `pkgutil.extend_path`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Ext/freecad/__init__.py.template:31`.

## Internal definitions not expanded

`freecad._path_to_freecad_libdir`, `freecad.__path__`. These are source internals unless an explicit export establishes otherwise.

