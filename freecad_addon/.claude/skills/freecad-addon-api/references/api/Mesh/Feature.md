# `Mesh.Feature`

[Module](index.md)

```python
class Feature(GeoFeature):
```

The Mesh::Feature class handles meshes.
The Mesh.MeshFeature() function is for internal use only and cannot be used to create instances of this class.
Therefore you must have a reference to a document, e.g. 'd' then you can create an instance with
d.addObject("Mesh::Feature").

Author: Werner Mayer (wmayer@users.sourceforge.net)
License: LGPL-2.1-or-later

Evidence: public stub `Mesh/__init__.pyi` line 715. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Mesh.Feature.Mesh`

```python
@property
def Mesh(self) -> Mesh:

@Mesh.setter
def Mesh(self, value: Mesh | list[list[float]]) -> None:
```

The mesh kernel

Access: getter and setter declared in the stub.

Evidence: public stub `Mesh/__init__.pyi` line(s) 727, 732.

## `Mesh.Feature.countPoints`

```python
def countPoints(self) -> Any:
```

Return the number of vertices of the mesh object

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 735.

## `Mesh.Feature.countFacets`

```python
def countFacets(self) -> Any:
```

Return the number of facets of the mesh object

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 739.

## `Mesh.Feature.harmonizeNormals`

```python
def harmonizeNormals(self) -> Any:
```

Adjust wrong oriented facets

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 743.

## `Mesh.Feature.smooth`

```python
def smooth(self, iteration: int=1, max_error: float=..., /) -> None:
```

Smooth the mesh data

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Mesh/__init__.pyi` line(s) 747.

## `Mesh.Feature.decimate`

```python
@overload
def decimate(self, tolerance: float, reduction: float, /) -> None:

@overload
def decimate(self, target_size: int, /) -> None:

def decimate(self, *args) -> None:
```

Decimate the mesh
decimate(tolerance(Float), reduction(Float))
tolerance: maximum error
reduction: reduction factor must be in the range [0.0,1.0]
Example:
mesh.decimate(0.5, 0.1) # reduction by up to 10 percent
mesh.decimate(0.5, 0.9) # reduction by up to 90 percent

or

decimate(targwt size(int))
mesh.decimate(mesh.CountFacets/2)

Evidence: public stub `Mesh/__init__.pyi` line(s) 752, 756, 759.

## `Mesh.Feature.removeNonManifolds`

```python
def removeNonManifolds(self) -> Any:
```

Remove non-manifolds

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 776.

## `Mesh.Feature.removeNonManifoldPoints`

```python
def removeNonManifoldPoints(self) -> Any:
```

Remove non-manifold points

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 780.

## `Mesh.Feature.fixIndices`

```python
def fixIndices(self) -> Any:
```

Repair any invalid indices

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 784.

## `Mesh.Feature.fixDegenerations`

```python
def fixDegenerations(self, epsilon: float=..., /) -> None:
```

Remove degenerated facets

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Mesh/__init__.pyi` line(s) 788.

## `Mesh.Feature.removeDuplicatedFacets`

```python
def removeDuplicatedFacets(self) -> Any:
```

Remove duplicated facets

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 792.

## `Mesh.Feature.removeDuplicatedPoints`

```python
def removeDuplicatedPoints(self) -> Any:
```

Remove duplicated points

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 796.

## `Mesh.Feature.fixSelfIntersections`

```python
def fixSelfIntersections(self) -> Any:
```

Repair self-intersections

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 800.

## `Mesh.Feature.removeFoldsOnSurface`

```python
def removeFoldsOnSurface(self) -> Any:
```

Remove folds on surfaces

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 804.

## `Mesh.Feature.removeInvalidPoints`

```python
def removeInvalidPoints(self) -> Any:
```

Remove points with invalid coordinates (NaN)

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Mesh/__init__.pyi` line(s) 808.

