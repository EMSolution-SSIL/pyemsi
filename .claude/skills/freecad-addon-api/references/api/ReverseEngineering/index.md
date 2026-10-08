# `ReverseEngineering`

[Catalogue index](../index.md)

Evidence: import-shaped public stub `ReverseEngineering/__init__.pyi`; generated binding/typing declarations, runtime unverified.

## Imports and aliases

These preserve stub type context and reexports. Imported typing helpers and underscored names are not a promise of supported runtime API.

```python
from __future__ import annotations
from typing import Any, overload
from collections.abc import Sequence
from typing import Literal, TypeAlias, TypedDict
from FreeCAD.Base import Vector
from Mesh import Mesh
from Part import BSplineCurve, BSplineSurface
from Points import Points
```

## `ReverseEngineering._Point3`

```python
_Point3: TypeAlias = tuple[float, float, float]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `ReverseEngineering/__init__.pyi` line(s) 12.

## `ReverseEngineering._VectorLike`

```python
_VectorLike: TypeAlias = Vector | _Point3
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `ReverseEngineering/__init__.pyi` line(s) 13.

## `ReverseEngineering._CurvePointCloud`

```python
_CurvePointCloud: TypeAlias = Points | Sequence[_VectorLike]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `ReverseEngineering/__init__.pyi` line(s) 14.

## `ReverseEngineering._SurfacePointCloud`

```python
_SurfacePointCloud: TypeAlias = Points | Mesh | Sequence[_VectorLike]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `ReverseEngineering/__init__.pyi` line(s) 15.

## `ReverseEngineering._Normals`

```python
_Normals: TypeAlias = Sequence[_VectorLike]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `ReverseEngineering/__init__.pyi` line(s) 16.

## `ReverseEngineering._SegmentationCluster`

```python
_SegmentationCluster: TypeAlias = tuple[int, ...]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `ReverseEngineering/__init__.pyi` line(s) 17.

## `ReverseEngineering._UvDirections`

```python
_UvDirections: TypeAlias = tuple[_VectorLike, _VectorLike]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `ReverseEngineering/__init__.pyi` line(s) 18.

## `ReverseEngineering._ParametrizationType`

```python
_ParametrizationType: TypeAlias = Literal['Uniform', 'Centripetal', 'ChordLength'] | str
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `ReverseEngineering/__init__.pyi` line(s) 19.

## `ReverseEngineering._SacModel`

```python
_SacModel: TypeAlias = Literal['Plane', 'Cylinder', 'Sphere', 'Cone'] | str
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `ReverseEngineering/__init__.pyi` line(s) 20.

## `ReverseEngineering.SampleConsensusResult`

```python
SampleConsensusResult = TypedDict('SampleConsensusResult', {'Probability': float, 'Parameters': tuple[float, ...], 'Model': tuple[int, ...]})
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Evidence: public stub `ReverseEngineering/__init__.pyi` line(s) 21.

## `ReverseEngineering.approxCurve`

```python
@overload
def approxCurve(Points: _CurvePointCloud, Closed: bool=False, MinDegree: int=3, MaxDegree: int=8, Continuity: int=2, Tolerance: float=0.001) -> BSplineCurve:

@overload
def approxCurve(Points: _CurvePointCloud, ParametrizationType: _ParametrizationType, Closed: bool=False, MinDegree: int=3, MaxDegree: int=8, Continuity: int=2, Tolerance: float=0.001) -> BSplineCurve:

@overload
def approxCurve(Points: _CurvePointCloud, Weight1: float, Weight2: float, Weight3: float, Closed: bool=False, MaxDegree: int=8, Continuity: int=2, Tolerance: float=0.001) -> BSplineCurve:
```

Approximate one point sequence with one B-spline curve.

Approximate one point sequence with one explicitly parametrized B-spline curve.

Approximate one point sequence with weighted energy terms.

Evidence: public stub `ReverseEngineering/__init__.pyi` line(s) 24, 29, 34.

## `ReverseEngineering.approxSurface`

```python
def approxSurface(Points: _SurfacePointCloud, UDegree: int=3, VDegree: int=3, NbUPoles: int=6, NbVPoles: int=6, Smooth: bool=True, Weight: float=0.1, Grad: float=1.0, Bend: float=0.0, Curv: float=0.0, Iterations: int=5, Correction: bool=True, PatchFactor: float=1.0, UVDirs: _UvDirections | None=None) -> BSplineSurface:
```

Approximate one point cloud or mesh with one B-spline surface.

Evidence: public stub `ReverseEngineering/__init__.pyi` line(s) 38.

## `ReverseEngineering.triangulate`

```python
def triangulate(Points: Points, SearchRadius: float, Mu: float=2.5, KSearch: int=5, Normals: _Normals | None=None) -> Mesh:
```

Triangulate one point cloud into one mesh with greedy surface reconstruction.

Evidence: public stub `ReverseEngineering/__init__.pyi` line(s) 42.

## `ReverseEngineering.poissonReconstruction`

```python
def poissonReconstruction(Points: Points, KSearch: int=5, OctreeDepth: int=-1, SolverDivide: int=-1, SamplesPerNode: float=-1.0, Normals: _Normals | None=None) -> Mesh:
```

Reconstruct one mesh from one point cloud with the Poisson method.

Evidence: public stub `ReverseEngineering/__init__.pyi` line(s) 46.

## `ReverseEngineering.viewTriangulation`

```python
def viewTriangulation(Points: Points, Width: int, Height: int) -> Mesh:
```

Triangulate one regularly sampled height field into one mesh.

Evidence: public stub `ReverseEngineering/__init__.pyi` line(s) 50.

## `ReverseEngineering.gridProjection`

```python
def gridProjection(Points: Points, KSearch: int=5, Normals: _Normals | None=None) -> Mesh:
```

Reconstruct one mesh from one point cloud with grid projection.

Evidence: public stub `ReverseEngineering/__init__.pyi` line(s) 54.

## `ReverseEngineering.marchingCubesRBF`

```python
def marchingCubesRBF(Points: Points, KSearch: int=5, Normals: _Normals | None=None) -> Mesh:
```

Reconstruct one mesh from one point cloud with radial-basis marching cubes.

Evidence: public stub `ReverseEngineering/__init__.pyi` line(s) 58.

## `ReverseEngineering.marchingCubesHoppe`

```python
def marchingCubesHoppe(Points: Points, KSearch: int=5, Normals: _Normals | None=None) -> Mesh:
```

Reconstruct one mesh from one point cloud with Hoppe marching cubes.

Evidence: public stub `ReverseEngineering/__init__.pyi` line(s) 62.

## `ReverseEngineering.fitBSpline`

```python
def fitBSpline(Points: Points, Degree: int=2, Refinement: int=4, Iterations: int=10, InteriorSmoothness: float=0.2, InteriorWeight: float=1.0, BoundarySmoothness: float=0.2, BoundaryWeight: float=0.0) -> BSplineSurface:
```

Fit one B-spline surface directly to one point cloud.

Evidence: public stub `ReverseEngineering/__init__.pyi` line(s) 66.

## `ReverseEngineering.filterVoxelGrid`

```python
def filterVoxelGrid(Points: Points, DimX: float, DimY: float=0.0, DimZ: float=0.0) -> Points:
```

Downsample one point cloud with one voxel-grid filter.

Evidence: public stub `ReverseEngineering/__init__.pyi` line(s) 70.

## `ReverseEngineering.normalEstimation`

```python
def normalEstimation(Points: Points, KSearch: int=0, SearchRadius: float=0.0) -> list[Vector]:
```

Estimate one normal vector per point in one point cloud.

Evidence: public stub `ReverseEngineering/__init__.pyi` line(s) 74.

## `ReverseEngineering.regionGrowingSegmentation`

```python
def regionGrowingSegmentation(Points: Points, KSearch: int=5, Normals: _Normals | None=None) -> list[_SegmentationCluster]:
```

Segment one point cloud into smooth regions and return point-index clusters.

Evidence: public stub `ReverseEngineering/__init__.pyi` line(s) 78.

## `ReverseEngineering.featureSegmentation`

```python
def featureSegmentation(Points: Points, KSearch: int=5) -> list[_SegmentationCluster]:
```

Segment one point cloud by geometric features and return point-index clusters.

Evidence: public stub `ReverseEngineering/__init__.pyi` line(s) 82.

## `ReverseEngineering.sampleConsensus`

```python
def sampleConsensus(SacModel: _SacModel, Points: Points, Normals: _Normals | None=None) -> SampleConsensusResult:
```

Fit one sample-consensus primitive model to one point cloud.

Evidence: public stub `ReverseEngineering/__init__.pyi` line(s) 86.

