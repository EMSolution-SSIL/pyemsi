# `PartDesign::Hole`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/PartDesign/App/FeatureHole.cpp:538`. Abstract macro: no.

Native parent: [PartDesign::ProfileBased](../PartDesign/ProfileBased.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `PartDesign::Feature` -> `PartDesign.Feature`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `Part::Feature`: This implementation creates PartFeaturePy, exposed as Part.Feature. Descendant overrides, including Primitive and FeaturePython, are separate implementations. Evidence: `src/Mod/Part/App/PartFeature.cpp:130`, `src/Mod/Part/App/PartFeature.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `BaseProfileType` | `App::PropertyInteger` | `int` | `int` | Which profile feature to base the holes on | `src/Mod/PartDesign/App/FeatureHole.cpp:651` |
| `CosmeticThread` | `App::PropertyBool` | `bool` | `bool \| int` | Texture the thread | `src/Mod/PartDesign/App/FeatureHole.cpp:563` |
| `CustomThreadClearance` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | Custom thread clearance (overrides ThreadClass) | `src/Mod/PartDesign/App/FeatureHole.cpp:640` |
| `Depth` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | Length | `src/Mod/PartDesign/App/FeatureHole.cpp:606` |
| `DepthType` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Type | `src/Mod/PartDesign/App/FeatureHole.cpp:603` |
| `Diameter` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | Diameter | `src/Mod/PartDesign/App/FeatureHole.cpp:577` |
| `DrillForDepth` | `App::PropertyBool` | `bool` | `bool \| int` | The size of the drill point will be taken into  account for the depth of blind holes | `src/Mod/PartDesign/App/FeatureHole.cpp:613` |
| `DrillPoint` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Drill point type | `src/Mod/PartDesign/App/FeatureHole.cpp:608` |
| `DrillPointAngle` | `App::PropertyAngle` | `Base.Quantity` | `float \| str \| Base.Quantity` | Drill point angle | `src/Mod/PartDesign/App/FeatureHole.cpp:611` |
| `HoleCutCountersinkAngle` | `App::PropertyAngle` | `Base.Quantity` | `float \| str \| Base.Quantity` | Head cut countersink angle | `src/Mod/PartDesign/App/FeatureHole.cpp:599` |
| `HoleCutCustomValues` | `App::PropertyBool` | `bool` | `bool \| int` | Custom cut values | `src/Mod/PartDesign/App/FeatureHole.cpp:590` |
| `HoleCutDepth` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | Head cut depth | `src/Mod/PartDesign/App/FeatureHole.cpp:596` |
| `HoleCutDiameter` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | Head cut diameter | `src/Mod/PartDesign/App/FeatureHole.cpp:593` |
| `HoleCutType` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Head cut type | `src/Mod/PartDesign/App/FeatureHole.cpp:587` |
| `ModelThread` | `App::PropertyBool` | `bool` | `bool \| int` | Model actual thread | `src/Mod/PartDesign/App/FeatureHole.cpp:561` |
| `StartOffset` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | Offset from the start plane | `src/Mod/PartDesign/App/FeatureHole.cpp:660` |
| `StartReference` | `App::PropertyLinkSub` | `tuple[DocumentObject, list[str]] \| None` | `DocumentObject \| None \| _DocumentObjectSubLinkPairInput` | Face, plane or sketch used as the start reference | `src/Mod/PartDesign/App/FeatureHole.cpp:661` |
| `StartType` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | How to define the start plane | `src/Mod/PartDesign/App/FeatureHole.cpp:658` |
| `Tapered` | `App::PropertyBool` | `bool` | `bool \| int` | Tapered | `src/Mod/PartDesign/App/FeatureHole.cpp:621` |
| `TaperedAngle` | `App::PropertyAngle` | `Base.Quantity` | `float \| str \| Base.Quantity` | Tapered angle | `src/Mod/PartDesign/App/FeatureHole.cpp:623` |
| `ThreadClass` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Thread class | `src/Mod/PartDesign/App/FeatureHole.cpp:571` |
| `ThreadDepth` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | Thread Length | `src/Mod/PartDesign/App/FeatureHole.cpp:629` |
| `ThreadDepthType` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Thread depth type | `src/Mod/PartDesign/App/FeatureHole.cpp:626` |
| `ThreadDiameter` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | Thread major diameter | `src/Mod/PartDesign/App/FeatureHole.cpp:580` |
| `ThreadDirection` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Thread direction | `src/Mod/PartDesign/App/FeatureHole.cpp:583` |
| `ThreadFit` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Clearance hole fit | `src/Mod/PartDesign/App/FeatureHole.cpp:574` |
| `ThreadSize` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Thread size | `src/Mod/PartDesign/App/FeatureHole.cpp:568` |
| `ThreadType` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Thread type | `src/Mod/PartDesign/App/FeatureHole.cpp:565` |
| `Threaded` | `App::PropertyBool` | `bool` | `bool \| int` | Threaded | `src/Mod/PartDesign/App/FeatureHole.cpp:559` |
| `UseCustomThreadClearance` | `App::PropertyBool` | `bool` | `bool \| int` | Use custom thread clearance | `src/Mod/PartDesign/App/FeatureHole.cpp:632` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

