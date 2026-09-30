# Python source module `ArchWindowPresets`

[Python catalogue](../index.md)

Evidence: `src/Mod/BIM/ArchWindowPresets.py`. Import path is source-routed; installed availability is unverified.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import FreeCAD

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `ArchWindowPresets.FreeCAD` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/BIM/ArchWindowPresets.py:25`.

### from FreeCAD import Vector

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `ArchWindowPresets.Vector` -> `FreeCAD.Vector`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/BIM/ArchWindowPresets.py:27`.

### from draftutils.translate import translate

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `ArchWindowPresets.translate` -> `draftutils.translate.translate`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/BIM/ArchWindowPresets.py:28`.

## `ArchWindowPresets.WindowPresets`

Status: source-defined name; no independently verified stability/export guarantee.

```python
WindowPresets = ['Fixed', 'Open 1-pane', 'Open 2-pane', 'Sash 2-pane', 'Sliding 2-pane', 'Simple door', 'Sliding door', 'Glass door', 'Sliding 4-pane', 'Awning', 'Opening only']
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/BIM/ArchWindowPresets.py:30`. Decorators are copied as source expressions and have not been executed.

## `ArchWindowPresets.makeWindowPreset`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeWindowPreset(windowtype, width, height, h1, h2, h3, w1, w2, o1, o2, placement=None):
```

makeWindowPreset(windowtype,width,height,h1,h2,h3,w1,w2,o1,o2,[placement]): makes a
window object based on the given data. windowtype must be one of the names
defined in Arch.WindowPresets

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchWindowPresets.py:45`. Decorators are copied as source expressions and have not been executed.

