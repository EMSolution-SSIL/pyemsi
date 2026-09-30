# `Sketcher.Sketch`

[Module](index.md)

```python
class Sketch(Persistence):
```

With this objects you can handle constraint sketches

Author: Juergen Riegel (FreeCAD@juergen-riegel.net)
Licence: LGPL

Evidence: public stub `Sketcher/__init__.pyi` line 354. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Sketcher.Sketch.Constraint`

```python
Constraint: Final[int] = 0
```

0: exactly constraint, -1 under-constraint, 1 over-constraint

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 361.

## `Sketcher.Sketch.Conflicts`

```python
Conflicts: Final[Tuple] = ()
```

Tuple of conflicting constraints

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 363.

## `Sketcher.Sketch.Redundancies`

```python
Redundancies: Final[Tuple] = ()
```

Tuple of redundant constraints

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 365.

## `Sketcher.Sketch.Geometries`

```python
Geometries: Final[Tuple] = ()
```

Tuple of all geometric elements in this sketch

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 367.

## `Sketcher.Sketch.Shape`

```python
Shape: Final[object] = ...
```

Resulting shape from the sketch geometry

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 369.

## `Sketcher.Sketch.solve`

```python
def solve(self) -> int:
```

Solve the actual set of geometry and constraints

Evidence: public stub `Sketcher/__init__.pyi` line(s) 372.

## `Sketcher.Sketch.addGeometry`

```python
def addGeometry(self, geometry: Union[Geometry, List[Geometry]], /) -> Union[int, Tuple[int, ...]]:
```

Add a geometric object to the sketch

Evidence: public stub `Sketcher/__init__.pyi` line(s) 378.

## `Sketcher.Sketch.addConstraint`

```python
def addConstraint(self, constraint: 'Union[Sketcher.Constraint, List[Sketcher.Constraint]]', /) -> Union[int, Tuple[int, ...]]:
```

Add an constraint object to the sketch

Evidence: public stub `Sketcher/__init__.pyi` line(s) 384.

## `Sketcher.Sketch.clear`

```python
def clear(self) -> None:
```

Clear the sketch

Evidence: public stub `Sketcher/__init__.pyi` line(s) 390.

## `Sketcher.Sketch.moveGeometry`

```python
def moveGeometry(self, geo_index: int, point_pos: int, vector: Vector, relative: bool=False, /) -> int:
```

Move a given point (or curve).
to another location.
It moves the specified point (or curve) to the given location by adding some
temporary weak constraints and solve the sketch.
This method is mostly used to allow the user to drag some portions of the sketch
in real time by e.g. the mouse and it works only for underconstrained portions of
the sketch.
The argument 'relative', if present, states if the new location is given
relatively to the current one.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 396.

