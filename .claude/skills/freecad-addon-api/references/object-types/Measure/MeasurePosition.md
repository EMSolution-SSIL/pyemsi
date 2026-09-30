# `Measure::MeasurePosition`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/Measure/App/MeasurePosition.cpp:36`. Abstract macro: no.

Native parent: [Measure::MeasureBase](../Measure/MeasureBase.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `Measure::MeasureBase` -> `Measure.MeasureBase`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `App::DocumentObject`: This implementation creates DocumentObjectPy. Its binding is FreeCAD.DocumentObject; descendant overrides must be checked before claiming the same returned Python type. Evidence: `src/App/DocumentObject.cpp:1239`, `src/App/DocumentObject.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `Element` | `App::PropertyLinkSub` | `tuple[DocumentObject, list[str]] \| None` | `DocumentObject \| None \| _DocumentObjectSubLinkPairInput` | Element to get the position from | `src/Mod/Measure/App/MeasurePosition.cpp:41` |
| `Position` | `App::PropertyPosition` | `Base.Vector` | `Base.Vector \| tuple[float, float, float]` | The absolute position | `src/Mod/Measure/App/MeasurePosition.cpp:46` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

