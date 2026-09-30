# `femtools.objecttools.ObjectTools`

[Source module](index.md)

```python
class ObjectTools(ABC):
```

Abstract base class for the work with solvers and meshers

Evidence: `src/Mod/Fem/femtools/objecttools.py:37`. Source-defined class; runtime behavior and support status unverified.

## `femtools.objecttools.ObjectTools.__init__`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def __init__(self, obj):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femtools/objecttools.py:40`. Decorators are copied as source expressions and have not been executed.

## `femtools.objecttools.ObjectTools.prepare`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@abstractmethod
def prepare(self):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femtools/objecttools.py:77`. Decorators are copied as source expressions and have not been executed.

## `femtools.objecttools.ObjectTools.compute`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@abstractmethod
def compute(self):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femtools/objecttools.py:81`. Decorators are copied as source expressions and have not been executed.

## `femtools.objecttools.ObjectTools.update_properties`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@abstractmethod
def update_properties(self):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femtools/objecttools.py:85`. Decorators are copied as source expressions and have not been executed.

## `femtools.objecttools.ObjectTools.run`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def run(self, blocking=False):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Fem/femtools/objecttools.py:88`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`femtools.objecttools.ObjectTools._create_working_directory`, `femtools.objecttools.ObjectTools._process_finished`. These are source internals unless an explicit export establishes otherwise.

