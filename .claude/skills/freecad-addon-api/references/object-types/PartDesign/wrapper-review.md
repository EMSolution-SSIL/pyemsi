# `PartDesign` wrapper association audit

[Namespace index](index.md) | [Audit overview](../wrapper-review.md)

Every listed owner has no direct binding association in existing discovery. Native inheritance and closest verified implementation context are routing evidence, not automatic public Python class declarations. Exact descendant overrides, conditional compilation, initialization, cached PythonObject replacement, and target-version behavior remain unverified unless the linked type record supplies an explicit review.

| Native owner | Closest discovered ancestor binding | Reviewed implementation context | Registration evidence |
| --- | --- | --- | --- |
| [PartDesign::AdditiveBox](AdditiveBox.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeaturePrimitive.cpp:241` |
| [PartDesign::AdditiveCone](AdditiveCone.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeaturePrimitive.cpp:441` |
| [PartDesign::AdditiveCylinder](AdditiveCylinder.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeaturePrimitive.cpp:308` |
| [PartDesign::AdditiveEllipsoid](AdditiveEllipsoid.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeaturePrimitive.cpp:548` |
| [PartDesign::AdditiveHelix](AdditiveHelix.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeatureHelix.cpp:819` |
| [PartDesign::AdditiveLoft](AdditiveLoft.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeatureLoft.cpp:444` |
| [PartDesign::AdditivePipe](AdditivePipe.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeaturePipe.cpp:725` |
| [PartDesign::AdditivePrism](AdditivePrism.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeaturePrimitive.cpp:718` |
| [PartDesign::AdditiveSphere](AdditiveSphere.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeaturePrimitive.cpp:361` |
| [PartDesign::AdditiveTorus](AdditiveTorus.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeaturePrimitive.cpp:630` |
| [PartDesign::AdditiveWedge](AdditiveWedge.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeaturePrimitive.cpp:816` |
| [PartDesign::Boolean](Boolean.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeatureBoolean.cpp:50` |
| [PartDesign::Box](Box.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeaturePrimitive.cpp:186` |
| [PartDesign::Chamfer](Chamfer.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeatureChamfer.cpp:53` |
| [PartDesign::CircularPattern](CircularPattern.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeatureCircularPattern.cpp:13` |
| [PartDesign::Cone](Cone.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeaturePrimitive.cpp:365` |
| [PartDesign::CoordinateSystem](CoordinateSystem.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/PartDesign/App/DatumCS.cpp:41` |
| [PartDesign::Cylinder](Cylinder.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeaturePrimitive.cpp:245` |
| [PartDesign::Defeaturing](Defeaturing.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeatureDefeaturing.cpp:37` |
| [PartDesign::Draft](Draft.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeatureDraft.cpp:61` |
| [PartDesign::DressUp](DressUp.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeatureDressUp.cpp:53` |
| [PartDesign::Ellipsoid](Ellipsoid.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeaturePrimitive.cpp:444` |
| [PartDesign::FeatureAddSub](FeatureAddSub.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeatureAddSub.cpp:48` |
| [PartDesign::FeatureAddSubPython](FeatureAddSubPython.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeatureAddSub.cpp:206` |
| [PartDesign::FeatureAdditivePython](FeatureAdditivePython.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeatureAddSub.cpp:231` |
| [PartDesign::FeatureBase](FeatureBase.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeatureBase.cpp:40` |
| [PartDesign::FeatureExtrude](FeatureExtrude.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeatureExtrude.cpp:62` |
| [PartDesign::FeaturePrimitive](FeaturePrimitive.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeaturePrimitive.cpp:65` |
| [PartDesign::FeaturePython](FeaturePython.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/Feature.cpp:687` |
| [PartDesign::FeatureRefine](FeatureRefine.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeatureRefine.cpp:39` |
| [PartDesign::FeatureRefinePython](FeatureRefinePython.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeatureRefine.cpp:123` |
| [PartDesign::FeatureSubtractivePython](FeatureSubtractivePython.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeatureAddSub.cpp:241` |
| [PartDesign::Fillet](Fillet.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeatureFillet.cpp:48` |
| [PartDesign::Groove](Groove.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeatureGroove.cpp:40` |
| [PartDesign::Helix](Helix.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeatureHelix.cpp:64` |
| [PartDesign::Hole](Hole.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeatureHole.cpp:538` |
| [PartDesign::Line](Line.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/PartDesign/App/DatumLine.cpp:41` |
| [PartDesign::LinearPattern](LinearPattern.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeatureLinearPattern.cpp:54` |
| [PartDesign::Loft](Loft.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeatureLoft.cpp:95` |
| [PartDesign::Mirrored](Mirrored.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeatureMirrored.cpp:47` |
| [PartDesign::MultiTransform](MultiTransform.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeatureMultiTransform.cpp:45` |
| [PartDesign::Pad](Pad.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeaturePad.cpp:48` |
| [PartDesign::PathPattern](PathPattern.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeaturePathPattern.cpp:7` |
| [PartDesign::Pipe](Pipe.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeaturePipe.cpp:67` |
| [PartDesign::Plane](Plane.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/PartDesign/App/DatumPlane.cpp:41` |
| [PartDesign::Pocket](Pocket.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeaturePocket.cpp:49` |
| [PartDesign::Point](Point.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/PartDesign/App/DatumPoint.cpp:38` |
| [PartDesign::PointPattern](PointPattern.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeaturePointPattern.cpp:9` |
| [PartDesign::PolarPattern](PolarPattern.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeaturePolarPattern.cpp:49` |
| [PartDesign::Prism](Prism.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeaturePrimitive.cpp:634` |
| [PartDesign::ProfileBased](ProfileBased.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeatureSketchBased.cpp:89` |
| [PartDesign::Revolution](Revolution.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeatureRevolution.cpp:43` |
| [PartDesign::Revolved](Revolved.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeatureRevolved.cpp:59` |
| [PartDesign::Scaled](Scaled.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeatureScaled.cpp:41` |
| [PartDesign::ShapeBinder](ShapeBinder.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/PartDesign/App/ShapeBinder.cpp:62` |
| [PartDesign::Solid](Solid.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeatureSolid.cpp:33` |
| [PartDesign::Sphere](Sphere.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeaturePrimitive.cpp:312` |
| [PartDesign::SubShapeBinder](SubShapeBinder.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/PartDesign/App/ShapeBinder.cpp:346` |
| [PartDesign::SubShapeBinderPython](SubShapeBinderPython.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/PartDesign/App/ShapeBinder.cpp:1292` |
| [PartDesign::SubtractiveBox](SubtractiveBox.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeaturePrimitive.cpp:242` |
| [PartDesign::SubtractiveCone](SubtractiveCone.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeaturePrimitive.cpp:442` |
| [PartDesign::SubtractiveCylinder](SubtractiveCylinder.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeaturePrimitive.cpp:309` |
| [PartDesign::SubtractiveEllipsoid](SubtractiveEllipsoid.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeaturePrimitive.cpp:549` |
| [PartDesign::SubtractiveHelix](SubtractiveHelix.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeatureHelix.cpp:825` |
| [PartDesign::SubtractiveLoft](SubtractiveLoft.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeatureLoft.cpp:450` |
| [PartDesign::SubtractivePipe](SubtractivePipe.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeaturePipe.cpp:731` |
| [PartDesign::SubtractivePrism](SubtractivePrism.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeaturePrimitive.cpp:719` |
| [PartDesign::SubtractiveSphere](SubtractiveSphere.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeaturePrimitive.cpp:362` |
| [PartDesign::SubtractiveTorus](SubtractiveTorus.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeaturePrimitive.cpp:631` |
| [PartDesign::SubtractiveWedge](SubtractiveWedge.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeaturePrimitive.cpp:817` |
| [PartDesign::Thickness](Thickness.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeatureThickness.cpp:114` |
| [PartDesign::Torus](Torus.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeaturePrimitive.cpp:552` |
| [PartDesign::Transformed](Transformed.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeatureTransformed.cpp:66` |
| [PartDesign::Wedge](Wedge.md) | PartDesign::Feature -> PartDesign.Feature | Part::Feature | `src/Mod/PartDesign/App/FeaturePrimitive.cpp:722` |
