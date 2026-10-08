# `Part.Vertex`

[Module](index.md)

```python
class Vertex(Shape):
```

TopoShapeVertex is the OpenCasCade topological vertex wrapper

Author: Juergen Riegel (Juergen.Riegel@web.de)

Evidence: public stub `Part/__init__.pyi` line 5225. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.Vertex.__init__`

```python
@overload
def __init__(self, x: float=..., y: float=..., z: float=..., /) -> None:

@overload
def __init__(self, coordinates: Vector, /) -> None:

@overload
def __init__(self, coordinates: tuple[float, float, float], /) -> None:

@overload
def __init__(self, point: 'Part.Point', /) -> None:

@overload
def __init__(self, shape: Shape, /) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 5233, 5237, 5241, 5245, 5249.

## `Part.Vertex.X`

```python
X: Final[float] = ...
```

X component of this Vertex.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 5251.

## `Part.Vertex.Y`

```python
Y: Final[float] = ...
```

Y component of this Vertex.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 5253.

## `Part.Vertex.Z`

```python
Z: Final[float] = ...
```

Z component of this Vertex.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 5255.

## `Part.Vertex.Point`

```python
Point: Final[Vector] = ...
```

Position of this Vertex as a Vector

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 5257.

## `Part.Vertex.Tolerance`

```python
Tolerance: float = ...
```

Set or get the tolerance of the vertex

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 5259.

