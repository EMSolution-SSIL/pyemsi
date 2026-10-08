# `Part.BSplineCurve`

[Module](index.md)

```python
class BSplineCurve(BoundedCurve):
```

Describes a B-Spline curve in 3D space

Author: Werner Mayer (wmayer@users.sourceforge.net)
Licence: LGPL

Evidence: public stub `Part/__init__.pyi` line 532. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.BSplineCurve.Degree`

```python
Degree: Final[int] = 0
```

Returns the polynomial degree of this B-Spline curve.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 539.

## `Part.BSplineCurve.MaxDegree`

```python
MaxDegree: Final[int] = 25
```


    Returns the value of the maximum polynomial degree of any
    B-Spline curve curve. This value is 25.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 541.

## `Part.BSplineCurve.NbPoles`

```python
NbPoles: Final[int] = 0
```

Returns the number of poles of this B-Spline curve.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 543.

## `Part.BSplineCurve.NbKnots`

```python
NbKnots: Final[int] = 0
```

Returns the number of knots of this B-Spline curve.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 545.

## `Part.BSplineCurve.StartPoint`

```python
StartPoint: Final[Vector] = Vector()
```

Returns the start point of this B-Spline curve.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 547.

## `Part.BSplineCurve.EndPoint`

```python
EndPoint: Final[Vector] = Vector()
```

Returns the end point of this B-Spline curve.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 549.

## `Part.BSplineCurve.FirstUKnotIndex`

```python
FirstUKnotIndex: Final[int] = 0
```


    Returns the index in the knot array of the knot
    corresponding to the first or last parameter
    of this B-Spline curve.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 551.

## `Part.BSplineCurve.LastUKnotIndex`

```python
LastUKnotIndex: Final[int] = 0
```


    Returns the index in the knot array of the knot
    corresponding to the first or last parameter
    of this B-Spline curve.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 553.

## `Part.BSplineCurve.KnotSequence`

```python
KnotSequence: Final[List[float]] = []
```

Returns the knots sequence of this B-Spline curve.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 555.

## `Part.BSplineCurve.__reduce__`

```python
def __reduce__(self) -> Any:
```

__reduce__()
Serialization of Part.BSplineCurve objects

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Part/__init__.pyi` line(s) 558.

## `Part.BSplineCurve.isRational`

```python
def isRational(self) -> bool:
```

Returns true if this B-Spline curve is rational.
A B-Spline curve is rational if, at the time of construction,
the weight table has been initialized.

Evidence: public stub `Part/__init__.pyi` line(s) 565.

## `Part.BSplineCurve.isPeriodic`

```python
def isPeriodic(self) -> bool:
```

Returns true if this BSpline curve is periodic.

Evidence: public stub `Part/__init__.pyi` line(s) 573.

## `Part.BSplineCurve.isClosed`

```python
def isClosed(self) -> bool:
```

Returns true if the distance between the start point and end point of
this B-Spline curve is less than or equal to gp::Resolution().

Evidence: public stub `Part/__init__.pyi` line(s) 579.

## `Part.BSplineCurve.increaseDegree`

```python
def increaseDegree(self, degree: int, /) -> None:
```

increaseDegree(degree)
Increases the degree of this B-Spline curve to degree.
As a result, the poles, weights and multiplicities tables
are modified; the knots table is not changed. Nothing is
done if degree is less than or equal to the current degree.

Evidence: public stub `Part/__init__.pyi` line(s) 586.

## `Part.BSplineCurve.increaseMultiplicity`

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

Evidence: public stub `Part/__init__.pyi` line(s) 597, 601, 604.

## `Part.BSplineCurve.incrementMultiplicity`

```python
def incrementMultiplicity(self, start: int, end: int, mult: int, /) -> None:
```

incrementMultiplicity(int start, int end, int mult)

Raises multiplicity of knots by mult.

start, end: index range of knots to modify.

Evidence: public stub `Part/__init__.pyi` line(s) 617.

## `Part.BSplineCurve.insertKnot`

```python
def insertKnot(self, u: float, mult: int=1, tol: float=0.0, add: bool=..., /) -> None:
```

insertKnot(u, mult = 1, tol = 0.0)

Inserts a knot value in the sequence of knots. If u is an existing knot the
multiplicity is increased by mult.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 627.

## `Part.BSplineCurve.insertKnots`

```python
def insertKnots(self, list_of_floats: List[float], list_of_ints: List[int], tol: float=0.0, bool_add: bool=True, /) -> None:
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

Evidence: public stub `Part/__init__.pyi` line(s) 636.

## `Part.BSplineCurve.removeKnot`

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
the second algorithm, is less than Tolerance, this ensures that the curve
is not modified by more than Tolerance. Under these conditions, true is
returned; otherwise, false is returned.

A low tolerance is used to prevent modification of the curve.
A high tolerance is used to 'smooth' the curve.

Evidence: public stub `Part/__init__.pyi` line(s) 656.

## `Part.BSplineCurve.segment`

```python
def segment(self, u1: float, u2: float, /) -> None:
```

segment(u1,u2)

Modifies this B-Spline curve by segmenting it.

Evidence: public stub `Part/__init__.pyi` line(s) 675.

## `Part.BSplineCurve.split`

```python
def split(self, u: float, tolerance: float=0.0, /) -> tuple[BSplineCurve, BSplineCurve]:
```

split(u, tolerance=0.0)

Splits this B-Spline curve at parameter u and returns the two resulting curves.

Evidence: public stub `Part/__init__.pyi` line(s) 683.

## `Part.BSplineCurve.setKnot`

```python
def setKnot(self, index: int, knot: float, mult: int=..., /) -> None:
```

Set a knot of the B-Spline curve.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 691.

## `Part.BSplineCurve.getKnot`

```python
def getKnot(self, index: int, /) -> float:
```

Get a knot of the B-Spline curve.

Evidence: public stub `Part/__init__.pyi` line(s) 697.

## `Part.BSplineCurve.setKnots`

```python
def setKnots(self, knots: List[float], /) -> None:
```

Set knots of the B-Spline curve.

Evidence: public stub `Part/__init__.pyi` line(s) 703.

## `Part.BSplineCurve.getKnots`

```python
def getKnots(self) -> List[float]:
```

Get all knots of the B-Spline curve.

Evidence: public stub `Part/__init__.pyi` line(s) 709.

## `Part.BSplineCurve.setPole`

```python
def setPole(self, index: int, pole: Vector, weight: float=..., /) -> None:
```

Modifies this B-Spline curve by assigning `pole`
to the pole of index `index` in the poles table.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 715.

## `Part.BSplineCurve.getPole`

```python
def getPole(self, index: int, /) -> Vector:
```

Get a pole of the B-Spline curve.

Evidence: public stub `Part/__init__.pyi` line(s) 722.

## `Part.BSplineCurve.getPoles`

```python
def getPoles(self) -> List[Vector]:
```

Get all poles of the B-Spline curve.

Evidence: public stub `Part/__init__.pyi` line(s) 728.

## `Part.BSplineCurve.setWeight`

```python
def setWeight(self, index: int, weight: float, /) -> None:
```

Set a weight of the B-Spline curve.

Evidence: public stub `Part/__init__.pyi` line(s) 734.

## `Part.BSplineCurve.getWeight`

```python
def getWeight(self, index: int, /) -> float:
```

Get a weight of the B-Spline curve.

Evidence: public stub `Part/__init__.pyi` line(s) 740.

## `Part.BSplineCurve.getWeights`

```python
def getWeights(self) -> List[float]:
```

Get all weights of the B-Spline curve.

Evidence: public stub `Part/__init__.pyi` line(s) 746.

## `Part.BSplineCurve.getPolesAndWeights`

```python
def getPolesAndWeights(self) -> List[float]:
```

Returns the table of poles and weights in homogeneous coordinates.

Evidence: public stub `Part/__init__.pyi` line(s) 752.

## `Part.BSplineCurve.getResolution`

```python
def getResolution(self, tolerance_3d: float, /) -> float:
```

Computes for this B-Spline curve the parametric tolerance (UTolerance)
for a given 3D tolerance (tolerance_3d).
If f(t) is the equation of this B-Spline curve, the parametric tolerance
ensures that:
|t1-t0| < UTolerance =""==> |f(t1)-f(t0)| < tolerance_3d

Evidence: public stub `Part/__init__.pyi` line(s) 758.

## `Part.BSplineCurve.movePoint`

```python
def movePoint(self, u: float, pole: Vector, index1: int, index2: int, /) -> tuple[int, int]:
```

movePoint(u, pole, index1, index2)

Moves the point of parameter u of this B-Spline curve to pole.
index1 and index2 are the indexes in the table of poles of this B-Spline curve
of the first and last poles designated to be moved.

Returns: (FirstModifiedPole, LastModifiedPole). They are the indexes of the
first and last poles which are effectively modified.

Evidence: public stub `Part/__init__.pyi` line(s) 768.

## `Part.BSplineCurve.setNotPeriodic`

```python
def setNotPeriodic(self) -> None:
```

Changes this B-Spline curve into a non-periodic curve.
If this curve is already non-periodic, it is not modified.

Evidence: public stub `Part/__init__.pyi` line(s) 781.

## `Part.BSplineCurve.setPeriodic`

```python
def setPeriodic(self) -> None:
```

Changes this B-Spline curve into a periodic curve.

Evidence: public stub `Part/__init__.pyi` line(s) 788.

## `Part.BSplineCurve.setOrigin`

```python
def setOrigin(self, index: int, /) -> None:
```

Assigns the knot at the given index in the knots table
as the origin of this periodic B-Spline curve. As a consequence,
the knots and poles tables are modified.

Evidence: public stub `Part/__init__.pyi` line(s) 794.

## `Part.BSplineCurve.getMultiplicity`

```python
def getMultiplicity(self, index: int, /) -> int:
```

Returns the multiplicity of the knot of index
from the knots table of this B-Spline curve.

Evidence: public stub `Part/__init__.pyi` line(s) 802.

## `Part.BSplineCurve.getMultiplicities`

```python
def getMultiplicities(self) -> List[int]:
```

Returns the multiplicities table M of the knots of this B-Spline curve.

Evidence: public stub `Part/__init__.pyi` line(s) 809.

## `Part.BSplineCurve.approximate`

```python
@overload
def approximate(self, MaxDegree: int, MaxSegments: int=8, Continuity: str='C2', Tolerance: float=0.001) -> None:

@overload
def approximate(self, Points: List[Vector], DegMax: int=8, Continuity: str='C2', Tolerance: float=0.001, DegMin: int=3, ParamType: str='ChordLength', Parameters: List[float]=None, LengthWeight: float=0.0, CurvatureWeight: float=0.0, TorsionWeight: float=0.0) -> None:

def approximate(self, **kwargs) -> None:
```

Replaces this B-Spline curve by approximating a set of points.

The function accepts keywords as arguments.

approximate(Points = list_of_points)

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
        Continuity must be C0, C1(with DegMax >= 3) or C2(with DegMax >= 5).

Parameters = list of floats : knot sequence of the approximated points.
This argument is only used if the weights above are all null.

ParamType = string ('Uniform','Centripetal' or 'ChordLength')
Parameterization type. Only used if weights and Parameters above aren't specified.

Note : Continuity of the spline defaults to C2. However, it may not be applied if
it conflicts with other parameters ( especially DegMax ).

Evidence: public stub `Part/__init__.pyi` line(s) 816, 820, 823.

## `Part.BSplineCurve.getCardinalSplineTangents`

```python
@overload
def getCardinalSplineTangents(self, Points: List[Vector], Parameter: float) -> List[Vector]:

@overload
def getCardinalSplineTangents(self, Points: List[Vector], Parameters: List[float]) -> List[Vector]:

def getCardinalSplineTangents(self, **kwargs) -> List[Vector]:
```

Compute the tangents for a Cardinal spline

Evidence: public stub `Part/__init__.pyi` line(s) 858, 862, 865.

## `Part.BSplineCurve.interpolate`

```python
@overload
def interpolate(self, Points: List[Vector], PeriodicFlag: bool=False, Tolerance: float=1e-06, InitialTangent: Vector=None, FinalTangent: Vector=None, Tangents: List[Vector]=None, TangentFlags: List[bool]=None, Parameters: List[float]=None, Scale: bool=True) -> None:

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

Evidence: public stub `Part/__init__.pyi` line(s) 872, 875.

## `Part.BSplineCurve.buildFromPoles`

```python
def buildFromPoles(self, poles: List[Vector], periodic: bool=False, degree: int=3, interpolate: bool=False, /) -> None:
```

Builds a B-Spline by a list of poles.
arguments: poles (sequence of Base.Vector), [periodic (default is False), degree (default is 3), interpolate (default is False)]

Examples:
from FreeCAD import Base
import Part
V = Base.Vector
poles = [V(-2, 2, 0),V(0, 2, 1),V(2, 2, 0),V(2, -2, 0),V(0, -2, 1),V(-2, -2, 0)]

# non-periodic spline
n=Part.BSplineCurve()
n.buildFromPoles(poles)
Part.show(n.toShape())

# periodic spline
n=Part.BSplineCurve()
n.buildFromPoles(poles, True)
Part.show(n.toShape())

Evidence: public stub `Part/__init__.pyi` line(s) 911.

## `Part.BSplineCurve.buildFromPolesMultsKnots`

```python
@overload
def buildFromPolesMultsKnots(self, poles: List[Vector], mults: List[int]=None, knots: List[float]=None, periodic: bool=False, degree: int=3, weights: List[float]=None, CheckRational: bool=False) -> None:

def buildFromPolesMultsKnots(self, **kwargs) -> None:
```

Builds a B-Spline by a lists of Poles, Mults, Knots.
arguments: poles (sequence of Base.Vector), [mults , knots, periodic, degree, weights (sequence of float), CheckRational]

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

Evidence: public stub `Part/__init__.pyi` line(s) 935, 938.

## `Part.BSplineCurve.toBezier`

```python
def toBezier(self) -> List[BezierCurve]:
```

Build a list of Bezier splines.

Evidence: public stub `Part/__init__.pyi` line(s) 966.

## `Part.BSplineCurve.toBiArcs`

```python
def toBiArcs(self, tolerance: float, /) -> List[Arc]:
```

Build a list of arcs and lines to approximate the B-spline.
toBiArcs(tolerance) -> list.

Evidence: public stub `Part/__init__.pyi` line(s) 972.

## `Part.BSplineCurve.join`

```python
def join(self, other: 'BSplineCurve', /) -> bool:
```

Build a new spline by joining this and a second spline.

Evidence: public stub `Part/__init__.pyi` line(s) 979.

## `Part.BSplineCurve.makeC1Continuous`

```python
def makeC1Continuous(self, tol: float=1e-06, ang_tol: float=1e-07, /) -> None:
```

makeC1Continuous(tol = 1e-6, ang_tol = 1e-7)
Reduces as far as possible the multiplicities of the knots of this BSpline
(keeping the geometry). It returns a new BSpline, which could still be C0.
tol is a geometrical tolerance.
The tol_ang is angular tolerance, in radians. It sets tolerable angle mismatch
of the tangents on the left and on the right to decide if the curve is G1 or
not at a given point.

Evidence: public stub `Part/__init__.pyi` line(s) 985.

## `Part.BSplineCurve.scaleKnotsToBounds`

```python
def scaleKnotsToBounds(self, u0: float=0.0, u1: float=1.0, /) -> None:
```

Scales the knots list to fit the specified bounds.
The shape of the curve is not modified.
bspline_curve.scaleKnotsToBounds(u0, u1)
Default arguments are (0.0, 1.0)

Evidence: public stub `Part/__init__.pyi` line(s) 997.

