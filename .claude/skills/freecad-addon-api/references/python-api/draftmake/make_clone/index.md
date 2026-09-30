# Python source module `draftmake.make_clone`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftmake/make_clone.py`. Import path is source-routed; installed availability is unverified.

Provides functions to create Clone objects.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_clone.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_clone.py:33`.

### from draftobjects.clone import Clone

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_clone.Clone` -> `draftobjects.clone.Clone`.

[Source module `draftobjects.clone`](../../draftobjects/clone/index.md).

Evidence: `src/Mod/Draft/draftmake/make_clone.py:34`.

### from draftutils import params

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_clone.params` -> `draftutils.params`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_clone.py:35`.

### from draftutils import utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_clone.utils` -> `draftutils.utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_clone.py:36`.

### from draftutils import gui_utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_clone.gui_utils` -> `draftutils.gui_utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_clone.py:37`.

### from freecad.deprecation import deprecated

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_clone.deprecated` -> `freecad.deprecation.deprecated`.

[Source module `freecad.deprecation`](../../freecad/deprecation/index.md).

Evidence: `src/Mod/Draft/draftmake/make_clone.py:38`.

### from PySide import QtCore

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if App.GuiUp`.

Bound source name `draftmake.make_clone.QtCore` -> `PySide.QtCore`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_clone.py:41`.

### from draftviewproviders.view_clone import ViewProviderClone

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if App.GuiUp`.

Bound source name `draftmake.make_clone.ViewProviderClone` -> `draftviewproviders.view_clone.ViewProviderClone`.

[Source module `draftviewproviders.view_clone`](../../draftviewproviders/view_clone/index.md).

Evidence: `src/Mod/Draft/draftmake/make_clone.py:42`.

## `draftmake.make_clone.make_clone`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def make_clone(obj, delta=None, forcedraft=False):
```

clone(obj,[delta,forcedraft])

Makes a clone of the given object(s).
The clone is an exact, linked copy of the given object. If the original
object changes, the final object changes too.

Parameters
----------
obj :

delta : Base.Vector
    Delta Vector to move the clone from the original position.

forcedraft : bool
    If forcedraft is True, the resulting object is a Draft clone
    even if the input object is an Arch object.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_clone.py:87`. Decorators are copied as source expressions and have not been executed.

## `draftmake.make_clone.clone`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@deprecated(deprecated_in='26.3', removed_in='28.3', replacement='Draft.make_clone()')
def clone(*args, **kwarg):
```

DEPRECATED. Use 'make_clone'.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_clone.py:167`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`draftmake.make_clone._make_bim_clone`. These are source internals unless an explicit export establishes otherwise.

