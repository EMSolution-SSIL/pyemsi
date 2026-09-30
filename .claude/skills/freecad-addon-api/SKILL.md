---
name: freecad-addon-api
description: Find and use FreeCAD Python APIs when developing or reviewing addons, scripted document objects, commands, and workbenches. Covers binding signatures, Python helpers and reexports, dynamic properties, and addon callback contracts.
---

# FreeCAD addon API

Use the bundled references to select APIs and implement addon behavior. The catalogue describes a source snapshot; it does not prove availability in an installed FreeCAD build.

## Choose references

Start with [the task index](references/index.md). Read only the relevant guide and symbol pages:

- [Runtime and version](references/runtime-and-version.md): environment, source evidence, compatibility, deprecations, and regeneration.
- [Runtime validation](references/runtime-validation.md): executable checks and results from the installed FreeCAD build.
- [Core API](references/core-api.md): documents, recompute, transactions, Base geometry values, and properties.
- [Object types](references/object-types.md): `Document.addObject` type strings, wrappers, dynamic properties, and discovery.
- [Native object catalogue](references/object-types/index.md): source-discovered document TypeIds, parent types, and C++ property registrations.
- [GUI and lifecycles](references/gui-and-lifecycles.md): commands, workbenches, feature/view proxies, observers, startup, and persistence.
- [Modeling API](references/modeling-api.md): Part, Sketcher, PartDesign, and Python workbench helpers.
- [Generated API index](references/api/index.md): exact module, class, method, property, and function declarations, plus source-derived descriptions.
- [Python API index](references/python-api/index.md): Python-defined helpers, source signatures, docstrings, reexports, and import conditions.

Search the generated catalogue for a fully qualified name or task keyword. Follow class bases and reexports when a member is inherited or aliased. Distinguish geometry values such as `Part.Shape` from document objects such as `Part.Feature`, and Python wrappers from native type strings such as `Part::FeaturePython`.

## Use evidence

Before writing a call, check its public import path, overload, return type, positional/keyword rules, and relevant preconditions. The source-adjacent `.pyi` imports and binding decorators describe generator inputs; they are not addon imports.

Treat callbacks as methods the addon implements, using the callback guide's trigger, arguments, and return meaning. A function catalogue alone is insufficient for proxy persistence and observer cleanup.

For dynamic properties, inspect the object-type guide and conversion contracts. An absent property or unresolved owner in static output does not mean the property is unavailable. Check the installed object or its C++ property registration when needed. Keep unknown signatures, descriptions, and availability explicit; do not infer them from an `Any` fallback or a plausible method name.

When source and installed behavior differ, target the user's FreeCAD version and verify the relevant API there. Keep GUI-dependent code conditional on GUI availability. Validate addon behavior in FreeCAD; successful static reference generation is not a runtime addon test.
