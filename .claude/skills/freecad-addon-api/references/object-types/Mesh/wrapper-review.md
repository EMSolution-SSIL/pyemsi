# `Mesh` wrapper association audit

[Namespace index](index.md) | [Audit overview](../wrapper-review.md)

Every listed owner has no direct binding association in existing discovery. Native inheritance and closest verified implementation context are routing evidence, not automatic public Python class declarations. Exact descendant overrides, conditional compilation, initialization, cached PythonObject replacement, and target-version behavior remain unverified unless the linked type record supplies an explicit review.

| Native owner | Closest discovered ancestor binding | Reviewed implementation context | Registration evidence |
| --- | --- | --- | --- |
| [Mesh::Cone](Cone.md) | Mesh::Feature -> Mesh.Feature | App::GeoFeature | `src/Mod/Mesh/App/FeatureMeshSolid.cpp:203` |
| [Mesh::Cube](Cube.md) | Mesh::Feature -> Mesh.Feature | App::GeoFeature | `src/Mod/Mesh/App/FeatureMeshSolid.cpp:314` |
| [Mesh::Curvature](Curvature.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/Mod/Mesh/App/FeatureMeshCurvature.cpp:34` |
| [Mesh::Cylinder](Cylinder.md) | Mesh::Feature -> Mesh.Feature | App::GeoFeature | `src/Mod/Mesh/App/FeatureMeshSolid.cpp:144` |
| [Mesh::Ellipsoid](Ellipsoid.md) | Mesh::Feature -> Mesh.Feature | App::GeoFeature | `src/Mod/Mesh/App/FeatureMeshSolid.cpp:87` |
| [Mesh::Export](Export.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/Mod/Mesh/App/FeatureMeshExport.cpp:33` |
| [Mesh::FeatureCustom](FeatureCustom.md) | Mesh::Feature -> Mesh.Feature | App::GeoFeature | `src/Mod/Mesh/App/MeshFeature.cpp:94` |
| [Mesh::FeaturePython](FeaturePython.md) | Mesh::Feature -> Mesh.Feature | App::GeoFeature | `src/Mod/Mesh/App/MeshFeature.cpp:106` |
| [Mesh::FillHoles](FillHoles.md) | Mesh::Feature -> Mesh.Feature | App::GeoFeature | `src/Mod/Mesh/App/FeatureMeshDefects.cpp:259` |
| [Mesh::FixDefects](FixDefects.md) | Mesh::Feature -> Mesh.Feature | App::GeoFeature | `src/Mod/Mesh/App/FeatureMeshDefects.cpp:40` |
| [Mesh::FixDeformations](FixDeformations.md) | Mesh::Feature -> Mesh.Feature | App::GeoFeature | `src/Mod/Mesh/App/FeatureMeshDefects.cpp:207` |
| [Mesh::FixDegenerations](FixDegenerations.md) | Mesh::Feature -> Mesh.Feature | App::GeoFeature | `src/Mod/Mesh/App/FeatureMeshDefects.cpp:183` |
| [Mesh::FixDuplicatedFaces](FixDuplicatedFaces.md) | Mesh::Feature -> Mesh.Feature | App::GeoFeature | `src/Mod/Mesh/App/FeatureMeshDefects.cpp:135` |
| [Mesh::FixDuplicatedPoints](FixDuplicatedPoints.md) | Mesh::Feature -> Mesh.Feature | App::GeoFeature | `src/Mod/Mesh/App/FeatureMeshDefects.cpp:159` |
| [Mesh::FixIndices](FixIndices.md) | Mesh::Feature -> Mesh.Feature | App::GeoFeature | `src/Mod/Mesh/App/FeatureMeshDefects.cpp:235` |
| [Mesh::FixNonManifolds](FixNonManifolds.md) | Mesh::Feature -> Mesh.Feature | App::GeoFeature | `src/Mod/Mesh/App/FeatureMeshDefects.cpp:111` |
| [Mesh::FlipNormals](FlipNormals.md) | Mesh::Feature -> Mesh.Feature | App::GeoFeature | `src/Mod/Mesh/App/FeatureMeshDefects.cpp:87` |
| [Mesh::HarmonizeNormals](HarmonizeNormals.md) | Mesh::Feature -> Mesh.Feature | App::GeoFeature | `src/Mod/Mesh/App/FeatureMeshDefects.cpp:63` |
| [Mesh::Import](Import.md) | Mesh::Feature -> Mesh.Feature | App::GeoFeature | `src/Mod/Mesh/App/FeatureMeshImport.cpp:32` |
| [Mesh::RemoveComponents](RemoveComponents.md) | Mesh::Feature -> Mesh.Feature | App::GeoFeature | `src/Mod/Mesh/App/FeatureMeshDefects.cpp:289` |
| [Mesh::SegmentByMesh](SegmentByMesh.md) | Mesh::Feature -> Mesh.Feature | App::GeoFeature | `src/Mod/Mesh/App/FeatureMeshSegmentByMesh.cpp:38` |
| [Mesh::SetOperations](SetOperations.md) | Mesh::Feature -> Mesh.Feature | App::GeoFeature | `src/Mod/Mesh/App/FeatureMeshSetOperations.cpp:35` |
| [Mesh::Sphere](Sphere.md) | Mesh::Feature -> Mesh.Feature | App::GeoFeature | `src/Mod/Mesh/App/FeatureMeshSolid.cpp:41` |
| [Mesh::Torus](Torus.md) | Mesh::Feature -> Mesh.Feature | App::GeoFeature | `src/Mod/Mesh/App/FeatureMeshSolid.cpp:265` |
| [Mesh::Transform](Transform.md) | Mesh::Feature -> Mesh.Feature | App::GeoFeature | `src/Mod/Mesh/App/FeatureMeshTransform.cpp:35` |
| [Mesh::TransformDemolding](TransformDemolding.md) | Mesh::Feature -> Mesh.Feature | App::GeoFeature | `src/Mod/Mesh/App/FeatureMeshTransformDemolding.cpp:32` |
