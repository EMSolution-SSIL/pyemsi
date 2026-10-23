# `PartDesign::Chamfer`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/PartDesign/App/FeatureChamfer.cpp:53`. Abstract macro: no.

Native parent: [PartDesign::DressUp](../PartDesign/DressUp.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `PartDesign::Feature` -> `PartDesign.Feature`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `Part::Feature`: This implementation creates PartFeaturePy, exposed as Part.Feature. Descendant overrides, including Primitive and FeaturePython, are separate implementations. Evidence: `src/Mod/Part/App/PartFeature.cpp:130`, `src/Mod/Part/App/PartFeature.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `Angle` | `App::PropertyAngle` | `Base.Quantity` | `float \| str \| Base.Quantity` | Angle of chamfer | `src/Mod/PartDesign/App/FeatureChamfer.cpp:80` |
| `ChamferType` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Type of chamfer | `src/Mod/PartDesign/App/FeatureChamfer.cpp:69` |
| `FlipDirection` | `App::PropertyBool` | `bool` | `bool \| int` | Flip direction | `src/Mod/PartDesign/App/FeatureChamfer.cpp:84` |
| `Size` | `App::PropertyQuantityConstraint` | `Base.Quantity` | `float \| str \| Base.Quantity` | Size of chamfer | `src/Mod/PartDesign/App/FeatureChamfer.cpp:72` |
| `Size2` | `App::PropertyQuantityConstraint` | `Base.Quantity` | `float \| str \| Base.Quantity` | Second size of chamfer | `src/Mod/PartDesign/App/FeatureChamfer.cpp:76` |
| `UseAllEdges` | `App::PropertyBool` | `bool` | `bool \| int` | Not documented by registration | `src/Mod/PartDesign/App/FeatureChamfer.cpp:85` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

