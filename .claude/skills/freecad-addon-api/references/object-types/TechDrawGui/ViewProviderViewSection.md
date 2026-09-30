# `TechDrawGui::ViewProviderViewSection`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: Other native property owner; not a Document.addObject type. Registration: `src/Mod/TechDraw/Gui/ViewProviderViewSection.cpp:52`. Abstract macro: no.

Native parent: [TechDrawGui::ViewProviderViewPart](../TechDrawGui/ViewProviderViewPart.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `Gui::ViewProviderDocumentObject` -> `FreeCADGui.ViewProviderDocumentObject`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `Gui::ViewProviderDocumentObject`: This implementation requires the main thread and creates ViewProviderDocumentObjectPy; the binding is FreeCADGui.ViewProviderDocumentObject. It does not prove that every derived view provider returns this exact wrapper. Evidence: `src/Gui/ViewProviderDocumentObject.cpp:606`, `src/Gui/ViewProviderDocumentObject.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `CutSurfaceColor` | `App::PropertyColor` | `tuple[float, float, float, float]` | `int \| tuple[float, float, float] \| tuple[float, float, float, float] \| tuple[int, int, int] \| tuple[int, int, int, int]` | Set color of the cut surface | `src/Mod/TechDraw/Gui/ViewProviderViewSection.cpp:66` |
| `CutSurfaceTransparency` | `App::PropertyPercent` | `int` | `int \| dict[str, int] \| tuple[int, int, int, int]` | Set transparency of the cut surface | `src/Mod/TechDraw/Gui/ViewProviderViewSection.cpp:68` |
| `GeomHatchColor` | `App::PropertyColor` | `tuple[float, float, float, float]` | `int \| tuple[float, float, float] \| tuple[float, float, float, float] \| tuple[int, int, int] \| tuple[int, int, int, int]` | The color of the Geometric hatch pattern | `src/Mod/TechDraw/Gui/ViewProviderViewSection.cpp:77` |
| `HatchColor` | `App::PropertyColor` | `tuple[float, float, float, float]` | `int \| tuple[float, float, float] \| tuple[float, float, float, float] \| tuple[int, int, int] \| tuple[int, int, int, int]` | The color of the Svg hatch pattern | `src/Mod/TechDraw/Gui/ViewProviderViewSection.cpp:75` |
| `HatchCutSurface` | `App::PropertyBool` | `bool` | `bool \| int` | Hatch the cut surface | `src/Mod/TechDraw/Gui/ViewProviderViewSection.cpp:73` |
| `SectionLineArrowsize` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | Section line arrow size in units | `src/Mod/TechDraw/Gui/ViewProviderViewSection.cpp:86` |
| `SectionLineFont` | `App::PropertyFont` | `str` | `str` | The name of the font to use for the section line | `src/Mod/TechDraw/Gui/ViewProviderViewSection.cpp:82` |
| `SectionLineFontsize` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | Section line text size in units | `src/Mod/TechDraw/Gui/ViewProviderViewSection.cpp:84` |
| `WeightPattern` | `App::PropertyFloat` | `float` | `float` | GeomHatch pattern line thickness | `src/Mod/TechDraw/Gui/ViewProviderViewSection.cpp:80` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

