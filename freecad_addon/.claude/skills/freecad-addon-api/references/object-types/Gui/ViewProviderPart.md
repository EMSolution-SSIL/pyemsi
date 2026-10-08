# `Gui::ViewProviderPart`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: Other native property owner; not a Document.addObject type. Registration: `src/Gui/ViewProviderPart.cpp:47`. Abstract macro: no.

Native parent: [Gui::ViewProviderGeometryObject](../Gui/ViewProviderGeometryObject.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `Gui::ViewProviderGeometryObject` -> `FreeCADGui.ViewProviderGeometryObject`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `Gui::ViewProviderDocumentObject`: This implementation requires the main thread and creates ViewProviderDocumentObjectPy; the binding is FreeCADGui.ViewProviderDocumentObject. It does not prove that every derived view provider returns this exact wrapper. Evidence: `src/Gui/ViewProviderDocumentObject.cpp:606`, `src/Gui/ViewProviderDocumentObject.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `OverrideColorList` | `App::PropertyColorList` | list[tuple[float, float, float, float]] (source review) | _ColorInput \| Iterable[_ColorInput] \| dict[int, _ColorInput] (source review) | Not documented by registration | `src/Gui/ViewProviderPart.cpp:59` |
| `OverrideMaterial` | `App::PropertyBool` | `bool` | `bool \| int` | Override part material | `src/Gui/ViewProviderPart.cpp:57` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

Conversion metadata gaps have exact-TypeId, direction-specific [source reviews](../conversion-review.md), with build conditions and unsupported operations preserved. These reviews do not change upstream generator metadata and are never inherited across a different conversion implementation.

