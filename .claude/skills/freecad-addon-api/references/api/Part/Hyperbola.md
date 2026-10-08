# `Part.Hyperbola`

[Module](index.md)

```python
class Hyperbola(Conic):
```

Describes an hyperbola in 3D space

To create a hyperbola there are several ways:

Part.Hyperbola()
    Creates an hyperbola with major radius 2 and minor radius 1 with the
    center in (0,0,0)

Part.Hyperbola(Hyperbola)
    Create a copy of the given hyperbola

Part.Hyperbola(S1,S2,Center)
    Creates an hyperbola centered on the point Center, where
    the plane of the hyperbola is defined by Center, S1 and S2,
    its major axis is defined by Center and S1,
    its major radius is the distance between Center and S1, and
    its minor radius is the distance between S2 and the major axis.

Part.Hyperbola(Center,MajorRadius,MinorRadius)
    Creates an hyperbola with major and minor radii MajorRadius and
    MinorRadius, and located in the plane defined by Center and
    the normal (0,0,1)

Evidence: public stub `Part/__init__.pyi` line 2963. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.Hyperbola.MajorRadius`

```python
MajorRadius: float
```

The major radius of the hyperbola.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 2988.

## `Part.Hyperbola.MinorRadius`

```python
MinorRadius: float
```

The minor radius of the hyperbola.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 2990.

## `Part.Hyperbola.Focal`

```python
Focal: Final[float]
```

The focal distance of the hyperbola.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 2992.

## `Part.Hyperbola.Focus1`

```python
Focus1: Final[Vector]
```

The first focus is on the positive side of the major axis of the hyperbola.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 2994.

## `Part.Hyperbola.Focus2`

```python
Focus2: Final[Vector]
```

The second focus is on the negative side of the major axis of the hyperbola.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 2996.

## `Part.Hyperbola.__init__`

```python
@overload
def __init__(self) -> None:

@overload
def __init__(self, hyperbola: 'Hyperbola') -> None:

@overload
def __init__(self, S1: Vector, S2: Vector, Center: Vector) -> None:

@overload
def __init__(self, Center: Vector, MajorRadius: float, MinorRadius: float) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Evidence: public stub `Part/__init__.pyi` line(s) 3000, 3004, 3008, 3012.

