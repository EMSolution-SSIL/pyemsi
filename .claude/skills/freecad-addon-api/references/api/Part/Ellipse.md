# `Part.Ellipse`

[Module](index.md)

```python
class Ellipse(Conic):
```

Describes an ellipse in 3D space

To create an ellipse there are several ways:

Part.Ellipse()
    Creates an ellipse with major radius 2 and minor radius 1 with the
    center in (0,0,0)

Part.Ellipse(Ellipse)
    Create a copy of the given ellipse

Part.Ellipse(S1,S2,Center)
    Creates an ellipse centered on the point Center, where
    the plane of the ellipse is defined by Center, S1 and S2,
    its major axis is defined by Center and S1,
    its major radius is the distance between Center and S1, and
    its minor radius is the distance between S2 and the major axis.

Part.Ellipse(Center,MajorRadius,MinorRadius)
    Creates an ellipse with major and minor radii MajorRadius and
    MinorRadius, and located in the plane defined by Center and
    the normal (0,0,1)

Evidence: public stub `Part/__init__.pyi` line 2194. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.Ellipse.MajorRadius`

```python
MajorRadius: float = 0.0
```

The major radius of the ellipse.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 2219.

## `Part.Ellipse.MinorRadius`

```python
MinorRadius: float = 0.0
```

The minor radius of the ellipse.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 2221.

## `Part.Ellipse.Focal`

```python
Focal: Final[float] = 0.0
```

The focal distance of the ellipse.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 2223.

## `Part.Ellipse.__init__`

```python
@overload
def __init__(self) -> None:

@overload
def __init__(self, ellipse: 'Ellipse', /) -> None:

@overload
def __init__(self, s1: Vector, s2: Vector, center: Vector, /) -> None:

@overload
def __init__(self, center: Vector, major_radius: float, minor_radius: float, /) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Evidence: public stub `Part/__init__.pyi` line(s) 2227, 2231, 2235, 2239.

## `Part.Ellipse.Focus1`

```python
Focus1: Final[Vector] = ...
```

The first focus is on the positive side of the major axis of the ellipse.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 2241.

## `Part.Ellipse.Focus2`

```python
Focus2: Final[Vector] = ...
```

The second focus is on the negative side of the major axis of the ellipse.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 2243.

