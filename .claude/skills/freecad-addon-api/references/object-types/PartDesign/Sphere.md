# `PartDesign::Sphere`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/PartDesign/App/FeaturePrimitive.cpp:312`. Abstract macro: no.

Native parent: [PartDesign::FeaturePrimitive](../PartDesign/FeaturePrimitive.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `PartDesign::Feature` -> `PartDesign.Feature`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `Part::Feature`: This implementation creates PartFeaturePy, exposed as Part.Feature. Descendant overrides, including Primitive and FeaturePython, are separate implementations. Evidence: `src/Mod/Part/App/PartFeature.cpp:130`, `src/Mod/Part/App/PartFeature.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `Angle1` | `App::PropertyAngle` | `Base.Quantity` | `float \| str \| Base.Quantity` | The angle of the sphere | `src/Mod/PartDesign/App/FeaturePrimitive.cpp:318` |
| `Angle2` | `App::PropertyAngle` | `Base.Quantity` | `float \| str \| Base.Quantity` | The angle of the sphere | `src/Mod/PartDesign/App/FeaturePrimitive.cpp:320` |
| `Angle3` | `App::PropertyAngle` | `Base.Quantity` | `float \| str \| Base.Quantity` | The angle of the sphere | `src/Mod/PartDesign/App/FeaturePrimitive.cpp:322` |
| `Radius` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | The radius of the sphere | `src/Mod/PartDesign/App/FeaturePrimitive.cpp:316` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

