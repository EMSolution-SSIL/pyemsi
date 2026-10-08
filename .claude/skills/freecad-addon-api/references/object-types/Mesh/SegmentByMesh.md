# `Mesh::SegmentByMesh`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/Mesh/App/FeatureMeshSegmentByMesh.cpp:38`. Abstract macro: no.

Native parent: [Mesh::Feature](../Mesh/Feature.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `Mesh::Feature` -> `Mesh.Feature`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `App::GeoFeature`: This implementation creates GeoFeaturePy. The binding is FreeCAD.GeoFeature; native descendants may override getPyObject. Evidence: `src/App/GeoFeature.cpp:82`, `src/App/GeoFeature.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `Base` | `App::PropertyVector` | `Base.Vector` | `Base.Vector \| tuple[float, float, float]` | Not documented by registration | `src/Mod/Mesh/App/FeatureMeshSegmentByMesh.cpp:45` |
| `Normal` | `App::PropertyVector` | `Base.Vector` | `Base.Vector \| tuple[float, float, float]` | Not documented by registration | `src/Mod/Mesh/App/FeatureMeshSegmentByMesh.cpp:46` |
| `Source` | `App::PropertyLink` | `DocumentObject \| None` | `DocumentObject \| None` | Not documented by registration | `src/Mod/Mesh/App/FeatureMeshSegmentByMesh.cpp:43` |
| `Tool` | `App::PropertyLink` | `DocumentObject \| None` | `DocumentObject \| None` | Not documented by registration | `src/Mod/Mesh/App/FeatureMeshSegmentByMesh.cpp:44` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

