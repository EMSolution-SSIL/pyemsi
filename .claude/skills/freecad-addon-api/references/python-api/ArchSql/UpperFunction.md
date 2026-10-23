# `ArchSql.UpperFunction`

[Source module](index.md)

```python
@register_select_function(name='UPPER', category=QT_TRANSLATE_NOOP('ArchSql', 'String'), signature='UPPER(property)', description=QT_TRANSLATE_NOOP('ArchSql', 'Converts text to uppercase.'), snippet="SELECT Label FROM document WHERE UPPER(IfcType) = 'WALL'")
class UpperFunction(FunctionBase):
```

Implements the UPPER() string function.

Evidence: `src/Mod/BIM/ArchSql.py:708`. Source-defined class; runtime behavior and support status unverified.

## `ArchSql.UpperFunction.__init__`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def __init__(self, function_name, arg_extractors):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchSql.py:711`. Decorators are copied as source expressions and have not been executed.

## `ArchSql.UpperFunction.get_value`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_value(self, obj):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchSql.py:716`. Decorators are copied as source expressions and have not been executed.

