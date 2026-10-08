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

## `Part.Shape.ShapeType`

```python
ShapeType: Final[str] = ''
```

Returns the type of the shape.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 3370.

## `Part.Shape.Orientation`

```python
Orientation: str = ''
```

Returns the orientation of the shape.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 3372.

## `Part.Shape.Faces`

```python
Faces: Final[List['Face']] = []
```

List of faces in this shape.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 3374.

## `Part.Shape.Vertexes`

```python
Vertexes: Final[List['Vertex']] = []
```

List of vertexes in this shape.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 3376.

## `Part.Shape.Shells`

```python
Shells: Final[List['Shell']] = []
```

List of subsequent shapes in this shape.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 3378.

## `Part.Shape.Solids`

```python
Solids: Final[List['Solid']] = []
```

List of subsequent shapes in this shape.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 3380.

## `Part.Shape.CompSolids`

```python
CompSolids: Final[List['CompSolid']] = []
```

List of compound solids in this shape.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 3382.

## `Part.Shape.Edges`

```python
Edges: Final[List['Edge']] = []
```

List of Edges in this shape.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 3384.

## `Part.Shape.Wires`

```python
Wires: Final[List['Wire']] = []
```

List of wires in this shape.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 3386.

## `Part.Shape.Compounds`

```python
Compounds: Final[List['Compound']] = []
```

List of compounds in this shape.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 3388.

## `Part.Shape.SubShapes`

```python
SubShapes: Final[List['TopoShape']] = []
```

List of sub-shapes in this shape.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 3390.

## `Part.Shape.Length`

```python
Length: Final[float] = 0.0
```

Total length of the edges of the shape.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 3392.

## `Part.Shape.Area`

```python
Area: Final[float] = 0.0
```

Total area of the faces of the shape.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 3394.

## `Part.Shape.Volume`

```python
Volume: Final[float] = 0.0
```

Total volume of the solids of the shape.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 3396.

## `Part.Shape.dumps`

```python
def dumps(self) -> str:
```

Serialize the content of this shape to a string in BREP format.

Evidence: public stub `Part/__init__.pyi` line(s) 3399.

## `Part.Shape.loads`

```python
def loads(self, brep_str: str, /) -> None:
```

Deserialize the content of this shape from a string in BREP format.

Evidence: public stub `Part/__init__.pyi` line(s) 3405.

## `Part.Shape.read`

```python
def read(self, filename: str, /) -> None:
```

Read in an IGES, STEP or BREP file.
read(filename)

Evidence: public stub `Part/__init__.pyi` line(s) 3411.

## `Part.Shape.writeInventor`

```python
def writeInventor(self, *, Mode: int=..., Deviation: float=..., Angle: float=..., FaceColors: object=...) -> str:
```

Write the mesh in OpenInventor format to a string.
writeInventor() -> string

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 3418.

## `Part.Shape.exportIges`

```python
def exportIges(self, filename: str, /) -> None:
```

Export the content of this shape to an IGES file.
exportIges(filename)

Evidence: public stub `Part/__init__.pyi` line(s) 3425.

## `Part.Shape.exportStep`

```python
def exportStep(self, filename: str, /) -> None:
```

Export the content of this shape to an STEP file.
exportStep(filename)

Evidence: public stub `Part/__init__.pyi` line(s) 3432.

## `Part.Shape.exportBrep`

```python
@overload
def exportBrep(self, filename: str, /) -> None:

@overload
def exportBrep(self, stream: object, /) -> None:

def exportBrep(self, *args) -> None:
```

Export the content of this shape to an BREP file.
exportBrep(filename)
--
BREP is an OpenCasCade native format.

Evidence: public stub `Part/__init__.pyi` line(s) 3440, 3444, 3447.

## `Part.Shape.exportBinary`

```python
def exportBinary(self, filename: str, /) -> None:
```

Export the content of this shape in binary format to a file.
exportBinary(filename)

Evidence: public stub `Part/__init__.pyi` line(s) 3456.

## `Part.Shape.exportBrepToString`

```python
def exportBrepToString(self) -> str:
```

Export the content of this shape to a string in BREP format.
exportBrepToString() -> string
--
BREP is an OpenCasCade native format.

Evidence: public stub `Part/__init__.pyi` line(s) 3463.

## `Part.Shape.dumpToString`

```python
def dumpToString(self) -> str:
```

Dump information about the shape to a string.
dumpToString() -> string

Evidence: public stub `Part/__init__.pyi` line(s) 3472.

## `Part.Shape.exportStl`

```python
def exportStl(self, filename: str, deflection: float=0.01, /) -> None:
```

Export the content of this shape to an STL mesh file.
exportStl(filename, deflection=0.01)

Evidence: public stub `Part/__init__.pyi` line(s) 3479.

## `Part.Shape.importBrep`

```python
@overload
def importBrep(self, filename: str, /) -> None:

@overload
def importBrep(self, stream: object, /) -> None:

def importBrep(self, *args) -> None:
```

Load the shape from a file in BREP format.
importBrep(filename)

Evidence: public stub `Part/__init__.pyi` line(s) 3487, 3491, 3494.

## `Part.Shape.importBinary`

```python
def importBinary(self, filename: str, /) -> None:
```

Import the content to this shape of a string in BREP format.
importBinary(filename)

Evidence: public stub `Part/__init__.pyi` line(s) 3501.

## `Part.Shape.importBrepFromString`

```python
def importBrepFromString(self, s: str, displayProgressBar: bool=True, /) -> None:
```

Load the shape from a string that keeps the content in BREP format.
importBrepFromString(string, [displayProgressBar=True])
--
importBrepFromString(str, False) to not display a progress bar.

Evidence: public stub `Part/__init__.pyi` line(s) 3508.

## `Part.Shape.extrude`

```python
def extrude(self, vector: Vector, /) -> Shape:
```

Extrude the shape along a vector.
extrude(vector) -> Shape
--
Shp2 = Shp1.extrude(App.Vector(0,0,10)) - extrude the shape 10 mm in the +Z direction.

Evidence: public stub `Part/__init__.pyi` line(s) 3517.

## `Part.Shape.revolve`

```python
def revolve(self, base: Vector, direction: Vector, angle: float=..., /) -> Shape:
```

Revolve the shape around an Axis to a given degree.
revolve(base, direction[, angle])
--
Part.revolve(App.Vector(0,0,0),App.Vector(0,0,1),360) - revolves the shape around the Z Axis 360 degree.

Hints: Sometimes you want to create a rotation body out of a closed edge or wire.
Example:
from FreeCAD import Base
import Part
V=Base.Vector

e=Part.Ellipse()
s=e.toShape()
r=s.revolve(V(0,0,0),V(0,1,0), 360)
Part.show(r)

However, you may possibly realize some rendering artifacts or that the mesh
creation seems to hang. This is because this way the surface is created twice.
Since the curve is a full ellipse it is sufficient to do a rotation of 180 degree
only, i.e. r=s.revolve(V(0,0,0),V(0,1,0), 180)

Now when rendering this object you may still see some artifacts at the poles. Now the
problem seems to be that the meshing algorithm doesn't like to rotate around a point
where there is no vertex.

The idea to fix this issue is that you create only half of the ellipse so that its shape
representation has vertexes at its start and end point.

from FreeCAD import Base
import Part
V=Base.Vector

e=Part.Ellipse()
s=e.toShape(e.LastParameter/4,3*e.LastParameter/4)
r=s.revolve(V(0,0,0),V(0,1,0), 360)
Part.show(r)

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 3526.

## `Part.Shape.check`

```python
def check(self, runBopCheck: bool=False, /) -> bool:
```

Checks the shape and report errors in the shape structure.
check([runBopCheck = False])
--
This is a more detailed check as done in isValid().
if runBopCheck is True, a BOPCheck analysis is also performed.

Evidence: public stub `Part/__init__.pyi` line(s) 3567.

## `Part.Shape.fuse`

```python
def fuse(self, tools: Tuple[Shape, ...], tolerance: float=0.0, *, noElementMap: bool=False) -> Shape:
```

Union of this and a given (list of) topo shape.
fuse(tool) -> Shape
  or
fuse((tool1,tool2,...),[tolerance=0.0], noElementMap=False) -> Shape
--
Union of this and a given list of topo shapes.

Supports (OCCT 6.9.0 and above):
- Fuzzy Boolean operations (global tolerance for a Boolean operation)
- Support of multiple arguments for a single Boolean operation
- Parallelization of Boolean Operations algorithm

Beginning from OCCT 6.8.1 a tolerance value can be specified.
Set noElementMap=True for transient analysis geometry where stable
element naming is not needed.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 3577.

## `Part.Shape.multiFuse`

```python
@deprecated('since FreeCAD 26.3 and will be removed in FreeCAD 27.2; use fuse instead.')
def multiFuse(self, tools: Tuple[Shape, ...], tolerance: float=0.0, *, noElementMap: bool=False) -> Shape:
```

Union of this and a given list of topo shapes.
multiFuse((tool1,tool2,...),[tolerance=0.0], noElementMap=False) -> Shape
--
Supports (OCCT 6.9.0 and above):
- Fuzzy Boolean operations (global tolerance for a Boolean operation)
- Support of multiple arguments for a single Boolean operation
- Parallelization of Boolean Operations algorithm

Beginning from OCCT 6.8.1 a tolerance value can be specified.
Set noElementMap=True for transient analysis geometry where stable
element naming is not needed.
Deprecated: use fuse() instead.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 3598.

## `Part.Shape.common`

```python
def common(self, tools: Tuple[Shape, ...], tolerance: float=0.0, /) -> Shape:
```

Intersection of this and a given (list of) topo shape.
common(tool) -> Shape
  or
common((tool1,tool2,...),[tolerance=0.0]) -> Shape
--
Supports:
- Fuzzy Boolean operations (global tolerance for a Boolean operation)
- Support of multiple arguments for a single Boolean operation (s1 AND (s2 OR s3))
- Parallelization of Boolean Operations algorithm

OCC 6.9.0 or later is required.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 3615.

## `Part.Shape.section`

```python
def section(self, tool: Tuple[Shape, ...], tolerance: float=0.0, approximation: bool=False, /) -> Shape:
```

Section of this with a given (list of) topo shape.
section(tool,[approximation=False]) -> Shape
  or
section((tool1,tool2,...),[tolerance=0.0, approximation=False]) -> Shape
--
If approximation is True, section edges are approximated to a C1-continuous BSpline curve.

Supports:
- Fuzzy Boolean operations (global tolerance for a Boolean operation)
- Support of multiple arguments for a single Boolean operation (s1 AND (s2 OR s3))
- Parallelization of Boolean Operations algorithm

OCC 6.9.0 or later is required.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 3631.

## `Part.Shape.slices`

```python
def slices(self, direction: Vector, distancesList: List[float], /) -> List:
```

Make slices of this shape.
slices(direction, distancesList) --> Wires

Evidence: public stub `Part/__init__.pyi` line(s) 3649.

## `Part.Shape.slice`

```python
def slice(self, direction: Vector, distance: float, /) -> List:
```

Make single slice of this shape.
slice(direction, distance) --> Wires

Evidence: public stub `Part/__init__.pyi` line(s) 3656.

## `Part.Shape.cut`

```python
def cut(self, tool: Tuple[Shape, ...], tolerance: float=0.0, /) -> Shape:
```

Difference of this and a given (list of) topo shape
cut(tool) -> Shape
  or
cut((tool1,tool2,...),[tolerance=0.0]) -> Shape
--
Supports:
- Fuzzy Boolean operations (global tolerance for a Boolean operation)
- Support of multiple arguments for a single Boolean operation
- Parallelization of Boolean Operations algorithm

OCC 6.9.0 or later is required.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 3663.

## `Part.Shape.generalFuse`

```python
def generalFuse(self, shapes: Tuple[Shape, ...], fuzzy_value: float=0.0, /) -> Tuple[Shape, List[List[Shape]]]:
```

Run general fuse algorithm (GFA) between this and given shapes.
generalFuse(list_of_other_shapes, [fuzzy_value = 0.0]) -> (result, map)
--
list_of_other_shapes: shapes to run the algorithm against (the list is
effectively prepended by 'self').

fuzzy_value: extra tolerance to apply when searching for interferences, in
addition to tolerances of the input shapes.

Returns a tuple of 2: (result, map).

result is a compound containing all the pieces generated by the algorithm
(e.g., for two spheres, the pieces are three touching solids). Pieces that
touch share elements.

map is a list of lists of shapes, providing the info on which children of
result came from which argument. The length of list is equal to length of
list_of_other_shapes + 1. First element is a list of pieces that came from
shape of this, and the rest are those that come from corresponding shapes in
list_of_other_shapes.
hint: use isSame method to test shape equality

Parallelization of Boolean Operations algorithm

OCC 6.9.0 or later is required.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Part/__init__.pyi` line(s) 3679.

## `Part.Shape.sewShape`

```python
def sewShape(self, tolerance: float=1e-06, /) -> None:
```

Sew the shape if there is a gap.
sewShape(tolerance=1e-06)

Evidence: public stub `Part/__init__.pyi` line(s) 3709.

## `Part.Shape.childShapes`

```python
def childShapes(self, cumOri: bool=True, cumLoc: bool=True, /) -> List:
```

Return a list of sub-shapes that are direct children of this shape.
childShapes([cumOri=True, cumLoc=True]) -> list
--
* If cumOri is true, the function composes all
  sub-shapes with the orientation of this shape.
* If cumLoc is true, the function multiplies all
  sub-shapes by the location of this shape, i.e. it applies to
  each sub-shape the transformation that is associated with this shape.

Evidence: public stub `Part/__init__.pyi` line(s) 3716.

## `Part.Shape.ancestorsOfType`

```python
def ancestorsOfType(self, shape: Shape, shape_type: str, /) -> List:
```

For a sub-shape of this shape get its ancestors of a type.
ancestorsOfType(shape, shape type) -> list

Evidence: public stub `Part/__init__.pyi` line(s) 3729.

## `Part.Shape.removeInternalWires`

```python
def removeInternalWires(self, minimalArea: float, /) -> bool:
```

Removes internal wires (also holes) from the shape.
removeInternalWires(minimalArea) -> bool

Evidence: public stub `Part/__init__.pyi` line(s) 3736.

## `Part.Shape.mirror`

```python
def mirror(self, base: Vector, norm: Vector, /) -> Shape:
```

Mirror this shape on a given plane.
mirror(base, norm) -> Shape
--
The plane is given with its base point and its normal direction.

Evidence: public stub `Part/__init__.pyi` line(s) 3743.

## `Part.Shape.transformGeometry`

```python
def transformGeometry(self, matrix: Matrix, copy: bool=False, /) -> Shape:
```

Apply geometric transformation on this or a copy the shape.
transformGeometry(matrix, copy=False) -> Shape
--
This method returns a new shape.
The transformation to be applied is defined as a 4x4 matrix.
The underlying geometry of the following shapes may change:
- a curve which supports an edge of the shape, or
- a surface which supports a face of the shape;

For example, a circle may be transformed into an ellipse when
applying an affinity transformation. It may also happen that
the circle then is represented as a B-spline curve.

The transformation is applied to:
- all the curves which support edges of the shape, and
- all the surfaces which support faces of the shape.

Note: If you want to transform a shape without changing the
underlying geometry then use the methods translate or rotate.

Evidence: public stub `Part/__init__.pyi` line(s) 3752.

## `Part.Shape.transformShape`

```python
def transformShape(self, matrix: Matrix, copy: bool=False, checkScale: bool=False, /) -> Shape:
```

Apply a transformation on this shape in place and return self.
--
If copy is True the underlying geometry is duplicated and the transformation is baked into
it. If copy is False the transformation is applied as a location change without modifying
the underlying geometry (no bake-in). Note that scaling, mirroring, and non-uniform
transformations may force a copy regardless of this flag. If checkScale is True,
transformGeometry is used when non-uniform scaling is detected. To obtain a transformed copy
while leaving this shape untouched, use transformed() instead.

Evidence: public stub `Part/__init__.pyi` line(s) 3776.

## `Part.Shape.transformed`

```python
def transformed(self, matrix: Matrix, *, copy: bool=False, checkScale: bool=False, op: str=None) -> Shape:
```

Return a new shape with the transformation applied; leave self unchanged.
--
The copy and checkScale arguments have the same meaning as in transformShape(). op is
unused.

Evidence: public stub `Part/__init__.pyi` line(s) 3789.

## `Part.Shape.translate`

```python
def translate(self, vector: Vector | tuple[float, float, float], /) -> Shape:
```

Apply the translation to the current location of this shape.
translate(vector)

Evidence: public stub `Part/__init__.pyi` line(s) 3798.

## `Part.Shape.translated`

```python
def translated(self, vector: Vector, /) -> Shape:
```

Create a new shape with translation
translated(vector) -> shape

Evidence: public stub `Part/__init__.pyi` line(s) 3805.

## `Part.Shape.rotate`

```python
def rotate(self, base: Vector | tuple[float, float, float], dir: Vector | tuple[float, float, float], degree: float, /) -> Shape:
```

Apply the rotation (base, dir, degree) to the current location of this shape
rotate(base, dir, degree)
--
Shp.rotate(App.Vector(0,0,0), App.Vector(0,0,1), 180) - rotate the shape around the Z Axis 180 degrees.

Evidence: public stub `Part/__init__.pyi` line(s) 3812.

## `Part.Shape.rotated`

```python
def rotated(self, base: Vector, dir: Vector, degree: float, /) -> Shape:
```

Create a new shape with rotation.
rotated(base, dir, degree) -> shape

Evidence: public stub `Part/__init__.pyi` line(s) 3821.

## `Part.Shape.scale`

```python
def scale(self, factor: float, base: Vector=None, /) -> Shape:
```

Apply scaling with point and factor to this shape.
scale(factor, [base=App.Vector(0,0,0)])

Evidence: public stub `Part/__init__.pyi` line(s) 3828.

## `Part.Shape.scaled`

```python
def scaled(self, factor: float, base: Vector=None, /) -> Shape:
```

Create a new shape with scale.
scaled(factor, [base=App.Vector(0,0,0)]) -> shape

Evidence: public stub `Part/__init__.pyi` line(s) 3835.

## `Part.Shape.makeFillet`

```python
@overload
def makeFillet(self, radius: float, edgeList: List, /) -> Shape:

@overload
def makeFillet(self, radius1: float, radius2: float, edgeList: List, /) -> Shape:

def makeFillet(self, *args) -> Shape:
```

Make fillet.
makeFillet(radius, edgeList) -> Shape
or
makeFillet(radius1, radius2, edgeList) -> Shape

Evidence: public stub `Part/__init__.pyi` line(s) 3843, 3847, 3850.

## `Part.Shape.makeChamfer`

```python
@overload
def makeChamfer(self, radius: float, edgeList: List, /) -> Shape:

@overload
def makeChamfer(self, radius1: float, radius2: float, edgeList: List, /) -> Shape:

def makeChamfer(self, *args) -> Shape:
```

Make chamfer.
makeChamfer(radius, edgeList) -> Shape
or
makeChamfer(radius1, radius2, edgeList) -> Shape

Evidence: public stub `Part/__init__.pyi` line(s) 3860, 3864, 3867.

## `Part.Shape.makeThickness`

```python
def makeThickness(self, faces: List, offset: float, tolerance: float, inter: bool=False, self_inter: bool=False, offset_mode: int=0, join: int=0, /) -> Shape:
```

Hollow a solid according to given thickness and faces.
makeThickness(List of faces, Offset (Float), Tolerance (Float),
              Inter (Bool), SelfInter (Bool), OffsetMode (Int), Join (Int)) -> Shape
--
A hollowed solid is built from an initial solid and a set of faces on this solid,
which are to be removed. The remaining faces of the solid become the walls of
the hollowed solid, their thickness defined at the time of construction.

Evidence: public stub `Part/__init__.pyi` line(s) 3876.

## `Part.Shape.makeOffsetShape`

```python
def makeOffsetShape(self, offset: float, tolerance: float, *, inter: bool=False, self_inter: bool=False, offsetMode: int=0, join: int=0, fill: bool=False) -> Shape:
```

Makes an offset shape (3d offsetting).
makeOffsetShape(offset, tolerance, [inter=False, self_inter=False, offsetMode=0, join=0, fill=False]) -> Shape
--
The function supports keyword arguments.

* offset: distance to expand the shape by. Negative value will shrink the shape.

* tolerance: precision of approximation.

* inter: (parameter to OCC routine; not implemented)

* self_inter: (parameter to OCC routine; not implemented)

* offsetMode: 0 = skin; 1 = pipe; 2 = recto-verso

* join: method of offsetting non-tangent joints. 0 = arcs, 1 = tangent, 2 =
intersection

* fill: if true, offsetting a shell is to yield a solid

Returns: result of offsetting.

Evidence: public stub `Part/__init__.pyi` line(s) 3888.

