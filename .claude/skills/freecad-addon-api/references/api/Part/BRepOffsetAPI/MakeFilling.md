# `Part.BRepOffsetAPI.MakeFilling`

[Module](index.md)

```python
class MakeFilling:
```

N-Side Filling

Author: Werner Mayer (wmayer[at]users.sourceforge.net)
Licence: LGPL

Evidence: public stub `Part/BRepOffsetAPI.pyi` line 12. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.BRepOffsetAPI.MakeFilling.setConstrParam`

```python
def setConstrParam(self, *, Tol2d: float=1e-05, Tol3d: float=0.0001, TolAng: float=0.01, TolCurv: float=0.1) -> None:
```

setConstrParam(Tol2d=0.00001, Tol3d=0.0001, TolAng=0.01, TolCurv=0.1)
Sets the values of Tolerances used to control the constraint.

Evidence: public stub `Part/BRepOffsetAPI.pyi` line(s) 20.

## `Part.BRepOffsetAPI.MakeFilling.setResolParam`

```python
def setResolParam(self, *, Degree: int=3, NbPtsOnCur: int=15, NbIter: int=2, Anisotropy: bool=False) -> None:
```

setResolParam(Degree=3, NbPtsOnCur=15, NbIter=2, Anisotropy=False)
Sets the parameters used for resolution.

Evidence: public stub `Part/BRepOffsetAPI.pyi` line(s) 27.

## `Part.BRepOffsetAPI.MakeFilling.setApproxParam`

```python
def setApproxParam(self, *, MaxDegree: int=8, MaxSegments: int=9) -> None:
```

setApproxParam(MaxDegree=8, MaxSegments=9)
Sets the parameters used to approximate the filling the surface

Evidence: public stub `Part/BRepOffsetAPI.pyi` line(s) 34.

## `Part.BRepOffsetAPI.MakeFilling.loadInitSurface`

```python
def loadInitSurface(self, face: TopoShapeFace, /) -> None:
```

loadInitSurface(face)
Loads the initial surface.

Evidence: public stub `Part/BRepOffsetAPI.pyi` line(s) 41.

## `Part.BRepOffsetAPI.MakeFilling.add`

```python
@overload
def add(self, Constraint: TopoShapeEdge, Order: int, IsBound: bool=True) -> None:

@overload
def add(self, Constraint: TopoShapeEdge, Support: TopoShapeFace, Order: int, IsBound: bool=True) -> None:

@overload
def add(self, Support: TopoShapeFace, Order: int) -> None:

@overload
def add(self, Point: Point) -> None:

@overload
def add(self, U: float, V: float, Support: TopoShapeFace, Order: int) -> None:

def add(self, **kwargs) -> None:
```

add(Constraint, Order, IsBound=True)
add(Constraint, Support, Order, IsBound=True)
add(Support, Order)
add(Point)
add(U, V, Support, Order)
Adds a new constraint.

Evidence: public stub `Part/BRepOffsetAPI.pyi` line(s) 49, 53, 57, 61, 65, 68.

## `Part.BRepOffsetAPI.MakeFilling.build`

```python
def build(self) -> None:
```

Builds the resulting faces.

Evidence: public stub `Part/BRepOffsetAPI.pyi` line(s) 79.

## `Part.BRepOffsetAPI.MakeFilling.isDone`

```python
def isDone(self) -> bool:
```

Tests whether computation of the filling plate has been completed.

Evidence: public stub `Part/BRepOffsetAPI.pyi` line(s) 85.

## `Part.BRepOffsetAPI.MakeFilling.G0Error`

```python
@overload
def G0Error(self, /) -> float:

@overload
def G0Error(self, arg: int, /) -> float:

def G0Error(self, arg: int=0, /) -> float:
```

G0Error([int])
Returns the maximum distance between the result and the constraints.

Evidence: public stub `Part/BRepOffsetAPI.pyi` line(s) 92, 96, 99.

## `Part.BRepOffsetAPI.MakeFilling.G1Error`

```python
@overload
def G1Error(self, /) -> float:

@overload
def G1Error(self, arg: int, /) -> float:

def G1Error(self, arg: int=0, /) -> float:
```

G1Error([int])
Returns the maximum angle between the result and the constraints.

Evidence: public stub `Part/BRepOffsetAPI.pyi` line(s) 107, 111, 114.

## `Part.BRepOffsetAPI.MakeFilling.G2Error`

```python
@overload
def G2Error(self, /) -> float:

@overload
def G2Error(self, arg: int, /) -> float:

def G2Error(self, arg: int=0, /) -> float:
```

G2Error([int])
Returns the greatest difference in curvature between the result and the constraints.

Evidence: public stub `Part/BRepOffsetAPI.pyi` line(s) 122, 126, 129.

## `Part.BRepOffsetAPI.MakeFilling.shape`

```python
def shape(self) -> TopoShape:
```

shape()
Returns the resulting shape.

Evidence: public stub `Part/BRepOffsetAPI.pyi` line(s) 136.

