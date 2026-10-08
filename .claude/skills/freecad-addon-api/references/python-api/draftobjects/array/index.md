# Python source module `draftobjects.array`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftobjects/array.py`. Import path is source-routed; installed availability is unverified.

Provides the object code for the Array object.

The `Array` class currently handles three types of arrays,
orthogonal, polar, and circular. In the future, probably they should be
split in separate classes so that they are easier to manage.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import math

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftobjects.array.math` -> `math`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftobjects/array.py:39`.

### from PySide.QtCore import QT_TRANSLATE_NOOP

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftobjects.array.QT_TRANSLATE_NOOP` -> `PySide.QtCore.QT_TRANSLATE_NOOP`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftobjects/array.py:40`.

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftobjects.array.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftobjects/array.py:42`.

### import DraftVecUtils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftobjects.array.DraftVecUtils` -> `DraftVecUtils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftobjects/array.py:43`.

### from draftutils.messages import _log

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftobjects.array._log` -> `draftutils.messages._log`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftobjects/array.py:45`.

### from draftobjects.draftlink import DraftLink

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftobjects.array.DraftLink` -> `draftobjects.draftlink.DraftLink`.

[Source module `draftobjects.draftlink`](../draftlink/index.md).

Evidence: `src/Mod/Draft/draftobjects/array.py:47`.

## Classes

- [draftobjects.array.Array](Array.md)

## `draftobjects.array.rect_placements`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def rect_placements(base_placement, xvector, yvector, zvector, xnum, ynum, znum):
```

Determine the placements where the rectangular copies will be.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/array.py:468`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.array.polar_placements`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def polar_placements(base_placement, center, angle, number, axis, axisvector):
```

Determine the placements where the polar copies will be.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/array.py:501`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.array.circ_placements`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def circ_placements(base_placement, r_distance, tan_distance, axis, center, circle_number, symmetry):
```

Determine the placements where the circular copies will be.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/array.py:526`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`draftobjects.array._Array`. These are source internals unless an explicit export establishes otherwise.

