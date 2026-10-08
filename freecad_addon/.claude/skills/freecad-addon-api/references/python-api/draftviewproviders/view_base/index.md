# Python source module `draftviewproviders.view_base`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftviewproviders/view_base.py`. Import path is source-routed; installed availability is unverified.

Provides the viewprovider code for the base Draft object.

Many viewprovider classes may inherit this class in order to have
the same basic behavior.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import PySide.QtCore as QtCore

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftviewproviders.view_base.QtCore` -> `PySide.QtCore`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftviewproviders/view_base.py:36`.

### import PySide.QtGui as QtGui

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftviewproviders.view_base.QtGui` -> `PySide.QtGui`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftviewproviders/view_base.py:37`.

### from PySide.QtCore import QT_TRANSLATE_NOOP

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftviewproviders.view_base.QT_TRANSLATE_NOOP` -> `PySide.QtCore.QT_TRANSLATE_NOOP`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftviewproviders/view_base.py:38`.

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftviewproviders.view_base.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftviewproviders/view_base.py:40`.

### from draftutils import gui_utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftviewproviders.view_base.gui_utils` -> `draftutils.gui_utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftviewproviders/view_base.py:41`.

### from draftutils import params

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftviewproviders.view_base.params` -> `draftutils.params`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftviewproviders/view_base.py:42`.

### from draftutils import utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftviewproviders.view_base.utils` -> `draftutils.utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftviewproviders/view_base.py:43`.

### from draftutils.translate import translate

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftviewproviders.view_base.translate` -> `draftutils.translate.translate`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftviewproviders/view_base.py:44`.

### from pivy import coin

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if App.GuiUp`.

Bound source name `draftviewproviders.view_base.coin` -> `pivy.coin`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftviewproviders/view_base.py:47`.

### import FreeCADGui as Gui

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if App.GuiUp`.

Bound source name `draftviewproviders.view_base.Gui` -> `FreeCADGui`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftviewproviders/view_base.py:48`.

### import Draft_rc

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if App.GuiUp`.

Bound source name `draftviewproviders.view_base.Draft_rc` -> `Draft_rc`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftviewproviders/view_base.py:49`.

## Classes

- [draftviewproviders.view_base.ViewProviderDraft](ViewProviderDraft.md)
- [draftviewproviders.view_base.ViewProviderDraftAlt](ViewProviderDraftAlt.md)
- [draftviewproviders.view_base.ViewProviderDraftPart](ViewProviderDraftPart.md)

## Internal definitions not expanded

`draftviewproviders.view_base._ViewProviderDraft`, `draftviewproviders.view_base._ViewProviderDraftAlt`, `draftviewproviders.view_base._ViewProviderDraftPart`. These are source internals unless an explicit export establishes otherwise.

