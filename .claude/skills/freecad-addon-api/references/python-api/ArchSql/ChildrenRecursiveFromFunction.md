# `ArchSql.ChildrenRecursiveFromFunction`

[Source module](index.md)

```python
@register_from_function(name='CHILDREN_RECURSIVE', category=QT_TRANSLATE_NOOP('ArchSql', 'Hierarchical'), signature='CHILDREN_RECURSIVE(subquery, max_depth=15)', description=QT_TRANSLATE_NOOP('ArchSql', 'Selects all descendant objects of a given set, traversing the full hierarchy.'), snippet="SELECT * FROM CHILDREN_RECURSIVE(SELECT * FROM document WHERE Label = 'My Building')")
class ChildrenRecursiveFromFunction(FromFunctionBase):
```

Implements the CHILDREN_RECURSIVE() function.

Evidence: `src/Mod/BIM/ArchSql.py:880`. Source-defined class; runtime behavior and support status unverified.

## `ArchSql.ChildrenRecursiveFromFunction.get_objects`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_objects(self, source_objects=None):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchSql.py:883`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`ArchSql.ChildrenRecursiveFromFunction._get_parent_objects_from_subquery`. These are source internals unless an explicit export establishes otherwise.

