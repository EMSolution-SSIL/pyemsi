# `Part.Geom2d.Parabola2d`

[Module](index.md)

```python
class Parabola2d(Conic2d):
```

Describes a parabola in 2D space

Author: Werner Mayer (wmayer@users.sourceforge.net)
Licence: LGPL

Evidence: public stub `Part/Geom2d.pyi` line 1184. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.Geom2d.Parabola2d.Focal`

```python
Focal: float = ...
```


    The focal distance is the distance between the apex and the focus of the parabola.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/Geom2d.pyi` line(s) 1191.

## `Part.Geom2d.Parabola2d.Focus`

```python
Focus: Final[object] = ...
```


    The focus is on the positive side of the
    'X Axis' of the local coordinate system of the parabola.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/Geom2d.pyi` line(s) 1193.

## `Part.Geom2d.Parabola2d.Parameter`

```python
Parameter: Final[float] = ...
```


    Compute the parameter of this parabola which is the distance between its focus
    and its directrix. This distance is twice the focal length.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/Geom2d.pyi` line(s) 1195.

