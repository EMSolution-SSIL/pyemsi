# `Path` wrapper association audit

[Namespace index](index.md) | [Audit overview](../wrapper-review.md)

Every listed owner has no direct binding association in existing discovery. Native inheritance and closest verified implementation context are routing evidence, not automatic public Python class declarations. Exact descendant overrides, conditional compilation, initialization, cached PythonObject replacement, and target-version behavior remain unverified unless the linked type record supplies an explicit review.

| Native owner | Closest discovered ancestor binding | Reviewed implementation context | Registration evidence |
| --- | --- | --- | --- |
| [Path::Feature](Feature.md) | App::GeoFeature -> FreeCAD.GeoFeature | App::GeoFeature | `src/Mod/CAM/App/FeaturePath.cpp:32` |
| [Path::FeatureAreaPython](FeatureAreaPython.md) | Path::FeatureArea -> CAM.FeatureArea | Part::Feature | `src/Mod/CAM/App/FeatureArea.cpp:290` |
| [Path::FeatureAreaView](FeatureAreaView.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/CAM/App/FeatureArea.cpp:179` |
| [Path::FeatureAreaViewPython](FeatureAreaViewPython.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/CAM/App/FeatureArea.cpp:291` |
| [Path::FeatureCompound](FeatureCompound.md) | App::GeoFeature -> FreeCAD.GeoFeature | App::GeoFeature | `src/Mod/CAM/App/FeaturePathCompound.cpp:33` |
| [Path::FeatureCompoundPython](FeatureCompoundPython.md) | App::GeoFeature -> FreeCAD.GeoFeature | App::GeoFeature | `src/Mod/CAM/App/FeaturePathCompound.cpp:129` |
| [Path::FeaturePython](FeaturePython.md) | App::GeoFeature -> FreeCAD.GeoFeature | App::GeoFeature | `src/Mod/CAM/App/FeaturePath.cpp:67` |
| [Path::FeatureShape](FeatureShape.md) | App::GeoFeature -> FreeCAD.GeoFeature | App::GeoFeature | `src/Mod/CAM/App/FeaturePathShape.cpp:34` |
| [Path::FeatureShapePython](FeatureShapePython.md) | App::GeoFeature -> FreeCAD.GeoFeature | App::GeoFeature | `src/Mod/CAM/App/FeaturePathShape.cpp:91` |
