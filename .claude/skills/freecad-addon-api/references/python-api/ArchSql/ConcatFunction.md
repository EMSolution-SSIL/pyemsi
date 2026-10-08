# `ArchSql.ConcatFunction`

[Source module](index.md)

```python
@register_select_function(name='CONCAT', category=QT_TRANSLATE_NOOP('ArchSql', 'String'), signature='CONCAT(value1, value2, ...)', description=QT_TRANSLATE_NOOP('ArchSql', 'Joins multiple strings and properties together.'), snippet="SELECT CONCAT(Label, ': ', IfcType) FROM document")
class ConcatFunction(FunctionBase):
```

Implements the CONCAT() string function.

Evidence: `src/Mod/BIM/ArchSql.py:728`. Source-defined class; runtime behavior and support status unverified.

## `ArchSql.ConcatFunction.__init__`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def __init__(self, function_name, arg_extractors):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchSql.py:731`. Decorators are copied as source expressions and have not been executed.

## `ArchSql.ConcatFunction.get_value`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_value(self, obj):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchSql.py:736`. Decorators are copied as source expressions and have not been executed.

