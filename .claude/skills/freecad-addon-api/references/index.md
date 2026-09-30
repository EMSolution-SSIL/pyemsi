# Find the API for an addon task

Use the guide for the behavior, then the generated catalogue for the declaration. Source locations in these guides are relative to a FreeCAD checkout root.

| Task | Read first | Catalogue search terms |
| --- | --- | --- |
| Create or modify document objects | [Core API](core-api.md), [object types](object-types.md) | `FreeCAD.Document`, `addObject`, `DocumentObject` |
| Add properties, links, quantities, expressions | [Core API](core-api.md), [object types](object-types.md) | `addProperty`, `PropertyContainer`, `Quantity`, `setExpression` |
| Recompute, manage dependencies, support undo | [Core API](core-api.md) | `recompute`, `touch`, `openTransaction`, `commitTransaction`, `abortTransaction` |
| Create or inspect geometry | [Modeling API](modeling-api.md) | `Part.makeBox`, `Part.Shape`, `Part.Face`, `Part.Wire` |
| Build sketches or PartDesign features | [Modeling API](modeling-api.md), [object types](object-types.md) | `Sketcher.SketchObject`, `Constraint`, `PartDesign::Body`, `PartDesign::Pad` |
| Implement parametric behavior, save and reopen it | [GUI and lifecycles](gui-and-lifecycles.md) | `FeaturePython`, `execute`, `onChanged`, `onDocumentRestored`, `Proxy` |
| Register a command or workbench | [GUI and lifecycles](gui-and-lifecycles.md) | `FreeCADGui.addCommand`, `Workbench`, `addWorkbench` |
| Read selection, selected faces, or edges | [GUI and lifecycles](gui-and-lifecycles.md) | `Selection.getSelectionEx`, `SelectionObject`, `SubElementNames` |
| Customize appearance, editing, task dialogs | [GUI and lifecycles](gui-and-lifecycles.md) | `ViewProvider`, `FreeCADGui.Control`, `setEdit` |
| Observe document or selection changes | [GUI and lifecycles](gui-and-lifecycles.md) | `addDocumentObserver`, `removeDocumentObserver`, `Selection.addObserver` |
| Use preferences or logging | [Core API](core-api.md) | `FreeCAD.ParamGet`, `ParameterGrp`, `FreeCAD.Console` |
| Import/export, mesh, drawing, spreadsheet, FEM, materials, assembly, CAM | [Modeling API](modeling-api.md), [API index](api/index.md) | `Import`, `Mesh`, `TechDraw`, `Spreadsheet`, `Fem`, `Materials`, `Assembly`, `PathApp` |
| Use Draft, Arch, FEM, or other Python helpers | [Python API index](python-api/index.md), [Modeling API](modeling-api.md) | `Draft.make_line`, `ObjectsFem`, `freecad`, the module or function name |
| Test an addon in the installed FreeCAD | [Runtime validation](runtime-validation.md) | `check_runtime.py`, recompute, undo/redo, proxy persistence, observer cleanup |
| Resolve an unavailable API or deprecated name | [Runtime and version](runtime-and-version.md) | `deprecated`, `Any`, the exact symbol name |

For an exact symbol, search `references/api` for bindings or `references/python-api` for Python definitions and reexports. For native TypeIds and C++ property registrations, use the [native object catalogue](object-types/index.md). Optional/private-looking modules in static output need their source export and installed availability checked before using them in an addon.
