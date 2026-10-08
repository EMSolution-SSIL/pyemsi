# `PathGui::ViewProviderPath`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: Other native property owner; not a Document.addObject type. Registration: `src/Mod/CAM/Gui/ViewProviderPath.cpp:143`. Abstract macro: no.

Native parent: [Gui::ViewProviderGeometryObject](../Gui/ViewProviderGeometryObject.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `Gui::ViewProviderGeometryObject` -> `FreeCADGui.ViewProviderGeometryObject`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `Gui::ViewProviderDocumentObject`: This implementation requires the main thread and creates ViewProviderDocumentObjectPy; the binding is FreeCADGui.ViewProviderDocumentObject. It does not prove that every derived view provider returns this exact wrapper. Evidence: `src/Gui/ViewProviderDocumentObject.cpp:606`, `src/Gui/ViewProviderDocumentObject.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `LineWidth` | `App::PropertyInteger` | `int` | `int` | The line width of this path | `src/Mod/CAM/Gui/ViewProviderPath.cpp:172` |
| `MarkerColor` | `App::PropertyColor` | `tuple[float, float, float, float]` | `int \| tuple[float, float, float] \| tuple[float, float, float, float] \| tuple[int, int, int] \| tuple[int, int, int, int]` | The color of the markers | `src/Mod/CAM/Gui/ViewProviderPath.cpp:171` |
| `NormalColor` | `App::PropertyColor` | `tuple[float, float, float, float]` | `int \| tuple[float, float, float] \| tuple[float, float, float, float] \| tuple[int, int, int] \| tuple[int, int, int, int]` | The color of the feed rate moves | `src/Mod/CAM/Gui/ViewProviderPath.cpp:170` |
| `ShowCount` | `App::PropertyIntegerConstraint` | `int` | `int \| dict[str, int] \| tuple[int, int, int, int]` | Number of movement GCode to show, 0 means all | `src/Mod/CAM/Gui/ViewProviderPath.cpp:186` |
| `ShowNodes` | `App::PropertyBool` | `bool` | `bool \| int` | Turns the display of nodes on/off | `src/Mod/CAM/Gui/ViewProviderPath.cpp:173` |
| `StartIndex` | `App::PropertyIntegerConstraint` | `int` | `int \| dict[str, int] \| tuple[int, int, int, int]` | The index of first GCode to show | `src/Mod/CAM/Gui/ViewProviderPath.cpp:185` |
| `StartPosition` | `App::PropertyVector` | `Base.Vector` | `Base.Vector \| tuple[float, float, float]` | Tool initial position | `src/Mod/CAM/Gui/ViewProviderPath.cpp:184` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

