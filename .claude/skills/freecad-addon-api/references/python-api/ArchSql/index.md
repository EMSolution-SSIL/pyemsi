# Python source module `ArchSql`

[Python catalogue](../index.md)

Evidence: `src/Mod/BIM/ArchSql.py`. Import path is source-routed; installed availability is unverified.

Contains the SQL parsing and execution engine for BIM/Arch objects.

Literal `__all__`: `BimSqlSyntaxError`, `ReportStatement`, `SqlEngineError`, `count`, `getSqlApiDocumentation`, `getSqlKeywords`, `select`, `selectObjects`, `selectObjectsFromPipeline`.

## Imports, aliases and conditional reexports

### import FreeCAD

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `ArchSql.FreeCAD` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/BIM/ArchSql.py:13`.

### import re

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `ArchSql.re` -> `re`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/BIM/ArchSql.py:14`.

### from collections import deque

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `ArchSql.deque` -> `collections.deque`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/BIM/ArchSql.py:15`.

### from PySide import QtCore

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if FreeCAD.GuiUp`.

Bound source name `ArchSql.QtCore` -> `PySide.QtCore`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/BIM/ArchSql.py:19`.

### from generated_sql_parser import UnexpectedCharacters, UnexpectedEOF, UnexpectedToken, VisitError

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `ArchSql.UnexpectedCharacters` -> `generated_sql_parser.UnexpectedCharacters`.

Bound source name `ArchSql.UnexpectedEOF` -> `generated_sql_parser.UnexpectedEOF`.

Bound source name `ArchSql.UnexpectedToken` -> `generated_sql_parser.UnexpectedToken`.

Bound source name `ArchSql.VisitError` -> `generated_sql_parser.VisitError`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/BIM/ArchSql.py:39`.

### import generated_sql_parser

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `ArchSql.generated_sql_parser` -> `generated_sql_parser`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/BIM/ArchSql.py:40`.

### from typing import List, Tuple, Any, Optional

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `ArchSql.List` -> `typing.List`.

Bound source name `ArchSql.Tuple` -> `typing.Tuple`.

Bound source name `ArchSql.Any` -> `typing.Any`.

Bound source name `ArchSql.Optional` -> `typing.Optional`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/BIM/ArchSql.py:42`.

## Export declaration evidence

```python
__all__ = ['select', 'count', 'selectObjects', 'selectObjectsFromPipeline', 'getSqlKeywords', 'getSqlApiDocumentation', 'BimSqlSyntaxError', 'SqlEngineError', 'ReportStatement']
```

Evidence: `src/Mod/BIM/ArchSql.py:44`. Conditional/dynamic alternatives have not been evaluated.

## Classes

- [ArchSql.SqlEngineError](SqlEngineError.md)
- [ArchSql.BimSqlSyntaxError](BimSqlSyntaxError.md)
- [ArchSql.FunctionRegistry](FunctionRegistry.md)
- [ArchSql.AggregateFunction](AggregateFunction.md)
- [ArchSql.CountFunction](CountFunction.md)
- [ArchSql.SumFunction](SumFunction.md)
- [ArchSql.MinFunction](MinFunction.md)
- [ArchSql.MaxFunction](MaxFunction.md)
- [ArchSql.FunctionBase](FunctionBase.md)
- [ArchSql.TypeFunction](TypeFunction.md)
- [ArchSql.LowerFunction](LowerFunction.md)
- [ArchSql.UpperFunction](UpperFunction.md)
- [ArchSql.ConcatFunction](ConcatFunction.md)
- [ArchSql.ConvertFunction](ConvertFunction.md)
- [ArchSql.FromFunctionBase](FromFunctionBase.md)
- [ArchSql.ChildrenFromFunction](ChildrenFromFunction.md)
- [ArchSql.ChildrenRecursiveFromFunction](ChildrenRecursiveFromFunction.md)
- [ArchSql.ParentFunction](ParentFunction.md)
- [ArchSql.GroupByClause](GroupByClause.md)
- [ArchSql.OrderByClause](OrderByClause.md)
- [ArchSql.SelectStatement](SelectStatement.md)
- [ArchSql.FromClause](FromClause.md)
- [ArchSql.WhereClause](WhereClause.md)
- [ArchSql.BooleanExpression](BooleanExpression.md)
- [ArchSql.BooleanComparison](BooleanComparison.md)
- [ArchSql.InComparison](InComparison.md)
- [ArchSql.ArithmeticOperation](ArithmeticOperation.md)
- [ArchSql.ReferenceExtractor](ReferenceExtractor.md)
- [ArchSql.StaticExtractor](StaticExtractor.md)
- [ArchSql.SqlTransformerMixin](SqlTransformerMixin.md)
- [ArchSql.ReportStatement](ReportStatement.md)

## `ArchSql.translate`

Status: source-defined name; no independently verified stability/export guarantee.

Conditions: `if FreeCAD.GuiUp`.

```python
def translate(context, text, comment=None):
```

Wraps the Qt translation function.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchSql.py:21`. Decorators are copied as source expressions and have not been executed.

## `ArchSql.QT_TRANSLATE_NOOP`

Status: source-defined name; no independently verified stability/export guarantee.

Conditions: `if FreeCAD.GuiUp`.

```python
QT_TRANSLATE_NOOP = QtCore.QT_TRANSLATE_NOOP
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/BIM/ArchSql.py:27`. Decorators are copied as source expressions and have not been executed.

## `ArchSql.translate`

Status: source-defined name; no independently verified stability/export guarantee.

Conditions: `else of (FreeCAD.GuiUp)`.

```python
def translate(context, text, comment=None):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchSql.py:31`. Decorators are copied as source expressions and have not been executed.

## `ArchSql.QT_TRANSLATE_NOOP`

Status: source-defined name; no independently verified stability/export guarantee.

Conditions: `else of (FreeCAD.GuiUp)`.

```python
def QT_TRANSLATE_NOOP(context, text):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchSql.py:34`. Decorators are copied as source expressions and have not been executed.

## `ArchSql.debug_transformer_method`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def debug_transformer_method(func):
```

A decorator to add verbose logging to transformer methods for debugging.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchSql.py:76`. Decorators are copied as source expressions and have not been executed.

## `ArchSql.SELECT_STAR_HEADER`

Status: source-defined name; no independently verified stability/export guarantee.

```python
SELECT_STAR_HEADER = 'Object Label'
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/BIM/ArchSql.py:92`. Decorators are copied as source expressions and have not been executed.

## `ArchSql.register_select_function`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def register_select_function(name, category, signature, description, snippet=''):
```

A decorator that registers a class as a selectable SQL function.
The decorated class must be a subclass of FunctionBase or similar.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchSql.py:527`. Decorators are copied as source expressions and have not been executed.

## `ArchSql.register_from_function`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def register_from_function(name, category, signature, description, snippet=''):
```

A decorator that registers a class as a FROM clause SQL function.
The decorated class must be a subclass of FromFunctionBase.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchSql.py:540`. Decorators are copied as source expressions and have not been executed.

## `ArchSql.(_parser, _transformer, _FRIENDLY_TOKEN_NAMES)`

Status: source-defined name; no independently verified stability/export guarantee.

Conditions: `except Exception at line 2039`.

```python
_parser, _transformer, _FRIENDLY_TOKEN_NAMES = (None, None, {})
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/BIM/ArchSql.py:2040`. Decorators are copied as source expressions and have not been executed.

## `ArchSql.selectObjectsFromPipeline`

Status: listed in literal __all__.

```python
def selectObjectsFromPipeline(statements: list) -> list:
```

Executes a multi-statement pipeline and returns a final list of FreeCAD objects.

This is a high-level convenience function for scripting complex, multi-step
selections that are too difficult or cumbersome for a single SQL query.

Parameters
----------
statements : list of ArchReport.ReportStatement
    A configured list of statements defining the pipeline.

Returns
-------
list of FreeCAD.DocumentObject
    A list of the final FreeCAD.DocumentObject instances that result from
    the pipeline.

Evidence: `src/Mod/BIM/ArchSql.py:2332`. Decorators are copied as source expressions and have not been executed.

## `ArchSql.execute_pipeline`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def execute_pipeline(statements: List['ReportStatement']):
```

Executes a list of statements, handling chained data flow as a generator.

This function orchestrates a multi-step query. It yields the results of
each standalone statement or the final statement of a contiguous pipeline,
allowing the caller to handle presentation.

Parameters
----------
statements : list of ArchReport.ReportStatement
    A configured list of statements to execute.

Yields
------
tuple
    A tuple `(statement, headers, data_rows)` for each result block that
    should be outputted.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchSql.py:2365`. Decorators are copied as source expressions and have not been executed.

## `ArchSql.count`

Status: listed in literal __all__.

```python
def count(query_string: str, source_objects: Optional[List]=None) -> Tuple[int, Optional[str]]:
```

Executes a query and returns only the count of resulting rows.

This is a "safe" public API function intended for UI components like
live validation feedback. It catches all exceptions and returns a
consistent tuple, making it safe to call with incomplete user input.

Parameters
----------
query_string : str
    The raw SQL query string.
source_objects : list of FreeCAD.DocumentObject, optional
    If provided, the query count will run on this list of objects instead
    of the entire document. Defaults to None.

Returns
-------
Tuple[int, Optional[str]]
    A tuple `(count, error_string)`.
    On success, `count` is the number of rows and `error_string` is `None`.
    On failure, `count` is `-1` and `error_string` contains a user-friendly
    description of the error (e.g., "INCOMPLETE", "Syntax Error").

Evidence: `src/Mod/BIM/ArchSql.py:2426`. Decorators are copied as source expressions and have not been executed.

## `ArchSql.select`

Status: listed in literal __all__.

```python
def select(query_string: str) -> Tuple[List[str], List[List[Any]]]:
```

Executes a query and returns the full results.

This function implements a "Catch, Log, and Re-Raise" pattern. It is
safe in that it logs a detailed error to the console, but it is also
"unsafe" in that it re-raises the exception to signal the failure to
the calling function, which is responsible for handling it.

Returns
-------
Tuple[List[str], List[List[Any]]]
    A tuple `(headers, data_rows)`.

Raises
------
SqlEngineError
    Re-raises any SqlEngineError or BimSqlSyntaxError without logging it.
    The caller is responsible for logging and handling.

Evidence: `src/Mod/BIM/ArchSql.py:2468`. Decorators are copied as source expressions and have not been executed.

## `ArchSql.selectObjects`

Status: listed in literal __all__.

```python
def selectObjects(query_string: str) -> List['FreeCAD.DocumentObject']:
```

Selects objects from the active document using a SQL-like query.

This provides a declarative way to select BIM objects
based on their properties. This is a convenience function for scripting.

Parameters
----------
query_string : str
    The SQL query to execute. For example:
    'SELECT * FROM document WHERE IfcType = "Wall" AND Label LIKE "%exterior%"'

Returns
-------
list of App::DocumentObject
    A list of the FreeCAD document objects that match the query.
    Returns an empty list if the query is invalid or finds no objects.

Evidence: `src/Mod/BIM/ArchSql.py:2495`. Decorators are copied as source expressions and have not been executed.

## `ArchSql.getSqlKeywords`

Status: listed in literal __all__.

```python
def getSqlKeywords(kind='all') -> List[str]:
```

Returns a list of all keywords and function names for syntax highlighters.

This function provides the single source of truth for SQL syntax in the
BIM workbench. It dynamically introspects the initialized Lark parser and
the function registries. It can return different subsets of keywords
based on the `kind` parameter.

Parameters
----------
kind : str, optional
    Specifies the type of keyword list to return.
    - 'all': (Default) Returns all single keywords from the grammar.
    - 'no_space': Returns a list of keywords that should not have a
      trailing space in autocompletion (e.g., functions, modifiers).

Returns
-------
List[str]
    A sorted, unique list of keywords and function names (e.g.,
    ['SELECT', 'FROM', 'COUNT', 'CHILDREN', ...]). Returns an empty list
    if the engine failed to initialize.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchSql.py:2530`. Decorators are copied as source expressions and have not been executed.

## `ArchSql.getSqlApiDocumentation`

Status: listed in literal __all__.

```python
def getSqlApiDocumentation() -> dict:
```

Generates a structured dictionary describing the supported SQL dialect.

This function introspects the live engine configuration and performs
just-in-time translation of descriptive strings to ensure they appear
in the user's current language.

Returns
-------
dict
    A dictionary with keys 'clauses' and 'functions'. 'functions' is a
    dict of lists, categorized by function type.

Evidence: `src/Mod/BIM/ArchSql.py:2593`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`ArchSql.__all__`, `ArchSql._CUSTOM_FRIENDLY_TOKEN_NAMES`, `ArchSql._get_property`, `ArchSql._generate_friendly_token_names`, `ArchSql._map_results_to_objects`, `ArchSql._is_generic_group`, `ArchSql._get_bim_type`, `ArchSql._is_bim_group`, `ArchSql._get_direct_children`, `ArchSql._traverse_architectural_hierarchy`, `ArchSql._execute_pipeline_for_objects`, `ArchSql._initialize_engine`, `ArchSql._run_query`, `ArchSql._get_sql_function_names`. These are source internals unless an explicit export establishes otherwise.

