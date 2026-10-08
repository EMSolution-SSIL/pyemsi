# Python source module `draftgeoutils.geo_arrays`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftgeoutils/geo_arrays.py`. Import path is source-routed; installed availability is unverified.

Provides various functions to work with arrays.

One of the functions is used to create a `twisted array` object.
See `draftobjects/twistedarray.py`.

This array was developed in order to build a `twisted bridge` object.

See https://forum.freecad.org/viewtopic.php?f=23&t=49617

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import lazy_loader.lazy_loader as lz

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.geo_arrays.lz` -> `lazy_loader.lazy_loader`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/geo_arrays.py:40`.

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.geo_arrays.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/geo_arrays.py:42`.

### from draftutils.messages import _msg

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftgeoutils.geo_arrays._msg` -> `draftutils.messages._msg`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftgeoutils/geo_arrays.py:43`.

## `draftgeoutils.geo_arrays.print_places`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def print_places(places, title='Places'):
```

Print a vector with a title.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/geo_arrays.py:52`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.geo_arrays.get_init_values`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_init_values(path, count=6):
```

Set values needed to create the array.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/geo_arrays.py:60`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.geo_arrays.get_n_params`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_n_params(edge, number, step, norm):
```

Get the parameters needed in each iteration.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/geo_arrays.py:77`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.geo_arrays.get_twisted_placements`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_twisted_placements(path, count=15, rot_factor=0.25):
```

Get the placements of the twisted array elements.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/geo_arrays.py:89`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.geo_arrays.get_twisted_array_shape`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_twisted_array_shape(base, path, count=15, rot_factor=0.25):
```

Get the twisted array shape as a compound.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/geo_arrays.py:114`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.geo_arrays.get_twisted_bridge_shape`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_twisted_bridge_shape(base, path, count=15, rot_factor=0.25, width=100, thickness=10):
```

Get the twisted bridge array shape as a compound.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/geo_arrays.py:123`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.geo_arrays.create_frames`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def create_frames(obj, places):
```

Create the frames from the placements.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/geo_arrays.py:147`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.geo_arrays.make_tunnel`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def make_tunnel(path, profiles):
```

Create the tunnel shape.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/geo_arrays.py:162`. Decorators are copied as source expressions and have not been executed.

## `draftgeoutils.geo_arrays.make_walkway`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def make_walkway(path, width=100, thickness=10):
```

Construct the walkway of the twisted bridge array.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftgeoutils/geo_arrays.py:170`. Decorators are copied as source expressions and have not been executed.

