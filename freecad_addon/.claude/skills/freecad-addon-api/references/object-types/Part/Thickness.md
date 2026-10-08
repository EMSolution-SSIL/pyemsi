# `Part::Thickness`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/Part/App/PartFeatures.cpp:365`. Abstract macro: no.

Native parent: [Part::Feature](../Part/Feature.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `Part::Feature` -> `Part.Feature`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `Part::Feature`: This implementation creates PartFeaturePy, exposed as Part.Feature. Descendant overrides, including Primitive and FeaturePython, are separate implementations. Evidence: `src/Mod/Part/App/PartFeature.cpp:130`, `src/Mod/Part/App/PartFeature.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `Faces` | `App::PropertyLinkSub` | `tuple[DocumentObject, list[str]] \| None` | `DocumentObject \| None \| _DocumentObjectSubLinkPairInput` | Faces to be removed | `src/Mod/Part/App/PartFeatures.cpp:369` |
| `Intersection` | `App::PropertyBool` | `bool` | `bool \| int` | Intersection | `src/Mod/Part/App/PartFeatures.cpp:375` |
| `Join` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Join type | `src/Mod/Part/App/PartFeatures.cpp:373` |
| `Mode` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Mode | `src/Mod/Part/App/PartFeatures.cpp:371` |
| `SelfIntersection` | `App::PropertyBool` | `bool` | `bool \| int` | Self Intersection | `src/Mod/Part/App/PartFeatures.cpp:376` |
| `Value` | `App::PropertyQuantity` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Thickness value | `src/Mod/Part/App/PartFeatures.cpp:370` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

