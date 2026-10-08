# `Part::Wedge`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/Part/App/PrimitiveFeature.cpp:1020`. Abstract macro: no.

Native parent: [Part::Primitive](../Part/Primitive.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `Part::Feature` -> `Part.Feature`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `Part::Primitive`: Handwritten PrimitivePy derives from PartFeaturePy. No independent public Part.Primitive import is established by this review. Evidence: `src/Mod/Part/App/PrimitiveFeature.cpp:96`, `src/Mod/Part/App/PrimitiveFeature.cpp:104`, `src/Mod/Part/App/PrimitiveFeature.h`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `X2max` | `App::PropertyDistance` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | X2max of the wedge | `src/Mod/Part/App/PrimitiveFeature.cpp:1032` |
| `X2min` | `App::PropertyDistance` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | X2min of the wedge | `src/Mod/Part/App/PrimitiveFeature.cpp:1027` |
| `Xmax` | `App::PropertyDistance` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Xmax of the wedge | `src/Mod/Part/App/PrimitiveFeature.cpp:1029` |
| `Xmin` | `App::PropertyDistance` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Xmin of the wedge | `src/Mod/Part/App/PrimitiveFeature.cpp:1024` |
| `Ymax` | `App::PropertyDistance` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Ymax of the wedge | `src/Mod/Part/App/PrimitiveFeature.cpp:1030` |
| `Ymin` | `App::PropertyDistance` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Ymin of the wedge | `src/Mod/Part/App/PrimitiveFeature.cpp:1025` |
| `Z2max` | `App::PropertyDistance` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Z2max of the wedge | `src/Mod/Part/App/PrimitiveFeature.cpp:1033` |
| `Z2min` | `App::PropertyDistance` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Z2min of the wedge | `src/Mod/Part/App/PrimitiveFeature.cpp:1028` |
| `Zmax` | `App::PropertyDistance` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Zmax of the wedge | `src/Mod/Part/App/PrimitiveFeature.cpp:1031` |
| `Zmin` | `App::PropertyDistance` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Zmin of the wedge | `src/Mod/Part/App/PrimitiveFeature.cpp:1026` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

