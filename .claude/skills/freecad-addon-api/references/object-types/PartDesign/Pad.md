# `PartDesign::Pad`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/PartDesign/App/FeaturePad.cpp:48`. Abstract macro: no.

Native parent: [PartDesign::FeatureExtrude](../PartDesign/FeatureExtrude.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `PartDesign::Feature` -> `PartDesign.Feature`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `Part::Feature`: This implementation creates PartFeaturePy, exposed as Part.Feature. Descendant overrides, including Primitive and FeaturePython, are separate implementations. Evidence: `src/Mod/Part/App/PartFeature.cpp:130`, `src/Mod/Part/App/PartFeature.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `AlongSketchNormal` | `App::PropertyBool` | `bool` | `bool \| int` | Measure pad length along the sketch normal direction | `src/Mod/PartDesign/App/FeaturePad.cpp:71` |
| `Direction` | `App::PropertyVector` | `Base.Vector` | `Base.Vector \| tuple[float, float, float]` | Pad direction vector | `src/Mod/PartDesign/App/FeaturePad.cpp:63` |
| `Length` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | Pad length | `src/Mod/PartDesign/App/FeaturePad.cpp:60` |
| `Length2` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | Pad length in 2nd direction | `src/Mod/PartDesign/App/FeaturePad.cpp:61` |
| `Offset` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | Offset from face in which pad will end | `src/Mod/PartDesign/App/FeaturePad.cpp:98` |
| `Offset2` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | Offset from face in which pad will end on side 2 | `src/Mod/PartDesign/App/FeaturePad.cpp:99` |
| `ReferenceAxis` | `App::PropertyLinkSub` | `tuple[DocumentObject, list[str]] \| None` | `DocumentObject \| None \| _DocumentObjectSubLinkPairInput` | Reference axis of direction | `src/Mod/PartDesign/App/FeaturePad.cpp:70` |
| `SideType` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Type of sides definition | `src/Mod/PartDesign/App/FeaturePad.cpp:54` |
| `StartOffset` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | Offset from the start plane | `src/Mod/PartDesign/App/FeaturePad.cpp:80` |
| `StartReference` | `App::PropertyLinkSub` | `tuple[DocumentObject, list[str]] \| None` | `DocumentObject \| None \| _DocumentObjectSubLinkPairInput` | Face, plane or sketch used as the start reference | `src/Mod/PartDesign/App/FeaturePad.cpp:81` |
| `StartType` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | How to define the start plane | `src/Mod/PartDesign/App/FeaturePad.cpp:78` |
| `TaperAngle` | `App::PropertyAngle` | `Base.Quantity` | `float \| str \| Base.Quantity` | Taper angle | `src/Mod/PartDesign/App/FeaturePad.cpp:109` |
| `TaperAngle2` | `App::PropertyAngle` | `Base.Quantity` | `float \| str \| Base.Quantity` | Taper angle for 2nd direction | `src/Mod/PartDesign/App/FeaturePad.cpp:111` |
| `Type` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Pad type for side 1 | `src/Mod/PartDesign/App/FeaturePad.cpp:55` |
| `Type2` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Pad type for side 2 | `src/Mod/PartDesign/App/FeaturePad.cpp:56` |
| `UpToFace` | `App::PropertyLinkSub` | `tuple[DocumentObject, list[str]] \| None` | `DocumentObject \| None \| _DocumentObjectSubLinkPairInput` | Face where pad will end | `src/Mod/PartDesign/App/FeaturePad.cpp:88` |
| `UpToFace2` | `App::PropertyLinkSub` | `tuple[DocumentObject, list[str]] \| None` | `DocumentObject \| None \| _DocumentObjectSubLinkPairInput` | Face where pad will end on side2 | `src/Mod/PartDesign/App/FeaturePad.cpp:90` |
| `UpToShape` | `App::PropertyLinkSubList` | `list[tuple[DocumentObject, tuple[str, ...]]]` | `_DocumentObjectSubLinkInput \| Sequence[_DocumentObjectSubLinkListItemInput]` | Faces or shape(s) where pad will end | `src/Mod/PartDesign/App/FeaturePad.cpp:89` |
| `UpToShape2` | `App::PropertyLinkSubList` | `list[tuple[DocumentObject, tuple[str, ...]]]` | `_DocumentObjectSubLinkInput \| Sequence[_DocumentObjectSubLinkListItemInput]` | Faces or shape(s) where pad will end on side2 | `src/Mod/PartDesign/App/FeaturePad.cpp:91` |
| `UseCustomVector` | `App::PropertyBool` | `bool` | `bool \| int` | Use custom vector for pad direction | `src/Mod/PartDesign/App/FeaturePad.cpp:62` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

