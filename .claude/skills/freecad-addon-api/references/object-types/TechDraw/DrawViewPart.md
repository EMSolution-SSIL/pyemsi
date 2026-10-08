# `TechDraw::DrawViewPart`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/TechDraw/App/DrawViewPart.cpp:101`. Abstract macro: no.

Native parent: [TechDraw::DrawView](../TechDraw/DrawView.md). Read the parent record for inherited properties.

Direct binding association: `TechDraw.DrawViewPart`. This is a source binding name, not a runtime wrapper check.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `CoarseView` | `App::PropertyBool` | `bool` | `bool \| int` | Coarse View on/off | `src/Mod/TechDraw/App/DrawViewPart.cpp:132` |
| `Direction` | `App::PropertyVector` | `Base.Vector` | `Base.Vector \| tuple[float, float, float]` | Projection Plane normal. View direction for the projection plane | `src/Mod/TechDraw/App/DrawViewPart.cpp:122` |
| `Focus` | `App::PropertyDistance` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Perspective view focus distance | `src/Mod/TechDraw/App/DrawViewPart.cpp:128` |
| `HardHidden` | `App::PropertyBool` | `bool` | `bool \| int` | Show Hidden Hard lines | `src/Mod/TechDraw/App/DrawViewPart.cpp:141` |
| `IsoCount` | `App::PropertyInteger` | `int` | `int` | Number of iso parameters lines | `src/Mod/TechDraw/App/DrawViewPart.cpp:149` |
| `IsoHidden` | `App::PropertyBool` | `bool` | `bool \| int` | Show Hidden Iso u, v lines | `src/Mod/TechDraw/App/DrawViewPart.cpp:147` |
| `IsoVisible` | `App::PropertyBool` | `bool` | `bool \| int` | Show Visible Iso u, v lines | `src/Mod/TechDraw/App/DrawViewPart.cpp:139` |
| `Perspective` | `App::PropertyBool` | `bool` | `bool \| int` | Perspective(true) or Orthographic(false) projection | `src/Mod/TechDraw/App/DrawViewPart.cpp:126` |
| `ScrubCount` | `App::PropertyInteger` | `int` | `int` | The number of times FreeCAD should try to clean the HLR result. | `src/Mod/TechDraw/App/DrawViewPart.cpp:152` |
| `SeamHidden` | `App::PropertyBool` | `bool` | `bool \| int` | Show Hidden Seam lines | `src/Mod/TechDraw/App/DrawViewPart.cpp:145` |
| `SeamVisible` | `App::PropertyBool` | `bool` | `bool \| int` | Show Visible Seam lines | `src/Mod/TechDraw/App/DrawViewPart.cpp:136` |
| `SmoothHidden` | `App::PropertyBool` | `bool` | `bool \| int` | Show Hidden Smooth lines | `src/Mod/TechDraw/App/DrawViewPart.cpp:143` |
| `SmoothVisible` | `App::PropertyBool` | `bool` | `bool \| int` | Show Visible Smooth lines | `src/Mod/TechDraw/App/DrawViewPart.cpp:134` |
| `Source` | `App::PropertyLinkList` | `list[DocumentObject \| None]` | `Sequence[DocumentObject]` | 3D Shape to view | `src/Mod/TechDraw/App/DrawViewPart.cpp:117` |
| `XDirection` | `App::PropertyVector` | `Base.Vector` | `Base.Vector \| tuple[float, float, float]` | Projection Plane X Axis in R3. Rotates/Mirrors View | `src/Mod/TechDraw/App/DrawViewPart.cpp:124` |
| `XSource` | `App::PropertyXLinkList` | `_DocumentObjectList \| _DocumentObjectSubLinkList` | `_DocumentObjectListInput \| _DocumentObjectSubLinkListInput` | External 3D Shape to view | `src/Mod/TechDraw/App/DrawViewPart.cpp:120` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

