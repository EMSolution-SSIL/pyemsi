# Python source module `draftobjects.label`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftobjects/label.py`. Import path is source-routed; installed availability is unverified.

Provides the object code for the Label object.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### from PySide.QtCore import QT_TRANSLATE_NOOP

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftobjects.label.QT_TRANSLATE_NOOP` -> `PySide.QtCore.QT_TRANSLATE_NOOP`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftobjects/label.py:35`.

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftobjects.label.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftobjects/label.py:37`.

### from FreeCAD import Units as U

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftobjects.label.U` -> `FreeCAD.Units`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftobjects/label.py:38`.

### from draftobjects.draft_annotation import DraftAnnotation

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftobjects.label.DraftAnnotation` -> `draftobjects.draft_annotation.DraftAnnotation`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftobjects/label.py:39`.

### from draftutils import gui_utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftobjects.label.gui_utils` -> `draftutils.gui_utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftobjects/label.py:40`.

### from draftutils.messages import _log

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftobjects.label._log` -> `draftutils.messages._log`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftobjects/label.py:41`.

### from draftutils.translate import translate

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftobjects.label.translate` -> `draftutils.translate.translate`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftobjects/label.py:42`.

## Classes

- [draftobjects.label.Label](Label.md)

## `draftobjects.label.DraftLabel`

Status: source-defined name; no independently verified stability/export guarantee.

```python
DraftLabel = Label
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Evidence: `src/Mod/Draft/draftobjects/label.py:320`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.label.get_label_types`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_label_types():
```

No source docstring; inspect implementation and callers for purpose, return values and side effects.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/label.py:323`. Decorators are copied as source expressions and have not been executed.

## `draftobjects.label.return_info`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def return_info(target, typ, subelement=None):
```

Return the text list from the target and the given type.

Parameters
----------
target: Part::Feature
    The object targeted by the label.

typ: str
    It is the type of information that we want to extract.

subelement: str, optional
    A string indicating a subelement of the `target`;
    it could be `'VertexN'`, `'EdgeN'`, or `'FaceN'`,
    where `'N'` is a number that starts from `1` up to the maximum
    number of subelements in that target.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftobjects/label.py:342`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`draftobjects.label._get_name`, `draftobjects.label._get_label`, `draftobjects.label._get_tag`, `draftobjects.label._get_material`, `draftobjects.label._get_position`, `draftobjects.label._get_length`, `draftobjects.label._get_area`, `draftobjects.label._get_volume`. These are source internals unless an explicit export establishes otherwise.

