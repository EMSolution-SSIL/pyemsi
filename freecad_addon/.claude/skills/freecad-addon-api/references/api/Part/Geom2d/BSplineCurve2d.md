# `Part.Geom2d.BSplineCurve2d`

[Module](index.md)

```python
class BSplineCurve2d(Curve2d):
```

Describes a B-Spline curve in 3D space

Author: Werner Mayer (wmayer@users.sourceforge.net)
Licence: LGPL

Evidence: public stub `Part/Geom2d.pyi` line 102. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.Geom2d.BSplineCurve2d.Degree`

```python
Degree: Final[int] = ...
```

Returns the polynomial degree of this B-Spline curve.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/Geom2d.pyi` line(s) 109.

## `Part.Geom2d.BSplineCurve2d.MaxDegree`

```python
MaxDegree: Final[int] = ...
```

Returns the value of the maximum polynomial degree of any
                    B-Spline curve curve. This value is 25.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/Geom2d.pyi` line(s) 111.

## `Part.Geom2d.BSplineCurve2d.NbPoles`

```python
NbPoles: Final[int] = ...
```

Returns the number of poles of this B-Spline curve.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/Geom2d.pyi` line(s) 113.

## `Part.Geom2d.BSplineCurve2d.NbKnots`

```python
NbKnots: Final[int] = ...
```

Returns the number of knots of this B-Spline curve.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/Geom2d.pyi` line(s) 115.

## `Part.Geom2d.BSplineCurve2d.StartPoint`

```python
StartPoint: Final[object] = ...
```

Returns the start point of this B-Spline curve.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/Geom2d.pyi` line(s) 117.

## `Part.Geom2d.BSplineCurve2d.EndPoint`

```python
EndPoint: Final[object] = ...
```

Returns the end point of this B-Spline curve.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/Geom2d.pyi` line(s) 119.

## `Part.Geom2d.BSplineCurve2d.FirstUKnotIndex`

```python
FirstUKnotIndex: Final[object] = ...
```

Returns the index in the knot array of the knot
                    corresponding to the first or last parameter
                    of this B-Spline curve.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/Geom2d.pyi` line(s) 121.

## `Part.Geom2d.BSplineCurve2d.LastUKnotIndex`

```python
LastUKnotIndex: Final[object] = ...
```

Returns the index in the knot array of the knot
                    corresponding to the first or last parameter
                    of this B-Spline curve.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/Geom2d.pyi` line(s) 123.

## `Part.Geom2d.BSplineCurve2d.KnotSequence`

```python
KnotSequence: Final[list] = ...
```

Returns the knots sequence of this B-Spline curve.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/Geom2d.pyi` line(s) 125.

## `Part.Geom2d.BSplineCurve2d.isRational`

```python
def isRational(self) -> bool:
```

Returns true if this B-Spline curve is rational.
A B-Spline curve is rational if, at the time of construction, the weight table has been initialized.

Evidence: public stub `Part/Geom2d.pyi` line(s) 128.

## `Part.Geom2d.BSplineCurve2d.isPeriodic`

```python
def isPeriodic(self) -> bool:
```

Returns true if this BSpline curve is periodic.

Evidence: public stub `Part/Geom2d.pyi` line(s) 135.

## `Part.Geom2d.BSplineCurve2d.isClosed`

```python
def isClosed(self) -> bool:
```

Returns true if the distance between the start point and end point of
this B-Spline curve is less than or equal to gp::Resolution().

Evidence: public stub `Part/Geom2d.pyi` line(s) 141.

## `Part.Geom2d.BSplineCurve2d.increaseDegree`

```python
def increaseDegree(self, degree: int, /) -> None:
```

increaseDegree(degree)

Increases the degree of this B-Spline curve to degree.
As a result, the poles, weights and multiplicities tables
are modified; the knots table is not changed. Nothing is
done if degree is less than or equal to the current degree.

Evidence: public stub `Part/Geom2d.pyi` line(s) 148.

## `Part.Geom2d.BSplineCurve2d.increaseMultiplicity`

```python
@overload
def increaseMultiplicity(self, index: int, mult: int, /) -> None:

@overload
def increaseMultiplicity(self, start: int, end: int, mult: int, /) -> None:

def increaseMultiplicity(self, *args, **kwargs) -> None:
```

increaseMultiplicity(int index, int mult)
increaseMultiplicity(int start, int end, int mult)
Increases multiplicity of knots up to mult.

index: the index of a knot to modify (1-based)
start, end: index range of knots to modify.
If mult is lower or equal to the current multiplicity nothing is done.
If mult is higher than the degree the degree is used.

Evidence: public stub `Part/Geom2d.pyi` line(s) 160, 164, 167.

## `Part.Geom2d.BSplineCurve2d.incrementMultiplicity`

```python
def incrementMultiplicity(self, start: int, end: int, mult: int, /) -> None:
```

incrementMultiplicity(int start, int end, int mult)
Raises multiplicity of knots by mult.

start, end: index range of knots to modify.

Evidence: public stub `Part/Geom2d.pyi` line(s) 180.

## `Part.Geom2d.BSplineCurve2d.insertKnot`

```python
def insertKnot(self, u: float, mult: int=1, tol: float=0.0, /) -> None:
```

insertKnot(u, mult = 1, tol = 0.0)

Inserts a knot value in the sequence of knots. If u is an existing knot the multiplicity is increased by mult.

Evidence: public stub `Part/Geom2d.pyi` line(s) 189.

## `Part.Geom2d.BSplineCurve2d.insertKnots`

```python
def insertKnots(self, list_of_floats: list[float], list_of_ints: list[int], tol: float=0.0, bool_add: bool=True, /) -> None:
```

insertKnots(list_of_floats, list_of_ints, tol = 0.0, bool_add = True)

Inserts a set of knots values in the sequence of knots.

For each u = list_of_floats[i], mult = list_of_ints[i]

If u is an existing knot the multiplicity is increased by mult if bool_add is
True, otherwise increased to mult.

If u is not on the parameter range nothing is done.

If the multiplicity is negative or null nothing is done. The new multiplicity
is limited to the degree.

The tolerance criterion for knots equality is the max of Epsilon(U) and ParametricTolerance.

Evidence: public stub `Part/Geom2d.pyi` line(s) 197.

## `Part.Geom2d.BSplineCurve2d.removeKnot`

```python
def removeKnot(self, index: int, mult: int, tol: float, /) -> bool:
```

removeKnot(index, mult, tol)

Reduces the multiplicity of the knot of index index to mult.
If mult is equal to 0, the knot is removed.
With a modification of this type, the array of poles is also modified.
Two different algorithms are systematically used to compute the new
poles of the curve. If, for each pole, the distance between the pole
calculated using the first algorithm and the same pole calculated using
the second algorithm, is less than tol, this ensures that the curve
is not modified by more than tol. Under these conditions, true is
returned; otherwise, false is returned.

A low tolerance is used to prevent modification of the curve.
A high tolerance is used to 'smooth' the curve.

Evidence: public stub `Part/Geom2d.pyi` line(s) 217.

## `Part.Geom2d.BSplineCurve2d.segment`

```python
def segment(self, u1: float, u2: float, /) -> None:
```

segment(u1,u2)
Modifies this B-Spline curve by segmenting it.

Evidence: public stub `Part/Geom2d.pyi` line(s) 236.

## `Part.Geom2d.BSplineCurve2d.setKnot`

```python
def setKnot(self, index: int, knot: float, mult: int=..., /) -> None:
```

Set a knot of the B-Spline curve.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/Geom2d.pyi` line(s) 243.

## `Part.Geom2d.BSplineCurve2d.getKnot`

```python
def getKnot(self, index: int, /) -> float:
```

Get a knot of the B-Spline curve.

Evidence: public stub `Part/Geom2d.pyi` line(s) 249.

## `Part.Geom2d.BSplineCurve2d.setKnots`

```python
def setKnots(self, knots: list[float], /) -> None:
```

Set knots of the B-Spline curve.

Evidence: public stub `Part/Geom2d.pyi` line(s) 255.

## `Part.Geom2d.BSplineCurve2d.getKnots`

```python
def getKnots(self) -> list[float]:
```

Get all knots of the B-Spline curve.

Evidence: public stub `Part/Geom2d.pyi` line(s) 261.

## `Part.Geom2d.BSplineCurve2d.setPole`

```python
def setPole(self, index: int, pole: Vector, weight: float=..., /) -> None:
```

Modifies this B-Spline curve by assigning pole to the pole of index index in the poles table.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/Geom2d.pyi` line(s) 267.

## `Part.Geom2d.BSplineCurve2d.getPole`

```python
def getPole(self, index: int, /) -> Vector:
```

Get a pole of the B-Spline curve.

Evidence: public stub `Part/Geom2d.pyi` line(s) 273.

## `Part.Geom2d.BSplineCurve2d.getPoles`

```python
def getPoles(self) -> list[Vector]:
```

Get all poles of the B-Spline curve.

Evidence: public stub `Part/Geom2d.pyi` line(s) 279.

## `Part.Geom2d.BSplineCurve2d.setWeight`

```python
def setWeight(self, index: int, weight: float, /) -> None:
```

Set a weight of the B-Spline curve.

Evidence: public stub `Part/Geom2d.pyi` line(s) 285.

## `Part.Geom2d.BSplineCurve2d.getWeight`

```python
def getWeight(self, index: int, /) -> float:
```

Get a weight of the B-Spline curve.

Evidence: public stub `Part/Geom2d.pyi` line(s) 291.

## `Part.Geom2d.BSplineCurve2d.getWeights`

```python
def getWeights(self) -> list[float]:
```

Get all weights of the B-Spline curve.

Evidence: public stub `Part/Geom2d.pyi` line(s) 297.

## `Part.Geom2d.BSplineCurve2d.getPolesAndWeights`

```python
def getPolesAndWeights(self) -> tuple[list[Vector], list[float]]:
```

Returns the table of poles and weights in homogeneous coordinates.

Evidence: public stub `Part/Geom2d.pyi` line(s) 303.

## `Part.Geom2d.BSplineCurve2d.getResolution`

```python
def getResolution(self, tolerance_3d: float, /) -> float:
```

Computes for this B-Spline curve the parametric tolerance (UTolerance)
for a given 3D tolerance (tolerance_3d).
If f(t) is the equation of this B-Spline curve, the parametric tolerance ensures that:
|t1-t0| < UTolerance =""==> |f(t1)-f(t0)| < tolerance_3d

Evidence: public stub `Part/Geom2d.pyi` line(s) 309.

## `Part.Geom2d.BSplineCurve2d.movePoint`

```python
def movePoint(self, u: float, pole: Vector, index1: int, index2: int, /) -> tuple[int, int]:
```

movePoint(u, pole, index1, index2)

Moves the point of parameter u of this B-Spline curve to pole.
index1 and index2 are the indexes in the table of poles of this B-Spline curve
of the first and last poles designated to be moved.

Returns: (FirstModifiedPole, LastModifiedPole). They are the indexes of the
first and last poles which are effectively modified.

Evidence: public stub `Part/Geom2d.pyi` line(s) 318.

## `Part.Geom2d.BSplineCurve2d.setNotPeriodic`

```python
def setNotPeriodic(self) -> None:
```

Changes this B-Spline curve into a non-periodic curve.
If this curve is already non-periodic, it is not modified.

Evidence: public stub `Part/Geom2d.pyi` line(s) 331.

## `Part.Geom2d.BSplineCurve2d.setPeriodic`

```python
def setPeriodic(self) -> None:
```

Changes this B-Spline curve into a periodic curve.

Evidence: public stub `Part/Geom2d.pyi` line(s) 338.

## `Part.Geom2d.BSplineCurve2d.setOrigin`

```python
def setOrigin(self, index: int, /) -> None:
```

Assigns the knot at the given index in the knots table as the origin of this periodic B-Spline curve.
As a consequence, the knots and poles tables are modified.

Evidence: public stub `Part/Geom2d.pyi` line(s) 344.

## `Part.Geom2d.BSplineCurve2d.getMultiplicity`

```python
def getMultiplicity(self, index: int, /) -> int:
```

Returns the multiplicity of the knot of index from the knots table of this B-Spline curve.

Evidence: public stub `Part/Geom2d.pyi` line(s) 351.

## `Part.Geom2d.BSplineCurve2d.getMultiplicities`

```python
def getMultiplicities(self) -> list[int]:
```

Returns the multiplicities table M of the knots of this B-Spline curve.

Evidence: public stub `Part/Geom2d.pyi` line(s) 357.

## `Part.Geom2d.BSplineCurve2d.approximate`

```python
@overload
def approximate(self, Points: list[Vector], DegMax: int=8, Continuity: str='C2', Tolerance: float=0.001, DegMin: int=3, ParamType: str='ChordLength', Parameters: list[float]=None, LengthWeight: float=0.0, CurvatureWeight: float=0.0, TorsionWeight: float=0.0) -> None:

def approximate(self, **kwargs) -> None:
```

Replaces this B-Spline curve by approximating a set of points.
The function accepts keywords as arguments.

approximate2(Points = list_of_points)

Optional arguments :

DegMin = integer (3) : Minimum degree of the curve.
DegMax = integer (8) : Maximum degree of the curve.
Tolerance = float (1e-3) : approximating tolerance.
Continuity = string ('C2') : Desired continuity of the curve.
Possible values : 'C0','G1','C1','G2','C2','C3','CN'

LengthWeight = float, CurvatureWeight = float, TorsionWeight = float
If one of these arguments is not null, the functions approximates the
points using variational smoothing algorithm, which tries to minimize
additional criterium:
LengthWeight*CurveLength + CurvatureWeight*Curvature + TorsionWeight*Torsion
Continuity must be C0, C1 or C2, else defaults to C2.

Parameters = list of floats : knot sequence of the approximated points.
This argument is only used if the weights above are all null.

ParamType = string ('Uniform','Centripetal' or 'ChordLength')
Parameterization type. Only used if weights and Parameters above aren't specified.

Note : Continuity of the spline defaults to C2. However, it may not be applied if
it conflicts with other parameters ( especially DegMax ).

Evidence: public stub `Part/Geom2d.pyi` line(s) 364, 367.

## `Part.Geom2d.BSplineCurve2d.getCardinalSplineTangents`

```python
@overload
def getCardinalSplineTangents(self, Points: list[Vector], Parameter: float) -> list[Vector]:

@overload
def getCardinalSplineTangents(self, Points: list[Vector], Parameters: list[float]) -> list[Vector]:

def getCardinalSplineTangents(self, **kwargs) -> list[Vector]:
```

Compute the tangents for a Cardinal spline

Evidence: public stub `Part/Geom2d.pyi` line(s) 401, 405, 408.

## `Part.Geom2d.BSplineCurve2d.interpolate`

```python
@overload
def interpolate(self, Points: list[Vector], PeriodicFlag: bool=False, Tolerance: float=1e-06, InitialTangent: Vector=None, FinalTangent: Vector=None, Tangents: list[Vector]=None, TangentFlags: list[bool]=None, Parameters: list[float]=None) -> None:

def interpolate(self, **kwargs) -> None:
```

Replaces this B-Spline curve by interpolating a set of points.
The function accepts keywords as arguments.

interpolate(Points = list_of_points)

Optional arguments :

PeriodicFlag = bool (False) : Sets the curve closed or opened.
Tolerance = float (1e-6) : interpolating tolerance

Parameters : knot sequence of the interpolated points.
If not supplied, the function defaults to chord-length parameterization.
If PeriodicFlag == True, one extra parameter must be appended.

EndPoint Tangent constraints :

InitialTangent = vector, FinalTangent = vector
specify tangent vectors for starting and ending points
of the BSpline. Either none, or both must be specified.

Full Tangent constraints :

Tangents = list_of_vectors, TangentFlags = list_of_bools
Both lists must have the same length as Points list.
Tangents specifies the tangent vector of each point in Points list.
TangentFlags (bool) activates or deactivates the corresponding tangent.
These arguments will be ignored if EndPoint Tangents (above) are also defined.

Note : Continuity of the spline defaults to C2. However, if periodic, or tangents
are supplied, the continuity will drop to C1.

Evidence: public stub `Part/Geom2d.pyi` line(s) 415, 418.

## `Part.Geom2d.BSplineCurve2d.buildFromPoles`

```python
def buildFromPoles(self, poles: list[Vector], periodic: bool=..., degree: int=..., interpolate: bool=..., /) -> None:
```

Builds a B-Spline by a list of poles.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/Geom2d.pyi` line(s) 453.

## `Part.Geom2d.BSplineCurve2d.buildFromPolesMultsKnots`

```python
@overload
def buildFromPolesMultsKnots(self, poles: list[Vector], mults: tuple[int, ...]=None, knots: tuple[float, ...]=None, periodic: bool=False, degree: int=3, weights: tuple[float, ...]=None) -> None:

def buildFromPolesMultsKnots(self, **kwargs) -> None:
```

Builds a B-Spline by a lists of Poles, Mults, Knots.
arguments: poles (sequence of Base.Vector),
[mults , knots, periodic, degree, weights (sequence of float), CheckRational]

Examples:
from FreeCAD import Base
import Part
V=Base.Vector
poles=[V(-10,-10),V(10,-10),V(10,10),V(-10,10)]

# non-periodic spline
n=Part.BSplineCurve()
n.buildFromPolesMultsKnots(poles,(3,1,3),(0,0.5,1),False,2)
Part.show(n.toShape())

# periodic spline
p=Part.BSplineCurve()
p.buildFromPolesMultsKnots(poles,(1,1,1,1,1),(0,0.25,0.5,0.75,1),True,2)
Part.show(p.toShape())

# periodic and rational spline
r=Part.BSplineCurve()
r.buildFromPolesMultsKnots(poles,(1,1,1,1,1),(0,0.25,0.5,0.75,1),True,2,(1,0.8,0.7,0.2))
Part.show(r.toShape())

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/Geom2d.pyi` line(s) 460, 463.

## `Part.Geom2d.BSplineCurve2d.toBezier`

```python
def toBezier(self) -> list:
```

Build a list of Bezier splines.

Evidence: public stub `Part/Geom2d.pyi` line(s) 492.

## `Part.Geom2d.BSplineCurve2d.toBiArcs`

```python
def toBiArcs(self, tolerance: float, /) -> list:
```

toBiArcs(tolerance) -> list.
Build a list of arcs and lines to approximate the B-spline.

Evidence: public stub `Part/Geom2d.pyi` line(s) 498.

## `Part.Geom2d.BSplineCurve2d.join`

```python
def join(self, other: 'BSplineCurve2d', /) -> 'BSplineCurve2d':
```

Build a new spline by joining this and a second spline.

Evidence: public stub `Part/Geom2d.pyi` line(s) 505.

## `Part.Geom2d.BSplineCurve2d.makeC1Continuous`

```python
def makeC1Continuous(self, tol: float=..., /) -> None:
```

makeC1Continuous(tol)

Reduces as far as possible the multiplicities of the knots of this BSpline
(keeping the geometry). It returns a new BSpline, which could still be C0.
tol is a geometrical tolerance.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/Geom2d.pyi` line(s) 511.

