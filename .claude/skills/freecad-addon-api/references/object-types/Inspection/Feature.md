# `Inspection::Feature`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/Inspection/App/InspectionFeature.cpp:764`. Abstract macro: no.

Native parent: [App::DocumentObject](../App/DocumentObject.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `App::DocumentObject` -> `FreeCAD.DocumentObject`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `App::DocumentObject`: This implementation creates DocumentObjectPy. Its binding is FreeCAD.DocumentObject; descendant overrides must be checked before claiming the same returned Python type. Evidence: `src/App/DocumentObject.cpp:1239`, `src/App/DocumentObject.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `Actual` | `App::PropertyLink` | `DocumentObject \| None` | `DocumentObject \| None` | Not documented by registration | `src/Mod/Inspection/App/InspectionFeature.cpp:770` |
| `Distances` | `Inspection::PropertyDistanceList` | list[float] (source review) | float \| list[float] (source review) | Not documented by registration | `src/Mod/Inspection/App/InspectionFeature.cpp:772` |
| `Nominals` | `App::PropertyLinkList` | `list[DocumentObject \| None]` | `Sequence[DocumentObject]` | Not documented by registration | `src/Mod/Inspection/App/InspectionFeature.cpp:771` |
| `SearchRadius` | `App::PropertyFloat` | `float` | `float` | Not documented by registration | `src/Mod/Inspection/App/InspectionFeature.cpp:768` |
| `Thickness` | `App::PropertyFloat` | `float` | `float` | Not documented by registration | `src/Mod/Inspection/App/InspectionFeature.cpp:769` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

Conversion metadata gaps have exact-TypeId, direction-specific [source reviews](../conversion-review.md), with build conditions and unsupported operations preserved. These reviews do not change upstream generator metadata and are never inherited across a different conversion implementation.

