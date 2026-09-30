# `Part.Geom2d.Hyperbola2d`

[Module](index.md)

```python
class Hyperbola2d(Conic2d):
```

Describes a hyperbola in 2D space
To create a hyperbola there are several ways:
Part.Geom2d.Hyperbola2d()
    Creates a hyperbola with major radius 2 and minor radius 1 with the
    center in (0,0)

Part.Geom2d.Hyperbola2d(Hyperbola)
    Create a copy of the given hyperbola

Part.Geom2d.Hyperbola2d(S1,S2,Center)
    Creates a hyperbola centered on the point Center, S1 and S2,
    its major axis is defined by Center and S1,
    its major radius is the distance between Center and S1, and
    its minor radius is the distance between S2 and the major axis.

Part.Geom2d.Hyperbola2d(Center,MajorRadius,MinorRadius)
    Creates a hyperbola with major and minor radii MajorRadius and
    MinorRadius and located at Center

Author: Werner Mayer (wmayer@users.sourceforge.net)
Licence: LGPL

Evidence: public stub `Part/Geom2d.pyi` line 1061. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.Geom2d.Hyperbola2d.MajorRadius`

```python
MajorRadius: float = ...
```

The major radius of the hyperbola.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/Geom2d.pyi` line(s) 1085.

## `Part.Geom2d.Hyperbola2d.MinorRadius`

```python
MinorRadius: float = ...
```

The minor radius of the hyperbola.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/Geom2d.pyi` line(s) 1087.

## `Part.Geom2d.Hyperbola2d.Focal`

```python
Focal: Final[float] = ...
```

The focal distance of the hyperbola.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/Geom2d.pyi` line(s) 1089.

## `Part.Geom2d.Hyperbola2d.Focus1`

```python
Focus1: Final[object] = ...
```


    The first focus is on the positive side of the major axis of the hyperbola;
    the second focus is on the negative side.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/Geom2d.pyi` line(s) 1091.

## `Part.Geom2d.Hyperbola2d.Focus2`

```python
Focus2: Final[object] = ...
```


    The first focus is on the positive side of the major axis of the hyperbola;
    the second focus is on the negative side.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/Geom2d.pyi` line(s) 1093.

## `Part.Geom2d.Hyperbola2d.__init__`

```python
@overload
def __init__(self) -> None:

@overload
def __init__(self, Hyperbola: 'Hyperbola2d') -> None:

@overload
def __init__(self, S1: object, S2: object, Center: object) -> None:

@overload
def __init__(self, Center: object, MajorRadius: float, MinorRadius: float) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Evidence: public stub `Part/Geom2d.pyi` line(s) 1097, 1101, 1105, 1109.

