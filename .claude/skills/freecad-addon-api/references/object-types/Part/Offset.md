# `Part::Offset`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/Part/App/FeatureOffset.cpp:39`. Abstract macro: no.

Native parent: [Part::Feature](../Part/Feature.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `Part::Feature` -> `Part.Feature`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `Part::Feature`: This implementation creates PartFeaturePy, exposed as Part.Feature. Descendant overrides, including Primitive and FeaturePython, are separate implementations. Evidence: `src/Mod/Part/App/PartFeature.cpp:130`, `src/Mod/Part/App/PartFeature.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `Fill` | `App::PropertyBool` | `bool` | `bool \| int` | Fill offset | `src/Mod/Part/App/FeatureOffset.cpp:51` |
| `Intersection` | `App::PropertyBool` | `bool` | `bool \| int` | Intersection | `src/Mod/Part/App/FeatureOffset.cpp:49` |
| `Join` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Join type | `src/Mod/Part/App/FeatureOffset.cpp:47` |
| `Mode` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Mode | `src/Mod/Part/App/FeatureOffset.cpp:45` |
| `SelfIntersection` | `App::PropertyBool` | `bool` | `bool \| int` | Self Intersection | `src/Mod/Part/App/FeatureOffset.cpp:50` |
| `Source` | `App::PropertyLink` | `DocumentObject \| None` | `DocumentObject \| None` | Source shape | `src/Mod/Part/App/FeatureOffset.cpp:43` |
| `Value` | `App::PropertyFloat` | `float` | `float` | Offset value | `src/Mod/Part/App/FeatureOffset.cpp:44` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

