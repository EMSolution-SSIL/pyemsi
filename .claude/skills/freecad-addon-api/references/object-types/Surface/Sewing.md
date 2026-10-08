# `Surface::Sewing`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/Surface/App/FeatureSewing.cpp:35`. Abstract macro: no.

Native parent: [Part::Feature](../Part/Feature.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `Part::Feature` -> `Part.Feature`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `Part::Feature`: This implementation creates PartFeaturePy, exposed as Part.Feature. Descendant overrides, including Primitive and FeaturePython, are separate implementations. Evidence: `src/Mod/Part/App/PartFeature.cpp:130`, `src/Mod/Part/App/PartFeature.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `CutFreeEdges` | `App::PropertyBool` | `bool` | `bool \| int` | Cutting of free edges | `src/Mod/Surface/App/FeatureSewing.cpp:45` |
| `DegenerateShape` | `App::PropertyBool` | `bool` | `bool \| int` | Analysis of degenerated shapes | `src/Mod/Surface/App/FeatureSewing.cpp:44` |
| `Nonmanifold` | `App::PropertyBool` | `bool` | `bool \| int` | Non-manifold processing | `src/Mod/Surface/App/FeatureSewing.cpp:46` |
| `SewingOption` | `App::PropertyBool` | `bool` | `bool \| int` | Sewing option | `src/Mod/Surface/App/FeatureSewing.cpp:43` |
| `ShapeList` | `App::PropertyLinkSubList` | `list[tuple[DocumentObject, tuple[str, ...]]]` | `_DocumentObjectSubLinkInput \| Sequence[_DocumentObjectSubLinkListItemInput]` | Input shapes | `src/Mod/Surface/App/FeatureSewing.cpp:41` |
| `Tolerance` | `App::PropertyFloat` | `float` | `float` | Sewing tolerance | `src/Mod/Surface/App/FeatureSewing.cpp:42` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

