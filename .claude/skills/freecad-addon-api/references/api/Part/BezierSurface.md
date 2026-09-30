# `Part.BezierSurface`

[Module](index.md)

```python
class BezierSurface(GeometrySurface):
```

Describes a rational or non-rational Bezier surface
-- A non-rational Bezier surface is defined by a table of poles (also known as control points).
-- A rational Bezier surface is defined by a table of poles with varying associated weights.

Evidence: public stub `Part/__init__.pyi` line 1735. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.BezierSurface.UDegree`

```python
UDegree: Final[int]
```


    Returns the polynomial degree in u direction of this Bezier surface,
    which is equal to the number of poles minus 1.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 1741.

## `Part.BezierSurface.VDegree`

```python
VDegree: Final[int]
```


    Returns the polynomial degree in v direction of this Bezier surface,
    which is equal to the number of poles minus 1.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 1743.

## `Part.BezierSurface.MaxDegree`

```python
MaxDegree: Final[int]
```


    Returns the value of the maximum polynomial degree of any
    Bezier surface. This value is 25.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 1745.

## `Part.BezierSurface.NbUPoles`

```python
NbUPoles: Final[int]
```

Returns the number of poles in u direction of this Bezier surface.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 1747.

## `Part.BezierSurface.NbVPoles`

```python
NbVPoles: Final[int]
```

Returns the number of poles in v direction of this Bezier surface.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 1749.

## `Part.BezierSurface.bounds`

```python
def bounds(self) -> Tuple[float, float, float, float]:
```

Returns the parametric bounds (U1, U2, V1, V2) of this Bezier surface.

Evidence: public stub `Part/__init__.pyi` line(s) 1752.

## `Part.BezierSurface.isURational`

```python
def isURational(self) -> bool:
```

Returns false if the equation of this Bezier surface is polynomial
(e.g. non-rational) in the u or v parametric direction.
In other words, returns false if for each row of poles, the associated
weights are identical.

Evidence: public stub `Part/__init__.pyi` line(s) 1758.

## `Part.BezierSurface.isVRational`

```python
def isVRational(self) -> bool:
```

Returns false if the equation of this Bezier surface is polynomial
(e.g. non-rational) in the u or v parametric direction.
In other words, returns false if for each column of poles, the associated
weights are identical.

Evidence: public stub `Part/__init__.pyi` line(s) 1767.

## `Part.BezierSurface.isUPeriodic`

```python
def isUPeriodic(self) -> bool:
```

Returns false.

Evidence: public stub `Part/__init__.pyi` line(s) 1776.

## `Part.BezierSurface.isVPeriodic`

```python
def isVPeriodic(self) -> bool:
```

Returns false.

Evidence: public stub `Part/__init__.pyi` line(s) 1782.

## `Part.BezierSurface.isUClosed`

```python
def isUClosed(self) -> bool:
```

Checks if this surface is closed in the u parametric direction.
Returns true if, in the table of poles the first row and the last
row are identical.

Evidence: public stub `Part/__init__.pyi` line(s) 1788.

## `Part.BezierSurface.isVClosed`

```python
def isVClosed(self) -> bool:
```

Checks if this surface is closed in the v parametric direction.
Returns true if, in the table of poles the first column and the
last column are identical.

Evidence: public stub `Part/__init__.pyi` line(s) 1796.

## `Part.BezierSurface.increase`

```python
def increase(self, DegreeU: int, DegreeV: int, /) -> None:
```

increase(DegreeU: int, DegreeV: int)
Increases the degree of this Bezier surface in the two
parametric directions.

Evidence: public stub `Part/__init__.pyi` line(s) 1804.

## `Part.BezierSurface.insertPoleColAfter`

```python
def insertPoleColAfter(self, index: int, poles: Any, weights: Any=..., /) -> None:
```

Inserts into the table of poles of this surface, after the column
of poles of index.
If this Bezier surface is non-rational, it can become rational if
the weights associated with the new poles are different from each
other, or collectively different from the existing weights in the
table.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 1812.

## `Part.BezierSurface.insertPoleRowAfter`

```python
def insertPoleRowAfter(self, index: int, poles: Any, weights: Any=..., /) -> None:
```

Inserts into the table of poles of this surface, after the row
of poles of index.
If this Bezier surface is non-rational, it can become rational if
the weights associated with the new poles are different from each
other, or collectively different from the existing weights in the
table.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 1823.

## `Part.BezierSurface.insertPoleColBefore`

```python
def insertPoleColBefore(self, index: int, poles: Any, weights: Any=..., /) -> None:
```

Inserts into the table of poles of this surface, before the column
of poles of index.
If this Bezier surface is non-rational, it can become rational if
the weights associated with the new poles are different from each
other, or collectively different from the existing weights in the
table.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 1834.

## `Part.BezierSurface.insertPoleRowBefore`

```python
def insertPoleRowBefore(self, index: int, poles: Any, weights: Any=..., /) -> None:
```

Inserts into the table of poles of this surface, before the row
of poles of index.
If this Bezier surface is non-rational, it can become rational if
the weights associated with the new poles are different from each
other, or collectively different from the existing weights in the
table.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 1845.

## `Part.BezierSurface.removePoleCol`

```python
def removePoleCol(self, VIndex: int, /) -> None:
```

removePoleRow(VIndex: int)
Removes the column of poles of index VIndex from the table of
poles of this Bezier surface.
If this Bezier curve is rational, it can become non-rational.

Evidence: public stub `Part/__init__.pyi` line(s) 1856.

## `Part.BezierSurface.removePoleRow`

```python
def removePoleRow(self, UIndex: int, /) -> None:
```

removePoleRow(UIndex: int)
Removes the row of poles of index UIndex from the table of
poles of this Bezier surface.
If this Bezier curve is rational, it can become non-rational.

Evidence: public stub `Part/__init__.pyi` line(s) 1865.

## `Part.BezierSurface.segment`

```python
def segment(self, U1: float, U2: float, V1: float, V2: float, /) -> None:
```

segment(U1: double, U2: double, V1: double, V2: double)
Modifies this Bezier surface by segmenting it between U1 and U2
in the u parametric direction, and between V1 and V2 in the v
parametric direction.
U1, U2, V1, and V2 can be outside the bounds of this surface.

-- U1 and U2 isoparametric Bezier curves, segmented between
    V1 and V2, become the two bounds of the surface in the v
    parametric direction (0. and 1. u isoparametric curves).
-- V1 and V2 isoparametric Bezier curves, segmented between
    U1 and U2, become the two bounds of the surface in the u
    parametric direction (0. and 1. v isoparametric curves).

The poles and weights tables are modified, but the degree of
this surface in the u and v parametric directions does not
change.U1 can be greater than U2, and V1 can be greater than V2.
In these cases, the corresponding parametric direction is inverted.
The orientation of the surface is inverted if one (and only one)
parametric direction is inverted.

Evidence: public stub `Part/__init__.pyi` line(s) 1874.

## `Part.BezierSurface.setPole`

```python
def setPole(self, u_index: int, v_index: int, pole: Vector, weight: float=..., /) -> None:
```

Set a pole of the Bezier surface.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 1898.

## `Part.BezierSurface.setPoleCol`

```python
def setPoleCol(self, index: int, poles: Any, weights: Any=..., /) -> None:
```

Set the column of poles of the Bezier surface.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 1904.

## `Part.BezierSurface.setPoleRow`

```python
def setPoleRow(self, index: int, poles: Any, weights: Any=..., /) -> None:
```

Set the row of poles of the Bezier surface.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 1910.

## `Part.BezierSurface.getPole`

```python
def getPole(self, UIndex: int, VIndex: int, /) -> Any:
```

Get a pole of index (UIndex, VIndex) of the Bezier surface.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Part/__init__.pyi` line(s) 1916.

## `Part.BezierSurface.getPoles`

```python
def getPoles(self) -> Any:
```

Get all poles of the Bezier surface.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Part/__init__.pyi` line(s) 1922.

## `Part.BezierSurface.setWeight`

```python
def setWeight(self, UIndex: int, VIndex: int, weight: float, /) -> None:
```

Set the weight of pole of the index (UIndex, VIndex)
for the Bezier surface.

Evidence: public stub `Part/__init__.pyi` line(s) 1928.

## `Part.BezierSurface.setWeightCol`

```python
def setWeightCol(self, VIndex: int, weights: Any, /) -> None:
```

Set the weights of the poles in the column of poles
of index VIndex of the Bezier surface.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Part/__init__.pyi` line(s) 1935.

## `Part.BezierSurface.setWeightRow`

```python
def setWeightRow(self, UIndex: int, weights: Any, /) -> None:
```

Set the weights of the poles in the row of poles
of index UIndex of the Bezier surface.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Part/__init__.pyi` line(s) 1942.

## `Part.BezierSurface.getWeight`

```python
def getWeight(self, UIndex: int, VIndex: int, /) -> float:
```

Get a weight of the pole of index (UIndex, VIndex)
of the Bezier surface.

Evidence: public stub `Part/__init__.pyi` line(s) 1949.

## `Part.BezierSurface.getWeights`

```python
def getWeights(self) -> Any:
```

Get all weights of the Bezier surface.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Part/__init__.pyi` line(s) 1956.

## `Part.BezierSurface.getResolution`

```python
def getResolution(self, Tolerance3D: float, /) -> Tuple[float, float]:
```

Computes two tolerance values for this Bezier surface, based on the
given tolerance in 3D space Tolerance3D. The tolerances computed are:
-- UTolerance in the u parametric direction and
-- VTolerance in the v parametric direction.

If f(u,v) is the equation of this Bezier surface, UTolerance and VTolerance
guarantee that:
|u1 - u0| < UTolerance
|v1 - v0| < VTolerance
====> ||f(u1, v1) - f(u2, v2)|| < Tolerance3D

Evidence: public stub `Part/__init__.pyi` line(s) 1962.

## `Part.BezierSurface.exchangeUV`

```python
def exchangeUV(self) -> None:
```

Exchanges the u and v parametric directions on this Bezier surface.
As a consequence:
-- the poles and weights tables are transposed,
-- degrees, rational characteristics and so on are exchanged between
   the two parametric directions, and
-- the orientation of the surface is reversed.

Evidence: public stub `Part/__init__.pyi` line(s) 1977.

