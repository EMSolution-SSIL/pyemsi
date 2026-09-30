# `Mesh`

[Catalogue index](../index.md)

Evidence: import-shaped public stub `Mesh/__init__.pyi`; generated binding/typing declarations, runtime unverified.

## Classes

- [Mesh.Edge](Edge.md)
- [Mesh.Facet](Facet.md)
- [Mesh.Mesh](Mesh.md)
- [Mesh.Feature](Feature.md)
- [Mesh.MeshPoint](MeshPoint.md)

## Imports and aliases

These preserve stub type context and reexports. Imported typing helpers and underscored names are not a promise of supported runtime API.

```python
from __future__ import annotations
from typing import Any, overload
from collections.abc import Sequence
from typing import TypeAlias, TypedDict
from FreeCAD import DocumentObject
from FreeCAD.Base import BoundBox, Placement, Vector
from typing import Final
from FreeCAD.Base import Vector
from FreeCAD import ComplexGeoData
from typing import overload
from FreeCAD.Base import Matrix
from FreeCAD import GeoFeature
```

## `Mesh._Point3`

```python
_Point3: TypeAlias = tuple[float, float, float]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Mesh/__init__.pyi` line(s) 10.

## `Mesh._PolynomialCoefficients`

```python
_PolynomialCoefficients: TypeAlias = tuple[float, float, float, float, float, float]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Mesh/__init__.pyi` line(s) 11.

## `Mesh._MinimumVolumeBoxResult`

```python
_MinimumVolumeBoxResult: TypeAlias = tuple[Vector, Vector, Vector, Vector, float, float, float]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Mesh/__init__.pyi` line(s) 12.

## `Mesh.PolynomialFitResult`

```python
PolynomialFitResult = TypedDict('PolynomialFitResult', {'Sigma': float, 'Coefficients': _PolynomialCoefficients, 'Residuals': tuple[float, ...]})
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 13.

## `Mesh.read`

```python
def read(name: str, /) -> Mesh:
```

Read one mesh file and return the resulting `Mesh` object.

Evidence: public stub `Mesh/__init__.pyi` line(s) 15.

## `Mesh.open`

```python
def open(name: str, /) -> None:
```

Open one mesh file into a new document.

Evidence: public stub `Mesh/__init__.pyi` line(s) 19.

## `Mesh.insert`

```python
@overload
def insert(name: str, /) -> None:

@overload
def insert(name: str, doc_name: str, /) -> None:
```

Insert one mesh file into the active document, creating one if needed.

Insert one mesh file into the named document, creating it if needed.

Evidence: public stub `Mesh/__init__.pyi` line(s) 24, 29.

## `Mesh.export`

```python
def export(objectList: Sequence[DocumentObject], filename: str, tolerance: float=0.1, exportAmfCompressed: bool=True) -> None:
```

Export document objects to one mesh file.

Evidence: public stub `Mesh/__init__.pyi` line(s) 33.

## `Mesh.show`

```python
def show(mesh: Mesh, name: str='Mesh', /) -> Feature:
```

Create one mesh feature in the active document from a `Mesh` object.

Evidence: public stub `Mesh/__init__.pyi` line(s) 37.

## `Mesh.createBox`

```python
@overload
def createBox(length: float=10.0, width: float=10.0, height: float=10.0, edge_length: float=-1.0, /) -> Mesh:

@overload
def createBox(box: BoundBox, /) -> Mesh:
```

Create a box mesh from dimensions and an optional target edge length.

Create a box mesh from one existing bounding box.

Evidence: public stub `Mesh/__init__.pyi` line(s) 42, 47.

## `Mesh.createPlane`

```python
def createPlane(x: float=1.0, y: float=0.0, z: float=0.0, /) -> Mesh:
```

Create a two-triangle XY plane; when `y` is zero it defaults to `x`.

Evidence: public stub `Mesh/__init__.pyi` line(s) 51.

## `Mesh.createSphere`

```python
def createSphere(radius: float=5.0, sampling: int=50, /) -> Mesh:
```

Create a tessellated sphere mesh.

Evidence: public stub `Mesh/__init__.pyi` line(s) 55.

## `Mesh.createEllipsoid`

```python
def createEllipsoid(radius1: float=2.0, radius2: float=4.0, sampling: int=50, /) -> Mesh:
```

Create a tessellated ellipsoid mesh.

Evidence: public stub `Mesh/__init__.pyi` line(s) 59.

## `Mesh.createCylinder`

```python
def createCylinder(radius: float=2.0, length: float=10.0, closed: bool=True, edge_length: float=1.0, sampling: int=50, /) -> Mesh:
```

Create a tessellated cylinder mesh.

Evidence: public stub `Mesh/__init__.pyi` line(s) 63.

## `Mesh.createCone`

```python
def createCone(radius1: float=2.0, radius2: float=4.0, length: float=10.0, closed: bool=True, edge_length: float=1.0, sampling: int=50, /) -> Mesh:
```

Create a tessellated cone mesh.

Evidence: public stub `Mesh/__init__.pyi` line(s) 67.

## `Mesh.createTorus`

```python
def createTorus(radius1: float=10.0, radius2: float=2.0, sampling: int=50, /) -> Mesh:
```

Create a tessellated torus mesh.

Evidence: public stub `Mesh/__init__.pyi` line(s) 71.

## `Mesh.calculateEigenTransform`

```python
def calculateEigenTransform(points: Sequence[Vector], /) -> Placement:
```

Return the principal-axis placement for one point set.

Evidence: public stub `Mesh/__init__.pyi` line(s) 75.

## `Mesh.polynomialFit`

```python
def polynomialFit(points: Sequence[Vector], /) -> PolynomialFitResult:
```

Fit a quadratic surface to one point set and return fit diagnostics.

Evidence: public stub `Mesh/__init__.pyi` line(s) 79.

## `Mesh.minimumVolumeOrientedBox`

```python
def minimumVolumeOrientedBox(points: Sequence[Vector], /) -> _MinimumVolumeBoxResult:
```

Return the oriented minimum-volume box center, axes, and extents.

Evidence: public stub `Mesh/__init__.pyi` line(s) 83.

