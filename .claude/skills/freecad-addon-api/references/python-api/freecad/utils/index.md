# Python source module `freecad.utils`

[Python catalogue](../../index.md)

Evidence: `src/Ext/freecad/utils.py`. Import path is source-routed; installed availability is unverified.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import os

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `freecad.utils.os` -> `os`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Ext/freecad/utils.py:26`.

### import platform

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `freecad.utils.platform` -> `platform`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Ext/freecad/utils.py:27`.

### import shutil

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `freecad.utils.shutil` -> `shutil`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Ext/freecad/utils.py:28`.

### import FreeCAD

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `freecad.utils.FreeCAD` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Ext/freecad/utils.py:30`.

## `freecad.utils.get_python_exe`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_python_exe() -> str:
```

Find Python. In preference order
A) The value of the BaseApp/Preferences/PythonConsole/PathToPythonExecutable user preference
B) The executable located in the same bin directory as FreeCAD and called "python3"
C) The executable located in the same bin directory as FreeCAD and called "python"
D) The result of a shutil search for your system's "python3" executable
E) The result of a shutil search for your system's "python" executable

Evidence: `src/Ext/freecad/utils.py:33`. Decorators are copied as source expressions and have not been executed.

