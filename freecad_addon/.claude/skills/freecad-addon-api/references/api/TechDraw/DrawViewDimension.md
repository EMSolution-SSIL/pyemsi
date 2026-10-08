# `TechDraw.DrawViewDimension`

[Module](index.md)

```python
class DrawViewDimension(DrawView):
```

Feature for creating and manipulating Technical Drawing Dimensions

Author: WandererFan (wandererfan@gmail.com)
License: LGPL-2.1-or-later

Evidence: public stub `TechDraw/__init__.pyi` line 1231. Inherited members are on the named base's reference; aliases keep their imported identity.

## `TechDraw.DrawViewDimension.AngleOverride`

```python
@property
def AngleOverride(self) -> bool:

@AngleOverride.setter
def AngleOverride(self, value: bool | int) -> None:
```

User specified angles

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1240, 1245.

## `TechDraw.DrawViewDimension.Arbitrary`

```python
@property
def Arbitrary(self) -> bool:

@Arbitrary.setter
def Arbitrary(self, value: bool | int) -> None:
```

Value overridden by user

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1249, 1254.

## `TechDraw.DrawViewDimension.ArbitraryTolerances`

```python
@property
def ArbitraryTolerances(self) -> bool:

@ArbitraryTolerances.setter
def ArbitraryTolerances(self, value: bool | int) -> None:
```

Tolerance values overridden by user

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1258, 1263.

## `TechDraw.DrawViewDimension.AreaLeaderPoint`

```python
@property
def AreaLeaderPoint(self) -> Base.Vector:

@AreaLeaderPoint.setter
def AreaLeaderPoint(self, value: Base.Vector | tuple[float, float, float]) -> None:
```

Area leader end point

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1267, 1272.

## `TechDraw.DrawViewDimension.BoxCorners`

```python
@property
def BoxCorners(self) -> list[Base.Vector]:

@BoxCorners.setter
def BoxCorners(self, value: Sequence[_VectorInput]) -> None:
```

Feature bounding box corners as of last reference update.  Used by autocorrect

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1276, 1281.

## `TechDraw.DrawViewDimension.EqualTolerance`

```python
@property
def EqualTolerance(self) -> bool:

@EqualTolerance.setter
def EqualTolerance(self, value: bool | int) -> None:
```

If over- and undertolerance are equal

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1285, 1290.

## `TechDraw.DrawViewDimension.ExtensionAngle`

```python
@property
def ExtensionAngle(self) -> Base.Quantity:

@ExtensionAngle.setter
def ExtensionAngle(self, value: float | str | Base.Quantity) -> None:
```

Extension line angle

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1294, 1299.

## `TechDraw.DrawViewDimension.FormatSpec`

```python
@property
def FormatSpec(self) -> str:

@FormatSpec.setter
def FormatSpec(self, value: str) -> None:
```

Dimension format

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1303, 1308.

## `TechDraw.DrawViewDimension.FormatSpecOverTolerance`

```python
@property
def FormatSpecOverTolerance(self) -> str:

@FormatSpecOverTolerance.setter
def FormatSpecOverTolerance(self, value: str) -> None:
```

Dimension overtolerance format

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1312, 1317.

## `TechDraw.DrawViewDimension.FormatSpecUnderTolerance`

```python
@property
def FormatSpecUnderTolerance(self) -> str:

@FormatSpecUnderTolerance.setter
def FormatSpecUnderTolerance(self, value: str) -> None:
```

Dimension undertolerance format

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1321, 1326.

## `TechDraw.DrawViewDimension.Inverted`

```python
@property
def Inverted(self) -> bool:

@Inverted.setter
def Inverted(self, value: bool | int) -> None:
```

The dimensional value is displayed inverted

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1330, 1335.

## `TechDraw.DrawViewDimension.LineAngle`

```python
@property
def LineAngle(self) -> Base.Quantity:

@LineAngle.setter
def LineAngle(self, value: float | str | Base.Quantity) -> None:
```

Dimension line angle

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1339, 1344.

## `TechDraw.DrawViewDimension.MeasureType`

```python
@property
def MeasureType(self) -> str:

@MeasureType.setter
def MeasureType(self, value: str | list[str]) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1348, 1352.

## `TechDraw.DrawViewDimension.OverTolerance`

```python
@property
def OverTolerance(self) -> Base.Quantity:

@OverTolerance.setter
def OverTolerance(self, value: float | str | Base.Quantity) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1356, 1360.

## `TechDraw.DrawViewDimension.References2D`

```python
@property
def References2D(self) -> list[tuple[DocumentObject, tuple[str, ...]]]:

@References2D.setter
def References2D(self, value: _DocumentObjectSubLinkInput | Sequence[_DocumentObjectSubLinkListItemInput]) -> None:
```

Projected Geometry References

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1364, 1369.

## `TechDraw.DrawViewDimension.References3D`

```python
@property
def References3D(self) -> list[tuple[DocumentObject, tuple[str, ...]]]:

@References3D.setter
def References3D(self, value: _DocumentObjectSubLinkInput | Sequence[_DocumentObjectSubLinkListItemInput]) -> None:
```

3D Geometry References

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1373, 1378.

## `TechDraw.DrawViewDimension.SavedGeometry`

```python
@property
def SavedGeometry(self) -> list[Part.Shape]:

@SavedGeometry.setter
def SavedGeometry(self, value: Part.Shape | Sequence[Part.Shape]) -> None:
```

Reference Geometry

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1382, 1387.

## `TechDraw.DrawViewDimension.ShowSupplementary`

```python
@property
def ShowSupplementary(self) -> bool:

@ShowSupplementary.setter
def ShowSupplementary(self, value: bool | int) -> None:
```

Toggle supplementary angle
Angle displayed is dependent on selection order

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1391, 1397.

## `TechDraw.DrawViewDimension.ShowUnits`

```python
@property
def ShowUnits(self) -> bool:

@ShowUnits.setter
def ShowUnits(self, value: bool | int) -> None:
```

Show or hide the units.

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1401, 1406.

## `TechDraw.DrawViewDimension.TheoreticalExact`

```python
@property
def TheoreticalExact(self) -> bool:

@TheoreticalExact.setter
def TheoreticalExact(self, value: bool | int) -> None:
```

If theoretical exact (basic) dimension

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1410, 1415.

## `TechDraw.DrawViewDimension.Type`

```python
@property
def Type(self) -> str:

@Type.setter
def Type(self, value: str | list[str]) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1419, 1423.

## `TechDraw.DrawViewDimension.UnderTolerance`

```python
@property
def UnderTolerance(self) -> Base.Quantity:

@UnderTolerance.setter
def UnderTolerance(self, value: float | str | Base.Quantity) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1427, 1431.

## `TechDraw.DrawViewDimension.UseActualArea`

```python
@property
def UseActualArea(self) -> bool:

@UseActualArea.setter
def UseActualArea(self, value: bool | int) -> None:
```

If true, area dimensions return the area of the face minus the areas of any enclosed faces.                        If false, the area of the face's outer boundary is returned.

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1435, 1440.

## `TechDraw.DrawViewDimension.UseAreaLeaderPoint`

```python
@property
def UseAreaLeaderPoint(self) -> bool:

@UseAreaLeaderPoint.setter
def UseAreaLeaderPoint(self, value: bool | int) -> None:
```

If true, the area leader end pt uses user clicked pt instead of face center.

Access: getter and setter declared in the stub.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1444, 1449.

## `TechDraw.DrawViewDimension.getRawValue`

```python
def getRawValue(self) -> Any:
```

getRawValue() - returns Dimension value in mm.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1452.

## `TechDraw.DrawViewDimension.getText`

```python
def getText(self) -> Any:
```

getText() - returns Dimension text.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1456.

## `TechDraw.DrawViewDimension.getLinearPoints`

```python
def getLinearPoints(self) -> Any:
```

getLinearPoints() - returns list of points for linear Dimension

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1460.

## `TechDraw.DrawViewDimension.getArcPoints`

```python
def getArcPoints(self) -> Any:
```

getArcPoints() - returns list of points for circle/arc Dimension

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1464.

## `TechDraw.DrawViewDimension.getAnglePoints`

```python
def getAnglePoints(self) -> Any:
```

getAnglePoints() - returns list of points for angle Dimension

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1468.

## `TechDraw.DrawViewDimension.getAreaPoints`

```python
def getAreaPoints(self) -> Any:
```

getAreaPoints() - returns list of values (center, filled area, actual area) for area Dimension.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1472.

## `TechDraw.DrawViewDimension.getArrowPositions`

```python
def getArrowPositions(self) -> Any:
```

getArrowPositions() - returns list of locations or Dimension Arrowheads. Locations are in unscaled coordinates of parent View

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `TechDraw/__init__.pyi` line(s) 1476.

