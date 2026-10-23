# `BOPTools.GeneralFuseResult.GeneralFuseResult`

[Source module](index.md)

```python
class GeneralFuseResult(FrozenClass):
```

class GeneralFuseResult: helper object for obtaining info from results of
    Part.Shape.generalFuse() method.

Usage:
def myCustomFusionRoutine(list_of_shapes):
    generalFuse_return = list_of_shapes[0].generalFuse(list_of_shapes[1:])
    ao = GeneralFuseResult(list_of_shapes, generalFuse_return)
    ... (use attributes and methods of ao) ...

Evidence: `src/Mod/Part/BOPTools/GeneralFuseResult.py:34`. Source-defined class; runtime behavior and support status unverified.

## `BOPTools.GeneralFuseResult.GeneralFuseResult.__init__`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def __init__(self, source_shapes, generalFuse_return):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/GeneralFuseResult.py:69`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.GeneralFuseResult.GeneralFuseResult.parse`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def parse(self):
```

Parses the result of generalFuse recorded into self.gfa_return. Recovers missing
information. Fills in data structures.

It is called automatically by class constructor.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/GeneralFuseResult.py:76`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.GeneralFuseResult.GeneralFuseResult.parse_elements`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def parse_elements(self):
```

Fills element-to-source map. Potentially slow, so separated from general parse.
Needed for splitAggregates; called automatically from splitAggregates.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/GeneralFuseResult.py:174`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.GeneralFuseResult.GeneralFuseResult.indexOfPiece`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def indexOfPiece(self, piece_shape):
```

indexOfPiece(piece_shape): returns index of piece_shape in list of pieces

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/GeneralFuseResult.py:190`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.GeneralFuseResult.GeneralFuseResult.indexOfSource`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def indexOfSource(self, source_shape):
```

indexOfSource(source_shape): returns index of source_shape in list of arguments

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/GeneralFuseResult.py:194`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.GeneralFuseResult.GeneralFuseResult.piecesFromSource`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def piecesFromSource(self, source_shape):
```

piecesFromSource(source_shape): returns list of pieces (shapes) that came from
given source shape.

Note: aggregate pieces (e.g. wire, shell, compound) always have only one source - the
shape they came directly from. Only after executing splitAggregates and
explodeCompounds the source lists become completely populated.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/GeneralFuseResult.py:198`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.GeneralFuseResult.GeneralFuseResult.sourcesOfPiece`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def sourcesOfPiece(self, piece_shape):
```

sourcesOfPiece(piece_shape): returns list of source shapes given piece came from.

Note: aggregate pieces (e.g. wire, shell, compound) always have only one source - the
shape they came directly from. Only after executing splitAggregates and
explodeCompounds the source lists become completely populated.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/GeneralFuseResult.py:209`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.GeneralFuseResult.GeneralFuseResult.largestOverlapCount`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def largestOverlapCount(self):
```

largestOverlapCount(self): returns the largest overlap count. For example, if three
spheres intersect and have some volume common to all three, largestOverlapCount
returns 3.

Note: the return value may be incorrect if some of the pieces are wires/shells/
compsolids/compounds. Please use explodeCompounds and splitAggregates before using this function.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/GeneralFuseResult.py:219`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.GeneralFuseResult.GeneralFuseResult.splitAggregates`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def splitAggregates(self, pieces_to_split=None):
```

splitAggregates(pieces_to_split = None): splits aggregate shapes (wires, shells,
compsolids) in pieces of GF result as cut by intersections. Also splits aggregates
inside compounds. After running this, 'self' is replaced with new data, where the
pieces_to_split are split.

'pieces_to_split': list of shapes (from self.pieces), that are to be processed. If
None, all pieces will be split if possible.

Notes:
* this routine is very important to functioning of Connect on shells and wires.
* Warning: convoluted and slow.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/GeneralFuseResult.py:230`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.GeneralFuseResult.GeneralFuseResult.makeSplitPieces`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def makeSplitPieces(self, shape):
```

makeSplitPieces(self, shape): splits a shell, wire or compsolid into pieces where
it intersects with other shapes.

Returns list of split pieces. If no splits were done, returns list containing the
original shape.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/GeneralFuseResult.py:316`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.GeneralFuseResult.GeneralFuseResult.explodeCompounds`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def explodeCompounds(self):
```

explodeCompounds(): if any of self.pieces is a compound, the compound is exploded.
After running this, 'self' is filled with new data, where pieces are updated to
contain the stuff extracted from compounds.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/GeneralFuseResult.py:367`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`BOPTools.GeneralFuseResult.GeneralFuseResult.__define_attributes`, `BOPTools.GeneralFuseResult.GeneralFuseResult._splitInCompound`. These are source internals unless an explicit export establishes otherwise.

