# Python source module `draftobjects.draftlink`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftobjects/draftlink.py`. Import path is source-routed; installed availability is unverified.

Provides the base class for Link objects used by other objects.

This class was created by realthunder during the `LinkMerge`
to demonstrate how to use the `App::Link` objects to create
Link aware arrays.
It is used by `draftobject.array` (ortho, polar, circular)
and `draftobject.patharray` to create respective Link arrays.

NOTE: this class is a bit mysterious. We need more documentation
on how the properties are being set, and how the code interacts with
the arrays that use it.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import lazy_loader.lazy_loader as lz

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftobjects.draftlink.lz` -> `lazy_loader.lazy_loader`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftobjects/draftlink.py:40`.

### from PySide.QtCore import QT_TRANSLATE_NOOP

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftobjects.draftlink.QT_TRANSLATE_NOOP` -> `PySide.QtCore.QT_TRANSLATE_NOOP`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftobjects/draftlink.py:41`.

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftobjects.draftlink.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftobjects/draftlink.py:43`.

### from draftgeoutils import general as geo_general

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftobjects.draftlink.geo_general` -> `draftgeoutils.general`.

[Source module `draftgeoutils`](../../draftgeoutils/index.md).

Evidence: `src/Mod/Draft/draftobjects/draftlink.py:44`.

### from draftobjects.base import DraftObject

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftobjects.draftlink.DraftObject` -> `draftobjects.base.DraftObject`.

[Source module `draftobjects.base`](../base/index.md).

Evidence: `src/Mod/Draft/draftobjects/draftlink.py:45`.

### from draftutils import gui_utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftobjects.draftlink.gui_utils` -> `draftutils.gui_utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftobjects/draftlink.py:46`.

### from draftutils.messages import _log

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftobjects.draftlink._log` -> `draftutils.messages._log`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftobjects/draftlink.py:47`.

## Classes

- [draftobjects.draftlink.DraftLink](DraftLink.md)

## Internal definitions not expanded

`draftobjects.draftlink._DraftLink`. These are source internals unless an explicit export establishes otherwise.

