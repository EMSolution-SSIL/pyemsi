# `Part::Sweep`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/Part/App/PartFeatures.cpp:258`. Abstract macro: no.

Native parent: [Part::Feature](../Part/Feature.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `Part::Feature` -> `Part.Feature`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `Part::Feature`: This implementation creates PartFeaturePy, exposed as Part.Feature. Descendant overrides, including Primitive and FeaturePython, are separate implementations. Evidence: `src/Mod/Part/App/PartFeature.cpp:130`, `src/Mod/Part/App/PartFeature.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `Frenet` | `App::PropertyBool` | `bool` | `bool \| int` | Frenet | `src/Mod/Part/App/PartFeatures.cpp:266` |
| `Linearize` | `App::PropertyBool` | `bool` | `bool \| int` | Linearize the result shape by simplifying linear edge and planar face into line and plane | `src/Mod/Part/App/PartFeatures.cpp:268` |
| `Sections` | `App::PropertyLinkList` | `list[DocumentObject \| None]` | `Sequence[DocumentObject]` | List of sections | `src/Mod/Part/App/PartFeatures.cpp:262` |
| `Solid` | `App::PropertyBool` | `bool` | `bool \| int` | Create solid | `src/Mod/Part/App/PartFeatures.cpp:265` |
| `Spine` | `App::PropertyLinkSub` | `tuple[DocumentObject, list[str]] \| None` | `DocumentObject \| None \| _DocumentObjectSubLinkPairInput` | Path to sweep along | `src/Mod/Part/App/PartFeatures.cpp:264` |
| `Transition` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Transition mode | `src/Mod/Part/App/PartFeatures.cpp:267` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

