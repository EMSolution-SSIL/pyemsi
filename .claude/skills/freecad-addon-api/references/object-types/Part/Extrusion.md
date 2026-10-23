# `Part::Extrusion`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/Part/App/FeatureExtrusion.cpp:54`. Abstract macro: no.

Native parent: [Part::Feature](../Part/Feature.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `Part::Feature` -> `Part.Feature`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `Part::Feature`: This implementation creates PartFeaturePy, exposed as Part.Feature. Descendant overrides, including Primitive and FeaturePython, are separate implementations. Evidence: `src/Mod/Part/App/PartFeature.cpp:130`, `src/Mod/Part/App/PartFeature.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `Base` | `App::PropertyLink` | `DocumentObject \| None` | `DocumentObject \| None` | Shape to extrude | `src/Mod/Part/App/FeatureExtrusion.cpp:118` |
| `Dir` | `App::PropertyVector` | `Base.Vector` | `Base.Vector \| tuple[float, float, float]` | Direction of extrusion (also magnitude, if both lengths are zero). | `src/Mod/Part/App/FeatureExtrusion.cpp:120` |
| `DirLink` | `App::PropertyLinkSub` | `tuple[DocumentObject, list[str]] \| None` | `DocumentObject \| None \| _DocumentObjectSubLinkPairInput` | Link to edge defining extrusion direction. | `src/Mod/Part/App/FeatureExtrusion.cpp:125` |
| `DirMode` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Sets, how Dir is updated. | `src/Mod/Part/App/FeatureExtrusion.cpp:122` |
| `FaceMakerClass` | `App::PropertyString` | `str` | `str` | If Solid is true, this sets the facemaker class to use when converting wires to faces. Otherwise, ignored. | `src/Mod/Part/App/FeatureExtrusion.cpp:142` |
| `FaceMakerMode` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | If Solid is true, this sets the facemaker class to use when converting wires to faces. Otherwise, ignored. | `src/Mod/Part/App/FeatureExtrusion.cpp:144` |
| `InnerWireTaper` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Controls taper direction for inner wires (holes). | `src/Mod/Part/App/FeatureExtrusion.cpp:147` |
| `LengthFwd` | `App::PropertyDistance` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Length of extrusion along direction. If both LengthFwd and LengthRev are zero, magnitude of Dir is used. | `src/Mod/Part/App/FeatureExtrusion.cpp:127` |
| `LengthRev` | `App::PropertyDistance` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Length of additional extrusion, against direction. | `src/Mod/Part/App/FeatureExtrusion.cpp:129` |
| `Reversed` | `App::PropertyBool` | `bool` | `bool \| int` | Set to true to swap the direction of extrusion. | `src/Mod/Part/App/FeatureExtrusion.cpp:133` |
| `Solid` | `App::PropertyBool` | `bool` | `bool \| int` | If true, extruding a wire yields a solid. If false, a shell. | `src/Mod/Part/App/FeatureExtrusion.cpp:131` |
| `Symmetric` | `App::PropertyBool` | `bool` | `bool \| int` | If true, extrusion is done in both directions to a total of LengthFwd. LengthRev is ignored. | `src/Mod/Part/App/FeatureExtrusion.cpp:135` |
| `TaperAngle` | `App::PropertyAngle` | `Base.Quantity` | `float \| str \| Base.Quantity` | Sets the angle of slope (draft) to apply to the sides. The angle is for outward taper; negative value yields inward tapering. | `src/Mod/Part/App/FeatureExtrusion.cpp:137` |
| `TaperAngleRev` | `App::PropertyAngle` | `Base.Quantity` | `float \| str \| Base.Quantity` | Taper angle of reverse part of extrusion. | `src/Mod/Part/App/FeatureExtrusion.cpp:139` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

