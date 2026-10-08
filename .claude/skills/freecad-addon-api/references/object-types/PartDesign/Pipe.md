# `PartDesign::Pipe`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/PartDesign/App/FeaturePipe.cpp:67`. Abstract macro: no.

Native parent: [PartDesign::ProfileBased](../PartDesign/ProfileBased.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `PartDesign::Feature` -> `PartDesign.Feature`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `Part::Feature`: This implementation creates PartFeaturePy, exposed as Part.Feature. Descendant overrides, including Primitive and FeaturePython, are separate implementations. Evidence: `src/Mod/Part/App/PartFeature.cpp:130`, `src/Mod/Part/App/PartFeature.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `AuxiliaryCurvilinear` | `App::PropertyBool` | `bool` | `bool \| int` | Calculate normal between equidistant points on both spines | `src/Mod/PartDesign/App/FeaturePipe.cpp:83` |
| `AuxiliarySpine` | `App::PropertyLinkSub` | `tuple[DocumentObject, list[str]] \| None` | `DocumentObject \| None \| _DocumentObjectSubLinkPairInput` | Secondary path to orient sweep | `src/Mod/PartDesign/App/FeaturePipe.cpp:75` |
| `AuxiliarySpineTangent` | `App::PropertyBool` | `bool` | `bool \| int` | Include tangent edges into secondary path | `src/Mod/PartDesign/App/FeaturePipe.cpp:76` |
| `Binormal` | `App::PropertyVector` | `Base.Vector` | `Base.Vector \| tuple[float, float, float]` | Binormal vector for corresponding orientation mode | `src/Mod/PartDesign/App/FeaturePipe.cpp:91` |
| `Mode` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Profile mode | `src/Mod/PartDesign/App/FeaturePipe.cpp:90` |
| `Sections` | `App::PropertyLinkSubList` | `list[tuple[DocumentObject, tuple[str, ...]]]` | `_DocumentObjectSubLinkInput \| Sequence[_DocumentObjectSubLinkListItemInput]` | List of sections | `src/Mod/PartDesign/App/FeaturePipe.cpp:71` |
| `Spine` | `App::PropertyLinkSub` | `tuple[DocumentObject, list[str]] \| None` | `DocumentObject \| None \| _DocumentObjectSubLinkPairInput` | Path to sweep along | `src/Mod/PartDesign/App/FeaturePipe.cpp:73` |
| `SpineTangent` | `App::PropertyBool` | `bool` | `bool \| int` | Include tangent edges into path | `src/Mod/PartDesign/App/FeaturePipe.cpp:74` |
| `Transformation` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Section transformation mode | `src/Mod/PartDesign/App/FeaturePipe.cpp:99` |
| `Transition` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Transition mode | `src/Mod/PartDesign/App/FeaturePipe.cpp:98` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

