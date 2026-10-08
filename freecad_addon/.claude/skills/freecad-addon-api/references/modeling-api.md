# Modeling API routing

Use [the generated catalogue](api/index.md) for exact stub signatures and overloads. It covers binding/typing output, including support types; it is not a complete runtime API guarantee. Confirm the installed FreeCAD version, build options and GUI availability before selecting an implementation.

## Part: shapes and document features

| Need | Load | Evidence in this checkout |
|---|---|---|
| Primitive solids, wires, faces; show/read/export shapes | [Part module](api/Part/index.md) | `src/Mod/Part/App/Part.module.pyi` |
| Shape operations, topology traversal, booleans, transformations | [Part.Shape](api/Part/Shape.md), then its linked continuation pages | `src/Mod/Part/App/TopoShape.pyi` |
| Curves and surfaces used to build geometry | [Part classes](api/Part/index.md) | Source-adjacent geometry binding `.pyi` files under `src/Mod/Part/App/` |
| Document object carrying a Shape and inherited object behavior | [Part.Feature](api/Part/Feature.md) and its base references | `src/Mod/Part/App/PartFeature.pyi` |
| Registered feature properties, e.g. Part::Box dimensions | Object-type catalogue from the main skill index, plus conversion contracts | `src/Mod/Part/App/FeaturePartBox.cpp`; `src/App/PropertyPythonContracts.pyi` |
| Shape repair / advanced OCC algorithms | [ShapeFix](api/Part/ShapeFix/index.md), [ShapeUpgrade](api/Part/ShapeUpgrade/index.md), [BRepOffsetAPI](api/Part/BRepOffsetAPI/index.md), [Geom2d](api/Part/Geom2d/index.md) | Matching public submodule stubs; optional runtime exposure remains to be checked |

`Part.makeBox(...)` returns a shape value. `Document.addObject("Part::Feature", ...)` creates a document object; assigning its `Shape` attaches geometry to that object. A shape factory alone does not define a persistent parametric feature or an `execute` callback. Use a document feature/proxy when the addon needs editable parameters and recomputation.

Source-backed illustrative pattern, not runtime-tested by this skill:

```python
import FreeCAD as App
import Part

doc = App.newDocument("Example")
feature = doc.addObject("Part::Feature", "Box")
feature.Shape = Part.makeBox(10.0, 20.0, 30.0)
doc.recompute()
```

Check whether a transformation mutates an existing value or returns a new value in its documented overload. Do not generalize behavior between similarly named shape and geometry methods. Inspect validity and the intended solid/shell/face result as appropriate to the operation. When storing face/edge references, investigate the repository's element-reference facilities and relevant topology-change tests; an index such as `Face1` alone does not establish stable identity across edits.

## Sketcher: geometry, constraints and solver results

Start with [Sketcher module](api/Sketcher/index.md), [SketchObject](api/Sketcher/SketchObject.md) and [Constraint](api/Sketcher/Constraint.md). Geometry primitives are supplied by `Part`; constraints use `Sketcher.Constraint` overloads whose argument meanings differ by constraint type. Do not select an overload merely because its argument count fits.

Create the document object using the registered string `Sketcher::SketchObject`. It is separate from the public wrapper/class name and from `Sketcher.Sketch`. Capture the geometry index returned by `addGeometry`; use the actual returned indices when adding constraints. Check endpoint positions, construction-geometry flags, datum units, return codes and solver state in the selected method's source/reference.

Source-backed illustrative pattern, not runtime-tested by this skill:

```python
import FreeCAD as App
import Part
import Sketcher

doc = App.newDocument("SketchExample")
sketch = doc.addObject("Sketcher::SketchObject", "Sketch")
index = sketch.addGeometry(
    Part.LineSegment(App.Vector(0, 0, 0), App.Vector(10, 0, 0))
)
sketch.addConstraint(Sketcher.Constraint("Horizontal", index))
doc.recompute()
```

Evidence: `src/Mod/Sketcher/SketcherTests/TestSketchValidateCoincidents.py` uses returned geometry indices, `Constraint("Horizontal", ...)`, `addConstraint`, and recomputation. `src/Mod/Sketcher/App/SketchObject.pyi` and `Constraint.pyi` declare the binding contracts. Search the Sketcher tests for the particular constraint or attachment scenario before constructing more complex sketches. A sketch may intentionally remain under-constrained; validation should match the addon's intended degrees of freedom.

## PartDesign: bodies and feature history

Start with [PartDesign.Body](api/PartDesign/Body.md), [PartDesign.Feature](api/PartDesign/Feature.md), their inherited [Part.BodyBase](api/Part/BodyBase.md) behavior, and [PartDesign module](api/PartDesign/index.md).

`PartDesign::Body`, `PartDesign::Pad`, and other creation strings refer to registered C++ document object types, not necessarily Python classes with matching names. Body membership, dependencies, `Tip`, profile links and recomputation must be handled together. Discover feature-specific properties through the object-type/source catalogue instead of fabricating constructors from a class listing. The Body binding explicitly documents that `insertObject` does not modify `Tip`, unlike `addObject`.

Evidence: `src/Mod/PartDesign/PartDesignTests/TestSketch.py` creates a body with `Document.addObject("PartDesign::Body", "Body")`, creates a sketch through `Body.newObject("Sketcher::SketchObject", "Sketch")`, sets attachment properties and recomputes. `TestPad.py`, `TestBaseFeature.py`, and `TestTopologicalNamingProblem.py` give concrete feature/dependency scenarios. Use the scenario relevant to the requested addon rather than treating a minimal isolated body as a complete PartDesign workflow.

## Other domains

Load the module reference first, then the specific class page or continuation linked there. These are source-discovered names, not verified imports for every distribution.

| Domain | References | Additional source route |
|---|---|---|
| Mesh creation/manipulation and shape conversion | [Mesh](api/Mesh/index.md), [MeshPart](api/MeshPart/index.md) | `src/Mod/Mesh/`, `src/Mod/MeshPart/` |
| Spreadsheet cells, expressions and aliases | [Spreadsheet](api/Spreadsheet/index.md) | `src/Mod/Spreadsheet/` |
| Drawing pages/views and export | [TechDraw](api/TechDraw/index.md) | `src/Mod/TechDraw/` |
| FEM objects and GUI integration | [Fem](api/Fem/index.md), [FemGui](api/FemGui/index.md) | `src/Mod/Fem/`; solver helpers are often Python |
| Assembly objects and links | [Assembly](api/Assembly/index.md) | `src/Mod/Assembly/` |
| Toolpaths and simulation | [PathApp](api/PathApp/index.md), [PathGui](api/PathGui/index.md), [CAM](api/CAM/index.md) | `src/Mod/CAM/`; source can retain Path names |
| Material data | [Materials](api/Materials/index.md) | `src/Mod/Material/` |
| File import/export | [Import](api/Import/index.md), [ImportGui](api/ImportGui/index.md) | `src/Mod/Import/` and format-specific workbenches |
| Units and placement | [FreeCAD.Units](api/FreeCAD/Units/index.md), [Base classes](api/FreeCAD/Base/index.md) | `src/Base/`, `src/App/FreeCADInit.py` |

Do not assume all angles use the same unit because two signatures accept `float`; inspect the contract for the exact method. GUI modules and GUI exporters require a suitable GUI-enabled environment.

## Python APIs outside the binding catalogue

Use the [Python-defined API catalogue](python-api/index.md) and [its guide](python-api-guide.md) for source-backed functions, classes, aliases and guarded reexports in selected Draft, BIM, Part, FEM, TechDraw, Sketcher and CAM modules, plus `src/Ext/freecad`. This catalogue supplements the binding output; it does not prove installed imports or promote every source-defined helper to stable addon API.

The existing generator primarily inventories C++ bindings and curated typing inputs, plus selected bootstrap exports. It does not catalogue every public Python function in the workbenches or `src/Ext/freecad`.

For Draft, trace imports/reexports in `src/Mod/Draft/Draft.py` to `draftmake`, `draftfunctions`, `draftobjects`, and `draftviewproviders`. Several view providers are imported only when the GUI is available. `Draft.make_line` is reexported from `src/Mod/Draft/draftmake/make_line.py`; the latter documents accepted inputs and keeps a deprecated `makeLine` wrapper with lifecycle metadata. Inspect the snake-case implementation and deprecation metadata before selecting the legacy spelling. `DraftUtils` in the binding catalogue is not a substitute for the Python `Draft` module.

The lowercase `freecad` namespace is installed from `src/Ext/freecad/__init__.py.template`, which imports `FreeCAD` as `app` and extends the namespace path. Its `part.py`, `partdesign.py`, and `sketcher.py` reexport their corresponding extension modules. Other helpers include `deprecation.py`, `module_io.py`, `project_utility.py`, `utils.py` and the GUI-dependent `UiTools.py`. These paths establish where to inspect code; they do not independently declare that every helper is stable addon API.

For a Python function absent from the catalogue, record its public import/reexport path, actual definition, signature/docstring, GUI guards, deprecation and side effects from the source. Inspect callers or repository tests to understand arguments not explained by the docstring. Runtime checks should happen inside FreeCAD or an explicitly configured FreeCAD Python environment; a system Python import failure alone does not show that the API is absent.

## Regeneration and evidence

Run from a matching source checkout:

```sh
python -B contrib/skills/freecad-addon-api/scripts/build_references.py --root .
python -B contrib/skills/freecad-addon-api/scripts/test_build_references.py
```

To reuse existing import-shaped stubs, add `--stubs-dir path/to/stubs`. This mode records that their original revision is unverified. Fresh generation reuses `src/Tools/typing/generate_stubs.py`, then renders Markdown with stdlib AST parsing. The generated index records checkout HEAD/version, a content hash, counts and coverage limits. Its stub line numbers identify input declarations; they are not invented C++ implementation mappings. Overload variants, getter/setter pairs, imported aliases, adjacent field docs and nested classes are retained. Unexpected non-typing conditionals cause an explicit generation error instead of silently merging runtime alternatives.

The fixture check verifies these rendering contracts and cleanup boundaries. It does not validate the accuracy of upstream types, runtime imports or modeling examples. Improve authoritative source `.pyi` inputs/conversion contracts when correcting binding information, then regenerate; hand-written workflow guidance belongs here rather than in generated pages.
