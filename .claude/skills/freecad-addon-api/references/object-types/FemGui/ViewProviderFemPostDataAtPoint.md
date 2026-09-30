# `FemGui::ViewProviderFemPostDataAtPoint`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: Other native property owner; not a Document.addObject type. Registration: `src/Mod/Fem/Gui/ViewProviderFemPostFilter.cpp:105`. Abstract macro: no.

Native parent: [FemGui::ViewProviderFemPostObject](../FemGui/ViewProviderFemPostObject.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `FemGui::ViewProviderFemPostObject` -> `FemGui.ViewProviderFemPostFilter`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `Gui::ViewProviderDocumentObject`: This implementation requires the main thread and creates ViewProviderDocumentObjectPy; the binding is FreeCADGui.ViewProviderDocumentObject. It does not prove that every derived view provider returns this exact wrapper. Evidence: `src/Gui/ViewProviderDocumentObject.cpp:606`, `src/Gui/ViewProviderDocumentObject.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `PointSize` | `App::PropertyFloatConstraint` | `float` | `float \| int \| dict[str, float] \| tuple[float, float, float, float]` | Set point size | `src/Mod/Fem/Gui/ViewProviderFemPostFilter.cpp:112` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

