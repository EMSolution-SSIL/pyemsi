# `ArchSql.ChildrenFromFunction`

[Source module](index.md)

```python
@register_from_function(name='CHILDREN', category=QT_TRANSLATE_NOOP('ArchSql', 'Hierarchical'), signature='CHILDREN(subquery)', description=QT_TRANSLATE_NOOP('ArchSql', 'Selects direct child objects of a given parent set.'), snippet="SELECT * FROM CHILDREN(SELECT * FROM document WHERE Label = 'My Floor')")
class ChildrenFromFunction(FromFunctionBase):
```

Implements the CHILDREN() function.

Evidence: `src/Mod/BIM/ArchSql.py:848`. Source-defined class; runtime behavior and support status unverified.

## `ArchSql.ChildrenFromFunction.get_objects`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_objects(self, source_objects=None):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchSql.py:851`. Decorators are copied as source expressions and have not been executed.

