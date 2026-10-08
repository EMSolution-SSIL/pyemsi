# `MeshPart`

[Catalogue index](../index.md)

Evidence: import-shaped public stub `MeshPart/__init__.pyi`; generated binding/typing declarations, runtime unverified.

## Imports and aliases

These preserve stub type context and reexports. Imported typing helpers and underscored names are not a promise of supported runtime API.

```python
from __future__ import annotations
from typing import Any, overload
from collections.abc import Sequence
from typing import TypeAlias
from FreeCAD.Base import Vector
from Mesh import Mesh
from Part import Edge, Shape, Wire
```

## `MeshPart._Point2`

```python
_Point2: TypeAlias = tuple[float, float]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `MeshPart/__init__.pyi` line(s) 11.

## `MeshPart._Point3`

```python
_Point3: TypeAlias = tuple[float, float, float]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `MeshPart/__init__.pyi` line(s) 12.

## `MeshPart._Color`

```python
_Color: TypeAlias = tuple[float, float, float]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `MeshPart/__init__.pyi` line(s) 13.

## `MeshPart._LoftPoint`

```python
_LoftPoint: TypeAlias = _Point2 | _Point3
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `MeshPart/__init__.pyi` line(s) 14.

## `MeshPart._VectorLike`

```python
_VectorLike: TypeAlias = Vector | _Point3
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `MeshPart/__init__.pyi` line(s) 15.

## `MeshPart._ProjectedPolyline`

```python
_ProjectedPolyline: TypeAlias = list[Vector]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `MeshPart/__init__.pyi` line(s) 16.

## `MeshPart._ProjectedPolylines`

```python
_ProjectedPolylines: TypeAlias = list[_ProjectedPolyline]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `MeshPart/__init__.pyi` line(s) 17.

## `MeshPart.loftOnCurve`

```python
def loftOnCurve(curve: Shape, poly: Sequence[_LoftPoint], up_vector: _Point3, max_size: float, /) -> Mesh:
```

Create one lofted mesh by sweeping a polygon along a curve-like shape.

Evidence: public stub `MeshPart/__init__.pyi` line(s) 19.

## `MeshPart.findSectionParameters`

```python
def findSectionParameters(edge: Edge, mesh: Mesh, direction: Vector, /) -> list[float]:
```

Return edge parameters whose projected points land on mesh edges.

Evidence: public stub `MeshPart/__init__.pyi` line(s) 23.

## `MeshPart.projectShapeOnMesh`

```python
@overload
def projectShapeOnMesh(Shape: Shape, Mesh: Mesh, MaxDistance: float) -> _ProjectedPolylines:

@overload
def projectShapeOnMesh(Shape: Shape, Mesh: Mesh, Direction: Vector) -> _ProjectedPolylines:

@overload
def projectShapeOnMesh(Polygons: Sequence[Sequence[_VectorLike]], Mesh: Mesh, Direction: Vector) -> _ProjectedPolylines:
```

Project one shape to the mesh within a maximum search distance.

Project one shape to the mesh along one explicit direction.

Project one sampled polygon sequence to the mesh along one direction.

Evidence: public stub `MeshPart/__init__.pyi` line(s) 28, 33, 38.

## `MeshPart.projectPointsOnMesh`

```python
def projectPointsOnMesh(points: Sequence[_VectorLike], mesh: Mesh, direction: Vector, precision: float=-1.0, /) -> list[Vector]:
```

Project points to the mesh along one direction and return the hits.

Evidence: public stub `MeshPart/__init__.pyi` line(s) 42.

## `MeshPart.wireFromSegment`

```python
def wireFromSegment(mesh: Mesh, segment: Sequence[int], /) -> list[Wire]:
```

Create boundary wires from one mesh segment given by facet indices.

Evidence: public stub `MeshPart/__init__.pyi` line(s) 46.

## `MeshPart.wireFromMesh`

```python
def wireFromMesh(mesh: Mesh, /) -> list[Wire]:
```

Create boundary wires for the full mesh border.

Evidence: public stub `MeshPart/__init__.pyi` line(s) 50.

## `MeshPart.meshFromShape`

```python
@overload
def meshFromShape(Shape: Shape, /) -> Mesh:

@overload
def meshFromShape(Shape: Shape, LinearDeflection: float, AngularDeflection: float=0.5, Relative: bool=False, Segments: bool=False, GroupColors: Sequence[_Color] | None=None) -> Mesh:

@overload
def meshFromShape(Shape: Shape, /, *, MaxLength: float) -> Mesh:

@overload
def meshFromShape(Shape: Shape, /, *, MaxArea: float) -> Mesh:

@overload
def meshFromShape(Shape: Shape, /, *, LocalLength: float) -> Mesh:

@overload
def meshFromShape(Shape: Shape, /, *, Deflection: float) -> Mesh:

@overload
def meshFromShape(Shape: Shape, /, *, MinLength: float, MaxLength: float) -> Mesh:

@overload
def meshFromShape(Shape: Shape, /, *, Fineness: int, SecondOrder: bool=False, Optimize: bool=True, AllowQuad: bool=False, MinLength: float=0.0, MaxLength: float=0.0) -> Mesh:

@overload
def meshFromShape(Shape: Shape, /, *, GrowthRate: float=0.0, SegPerEdge: float=0.0, SegPerRadius: float=0.0, SecondOrder: bool=False, Optimize: bool=True, AllowQuad: bool=False, MinLength: float=0.0, MaxLength: float=0.0) -> Mesh:
```

Create a mesh from one shape using the default mesher settings.

Create a mesh from one shape using the standard deflection-based mesher.

Create a mesh from one shape using a maximum edge-length target.

Create a mesh from one shape using a maximum facet-area target.

Create a mesh from one shape using one local target edge length.

Create a mesh from one shape using one mefisto deflection value.

Create a mesh from one shape using explicit minimum and maximum lengths.

Create a mesh from one shape using the netgen fineness-driven settings.

Create a mesh from one shape using the user-tuned netgen settings.

Evidence: public stub `MeshPart/__init__.pyi` line(s) 55, 60, 65, 70, 75, 80, 85, 90, 95.

