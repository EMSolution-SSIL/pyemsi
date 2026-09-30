# `ArchSql.SumFunction`

[Source module](index.md)

```python
@register_select_function(name='SUM', category=QT_TRANSLATE_NOOP('ArchSql', 'Aggregate'), signature='SUM(property)', description=QT_TRANSLATE_NOOP('ArchSql', 'Calculates the sum of a numerical property.'), snippet="SELECT SUM(Area) FROM document WHERE IfcType = 'Space'")
class SumFunction(AggregateFunction):
```

Implements the SUM() aggregate function.

Evidence: `src/Mod/BIM/ArchSql.py:596`. Source-defined class; runtime behavior and support status unverified.

