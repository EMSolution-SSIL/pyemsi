# `Path.Tool.Controller.ToolController`

[Source module](index.md)

```python
class ToolController:
```

No class source docstring.

Evidence: `src/Mod/CAM/Path/Tool/Controller.py:137`. Source-defined class; runtime behavior and support status unverified.

## `Path.Tool.Controller.ToolController.__init__`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def __init__(self, obj, createTool=True):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Tool/Controller.py:138`. Decorators are copied as source expressions and have not been executed.

## `Path.Tool.Controller.ToolController.propertyEnumerations`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@classmethod
def propertyEnumerations(cls, dataType='data'):
```

helixOpPropertyEnumerations(dataType="data")... return property enumeration lists of specified dataType.
Args:
    dataType = 'data', 'raw', 'translated'
Notes:
'data' is list of internal string literals used in code
'raw' is list of (translated_text, data_string) tuples
'translated' is list of translated string literals

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Tool/Controller.py:228`. Decorators are copied as source expressions and have not been executed.

## `Path.Tool.Controller.ToolController.onDocumentRestored`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def onDocumentRestored(self, obj):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Tool/Controller.py:261`. Decorators are copied as source expressions and have not been executed.

## `Path.Tool.Controller.ToolController.onDelete`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def onDelete(self, obj, arg2=None):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Tool/Controller.py:325`. Decorators are copied as source expressions and have not been executed.

## `Path.Tool.Controller.ToolController.setFromTemplate`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def setFromTemplate(self, obj, template):
```

setFromTemplate(obj, xmlItem) ... extract properties from xmlItem
and assign to receiver.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Tool/Controller.py:330`. Decorators are copied as source expressions and have not been executed.

## `Path.Tool.Controller.ToolController.templateAttrs`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def templateAttrs(self, obj):
```

templateAttrs(obj) ... answer a dictionary with all properties that should be stored for a template.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Tool/Controller.py:405`. Decorators are copied as source expressions and have not been executed.

## `Path.Tool.Controller.ToolController.execute`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def execute(self, obj):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Tool/Controller.py:436`. Decorators are copied as source expressions and have not been executed.

## `Path.Tool.Controller.ToolController.getTool`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def getTool(self, obj):
```

returns the tool associated with this tool controller

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Tool/Controller.py:453`. Decorators are copied as source expressions and have not been executed.

## `Path.Tool.Controller.ToolController.ensureToolBit`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def ensureToolBit(self, obj):
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/CAM/Path/Tool/Controller.py:458`. Decorators are copied as source expressions and have not been executed.

