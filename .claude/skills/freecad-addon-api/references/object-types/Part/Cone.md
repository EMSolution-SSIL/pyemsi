# `Part::Cone`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/Part/App/PrimitiveFeature.cpp:688`. Abstract macro: no.

Native parent: [Part::Primitive](../Part/Primitive.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `Part::Feature` -> `Part.Feature`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `Part::Primitive`: Handwritten PrimitivePy derives from PartFeaturePy. No independent public Part.Primitive import is established by this review. Evidence: `src/Mod/Part/App/PrimitiveFeature.cpp:96`, `src/Mod/Part/App/PrimitiveFeature.cpp:104`, `src/Mod/Part/App/PrimitiveFeature.h`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `Angle` | `App::PropertyAngle` | `Base.Quantity` | `float \| str \| Base.Quantity` | The angle of the cone | `src/Mod/Part/App/PrimitiveFeature.cpp:695` |
| `Height` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | The height of the cone | `src/Mod/Part/App/PrimitiveFeature.cpp:694` |
| `Radius1` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | The radius of the cone | `src/Mod/Part/App/PrimitiveFeature.cpp:692` |
| `Radius2` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | The radius of the cone | `src/Mod/Part/App/PrimitiveFeature.cpp:693` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

