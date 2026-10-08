# Python source module `BOPTools.Utils`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Part/BOPTools/Utils.py`. Import path is source-routed; installed availability is unverified.

Literal `__all__`: not available; source names do not imply supported public API.

## Classes

- [BOPTools.Utils.HashableShape](HashableShape.md)
- [BOPTools.Utils.HashableShape_Deep](HashableShape_Deep.md)
- [BOPTools.Utils.FrozenClass](FrozenClass.md)

## `BOPTools.Utils.compoundLeaves`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def compoundLeaves(shape_or_compound):
```

compoundLeaves(shape_or_compound): extracts all non-compound shapes from a nested compound.
Note: shape_or_compound may be a non-compound; then, it is the only thing in the
returned list.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/Utils.py:74`. Decorators are copied as source expressions and have not been executed.

## `BOPTools.Utils.upgradeToAggregateIfNeeded`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def upgradeToAggregateIfNeeded(list_of_shapes, types=None):
```

upgradeToAggregateIfNeeded(list_of_shapes, types = None): upgrades non-aggregate type
shapes to aggregate-type shapes if the list has a mix of aggregate and non-aggregate
type shapes. Returns the new list. Recursively traverses into compounds.

aggregate shape types are Wire, Shell, CompSolid
non-aggregate shape types are Vertex, Edge, Face, Solid
Compounds are something special: they are recursively traversed to upgrade the
contained shapes.

Examples:
list_of_shapes contains only faces -> nothing happens
list_of_shapes contains faces and shells -> faces are converted to shells

'types' argument is needed for recursive traversal. Do not supply.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/Utils.py:88`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`BOPTools.Utils.__title__`, `BOPTools.Utils.__author__`, `BOPTools.Utils.__url__`, `BOPTools.Utils.__doc__`. These are source internals unless an explicit export establishes otherwise.

