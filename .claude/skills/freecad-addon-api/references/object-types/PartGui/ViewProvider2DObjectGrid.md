# `PartGui::ViewProvider2DObjectGrid`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: Other native property owner; not a Document.addObject type. Registration: `src/Mod/Part/Gui/ViewProvider2DObject.cpp:60`. Abstract macro: no.

Native parent: [PartGui::ViewProvider2DObject](../PartGui/ViewProvider2DObject.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `PartGui::ViewProviderPartExt` -> `PartGui.ViewProviderPartExt`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `Gui::ViewProviderDocumentObject`: This implementation requires the main thread and creates ViewProviderDocumentObjectPy; the binding is FreeCADGui.ViewProviderDocumentObject. It does not prove that every derived view provider returns this exact wrapper. Evidence: `src/Gui/ViewProviderDocumentObject.cpp:606`, `src/Gui/ViewProviderDocumentObject.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `GridAutoSize` | `App::PropertyBool` | `bool` | `bool \| int` | Auto-size grid based on shape boundary box | `src/Mod/Part/Gui/ViewProvider2DObject.cpp:94` |
| `GridSize` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | Gap size of the grid | `src/Mod/Part/Gui/ViewProvider2DObject.cpp:78` |
| `GridSnap` | `App::PropertyBool` | `bool` | `bool \| int` | Toggle grid snapping | `src/Mod/Part/Gui/ViewProvider2DObject.cpp:93` |
| `GridStyle` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Appearance style of the grid | `src/Mod/Part/Gui/ViewProvider2DObject.cpp:79` |
| `ShowGrid` | `App::PropertyBool` | `bool` | `bool \| int` | Toggle grid visibility | `src/Mod/Part/Gui/ViewProvider2DObject.cpp:64` |
| `ShowOnlyInEditMode` | `App::PropertyBool` | `bool` | `bool \| int` | Show only while in edit mode | `src/Mod/Part/Gui/ViewProvider2DObject.cpp:71` |
| `TightGrid` | `App::PropertyBool` | `bool` | `bool \| int` | Toggle tight grid mode | `src/Mod/Part/Gui/ViewProvider2DObject.cpp:86` |
| `maxNumberOfLines` | `App::PropertyInteger` | `int` | `int` | Maximum number of lines in grid | `src/Mod/Part/Gui/ViewProvider2DObject.cpp:101` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

