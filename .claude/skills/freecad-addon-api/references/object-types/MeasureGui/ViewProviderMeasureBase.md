# `MeasureGui::ViewProviderMeasureBase`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: Other native property owner; not a Document.addObject type. Registration: `src/Mod/Measure/Gui/ViewProviderMeasureBase.cpp:78`. Abstract macro: no.

Native parent: [Gui::ViewProviderDocumentObject](../Gui/ViewProviderDocumentObject.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `Gui::ViewProviderDocumentObject` -> `FreeCADGui.ViewProviderDocumentObject`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `Gui::ViewProviderDocumentObject`: This implementation requires the main thread and creates ViewProviderDocumentObjectPy; the binding is FreeCADGui.ViewProviderDocumentObject. It does not prove that every derived view provider returns this exact wrapper. Evidence: `src/Gui/ViewProviderDocumentObject.cpp:606`, `src/Gui/ViewProviderDocumentObject.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `ArrowHeight` | `App::PropertyFloat` | `float` | `float` | Height of arrow indicators | `src/Mod/Measure/Gui/ViewProviderMeasureBase.cpp:113` |
| `ArrowRadius` | `App::PropertyFloat` | `float` | `float` | Radius of arrow indicators | `src/Mod/Measure/Gui/ViewProviderMeasureBase.cpp:120` |
| `FontSize` | `App::PropertyInteger` | `int` | `int` | Size of measurement text | `src/Mod/Measure/Gui/ViewProviderMeasureBase.cpp:106` |
| `LabelPosition` | `App::PropertyVector` | `Base.Vector` | `Base.Vector \| tuple[float, float, float]` | Position of measurement label | `src/Mod/Measure/Gui/ViewProviderMeasureBase.cpp:127` |
| `LineColor` | `App::PropertyColor` | `tuple[float, float, float, float]` | `int \| tuple[float, float, float] \| tuple[float, float, float, float] \| tuple[int, int, int] \| tuple[int, int, int, int]` | Color for the measurement lines | `src/Mod/Measure/Gui/ViewProviderMeasureBase.cpp:99` |
| `TextBackgroundColor` | `App::PropertyColor` | `tuple[float, float, float, float]` | `int \| tuple[float, float, float] \| tuple[float, float, float, float] \| tuple[int, int, int] \| tuple[int, int, int, int]` | Color for the measurement text background | `src/Mod/Measure/Gui/ViewProviderMeasureBase.cpp:92` |
| `TextColor` | `App::PropertyColor` | `tuple[float, float, float, float]` | `int \| tuple[float, float, float] \| tuple[float, float, float, float] \| tuple[int, int, int] \| tuple[int, int, int, int]` | Color for the measurement text | `src/Mod/Measure/Gui/ViewProviderMeasureBase.cpp:85` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

