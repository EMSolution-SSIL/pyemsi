# `Sketcher.SketchObject`

[Module](index.md)

```python
class SketchObject(Part2DObject):
```

Represents a sketch object

Author: Juergen Riegel
Licence: LGPL

Evidence: public stub `Sketcher/__init__.pyi` line 440. Inherited members are on the named base's reference; aliases keep their imported identity.

[part 1](SketchObject.md) | [part 2](SketchObject-2.md)

## `Sketcher.SketchObject.setVirtualSpace`

```python
@overload
def setVirtualSpace(self, constraint_index: int, state: bool, /) -> None:

@overload
def setVirtualSpace(self, constraint_indices: List[int] | Tuple[int, ...], state: bool, /) -> None:
```

Set the VirtualSpace status of one or more constraints.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1002, 1009.

## `Sketcher.SketchObject.setVisibility`

```python
def setVisibility(self, id_or_ids: Union[int, List[int]], is_visible: bool, /) -> None:
```

Set the visibility of a constraint

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1012.

## `Sketcher.SketchObject.getVirtualSpace`

```python
def getVirtualSpace(self, constraint_index: int, /) -> bool:
```

Get the VirtualSpace status of a constraint

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1018.

## `Sketcher.SketchObject.toggleVirtualSpace`

```python
def toggleVirtualSpace(self, constraint_index: int, /) -> None:
```

Toggle the VirtualSpace status of a constraint

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1024.

## `Sketcher.SketchObject.setActive`

```python
def setActive(self, constraint_index: int, state: bool, /) -> None:
```

Activates or deactivates a constraint (enforce it or not).

setActive(constraintIndex:int, state:bool)

    Args:
        constraintIndex: The zero-based index of the constraint to configure.
        state: `True` sets the constraint to active i.e. enforced,
            `False` configures it as inactive, i.e. not enforced.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1030.

## `Sketcher.SketchObject.getActive`

```python
def getActive(self, constraint_index: int, /) -> bool:
```

Get whether a constraint is active, i.e. enforced, or not.

getActive(constraintIndex:int)

    Args:
        constraintIndex: The zero-based index of the constraint to query.

    Returns:
        `True` if the constraint is active, i.e. enforced,
        `False` if it is inactive, i.e. not enforced.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1043.

## `Sketcher.SketchObject.toggleActive`

```python
def toggleActive(self, constraint_index: int, /) -> None:
```

Toggle the constraint between active (enforced) and inactive.

toggleActive(constraintIndex:int)

    Args:
        constraintIndex: The zero-based index of the constraint to toggle.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1058.

## `Sketcher.SketchObject.getLabelPosition`

```python
def getLabelPosition(self, constraint_index: int, /) -> float:
```

Get label position of the constraint.

getLabelPosition(constraintIndex:int)

    Args:
        constraintIndex: The zero-based index of the constraint to query.

    Returns:
        float with the current value.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1069.

## `Sketcher.SketchObject.setLabelPosition`

```python
def setLabelPosition(self, constraint_index: int, value: float, /) -> None:
```

Set label position of the constraint.

setLabelPosition(constraintIndex:int, value:float)

    Args:
        constraintIndex: The zero-based index of the constraint to query.
        value: Value of the label position.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1083.

## `Sketcher.SketchObject.getLabelDistance`

```python
def getLabelDistance(self, constraint_index: int, /) -> float:
```

Get label distance of the constraint.

getLabelDistance(constraintIndex:int)

    Args:
        constraintIndex: The zero-based index of the constraint to query.

    Returns:
        float with the current value.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1095.

## `Sketcher.SketchObject.setLabelDistance`

```python
def setLabelDistance(self, constraint_index: int, value: float, /) -> None:
```

Set label distance of the constraint.

setLabelDistance(constraintIndex:int, value:float)

    Args:
        constraintIndex: The zero-based index of the constraint to query.
        value: Value of the label position.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1109.

## `Sketcher.SketchObject.moveGeometry`

```python
def moveGeometry(self, geo_index: int, point_pos: int, vector: Vector, relative: bool=False, /) -> None:
```

Move a given point (or curve) to another location.

moveGeometry(GeoIndex,PointPos,Vector,[relative])

It moves the specified point (or curve) to the given location by adding some
temporary weak constraints and solving the sketch.
This method is mostly used to allow the user to drag some portions of the sketch
in real time by e.g. the mouse and it works only for underconstrained portions of
the sketch.
The argument 'relative', if present, states if the new location is given
relatively to the current one.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1121.

## `Sketcher.SketchObject.moveGeometries`

```python
def moveGeometries(self, geos: List[Tuple[int, int]], vector: Vector, relative: bool=False, /) -> None:
```

Move given points and curves to another location.

moveGeometries(Geos,Vector,[relative])

It moves the specified points and curves to the given location by adding some
temporary weak constraints and solving the sketch.
This method is mostly used to allow the user to drag some portions of the sketch
in real time by e.g. the mouse and it works only for underconstrained portions of
the sketch.
The argument 'relative', if present, states if the new location is given
relatively to the current one. For group dragging this is enforced.
Geos is a vector of pairs of geoId and posId.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1137.

## `Sketcher.SketchObject.getPoint`

```python
def getPoint(self, geo_index: int, point_pos: int, /) -> Vector:
```

Retrieve the vector of a point in the sketch.

getPoint(GeoIndex,PointPos)

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1154.

## `Sketcher.SketchObject.getGeoVertexIndex`

```python
def getGeoVertexIndex(self, index: int, /) -> Tuple[int, int]:
```

Retrieve the GeoId and PosId of a point in the sketch.

(geoId, posId) = getGeoVertexIndex(index)

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1162.

## `Sketcher.SketchObject.getAxis`

```python
def getAxis(self, ax_id: int, /) -> Axis:
```

Return an axis based on the corresponding construction line

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1170.

## `Sketcher.SketchObject.fillet`

```python
@overload
def fillet(self, geo_id1: int, geo_id2: int, point1: Vector, point2: Vector, radius: float, trim: bool=..., create_corner: bool=..., chamfer: bool=..., /) -> None:

@overload
def fillet(self, geo_id: int, pos_id: int, radius: float, trim: bool=..., create_corner: bool=..., chamfer: bool=..., /) -> None:

def fillet(self, *args) -> None:
```

Create a fillet between two edges or at a point

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1177, 1181, 1184.

## `Sketcher.SketchObject.trim`

```python
def trim(self, geo_id: int, point: Vector, include_axes: bool=..., /) -> None:
```

Trim a curve with a given id at a given reference point

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1190.

## `Sketcher.SketchObject.extend`

```python
def extend(self, geo_id: int, increment: float, end_point: int, /) -> None:
```

Extend a curve to new start and end positions

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1196.

## `Sketcher.SketchObject.split`

```python
def split(self, geo_id: int, point: Vector, /) -> None:
```

Split a curve with a given id at a given reference point

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1202.

## `Sketcher.SketchObject.join`

```python
def join(self, geo_id1: int, pos_id1: int, geo_id2: int, pos_id2: int, continuity: int=..., /) -> None:
```

Join two curves at the given end points

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1208.

## `Sketcher.SketchObject.addSymmetric`

```python
def addSymmetric(self, geo_ids: List[int], ref_geo_id: int, ref_pos_id: int=..., /) -> Tuple[int, ...]:
```

Add symmetric geometric objects to the sketch with respect to a reference point or line

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1214.

## `Sketcher.SketchObject.addCopy`

```python
def addCopy(self, geo_ids: List[int], vector: Vector, clone: bool=..., /) -> Tuple[int, ...]:
```

Add a copy of geometric objects to the sketch displaced by a vector3d

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1220.

## `Sketcher.SketchObject.addMove`

```python
def addMove(self, geo_ids: List[int], vector: Vector, /) -> None:
```

Move the geometric objects in the sketch displaced by a vector3d

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1226.

## `Sketcher.SketchObject.addRectangularArray`

```python
def addRectangularArray(self, geo_ids: List[int], vector: Vector, clone: bool, rows: int, cols: int, constrain_displacement: bool=..., perpendicular_scale: float=..., /) -> None:
```

Add an array of size cols by rows where each element is a copy of the selected geometric objects displaced by a vector3d in the cols direction and by a vector perpendicular to it in the rows direction

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1232.

## `Sketcher.SketchObject.removeAxesAlignment`

```python
def removeAxesAlignment(self, geo_ids: List[int], /) -> None:
```

Modifies constraints so that the shape is not forced to be aligned with axes.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1238.

## `Sketcher.SketchObject.ExposeInternalGeometry`

```python
@deprecated('since FreeCAD 26.3 and will be removed in FreeCAD 27.2; use exposeInternalGeometry instead.')
def ExposeInternalGeometry(self, geo_id: int, /) -> None:
```

Deprecated -- use exposeInternalGeometry

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1245.

## `Sketcher.SketchObject.DeleteUnusedInternalGeometry`

```python
@deprecated('since FreeCAD 26.3 and will be removed in FreeCAD 27.2; use deleteUnusedInternalGeometry instead.')
def DeleteUnusedInternalGeometry(self, geo_id: int, /) -> None:
```

Deprecated -- use deleteUnusedInternalGeometry

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1252.

## `Sketcher.SketchObject.exposeInternalGeometry`

```python
def exposeInternalGeometry(self, geo_id: int, /) -> None:
```

Exposes all internal geometry of an object supporting internal geometry

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1258.

## `Sketcher.SketchObject.deleteUnusedInternalGeometry`

```python
def deleteUnusedInternalGeometry(self, geo_id: int, /) -> None:
```

Deletes all unused (not further constrained) internal geometry

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1264.

## `Sketcher.SketchObject.convertToNURBS`

```python
def convertToNURBS(self, geo_id: int, /) -> None:
```

Approximates the given geometry with a B-spline

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1270.

## `Sketcher.SketchObject.increaseBSplineDegree`

```python
def increaseBSplineDegree(self, geo_id: int, incr: int=..., /) -> None:
```

Increases the given B-spline Degree by a number of degrees

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1276.

## `Sketcher.SketchObject.decreaseBSplineDegree`

```python
def decreaseBSplineDegree(self, geo_id: int, decr: int=..., /) -> bool:
```

Decreases the given B-spline Degree by a number of degrees by approximating this curve

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1282.

## `Sketcher.SketchObject.modifyBSplineKnotMultiplicity`

```python
def modifyBSplineKnotMultiplicity(self, geo_id: int, knot_index: int, multiplicity: int=..., /) -> None:
```

Increases or reduces the given BSpline knot multiplicity

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1288.

## `Sketcher.SketchObject.insertBSplineKnot`

```python
def insertBSplineKnot(self, geo_id: int, knot_param: float, multiplicity: int=..., /) -> None:
```

Inserts a knot into the BSpline at the given param with given multiplicity. If the knot already exists, this increases the knot multiplicity by the given multiplicity.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1294.

## `Sketcher.SketchObject.calculateAngleViaPoint`

```python
def calculateAngleViaPoint(self, geo_id1: int, geo_id2: int, px: float, py: float, /) -> float:
```

calculateAngleViaPoint(GeoId1, GeoId2, px, py) - calculates angle between
curves identified by GeoId1 and GeoId2 at point (x,y). The point must be
on intersection of the curves, otherwise the result may be useless (except
line-to-line, where (0,0) is OK). Returned value is in radians.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1300.

## `Sketcher.SketchObject.isPointOnCurve`

```python
def isPointOnCurve(self, geo_id_curve: int, x: float, y: float, /) -> bool:
```

isPointOnCurve(GeoIdCurve, float x, float y) -> bool - tests if the point (x,y)
geometrically lies on a curve (e.g. ellipse). It treats lines as infinite,
arcs as full circles/ellipses/etc.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1309.

## `Sketcher.SketchObject.calculateConstraintError`

```python
def calculateConstraintError(self, index: int, /) -> float:
```

calculateConstraintError(index) - calculates the error function of the
constraint identified by its index and returns the signed error value.
The error value roughly corresponds to by how much the constraint is
violated. If the constraint internally has more than one error function,
the returned value is RMS of all errors (sign is lost in this case).

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1317.

## `Sketcher.SketchObject.changeConstraintsLocking`

```python
def changeConstraintsLocking(self, b_lock: int, /) -> int:
```

changeConstraintsLocking(bLock) - locks or unlocks all tangent and
perpendicular constraints. (Constraint locking prevents it from
flipping to another valid configuration, when e.g. external geometry
is updated from outside.) The sketch solve is not triggered by the
function, but the SketchObject is touched (a recompute will be
necessary). The geometry should not be affected by the function.

The bLock argument specifies, what to do. If true, all constraints
are unlocked and locked again. If false, all tangent and perp.
constraints are unlocked.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1327.

## `Sketcher.SketchObject.getGeometryWithDependentParameters`

```python
def getGeometryWithDependentParameters(self) -> List[Tuple[int, int]]:
```

getGeometryWithDependentParameters - returns a list of geoid posid pairs
with all the geometry element edges and vertices which the solver regards
as being dependent on other parameters.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1342.

## `Sketcher.SketchObject.autoconstraint`

```python
def autoconstraint(self, precision: float=..., angle_precision: float=..., include_construction: bool=True, /) -> None:
```

Automatic sketch constraining algorithm.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1350.

## `Sketcher.SketchObject.detectMissingPointOnPointConstraints`

```python
def detectMissingPointOnPointConstraints(self, precision: float=..., include_construction: bool=True, /) -> None:
```

Detects missing Point On Point Constraints. The detect step just identifies possible missing constraints.
The result may be retrieved or applied using the corresponding Get / Make methods.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1356.

## `Sketcher.SketchObject.analyseMissingPointOnPointCoincident`

```python
def analyseMissingPointOnPointCoincident(self, angle_precision: float=..., /) -> None:
```

Analyses the already detected missing Point On Point Constraints to detect endpoint tangency/perpendicular.
The result may be retrieved or applied using the corresponding Get / Make methods.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1363.

## `Sketcher.SketchObject.detectMissingVerticalHorizontalConstraints`

```python
def detectMissingVerticalHorizontalConstraints(self, angle_precision: float=..., /) -> None:
```

Detects missing Horizontal/Vertical Constraints. The detect step just identifies possible missing constraints.
The result may be retrieved or applied using the corresponding Get / Make methods.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1370.

## `Sketcher.SketchObject.detectMissingEqualityConstraints`

```python
def detectMissingEqualityConstraints(self, precision: float=..., /) -> None:
```

Detects missing Equality Constraints. The detect step just identifies possible missing constraints.
The result may be retrieved or applied using the corresponding Get / Make methods.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1377.

## `Sketcher.SketchObject.makeMissingPointOnPointCoincident`

```python
def makeMissingPointOnPointCoincident(self, one_by_one: bool=False, /) -> None:
```

Applies the detected / set Point On Point coincident constraints. If the argument is True, then solving and redundant removal is done after each individual addition.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1384.

## `Sketcher.SketchObject.makeMissingVerticalHorizontal`

```python
def makeMissingVerticalHorizontal(self, one_by_one: bool=False, /) -> None:
```

Applies the detected / set Vertical/Horizontal constraints. If the argument is True, then solving and redundant removal is done after each individual addition.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1390.

## `Sketcher.SketchObject.makeMissingEquality`

```python
def makeMissingEquality(self, one_by_one: bool=True, /) -> None:
```

Applies the detected / set Equality constraints. If the argument is True, then solving and redundant removal is done after each individual addition.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1396.

## `Sketcher.SketchObject.evaluateConstraints`

```python
def evaluateConstraints(self) -> bool:
```

Check for constraints with invalid indexes. Returns True if invalid constraints are found, False otherwise.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1402.

## `Sketcher.SketchObject.validateConstraints`

```python
def validateConstraints(self) -> None:
```

Removes constraints with invalid indexes.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1408.

## `Sketcher.SketchObject.autoRemoveRedundants`

```python
def autoRemoveRedundants(self, update_geometry: bool=True, /) -> None:
```

Removes constraints currently detected as redundant by the solver. If the argument is True, then the geometry is updated after solving.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1414.

## `Sketcher.SketchObject.toPythonCommands`

```python
def toPythonCommands(self) -> tuple[str, ...]:
```

Prints the commands that should be executed to recreate the Geometry and Constraints of the present sketch (excluding any External Geometry).

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1420.

## `Sketcher.SketchObject.setGeometryId`

```python
def setGeometryId(self, geo_id: int, id: int, /) -> None:
```

Sets the GeometryId of the SketchGeometryExtension of the geometry with the provided GeoId

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1426.

## `Sketcher.SketchObject.setGeometryIds`

```python
def setGeometryIds(self, geo_ids_to_ids: List[Tuple[int, int]], /) -> None:
```

Sets the GeometryId of the SketchGeometryExtension of the geometries with the provided GeoIds
Expects a list of pairs (GeoId, id)

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1432.

## `Sketcher.SketchObject.getGeometryId`

```python
def getGeometryId(self, geo_id: int, /) -> int:
```

Gets the GeometryId of the SketchGeometryExtension of the geometry with the provided GeoId

Evidence: public stub `Sketcher/__init__.pyi` line(s) 1438.

