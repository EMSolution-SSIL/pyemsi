# Python source module `draftgeoutils.fillets`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftgeoutils/fillets.py`. Import path is source-routed; installed availability is unverified.

Provides various functions to work with fillets.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import math

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.fillets.math` -> `math`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/fillets.py:32`.

### import lazy_loader.lazy_loader as lz

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.fillets.lz` -> `lazy_loader.lazy_loader`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/fillets.py:33`.

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.fillets.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/fillets.py:35`.

### from draftgeoutils.general import precision

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.fillets.precision` -> `draftgeoutils.general.precision`.

[Source module `draftgeoutils.general`](../general/index.md).

Evidence: `src/Mod/Draft/draftgeoutils/fillets.py:37`.

### from draftgeoutils.arcs import arcFrom2Pts

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.fillets.arcFrom2Pts` -> `draftgeoutils.arcs.arcFrom2Pts`.

[Source module `draftgeoutils.arcs`](../arcs/index.md).

Evidence: `src/Mod/Draft/draftgeoutils/fillets.py:38`.

### from draftgeoutils.wires import isReallyClosed

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.fillets.isReallyClosed` -> `draftgeoutils.wires.isReallyClosed`.

[Source module `draftgeoutils.wires`](../wires/index.md).

Evidence: `src/Mod/Draft/draftgeoutils/fillets.py:39`.

## `draftgeoutils.fillets.fillet`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def fillet(lEdges, r, chamfer=False):
```

Return a list of sorted edges describing a round corner.

Author: Jacques-Antoine Gaudin

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/fillets.py:48`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.fillets.filletWire`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def filletWire(aWire, r, chamfer=False):
```

Fillet each angle of a wire with r as radius.

If chamfer is true, a `chamfer` is made instead, and `r` is the
size of the chamfer.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/fillets.py:371`. Decorators are copied as source expressions and have not been executed.

