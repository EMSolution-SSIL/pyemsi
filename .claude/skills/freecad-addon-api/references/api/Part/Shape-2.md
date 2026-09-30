# `Part.Shape`

[Module](index.md)

```python
class Shape(ComplexGeoData):
```

TopoShape is the OpenCasCade topological shape wrapper.
Sub-elements such as vertices, edges or faces are accessible as:
* Vertex#, where # is in range(1, number of vertices)
* Edge#, where # is in range(1, number of edges)
* Face#, where # is in range(1, number of faces)

Evidence: public stub `Part/__init__.pyi` line 3362. Inherited members are on the named base's reference; aliases keep their imported identity.

[part 1](Shape.md) | [part 2](Shape-2.md)

## `Part.Shape.makeOffset2D`

```python
def makeOffset2D(self, offset: float, *, join: int=0, fill: bool=False, openResult: bool=False, intersection: bool=False) -> Shape:
```

Makes an offset shape (2d offsetting).
makeOffset2D(offset, [join=0, fill=False, openResult=False, intersection=False]) -> Shape
--
The function supports keyword arguments.
Input shape (self) can be edge, wire, face, or a compound of those.

* offset: distance to expand the shape by. Negative value will shrink the shape.

* join: method of offsetting non-tangent joints. 0 = arcs, 1 = tangent, 2 = intersection

* fill: if true, the output is a face filling the space covered by offset. If
false, the output is a wire.

* openResult: affects the way open wires are processed. If False, an open wire
is made. If True, a closed wire is made from a double-sided offset, with rounds
around open vertices.

* intersection: affects the way compounds are processed. If False, all children
are offset independently. If True, and children are edges/wires, the children
are offset in a collective manner. If compounding is nested, collectiveness
does not spread across compounds (only direct children of a compound are taken
collectively).

Returns: result of offsetting (wire or face or compound of those). Compounding
structure follows that of source shape.

Evidence: public stub `Part/__init__.pyi` line(s) 3914.

## `Part.Shape.makeEvolved`

```python
def makeEvolved(self, Profile: Shape, Join: int=..., AxeProf: bool=..., *, Solid: bool=..., ProfOnSpine: bool=..., Tolerance: float=...) -> Shape:
```

Profile along the spine

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 3944.

## `Part.Shape.makeWires`

```python
def makeWires(self, op: str, /) -> Shape:
```

Make wire(s) using the edges of this shape
makeWires(op)
--
The function will sort any edges inside the current shape, and connect them
into wire. If more than one wire is found, then it will make a compound out of
all found wires.

This function is element mapping aware. If the input shape has non-zero Tag,
it will map any edge and vertex element name inside the input shape into the
itself.

op: an optional string to be appended when auto generates element mapping.

Evidence: public stub `Part/__init__.pyi` line(s) 3950.

## `Part.Shape.reverse`

```python
def reverse(self) -> None:
```

Reverses the orientation of this shape.
reverse()

Evidence: public stub `Part/__init__.pyi` line(s) 3967.

## `Part.Shape.reversed`

```python
def reversed(self) -> Shape:
```

Reverses the orientation of a copy of this shape.
reversed() -> Shape

Evidence: public stub `Part/__init__.pyi` line(s) 3974.

## `Part.Shape.complement`

```python
def complement(self) -> None:
```

Computes the complement of the orientation of this shape,
i.e. reverses the interior/exterior status of boundaries of this shape.
complement()

Evidence: public stub `Part/__init__.pyi` line(s) 3981.

## `Part.Shape.nullify`

```python
def nullify(self) -> None:
```

Destroys the reference to the underlying shape stored in this shape.
As a result, this shape becomes null.
nullify()

Evidence: public stub `Part/__init__.pyi` line(s) 3989.

## `Part.Shape.isClosed`

```python
def isClosed(self) -> bool:
```

Checks if the shape is closed.
isClosed() -> bool
--
If the shape is a shell it returns True if it has no free boundaries (edges).
If the shape is a wire it returns True if it has no free ends (vertices).
(Internal and External sub-shapes are ignored in these checks)
If the shape is an edge it returns True if its vertices are the same.

Evidence: public stub `Part/__init__.pyi` line(s) 3997.

## `Part.Shape.isPartner`

```python
def isPartner(self, shape: Shape, /) -> bool:
```

Checks if both shapes share the same geometry.
Placement and orientation may differ.
isPartner(shape) -> bool

Evidence: public stub `Part/__init__.pyi` line(s) 4009.

## `Part.Shape.isSame`

```python
def isSame(self, shape: Shape, /) -> bool:
```

Checks if both shapes share the same geometry
and placement. Orientation may differ.
isSame(shape) -> bool

Evidence: public stub `Part/__init__.pyi` line(s) 4017.

## `Part.Shape.isEqual`

```python
def isEqual(self, shape: Shape, /) -> bool:
```

Checks if both shapes are equal.
This means geometry, placement and orientation are equal.
isEqual(shape) -> bool

Evidence: public stub `Part/__init__.pyi` line(s) 4025.

## `Part.Shape.isNull`

```python
def isNull(self) -> bool:
```

Checks if the shape is null.
isNull() -> bool

Evidence: public stub `Part/__init__.pyi` line(s) 4033.

## `Part.Shape.isValid`

```python
def isValid(self) -> bool:
```

Checks if the shape is valid, i.e. neither null, nor empty nor corrupted.
isValid() -> bool

Evidence: public stub `Part/__init__.pyi` line(s) 4040.

## `Part.Shape.isCoplanar`

```python
def isCoplanar(self, shape: Shape, tol: float=None, /) -> bool:
```

Checks if this shape is coplanar with the given shape.
isCoplanar(shape,tol=None) -> bool

Evidence: public stub `Part/__init__.pyi` line(s) 4047.

## `Part.Shape.isInfinite`

```python
def isInfinite(self) -> bool:
```

Checks if this shape has an infinite expansion.
isInfinite() -> bool

Evidence: public stub `Part/__init__.pyi` line(s) 4054.

## `Part.Shape.findPlane`

```python
def findPlane(self, tol: float=None, /) -> Plane | None:
```

Returns a plane if the shape is planar
findPlane(tol=None) -> Shape

Evidence: public stub `Part/__init__.pyi` line(s) 4061.

## `Part.Shape.fix`

```python
def fix(self, working_precision: float, minimum_precision: float, maximum_precision: float, /) -> bool:
```

Tries to fix a broken shape.
fix(working precision, minimum precision, maximum precision) -> bool
--
True is returned if the operation succeeded, False otherwise.

Evidence: public stub `Part/__init__.pyi` line(s) 4068.

## `Part.Shape.hashCode`

```python
def hashCode(self, upper: int=..., /) -> int:
```

This value is computed from the value of the underlying shape reference and the location.
hashCode(upper) -> int
--
Orientation is not taken into account.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 4077.

## `Part.Shape.tessellate`

```python
def tessellate(self, tolerance: float, ok: bool=..., /) -> Tuple[List[Vector], List]:
```

Tessellate the shape and return a list of vertices and face indices
tessellate(tolerance[, ok]) -> (vertex, facets)

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 4086.

## `Part.Shape.project`

```python
def project(self, shapeList: List[Shape], /) -> Shape:
```

Project a list of shapes on this shape
project(shapeList) -> Shape

Evidence: public stub `Part/__init__.pyi` line(s) 4093.

## `Part.Shape.makeParallelProjection`

```python
def makeParallelProjection(self, shape: Shape, dir: Vector, /) -> Shape:
```

Parallel projection of an edge or wire on this shape
makeParallelProjection(shape, dir) -> Shape

Evidence: public stub `Part/__init__.pyi` line(s) 4100.

## `Part.Shape.makePerspectiveProjection`

```python
def makePerspectiveProjection(self, shape: Shape, pnt: Vector, /) -> Shape:
```

Perspective projection of an edge or wire on this shape
makePerspectiveProjection(shape, pnt) -> Shape

Evidence: public stub `Part/__init__.pyi` line(s) 4107.

## `Part.Shape.reflectLines`

```python
def reflectLines(self, ViewDir: Vector, *, ViewPos: Vector=None, UpDir: Vector=None, EdgeType: str=None, Visible: bool=True, OnShape: bool=False) -> Shape:
```

Build projection or reflect lines of a shape according to a view direction.
reflectLines(ViewDir, [ViewPos, UpDir, EdgeType, Visible, OnShape]) -> Shape (Compound of edges)
--
This algorithm computes the projection of the shape in the ViewDir direction.
If OnShape is False(default), the returned edges are flat on the XY plane defined by
ViewPos(origin) and UpDir(up direction).
If OnShape is True, the returned edges are the corresponding 3D reflect lines located on the shape.
EdgeType is a string defining the type of result edges :
- IsoLine : isoparametric line
- OutLine : outline (silhouette) edge
- Rg1Line : smooth edge of G1-continuity between two surfaces
- RgNLine : sewn edge of CN-continuity on one surface
- Sharp : sharp edge (of C0-continuity)
If Visible is True (default), only visible edges are returned.
If Visible is False, only invisible edges are returned.

Evidence: public stub `Part/__init__.pyi` line(s) 4114.

## `Part.Shape.makeShapeFromMesh`

```python
def makeShapeFromMesh(self, mesh: Tuple[List[Vector], List], tolerance: float=..., sew_shape: bool=..., /) -> Shape:
```

Make a compound shape out of mesh data.
makeShapeFromMesh((vertex,facets)[, tolerance][, sew_shape]) -> Shape
--
Note: This should be used for rather small meshes only.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 4134.

## `Part.Shape.toNurbs`

```python
def toNurbs(self) -> Shape:
```

Conversion of the complete geometry of a shape into NURBS geometry.
toNurbs() -> Shape
--
For example, all curves supporting edges of the basis shape are converted
into B-spline curves, and all surfaces supporting its faces are converted
into B-spline surfaces.

Evidence: public stub `Part/__init__.pyi` line(s) 4143.

## `Part.Shape.copy`

```python
@overload
def copy(self, copyGeom: bool=True, copyMesh: bool=False, *, noElementMap: bool=False) -> Shape:

@overload
def copy(self, op: str, hasher: StringHasher, copyGeom: bool=True, copyMesh: bool=False, /) -> Shape:

def copy(self, copyGeom: bool=True, copyMesh: bool=False, *, noElementMap: bool=False) -> Shape:
```

Create a copy of this shape
copy(copyGeom=True, copyMesh=False, noElementMap=False) -> Shape
--
If copyMesh is True, triangulation contained in original shape will be
copied along with geometry.
If copyGeom is False, only topological objects will be copied, while
geometry and triangulation will be shared with original shape.
Set noElementMap=True for transient geometry where stable element
naming is not needed.

Evidence: public stub `Part/__init__.pyi` line(s) 4155, 4159, 4162.

## `Part.Shape.cleaned`

```python
def cleaned(self) -> Shape:
```

This creates a cleaned copy of the shape with the triangulation removed.
clean()
--
This can be useful to reduce file size when exporting as a BREP file.
Warning: Use the cleaned shape with care because certain algorithms may work incorrectly
if the shape has no internal triangulation any more.

Evidence: public stub `Part/__init__.pyi` line(s) 4176.

## `Part.Shape.replaceShape`

```python
def replaceShape(self, tupleList: List[Tuple[Shape, Shape]], /) -> Shape:
```

Replace a sub-shape with a new shape and return a new shape.
replaceShape(tupleList) -> Shape
--
The parameter is in the form list of tuples with the two shapes.

Evidence: public stub `Part/__init__.pyi` line(s) 4187.

## `Part.Shape.removeShape`

```python
def removeShape(self, shapeList: List[Shape], /) -> Shape:
```

Remove a sub-shape and return a new shape.
removeShape(shapeList) -> Shape
--
The parameter is a list of shapes.

Evidence: public stub `Part/__init__.pyi` line(s) 4196.

## `Part.Shape.defeaturing`

```python
def defeaturing(self, shapeList: List[Shape], /) -> Shape:
```

Remove a feature defined by supplied faces and return a new shape.
defeaturing(shapeList) -> Shape
--
The parameter is a list of faces.

Evidence: public stub `Part/__init__.pyi` line(s) 4205.

## `Part.Shape.isInside`

```python
def isInside(self, point: Vector, tolerance: float, checkFace: bool, /) -> bool:
```

Checks whether a point is inside or outside the shape.
isInside(point, tolerance, checkFace) => Boolean
--
checkFace indicates if the point lying directly on a face is considered to be inside or not

Evidence: public stub `Part/__init__.pyi` line(s) 4214.

## `Part.Shape.removeSplitter`

```python
def removeSplitter(self) -> Shape:
```

Removes redundant edges from the B-REP model
removeSplitter() -> Shape

Evidence: public stub `Part/__init__.pyi` line(s) 4223.

## `Part.Shape.proximity`

```python
def proximity(self, shape: Shape, tolerance: float=None, /) -> Tuple[List[int], List[int]]:
```

Returns two lists of Face indexes for the Faces involved in the intersection.
proximity(shape,[tolerance]) -> (selfFaces, shapeFaces)

Evidence: public stub `Part/__init__.pyi` line(s) 4230.

## `Part.Shape.distToShape`

```python
def distToShape(self, shape: Shape, tol: float=1e-07, /) -> Tuple[float, List[Tuple[Vector, Vector]], List[Tuple]]:
```

Find the minimum distance to another shape.
distToShape(shape, tol=1e-7) -> (dist, vectors, infos)
--
dist is the minimum distance, in mm (float value).

vectors is a list of pairs of App.Vector. Each pair corresponds to solution.
Example: [(App.Vector(2.0, -1.0, 2.0), App.Vector(2.0, 0.0, 2.0)),
(App.Vector(2.0, -1.0, 2.0), App.Vector(2.0, -1.0, 3.0))]
First vector is a point on self, second vector is a point on s.

infos contains additional info on the solutions. It is a list of tuples:
(topo1, index1, params1, topo2, index2, params2)

    topo1, topo2 are strings identifying type of BREP element: 'Vertex',
    'Edge', or 'Face'.

    index1, index2 are indexes of the elements (zero-based).

    params1, params2 are parameters of internal space of the elements. For
    vertices, params is None. For edges, params is one float, u. For faces,
    params is a tuple (u,v).

Evidence: public stub `Part/__init__.pyi` line(s) 4237.

## `Part.Shape.getElement`

```python
def getElement(self, elementName: str, silent: bool=False, /) -> Shape | None:
```

Returns a SubElement
getElement(elementName, [silent = False]) -> Face | Edge | Vertex
elementName:  SubElement name - i.e. 'Edge1', 'Face3' etc.
              Accepts TNP mitigation mapped names as well
silent:  True to suppress the exception throw if the shape isn't found.

Evidence: public stub `Part/__init__.pyi` line(s) 4263.

## `Part.Shape.countElement`

```python
def countElement(self, type: str, /) -> int:
```

Returns the count of a type of element
countElement(type) -> int

Evidence: public stub `Part/__init__.pyi` line(s) 4273.

## `Part.Shape.mapSubElement`

```python
def mapSubElement(self, shape: Union[Shape, Tuple[Shape, ...]], op: str='', /) -> Shape:
```

mapSubElement(shape|[shape...], op='') - maps the sub element of other shape

shape:  other shape or sequence of shapes to map the sub-elements
op:     optional string prefix to append before the mapped sub element names

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 4280.

## `Part.Shape.mapShapes`

```python
def mapShapes(self, generated: List[Tuple[Shape, Shape]], modified: List[Tuple[Shape, Shape]], op: str='', /) -> None:
```

mapShapes(generated, modified, op='')

generate element names with user defined mapping

generated: a list of tuple(src, dst) that indicating src shape or shapes
generates dst shape or shapes. Note that the dst shape or shapes
must be sub-shapes of this shape.
modified: a list of tuple(src, dst) that indicating src shape or shapes
modifies into dst shape or shapes. Note that the dst shape or
shapes must be sub-shapes of this shape.
op: optional string prefix to append before the mapped sub element names

Evidence: public stub `Part/__init__.pyi` line(s) 4289.

## `Part.Shape.getElementHistory`

```python
def getElementHistory(self, name: str, /) -> Union[Tuple[str, str, List[str]], None]:
```

getElementHistory(name) - returns the element mapped name history

name: mapped element name belonging to this shape

Returns tuple(sourceShapeTag, sourceName, [intermediateNames...]),
or None if no history.

Evidence: public stub `Part/__init__.pyi` line(s) 4305.

## `Part.Shape.getTolerance`

```python
def getTolerance(self, mode: int, ShapeType: str='Shape', /) -> float:
```

Determines a tolerance from the ones stored in a shape
getTolerance(mode, ShapeType=Shape) -> float
--
mode = 0 : returns the average value between sub-shapes,
mode > 0 : returns the maximal found,
mode < 0 : returns the minimal found.
ShapeType defines what kinds of sub-shapes to consider:
Shape (default) : all : Vertex, Edge, Face,
Vertex : only vertices,
Edge   : only edges,
Face   : only faces,
Shell  : combined Shell + Face, for each face (and containing
         shell), also checks edge and Vertex

Evidence: public stub `Part/__init__.pyi` line(s) 4316.

## `Part.Shape.overTolerance`

```python
def overTolerance(self, value: float, ShapeType: str='Shape', /) -> List[Shape]:
```

Determines which shapes have a tolerance over the given value
overTolerance(value, [ShapeType=Shape]) -> ShapeList
--
ShapeType is interpreted as in the method getTolerance

Evidence: public stub `Part/__init__.pyi` line(s) 4334.

## `Part.Shape.inTolerance`

```python
def inTolerance(self, valmin: float, valmax: float, ShapeType: str='Shape', /) -> List[Shape]:
```

Determines which shapes have a tolerance within a given interval
inTolerance(valmin, valmax, [ShapeType=Shape]) -> ShapeList
--
ShapeType is interpreted as in the method getTolerance

Evidence: public stub `Part/__init__.pyi` line(s) 4343.

## `Part.Shape.globalTolerance`

```python
def globalTolerance(self, mode: int, /) -> float:
```

Returns the computed tolerance according to the mode
globalTolerance(mode) -> float
--
mode = 0 : average
mode > 0 : maximal
mode < 0 : minimal

Evidence: public stub `Part/__init__.pyi` line(s) 4352.

## `Part.Shape.fixTolerance`

```python
def fixTolerance(self, value: float, ShapeType: str='Shape', /) -> None:
```

Sets (enforces) tolerances in a shape to the given value
fixTolerance(value, [ShapeType=Shape])
--
ShapeType = Vertex : only vertices are set
ShapeType = Edge   : only edges are set
ShapeType = Face   : only faces are set
ShapeType = Wire   : to have edges and their vertices set
ShapeType = other value : all (vertices,edges,faces) are set

Evidence: public stub `Part/__init__.pyi` line(s) 4363.

## `Part.Shape.limitTolerance`

```python
def limitTolerance(self, tmin: float, tmax: float=0, ShapeType: str='Shape', /) -> bool:
```

Limits tolerances in a shape
limitTolerance(tmin, [tmax=0, ShapeType=Shape]) -> bool
--
tmin = tmax -> as fixTolerance (forces)
tmin = 0   -> maximum tolerance will be tmax
tmax = 0 or not given (more generally, tmax < tmin) ->
tmax ignored, minimum will be tmin
else, maximum will be max and minimum will be min
ShapeType = Vertex : only vertices are set
ShapeType = Edge   : only edges are set
ShapeType = Face   : only faces are set
ShapeType = Wire   : to have edges and their vertices set
ShapeType = other value : all (vertices,edges,faces) are set
Returns True if at least one tolerance of the sub-shape has been modified

Evidence: public stub `Part/__init__.pyi` line(s) 4376.

## `Part.Shape.optimalBoundingBox`

```python
def optimalBoundingBox(self, useTriangulation: bool=True, useShapeTolerance: bool=False, /) -> BoundBox:
```

Get the optimal bounding box
optimalBoundingBox([useTriangulation = True, useShapeTolerance = False]) -> bound box

Evidence: public stub `Part/__init__.pyi` line(s) 4395.

## `Part.Shape.clearCache`

```python
def clearCache(self) -> Shape:
```

Clear internal sub-shape cache

Evidence: public stub `Part/__init__.pyi` line(s) 4402.

## `Part.Shape.findSubShape`

```python
def findSubShape(self, shape: Shape, /) -> Tuple[Union[str, None], int]:
```

findSubShape(shape) -> (type_name, index)

Find sub shape and return the shape type name and index. If not found,
then return (None, 0)

Evidence: public stub `Part/__init__.pyi` line(s) 4408.

## `Part.Shape.findSubShapesWithSharedVertex`

```python
def findSubShapesWithSharedVertex(self, shape: Shape, *, needName: bool=False, checkGeometry: bool=True, tol: float=1e-07, atol: float=1e-12, singleResult: bool=False) -> Union[List[Tuple[str, Shape]], List[Shape]]:
```

findSubShapesWithSharedVertex(shape, needName=False, checkGeometry=True, tol=1e-7, atol=1e-12) -> Shape

shape: input elementary shape, currently only support Face, Edge, or Vertex

needName: if True, return a list of tuple(name, shape), or else return a list
of shapes.

checkGeometry: whether to compare geometry

tol: distance tolerance

atol: angular tolerance

Search sub shape by checking vertex coordinates and comparing the underlying
geometries, This can find shapes that are copied. It currently only works with
elementary shapes, Face, Edge, Vertex.

Evidence: public stub `Part/__init__.pyi` line(s) 4417.

## `Part.Shape.getChildShapes`

```python
def getChildShapes(self, shapetype: str, avoidtype: str='', /) -> List[Shape]:
```

getChildShapes(shapetype, avoidtype='') -> list(Shape)

Return a list of child sub-shapes of given type.

shapetype: the type of requesting sub shapes
avoidtype: optional shape type to skip when exploring

Evidence: public stub `Part/__init__.pyi` line(s) 4438.

