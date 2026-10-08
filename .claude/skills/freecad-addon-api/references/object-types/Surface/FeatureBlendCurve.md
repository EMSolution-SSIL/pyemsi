# `Surface::FeatureBlendCurve`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/Surface/App/Blending/FeatureBlendCurve.cpp:46`. Abstract macro: no.

Native parent: [Part::Spline](../Part/Spline.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `Part::Feature` -> `Part.Feature`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `Part::Feature`: This implementation creates PartFeaturePy, exposed as Part.Feature. Descendant overrides, including Primitive and FeaturePython, are separate implementations. Evidence: `src/Mod/Part/App/PartFeature.cpp:130`, `src/Mod/Part/App/PartFeature.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `EndContinuity` | `App::PropertyIntegerConstraint` | `int` | `int \| dict[str, int] \| tuple[int, int, int, int]` | Geometric continuity at end point | `src/Mod/Surface/App/Blending/FeatureBlendCurve.cpp:71` |
| `EndEdge` | `App::PropertyLinkSub` | `tuple[DocumentObject, list[str]] \| None` | `DocumentObject \| None \| _DocumentObjectSubLinkPairInput` | Edge support of the end point | `src/Mod/Surface/App/Blending/FeatureBlendCurve.cpp:70` |
| `EndParameter` | `App::PropertyFloatConstraint` | `float` | `float \| int \| dict[str, float] \| tuple[float, float, float, float]` | Parameter of end point along edge | `src/Mod/Surface/App/Blending/FeatureBlendCurve.cpp:73` |
| `EndSize` | `App::PropertyFloatConstraint` | `float` | `float \| int \| dict[str, float] \| tuple[float, float, float, float]` | Size of derivatives at end point | `src/Mod/Surface/App/Blending/FeatureBlendCurve.cpp:81` |
| `StartContinuity` | `App::PropertyIntegerConstraint` | `int` | `int \| dict[str, int] \| tuple[int, int, int, int]` | Geometric continuity at start point | `src/Mod/Surface/App/Blending/FeatureBlendCurve.cpp:51` |
| `StartEdge` | `App::PropertyLinkSub` | `tuple[DocumentObject, list[str]] \| None` | `DocumentObject \| None \| _DocumentObjectSubLinkPairInput` | Edge support of the start point | `src/Mod/Surface/App/Blending/FeatureBlendCurve.cpp:50` |
| `StartParameter` | `App::PropertyFloatConstraint` | `float` | `float \| int \| dict[str, float] \| tuple[float, float, float, float]` | Parameter of start point along edge | `src/Mod/Surface/App/Blending/FeatureBlendCurve.cpp:59` |
| `StartSize` | `App::PropertyFloatConstraint` | `float` | `float \| int \| dict[str, float] \| tuple[float, float, float, float]` | Size of derivatives at start point | `src/Mod/Surface/App/Blending/FeatureBlendCurve.cpp:67` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

