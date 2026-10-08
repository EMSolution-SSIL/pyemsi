# `ArchSql.ReferenceExtractor`

[Source module](index.md)

```python
class ReferenceExtractor:
```

Represents a request to extract a value from an object, handling nesting.

This class is the core of property access in the SQL engine. It can represent a simple property
access (e.g., `Label`), a nested property access using a dot-notation string (e.g.,
`Shape.Volume`), or a chained access on the result of another function (e.g.,
`PARENT(*).Label`).

The chained access is achieved by making the class recursive. The `base` attribute can hold
another extractor object (like `ParentFunction` or another `ReferenceExtractor`), which is
evaluated first to get an intermediate object from which the final `value` is extracted.

Evidence: `src/Mod/BIM/ArchSql.py:1594`. Source-defined class; runtime behavior and support status unverified.

## `ArchSql.ReferenceExtractor.__init__`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def __init__(self, value, base=None):
```

Initializes the ReferenceExtractor.

Parameters
----------
value : str
    The name of the property to extract (e.g., 'Label', 'Shape.Volume').
base : object, optional
    Another logical extractor object that, when evaluated, provides the base object for this
    extraction. If None, the property is extracted from the main object of the current row.
    Defaults to None.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchSql.py:1608`. Decorators are copied as source expressions and have not been executed.

## `ArchSql.ReferenceExtractor.get_value`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_value(self, obj):
```

Extracts and returns the final property value from a given object.

If `self.base` is set, this method first recursively calls `get_value` on the base to
resolve the intermediate object (e.g., executing `PARENT(*)` to get the parent). It then
extracts the property specified by `self.value` from that intermediate object.

If `self.base` is None, it directly extracts the property from the provided row object
`obj`.

Parameters
----------
obj : FreeCAD.DocumentObject
    The document object for the current row being processed.

Returns
-------
any
    The value of the requested property, or None if any part of the access chain is invalid
    or returns None.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchSql.py:1624`. Decorators are copied as source expressions and have not been executed.

## `ArchSql.ReferenceExtractor.get_objects`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_objects(self, source_objects=None):
```

Provides the interface for the FromClause to get the initial set of objects to query.

This method is only intended to be used for the special case of `FROM document`, where it
returns all objects in the active document. In all other contexts, it returns an empty list.

Returns
-------
list of FreeCAD.DocumentObject
    A list of all objects in the active document if `self.value` is 'document', otherwise an
    empty list.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/BIM/ArchSql.py:1657`. Decorators are copied as source expressions and have not been executed.

