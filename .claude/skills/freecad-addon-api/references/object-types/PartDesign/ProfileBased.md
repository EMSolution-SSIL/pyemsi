# `PartDesign::ProfileBased`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/PartDesign/App/FeatureSketchBased.cpp:89`. Abstract macro: no.

Native parent: [PartDesign::FeatureAddSub](../PartDesign/FeatureAddSub.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `PartDesign::Feature` -> `PartDesign.Feature`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `Part::Feature`: This implementation creates PartFeaturePy, exposed as Part.Feature. Descendant overrides, including Primitive and FeaturePython, are separate implementations. Evidence: `src/Mod/Part/App/PartFeature.cpp:130`, `src/Mod/Part/App/PartFeature.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `AllowMultiFace` | `App::PropertyBool` | `bool` | `bool \| int` | Allow multiple faces in profile | `src/Mod/PartDesign/App/FeatureSketchBased.cpp:126` |
| `Midplane` | `App::PropertyBool` | `bool` | `bool \| int` | Extrude symmetric to sketch face | `src/Mod/PartDesign/App/FeatureSketchBased.cpp:96` |
| `Profile` | `App::PropertyLinkSub` | `tuple[DocumentObject, list[str]] \| None` | `DocumentObject \| None \| _DocumentObjectSubLinkPairInput` | Reference to sketch | `src/Mod/PartDesign/App/FeatureSketchBased.cpp:95` |
| `Reversed` | `App::PropertyBool` | `bool` | `bool \| int` | Reverse extrusion direction | `src/Mod/PartDesign/App/FeatureSketchBased.cpp:97` |
| `UpToFace` | `App::PropertyLinkSub` | `tuple[DocumentObject, list[str]] \| None` | `DocumentObject \| None \| _DocumentObjectSubLinkPairInput` | Face where feature will end | `src/Mod/PartDesign/App/FeatureSketchBased.cpp:98` |
| `UpToFace2` | `App::PropertyLinkSub` | `tuple[DocumentObject, list[str]] \| None` | `DocumentObject \| None \| _DocumentObjectSubLinkPairInput` | Face where feature will end | `src/Mod/PartDesign/App/FeatureSketchBased.cpp:112` |
| `UpToShape` | `App::PropertyLinkSubList` | `list[tuple[DocumentObject, tuple[str, ...]]]` | `_DocumentObjectSubLinkInput \| Sequence[_DocumentObjectSubLinkListItemInput]` | Shape where feature will end | `src/Mod/PartDesign/App/FeatureSketchBased.cpp:105` |
| `UpToShape2` | `App::PropertyLinkSubList` | `list[tuple[DocumentObject, tuple[str, ...]]]` | `_DocumentObjectSubLinkInput \| Sequence[_DocumentObjectSubLinkListItemInput]` | Shape where feature will end | `src/Mod/PartDesign/App/FeatureSketchBased.cpp:119` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

