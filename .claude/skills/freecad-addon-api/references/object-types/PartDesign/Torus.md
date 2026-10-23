# `PartDesign::Torus`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/PartDesign/App/FeaturePrimitive.cpp:552`. Abstract macro: no.

Native parent: [PartDesign::FeaturePrimitive](../PartDesign/FeaturePrimitive.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `PartDesign::Feature` -> `PartDesign.Feature`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `Part::Feature`: This implementation creates PartFeaturePy, exposed as Part.Feature. Descendant overrides, including Primitive and FeaturePython, are separate implementations. Evidence: `src/Mod/Part/App/PartFeature.cpp:130`, `src/Mod/Part/App/PartFeature.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `Angle1` | `App::PropertyAngle` | `Base.Quantity` | `float \| str \| Base.Quantity` | The angle of the torus | `src/Mod/PartDesign/App/FeaturePrimitive.cpp:560` |
| `Angle2` | `App::PropertyAngle` | `Base.Quantity` | `float \| str \| Base.Quantity` | The angle of the torus | `src/Mod/PartDesign/App/FeaturePrimitive.cpp:562` |
| `Angle3` | `App::PropertyAngle` | `Base.Quantity` | `float \| str \| Base.Quantity` | The angle of the torus | `src/Mod/PartDesign/App/FeaturePrimitive.cpp:564` |
| `Radius1` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | Radius in local XY-plane | `src/Mod/PartDesign/App/FeaturePrimitive.cpp:556` |
| `Radius2` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | Radius in local XZ-plane | `src/Mod/PartDesign/App/FeaturePrimitive.cpp:558` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

