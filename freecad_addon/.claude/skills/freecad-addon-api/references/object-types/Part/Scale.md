# `Part::Scale`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/Part/App/FeatureScale.cpp:40`. Abstract macro: no.

Native parent: [Part::Feature](../Part/Feature.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `Part::Feature` -> `Part.Feature`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `Part::Feature`: This implementation creates PartFeaturePy, exposed as Part.Feature. Descendant overrides, including Primitive and FeaturePython, are separate implementations. Evidence: `src/Mod/Part/App/PartFeature.cpp:130`, `src/Mod/Part/App/PartFeature.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `Base` | `App::PropertyLink` | `DocumentObject \| None` | `DocumentObject \| None` | Shape to scale | `src/Mod/Part/App/FeatureScale.cpp:44` |
| `Uniform` | `App::PropertyBool` | `bool` | `bool \| int` | If true, scale equally in all directions | `src/Mod/Part/App/FeatureScale.cpp:45` |
| `UniformScale` | `App::PropertyFloat` | `float` | `float` | Uniform scale factor - 1.0 means no scaling | `src/Mod/Part/App/FeatureScale.cpp:46` |
| `XScale` | `App::PropertyFloat` | `float` | `float` | Scale factor in X-direction - 1.0 means no scaling | `src/Mod/Part/App/FeatureScale.cpp:53` |
| `YScale` | `App::PropertyFloat` | `float` | `float` | Scale factor in Y-direction - 1.0 means no scaling | `src/Mod/Part/App/FeatureScale.cpp:60` |
| `ZScale` | `App::PropertyFloat` | `float` | `float` | Scale factor in Z-direction - 1.0 means no scaling | `src/Mod/Part/App/FeatureScale.cpp:67` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

