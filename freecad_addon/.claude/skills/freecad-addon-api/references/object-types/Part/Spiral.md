# `Part::Spiral`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/Part/App/PrimitiveFeature.cpp:943`. Abstract macro: no.

Native parent: [Part::Primitive](../Part/Primitive.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `Part::Feature` -> `Part.Feature`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `Part::Primitive`: Handwritten PrimitivePy derives from PartFeaturePy. No independent public Part.Primitive import is established by this review. Evidence: `src/Mod/Part/App/PrimitiveFeature.cpp:96`, `src/Mod/Part/App/PrimitiveFeature.cpp:104`, `src/Mod/Part/App/PrimitiveFeature.h`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `Growth` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | The growth of the spiral per rotation | `src/Mod/Part/App/PrimitiveFeature.cpp:947` |
| `Length` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | The length of the spiral | `src/Mod/Part/App/PrimitiveFeature.cpp:961` |
| `Radius` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | The radius of the spiral | `src/Mod/Part/App/PrimitiveFeature.cpp:949` |
| `Rotations` | `App::PropertyQuantityConstraint` | `Base.Quantity` | `float \| str \| Base.Quantity` | The number of rotations | `src/Mod/Part/App/PrimitiveFeature.cpp:951` |
| `SegmentLength` | `App::PropertyQuantityConstraint` | `Base.Quantity` | `float \| str \| Base.Quantity` | The number of turns per spiral subdivision | `src/Mod/Part/App/PrimitiveFeature.cpp:953` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

