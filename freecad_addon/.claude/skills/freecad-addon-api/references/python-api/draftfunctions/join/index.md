# Python source module `draftfunctions.join`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftfunctions/join.py`. Import path is source-routed; installed availability is unverified.

Provides functions to join wires together into a single wire.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.join.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/join.py:33`.

### import DraftVecUtils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftfunctions.join.DraftVecUtils` -> `DraftVecUtils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftfunctions/join.py:34`.

## `draftfunctions.join.join_wires`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def join_wires(wires, joinAttempts=0):
```

join_wires(objects): merges a set of wires where possible, if any of those
wires have a coincident start and end point

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/join.py:37`. Decorators are copied as source expressions and have not been executed.

## `draftfunctions.join.joinWires`

Status: source-defined name; no independently verified stability/export guarantee.

```python
joinWires = join_wires
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/Draft/draftfunctions/join.py:55`. Decorators are copied as source expressions and have not been executed.

## `draftfunctions.join.join_two_wires`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def join_two_wires(wire1, wire2):
```

join_two_wires(object, object): joins two wires if they share a common
point as a start or an end.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftfunctions/join.py:58`. Decorators are copied as source expressions and have not been executed.

## `draftfunctions.join.joinTwoWires`

Status: source-defined name; no independently verified stability/export guarantee.

```python
joinTwoWires = join_two_wires
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/Draft/draftfunctions/join.py:92`. Decorators are copied as source expressions and have not been executed.

