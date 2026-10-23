# `ArchSql.ArithmeticOperation`

[Source module](index.md)

```python
class ArithmeticOperation:
```

Represents a recursive arithmetic operation (e.g., a + (b * c)).

Evidence: `src/Mod/BIM/ArchSql.py:1547`. Source-defined class; runtime behavior and support status unverified.

## `ArchSql.ArithmeticOperation.__init__`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def __init__(self, left, op, right):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchSql.py:1550`. Decorators are copied as source expressions and have not been executed.

## `ArchSql.ArithmeticOperation.get_value`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_value(self, obj):
```

Recursively evaluates the calculation tree, propagating None.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchSql.py:1572`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`ArchSql.ArithmeticOperation._normalize_value`. These are source internals unless an explicit export establishes otherwise.

