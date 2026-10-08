# `ArchSql.MaxFunction`

[Source module](index.md)

```python
@register_select_function(name='MAX', category=QT_TRANSLATE_NOOP('ArchSql', 'Aggregate'), signature='MAX(property)', description=QT_TRANSLATE_NOOP('ArchSql', 'Finds the maximum value of a property.'), snippet="SELECT MAX(Height) FROM document WHERE IfcType = 'Wall'")
class MaxFunction(AggregateFunction):
```

Implements the MAX() aggregate function.

Evidence: `src/Mod/BIM/ArchSql.py:622`. Source-defined class; runtime behavior and support status unverified.

