# `Part.Wire`

[Module](index.md)

```python
class Wire(Shape):
```

TopoShapeWire is the OpenCasCade topological wire wrapper

Author: Juergen Riegel (Juergen.Riegel@web.de)
Licence: LGPL
DeveloperDocu: TopoShapeWire is the OpenCasCade topological wire wrapper

Evidence: public stub `Part/__init__.pyi` line 5262. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.Wire.__init__`

```python
@overload
def __init__(self) -> None:

@overload
def __init__(self, shape: Shape, /) -> None:

@overload
def __init__(self, shapes: Sequence[Shape], /) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Evidence: public stub `Part/__init__.pyi` line(s) 5272, 5276, 5280.

## `Part.Wire.Mass`

```python
Mass: Final[object] = ...
```

Returns the mass of the current system.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 5282.

## `Part.Wire.CenterOfMass`

```python
CenterOfMass: Final[object] = ...
```


    Returns the center of mass of the current system.
    If the gravitational field is uniform, it is the center of gravity.
    The coordinates returned for the center of mass are expressed in the
    absolute Cartesian coordinate system.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 5284.

## `Part.Wire.MatrixOfInertia`

```python
MatrixOfInertia: Final[object] = ...
```


    Returns the matrix of inertia. It is a symmetrical matrix.
    The coefficients of the matrix are the quadratic moments of
    inertia.

     | Ixx Ixy Ixz 0 |
     | Ixy Iyy Iyz 0 |
     | Ixz Iyz Izz 0 |
     | 0   0   0   1 |

    The moments of inertia are denoted by Ixx, Iyy, Izz.
    The products of inertia are denoted by Ixy, Ixz, Iyz.
    The matrix of inertia is returned in the central coordinate
    system (G, Gx, Gy, Gz) where G is the centre of mass of the
    system and Gx, Gy, Gz the directions parallel to the X(1,0,0)
    Y(0,1,0) Z(0,0,1) directions of the absolute cartesian
    coordinate system.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 5286.

## `Part.Wire.StaticMoments`

```python
StaticMoments: Final[object] = ...
```


    Returns Ix, Iy, Iz, the static moments of inertia of the
    current system; i.e. the moments of inertia about the
    three axes of the Cartesian coordinate system.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 5288.

## `Part.Wire.PrincipalProperties`

```python
PrincipalProperties: Final[Dict] = ...
```


    Computes the principal properties of inertia of the current system.
    There is always a set of axes for which the products
    of inertia of a geometric system are equal to 0; i.e. the
    matrix of inertia of the system is diagonal. These axes
    are the principal axes of inertia. Their origin is
    coincident with the center of mass of the system. The
    associated moments are called the principal moments of inertia.
    This function computes the eigen values and the
    eigen vectors of the matrix of inertia of the system.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 5290.

## `Part.Wire.OrderedEdges`

```python
OrderedEdges: Final[List] = ...
```

List of ordered edges in this shape.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 5292.

## `Part.Wire.Continuity`

```python
Continuity: Final[str] = ...
```

Returns the continuity

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 5294.

## `Part.Wire.OrderedVertexes`

```python
OrderedVertexes: Final[List] = ...
```

List of ordered vertexes in this shape.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 5296.

## `Part.Wire.makeOffset`

```python
@deprecated('since FreeCAD 26.3 and will be removed in FreeCAD 27.2; use makeOffset2D instead.')
def makeOffset(self, dist: float, /) -> Shape:
```

Offset the shape by a given amount. DEPRECATED - use makeOffset2D instead.

Evidence: public stub `Part/__init__.pyi` line(s) 5300.

## `Part.Wire.add`

```python
def add(self, edge: object, /) -> None:
```

Add an edge to the wire
add(edge)

Evidence: public stub `Part/__init__.pyi` line(s) 5306.

## `Part.Wire.fixWire`

```python
def fixWire(self, face: Optional[object]=None, tolerance: Optional[float]=None, /) -> None:
```

Fix wire
fixWire([face, tolerance])
--
A face and a tolerance can optionally be supplied to the algorithm:

Evidence: public stub `Part/__init__.pyi` line(s) 5313.

## `Part.Wire.makeHomogenousWires`

```python
def makeHomogenousWires(self, wire: object, /) -> object:
```

Make this and the given wire homogeneous to have the same number of edges
makeHomogenousWires(wire) -> Wire

Evidence: public stub `Part/__init__.pyi` line(s) 5322.

## `Part.Wire.makePipe`

```python
def makePipe(self, profile: object, /) -> object:
```

Make a pipe by sweeping along a wire.
makePipe(profile) -> Shape

Evidence: public stub `Part/__init__.pyi` line(s) 5329.

## `Part.Wire.makePipeShell`

```python
def makePipeShell(self, shapeList: List[object], isSolid: bool=False, isFrenet: bool=False, transition: int=0, /) -> object:
```

Make a loft defined by a list of profiles along a wire.
makePipeShell(shapeList,[isSolid=False,isFrenet=False,transition=0]) -> Shape
--
Transition can be 0 (default), 1 (right corners) or 2 (rounded corners).

Evidence: public stub `Part/__init__.pyi` line(s) 5336.

## `Part.Wire.makeEvolved`

```python
def makeEvolved(self, Profile: Shape, Join: int=..., AxeProf: bool=True, Solid: bool=False, ProfOnSpine: bool=False, Tolerance: float=1e-07) -> Shape:
```

Profile along the spine

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 5345.

## `Part.Wire.approximate`

```python
def approximate(self, Tol2d: float=None, Tol3d: float=0.0001, MaxSegments: int=10, MaxDegree: int=3) -> object:
```

Approximate B-Spline-curve from this wire
approximate([Tol2d,Tol3d=1e-4,MaxSegments=10,MaxDegree=3]) -> BSpline

Evidence: public stub `Part/__init__.pyi` line(s) 5351.

## `Part.Wire.discretize`

```python
@overload
def discretize(self, Number: int, First: float=None, Last: float=None) -> List[object]:

@overload
def discretize(self, QuasiNumber: int, First: float=None, Last: float=None) -> List[object]:

@overload
def discretize(self, Distance: float, First: float=None, Last: float=None) -> List[object]:

@overload
def discretize(self, Deflection: float, First: float=None, Last: float=None) -> List[object]:

@overload
def discretize(self, QuasiDeflection: float, First: float=None, Last: float=None) -> List[object]:

@overload
def discretize(self, Angular: float, Curvature: float, First: float=None, Last: float=None, Minimum: int=2) -> List[object]:

def discretize(self, **kwargs) -> List[object]:
```

discretize(Number=n) -> list

discretize(QuasiNumber=n) -> list

discretize(Distance=d) -> list

discretize(Deflection=d) -> list

discretize(QuasiDeflection=d) -> list

discretize(Angular=a,Curvature=c,[Minimum=m]) -> list

Discretizes the wire and returns a list of points.
discretize(kwargs) -> list
--
The function accepts keywords as argument:
discretize(Number=n) => gives a list of 'n' equidistant points
discretize(QuasiNumber=n) => gives a list of 'n' quasi equidistant points (is faster than the method above)
discretize(Distance=d) => gives a list of equidistant points with distance 'd'
discretize(Deflection=d) => gives a list of points with a maximum deflection 'd' to the wire
discretize(QuasiDeflection=d) => gives a list of points with a maximum deflection 'd' to the wire (faster)
discretize(Angular=a,Curvature=c,[Minimum=m]) => gives a list of points with an angular deflection of 'a'
                                    and a curvature deflection of 'c'. Optionally a minimum number of points
                                    can be set which by default is set to 2.

Optionally you can set the keywords 'First' and 'Last' to define a sub-range of the parameter range
of the wire.

If no keyword is given then it depends on whether the argument is an int or float.
If it's an int then the behaviour is as if using the keyword 'Number', if it's float
then the behaviour is as if using the keyword 'Distance'.

Example:

import Part
V=App.Vector

e1=Part.makeCircle(5,V(0,0,0),V(0,0,1),0,180)
e2=Part.makeCircle(5,V(10,0,0),V(0,0,1),180,360)
w=Part.Wire([e1,e2])

p=w.discretize(Number=50)
s=Part.Compound([Part.Vertex(i) for i in p])
Part.show(s)


p=w.discretize(Angular=0.09,Curvature=0.01,Minimum=100)
s=Part.Compound([Part.Vertex(i) for i in p])
Part.show(s)

Evidence: public stub `Part/__init__.pyi` line(s) 5359, 5366, 5373, 5380, 5387, 5394, 5400.

