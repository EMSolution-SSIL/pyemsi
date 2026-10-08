# `Surface::Extend`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/Surface/App/FeatureExtend.cpp:49`. Abstract macro: no.

Native parent: [Part::Spline](../Part/Spline.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `Part::Feature` -> `Part.Feature`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `Part::Feature`: This implementation creates PartFeaturePy, exposed as Part.Feature. Descendant overrides, including Primitive and FeaturePython, are separate implementations. Evidence: `src/Mod/Part/App/PartFeature.cpp:130`, `src/Mod/Part/App/PartFeature.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `ExtendUNeg` | `App::PropertyFloatConstraint` | `float` | `float \| int \| dict[str, float] \| tuple[float, float, float, float]` | Not documented by registration | `src/Mod/Surface/App/FeatureExtend.cpp:58` |
| `ExtendUPos` | `App::PropertyFloatConstraint` | `float` | `float \| int \| dict[str, float] \| tuple[float, float, float, float]` | Not documented by registration | `src/Mod/Surface/App/FeatureExtend.cpp:60` |
| `ExtendUSymetric` | `App::PropertyBool` | `bool` | `bool \| int` | Not documented by registration | `src/Mod/Surface/App/FeatureExtend.cpp:62` |
| `ExtendVNeg` | `App::PropertyFloatConstraint` | `float` | `float \| int \| dict[str, float] \| tuple[float, float, float, float]` | Not documented by registration | `src/Mod/Surface/App/FeatureExtend.cpp:64` |
| `ExtendVPos` | `App::PropertyFloatConstraint` | `float` | `float \| int \| dict[str, float] \| tuple[float, float, float, float]` | Not documented by registration | `src/Mod/Surface/App/FeatureExtend.cpp:66` |
| `ExtendVSymetric` | `App::PropertyBool` | `bool` | `bool \| int` | Not documented by registration | `src/Mod/Surface/App/FeatureExtend.cpp:68` |
| `Face` | `App::PropertyLinkSub` | `tuple[DocumentObject, list[str]] \| None` | `DocumentObject \| None \| _DocumentObjectSubLinkPairInput` | Not documented by registration | `src/Mod/Surface/App/FeatureExtend.cpp:53` |
| `SampleU` | `App::PropertyIntegerConstraint` | `int` | `int \| dict[str, int] \| tuple[int, int, int, int]` | Not documented by registration | `src/Mod/Surface/App/FeatureExtend.cpp:70` |
| `SampleV` | `App::PropertyIntegerConstraint` | `int` | `int \| dict[str, int] \| tuple[int, int, int, int]` | Not documented by registration | `src/Mod/Surface/App/FeatureExtend.cpp:72` |
| `Tolerance` | `App::PropertyFloatConstraint` | `float` | `float \| int \| dict[str, float] \| tuple[float, float, float, float]` | Not documented by registration | `src/Mod/Surface/App/FeatureExtend.cpp:55` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

