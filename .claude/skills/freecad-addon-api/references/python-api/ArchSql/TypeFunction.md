# `ArchSql.TypeFunction`

[Source module](index.md)

```python
@register_select_function(name='TYPE', category=QT_TRANSLATE_NOOP('ArchSql', 'Utility'), signature='TYPE(*)', description=QT_TRANSLATE_NOOP('ArchSql', "Returns the object's BIM type (e.g., 'Wall')."), snippet="SELECT Label FROM document WHERE TYPE(*) = 'Wall'")
class TypeFunction(FunctionBase):
```

Implements the TYPE() function.

Evidence: `src/Mod/BIM/ArchSql.py:668`. Source-defined class; runtime behavior and support status unverified.

## `ArchSql.TypeFunction.__init__`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def __init__(self, function_name, arg_extractors):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchSql.py:671`. Decorators are copied as source expressions and have not been executed.

## `ArchSql.TypeFunction.get_value`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_value(self, obj):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchSql.py:676`. Decorators are copied as source expressions and have not been executed.

