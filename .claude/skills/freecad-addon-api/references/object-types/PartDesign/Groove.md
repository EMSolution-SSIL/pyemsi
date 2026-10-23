# `PartDesign::Groove`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/PartDesign/App/FeatureGroove.cpp:40`. Abstract macro: no.

Native parent: [PartDesign::Revolved](../PartDesign/Revolved.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `PartDesign::Feature` -> `PartDesign.Feature`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `Part::Feature`: This implementation creates PartFeaturePy, exposed as Part.Feature. Descendant overrides, including Primitive and FeaturePython, are separate implementations. Evidence: `src/Mod/Part/App/PartFeature.cpp:130`, `src/Mod/Part/App/PartFeature.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `Angle` | `App::PropertyAngle` | `Base.Quantity` | `float \| str \| Base.Quantity` | Angle | `src/Mod/PartDesign/App/FeatureGroove.cpp:75` |
| `Angle2` | `App::PropertyAngle` | `Base.Quantity` | `float \| str \| Base.Quantity` | Groove angle in 2nd direction | `src/Mod/PartDesign/App/FeatureGroove.cpp:76` |
| `Axis` | `App::PropertyVector` | `Base.Vector` | `Base.Vector \| tuple[float, float, float]` | Axis | `src/Mod/PartDesign/App/FeatureGroove.cpp:61` |
| `Base` | `App::PropertyVector` | `Base.Vector` | `Base.Vector \| tuple[float, float, float]` | Base | `src/Mod/PartDesign/App/FeatureGroove.cpp:54` |
| `ProjectAxis` | `App::PropertyBool` | `bool` | `bool \| int` | Projects the reference axis onto the profile plane | `src/Mod/PartDesign/App/FeatureGroove.cpp:68` |
| `ReferenceAxis` | `App::PropertyLinkSub` | `tuple[DocumentObject, list[str]] \| None` | `DocumentObject \| None \| _DocumentObjectSubLinkPairInput` | Reference axis of groove | `src/Mod/PartDesign/App/FeatureGroove.cpp:79` |
| `SideType` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Type of side definition | `src/Mod/PartDesign/App/FeatureGroove.cpp:48` |
| `Type` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Groove type for side 1 | `src/Mod/PartDesign/App/FeatureGroove.cpp:49` |
| `Type2` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Groove type for side 2 | `src/Mod/PartDesign/App/FeatureGroove.cpp:50` |
| `UpToFace` | `App::PropertyLinkSub` | `tuple[DocumentObject, list[str]] \| None` | `DocumentObject \| None \| _DocumentObjectSubLinkPairInput` | Face where groove will end | `src/Mod/PartDesign/App/FeatureGroove.cpp:77` |
| `UpToFace2` | `App::PropertyLinkSub` | `tuple[DocumentObject, list[str]] \| None` | `DocumentObject \| None \| _DocumentObjectSubLinkPairInput` | Face where groove will end on side 2 | `src/Mod/PartDesign/App/FeatureGroove.cpp:78` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

