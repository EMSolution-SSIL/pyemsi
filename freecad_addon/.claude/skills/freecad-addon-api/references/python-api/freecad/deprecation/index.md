# Python source module `freecad.deprecation`

[Python catalogue](../../index.md)

Evidence: `src/Ext/freecad/deprecation.py`. Import path is source-routed; installed availability is unverified.

Python API deprecation helpers.

Literal `__all__`: `deprecated`.

## Imports, aliases and conditional reexports

### from __future__ import annotations

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `freecad.deprecation.annotations` -> `__future__.annotations`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Ext/freecad/deprecation.py:5`.

### from collections.abc import Callable

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `freecad.deprecation.Callable` -> `collections.abc.Callable`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Ext/freecad/deprecation.py:7`.

### import re

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `freecad.deprecation.re` -> `re`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Ext/freecad/deprecation.py:8`.

### from types import CodeType, FrameType

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `freecad.deprecation.CodeType` -> `types.CodeType`.

Bound source name `freecad.deprecation.FrameType` -> `types.FrameType`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Ext/freecad/deprecation.py:9`.

### from typing import TypeVar

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `freecad.deprecation.TypeVar` -> `typing.TypeVar`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Ext/freecad/deprecation.py:10`.

### from typing_extensions import deprecated as _pep702_deprecated

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `freecad.deprecation._pep702_deprecated` -> `typing_extensions.deprecated`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Ext/freecad/deprecation.py:12`.

## Export declaration evidence

```python
__all__ = ('deprecated',)
```

Evidence: `src/Ext/freecad/deprecation.py:87`. Conditional/dynamic alternatives have not been evaluated.

## `freecad.deprecation.deprecated`

Status: listed in literal __all__.

```python
def deprecated(*, deprecated_in: str, removed_in: str, replacement: str | None=None, details: str | None=None) -> Callable[[_T], _T]:
```

Mark a Python API for removal in a future FreeCAD release.

Evidence: `src/Ext/freecad/deprecation.py:60`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`freecad.deprecation._T`, `freecad.deprecation._RELEASE_RE`, `freecad.deprecation._WRAPPER_CODES`, `freecad.deprecation._unwrap_deprecated_frame`, `freecad.deprecation._release_key`, `freecad.deprecation._validate_lifecycle`, `freecad.deprecation._message`, `freecad.deprecation.__all__`. These are source internals unless an explicit export establishes otherwise.

