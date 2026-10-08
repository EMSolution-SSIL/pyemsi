# `Part::Revolution`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/Part/App/FeatureRevolution.cpp:43`. Abstract macro: no.

Native parent: [Part::Feature](../Part/Feature.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `Part::Feature` -> `Part.Feature`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `Part::Feature`: This implementation creates PartFeaturePy, exposed as Part.Feature. Descendant overrides, including Primitive and FeaturePython, are separate implementations. Evidence: `src/Mod/Part/App/PartFeature.cpp:130`, `src/Mod/Part/App/PartFeature.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `Angle` | `App::PropertyFloatConstraint` | `float` | `float \| int \| dict[str, float] \| tuple[float, float, float, float]` | Not documented by registration | `src/Mod/Part/App/FeatureRevolution.cpp:69` |
| `Axis` | `App::PropertyVector` | `Base.Vector` | `Base.Vector \| tuple[float, float, float]` | Direction of revolution axis | `src/Mod/Part/App/FeatureRevolution.cpp:55` |
| `AxisLink` | `App::PropertyLinkSub` | `tuple[DocumentObject, list[str]] \| None` | `DocumentObject \| None \| _DocumentObjectSubLinkPairInput` | Link to edge to use as revolution axis. | `src/Mod/Part/App/FeatureRevolution.cpp:62` |
| `Base` | `App::PropertyVector` | `Base.Vector` | `Base.Vector \| tuple[float, float, float]` | Base point of revolution axis | `src/Mod/Part/App/FeatureRevolution.cpp:48` |
| `FaceMakerClass` | `App::PropertyString` | `str` | `str` | Facemaker to use if Solid is true. | `src/Mod/Part/App/FeatureRevolution.cpp:86` |
| `Solid` | `App::PropertyBool` | `bool` | `bool \| int` | Make revolution a solid if possible | `src/Mod/Part/App/FeatureRevolution.cpp:85` |
| `Source` | `App::PropertyLink` | `DocumentObject \| None` | `DocumentObject \| None` | Shape to revolve | `src/Mod/Part/App/FeatureRevolution.cpp:47` |
| `Symmetric` | `App::PropertyBool` | `bool` | `bool \| int` | Extend revolution symmetrically from the profile. | `src/Mod/Part/App/FeatureRevolution.cpp:78` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

