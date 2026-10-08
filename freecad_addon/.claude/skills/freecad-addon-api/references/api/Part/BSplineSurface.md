# `Part.BSplineSurface`

[Module](index.md)

```python
class BSplineSurface(GeometrySurface):
```

Describes a B-Spline surface in 3D space

Author: Werner Mayer (wmayer@users.sourceforge.net)
Licence: LGPL
DeveloperDocu: Describes a B-Spline surface in 3D space

Evidence: public stub `Part/__init__.pyi` line 1006. Inherited members are on the named base's reference; aliases keep their imported identity.

[part 1](BSplineSurface.md) | [part 2](BSplineSurface-2.md)

## `Part.BSplineSurface.UDegree`

```python
UDegree: Final[int] = 0
```

Returns the degree of this B-Spline surface in the u parametric direction.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 1014.

## `Part.BSplineSurface.VDegree`

```python
VDegree: Final[int] = 0
```

Returns the degree of this B-Spline surface in the v parametric direction.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 1016.

## `Part.BSplineSurface.MaxDegree`

```python
MaxDegree: Final[int] = 25
```


    Returns the value of the maximum polynomial degree of any
    B-Spline surface surface in either parametric directions.
    This value is 25.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 1018.

## `Part.BSplineSurface.NbUPoles`

```python
NbUPoles: Final[int] = 0
```

Returns the number of poles of this B-Spline surface in the u parametric direction.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 1020.

## `Part.BSplineSurface.NbVPoles`

```python
NbVPoles: Final[int] = 0
```

Returns the number of poles of this B-Spline surface in the v parametric direction.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 1022.

## `Part.BSplineSurface.NbUKnots`

```python
NbUKnots: Final[int] = 0
```

Returns the number of knots of this B-Spline surface in the u parametric direction.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 1024.

## `Part.BSplineSurface.NbVKnots`

```python
NbVKnots: Final[int] = 0
```

Returns the number of knots of this B-Spline surface in the v parametric direction.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 1026.

## `Part.BSplineSurface.FirstUKnotIndex`

```python
FirstUKnotIndex: Final[Any] = ...
```


    Returns the index in the knot array associated with the u parametric direction,
    which corresponds to the first parameter of this B-Spline surface in the specified
    parametric direction.

    The isoparametric curves corresponding to these values are the boundary curves of
    this surface.

    Note: The index does not correspond to the first knot of the surface in the specified
    parametric direction unless the multiplicity of the first knot is equal to Degree + 1,
    where Degree is the degree of this surface in the corresponding parametric direction.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Part/__init__.pyi` line(s) 1028.

## `Part.BSplineSurface.LastUKnotIndex`

```python
LastUKnotIndex: Final[Any] = ...
```


    Returns the index in the knot array associated with the u parametric direction,
    which corresponds to the last parameter of this B-Spline surface in the specified
    parametric direction.

    The isoparametric curves corresponding to these values are the boundary curves of
    this surface.

    Note: The index does not correspond to the first knot of the surface in the specified
    parametric direction unless the multiplicity of the last knot is equal to Degree + 1,
    where Degree is the degree of this surface in the corresponding parametric direction.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Part/__init__.pyi` line(s) 1030.

## `Part.BSplineSurface.FirstVKnotIndex`

```python
FirstVKnotIndex: Final[Any] = ...
```


    Returns the index in the knot array associated with the v parametric direction,
    which corresponds to the first parameter of this B-Spline surface in the specified
    parametric direction.

    The isoparametric curves corresponding to these values are the boundary curves of
    this surface.

    Note: The index does not correspond to the first knot of the surface in the specified
    parametric direction unless the multiplicity of the first knot is equal to Degree + 1,
    where Degree is the degree of this surface in the corresponding parametric direction.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Part/__init__.pyi` line(s) 1032.

## `Part.BSplineSurface.LastVKnotIndex`

```python
LastVKnotIndex: Final[Any] = ...
```


    Returns the index in the knot array associated with the v parametric direction,
    which corresponds to the last parameter of this B-Spline surface in the specified
    parametric direction.

    The isoparametric curves corresponding to these values are the boundary curves of
    this surface.

    Note: The index does not correspond to the first knot of the surface in the specified
    parametric direction unless the multiplicity of the last knot is equal to Degree + 1,
    where Degree is the degree of this surface in the corresponding parametric direction.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Part/__init__.pyi` line(s) 1034.

## `Part.BSplineSurface.UKnotSequence`

```python
UKnotSequence: Final[List[Any]] = []
```


    Returns the knots sequence of this B-Spline surface in
    the u direction.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Part/__init__.pyi` line(s) 1036.

## `Part.BSplineSurface.VKnotSequence`

```python
VKnotSequence: Final[List[Any]] = []
```


    Returns the knots sequence of this B-Spline surface in
    the v direction.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Part/__init__.pyi` line(s) 1038.

## `Part.BSplineSurface.bounds`

```python
def bounds(self) -> Any:
```

Returns the parametric bounds (U1, U2, V1, V2) of this B-Spline surface.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Part/__init__.pyi` line(s) 1041.

## `Part.BSplineSurface.isURational`

```python
def isURational(self) -> Any:
```

Returns false if the equation of this B-Spline surface is polynomial
(e.g. non-rational) in the u or v parametric direction.
In other words, returns false if for each row of poles, the associated
weights are identical

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Part/__init__.pyi` line(s) 1047.

## `Part.BSplineSurface.isVRational`

```python
def isVRational(self) -> Any:
```

Returns false if the equation of this B-Spline surface is polynomial
(e.g. non-rational) in the u or v parametric direction.
In other words, returns false if for each column of poles, the associated
weights are identical

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Part/__init__.pyi` line(s) 1056.

## `Part.BSplineSurface.isUPeriodic`

```python
def isUPeriodic(self) -> Any:
```

Returns true if this surface is periodic in the u parametric direction.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Part/__init__.pyi` line(s) 1065.

## `Part.BSplineSurface.isVPeriodic`

```python
def isVPeriodic(self) -> Any:
```

Returns true if this surface is periodic in the v parametric direction.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Part/__init__.pyi` line(s) 1071.

## `Part.BSplineSurface.isUClosed`

```python
def isUClosed(self) -> Any:
```

Checks if this surface is closed in the u parametric direction.
Returns true if, in the table of poles the first row and the last
row are identical.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Part/__init__.pyi` line(s) 1077.

## `Part.BSplineSurface.isVClosed`

```python
def isVClosed(self) -> Any:
```

Checks if this surface is closed in the v parametric direction.
Returns true if, in the table of poles the first column and the
last column are identical.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Part/__init__.pyi` line(s) 1085.

## `Part.BSplineSurface.increaseDegree`

```python
def increaseDegree(self, u_degree: int, v_degree: int, /) -> None:
```

increaseDegree(u_degree, v_degree)
Increases the degrees of this B-Spline surface to u_degree and v_degree
in the u and v parametric directions respectively.
As a result, the tables of poles, weights and multiplicities are modified.
The tables of knots is not changed.

Note: Nothing is done if the given degree is less than or equal to the
current degree in the corresponding parametric direction.

Evidence: public stub `Part/__init__.pyi` line(s) 1093.

## `Part.BSplineSurface.increaseUMultiplicity`

```python
def increaseUMultiplicity(self, start: int, end: int, mult: int=..., /) -> None:
```

Increases the multiplicity in the u direction.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 1106.

## `Part.BSplineSurface.increaseVMultiplicity`

```python
def increaseVMultiplicity(self, start: int, end: int, mult: int=..., /) -> None:
```

Increases the multiplicity in the v direction.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 1112.

## `Part.BSplineSurface.incrementUMultiplicity`

```python
def incrementUMultiplicity(self, start: int, end: int, mult: int, /) -> None:
```

Increment the multiplicity in the u direction

Evidence: public stub `Part/__init__.pyi` line(s) 1118.

## `Part.BSplineSurface.incrementVMultiplicity`

```python
def incrementVMultiplicity(self, start: int, end: int, mult: int, /) -> None:
```

Increment the multiplicity in the v direction

Evidence: public stub `Part/__init__.pyi` line(s) 1124.

## `Part.BSplineSurface.insertUKnot`

```python
def insertUKnot(self, u: float, mult: int, tol: float, add: bool=..., /) -> None:
```

insertUKnot(u, mult, tol[, add]) - Insert or override a knot

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 1130.

## `Part.BSplineSurface.insertUKnots`

```python
def insertUKnots(self, u: List[float], mult: List[float], tol: float=0.0, add: bool=True, /) -> None:
```

insertUKnots(u, mult, tol[, add]) - Inserts knots.

Evidence: public stub `Part/__init__.pyi` line(s) 1136.

## `Part.BSplineSurface.insertVKnot`

```python
def insertVKnot(self, v: float, mult: int, tol: float, add: bool=..., /) -> None:
```

insertVKnot(v, mult, tol[, add]) - Insert or override a knot.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 1142.

## `Part.BSplineSurface.insertVKnots`

```python
def insertVKnots(self, v: List[float], mult: List[float], tol: float=0.0, add: bool=True, /) -> None:
```

insertVKnots(v, mult, tol[, add]) - Inserts knots.

Evidence: public stub `Part/__init__.pyi` line(s) 1148.

## `Part.BSplineSurface.removeUKnot`

```python
def removeUKnot(self, index: int, mult: int, tol: float, /) -> bool:
```

Reduces to mult the multiplicity of the knot of index index in the given
parametric direction. If mult is 0, the knot is removed.
With a modification of this type, the table of poles is also modified.
Two different algorithms are used systematically to compute the new
poles of the surface. For each pole, the distance between the pole
calculated using the first algorithm and the same pole calculated using
the second algorithm, is checked. If this distance is less than tol
it ensures that the surface is not modified by more than tol.
Under these conditions, the function returns true; otherwise, it returns
false.

A low tolerance prevents modification of the surface. A high tolerance
'smoothes' the surface.

Evidence: public stub `Part/__init__.pyi` line(s) 1154.

## `Part.BSplineSurface.removeVKnot`

```python
def removeVKnot(self, index: int, mult: int, tol: float, /) -> bool:
```

Reduces to mult the multiplicity of the knot of index index in the given
parametric direction. If mult is 0, the knot is removed.
With a modification of this type, the table of poles is also modified.
Two different algorithms are used systematically to compute the new
poles of the surface. For each pole, the distance between the pole
calculated using the first algorithm and the same pole calculated using
the second algorithm, is checked. If this distance is less than tol
it ensures that the surface is not modified by more than tol.
Under these conditions, the function returns true; otherwise, it returns
false.

A low tolerance prevents modification of the surface. A high tolerance
'smoothes' the surface.

Evidence: public stub `Part/__init__.pyi` line(s) 1172.

## `Part.BSplineSurface.segment`

```python
def segment(self, u1: float, u2: float, v1: float, v2: float, /) -> None:
```

Modifies this B-Spline surface by segmenting it between U1 and U2 in the
u parametric direction and between V1 and V2 in the v parametric direction.
Any of these values can be outside the bounds of this surface, but U2 must
be greater than U1 and V2 must be greater than V1.

All the data structure tables of this B-Spline surface are modified but the
knots located between U1 and U2 in the u parametric direction, and between
V1 and V2 in the v parametric direction are retained.
The degree of the surface in each parametric direction is not modified.

Evidence: public stub `Part/__init__.pyi` line(s) 1190.

## `Part.BSplineSurface.setUKnot`

```python
def setUKnot(self, index: int, knot: float, mult: int=..., /) -> None:
```

Modifies this B-Spline surface by assigning the value knot to the knot of index
index of the knots table corresponding to the u parametric direction.
This modification remains relatively local, since knot must lie between the values
of the knots which frame the modified knot.

You can also increase the multiplicity of the modified knot to mult. Note however
that it is not possible to decrease the multiplicity of a knot with this function.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 1204.

## `Part.BSplineSurface.setVKnot`

```python
def setVKnot(self, index: int, knot: float, mult: int=..., /) -> None:
```

Modifies this B-Spline surface by assigning the value knot to the knot of index
index of the knots table corresponding to the v parametric direction.
This modification remains relatively local, since knot must lie between the values
of the knots which frame the modified knot.

You can also increase the multiplicity of the modified knot to mult. Note however
that it is not possible to decrease the multiplicity of a knot with this function.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 1216.

## `Part.BSplineSurface.getUKnot`

```python
def getUKnot(self, index: int, /) -> Any:
```

Returns, for this B-Spline surface, in the u parametric direction
the knot of index index of the knots table.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Part/__init__.pyi` line(s) 1228.

## `Part.BSplineSurface.getVKnot`

```python
def getVKnot(self, index: int, /) -> Any:
```

Returns, for this B-Spline surface, in the v parametric direction
the knot of index index of the knots table.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Part/__init__.pyi` line(s) 1235.

## `Part.BSplineSurface.setUKnots`

```python
def setUKnots(self, knots: List[Any], /) -> None:
```

Changes all knots of this B-Spline surface in the u parametric
direction. The multiplicity of the knots is not modified.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Part/__init__.pyi` line(s) 1242.

## `Part.BSplineSurface.setVKnots`

```python
def setVKnots(self, knots: List[Any], /) -> None:
```

Changes all knots of this B-Spline surface in the v parametric
direction. The multiplicity of the knots is not modified.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Part/__init__.pyi` line(s) 1249.

## `Part.BSplineSurface.getUKnots`

```python
def getUKnots(self) -> List[Any]:
```

Returns, for this B-Spline surface, the knots table
in the u parametric direction

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Part/__init__.pyi` line(s) 1256.

## `Part.BSplineSurface.getVKnots`

```python
def getVKnots(self) -> List[Any]:
```

Returns, for this B-Spline surface, the knots table
in the v parametric direction

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Part/__init__.pyi` line(s) 1263.

## `Part.BSplineSurface.setPole`

```python
def setPole(self, u_index: int, v_index: int, pole: Any, weight: float=..., /) -> None:
```

Modifies this B-Spline surface by assigning pole to the pole of
index (u_index, v_index) in the poles table.
The second syntax allows you also to change the weight of the
modified pole. The weight is set to weight. This syntax must
only be used for rational surfaces.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 1270.

## `Part.BSplineSurface.setPoleCol`

```python
def setPoleCol(self, v_index: int, values: List[Any], pole_weights: List[float]=..., /) -> None:
```

Modifies this B-Spline surface by assigning values to all or part
of the column of poles of index v_index, of this B-Spline surface.
You can also change the weights of the modified poles. The weights
are set to the corresponding values of pole_weights.
These syntaxes must only be used for rational surfaces.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 1280.

## `Part.BSplineSurface.setPoleRow`

```python
def setPoleRow(self, u_index: int, values: List[Any], pole_weights: List[float]=..., /) -> None:
```

Modifies this B-Spline surface by assigning values to all or part
of the row of poles of index u_index, of this B-Spline surface.
You can also change the weights of the modified poles. The weights
are set to the corresponding values of pole_weights.
These syntaxes must only be used for rational surfaces.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 1290.

## `Part.BSplineSurface.getPole`

```python
def getPole(self, u_index: int, v_index: int, /) -> Any:
```

Returns the pole of index (u_index, v_index) of this B-Spline surface.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Part/__init__.pyi` line(s) 1300.

## `Part.BSplineSurface.getPoles`

```python
def getPoles(self) -> List[Any]:
```

Returns the table of poles of this B-Spline surface.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Part/__init__.pyi` line(s) 1306.

## `Part.BSplineSurface.setWeight`

```python
def setWeight(self, u_index: int, v_index: int, weight: float, /) -> None:
```

Modifies this B-Spline surface by assigning the value weight to the weight
of the pole of index (u_index, v_index) in the poles tables of this B-Spline
surface.

This function must only be used for rational surfaces.

Evidence: public stub `Part/__init__.pyi` line(s) 1312.

## `Part.BSplineSurface.setWeightCol`

```python
def setWeightCol(self, v_index: int, pole_weights: List[float], /) -> None:
```

Modifies this B-Spline surface by assigning values to all or part of the
weights of the column of poles of index v_index of this B-Spline surface.

The modified part of the column of weights is defined by the bounds
of the array pole_weights.

This function must only be used for rational surfaces.

Evidence: public stub `Part/__init__.pyi` line(s) 1322.

## `Part.BSplineSurface.setWeightRow`

```python
def setWeightRow(self, u_index: int, pole_weights: List[float], /) -> None:
```

Modifies this B-Spline surface by assigning values to all or part of the
weights of the row of poles of index u_index of this B-Spline surface.

The modified part of the row of weights is defined by the bounds of the
array pole_weights.

This function must only be used for rational surfaces.

Evidence: public stub `Part/__init__.pyi` line(s) 1334.

## `Part.BSplineSurface.getWeight`

```python
def getWeight(self, u_index: int, v_index: int, /) -> float:
```

Return the weight of the pole of index (u_index, v_index)
in the poles table for this B-Spline surface.

Evidence: public stub `Part/__init__.pyi` line(s) 1346.

## `Part.BSplineSurface.getWeights`

```python
def getWeights(self) -> List[float]:
```

Returns the table of weights of the poles for this B-Spline surface.

Evidence: public stub `Part/__init__.pyi` line(s) 1353.

## `Part.BSplineSurface.getPolesAndWeights`

```python
def getPolesAndWeights(self) -> List[Any]:
```

Returns the table of poles and weights in homogeneous coordinates.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Part/__init__.pyi` line(s) 1359.

