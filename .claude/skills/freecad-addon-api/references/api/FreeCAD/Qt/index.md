# `FreeCAD.Qt`

[Catalogue index](../../index.md)

Evidence: import-shaped public stub `FreeCAD/Qt.pyi`; generated binding/typing declarations, runtime unverified.

## Imports and aliases

These preserve stub type context and reexports. Imported typing helpers and underscored names are not a promise of supported runtime API.

```python
from __future__ import annotations
from typing import Any
from Base.Metadata import callback, module
from typing import TypeVar
```

## `FreeCAD.Qt._T`

```python
_T = TypeVar('_T')
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Evidence: public stub `FreeCAD/Qt.pyi` line(s) 8.

## `FreeCAD.Qt.QT_TRANSLATE_NOOP`

```python
def QT_TRANSLATE_NOOP(context: str, sourcetext: _T, /) -> _T:
```

Return one string unchanged while marking it for contextual translation.

Evidence: public stub `FreeCAD/Qt.pyi` line(s) 10.

## `FreeCAD.Qt.QT_TRANSLATE_NOOP3`

```python
def QT_TRANSLATE_NOOP3(context: str, sourcetext: _T, disambiguation: str, /) -> _T:
```

Return one string unchanged while marking it with disambiguation metadata.

Evidence: public stub `FreeCAD/Qt.pyi` line(s) 14.

## `FreeCAD.Qt.QT_TRANSLATE_NOOP_UTF8`

```python
def QT_TRANSLATE_NOOP_UTF8(context: str, sourcetext: _T, /) -> _T:
```

Return one UTF-8 string unchanged while marking it for contextual translation.

Evidence: public stub `FreeCAD/Qt.pyi` line(s) 18.

## `FreeCAD.Qt.QT_TR_NOOP`

```python
def QT_TR_NOOP(sourcetext: _T, /) -> _T:
```

Return one string unchanged while marking it for default-context translation.

Evidence: public stub `FreeCAD/Qt.pyi` line(s) 22.

## `FreeCAD.Qt.QT_TR_NOOP_UTF8`

```python
def QT_TR_NOOP_UTF8(sourcetext: _T, /) -> _T:
```

Return one UTF-8 string unchanged while marking it for default-context translation.

Evidence: public stub `FreeCAD/Qt.pyi` line(s) 26.

## `FreeCAD.Qt.installTranslator`

```python
def installTranslator(filename: str, /) -> bool:
```

Load and install one translator file.

Evidence: public stub `FreeCAD/Qt.pyi` line(s) 30.

## `FreeCAD.Qt.removeTranslators`

```python
def removeTranslators() -> bool:
```

Remove all translators that FreeCAD installed through this helper.

Evidence: public stub `FreeCAD/Qt.pyi` line(s) 34.

## `FreeCAD.Qt.translate`

```python
def translate(context: str, sourcetext: str, disambiguation: str | None=None, n: int=-1, /) -> str:
```

Translate one source string in a Qt translation context.

Installed translator files are searched from the most recently installed
translator back to the first installed translator.

Evidence: public stub `FreeCAD/Qt.pyi` line(s) 38.

