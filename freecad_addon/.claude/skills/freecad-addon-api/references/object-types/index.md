# Native object and property catalogue

Generated from checkout HEAD `3160daf1e2b62b0472854da4848255c6b3ad554c`, version `26.3.0-dev`, using current local source. HEAD alone does not identify uncommitted source changes. This full inventory is not runtime-verified; separate smoke checks are recorded in [runtime validation](../runtime-validation.md).

Discovery: 1035 native registrations, 380 DocumentObject descendants (including abstract types), 1292 C++ registered properties across 428 catalogued owners. 43 properties have unresolved conversion metadata; 370 owners lack a direct source binding association.

[Conversion gap audit](conversion-review.md): 43 occurrences have current source reviews; 0 remain unaudited/stale. 1 depend on optional build support and 1 have no supported Python counterpart. Upstream missing-metadata count is preserved. [Wrapper audit](wrapper-review.md) records all direct-association gaps with conservative ancestor/implementation context; 0 have no manually verified implementation context.

## Limits and use

- Follow namespace/type records and native parent links for inherited properties. This inventory also retains properties on non-document owners (such as extensions and view providers), marked accordingly.
- Abstract registration and available source are not promises of constructibility in a running build. Native TypeIds are not Python import paths.
- Discovery reuses `src/Tools/typing/stubgen/type_hierarchy.py` and `cpp_properties.py`. All properties returned by that helper are retained, including those omitted from public stubs for unresolved wrapper ownership. Its diagnostics retain skipped/unscoped registrations.
- Extension attachment and instance-specific Python addProperty calls are not flattened into this static catalogue. Zero discovered direct properties does not establish zero available properties.
- Public associations come from existing binding discovery. Manual handwritten implementations and nearest discovered ancestors are separate evidence, not automatic descendant type claims.
- Conversion expressions normally come from PropertyPythonContracts.pyi metadata and native inheritance; source-review exceptions are marked per row. Nested helper aliases are defined in [conversion aliases](conversion-aliases.md). Metadata may omit valid runtime inputs; registration descriptions are source text.
- See [object discovery guidance](../object-types.md) and [core property guidance](../core-api.md) for safe runtime inspection, copies, units, and editor status.

## Namespaces

- [App](App/index.md): 39 owners
- [Assembly](Assembly/index.md): 8 owners
- [Fem](Fem/index.md): 57 owners
- [FemGui](FemGui/index.md): 4 owners
- [Gui](Gui/index.md): 10 owners
- [Image](Image/index.md): 1 owners
- [Inspection](Inspection/index.md): 2 owners
- [InspectionGui](InspectionGui/index.md): 1 owners
- [Measure](Measure/index.md): 12 owners
- [MeasureGui](MeasureGui/index.md): 3 owners
- [Mesh](Mesh/index.md): 27 owners
- [MeshGui](MeshGui/index.md): 3 owners
- [Part](Part/index.md): 70 owners
- [PartDesign](PartDesign/index.md): 76 owners
- [PartDesignGui](PartDesignGui/index.md): 4 owners
- [PartGui](PartGui/index.md): 3 owners
- [Path](Path/index.md): 10 owners
- [PathGui](PathGui/index.md): 1 owners
- [Points](Points/index.md): 5 owners
- [PointsGui](PointsGui/index.md): 1 owners
- [Robot](Robot/index.md): 5 owners
- [RobotGui](RobotGui/index.md): 1 owners
- [Sketcher](Sketcher/index.md): 3 owners
- [SketcherGui](SketcherGui/index.md): 1 owners
- [Spreadsheet](Spreadsheet/index.md): 2 owners
- [Surface](Surface/index.md): 7 owners
- [TechDraw](TechDraw/index.md): 57 owners
- [TechDrawGui](TechDrawGui/index.md): 15 owners

## Discovery diagnostics

No discovery diagnostics.

Diagnostics appear on the corresponding owner records; unresolved conversion counts are separate.

## Regenerate

```sh
python -B contrib/skills/freecad-addon-api/scripts/build_object_types.py --root .
python -B contrib/skills/freecad-addon-api/scripts/test_build_object_types.py
```

In the repository layout, `--root` defaults to this script's checkout. When copying/installing the skill elsewhere, pass `--root /path/to/FreeCAD` explicitly. Output is fixed to this skill's references/object-types directory; only obsolete previously listed Markdown pages are removed. No FreeCAD runtime or third-party dependencies are required.
