# `PartDesign::Helix`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/PartDesign/App/FeatureHelix.cpp:64`. Abstract macro: no.

Native parent: [PartDesign::ProfileBased](../PartDesign/ProfileBased.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `PartDesign::Feature` -> `PartDesign.Feature`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `Part::Feature`: This implementation creates PartFeaturePy, exposed as Part.Feature. Descendant overrides, including Primitive and FeaturePython, are separate implementations. Evidence: `src/Mod/Part/App/PartFeature.cpp:130`, `src/Mod/Part/App/PartFeature.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `Angle` | `App::PropertyAngle` | `Base.Quantity` | `float \| str \| Base.Quantity` | Not documented by registration | `src/Mod/PartDesign/App/FeatureHelix.cpp:140` |
| `Axis` | `App::PropertyVector` | `Base.Vector` | `Base.Vector \| tuple[float, float, float]` | Not documented by registration | `src/Mod/PartDesign/App/FeatureHelix.cpp:89` |
| `Base` | `App::PropertyVector` | `Base.Vector` | `Base.Vector \| tuple[float, float, float]` | Not documented by registration | `src/Mod/PartDesign/App/FeatureHelix.cpp:79` |
| `Growth` | `App::PropertyDistance` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Not documented by registration | `src/Mod/PartDesign/App/FeatureHelix.cpp:153` |
| `HasBeenEdited` | `App::PropertyBool` | `bool` | `bool \| int` | Not documented by registration | `src/Mod/PartDesign/App/FeatureHelix.cpp:185` |
| `Height` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | Not documented by registration | `src/Mod/PartDesign/App/FeatureHelix.cpp:122` |
| `LeftHanded` | `App::PropertyBool` | `bool` | `bool \| int` | Not documented by registration | `src/Mod/PartDesign/App/FeatureHelix.cpp:164` |
| `Mode` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Not documented by registration | `src/Mod/PartDesign/App/FeatureHelix.cpp:103` |
| `Outside` | `App::PropertyBool` | `bool` | `bool \| int` | Not documented by registration | `src/Mod/PartDesign/App/FeatureHelix.cpp:205` |
| `Pitch` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | Not documented by registration | `src/Mod/PartDesign/App/FeatureHelix.cpp:115` |
| `ReferenceAxis` | `App::PropertyLinkSub` | `tuple[DocumentObject, list[str]] \| None` | `DocumentObject \| None \| _DocumentObjectSubLinkPairInput` | Not documented by registration | `src/Mod/PartDesign/App/FeatureHelix.cpp:96` |
| `Reversed` | `App::PropertyBool` | `bool` | `bool \| int` | Not documented by registration | `src/Mod/PartDesign/App/FeatureHelix.cpp:175` |
| `Tolerance` | `App::PropertyFloatConstraint` | `float` | `float \| int \| dict[str, float] \| tuple[float, float, float, float]` | Not documented by registration | `src/Mod/PartDesign/App/FeatureHelix.cpp:197` |
| `Turns` | `App::PropertyFloatConstraint` | `float` | `float \| int \| dict[str, float] \| tuple[float, float, float, float]` | Not documented by registration | `src/Mod/PartDesign/App/FeatureHelix.cpp:132` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

