# `Part` wrapper association audit

[Namespace index](index.md) | [Audit overview](../wrapper-review.md)

Every listed owner has no direct binding association in existing discovery. Native inheritance and closest verified implementation context are routing evidence, not automatic public Python class declarations. Exact descendant overrides, conditional compilation, initialization, cached PythonObject replacement, and target-version behavior remain unverified unless the linked type record supplies an explicit review.

| Native owner | Closest discovered ancestor binding | Reviewed implementation context | Registration evidence |
| --- | --- | --- | --- |
| [Part::Boolean](Boolean.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/Part/App/FeaturePartBoolean.cpp:75` |
| [Part::Box](Box.md) | Part::Feature -> Part.Feature | Part::Box | `src/Mod/Part/App/FeaturePartBox.cpp:36` |
| [Part::Chamfer](Chamfer.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/Part/App/FeatureChamfer.cpp:41` |
| [Part::Circle](Circle.md) | Part::Feature -> Part.Feature | Part::Primitive | `src/Mod/Part/App/FeaturePartCircle.cpp:39` |
| [Part::Common](Common.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/Part/App/FeaturePartCommon.cpp:48` |
| [Part::Compound](Compound.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/Part/App/FeatureCompound.cpp:37` |
| [Part::Compound2](Compound2.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/Part/App/FeatureCompound.cpp:86` |
| [Part::Cone](Cone.md) | Part::Feature -> Part.Feature | Part::Primitive | `src/Mod/Part/App/PrimitiveFeature.cpp:688` |
| [Part::CurveNet](CurveNet.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/Part/App/FeaturePartCurveNet.cpp:33` |
| [Part::CustomFeature](CustomFeature.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/Part/App/CustomFeature.cpp:32` |
| [Part::CustomFeaturePython](CustomFeaturePython.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/Part/App/CustomFeature.cpp:54` |
| [Part::Cut](Cut.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/Part/App/FeaturePartCut.cpp:33` |
| [Part::Cylinder](Cylinder.md) | Part::Feature -> Part.Feature | Part::Primitive | `src/Mod/Part/App/PrimitiveFeature.cpp:481` |
| [Part::Datum](Datum.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/Part/App/DatumFeature.cpp:35` |
| [Part::DatumLine](DatumLine.md) | App::GeoFeature -> FreeCAD.GeoFeature | App::GeoFeature | `src/Mod/Part/App/Datums.cpp:41` |
| [Part::DatumPlane](DatumPlane.md) | App::GeoFeature -> FreeCAD.GeoFeature | App::GeoFeature | `src/Mod/Part/App/Datums.cpp:32` |
| [Part::DatumPoint](DatumPoint.md) | App::GeoFeature -> FreeCAD.GeoFeature | App::GeoFeature | `src/Mod/Part/App/Datums.cpp:51` |
| [Part::Ellipse](Ellipse.md) | Part::Feature -> Part.Feature | Part::Primitive | `src/Mod/Part/App/PrimitiveFeature.cpp:1116` |
| [Part::Ellipsoid](Ellipsoid.md) | Part::Feature -> Part.Feature | Part::Primitive | `src/Mod/Part/App/PrimitiveFeature.cpp:388` |
| [Part::Extrusion](Extrusion.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/Part/App/FeatureExtrusion.cpp:54` |
| [Part::Face](Face.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/Part/App/FeatureFace.cpp:36` |
| [Part::FeatureExt](FeatureExt.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/Part/App/PartFeature.cpp:2117` |
| [Part::FeatureGeometrySet](FeatureGeometrySet.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/Part/App/FeatureGeometrySet.cpp:32` |
| [Part::FeaturePython](FeaturePython.md) | Part::Feature -> Part.Feature | Part::FeaturePython | `src/Mod/Part/App/PartFeature.cpp:2123` |
| [Part::FeatureReference](FeatureReference.md) | App::GeoFeature -> FreeCAD.GeoFeature | App::GeoFeature | `src/Mod/Part/App/PartFeatureReference.cpp:38` |
| [Part::Fillet](Fillet.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/Part/App/FeatureFillet.cpp:45` |
| [Part::FilletBase](FilletBase.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/Part/App/PartFeature.cpp:2028` |
| [Part::Fuse](Fuse.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/Part/App/FeaturePartFuse.cpp:51` |
| [Part::Helix](Helix.md) | Part::Feature -> Part.Feature | Part::Primitive | `src/Mod/Part/App/PrimitiveFeature.cpp:819` |
| [Part::ImportBrep](ImportBrep.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/Part/App/FeaturePartImportBrep.cpp:36` |
| [Part::ImportIges](ImportIges.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/Part/App/FeaturePartImportIges.cpp:36` |
| [Part::ImportStep](ImportStep.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/Part/App/FeaturePartImportStep.cpp:36` |
| [Part::Line](Line.md) | Part::Feature -> Part.Feature | Part::Primitive | `src/Mod/Part/App/PrimitiveFeature.cpp:210` |
| [Part::LinkArray](LinkArray.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/Mod/Part/App/LinkArray.cpp:40` |
| [Part::LinkArrayCircular](LinkArrayCircular.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/Mod/Part/App/LinkArrayCircular.cpp:29` |
| [Part::LinkArrayLinear](LinkArrayLinear.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/Mod/Part/App/LinkArrayLinear.cpp:41` |
| [Part::LinkArrayPath](LinkArrayPath.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/Mod/Part/App/LinkArrayPath.cpp:7` |
| [Part::LinkArrayPoint](LinkArrayPoint.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/Mod/Part/App/LinkArrayPoint.cpp:7` |
| [Part::LinkArrayPolar](LinkArrayPolar.md) | App::DocumentObject -> FreeCAD.DocumentObject | App::DocumentObject | `src/Mod/Part/App/LinkArrayPolar.cpp:45` |
| [Part::LocalCoordinateSystem](LocalCoordinateSystem.md) | App::GeoFeature -> FreeCAD.GeoFeature | App::GeoFeature | `src/Mod/Part/App/Datums.cpp:60` |
| [Part::Loft](Loft.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/Part/App/PartFeatures.cpp:177` |
| [Part::Mirroring](Mirroring.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/Part/App/FeatureMirroring.cpp:52` |
| [Part::MultiCommon](MultiCommon.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/Part/App/FeaturePartCommon.cpp:65` |
| [Part::MultiFuse](MultiFuse.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/Part/App/FeaturePartFuse.cpp:69` |
| [Part::Offset](Offset.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/Part/App/FeatureOffset.cpp:39` |
| [Part::Offset2D](Offset2D.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/Part/App/FeatureOffset.cpp:118` |
| [Part::Part2DObjectPython](Part2DObjectPython.md) | Part::Part2DObject -> Part.Part2DObject | Part::Feature | `src/Mod/Part/App/Part2DObject.cpp:278` |
| [Part::Plane](Plane.md) | Part::Feature -> Part.Feature | Part::Primitive | `src/Mod/Part/App/PrimitiveFeature.cpp:270` |
| [Part::Polygon](Polygon.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/Part/App/FeaturePartPolygon.cpp:33` |
| [Part::Primitive](Primitive.md) | Part::Feature -> Part.Feature | Part::Primitive | `src/Mod/Part/App/PrimitiveFeature.cpp:68` |
| [Part::Prism](Prism.md) | Part::Feature -> Part.Feature | Part::Primitive | `src/Mod/Part/App/PrimitiveFeature.cpp:540` |
| [Part::ProjectOnSurface](ProjectOnSurface.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/Part/App/FeatureProjectOnSurface.cpp:54` |
| [Part::Refine](Refine.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/Part/App/PartFeatures.cpp:455` |
| [Part::RegularPolygon](RegularPolygon.md) | Part::Feature -> Part.Feature | Part::Primitive | `src/Mod/Part/App/PrimitiveFeature.cpp:621` |
| [Part::Reverse](Reverse.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/Part/App/PartFeatures.cpp:481` |
| [Part::Revolution](Revolution.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/Part/App/FeatureRevolution.cpp:43` |
| [Part::RuledSurface](RuledSurface.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/Part/App/PartFeatures.cpp:54` |
| [Part::Scale](Scale.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/Part/App/FeatureScale.cpp:40` |
| [Part::Section](Section.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/Part/App/FeaturePartSection.cpp:34` |
| [Part::Sphere](Sphere.md) | Part::Feature -> Part.Feature | Part::Primitive | `src/Mod/Part/App/PrimitiveFeature.cpp:333` |
| [Part::Spiral](Spiral.md) | Part::Feature -> Part.Feature | Part::Primitive | `src/Mod/Part/App/PrimitiveFeature.cpp:943` |
| [Part::Spline](Spline.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/Part/App/FeaturePartSpline.cpp:31` |
| [Part::Sweep](Sweep.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/Part/App/PartFeatures.cpp:258` |
| [Part::Thickness](Thickness.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/Part/App/PartFeatures.cpp:365` |
| [Part::Torus](Torus.md) | Part::Feature -> Part.Feature | Part::Primitive | `src/Mod/Part/App/PrimitiveFeature.cpp:758` |
| [Part::Vertex](Vertex.md) | Part::Feature -> Part.Feature | Part::Primitive | `src/Mod/Part/App/PrimitiveFeature.cpp:161` |
| [Part::Wedge](Wedge.md) | Part::Feature -> Part.Feature | Part::Primitive | `src/Mod/Part/App/PrimitiveFeature.cpp:1020` |
