# Python source module `draftmake.make_orthoarray`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftmake/make_orthoarray.py`. Import path is source-routed; installed availability is unverified.

Provides functions to create orthogonal 2D and 3D Array objects.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_orthoarray.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_orthoarray.py:33`.

### from draftmake import make_array

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_orthoarray.make_array` -> `draftmake.make_array`.

[Source module `draftmake`](../index.md).

Evidence: `src/Mod/Draft/draftmake/make_orthoarray.py:34`.

### from draftutils import utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_orthoarray.utils` -> `draftutils.utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_orthoarray.py:35`.

### from draftutils.messages import _err, _wrn

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_orthoarray._err` -> `draftutils.messages._err`.

Bound source name `draftmake.make_orthoarray._wrn` -> `draftutils.messages._wrn`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_orthoarray.py:36`.

### from draftutils.translate import translate

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_orthoarray.translate` -> `draftutils.translate.translate`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_orthoarray.py:37`.

### from freecad.deprecation import deprecated

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_orthoarray.deprecated` -> `freecad.deprecation.deprecated`.

[Source module `freecad.deprecation`](../../freecad/deprecation/index.md).

Evidence: `src/Mod/Draft/draftmake/make_orthoarray.py:38`.

## `draftmake.make_orthoarray.make_ortho_array`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def make_ortho_array(base_object, v_x=App.Vector(10, 0, 0), v_y=App.Vector(0, 10, 0), v_z=App.Vector(0, 0, 10), n_x=2, n_y=2, n_z=1, use_link=True):
```

Create an orthogonal array from the given object.

Parameters
----------
base_object: Part::Feature or str
    Any of object that has a `Part::TopoShape` that can be duplicated.
    This means most 2D and 3D objects produced with any workbench.
    If it is a string, it must be the `Label` of that object.
    Since a label is not guaranteed to be unique in a document,
    it will use the first object found with this label.

v_x, v_y, v_z: Base::Vector3, optional
    The vector indicating the vector displacement between two elements
    in the specified orthogonal direction X, Y, Z.

    By default:
    ::
        v_x = App.Vector(10, 0, 0)
        v_y = App.Vector(0, 10, 0)
        v_z = App.Vector(0, 0, 10)

    Given that this is a vectorial displacement
    the next object can appear displaced in one, two or three axes
    at the same time.

    For example
    ::
        v_x = App.Vector(10, 5, 0)

    means that the next element in the X direction will be displaced
    10 mm in X, 5 mm in Y, and 0 mm in Z.

    A traditional "rectangular" array is obtained when
    the displacement vector only has its corresponding component,
    like in the default case.

    If these values are entered as single numbers instead
    of vectors, the single value is expanded into a vector
    of the corresponding direction, and the other components are assumed
    to be zero.

    For example
    ::
        v_x = 15
        v_y = 10
        v_z = 1
    becomes
    ::
        v_x = App.Vector(15, 0, 0)
        v_y = App.Vector(0, 10, 0)
        v_z = App.Vector(0, 0, 1)

n_x, n_y, n_z: int, optional
    The number of copies in the specified orthogonal direction X, Y, Z.
    This number includes the original object, therefore, it must be
    at least 1.

    The values of `n_x` and `n_y` default to 2,
    while `n_z` defaults to 1.
    This means the array is a planar array by default.

use_link: bool, optional
    It defaults to `True`.
    If it is `True` the produced copies are not `Part::TopoShape` copies,
    but rather `App::Link` objects.
    The Links repeat the shape of the original `base_object` exactly,
    and therefore the resulting array is more memory efficient.

    Also, when `use_link` is `True`, the `Fuse` property
    of the resulting array does not work; the array doesn't
    contain separate shapes, it only has the original shape repeated
    many times, so there is nothing to fuse together.

    If `use_link` is `False` the original shape is copied many times.
    In this case the `Fuse` property is able to fuse
    all copies into a single object, if they touch each other.

Returns
-------
Part::FeaturePython
    A scripted object of type `'Array'`.
    Its `Shape` is a compound of the copies of the original object.

None
    If there is a problem it will return `None`.

See Also
--------
make_ortho_array_2d, make_rect_array, make_rect_array_2d, make_polar_array,
make_circular_array, make_path_array, make_point_array

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_orthoarray.py:154`. Decorators are copied as source expressions and have not been executed.

## `draftmake.make_orthoarray.make_ortho_array_2d`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def make_ortho_array_2d(base_object, v_x=App.Vector(10, 0, 0), v_y=App.Vector(0, 10, 0), n_x=2, n_y=2, use_link=True):
```

Create a 2D orthogonal array from the given object.

This works the same as `make_ortho_array`.
The Z component is ignored so it only considers vector displacements
in X and Y directions.

Parameters
----------
base_object: Part::Feature or str
    Any of object that has a `Part::TopoShape` that can be duplicated.
    This means most 2D and 3D objects produced with any workbench.
    If it is a string, it must be the `Label` of that object.
    Since a label is not guaranteed to be unique in a document,
    it will use the first object found with this label.

v_x, v_y: Base::Vector3, optional
    Vectorial displacement of elements
    in the corresponding X and Y directions.
    See `make_ortho_array`.

n_x, n_y: int, optional
    Number of elements
    in the corresponding X and Y directions.
    See `make_ortho_array`.

use_link: bool, optional
    If it is `True`, create `App::Link` array.
    See `make_ortho_array`.

Returns
-------
Part::FeaturePython
    A scripted object of type `'Array'`.
    Its `Shape` is a compound of the copies of the original object.

None
    If there is a problem it will return `None`.

See Also
--------
make_ortho_array, make_rect_array, make_rect_array_2d, make_polar_array,
make_circular_array, make_path_array, make_point_array

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_orthoarray.py:277`. Decorators are copied as source expressions and have not been executed.

## `draftmake.make_orthoarray.make_ortho_array2d`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@deprecated(deprecated_in='26.3', removed_in='28.3', replacement='Draft.make_ortho_array_2d()')
def make_ortho_array2d(*args, **kwarg):
```

DEPRECATED. Use 'make_ortho_array_2d'.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_orthoarray.py:348`. Decorators are copied as source expressions and have not been executed.

## `draftmake.make_orthoarray.make_rect_array`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def make_rect_array(base_object, d_x=10, d_y=10, d_z=10, n_x=2, n_y=2, n_z=1, use_link=True):
```

Create a rectangular array from the given object.

This function wraps around `make_ortho_array`
to produce strictly rectangular arrays, in which
the displacement vectors `v_x`, `v_y`, and `v_z`
only have their respective components in X, Y, and Z.

Parameters
----------
base_object: Part::Feature or str
    Any of object that has a `Part::TopoShape` that can be duplicated.
    This means most 2D and 3D objects produced with any workbench.
    If it is a string, it must be the `Label` of that object.
    Since a label is not guaranteed to be unique in a document,
    it will use the first object found with this label.

d_x, d_y, d_z: Base::Vector3, optional
    Displacement of elements in the corresponding X, Y, and Z directions.

n_x, n_y, n_z: int, optional
    Number of elements in the corresponding X, Y, and Z directions.

use_link: bool, optional
    If it is `True`, create `App::Link` array.
    See `make_ortho_array`.

Returns
-------
Part::FeaturePython
    A scripted object of type `'Array'`.
    Its `Shape` is a compound of the copies of the original object.

None
    If there is a problem it will return `None`.

See Also
--------
make_ortho_array, make_ortho_array_2d, make_rect_array_2d, make_polar_array,
make_circular_array, make_path_array, make_point_array

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_orthoarray.py:353`. Decorators are copied as source expressions and have not been executed.

## `draftmake.make_orthoarray.make_rect_array_2d`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def make_rect_array_2d(base_object, d_x=10, d_y=10, n_x=2, n_y=2, use_link=True):
```

Create a 2D rectangular array from the given object.

This function wraps around `make_ortho_array`,
to produce strictly rectangular arrays, in which
the displacement vectors `v_x` and `v_y`
only have their respective components in X and Y.
The Z component is ignored.

Parameters
----------
base_object: Part::Feature or str
    Any of object that has a `Part::TopoShape` that can be duplicated.
    This means most 2D and 3D objects produced with any workbench.
    If it is a string, it must be the `Label` of that object.
    Since a label is not guaranteed to be unique in a document,
    it will use the first object found with this label.

d_x, d_y: Base::Vector3, optional
    Displacement of elements in the corresponding X and Y directions.

n_x, n_y: int, optional
    Number of elements in the corresponding X and Y directions.

use_link: bool, optional
    If it is `True`, create `App::Link` array.
    See `make_ortho_array`.

Returns
-------
Part::FeaturePython
    A scripted object of type `'Array'`.
    Its `Shape` is a compound of the copies of the original object.

None
    If there is a problem it will return `None`.

See Also
--------
make_ortho_array, make_ortho_array_2d, make_rect_array, make_polar_array,
make_circular_array, make_path_array, make_point_array

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_orthoarray.py:423`. Decorators are copied as source expressions and have not been executed.

## `draftmake.make_orthoarray.make_rect_array2d`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@deprecated(deprecated_in='26.3', removed_in='28.3', replacement='Draft.make_rect_array_2d()')
def make_rect_array2d(*args, **kwarg):
```

DEPRECATED. Use 'make_rect_array_2d'.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_orthoarray.py:497`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`draftmake.make_orthoarray._make_ortho_array`, `draftmake.make_orthoarray._are_vectors`, `draftmake.make_orthoarray._are_integers`, `draftmake.make_orthoarray._are_numbers`, `draftmake.make_orthoarray._find_object_in_doc`. These are source internals unless an explicit export establishes otherwise.

