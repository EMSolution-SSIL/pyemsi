# `ArchSql.MinFunction`

[Source module](index.md)

```python
@register_select_function(name='MIN', category=QT_TRANSLATE_NOOP('ArchSql', 'Aggregate'), signature='MIN(property)', description=QT_TRANSLATE_NOOP('ArchSql', 'Finds the minimum value of a property.'), snippet="SELECT MIN(Length) FROM document WHERE IfcType = 'Wall'")
class MinFunction(AggregateFunction):
```

Implements the MIN() aggregate function.

Evidence: `src/Mod/BIM/ArchSql.py:609`. Source-defined class; runtime behavior and support status unverified.

