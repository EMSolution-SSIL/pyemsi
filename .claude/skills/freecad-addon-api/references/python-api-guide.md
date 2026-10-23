# Python-defined addon APIs

The [Python catalogue](python-api/index.md) supplements the [C++ binding catalogue](api/index.md). Use it for workbench functions, Python classes/proxies, utilities and namespace reexports whose implementation lives in `.py` files. It is generated from selected source modules without importing FreeCAD or executing decorators.

## Route by task

| Need | Start here | What to inspect |
|---|---|---|
| Draft object creation and editing | [Draft facade](python-api/Draft/index.md) | Follow its explicit imports to `draftmake` and `draftfunctions`; use snake-case names when legacy wrappers declare replacements |
| Draft shape and vector operations | [DraftGeomUtils](python-api/DraftGeomUtils/index.md), [DraftVecUtils](python-api/DraftVecUtils/index.md) | Shape versus document-object parameters, tolerances, mutating behavior and units |
| Working planes | [WorkingPlane](python-api/WorkingPlane/index.md) | Class methods, placement conventions and GUI dependencies |
| Architectural/BIM factories | [Arch](python-api/Arch/index.md) | Active-document prerequisites and factory docstrings; wildcard targets remain separate source pages |
| Lowercase namespace / package helpers | [freecad](python-api/freecad/index.md), [deprecation](python-api/freecad/deprecation/index.md), [module_io](python-api/freecad/module_io/index.md) | Namespace initialization, extension-module reexports and helper signatures |
| Python shape builders / booleans | [BasicShapes.Shapes](python-api/BasicShapes/Shapes/index.md), [BOPTools.SplitAPI](python-api/BOPTools/SplitAPI/index.md), [BOPTools.JoinAPI](python-api/BOPTools/JoinAPI/index.md) | Pure shape operations versus document features and GUI commands |
| FEM document factories and analysis helpers | [ObjectsFem](python-api/ObjectsFem/index.md), [femtools.femutils](python-api/femtools/femutils/index.md) | Factory parameters, document ownership, solver/setup prerequisites |
| FEM mesh/result processing | [meshtools](python-api/femmesh/meshtools/index.md), [resulttools](python-api/femresult/resulttools/index.md) | Node/element conventions and expected result object shapes |
| CAM geometry, jobs and stock | [Path.Geom](python-api/Path/Geom/index.md), [Path.Main.Job](python-api/Path/Main/Job/index.md), [Path.Main.Stock](python-api/Path/Main/Stock/index.md) | Toolpath values versus document features, machine units and GUI-dependent setup |
| TechDraw commands/helpers or sketch profiles | [TechDrawTools](python-api/TechDrawTools/index.md), [ProfileLib](python-api/ProfileLib/index.md) | Follow the full catalogue index to selected child modules; commands require GUI availability |

The full index lists every selected module and each continuation page. Class pages are linked from their defining module. Imported aliases show a qualified bound name and original module/name, preserving alternate spellings. Source-relative file paths and line numbers provide evidence when the bundled skill is used away from the checkout.

## Read exposure and conditions correctly

- **Facade reexport declaration:** Draft, DraftGeomUtils or Arch exposes this source import. Follow the target source page for its definition. Support imports such as typing/deprecation helpers are labeled as dependencies. A facade alone does not establish version compatibility.
- **Listed in literal `__all__`:** a single unconditional literal export list contains the name. Conditional assignments, reassignment, augmentation or mutating calls make the list unresolved; the renderer does not union alternative exports.
- **Source-defined name:** the function, class, alias or constant is present in the selected module. A public-looking spelling does not independently establish a stable addon contract.
- **Internal definition:** private module definitions are listed briefly rather than expanded. Selected protocol/constructor dunder methods on public classes are retained. Private imported aliases remain visible in import evidence, preserving compatibility history without promoting them as supported API.

Conditional imports and declarations keep their `if`/`else`, `try`/`except`, or dynamic-block evidence. For example, Draft view providers imported under `if App.GuiUp` are available only when that branch executes successfully. A `try` import may select a fallback, and wildcard reexports depend on the target's actual export state. Do not treat alternatives shown in a page as simultaneously available.

Decorator source expressions retain deprecation versions, replacement names, property accessors and other wrapping behavior. The renderer does not execute a decorator, prove that the final runtime signature matches the undecorated source, or infer units/return types where annotations are absent. Getter and setter declarations are shown separately with their own source docs; copied descriptions can still require implementation review.

## What the catalogue does not establish

The selection favors addon-facing facades, factories, geometry utilities and direct reexport source modules. It includes some GUI commands/view providers because the selected facades expose them; it omits unrelated GUI/test internals and arbitrary transitive dependencies. The complete file selection is explicit in `scripts/build_python_api.py`.

Nested classes and function-local definitions, dynamically installed APIs, wildcard member enumeration, arbitrary alias-chain resolution and dynamic instance properties are not inventoried here. Source imports also depend on FreeCAD's startup search paths and installed build. The lowercase `freecad` initializer is a template; its configured library path is supplied during installation, not inferred by this skill.

Use the [object-type catalogue](object-types/index.md) for C++ registered properties and the [callback guide](gui-and-lifecycles.md) when implementing proxies/commands. For a missing Python API, inspect its actual source, facade reexports, initialization and callers; absence from this selected catalogue is not evidence of runtime absence.

## Update and verify

```sh
python -B contrib/skills/freecad-addon-api/scripts/build_python_api.py --root .
python -B contrib/skills/freecad-addon-api/scripts/test_build_python_api.py
```

`--root` selects the source checkout even when the skill is installed elsewhere. Generated output stays in this skill's `references/python-api/`. The index/manifest record checkout HEAD, selected-source hash, source paths and declaration counts. HEAD does not capture local modifications, and none of these identifiers validates runtime behavior.

The fixture verifies alias paths, package-relative imports, guards/fallbacks, signatures, source docs, lifecycle decorators and export-list conservatism. Validate the relevant addon behavior in the target FreeCAD installation separately.
