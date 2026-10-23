# Python source module `draftmake.make_text`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftmake/make_text.py`. Import path is source-routed; installed availability is unverified.

Provides functions to create Text objects.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_text.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_text.py:35`.

### from draftobjects.text import Text

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_text.Text` -> `draftobjects.text.Text`.

[Source module `draftobjects.text`](../../draftobjects/text/index.md).

Evidence: `src/Mod/Draft/draftmake/make_text.py:36`.

### from draftutils import gui_utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_text.gui_utils` -> `draftutils.gui_utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_text.py:37`.

### from draftutils import utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_text.utils` -> `draftutils.utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_text.py:38`.

### from draftutils.messages import _err

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_text._err` -> `draftutils.messages._err`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_text.py:39`.

### from draftutils.translate import translate

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_text.translate` -> `draftutils.translate.translate`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_text.py:40`.

### from freecad.deprecation import deprecated

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_text.deprecated` -> `freecad.deprecation.deprecated`.

[Source module `freecad.deprecation`](../../freecad/deprecation/index.md).

Evidence: `src/Mod/Draft/draftmake/make_text.py:41`.

### from draftviewproviders.view_text import ViewProviderText

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if App.GuiUp`.

Bound source name `draftmake.make_text.ViewProviderText` -> `draftviewproviders.view_text.ViewProviderText`.

[Source module `draftviewproviders.view_text`](../../draftviewproviders/view_text/index.md).

Evidence: `src/Mod/Draft/draftmake/make_text.py:44`.

## `draftmake.make_text.make_text`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def make_text(string, placement=None, screen=False, height=None, line_spacing=1):
```

Create a Text object containing the given list of strings.

The current color and text height and font specified in preferences
are used.

Parameters
----------
string: str, or list of str
    String to display on screen.
    If it is a list, each element in the list represents a new text line.

placement: Base::Placement, Base::Vector3, or Base::Rotation, optional
    Defaults to `None`.
    If it is provided, it is the placement of the new text.
    The input could be a full placement, just a vector indicating
    the translation, or just a rotation.

screen: bool or None, optional
    Defaults to `False`.
    If it is `True`, the DisplayMode is set to "Screen".
    If it is `False`, it is set to "World".
    If it is `None`, the DisplayMode depends on the current preferences.

height: float or None, optional
    Defaults to `None`.
    A height value for the text, in mm.
    If it is `None` or zero, the FontSize depends on the current preferences.

line_spacing: float or None, optional
    Defaults to 1.
    The line spacing factor.
    If it is `None` or zero, the LineSpacing depends on the current preferences.

Returns
-------
App::FeaturePython
    A scripted object of type `'Text'`.
    This object does not have a `Shape` attribute, as the text is created
    on screen by Coin (pivy).

None
    If there is a problem it will return `None`.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_text.py:47`. Decorators are copied as source expressions and have not been executed.

## `draftmake.make_text.makeText`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@deprecated(deprecated_in='26.3', removed_in='28.3', replacement='Draft.make_text()')
def makeText(stringlist, point=App.Vector(0, 0, 0), screen=False):
```

DEPRECATED. Use 'make_text'.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_text.py:155`. Decorators are copied as source expressions and have not been executed.

## `draftmake.make_text.convert_draft_texts`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def convert_draft_texts(textslist=None):
```

Convert the given Annotation to a Draft text.

In the past, the `Draft Text` object didn't exist; text objects
were of type `App::Annotation`. This function was introduced
to convert those older objects to a `Draft Text` scripted object.

This function was already present at splitting time during v0.19.

Parameters
----------
textslist: list of objects, optional
    It defaults to `None`.
    A list containing `App::Annotation` objects or a single of these
    objects.
    If it is `None` it will convert all objects in the current document.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_text.py:160`. Decorators are copied as source expressions and have not been executed.

## `draftmake.make_text.convertDraftTexts`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def convertDraftTexts(*args, **kwarg):
```

DEPRECATED. Use 'convert_draft_texts'.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_text.py:216`. Decorators are copied as source expressions and have not been executed.

