# `PartDesignGui` wrapper association audit

[Namespace index](index.md) | [Audit overview](../wrapper-review.md)

Every listed owner has no direct binding association in existing discovery. Native inheritance and closest verified implementation context are routing evidence, not automatic public Python class declarations. Exact descendant overrides, conditional compilation, initialization, cached PythonObject replacement, and target-version behavior remain unverified unless the linked type record supplies an explicit review.

| Native owner | Closest discovered ancestor binding | Reviewed implementation context | Registration evidence |
| --- | --- | --- | --- |
| [PartDesignGui::ViewProviderBody](ViewProviderBody.md) | PartGui::ViewProviderPartExt -> PartGui.ViewProviderPartExt | Gui::ViewProviderDocumentObject | `src/Mod/PartDesign/Gui/ViewProviderBody.cpp:76` |
| [PartDesignGui::ViewProviderBoolean](ViewProviderBoolean.md) | PartGui::ViewProviderPartExt -> PartGui.ViewProviderPartExt | Gui::ViewProviderDocumentObject | `src/Mod/PartDesign/Gui/ViewProviderBoolean.cpp:61` |
| [PartDesignGui::ViewProviderDatumCoordinateSystem](ViewProviderDatumCoordinateSystem.md) | Gui::ViewProviderGeometryObject -> FreeCADGui.ViewProviderGeometryObject | Gui::ViewProviderDocumentObject | `src/Mod/PartDesign/Gui/ViewProviderDatumCS.cpp:45` |
| [PartDesignGui::ViewProviderSubShapeBinder](ViewProviderSubShapeBinder.md) | PartGui::ViewProviderPartExt -> PartGui.ViewProviderPartExt | Gui::ViewProviderDocumentObject | `src/Mod/PartDesign/Gui/ViewProviderShapeBinder.cpp:240` |
