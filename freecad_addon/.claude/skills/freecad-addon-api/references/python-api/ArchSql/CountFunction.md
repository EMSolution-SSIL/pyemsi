# `ArchSql.CountFunction`

[Source module](index.md)

```python
@register_select_function(name='COUNT', category=QT_TRANSLATE_NOOP('ArchSql', 'Aggregate'), signature='COUNT(* | property)', description=QT_TRANSLATE_NOOP('ArchSql', 'Counts rows that match criteria.'), snippet="SELECT COUNT(*) FROM document WHERE IfcType = 'Space'")
class CountFunction(AggregateFunction):
```

Implements the COUNT() aggregate function.

Evidence: `src/Mod/BIM/ArchSql.py:583`. Source-defined class; runtime behavior and support status unverified.

