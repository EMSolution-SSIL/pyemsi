# `Part::ProjectOnSurface`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/Part/App/FeatureProjectOnSurface.cpp:54`. Abstract macro: no.

Native parent: [Part::Feature](../Part/Feature.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `Part::Feature` -> `Part.Feature`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `Part::Feature`: This implementation creates PartFeaturePy, exposed as Part.Feature. Descendant overrides, including Primitive and FeaturePython, are separate implementations. Evidence: `src/Mod/Part/App/PartFeature.cpp:130`, `src/Mod/Part/App/PartFeature.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `Direction` | `App::PropertyDirection` | `Base.Vector` | `Base.Vector \| tuple[float, float, float]` | Direction of projection | `src/Mod/Part/App/FeatureProjectOnSurface.cpp:63` |
| `Height` | `App::PropertyLength` | `Base.Quantity` | `float \| str \| Base.Quantity` | Extrusion height | `src/Mod/Part/App/FeatureProjectOnSurface.cpp:61` |
| `Mode` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Projection mode | `src/Mod/Part/App/FeatureProjectOnSurface.cpp:59` |
| `Offset` | `App::PropertyDistance` | `Base.Quantity` | `float \| str \| Base.Quantity \| Base.Unit` | Offset of solid | `src/Mod/Part/App/FeatureProjectOnSurface.cpp:62` |
| `Projection` | `App::PropertyLinkSubList` | `list[tuple[DocumentObject, tuple[str, ...]]]` | `_DocumentObjectSubLinkInput \| Sequence[_DocumentObjectSubLinkListItemInput]` | Shapes to project onto support face | `src/Mod/Part/App/FeatureProjectOnSurface.cpp:71` |
| `SupportFace` | `App::PropertyLinkSub` | `tuple[DocumentObject, list[str]] \| None` | `DocumentObject \| None \| _DocumentObjectSubLinkPairInput` | Support faceo | `src/Mod/Part/App/FeatureProjectOnSurface.cpp:70` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

