# `ArchSql.FunctionBase`

[Source module](index.md)

```python
class FunctionBase:
```

A base class for non-aggregate functions like TYPE, CONCAT, etc.

Evidence: `src/Mod/BIM/ArchSql.py:628`. Source-defined class; runtime behavior and support status unverified.

## `ArchSql.FunctionBase.__init__`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def __init__(self, function_name, arg_extractors):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchSql.py:631`. Decorators are copied as source expressions and have not been executed.

## `ArchSql.FunctionBase.get_value`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_value(self, obj):
```

Calculates the function's value. This is the entry point.
It determines the object to operate on (from the chain, or the row object)
and then calls the specific implementation.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchSql.py:637`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`ArchSql.FunctionBase._execute_function`. These are source internals unless an explicit export establishes otherwise.

