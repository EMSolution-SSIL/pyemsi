# `Part.Parabola`

[Module](index.md)

```python
class Parabola(Conic):
```

Describes a parabola in 3D space

Evidence: public stub `Part/__init__.pyi` line 3114. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.Parabola.Focal`

```python
Focal: float = ...
```


    The focal distance is the distance between
    the apex and the focus of the parabola.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 3118.

## `Part.Parabola.Focus`

```python
Focus: Final[Vector] = ...
```


    The focus is on the positive side of the
    'X Axis' of the local coordinate system of the parabola.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 3120.

## `Part.Parabola.Parameter`

```python
Parameter: Final[float] = ...
```


    Compute the parameter of this parabola
    which is the distance between its focus
    and its directrix. This distance is twice the focal length.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 3122.

## `Part.Parabola.compute`

```python
def compute(self, p1: Vector, p2: Vector, p3: Vector, /) -> None:
```

compute(p1,p2,p3) -> None

The three points must lie on a plane parallel to xy plane and must not be collinear

Evidence: public stub `Part/__init__.pyi` line(s) 3125.

