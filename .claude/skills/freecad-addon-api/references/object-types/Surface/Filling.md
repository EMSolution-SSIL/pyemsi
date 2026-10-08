# `Surface::Filling`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/Surface/App/FeatureFilling.cpp:39`. Abstract macro: no.

Native parent: [Part::Spline](../Part/Spline.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `Part::Feature` -> `Part.Feature`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `Part::Feature`: This implementation creates PartFeaturePy, exposed as Part.Feature. Descendant overrides, including Primitive and FeaturePython, are separate implementations. Evidence: `src/Mod/Part/App/PartFeature.cpp:130`, `src/Mod/Part/App/PartFeature.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `Anisotropy` | `App::PropertyBool` | `bool` | `bool \| int` | Anisotropy | `src/Mod/Surface/App/FeatureFilling.cpp:69` |
| `BoundaryEdges` | `App::PropertyLinkSubList` | `list[tuple[DocumentObject, tuple[str, ...]]]` | `_DocumentObjectSubLinkInput \| Sequence[_DocumentObjectSubLinkListItemInput]` | Boundary Edges (C0 is required for edges without a corresponding face) | `src/Mod/Surface/App/FeatureFilling.cpp:46` |
| `BoundaryFaces` | `App::PropertyStringList` | `list[str]` | `Sequence[str]` | Boundary Faces | `src/Mod/Surface/App/FeatureFilling.cpp:48` |
| `BoundaryOrder` | `App::PropertyIntegerList` | `list[int]` | `Sequence[int]` | Order of constraint on boundary faces (C0, G1 and G2 are possible) | `src/Mod/Surface/App/FeatureFilling.cpp:49` |
| `Degree` | `App::PropertyInteger` | `int` | `int` | Starting degree | `src/Mod/Surface/App/FeatureFilling.cpp:65` |
| `FreeFaces` | `App::PropertyLinkSubList` | `list[tuple[DocumentObject, tuple[str, ...]]]` | `_DocumentObjectSubLinkInput \| Sequence[_DocumentObjectSubLinkListItemInput]` | Free constraint on a face | `src/Mod/Surface/App/FeatureFilling.cpp:59` |
| `FreeOrder` | `App::PropertyIntegerList` | `list[int]` | `Sequence[int]` | Order of constraint on free faces | `src/Mod/Surface/App/FeatureFilling.cpp:60` |
| `InitialFace` | `App::PropertyLinkSub` | `tuple[DocumentObject, list[str]] \| None` | `DocumentObject \| None \| _DocumentObjectSubLinkPairInput` | Initial surface to use | `src/Mod/Surface/App/FeatureFilling.cpp:63` |
| `Iterations` | `App::PropertyInteger` | `int` | `int` | Number of iterations | `src/Mod/Surface/App/FeatureFilling.cpp:68` |
| `MaximumDegree` | `App::PropertyInteger` | `int` | `int` | Maximum curve degree | `src/Mod/Surface/App/FeatureFilling.cpp:74` |
| `MaximumSegments` | `App::PropertyInteger` | `int` | `int` | Maximum number of segments | `src/Mod/Surface/App/FeatureFilling.cpp:75` |
| `Points` | `App::PropertyLinkSubList` | `list[tuple[DocumentObject, tuple[str, ...]]]` | `_DocumentObjectSubLinkInput \| Sequence[_DocumentObjectSubLinkListItemInput]` | Constraint Points (on Surface) | `src/Mod/Surface/App/FeatureFilling.cpp:62` |
| `PointsOnCurve` | `App::PropertyInteger` | `int` | `int` | Number of points on an edge for constraint | `src/Mod/Surface/App/FeatureFilling.cpp:66` |
| `TolAngular` | `App::PropertyFloat` | `float` | `float` | G1 tolerance | `src/Mod/Surface/App/FeatureFilling.cpp:72` |
| `TolCurvature` | `App::PropertyFloat` | `float` | `float` | G2 tolerance | `src/Mod/Surface/App/FeatureFilling.cpp:73` |
| `Tolerance2d` | `App::PropertyFloat` | `float` | `float` | 2D Tolerance | `src/Mod/Surface/App/FeatureFilling.cpp:70` |
| `Tolerance3d` | `App::PropertyFloat` | `float` | `float` | 3D Tolerance | `src/Mod/Surface/App/FeatureFilling.cpp:71` |
| `UnboundEdges` | `App::PropertyLinkSubList` | `list[tuple[DocumentObject, tuple[str, ...]]]` | `_DocumentObjectSubLinkInput \| Sequence[_DocumentObjectSubLinkListItemInput]` | Unbound constraint edges (C0 is required for edges without a corresponding face) | `src/Mod/Surface/App/FeatureFilling.cpp:52` |
| `UnboundFaces` | `App::PropertyStringList` | `list[str]` | `Sequence[str]` | Unbound constraint faces | `src/Mod/Surface/App/FeatureFilling.cpp:54` |
| `UnboundOrder` | `App::PropertyIntegerList` | `list[int]` | `Sequence[int]` | Order of constraint on curve faces (C0, G1 and G2 are possible) | `src/Mod/Surface/App/FeatureFilling.cpp:56` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

