# `Part.Face`

[Module](index.md)

```python
class Face(Shape):
```

TopoShapeFace is the OpenCasCade topological face wrapper

Author: Juergen Riegel (Juergen.Riegel@web.de)
Licence: LGPL

Evidence: public stub `Part/__init__.pyi` line 4948. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.Face.__init__`

```python
@overload
def __init__(self) -> None:

@overload
def __init__(self, shape: Shape, /) -> None:

@overload
def __init__(self, face: Shape, wire: Shape, /) -> None:

@overload
def __init__(self, wires: Sequence[Shape], /) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Evidence: public stub `Part/__init__.pyi` line(s) 4957, 4961, 4965, 4969.

## `Part.Face.Tolerance`

```python
Tolerance: float = ...
```

Set or get the tolerance of the vertex

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 4971.

## `Part.Face.ParameterRange`

```python
ParameterRange: Final[Tuple] = ...
```

Returns a 4 tuple with the parameter range

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 4973.

## `Part.Face.Surface`

```python
Surface: Final[object] = ...
```

Returns the geometric surface of the face

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 4975.

## `Part.Face.Wire`

```python
@property
@deprecated('since FreeCAD 26.3 and will be removed in FreeCAD 27.2; use OuterWire instead.')
def Wire(self) -> object:
```

The outer wire of this face
deprecated -- use OuterWire

Access: getter only declared in the stub.

Evidence: public stub `Part/__init__.pyi` line(s) 4980.

## `Part.Face.OuterWire`

```python
OuterWire: Final[object] = ...
```

The outer wire of this face

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 4986.

## `Part.Face.Mass`

```python
Mass: Final[object] = ...
```

Returns the mass of the current system.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 4988.

## `Part.Face.CenterOfMass`

```python
CenterOfMass: Final[object] = ...
```


    Returns the center of mass of the current system.
    If the gravitational field is uniform, it is the center of gravity.
    The coordinates returned for the center of mass are expressed in the
    absolute Cartesian coordinate system.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 4990.

## `Part.Face.MatrixOfInertia`

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

Evidence: public stub `Part/__init__.pyi` line(s) 4992.

## `Part.Face.StaticMoments`

```python
StaticMoments: Final[object] = ...
```


    Returns Ix, Iy, Iz, the static moments of inertia of the
    current system; i.e. the moments of inertia about the
    three axes of the Cartesian coordinate system.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 4994.

## `Part.Face.PrincipalProperties`

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

Evidence: public stub `Part/__init__.pyi` line(s) 4996.

## `Part.Face.addWire`

```python
def addWire(self, wire: object, /) -> None:
```

Adds a wire to the face.
addWire(wire)

Evidence: public stub `Part/__init__.pyi` line(s) 4999.

## `Part.Face.makeOffset`

```python
@deprecated('since FreeCAD 26.3 and will be removed in FreeCAD 27.2; use makeOffset2D instead.')
def makeOffset(self, dist: float, /) -> object:
```

Offset the face by a given amount.
makeOffset(dist) -> Face
--
Returns Compound of Wires. Deprecated - use makeOffset2D instead.

Evidence: public stub `Part/__init__.pyi` line(s) 5007.

## `Part.Face.makeEvolved`

```python
def makeEvolved(self, Profile: Shape, Join: int, *, AxeProf: bool, Solid: bool, ProfOnSpine: bool, Tolerance: float) -> Shape:
```

Profile along the spine

Evidence: public stub `Part/__init__.pyi` line(s) 5016.

## `Part.Face.getUVNodes`

```python
def getUVNodes(self) -> List[Tuple[float, float]]:
```

Get the list of (u,v) nodes of the tessellation
getUVNodes() -> list
--
An exception is raised if the face is not triangulated.

Evidence: public stub `Part/__init__.pyi` line(s) 5022.

## `Part.Face.tangentAt`

```python
def tangentAt(self, u: float, v: float, /) -> Vector:
```

Get the tangent in u and v isoparametric at the given point if defined
tangentAt(u,v) -> Vector

Evidence: public stub `Part/__init__.pyi` line(s) 5031.

## `Part.Face.valueAt`

```python
def valueAt(self, u: float, v: float, /) -> Vector:
```

Get the point at the given parameter [0|Length] if defined
valueAt(u,v) -> Vector

Evidence: public stub `Part/__init__.pyi` line(s) 5038.

## `Part.Face.normalAt`

```python
def normalAt(self, u: float, v: float, /) -> Vector:
```

Get the normal vector at the given parameter [0|Length] if defined
normalAt(u,v) -> Vector

Evidence: public stub `Part/__init__.pyi` line(s) 5045.

## `Part.Face.derivative1At`

```python
def derivative1At(self, u: float, v: float, /) -> Tuple[Vector, Vector]:
```

Get the first derivative at the given parameter [0|Length] if defined
derivative1At(u,v) -> (vectorU,vectorV)

Evidence: public stub `Part/__init__.pyi` line(s) 5052.

## `Part.Face.derivative2At`

```python
def derivative2At(self, u: float, v: float, /) -> Tuple[Vector, Vector]:
```

Vector = d2At(pos) - Get the second derivative at the given parameter [0|Length] if defined
derivative2At(u,v) -> (vectorU,vectorV)

Evidence: public stub `Part/__init__.pyi` line(s) 5059.

## `Part.Face.curvatureAt`

```python
def curvatureAt(self, u: float, v: float, /) -> float:
```

Get the curvature at the given parameter [0|Length] if defined
curvatureAt(u,v) -> Float

Evidence: public stub `Part/__init__.pyi` line(s) 5066.

## `Part.Face.isPartOfDomain`

```python
def isPartOfDomain(self, u: float, v: float, /) -> bool:
```

Check if a given (u,v) pair is inside the domain of a face
isPartOfDomain(u,v) -> bool

Evidence: public stub `Part/__init__.pyi` line(s) 5073.

## `Part.Face.makeHalfSpace`

```python
def makeHalfSpace(self, pos: object, /) -> object:
```

Make a half-space solid by this face and a reference point.
makeHalfSpace(pos) -> Shape

Evidence: public stub `Part/__init__.pyi` line(s) 5080.

## `Part.Face.validate`

```python
def validate(self) -> None:
```

Validate the face.
validate()

Evidence: public stub `Part/__init__.pyi` line(s) 5087.

## `Part.Face.countNodes`

```python
def countNodes(self) -> int:
```

Returns the number of nodes of the triangulation.

Evidence: public stub `Part/__init__.pyi` line(s) 5094.

## `Part.Face.countTriangles`

```python
def countTriangles(self) -> int:
```

Returns the number of triangles of the triangulation.

Evidence: public stub `Part/__init__.pyi` line(s) 5100.

## `Part.Face.curveOnSurface`

```python
def curveOnSurface(self, Edge: object, /) -> Optional[Tuple[object, float, float]]:
```

Returns the curve associated to the edge in the parametric space of the face.
curveOnSurface(Edge) -> (curve, min, max) or None
--
If this curve exists then a tuple of curve and parameter range is returned.
Returns None if this curve does not exist.

Evidence: public stub `Part/__init__.pyi` line(s) 5106.

## `Part.Face.cutHoles`

```python
def cutHoles(self, list_of_wires: List[object], /) -> None:
```

Cut holes in the face.
cutHoles(list_of_wires)

Evidence: public stub `Part/__init__.pyi` line(s) 5116.

