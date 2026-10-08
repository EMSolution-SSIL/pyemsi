# `PartDesign::Pocket`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/PartDesign/App/FeaturePocket.cpp:49`. Abstract macro: no.

Native parent: [PartDesign::FeatureExtrude](../PartDesign/FeatureExtrude.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `PartDesign::Feature` -> `PartDesign.Feature`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `Part::Feature`: This implementation creates PartFeaturePy, exposed as Part.Feature. Descendant overrides, including Primitive and FeaturePython, are separate implementations. Evidence: `src/Mod/Part/App/PartFeature.cpp:130`, `src/Mod/Part/App/PartFeature.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `AlongSketchNormal` | `App::PropertyBool` | `bool` | `bool \| int` | Measure pocket length along the sketch normal direction | `src/Mod/PartDesign/App/FeaturePocket.cpp:78` |
| `Direction` | `App::PropertyVector` | `Base.Vector` | `Base.Vector \| tuple[float, float, float]` | Pocket direction vector | `src/Mod/PartDesign/App/FeaturePocket.cpp:70` |
| `Length` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | Pocket length | `src/Mod/PartDesign/App/FeaturePocket.cpp:61` |
| `Length2` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | Pocket length in 2nd direction | `src/Mod/PartDesign/App/FeaturePocket.cpp:62` |
| `Offset` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | Offset from face in which pocket will end | `src/Mod/PartDesign/App/FeaturePocket.cpp:111` |
| `Offset2` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | Offset from face in which pocket will end on side 2 | `src/Mod/PartDesign/App/FeaturePocket.cpp:112` |
| `ReferenceAxis` | `App::PropertyLinkSub` | `tuple[DocumentObject, list[str]] \| None` | `DocumentObject \| None \| _DocumentObjectSubLinkPairInput` | Reference axis of direction | `src/Mod/PartDesign/App/FeaturePocket.cpp:77` |
| `SideType` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Type of sides definition | `src/Mod/PartDesign/App/FeaturePocket.cpp:55` |
| `StartOffset` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | Offset from the start plane | `src/Mod/PartDesign/App/FeaturePocket.cpp:87` |
| `StartReference` | `App::PropertyLinkSub` | `tuple[DocumentObject, list[str]] \| None` | `DocumentObject \| None \| _DocumentObjectSubLinkPairInput` | Face, plane or sketch used as the start reference | `src/Mod/PartDesign/App/FeaturePocket.cpp:88` |
| `StartType` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | How to define the start plane | `src/Mod/PartDesign/App/FeaturePocket.cpp:85` |
| `TaperAngle` | `App::PropertyAngle` | `Base.Quantity` | `float \| str \| Base.Quantity` | Taper angle | `src/Mod/PartDesign/App/FeaturePocket.cpp:122` |
| `TaperAngle2` | `App::PropertyAngle` | `Base.Quantity` | `float \| str \| Base.Quantity` | Taper angle for 2nd direction | `src/Mod/PartDesign/App/FeaturePocket.cpp:124` |
| `Type` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Pocket type | `src/Mod/PartDesign/App/FeaturePocket.cpp:56` |
| `Type2` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Pocket type | `src/Mod/PartDesign/App/FeaturePocket.cpp:57` |
| `UpToFace` | `App::PropertyLinkSub` | `tuple[DocumentObject, list[str]] \| None` | `DocumentObject \| None \| _DocumentObjectSubLinkPairInput` | Face where pocket will end | `src/Mod/PartDesign/App/FeaturePocket.cpp:95` |
| `UpToFace2` | `App::PropertyLinkSub` | `tuple[DocumentObject, list[str]] \| None` | `DocumentObject \| None \| _DocumentObjectSubLinkPairInput` | Face where pocket will end | `src/Mod/PartDesign/App/FeaturePocket.cpp:103` |
| `UpToShape` | `App::PropertyLinkSubList` | `list[tuple[DocumentObject, tuple[str, ...]]]` | `_DocumentObjectSubLinkInput \| Sequence[_DocumentObjectSubLinkListItemInput]` | Face(s) or shape(s) where pocket will end | `src/Mod/PartDesign/App/FeaturePocket.cpp:96` |
| `UpToShape2` | `App::PropertyLinkSubList` | `list[tuple[DocumentObject, tuple[str, ...]]]` | `_DocumentObjectSubLinkInput \| Sequence[_DocumentObjectSubLinkListItemInput]` | Face(s) or shape(s) where pocket will end | `src/Mod/PartDesign/App/FeaturePocket.cpp:104` |
| `UseCustomVector` | `App::PropertyBool` | `bool` | `bool \| int` | Use custom vector for pocket direction | `src/Mod/PartDesign/App/FeaturePocket.cpp:63` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

