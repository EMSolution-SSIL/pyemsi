# `FreeCAD.Base.CoordinateSystem`

[Module](index.md)

```python
class CoordinateSystem:
```

Base.CoordinateSystem class.

An orthonormal right-handed coordinate system in 3D space.

CoordinateSystem()
Empty constructor.

Author: Juergen Riegel (FreeCAD@juergen-riegel.net)
Licence: LGPL

Evidence: public stub `FreeCAD/Base.pyi` line 446. Inherited members are on the named base's reference; aliases keep their imported identity.

## `FreeCAD.Base.CoordinateSystem.Axis`

```python
Axis: 'FreeCAD.Base.Axis' = ...
```

Set or get axis.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 458.

## `FreeCAD.Base.CoordinateSystem.XDirection`

```python
XDirection: Vector = ...
```

Set or get X-direction.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 460.

## `FreeCAD.Base.CoordinateSystem.YDirection`

```python
YDirection: Vector = ...
```

Set or get Y-direction.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 462.

## `FreeCAD.Base.CoordinateSystem.ZDirection`

```python
ZDirection: Vector = ...
```

Set or get Z-direction.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 464.

## `FreeCAD.Base.CoordinateSystem.Position`

```python
Position: Vector = ...
```

Set or get position.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 466.

## `FreeCAD.Base.CoordinateSystem.setAxes`

```python
def setAxes(self, axis: 'Union[FreeCAD.Base.Axis, Vector]', xDir: Vector, /) -> None:
```

Set axis or Z-direction, and X-direction.
The X-direction is determined from the orthonormal compononent of `xDir`
with respect to `axis` direction.

axis : Base.Axis, Base.Vector
xDir : Base.Vector

Evidence: public stub `FreeCAD/Base.pyi` line(s) 469.

## `FreeCAD.Base.CoordinateSystem.displacement`

```python
def displacement(self, coordSystem2: 'CoordinateSystem', /) -> Placement:
```

Computes the placement from this to the passed coordinate system `coordSystem2`.

coordSystem2 : Base.CoordinateSystem

Evidence: public stub `FreeCAD/Base.pyi` line(s) 480.

## `FreeCAD.Base.CoordinateSystem.transformTo`

```python
def transformTo(self, vector: Vector, /) -> Vector:
```

Computes the coordinates of the point in coordinates of this coordinate system.

vector : Base.Vector

Evidence: public stub `FreeCAD/Base.pyi` line(s) 488.

## `FreeCAD.Base.CoordinateSystem.transform`

```python
def transform(self, trans: Union[Rotation, Placement], /) -> None:
```

Applies a transformation on this coordinate system.

trans : Base.Rotation, Base.Placement

Evidence: public stub `FreeCAD/Base.pyi` line(s) 496.

## `FreeCAD.Base.CoordinateSystem.setPlacement`

```python
def setPlacement(self, placement: Placement, /) -> None:
```

Set placement to the coordinate system.

placement : Base.Placement

Evidence: public stub `FreeCAD/Base.pyi` line(s) 504.

