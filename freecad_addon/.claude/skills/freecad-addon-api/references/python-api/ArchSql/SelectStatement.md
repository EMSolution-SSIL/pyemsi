# `ArchSql.SelectStatement`

[Source module](index.md)

```python
class SelectStatement:
```

No class source docstring.

Evidence: `src/Mod/BIM/ArchSql.py:997`. Source-defined class; runtime behavior and support status unverified.

## `ArchSql.SelectStatement.__init__`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def __init__(self, columns_info, from_clause, where_clause, group_by_clause, order_by_clause):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchSql.py:998`. Decorators are copied as source expressions and have not been executed.

## `ArchSql.SelectStatement.execute`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def execute(self, all_objects):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchSql.py:1005`. Decorators are copied as source expressions and have not been executed.

## `ArchSql.SelectStatement.validate`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def validate(self):
```

Validates the select statement against SQL rules, such as those for GROUP BY.
Raises ValueError on failure with a user-friendly message.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchSql.py:1076`. Decorators are copied as source expressions and have not been executed.

## `ArchSql.SelectStatement.get_row_count`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_row_count(self, all_objects):
```

Calculates only the number of rows the query will produce, performing
the minimal amount of work necessary. This is used by Arch.count()
for a fast UI preview.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchSql.py:1292`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`ArchSql.SelectStatement._get_extractor_signature`, `ArchSql.SelectStatement._get_grouping_key`, `ArchSql.SelectStatement._execute_grouped_query`, `ArchSql.SelectStatement._execute_non_grouped_query`, `ArchSql.SelectStatement._get_grouped_data`, `ArchSql.SelectStatement._process_select_columns`, `ArchSql.SelectStatement._calculate_row_values`, `ArchSql.SelectStatement._calculate_aggregate`. These are source internals unless an explicit export establishes otherwise.

