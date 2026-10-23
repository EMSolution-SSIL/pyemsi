# Python source module `draftfunctions.dxf`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftfunctions/dxf.py`. Import path is source-routed; installed availability is unverified.

Provides functions to return the DXF representation of various shapes.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import lazy_loader.lazy_loader as lz

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.dxf.lz` -> `lazy_loader.lazy_loader`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/dxf.py:31`.

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.dxf.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/dxf.py:33`.

### import DraftVecUtils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.dxf.DraftVecUtils` -> `DraftVecUtils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/dxf.py:34`.

### import WorkingPlane

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.dxf.WorkingPlane` -> `WorkingPlane`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/dxf.py:35`.

### from draftutils import utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.dxf.utils` -> `draftutils.utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/dxf.py:36`.

### from draftutils.messages import _wrn

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.dxf._wrn` -> `draftutils.messages._wrn`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/dxf.py:37`.

## `draftfunctions.dxf.get_dxf`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_dxf(obj, direction=None):
```

Return a DXF entity from the given object.

If direction is given, the object is projected in 2D.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/dxf.py:64`. Decorators are copied as source expressions and have not been executed.

## `draftfunctions.dxf.getDXF`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getDXF(obj, direction=None):
```

Return DXF string of the object. DEPRECATED. Use 'get_dxf'.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/dxf.py:130`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`draftfunctions.dxf._get_proj`. These are source internals unless an explicit export establishes otherwise.

