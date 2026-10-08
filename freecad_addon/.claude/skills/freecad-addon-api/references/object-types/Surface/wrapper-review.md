# `Surface` wrapper association audit

[Namespace index](index.md) | [Audit overview](../wrapper-review.md)

Every listed owner has no direct binding association in existing discovery. Native inheritance and closest verified implementation context are routing evidence, not automatic public Python class declarations. Exact descendant overrides, conditional compilation, initialization, cached PythonObject replacement, and target-version behavior remain unverified unless the linked type record supplies an explicit review.

| Native owner | Closest discovered ancestor binding | Reviewed implementation context | Registration evidence |
| --- | --- | --- | --- |
| [Surface::Cut](Cut.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/Surface/App/FeatureCut.cpp:33` |
| [Surface::Extend](Extend.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/Surface/App/FeatureExtend.cpp:49` |
| [Surface::FeatureBlendCurve](FeatureBlendCurve.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/Surface/App/Blending/FeatureBlendCurve.cpp:46` |
| [Surface::Filling](Filling.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/Surface/App/FeatureFilling.cpp:39` |
| [Surface::GeomFillSurface](GeomFillSurface.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/Surface/App/FeatureGeomFillSurface.cpp:128` |
| [Surface::Sections](Sections.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/Surface/App/FeatureSections.cpp:42` |
| [Surface::Sewing](Sewing.md) | Part::Feature -> Part.Feature | Part::Feature | `src/Mod/Surface/App/FeatureSewing.cpp:35` |
