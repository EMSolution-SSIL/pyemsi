# `Fem` wrapper association audit

[Namespace index](index.md) | [Audit overview](../wrapper-review.md)

Every listed owner has no direct binding association in existing discovery. Native inheritance and closest verified implementation context are routing evidence, not automatic public Python class declarations. Exact descendant overrides, conditional compilation, initialization, cached PythonObject replacement, and target-version behavior remain unverified unless the linked type record supplies an explicit review.

| Native owner | Closest discovered ancestor binding | Reviewed implementation context | Registration evidence |
| --- | --- | --- | --- |
| [Fem::Constraint](Constraint.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/Mod/Fem/App/FemConstraint.cpp:82` |
| [Fem::ConstraintBearing](ConstraintBearing.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/Mod/Fem/App/FemConstraintBearing.cpp:39` |
| [Fem::ConstraintContact](ConstraintContact.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/Mod/Fem/App/FemConstraintContact.cpp:32` |
| [Fem::ConstraintDisplacement](ConstraintDisplacement.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/Mod/Fem/App/FemConstraintDisplacement.cpp:34` |
| [Fem::ConstraintFixed](ConstraintFixed.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/Mod/Fem/App/FemConstraintFixed.cpp:32` |
| [Fem::ConstraintFluidBoundary](ConstraintFluidBoundary.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/Mod/Fem/App/FemConstraintFluidBoundary.cpp:37` |
| [Fem::ConstraintForce](ConstraintForce.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/Mod/Fem/App/FemConstraintForce.cpp:35` |
| [Fem::ConstraintGear](ConstraintGear.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/Mod/Fem/App/FemConstraintGear.cpp:35` |
| [Fem::ConstraintHeatflux](ConstraintHeatflux.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/Mod/Fem/App/FemConstraintHeatflux.cpp:33` |
| [Fem::ConstraintInitialTemperature](ConstraintInitialTemperature.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/Mod/Fem/App/FemConstraintInitialTemperature.cpp:34` |
| [Fem::ConstraintPlaneRotation](ConstraintPlaneRotation.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/Mod/Fem/App/FemConstraintPlaneRotation.cpp:32` |
| [Fem::ConstraintPressure](ConstraintPressure.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/Mod/Fem/App/FemConstraintPressure.cpp:32` |
| [Fem::ConstraintPulley](ConstraintPulley.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/Mod/Fem/App/FemConstraintPulley.cpp:35` |
| [Fem::ConstraintPython](ConstraintPython.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/Mod/Fem/App/FemConstraint.cpp:564` |
| [Fem::ConstraintRigidBody](ConstraintRigidBody.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/Mod/Fem/App/FemConstraintRigidBody.cpp:31` |
| [Fem::ConstraintSpring](ConstraintSpring.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/Mod/Fem/App/FemConstraintSpring.cpp:34` |
| [Fem::ConstraintTemperature](ConstraintTemperature.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/Mod/Fem/App/FemConstraintTemperature.cpp:34` |
| [Fem::ConstraintTransform](ConstraintTransform.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/Mod/Fem/App/FemConstraintTransform.cpp:35` |
| [Fem::DocumentObject](DocumentObject.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/Mod/Fem/App/FemAnalysis.cpp:64` |
| [Fem::FeaturePython](FeaturePython.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/Mod/Fem/App/FemAnalysis.cpp:99` |
| [Fem::FemAnalysis](FemAnalysis.md) | App::DocumentObjectGroup -> FreeCAD.DocumentObjectGroup | App::DocumentObject | `src/Mod/Fem/App/FemAnalysis.cpp:36` |
| [Fem::FemAnalysisPython](FemAnalysisPython.md) | App::DocumentObjectGroup -> FreeCAD.DocumentObjectGroup | App::DocumentObject | `src/Mod/Fem/App/FemAnalysis.cpp:71` |
| [Fem::FemMeshObject](FemMeshObject.md) | App::GeoFeature -> FreeCAD.GeoFeature | App::GeoFeature | `src/Mod/Fem/App/FemMeshObject.cpp:37` |
| [Fem::FemMeshObjectPython](FemMeshObjectPython.md) | App::GeoFeature -> FreeCAD.GeoFeature | App::GeoFeature | `src/Mod/Fem/App/FemMeshObject.cpp:80` |
| [Fem::FemMeshShapeBaseObject](FemMeshShapeBaseObject.md) | App::GeoFeature -> FreeCAD.GeoFeature | App::GeoFeature | `src/Mod/Fem/App/FemMeshShapeObject.cpp:40` |
| [Fem::FemMeshShapeBaseObjectPython](FemMeshShapeBaseObjectPython.md) | App::GeoFeature -> FreeCAD.GeoFeature | App::GeoFeature | `src/Mod/Fem/App/FemMeshShapeObject.cpp:88` |
| [Fem::FemMeshShapeNetgenObject](FemMeshShapeNetgenObject.md) | App::GeoFeature -> FreeCAD.GeoFeature | App::GeoFeature | `src/Mod/Fem/App/FemMeshShapeNetgenObject.cpp:47` |
| [Fem::FemMeshShapeObject](FemMeshShapeObject.md) | App::GeoFeature -> FreeCAD.GeoFeature | App::GeoFeature | `src/Mod/Fem/App/FemMeshShapeObject.cpp:59` |
| [Fem::FemPostBoxFunction](FemPostBoxFunction.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/Mod/Fem/App/FemPostFunction.cpp:86` |
| [Fem::FemPostCalculatorFilter](FemPostCalculatorFilter.md) | Fem::FemPostFilter -> Fem.FemPostFilter | App::GeoFeature | `src/Mod/Fem/App/FemPostFilter.cpp:1416` |
| [Fem::FemPostClipFilter](FemPostClipFilter.md) | Fem::FemPostFilter -> Fem.FemPostFilter | App::GeoFeature | `src/Mod/Fem/App/FemPostFilter.cpp:678` |
| [Fem::FemPostContoursFilter](FemPostContoursFilter.md) | Fem::FemPostFilter -> Fem.FemPostFilter | App::GeoFeature | `src/Mod/Fem/App/FemPostFilter.cpp:882` |
| [Fem::FemPostCutFilter](FemPostCutFilter.md) | Fem::FemPostFilter -> Fem.FemPostFilter | App::GeoFeature | `src/Mod/Fem/App/FemPostFilter.cpp:1163` |
| [Fem::FemPostCylinderFunction](FemPostCylinderFunction.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/Mod/Fem/App/FemPostFunction.cpp:163` |
| [Fem::FemPostDataAlongLineFilter](FemPostDataAlongLineFilter.md) | Fem::FemPostFilter -> Fem.FemPostFilter | App::GeoFeature | `src/Mod/Fem/App/FemPostFilter.cpp:351` |
| [Fem::FemPostDataAtPointFilter](FemPostDataAtPointFilter.md) | Fem::FemPostFilter -> Fem.FemPostFilter | App::GeoFeature | `src/Mod/Fem/App/FemPostFilter.cpp:563` |
| [Fem::FemPostFunction](FemPostFunction.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/Mod/Fem/App/FemPostFunction.cpp:72` |
| [Fem::FemPostFunctionProvider](FemPostFunctionProvider.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/Mod/Fem/App/FemPostFunction.cpp:33` |
| [Fem::FemPostPlaneFunction](FemPostPlaneFunction.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/Mod/Fem/App/FemPostFunction.cpp:232` |
| [Fem::FemPostScalarClipFilter](FemPostScalarClipFilter.md) | Fem::FemPostFilter -> Fem.FemPostFilter | App::GeoFeature | `src/Mod/Fem/App/FemPostFilter.cpp:1228` |
| [Fem::FemPostSphereFunction](FemPostSphereFunction.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/Mod/Fem/App/FemPostFunction.cpp:293` |
| [Fem::FemPostWarpVectorFilter](FemPostWarpVectorFilter.md) | Fem::FemPostFilter -> Fem.FemPostFilter | App::GeoFeature | `src/Mod/Fem/App/FemPostFilter.cpp:1335` |
| [Fem::FemResultObject](FemResultObject.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/Mod/Fem/App/FemResultObject.cpp:35` |
| [Fem::FemResultObjectPython](FemResultObjectPython.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/Mod/Fem/App/FemResultObject.cpp:72` |
| [Fem::FemSetElementNodesObject](FemSetElementNodesObject.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/Mod/Fem/App/FemSetElementNodesObject.cpp:35` |
| [Fem::FemSetElementsObject](FemSetElementsObject.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/Mod/Fem/App/FemSetElementsObject.cpp:34` |
| [Fem::FemSetFacesObject](FemSetFacesObject.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/Mod/Fem/App/FemSetFacesObject.cpp:34` |
| [Fem::FemSetGeometryObject](FemSetGeometryObject.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/Mod/Fem/App/FemSetGeometryObject.cpp:33` |
| [Fem::FemSetNodesObject](FemSetNodesObject.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/Mod/Fem/App/FemSetNodesObject.cpp:34` |
| [Fem::FemSetObject](FemSetObject.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/Mod/Fem/App/FemSetObject.cpp:33` |
| [Fem::FemSolverObject](FemSolverObject.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/Mod/Fem/App/FemSolverObject.cpp:36` |
| [Fem::FemSolverObjectPython](FemSolverObjectPython.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/Mod/Fem/App/FemSolverObject.cpp:73` |
| [Fem::PostFilterPython](PostFilterPython.md) | Fem::FemPostFilter -> Fem.FemPostFilter | App::GeoFeature | `src/Mod/Fem/App/FemPostFilter.cpp:321` |
