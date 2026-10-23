# `PartDesign::Wedge`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/PartDesign/App/FeaturePrimitive.cpp:722`. Abstract macro: no.

Native parent: [PartDesign::FeaturePrimitive](../PartDesign/FeaturePrimitive.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `PartDesign::Feature` -> `PartDesign.Feature`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `Part::Feature`: This implementation creates PartFeaturePy, exposed as Part.Feature. Descendant overrides, including Primitive and FeaturePython, are separate implementations. Evidence: `src/Mod/Part/App/PartFeature.cpp:130`, `src/Mod/Part/App/PartFeature.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `X2max` | `App::PropertyDistance` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | X2max of the wedge | `src/Mod/PartDesign/App/FeaturePrimitive.cpp:734` |
| `X2min` | `App::PropertyDistance` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | X2min of the wedge | `src/Mod/PartDesign/App/FeaturePrimitive.cpp:729` |
| `Xmax` | `App::PropertyDistance` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Xmax of the wedge | `src/Mod/PartDesign/App/FeaturePrimitive.cpp:731` |
| `Xmin` | `App::PropertyDistance` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Xmin of the wedge | `src/Mod/PartDesign/App/FeaturePrimitive.cpp:726` |
| `Ymax` | `App::PropertyDistance` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Ymax of the wedge | `src/Mod/PartDesign/App/FeaturePrimitive.cpp:732` |
| `Ymin` | `App::PropertyDistance` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Ymin of the wedge | `src/Mod/PartDesign/App/FeaturePrimitive.cpp:727` |
| `Z2max` | `App::PropertyDistance` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Z2max of the wedge | `src/Mod/PartDesign/App/FeaturePrimitive.cpp:735` |
| `Z2min` | `App::PropertyDistance` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Z2min of the wedge | `src/Mod/PartDesign/App/FeaturePrimitive.cpp:730` |
| `Zmax` | `App::PropertyDistance` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Zmax of the wedge | `src/Mod/PartDesign/App/FeaturePrimitive.cpp:733` |
| `Zmin` | `App::PropertyDistance` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Zmin of the wedge | `src/Mod/PartDesign/App/FeaturePrimitive.cpp:728` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

