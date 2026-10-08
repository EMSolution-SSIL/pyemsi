# `ArchSql.ReportStatement`

[Source module](index.md)

```python
class ReportStatement:
```

A data model for a single statement within a BIM Report.

This class encapsulates all the information required to execute and present
a single query. It holds the SQL string itself, options for how its
results should be formatted in the final spreadsheet, and the crucial flag
that controls whether it participates in a pipeline.

Instances of this class are created and managed by the ReportTaskPanel UI
and are passed as a list to the `execute_pipeline` engine function. The
class includes methods for serialization to and from a dictionary format,
allowing it to be persisted within a FreeCAD document object.

Parameters
----------
description : str, optional
    A user-defined description for the statement. This is shown in the UI
    and can optionally be used as a section header in the spreadsheet.
query_string : str, optional
    The SQL query to be executed for this statement.
use_description_as_header : bool, optional
    If True, the `description` will be written as a merged header row
    before the statement's results in the spreadsheet. Defaults to False.
include_column_names : bool, optional
    If True, the column names from the SQL query (e.g., 'Label', 'Area')
    will be included as a header row for this statement's results.
    Defaults to True.
add_empty_row_after : bool, optional
    If True, an empty row will be inserted after this statement's results
    to provide visual spacing in the report. Defaults to False.
print_results_in_bold : bool, optional
    If True, the data cells for this statement's results will be formatted
    with a bold font for emphasis. Defaults to False.
is_pipelined : bool, optional
    If True, this statement will use the resulting objects from the
    previous statement as its data source instead of the entire document.
    This is the flag that enables pipeline functionality. Defaults to False.

Attributes
----------
_validation_status : str
    A transient (not saved) string indicating the validation state for the
    UI (e.g., "OK", "ERROR").
_validation_message : str
    A transient (not saved) user-facing message corresponding to the
    validation status.
_validation_count : int
    A transient (not saved) count of objects found during validation.

Evidence: `src/Mod/BIM/ArchSql.py:2182`. Source-defined class; runtime behavior and support status unverified.

## `ArchSql.ReportStatement.__init__`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def __init__(self, description='', query_string='', use_description_as_header=False, include_column_names=True, add_empty_row_after=False, print_results_in_bold=False, is_pipelined=False):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchSql.py:2232`. Decorators are copied as source expressions and have not been executed.

## `ArchSql.ReportStatement.dumps`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def dumps(self):
```

Returns the internal state for serialization.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchSql.py:2257`. Decorators are copied as source expressions and have not been executed.

## `ArchSql.ReportStatement.loads`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def loads(self, state):
```

Restores the internal state from serialized data.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchSql.py:2269`. Decorators are copied as source expressions and have not been executed.

## `ArchSql.ReportStatement.validate_and_update_status`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def validate_and_update_status(self, all_statements=None, index=None):
```

Runs validation for this statement's query and updates its internal status.

When ``all_statements`` and ``index`` are provided, the pipeline source objects are computed
automatically for pipelined statements.

Parameters
----------
all_statements : list of ReportStatement, optional
    The full ordered list of statements in the report.
index : int, optional
    The position of this statement within ``all_statements``.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchSql.py:2284`. Decorators are copied as source expressions and have not been executed.

