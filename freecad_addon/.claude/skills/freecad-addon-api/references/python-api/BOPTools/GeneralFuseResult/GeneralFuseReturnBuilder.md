# `BOPTools.GeneralFuseResult.GeneralFuseReturnBuilder`

[Source module](index.md)

```python
class GeneralFuseReturnBuilder(FrozenClass):
```

GeneralFuseReturnBuilder: utility class used by splitAggregates to build fake return of generalFuse, for re-parsing.

Evidence: `src/Mod/Part/BOPTools/GeneralFuseResult.py:396`. Source-defined class; runtime behavior and support status unverified.

## `BOPTools.GeneralFuseResult.GeneralFuseReturnBuilder.__init__`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def __init__(self, source_shapes):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/GeneralFuseResult.py:412`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.GeneralFuseResult.GeneralFuseReturnBuilder.addPiece`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def addPiece(self, piece_shape, source_shape_index_list):
```

addPiece(piece_shape, source_shape_index_list): adds a piece. If the piece
already exists, returns False, and only updates source<->piece map.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/GeneralFuseResult.py:417`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.GeneralFuseResult.GeneralFuseReturnBuilder.replacePiece`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def replacePiece(self, piece_index, new_shape):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/GeneralFuseResult.py:446`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.GeneralFuseResult.GeneralFuseReturnBuilder.getGFReturn`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getGFReturn(self):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/GeneralFuseResult.py:451`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`BOPTools.GeneralFuseResult.GeneralFuseReturnBuilder.__define_attributes`. These are source internals unless an explicit export establishes otherwise.

