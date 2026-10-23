# `Gui` wrapper association audit

[Namespace index](index.md) | [Audit overview](../wrapper-review.md)

Every listed owner has no direct binding association in existing discovery. Native inheritance and closest verified implementation context are routing evidence, not automatic public Python class declarations. Exact descendant overrides, conditional compilation, initialization, cached PythonObject replacement, and target-version behavior remain unverified unless the linked type record supplies an explicit review.

| Native owner | Closest discovered ancestor binding | Reviewed implementation context | Registration evidence |
| --- | --- | --- | --- |
| [Gui::ViewProviderAnnotation](ViewProviderAnnotation.md) | Gui::ViewProviderDocumentObject -> FreeCADGui.ViewProviderDocumentObject | Gui::ViewProviderDocumentObject | `src/Gui/ViewProviderAnnotation.cpp:127` |
| [Gui::ViewProviderAnnotationLabel](ViewProviderAnnotationLabel.md) | Gui::ViewProviderDocumentObject -> FreeCADGui.ViewProviderDocumentObject | Gui::ViewProviderDocumentObject | `src/Gui/ViewProviderAnnotation.cpp:327` |
| [Gui::ViewProviderDragger](ViewProviderDragger.md) | Gui::ViewProviderDocumentObject -> FreeCADGui.ViewProviderDocumentObject | Gui::ViewProviderDocumentObject | `src/Gui/ViewProviderDragger.cpp:59` |
| [Gui::ViewProviderFeature](ViewProviderFeature.md) | Gui::ViewProviderDocumentObject -> FreeCADGui.ViewProviderDocumentObject | Gui::ViewProviderDocumentObject | `src/Gui/ViewProviderFeature.cpp:32` |
| [Gui::ViewProviderImagePlane](ViewProviderImagePlane.md) | Gui::ViewProviderGeometryObject -> FreeCADGui.ViewProviderGeometryObject | Gui::ViewProviderDocumentObject | `src/Gui/ViewProviderImagePlane.cpp:56` |
| [Gui::ViewProviderPart](ViewProviderPart.md) | Gui::ViewProviderGeometryObject -> FreeCADGui.ViewProviderGeometryObject | Gui::ViewProviderDocumentObject | `src/Gui/ViewProviderPart.cpp:47` |
| [Gui::ViewProviderTextDocument](ViewProviderTextDocument.md) | Gui::ViewProviderDocumentObject -> FreeCADGui.ViewProviderDocumentObject | Gui::ViewProviderDocumentObject | `src/Gui/ViewProviderTextDocument.cpp:42` |
