# Python source module `draftmake.make_wpproxy`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftmake/make_wpproxy.py`. Import path is source-routed; installed availability is unverified.

Provides functions to create WorkingPlaneProxy objects.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_wpproxy.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_wpproxy.py:33`.

### from draftobjects.wpproxy import WorkingPlaneProxy

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_wpproxy.WorkingPlaneProxy` -> `draftobjects.wpproxy.WorkingPlaneProxy`.

[Source module `draftobjects.wpproxy`](../../draftobjects/wpproxy/index.md).

Evidence: `src/Mod/Draft/draftmake/make_wpproxy.py:34`.

### from freecad.deprecation import deprecated

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_wpproxy.deprecated` -> `freecad.deprecation.deprecated`.

[Source module `freecad.deprecation`](../../freecad/deprecation/index.md).

Evidence: `src/Mod/Draft/draftmake/make_wpproxy.py:35`.

### from draftviewproviders.view_wpproxy import ViewProviderWorkingPlaneProxy

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if App.GuiUp`.

Bound source name `draftmake.make_wpproxy.ViewProviderWorkingPlaneProxy` -> `draftviewproviders.view_wpproxy.ViewProviderWorkingPlaneProxy`.

[Source module `draftviewproviders.view_wpproxy`](../../draftviewproviders/view_wpproxy/index.md).

Evidence: `src/Mod/Draft/draftmake/make_wpproxy.py:38`.

## `draftmake.make_wpproxy.make_working_plane_proxy`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def make_working_plane_proxy(placement):
```

make_working_plane_proxy(placement)

Creates a Working Plane proxy object in the current document.

Parameters
----------
placement : Base.Placement
    specify the p.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_wpproxy.py:41`. Decorators are copied as source expressions and have not been executed.

## `draftmake.make_wpproxy.make_workingplaneproxy`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@deprecated(deprecated_in='26.3', removed_in='28.3', replacement='Draft.make_working_plane_proxy()')
def make_workingplaneproxy(*args, **kwarg):
```

DEPRECATED. Use 'make_working_plane_proxy'.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_wpproxy.py:67`. Decorators are copied as source expressions and have not been executed.

## `draftmake.make_wpproxy.makeWorkingPlaneProxy`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@deprecated(deprecated_in='26.3', removed_in='28.3', replacement='Draft.make_working_plane_proxy()')
def makeWorkingPlaneProxy(*args, **kwarg):
```

DEPRECATED. Use 'make_working_plane_proxy'.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_wpproxy.py:77`. Decorators are copied as source expressions and have not been executed.

