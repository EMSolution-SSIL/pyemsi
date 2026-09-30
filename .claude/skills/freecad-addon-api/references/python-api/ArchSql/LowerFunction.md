# `ArchSql.LowerFunction`

[Source module](index.md)

```python
@register_select_function(name='LOWER', category=QT_TRANSLATE_NOOP('ArchSql', 'String'), signature='LOWER(property)', description=QT_TRANSLATE_NOOP('ArchSql', 'Converts text to lowercase.'), snippet="SELECT Label FROM document WHERE LOWER(Label) = 'exterior wall'")
class LowerFunction(FunctionBase):
```

Implements the LOWER() string function.

Evidence: `src/Mod/BIM/ArchSql.py:688`. Source-defined class; runtime behavior and support status unverified.

## `ArchSql.LowerFunction.__init__`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def __init__(self, function_name, arg_extractors):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchSql.py:691`. Decorators are copied as source expressions and have not been executed.

## `ArchSql.LowerFunction.get_value`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_value(self, obj):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchSql.py:696`. Decorators are copied as source expressions and have not been executed.

