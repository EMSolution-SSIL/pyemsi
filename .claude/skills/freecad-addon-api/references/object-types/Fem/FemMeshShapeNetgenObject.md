# `Fem::FemMeshShapeNetgenObject`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/Mod/Fem/App/FemMeshShapeNetgenObject.cpp:47`. Abstract macro: no.

Native parent: [Fem::FemMeshShapeBaseObject](../Fem/FemMeshShapeBaseObject.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `App::GeoFeature` -> `FreeCAD.GeoFeature`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `App::GeoFeature`: This implementation creates GeoFeaturePy. The binding is FreeCAD.GeoFeature; native descendants may override getPyObject. Evidence: `src/App/GeoFeature.cpp:82`, `src/App/GeoFeature.pyi`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |
| --- | --- | --- | --- | --- | --- |
| `Fineness` | `App::PropertyEnumeration` | `str` | `str \| list[str]` | Fineness level of the mesh | `src/Mod/Fem/App/FemMeshShapeNetgenObject.cpp:57` |
| `GrowthRate` | `App::PropertyFloat` | `float` | `float` |  allows defining how much the linear dimensions of two adjacent cells can differ | `src/Mod/Fem/App/FemMeshShapeNetgenObject.cpp:59` |
| `MaxSize` | `App::PropertyFloat` | `float` | `float` | Maximum element size | `src/Mod/Fem/App/FemMeshShapeNetgenObject.cpp:54` |
| `MinSize` | `App::PropertyFloat` | `float` | `float` | Minimum element size | `src/Mod/Fem/App/FemMeshShapeNetgenObject.cpp:55` |
| `NbSegsPerEdge` | `App::PropertyInteger` | `int` | `int` | allows defining the minimum number of mesh segments in which edges will be split | `src/Mod/Fem/App/FemMeshShapeNetgenObject.cpp:66` |
| `NbSegsPerRadius` | `App::PropertyInteger` | `int` | `int` | allows defining the minimum number of mesh segments in which radii will be split | `src/Mod/Fem/App/FemMeshShapeNetgenObject.cpp:73` |
| `Optimize` | `App::PropertyBool` | `bool` | `bool \| int` | Optimize the resulting mesh | `src/Mod/Fem/App/FemMeshShapeNetgenObject.cpp:80` |
| `SecondOrder` | `App::PropertyBool` | `bool` | `bool \| int` | Create quadric elements | `src/Mod/Fem/App/FemMeshShapeNetgenObject.cpp:56` |

Getter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.

