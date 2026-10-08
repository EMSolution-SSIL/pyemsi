# `Part.GeomPlate.BuildPlateSurface`

[Module](index.md)

```python
class BuildPlateSurface:
```

This class provides an algorithm for constructing such a plate surface.

Author: Werner Mayer (wmayer@users.sourceforge.net)
Licence: LGPL

Evidence: public stub `Part/GeomPlate.pyi` line 12. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.GeomPlate.BuildPlateSurface.init`

```python
def init(self) -> None:
```

Resets all constraints

Evidence: public stub `Part/GeomPlate.pyi` line(s) 20.

## `Part.GeomPlate.BuildPlateSurface.setNbBounds`

```python
def setNbBounds(self, count: int, /) -> None:
```

Sets the number of bounds

Evidence: public stub `Part/GeomPlate.pyi` line(s) 26.

## `Part.GeomPlate.BuildPlateSurface.loadInitSurface`

```python
def loadInitSurface(self, surface: GeometrySurface, /) -> None:
```

Loads the initial surface

Evidence: public stub `Part/GeomPlate.pyi` line(s) 32.

## `Part.GeomPlate.BuildPlateSurface.surfInit`

```python
def surfInit(self) -> GeometrySurface | None:
```

Returns the initial surface

Evidence: public stub `Part/GeomPlate.pyi` line(s) 38.

## `Part.GeomPlate.BuildPlateSurface.surface`

```python
def surface(self) -> GeometrySurface | None:
```

Returns the plate surface

Evidence: public stub `Part/GeomPlate.pyi` line(s) 44.

## `Part.GeomPlate.BuildPlateSurface.add`

```python
def add(self, constraint: PointConstraint | CurveConstraint, /) -> None:
```

Adds a linear or point constraint

Evidence: public stub `Part/GeomPlate.pyi` line(s) 50.

## `Part.GeomPlate.BuildPlateSurface.perform`

```python
def perform(self) -> None:
```

Calls the algorithm and computes the plate surface

Evidence: public stub `Part/GeomPlate.pyi` line(s) 56.

## `Part.GeomPlate.BuildPlateSurface.isDone`

```python
def isDone(self) -> bool:
```

Tests whether computation of the plate has been completed

Evidence: public stub `Part/GeomPlate.pyi` line(s) 62.

## `Part.GeomPlate.BuildPlateSurface.sense`

```python
def sense(self) -> object:
```

Returns the orientation of the curves in the array returned by curves2d

Evidence: public stub `Part/GeomPlate.pyi` line(s) 68.

## `Part.GeomPlate.BuildPlateSurface.order`

```python
def order(self) -> int:
```

Returns the order of the curves in the array returned by curves2d

Evidence: public stub `Part/GeomPlate.pyi` line(s) 74.

## `Part.GeomPlate.BuildPlateSurface.curves2d`

```python
def curves2d(self) -> List[object]:
```

Extracts the array of curves on the plate surface which
correspond to the curve constraints set in add()

Evidence: public stub `Part/GeomPlate.pyi` line(s) 80.

## `Part.GeomPlate.BuildPlateSurface.curveConstraint`

```python
def curveConstraint(self, index: int, /) -> CurveConstraint | None:
```

Returns the curve constraint of order

Evidence: public stub `Part/GeomPlate.pyi` line(s) 87.

## `Part.GeomPlate.BuildPlateSurface.pointConstraint`

```python
def pointConstraint(self, index: int, /) -> PointConstraint | None:
```

Returns the point constraint of order

Evidence: public stub `Part/GeomPlate.pyi` line(s) 93.

## `Part.GeomPlate.BuildPlateSurface.disc2dContour`

```python
def disc2dContour(self, index: int, /) -> list:
```

Returns the 2D contour of the plate surface

Evidence: public stub `Part/GeomPlate.pyi` line(s) 99.

## `Part.GeomPlate.BuildPlateSurface.disc3dContour`

```python
def disc3dContour(self, index: int, order: int, /) -> list:
```

Returns the 3D contour of the plate surface

Evidence: public stub `Part/GeomPlate.pyi` line(s) 105.

## `Part.GeomPlate.BuildPlateSurface.G0Error`

```python
def G0Error(self, index: int=0, /) -> float:
```

Returns the max distance between the result and the constraints

Evidence: public stub `Part/GeomPlate.pyi` line(s) 111.

## `Part.GeomPlate.BuildPlateSurface.G1Error`

```python
def G1Error(self, index: int=0, /) -> float:
```

Returns the max angle between the result and the constraints

Evidence: public stub `Part/GeomPlate.pyi` line(s) 117.

## `Part.GeomPlate.BuildPlateSurface.G2Error`

```python
def G2Error(self, index: int=0, /) -> float:
```

Returns the max difference of curvature between the result and the constraints

Evidence: public stub `Part/GeomPlate.pyi` line(s) 123.

