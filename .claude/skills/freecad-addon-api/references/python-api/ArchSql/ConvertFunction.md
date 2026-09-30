# `ArchSql.ConvertFunction`

[Source module](index.md)

```python
@register_select_function(name='CONVERT', category=QT_TRANSLATE_NOOP('ArchSql', 'Utility'), signature="CONVERT(quantity, 'unit')", description=QT_TRANSLATE_NOOP('ArchSql', "Converts a Quantity to a different unit (e.g., CONVERT(Length, 'm'))."), snippet="SELECT CONVERT(Length, 'm') AS LengthInMeters FROM document")
class ConvertFunction(FunctionBase):
```

Implements the CONVERT(Quantity, 'unit') function.

Evidence: `src/Mod/BIM/ArchSql.py:753`. Source-defined class; runtime behavior and support status unverified.

## `ArchSql.ConvertFunction.__init__`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def __init__(self, function_name, arg_extractors):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchSql.py:756`. Decorators are copied as source expressions and have not been executed.

## `ArchSql.ConvertFunction.get_value`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_value(self, obj):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchSql.py:763`. Decorators are copied as source expressions and have not been executed.

