# `Part::MultiFuse`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/Part/App/FeaturePartFuse.cpp:69`. Abstract macro: no.

Native parent: [Part::Feature](../Part/Feature.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `Part::Feature` -> `Part.Feature`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `Part::Feature`: This implementation creates PartFeaturePy, exposed as Part.Feature. Descendant overrides, including Primitive and FeaturePython, are separate implementations. Evidence: `src/Mod/Part/App/PartFeature.cpp:130`, `src/Mod/Part/App/PartFeature.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `History` | `Part::PropertyShapeHistory` | None (source review) | object (ignored) (source review) | Shape history | `src/Mod/Part/App/FeaturePartFuse.cpp:76` |
| `Refine` | `App::PropertyBool` | `bool` | `bool \| int` | Refine shape (clean up redundant edges) after this boolean operation | `src/Mod/Part/App/FeaturePartFuse.cpp:85` |
| `Shapes` | `App::PropertyLinkList` | `list[DocumentObject \| None]` | `Sequence[DocumentObject]` | Not documented by registration | `src/Mod/Part/App/FeaturePartFuse.cpp:74` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

Conversion metadata gaps have exact-TypeId, direction-specific [source reviews](../conversion-review.md), with build conditions and unsupported operations preserved. These reviews do not change upstream generator metadata and are never inherited across a different conversion implementation.

