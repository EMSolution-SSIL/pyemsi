# `TechDrawGui::ViewProviderDimension`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: Other native property owner; not a Document.addObject type. Registration: `src/Mod/TechDraw/Gui/ViewProviderDimension.cpp:68`. Abstract macro: no.

Native parent: [TechDrawGui::ViewProviderDrawingView](../TechDrawGui/ViewProviderDrawingView.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `Gui::ViewProviderDocumentObject` -> `FreeCADGui.ViewProviderDocumentObject`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `Gui::ViewProviderDocumentObject`: This implementation requires the main thread and creates ViewProviderDocumentObjectPy; the binding is FreeCADGui.ViewProviderDocumentObject. It does not prove that every derived view provider returns this exact wrapper. Evidence: `src/Gui/ViewProviderDocumentObject.cpp:606`, `src/Gui/ViewProviderDocumentObject.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `AllowSnap` | `App::PropertyBool` | `bool` | `bool \| int` | Dimension will snap to position if true | `src/Mod/TechDraw/Gui/ViewProviderDimension.cpp:113` |
| `ArrowStyle` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Arrow end symbol - point, filled arrow, etc | `src/Mod/TechDraw/Gui/ViewProviderDimension.cpp:90` |
| `Arrowsize` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | Arrow size in units | `src/Mod/TechDraw/Gui/ViewProviderDimension.cpp:85` |
| `Color` | `App::PropertyColor` | `tuple[float, float, float, float]` | `int \| tuple[float, float, float] \| tuple[float, float, float, float] \| tuple[int, int, int] \| tuple[int, int, int, int]` | Color of the dimension | `src/Mod/TechDraw/Gui/ViewProviderDimension.cpp:96` |
| `FlipArrowheads` | `App::PropertyBool` | `bool` | `bool \| int` | Reverses usual direction of dimension line terminators | `src/Mod/TechDraw/Gui/ViewProviderDimension.cpp:104` |
| `Font` | `App::PropertyFont` | `str` | `str` | The name of the font to use | `src/Mod/TechDraw/Gui/ViewProviderDimension.cpp:80` |
| `Fontsize` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | Dimension text size in units | `src/Mod/TechDraw/Gui/ViewProviderDimension.cpp:82` |
| `GapFactorASME` | `App::PropertyFloat` | `float` | `float` | Adjusts the gap between dimension point and extension line | `src/Mod/TechDraw/Gui/ViewProviderDimension.cpp:108` |
| `GapFactorISO` | `App::PropertyFloat` | `float` | `float` | Adjusts the gap between dimension point and extension line | `src/Mod/TechDraw/Gui/ViewProviderDimension.cpp:106` |
| `LineSpacingFactorISO` | `App::PropertyFloat` | `float` | `float` | Adjusts the gap between dimension line and dimension text | `src/Mod/TechDraw/Gui/ViewProviderDimension.cpp:110` |
| `LineWidth` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | Dimension line width | `src/Mod/TechDraw/Gui/ViewProviderDimension.cpp:94` |
| `RenderingExtent` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Select the rendering mode by space requirements | `src/Mod/TechDraw/Gui/ViewProviderDimension.cpp:101` |
| `StandardAndStyle` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Standard and style according to which dimension is drawn | `src/Mod/TechDraw/Gui/ViewProviderDimension.cpp:97` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

