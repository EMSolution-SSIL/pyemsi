# `PartDesignGui::ViewProviderDatumCoordinateSystem`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: Other native property owner; not a Document.addObject type. Registration: `src/Mod/PartDesign/Gui/ViewProviderDatumCS.cpp:45`. Abstract macro: no.

Native parent: `PartDesignGui::ViewProviderDatum` (outside this document/property-owner inventory).

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `Gui::ViewProviderGeometryObject` -> `FreeCADGui.ViewProviderGeometryObject`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `Gui::ViewProviderDocumentObject`: This implementation requires the main thread and creates ViewProviderDocumentObjectPy; the binding is FreeCADGui.ViewProviderDocumentObject. It does not prove that every derived view provider returns this exact wrapper. Evidence: `src/Gui/ViewProviderDocumentObject.cpp:606`, `src/Gui/ViewProviderDocumentObject.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `FontSize` | `App::PropertyIntegerConstraint` | `int` | `int \| dict[str, int] \| tuple[int, int, int, int]` | Not documented by registration | `src/Mod/PartDesign/Gui/ViewProviderDatumCS.cpp:64` |
| `ShowLabel` | `App::PropertyBool` | `bool` | `bool \| int` | Not documented by registration | `src/Mod/PartDesign/Gui/ViewProviderDatumCS.cpp:66` |
| `Zoom` | `App::PropertyFloatConstraint` | `float` | `float \| int \| dict[str, float] \| tuple[float, float, float, float]` | Not documented by registration | `src/Mod/PartDesign/Gui/ViewProviderDatumCS.cpp:65` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

