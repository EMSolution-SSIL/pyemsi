# Runtime, version, and evidence

## Source snapshot versus installed API

The initial investigation used FreeCAD revision `3160daf1e2` (`version.json`: `26.3.0-dev`). Inspect the generated [API index](api/index.md) for the catalogue's current generation metadata and supplied-stub provenance. A version number alone does not identify local modifications, build options, or the original revision of an externally supplied stub tree.

Inside FreeCAD's Python environment:

```python
import FreeCAD as App

print(App.Version())
print("GUI available:", bool(App.GuiUp))
if App.ActiveDocument is not None:
    print(App.ActiveDocument.supportedTypes())
```

Import `FreeCADGui` and use view providers only when the task has a GUI environment. `DocumentObject.ViewObject` may be `None` without the GUI. Ordinary system Python does not necessarily load FreeCAD's compiled modules; use FreeCAD's Python console or an appropriately configured FreeCAD Python runtime for behavioral checks.

`supportedTypes()` reports registered document-object types in that environment; imported modules and build options can affect the result. It can include abstract types, so membership is not proof that a type is constructible. On a particular object, inspect `TypeId`, `isDerivedFrom(...)`, `PropertiesList`, `getTypeIdOfProperty(...)`, and `supportedProperties()` to resolve its native type and property behavior. See the object-type guide for the distinction between supported property *types* and installed property *names*.

## Where evidence comes from

| Question | Evidence in the checkout |
| --- | --- |
| Public name and alias | Export registrations in C++, `@export(PythonName=...)`, merged public stubs |
| Declared signature and explanation | Binding `.pyi`, `*.module.pyi`, curated type stubs, Python definitions and their docstrings |
| Runtime argument parsing, mutation, errors | Corresponding `*PyImp.cpp`, module callback implementations, or Python function body |
| Inheritance and native object type | C++ TypeId registrations; `src/Tools/typing/stubgen/type_hierarchy.py` |
| Dynamic property declaration | C++ `ADD_PROPERTY*` calls and inheritance; Python `addProperty` calls |
| Property getter/setter conversion | Owning `PropertyPythonContracts.pyi` plus C++ conversion implementation |
| Callback trigger and arguments | C++ dispatch implementation, corroborated by current Python callers/tests |
| Bootstrap and reexports | `src/App/FreeCADInit.py`, `src/Gui/FreeCADGuiInit.py`, package entrypoints |

Use source paths from the guides relative to the checkout provided for the task. Generated pages cite their input stub; they do not fabricate a direct C++ source mapping. `Any`, variadic fallbacks, undocumented declarations, typing helpers, and inferred module mappings remain incomplete evidence.

Assignment values in binding specifications can be placeholders; check the implementation before treating them as runtime defaults. A concrete discrepancy in this revision is `Document.UndoMode`: the source `.pyi` declares `0` with a legacy mode description, but `DocumentPy::getUndoMode` returns `1` unconditionally and its setter does nothing (`src/App/DocumentPyImp.cpp:980`). Do not infer a working undo toggle from that declaration. This finding is revision-specific; review the target runtime when compatibility with another release matters.

The generator deliberately omits cases it cannot type. In the initial run it found 1,292 C++ dynamic properties and emitted 257; 1,023 had unresolved owners and 12 had unresolved conversion contracts. These are static coverage diagnostics, not evidence that those properties are inaccessible. Pure Python workbench APIs and callback contracts also require the dedicated guides and source inspection.

The [native supplement](object-types/index.md) retains all 1,292 discovered properties. Its [conversion audit](object-types/conversion-review.md) reviews all 43 occurrences lacking conversion metadata across 20 property families, while preserving the upstream missing-metadata count. One reviewed conversion depends on VTK build support and one has no supported Python counterpart. [Wrapper reviews](object-types/wrapper-review.md) provide ancestor/implementation context for all 370 missing direct associations without inventing descendant Python classes. Reviewed evidence is hash-checked on regeneration and withheld when its sources change.

## Deprecations

Source decorators carry structured `deprecated_in`, `removed_in`, `replacement`, and optional `details` fields. Generated public stubs convert these to standard deprecation decorators; their rendered messages retain lifecycle guidance. Prefer the replacement when it meets the user's target version and behavior.

From a checkout root, use the existing inventory without importing FreeCAD:

```sh
python -B -m src.Tools.python_api check
python -B -m src.Tools.python_api list
python -B -m src.Tools.python_api list --remove-by 27.2
```

The last command is an example filter for APIs scheduled for removal by release 27.2, not the skill's target version. The initial checkout check found 80 deprecations and zero metadata errors. Consult `src/Tools/python_api/README.md`; the manifest is a disposable index, not a second source of truth. Resolve a reported name against its actual exports and caller context before changing an addon.

## Refreshing and checking the references

Use `scripts/build_references.py --help` for generation options. The renderer reuses the existing `src/Tools/typing/generate_stubs.py` pipeline when fresh bindings are needed; a supplied `--stubs-dir` is a cache input whose original revision must be checked separately. Run from the checkout root or pass its path with `--root`. Generated references are shipped with the skill for reading without the checkout; regeneration needs that checkout.

Use `scripts/build_object_types.py --help` to refresh the separate native object/property catalogue from the checkout. It reuses the existing type hierarchy and C++ property discovery helpers; extensions and properties added dynamically by Python still need runtime/source inspection.

Use `scripts/build_python_api.py --help` to refresh the Python source catalogue. Its index describes the selected module coverage and static export limitations. None of these catalogue builders imports FreeCAD.

Keep curated lifecycle/task guidance separate from the generated catalogue subtrees. Review renamed/removed symbols, unknown signatures, unresolved dynamic properties, and Python export changes when refreshing. For source-side documentation checks, the existing command is:

```sh
python -B src/Tools/typing/generate_stubs.py lint-docs --root .
```

That linter covers curated module/type inputs, not every binding or runtime API. The stub generator's `check` mode also runs external type checkers and requires their configured tool environment. Its smoke target is intentionally never executed as an addon test.

Validate behavior appropriate to the change in the target FreeCAD runtime: geometry creation/recompute for modeling, activation for GUI commands, save/reopen for proxy persistence, and add/remove for observers. A successful catalogue build or syntax check does not establish these runtime behaviors.

See [runtime validation](runtime-validation.md) for the bundled smoke check, tested build, results, and explicit skips. The installed build and this source checkout can have different versions; successful checks cover their tested operations, not every catalogue entry.
