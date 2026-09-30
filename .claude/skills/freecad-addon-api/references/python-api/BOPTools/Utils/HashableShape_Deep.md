# `BOPTools.Utils.HashableShape_Deep`

[Source module](index.md)

```python
class HashableShape_Deep(object):
```

Similar to HashableShape, except that the things the shape is composed of are compared.

Example:
    >>> wire2 = Part.Wire(wire1.childShapes())
    >>> wire2.isSame(wire1)
    False # <--- the wire2 is a new wire, although made of edges of wire1
    >>> HashableShape_Deep(wire2) == HashableShape_Deep(wire1)
    True # <--- made of same set of elements

Evidence: `src/Mod/Part/BOPTools/Utils.py:45`. Source-defined class; runtime behavior and support status unverified.

## `BOPTools.Utils.HashableShape_Deep.__init__`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def __init__(self, shape):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Part/BOPTools/Utils.py:56`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`BOPTools.Utils.HashableShape_Deep.__eq__`, `BOPTools.Utils.HashableShape_Deep.__hash__`. These are source internals unless an explicit export establishes otherwise.

