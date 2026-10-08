# Python source module `DraftVecUtils`

[Python catalogue](../index.md)

Evidence: `src/Mod/Draft/DraftVecUtils.py`. Import path is source-routed; installed availability is unverified.

Provide vector math utilities used in the Draft workbench.

Vector math utilities used primarily in the Draft workbench
but which can also be used in other workbenches and in macros.

Literal `__all__`: not available; source names do not imply supported public API.

[part 1](index.md) | [part 2](index-2.md)

## `DraftVecUtils.get_spherical_coords`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_spherical_coords(x, y, z, precision=None):
```

Get the Spherical coordinates of the vector represented
by Cartesian coordinates (x, y, z).

Parameters
----------
vector    : Base::Vector3
                    The input vector.
precision : int | None
            mathematical precision - if None use configured draft
            precision

Returns
-------
tuple of float
    Tuple (radius, theta, phi) with the Spherical coordinates.
    Radius is the radial coordinate, theta the polar angle and
    phi the azimuthal angle in radians.

Notes
-----
The vector (0, 0, 0) has undefined values for theta and phi, while
points on the z axis has undefined value for phi. The following
conventions are used (useful in DraftToolBar methods):
(0, 0, 0) -> (0, pi/2, 0)
(0, 0, z) -> (radius, theta, 0)

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/DraftVecUtils.py:852`. Decorators are copied as source expressions and have not been executed.

## `DraftVecUtils.get_cartesian_coords`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def get_cartesian_coords(radius, theta, phi):
```

Get the three-dimensional Cartesian coordinates of the vector
represented by Spherical coordinates (radius, theta, phi).

Parameters
----------
radius : float, int
    Radial coordinate of the vector.
theta : float, int
    Polar coordinate of the vector in radians.
phi : float, int
    Azimuthal coordinate of the vector in radians.

Returns
-------
tuple of float :
    Tuple (x, y, z) with the Cartesian coordinates.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/DraftVecUtils.py:904`. Decorators are copied as source expressions and have not been executed.

## Internal definitions not expanded

`DraftVecUtils.__title__`, `DraftVecUtils.__author__`, `DraftVecUtils.__url__`. These are source internals unless an explicit export establishes otherwise.

