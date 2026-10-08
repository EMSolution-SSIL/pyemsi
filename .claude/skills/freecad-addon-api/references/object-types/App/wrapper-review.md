# `App` wrapper association audit

[Namespace index](index.md) | [Audit overview](../wrapper-review.md)

Every listed owner has no direct binding association in existing discovery. Native inheritance and closest verified implementation context are routing evidence, not automatic public Python class declarations. Exact descendant overrides, conditional compilation, initialization, cached PythonObject replacement, and target-version behavior remain unverified unless the linked type record supplies an explicit review.

| Native owner | Closest discovered ancestor binding | Reviewed implementation context | Registration evidence |
| --- | --- | --- | --- |
| [App::Annotation](Annotation.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/App/Annotation.cpp:31` |
| [App::AnnotationLabel](AnnotationLabel.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/App/Annotation.cpp:44` |
| [App::DatumElement](DatumElement.md) | App::GeoFeature -> FreeCAD.GeoFeature | App::GeoFeature | `src/App/Datums.cpp:37` |
| [App::DocumentObjectFileIncluded](DocumentObjectFileIncluded.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/App/DocumentObjectFileIncluded.cpp:30` |
| [App::DocumentObjectGroupPython](DocumentObjectGroupPython.md) | App::DocumentObjectGroup -> FreeCAD.DocumentObjectGroup | App::DocumentObject | `src/App/DocumentObjectGroup.cpp:60` |
| [App::FeaturePython](FeaturePython.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::FeaturePython | `src/App/FeaturePython.cpp:756` |
| [App::FeatureTest](FeatureTest.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/App/FeatureTest.cpp:68` |
| [App::FeatureTestAbsAddress](FeatureTestAbsAddress.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/App/FeatureTest.cpp:301` |
| [App::FeatureTestAsyncBlocker](FeatureTestAsyncBlocker.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/App/FeatureTest.cpp:397` |
| [App::FeatureTestAttribute](FeatureTestAttribute.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/App/FeatureTest.cpp:342` |
| [App::FeatureTestColumn](FeatureTestColumn.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/App/FeatureTest.cpp:265` |
| [App::FeatureTestException](FeatureTestException.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/App/FeatureTest.cpp:247` |
| [App::FeatureTestPlacement](FeatureTestPlacement.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/App/FeatureTest.cpp:319` |
| [App::FeatureTestRow](FeatureTestRow.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/App/FeatureTest.cpp:283` |
| [App::GeometryPython](GeometryPython.md) | App::GeoFeature -> FreeCAD.GeoFeature | App::GeoFeature | `src/App/FeaturePython.cpp:779` |
| [App::InventorObject](InventorObject.md) | App::GeoFeature -> FreeCAD.GeoFeature | App::GeoFeature | `src/App/InventorObject.cpp:31` |
| [App::Line](Line.md) | App::GeoFeature -> FreeCAD.GeoFeature | App::GeoFeature | `src/App/Datums.cpp:39` |
| [App::Link](Link.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/App/Link.cpp:2650` |
| [App::LinkElement](LinkElement.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/App/Link.cpp:2761` |
| [App::LinkElementPython](LinkElementPython.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/App/Link.cpp:2847` |
| [App::LinkGroup](LinkGroup.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/App/Link.cpp:2858` |
| [App::LinkGroupPython](LinkGroupPython.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/App/Link.cpp:2870` |
| [App::LinkPython](LinkPython.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/App/Link.cpp:2750` |
| [App::LocalCoordinateSystem](LocalCoordinateSystem.md) | App::GeoFeature -> FreeCAD.GeoFeature | App::GeoFeature | `src/App/Datums.cpp:41` |
| [App::MaterialObject](MaterialObject.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/App/MaterialObject.cpp:30` |
| [App::MaterialObjectPython](MaterialObjectPython.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/App/MaterialObject.cpp:43` |
| [App::Origin](Origin.md) | App::GeoFeature -> FreeCAD.GeoFeature | App::GeoFeature | `src/App/Origin.cpp:34` |
| [App::Placement](Placement.md) | App::GeoFeature -> FreeCAD.GeoFeature | App::GeoFeature | `src/App/Placement.cpp:34` |
| [App::PlacementPython](PlacementPython.md) | App::GeoFeature -> FreeCAD.GeoFeature | App::GeoFeature | `src/App/Placement.cpp:49` |
| [App::Plane](Plane.md) | App::GeoFeature -> FreeCAD.GeoFeature | App::GeoFeature | `src/App/Datums.cpp:38` |
| [App::Point](Point.md) | App::GeoFeature -> FreeCAD.GeoFeature | App::GeoFeature | `src/App/Datums.cpp:40` |
| [App::TextDocument](TextDocument.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/App/TextDocument.cpp:33` |
| [App::VRMLObject](VRMLObject.md) | App::GeoFeature -> FreeCAD.GeoFeature | App::GeoFeature | `src/App/VRMLObject.cpp:37` |
| [App::VarSet](VarSet.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/App/VarSet.cpp:32` |
