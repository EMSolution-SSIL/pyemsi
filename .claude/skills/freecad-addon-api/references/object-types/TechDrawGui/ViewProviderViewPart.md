# `TechDrawGui::ViewProviderViewPart`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: Other native property owner; not a Document.addObject type. Registration: `src/Mod/TechDraw/Gui/ViewProviderViewPart.cpp:74`. Abstract macro: no.

Native parent: [TechDrawGui::ViewProviderDrawingView](../TechDrawGui/ViewProviderDrawingView.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `Gui::ViewProviderDocumentObject` -> `FreeCADGui.ViewProviderDocumentObject`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `Gui::ViewProviderDocumentObject`: This implementation requires the main thread and creates ViewProviderDocumentObjectPy; the binding is FreeCADGui.ViewProviderDocumentObject. It does not prove that every derived view provider returns this exact wrapper. Evidence: `src/Gui/ViewProviderDocumentObject.cpp:606`, `src/Gui/ViewProviderDocumentObject.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `ArcCenterMarks` | `App::PropertyBool` | `bool` | `bool \| int` | Center marks on/off | `src/Mod/TechDraw/Gui/ViewProviderViewPart.cpp:112` |
| `BreakLineColor` | `App::PropertyColor` | `tuple[float, float, float, float]` | `int \| tuple[float, float, float] \| tuple[float, float, float, float] \| tuple[int, int, int] \| tuple[int, int, int, int]` | Set break line  color if applicable | `src/Mod/TechDraw/Gui/ViewProviderViewPart.cpp:141` |
| `BreakLineStyle` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Set break line style if applicable | `src/Mod/TechDraw/Gui/ViewProviderViewPart.cpp:139` |
| `BreakLineType` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Adjusts the type of break line depiction on broken views | `src/Mod/TechDraw/Gui/ViewProviderViewPart.cpp:137` |
| `CenterScale` | `App::PropertyFloat` | `float` | `float` | Center mark size adjustment, if enabled | `src/Mod/TechDraw/Gui/ViewProviderViewPart.cpp:113` |
| `ExtraWidth` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | The thickness of LineGroup Extra lines, if enabled | `src/Mod/TechDraw/Gui/ViewProviderViewPart.cpp:105` |
| `FaceColor` | `App::PropertyColor` | `tuple[float, float, float, float]` | `int \| tuple[float, float, float] \| tuple[float, float, float, float] \| tuple[int, int, int] \| tuple[int, int, int, int]` | Set color of faces | `src/Mod/TechDraw/Gui/ViewProviderViewPart.cpp:147` |
| `FaceTransparency` | `App::PropertyPercent` | `int` | `int \| dict[str, int] \| tuple[int, int, int, int]` | Set transparency of faces | `src/Mod/TechDraw/Gui/ViewProviderViewPart.cpp:149` |
| `HiddenWidth` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | The thickness of hidden lines, if enabled (line groups xx.1) | `src/Mod/TechDraw/Gui/ViewProviderViewPart.cpp:99` |
| `HighlightAdjust` | `App::PropertyFloat` | `float` | `float` | Adjusts the rotation of the Detail highlight | `src/Mod/TechDraw/Gui/ViewProviderViewPart.cpp:133` |
| `HighlightLineColor` | `App::PropertyColor` | `tuple[float, float, float, float]` | `int \| tuple[float, float, float] \| tuple[float, float, float, float] \| tuple[int, int, int] \| tuple[int, int, int, int]` | Set highlight line color if applicable | `src/Mod/TechDraw/Gui/ViewProviderViewPart.cpp:131` |
| `HighlightLineStyle` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Set highlight line style if applicable | `src/Mod/TechDraw/Gui/ViewProviderViewPart.cpp:129` |
| `HorizCenterLine` | `App::PropertyBool` | `bool` | `bool \| int` | Show a horizontal centerline through view | `src/Mod/TechDraw/Gui/ViewProviderViewPart.cpp:110` |
| `IncludeCutLine` | `App::PropertyBool` | `bool` | `bool \| int` | Show/hide section cut line if applicable | `src/Mod/TechDraw/Gui/ViewProviderViewPart.cpp:117` |
| `IsoWidth` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | The thickness of isoparameter lines, if enabled | `src/Mod/TechDraw/Gui/ViewProviderViewPart.cpp:102` |
| `LineWidth` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | The thickness of visible lines (line groups xx.2 | `src/Mod/TechDraw/Gui/ViewProviderViewPart.cpp:96` |
| `SectionLineColor` | `App::PropertyColor` | `tuple[float, float, float, float]` | `int \| tuple[float, float, float] \| tuple[float, float, float, float] \| tuple[int, int, int] \| tuple[int, int, int, int]` | Set section line color if applicable | `src/Mod/TechDraw/Gui/ViewProviderViewPart.cpp:120` |
| `SectionLineMarks` | `App::PropertyBool` | `bool` | `bool \| int` | Show marks at direction changes for ComplexSection | `src/Mod/TechDraw/Gui/ViewProviderViewPart.cpp:125` |
| `SectionLineStyle` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Set section line style if applicable | `src/Mod/TechDraw/Gui/ViewProviderViewPart.cpp:118` |
| `ShowAllEdges` | `App::PropertyBool` | `bool` | `bool \| int` | Temporarily show invisible lines | `src/Mod/TechDraw/Gui/ViewProviderViewPart.cpp:144` |
| `ShowSectionLine` | `App::PropertyBool` | `bool` | `bool \| int` | Show/hide section line if applicable | `src/Mod/TechDraw/Gui/ViewProviderViewPart.cpp:116` |
| `VertCenterLine` | `App::PropertyBool` | `bool` | `bool \| int` | Show a vertical centerline through view | `src/Mod/TechDraw/Gui/ViewProviderViewPart.cpp:111` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

