# `Part::Loft`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/Part/App/PartFeatures.cpp:177`. Abstract macro: no.

Native parent: [Part::Feature](../Part/Feature.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `Part::Feature` -> `Part.Feature`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `Part::Feature`: This implementation creates PartFeaturePy, exposed as Part.Feature. Descendant overrides, including Primitive and FeaturePython, are separate implementations. Evidence: `src/Mod/Part/App/PartFeature.cpp:130`, `src/Mod/Part/App/PartFeature.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `Closed` | `App::PropertyBool` | `bool` | `bool \| int` | Close Last to First Profile | `src/Mod/Part/App/PartFeatures.cpp:185` |
| `Linearize` | `App::PropertyBool` | `bool` | `bool \| int` | Linearize the result shape by simplifying linear edge and planar face into line and plane | `src/Mod/Part/App/PartFeatures.cpp:187` |
| `MaxDegree` | `App::PropertyIntegerConstraint` | `int` | `int \| dict[str, int] \| tuple[int, int, int, int]` | Maximum Degree | `src/Mod/Part/App/PartFeatures.cpp:186` |
| `Ruled` | `App::PropertyBool` | `bool` | `bool \| int` | Ruled surface | `src/Mod/Part/App/PartFeatures.cpp:184` |
| `Sections` | `App::PropertyLinkList` | `list[DocumentObject \| None]` | `Sequence[DocumentObject]` | List of sections | `src/Mod/Part/App/PartFeatures.cpp:181` |
| `Solid` | `App::PropertyBool` | `bool` | `bool \| int` | Create solid | `src/Mod/Part/App/PartFeatures.cpp:183` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

