# `ArchSql.ParentFunction`

[Source module](index.md)

```python
@register_select_function(name='PARENT', category=QT_TRANSLATE_NOOP('ArchSql', 'Hierarchical'), signature='PARENT(*)', description=QT_TRANSLATE_NOOP('ArchSql', 'Returns the immediate, architecturally significant parent of an object.'), snippet="SELECT Label, PARENT(*).Label AS Floor FROM document WHERE IfcType = 'Space'")
class ParentFunction(FunctionBase):
```

Implements the PARENT(*) function to find an object's container.

Evidence: `src/Mod/BIM/ArchSql.py:929`. Source-defined class; runtime behavior and support status unverified.

## `ArchSql.ParentFunction.__init__`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def __init__(self, function_name, arg_extractors):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchSql.py:932`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`ArchSql.ParentFunction._execute_function`. These are source internals unless an explicit export establishes otherwise.

