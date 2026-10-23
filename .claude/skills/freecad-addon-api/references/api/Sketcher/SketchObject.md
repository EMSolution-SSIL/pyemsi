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

## `Sketcher.SketchObject.MissingPointOnPointConstraints`

```python
MissingPointOnPointConstraints: List = ...
```

Returns a list of (First FirstPos Second SecondPos Type) tuples with all the detected endpoint constraints.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 447.

## `Sketcher.SketchObject.MissingVerticalHorizontalConstraints`

```python
MissingVerticalHorizontalConstraints: List = ...
```

Returns a list of (First FirstPos Second SecondPos Type) tuples with all the detected vertical/horizontal constraints.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 449.

## `Sketcher.SketchObject.MissingLineEqualityConstraints`

```python
MissingLineEqualityConstraints: List = ...
```

Returns a list of (First FirstPos Second SecondPos) tuples with all the detected line segment equality constraints.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 451.

## `Sketcher.SketchObject.MissingRadiusConstraints`

```python
MissingRadiusConstraints: List = ...
```

Returns a list of (First FirstPos Second SecondPos) tuples with all the detected radius constraints.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 453.

## `Sketcher.SketchObject.OpenVertices`

```python
OpenVertices: Final[List] = ...
```

Returns a list of vertices positions.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 455.

## `Sketcher.SketchObject.ConstraintCount`

```python
ConstraintCount: Final[int] = ...
```

Number of Constraints in this sketch

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 457.

## `Sketcher.SketchObject.GeometryCount`

```python
GeometryCount: Final[int] = ...
```

Number of geometric objects in this sketch

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 459.

## `Sketcher.SketchObject.AxisCount`

```python
AxisCount: Final[int] = ...
```

Return the number of construction lines in the sketch which can be used as axes

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 461.

## `Sketcher.SketchObject.GeometryFacadeList`

```python
GeometryFacadeList: List = ...
```

Return a list of GeometryFacade objects corresponding to the PropertyGeometryList

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 463.

## `Sketcher.SketchObject.DoF`

```python
DoF: Final[int] = ...
```

Return the DoFs of the current solved sketch

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 465.

## `Sketcher.SketchObject.ConflictingConstraints`

```python
ConflictingConstraints: Final[List] = ...
```

Return a list of integers indicating the constraints detected as conflicting

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 467.

## `Sketcher.SketchObject.RedundantConstraints`

```python
RedundantConstraints: Final[List] = ...
```

Return a list of integers indicating the constraints detected as redundant

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 469.

## `Sketcher.SketchObject.PartiallyRedundantConstraints`

```python
PartiallyRedundantConstraints: Final[List] = ...
```

Return a list of integers indicating the constraints detected as partially redundant

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 471.

## `Sketcher.SketchObject.MalformedConstraints`

```python
MalformedConstraints: Final[List] = ...
```

Return a list of integers indicating the constraints detected as malformed

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 473.

## `Sketcher.SketchObject.ArcFitTolerance`

```python
@property
def ArcFitTolerance(self) -> float:

@ArcFitTolerance.setter
def ArcFitTolerance(self, value: float | int | dict[str, float] | tuple[float, float, float, float]) -> None:
```

Tolerance for fitting arcs of projected external geometry

Access: getter and setter declared in the stub.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 477, 482.

## `Sketcher.SketchObject.Constraints`

```python
@property
def Constraints(self) -> list[Constraint]:

@Constraints.setter
def Constraints(self, value: Constraint | list[Constraint]) -> None:
```

Sketch constraints

Access: getter and setter declared in the stub.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 486, 491.

## `Sketcher.SketchObject.Exports`

```python
@property
def Exports(self) -> list[DocumentObject | None]:

@Exports.setter
def Exports(self, value: Sequence[DocumentObject]) -> None:
```

Sketch export geometry

Access: getter and setter declared in the stub.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 495, 500.

## `Sketcher.SketchObject.ExternalGeo`

```python
@property
def ExternalGeo(self) -> list[Part.Geometry]:

@ExternalGeo.setter
def ExternalGeo(self, value: Part.Geometry | Sequence[Part.Geometry]) -> None:
```

Sketch external geometry

Access: getter and setter declared in the stub.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 504, 509.

## `Sketcher.SketchObject.ExternalGeometry`

```python
@property
def ExternalGeometry(self) -> list[tuple[DocumentObject, tuple[str, ...]]]:

@ExternalGeometry.setter
def ExternalGeometry(self, value: _DocumentObjectSubLinkInput | Sequence[_DocumentObjectSubLinkListItemInput]) -> None:
```

Sketch external geometry

Access: getter and setter declared in the stub.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 513, 518.

## `Sketcher.SketchObject.ExternalTypes`

```python
@property
def ExternalTypes(self) -> list[int]:

@ExternalTypes.setter
def ExternalTypes(self, value: Sequence[int]) -> None:
```

Sketch external geometry type: 0 = projection, 1 = intersection, 2 = both.

Access: getter and setter declared in the stub.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 522, 527.

## `Sketcher.SketchObject.FullyConstrained`

```python
@property
def FullyConstrained(self) -> bool:

@FullyConstrained.setter
def FullyConstrained(self, value: bool | int) -> None:
```

Sketch is fully constrained

Access: getter and setter declared in the stub.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 531, 536.

## `Sketcher.SketchObject.Geometry`

```python
@property
def Geometry(self) -> list[Part.Geometry]:

@Geometry.setter
def Geometry(self, value: Part.Geometry | Sequence[Part.Geometry]) -> None:
```

Sketch geometry

Access: getter and setter declared in the stub.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 540, 545.

## `Sketcher.SketchObject.InternalShape`

```python
@property
def InternalShape(self) -> Part.Shape:

@InternalShape.setter
def InternalShape(self, value: Part.Shape) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: getter and setter declared in the stub.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 549, 553.

## `Sketcher.SketchObject.MakeInternals`

```python
@property
def MakeInternals(self) -> bool:

@MakeInternals.setter
def MakeInternals(self, value: bool | int) -> None:
```

Enables selection of closed profiles within a sketch as input for operations

Access: getter and setter declared in the stub.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 557, 562.

## `Sketcher.SketchObject.solve`

```python
def solve(self) -> int:
```

Solve the sketch and update the geometry.

solve()

  Returns:
      0 in case of success, otherwise the following codes in this order of
      priority:
      -4 if over-constrained,
      -3 if conflicting constraints,
      -5 if malformed constraints
      -1 if solver error,
      -2 if redundant constraints.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 565.

## `Sketcher.SketchObject.addGeometry`

```python
@overload
def addGeometry(self, geo: Geometry, is_construction: bool=False, /) -> int:

@overload
def addGeometry(self, geo: List[Geometry], is_construction: bool=False, /) -> Tuple[int, ...]:

def addGeometry(self, geo: Union[Geometry, List[Geometry]], is_construction: bool=False, /) -> Union[int, Tuple[int, ...]]:
```

Add geometric objects to the sketch.

addGeometry(geo:Geometry, isConstruction=False) -> int
    Add a single geometric object to the sketch.

    Args:
        geo: The geometry to add. e.g. a Part.LineSegement
        isConstruction: Whether the added geometry is a "construction geometry".
            Defaults to `False`, i.e. by omitting, a regular geometry is added.

    Returns:
        The zero-based index of the newly added geometry.

addGeometry(geo:List(Geometry), isConstruction=False) -> Tuple(int)
    Add many geometric objects to the sketch.

    Args:
        geo: The geometry to add.
        isConstruction: see above.

    Returns:
        A tuple of zero-based indices of all newly added geometry.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 583, 587, 590.

## `Sketcher.SketchObject.delGeometry`

```python
def delGeometry(self, geo_id: int, no_solve: bool=False, /) -> None:
```

Delete a geometric object from the sketch.

delGeometry(geoId:int)

    Args:
        geoId: The zero-based index of the geometry to delete.
            Any internal alignment geometry thereof will be deleted, too.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 617.

## `Sketcher.SketchObject.delGeometries`

```python
def delGeometries(self, geo_ids: List[int], no_solve: bool=False, /) -> None:
```

Delete a list of geometric objects from the sketch.

delGeometries(geoIds:List(int))

    Args:
        geoId: A list of zero-based indices of the geometry to delete.
            Any internal alignment geometry thereof will be deleted, too.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 629.

## `Sketcher.SketchObject.deleteAllGeometry`

```python
def deleteAllGeometry(self, no_solve: bool=False, /) -> None:
```

Delete all the geometry objects from the sketch, except external geometry.

deleteAllGeometry()

Evidence: public stub `Sketcher/__init__.pyi` line(s) 641.

## `Sketcher.SketchObject.detectDegeneratedGeometries`

```python
def detectDegeneratedGeometries(self, tolerance: float, /) -> int:
```

Detect degenerated geometries. A curve geometry is considered degenerated
if the parameter range is less than the tolerance.

detectDegeneratedGeometries(tolerance:float)

    Args:
        tolerance: The tolerance to check the parameter range of a curve.

    Returns:
        The number of degenerated geometries.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 649.

## `Sketcher.SketchObject.removeDegeneratedGeometries`

```python
def removeDegeneratedGeometries(self, tolerance: float, /) -> int:
```

Remove degenerated geometries. A curve geometry is considered degenerated
if the parameter range is less than the tolerance.

removeDegeneratedGeometries(tolerance:float)

    Args:
        tolerance: The tolerance to check the parameter range of a curve.

    Returns:
        The number of degenerated geometries.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 664.

## `Sketcher.SketchObject.deleteAllConstraints`

```python
def deleteAllConstraints(self) -> None:
```

Delete all the constraints from the sketch.

deleteAllConstraints()

Evidence: public stub `Sketcher/__init__.pyi` line(s) 679.

## `Sketcher.SketchObject.toggleConstruction`

```python
def toggleConstruction(self, geo_id: int, /) -> None:
```

Toggles a geometry between regular and construction.

toggleConstruction(geoId:int)

    Args:
        geoId: The zero-based index of the geometry to toggle.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 687.

## `Sketcher.SketchObject.setConstruction`

```python
def setConstruction(self, geo_id: int, state: bool, /) -> None:
```

Set construction mode of a geometry.

setConstruction(geoId:int, state:bool)

    Args:
        geoId: The zero-based index of the geometry to configure.
        state: `True` configures the geometry to "construction geometry",
            `False` configures it to regular geometry.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 698.

## `Sketcher.SketchObject.getConstruction`

```python
def getConstruction(self, geo_id: int, /) -> bool:
```

Determine whether the given geometry is a "construction geometry".

getConstruction(geoId:int)

    Args:
        geoId: The zero-based index of the geometry to query.

    Returns:
        `True` if the geometry is "construction geometry" and
        `False` if it s a regular geometry.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 711.

## `Sketcher.SketchObject.addConstraint`

```python
@overload
def addConstraint(self, constraint: Constraint, /) -> int:

@overload
def addConstraint(self, constraints: List[Constraint], /) -> Tuple[int, ...]:

def addConstraint(self, constraint: Union[Constraint, List[Constraint]], /) -> Union[int, Tuple[int, ...]]:
```

Add constraints to the sketch.

addConstraint(constraint:Constraint) -> int
    Add a single constraint to the sketch and solves it.

    Returns:
        The zero-based index of the newly added constraint.

addConstraint(constraints:List(Constraint)) -> Tuple(int)
    Add many constraints to the sketch without solving.

    Returns:
        A tuple of zero-based indices of all newly added constraints.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 727, 731, 734.

## `Sketcher.SketchObject.delConstraint`

```python
def delConstraint(self, constraint_index: int, no_solve: bool=False, /) -> None:
```

Delete a constraint from the sketch.

delConstraint(constraintIndex:int)

    Args:
        constraintIndex: The zero-based index of the constraint to delete.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 752.

## `Sketcher.SketchObject.delConstraints`

```python
def delConstraints(self, constraint_indices: List[int], update_geometry: bool=True, no_solve: bool=False, /) -> None:
```

Delete multiple constraints from a sketch

delConstraints(constraintIndices: List[int], updateGeometry: bool)

    Args:
        constraintIndices: The zero-based indices of the constraints to delete
        updateGeometry: Whether to update the geometry after solve

Evidence: public stub `Sketcher/__init__.pyi` line(s) 763.

## `Sketcher.SketchObject.renameConstraint`

```python
def renameConstraint(self, constraint_index: int, name: str, /) -> None:
```

Rename a constraint in the sketch.

renameConstraint(constraintIndex:int, name:str)

    Args:
        constraintIndex: The zero-based index of the constraint to rename.
        name: The new name for the constraint.
            An empty string makes the constraint "unnamed" again.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 775.

## `Sketcher.SketchObject.getIndexByName`

```python
def getIndexByName(self, name: str, /) -> int:
```

Get the index of a constraint by name.

getIndexByName(name:str)

    Args:
        name: The name for the constraint to look up.
            If there is no such constraint an exception is raised.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 788.

## `Sketcher.SketchObject.setAllowUnaligned`

```python
def setAllowUnaligned(self, state: bool, /) -> None:
```

Set whether unaligned geometry is allowed in the sketch.

setAllowUnaligned(state:bool)

    Args:
        state: `True` allows unaligned geometry,
            `False` enforces aligned geometry.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 800.

## `Sketcher.SketchObject.carbonCopy`

```python
def carbonCopy(self, obj_name: str, as_construction: bool=True, /) -> None:
```

Copy another sketch's geometry and constraints into this sketch.

carbonCopy(objName:str, asConstruction=True)

    Args:
        ObjName: The name of the sketch object to copy from.
        asConstruction: Whether to copy the geometry as "construction geometry".

Evidence: public stub `Sketcher/__init__.pyi` line(s) 812.

## `Sketcher.SketchObject.addExternal`

```python
def addExternal(self, obj_name: str, sub_name: str, defining: bool=False, intersection: bool=False, /) -> None:
```

Add a link to an external geometry.

addExternal(objName:str, subName:str, defining:bool=False, intersection:bool=False)

    Args:
        objName: The name of the document object to reference.
        subName: The name of the sub-element of the object's shape to link as
            "external geometry".
        defining: Should the external edges be defining or construction?
        intersection: Should the external edges be projections or intersections?

Evidence: public stub `Sketcher/__init__.pyi` line(s) 824.

## `Sketcher.SketchObject.delExternal`

```python
def delExternal(self, ext_geo_id: int, /) -> None:
```

Delete an external geometry link from the sketch.

delExternal(extGeoId:int)

    Args:
        extGeoId: The zero-based index of the external geometry to remove.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 839.

## `Sketcher.SketchObject.delExternals`

```python
def delExternals(self, ext_geo_ids: List[int], /) -> None:
```

Delete a list of external geometry links from the sketch.

delExternals(extGeoIds:List(int))

    Args:
        extGeoIds: A list of zero-based indices of the external geometry to remove.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 850.

## `Sketcher.SketchObject.delConstraintOnPoint`

```python
@overload
def delConstraintOnPoint(self, vertex_id: int, /) -> None:

@overload
def delConstraintOnPoint(self, geo_id: int, point_pos: int, /) -> None:

def delConstraintOnPoint(self, *args: int) -> None:
```

Delete coincident constraints associated with a sketch point.

delConstraintOnPoint(vertexId:int)

    Args:
        vertexId: A zero-based index of the shape's vertices.

delConstraintOnPoint(geoId:int, pointPos:int)

    Args:
        geoId: The zero-based index of the geometry that contains the point.
        pointPos: Enum denoting which point on the geometry is meant:
            1: the start of a line or bounded curve.
            2: the end of a line or bounded curve.
            3: the center of a circle or ellipse.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 862, 866, 869.

## `Sketcher.SketchObject.delConstraintsToExternal`

```python
def delConstraintsToExternal(self) -> None:
```

Deletes all constraints referencing an external geometry.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 889.

## `Sketcher.SketchObject.setDatum`

```python
def setDatum(self, constraint: Union[int, str], value: Union[float, Quantity], /) -> None:
```

Set the value of a datum constraint (e.g. Distance or Angle)

setDatum(constraint, value)

    Args:
        constraint (int or str): The index or name of the constraint to set.
        value (float or Quantity): The value to set for the constraint. When
            using floats, values for linear dimensions are interpreted as
            millimeter, angular ones as radians.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 895.

## `Sketcher.SketchObject.setTextAndFont`

```python
def setTextAndFont(self, constraint: int, text: str, font: str, isheight: bool=True, isConstruction: bool=False) -> None:
```

Set the text and font of a Text constraint.

setTextAndFont(constraint: int, text: str, font: str, isHeight: bool, isConstruction: bool)

    Args:
        constraint: The index of the Text constraint.
        text: The text string to display.
        font: The full path to the font file (.ttf, .otf, etc.).
        isHeight: Is the line handle of the group the height of the text.
        isConstruction: Are text geometry construction of not.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 909.

## `Sketcher.SketchObject.getDatum`

```python
def getDatum(self, constraint: Union[int, str], /) -> Quantity:
```

Get the value of a datum constraint (e.g. Distance or Angle)

getDatum(constraint) -> Quantity

    Args:
        constraint (int or str): The index or name of the constraint to query.

    Returns:
        The value of the constraint.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 924.

## `Sketcher.SketchObject.setDriving`

```python
def setDriving(self, constraint_index: int, state: bool, /) -> None:
```

Set the Driving status of a datum constraint.

setDriving(constraintIndex:int, state:bool)

    Args:
        constraintIndex: The zero-based index of the constraint to configure.
        state: `True` sets the constraint to driving,
            `False` configures it as non-driving, i.e. reference.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 938.

## `Sketcher.SketchObject.setDatumsDriving`

```python
def setDatumsDriving(self, state: bool, /) -> None:
```

Set the Driving status of all datum constraints.

setDatumsDriving(state:bool)

    Args:
        state: `True` set all datum constraints to driving,
            `False` configures them as non-driving, i.e. reference.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 951.

## `Sketcher.SketchObject.moveDatumsToEnd`

```python
def moveDatumsToEnd(self) -> None:
```

Moves all datum constraints to the end of the constraint list.

moveDatumsToEnd()

    Warning: This method reorders the constraint indices. Previously held
        numeric references to constraints may reference different constraints
        after this operation.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 963.

## `Sketcher.SketchObject.getDriving`

```python
def getDriving(self, constraint_index: int, /) -> bool:
```

Get the Driving status of a datum constraint.

getDriving(constraintIndex:int)

    Args:
        constraintIndex: The zero-based index of the constraint to query.

    Returns:
        `True` if the constraint is driving,
        `False` if it is non-driving, i.e. reference.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 975.

## `Sketcher.SketchObject.toggleDriving`

```python
def toggleDriving(self, constraint_index: int, /) -> None:
```

Toggle the Driving status of a datum constraint.

toggleDriving(constraintIndex:int)

    Args:
        constraintIndex: The zero-based index of the constraint to toggle.

Evidence: public stub `Sketcher/__init__.pyi` line(s) 990.

