# `TechDraw::DrawViewDimension`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/TechDraw/App/DrawViewDimension.cpp:93`. Abstract macro: no.

Native parent: [TechDraw::DrawView](../TechDraw/DrawView.md). Read the parent record for inherited properties.

Direct binding association: `TechDraw.DrawViewDimension`. This is a source binding name, not a runtime wrapper check.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `AngleOverride` | `App::PropertyBool` | `bool` | `bool \| int` | User specified angles | `src/Mod/TechDraw/App/DrawViewDimension.cpp:198` |
| `Arbitrary` | `App::PropertyBool` | `bool` | `bool \| int` | Value overridden by user | `src/Mod/TechDraw/App/DrawViewDimension.cpp:148` |
| `ArbitraryTolerances` | `App::PropertyBool` | `bool` | `bool \| int` | Tolerance values overridden by user | `src/Mod/TechDraw/App/DrawViewDimension.cpp:149` |
| `AreaLeaderPoint` | `App::PropertyVector` | `Base.Vector` | `Base.Vector \| tuple[float, float, float]` | Area leader end point | `src/Mod/TechDraw/App/DrawViewDimension.cpp:208` |
| `BoxCorners` | `App::PropertyVectorList` | `list[Base.Vector]` | `Sequence[_VectorInput]` | Feature bounding box corners as of last reference update.  Used by autocorrect | `src/Mod/TechDraw/App/DrawViewDimension.cpp:218` |
| `EqualTolerance` | `App::PropertyBool` | `bool` | `bool \| int` | If over- and undertolerance are equal | `src/Mod/TechDraw/App/DrawViewDimension.cpp:164` |
| `ExtensionAngle` | `App::PropertyAngle` | `Base.Quantity` | `float \| str \| Base.Quantity` | Extension line angle | `src/Mod/TechDraw/App/DrawViewDimension.cpp:204` |
| `FormatSpec` | `App::PropertyString` | `str` | `str` | Dimension format | `src/Mod/TechDraw/App/DrawViewDimension.cpp:133` |
| `FormatSpecOverTolerance` | `App::PropertyString` | `str` | `str` | Dimension overtolerance format | `src/Mod/TechDraw/App/DrawViewDimension.cpp:138` |
| `FormatSpecUnderTolerance` | `App::PropertyString` | `str` | `str` | Dimension undertolerance format | `src/Mod/TechDraw/App/DrawViewDimension.cpp:143` |
| `Inverted` | `App::PropertyBool` | `bool` | `bool \| int` | The dimensional value is displayed inverted | `src/Mod/TechDraw/App/DrawViewDimension.cpp:186` |
| `LineAngle` | `App::PropertyAngle` | `Base.Quantity` | `float \| str \| Base.Quantity` | Dimension line angle | `src/Mod/TechDraw/App/DrawViewDimension.cpp:203` |
| `MeasureType` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Not documented by registration | `src/Mod/TechDraw/App/DrawViewDimension.cpp:158` |
| `OverTolerance` | `App::PropertyQuantityConstraint` | `Base.Quantity` | `float \| str \| Base.Quantity` | Not documented by registration | `src/Mod/TechDraw/App/DrawViewDimension.cpp:170` |
| `References2D` | `App::PropertyLinkSubList` | `list[tuple[DocumentObject, tuple[str, ...]]]` | `_DocumentObjectSubLinkInput \| Sequence[_DocumentObjectSubLinkListItemInput]` | Projected Geometry References | `src/Mod/TechDraw/App/DrawViewDimension.cpp:120` |
| `References3D` | `App::PropertyLinkSubList` | `list[tuple[DocumentObject, tuple[str, ...]]]` | `_DocumentObjectSubLinkInput \| Sequence[_DocumentObjectSubLinkListItemInput]` | 3D Geometry References | `src/Mod/TechDraw/App/DrawViewDimension.cpp:126` |
| `SavedGeometry` | `Part::PropertyTopoShapeList` | `list[Part.Shape]` | `Part.Shape \| Sequence[Part.Shape]` | Reference Geometry | `src/Mod/TechDraw/App/DrawViewDimension.cpp:211` |
| `ShowSupplementary` | `App::PropertyBool` | `bool` | `bool \| int` | Toggle supplementary angle Angle displayed is dependent on selection order | `src/Mod/TechDraw/App/DrawViewDimension.cpp:192` |
| `ShowUnits` | `App::PropertyBool` | `bool` | `bool \| int` | Show or hide the units. | `src/Mod/TechDraw/App/DrawViewDimension.cpp:248` |
| `TheoreticalExact` | `App::PropertyBool` | `bool` | `bool \| int` | If theoretical exact (basic) dimension | `src/Mod/TechDraw/App/DrawViewDimension.cpp:159` |
| `Type` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Not documented by registration | `src/Mod/TechDraw/App/DrawViewDimension.cpp:156` |
| `UnderTolerance` | `App::PropertyQuantityConstraint` | `Base.Quantity` | `float \| str \| Base.Quantity` | Not documented by registration | `src/Mod/TechDraw/App/DrawViewDimension.cpp:178` |
| `UseActualArea` | `App::PropertyBool` | `bool` | `bool \| int` | If true, area dimensions return the area of the face minus the areas of any enclosed faces.                        If false, the area of the face's outer boundary is returned. | `src/Mod/TechDraw/App/DrawViewDimension.cpp:244` |
| `UseAreaLeaderPoint` | `App::PropertyBool` | `bool` | `bool \| int` | If true, the area leader end pt uses user clicked pt instead of face center. | `src/Mod/TechDraw/App/DrawViewDimension.cpp:206` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

