# `ArchSql.FunctionRegistry`

[Source module](index.md)

```python
class FunctionRegistry:
```

A simple class to manage the registration of SQL functions.

Evidence: `src/Mod/BIM/ArchSql.py:500`. Source-defined class; runtime behavior and support status unverified.

## `ArchSql.FunctionRegistry.__init__`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def __init__(self):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchSql.py:503`. Decorators are copied as source expressions and have not been executed.

## `ArchSql.FunctionRegistry.register`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def register(self, name, function_class, category, signature, description, snippet=''):
```

Registers a class to handle a function with the given name.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchSql.py:506`. Decorators are copied as source expressions and have not been executed.

## `ArchSql.FunctionRegistry.get_class`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_class(self, name):
```

Retrieves the class registered for a given function name.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchSql.py:516`. Decorators are copied as source expressions and have not been executed.

