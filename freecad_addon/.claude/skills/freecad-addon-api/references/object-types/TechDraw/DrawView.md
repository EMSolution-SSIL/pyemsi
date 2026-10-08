# `TechDraw::DrawView`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/TechDraw/App/DrawView.cpp:95`. Abstract macro: no.

Native parent: [App::DocumentObject](../App/DocumentObject.md). Read the parent record for inherited properties.

Direct binding association: `TechDraw.DrawView`. This is a source binding name, not a runtime wrapper check.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `Caption` | `App::PropertyString` | `str` | `str` | Short text about the view | `src/Mod/TechDraw/App/DrawView.cpp:113` |
| `CaptionLocation` | `App::PropertyVector` | `Base.Vector` | `Base.Vector \| tuple[float, float, float]` | Location of the caption relative to the view | `src/Mod/TechDraw/App/DrawView.cpp:114` |
| `CaptionSnap` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Snap the caption to the view's top, bottom, left or right edge | `src/Mod/TechDraw/App/DrawView.cpp:116` |
| `LockPosition` | `App::PropertyBool` | `bool` | `bool \| int` | Lock View position to parent Page or Group | `src/Mod/TechDraw/App/DrawView.cpp:105` |
| `Rotation` | `App::PropertyAngle` | `Base.Quantity` | `float \| str \| Base.Quantity` | Rotation in degrees counterclockwise | `src/Mod/TechDraw/App/DrawView.cpp:106` |
| `Scale` | `App::PropertyFloatConstraint` | `float` | `float \| int \| dict[str, float] \| tuple[float, float, float, float]` | Scale factor of the view (decimal value). For fractions, use an expression (e.g. =1/10). | `src/Mod/TechDraw/App/DrawView.cpp:110` |
| `ScaleType` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Scale Type | `src/Mod/TechDraw/App/DrawView.cpp:109` |
| `X` | `App::PropertyDistance` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | X position | `src/Mod/TechDraw/App/DrawView.cpp:103` |
| `Y` | `App::PropertyDistance` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Y position | `src/Mod/TechDraw/App/DrawView.cpp:104` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

