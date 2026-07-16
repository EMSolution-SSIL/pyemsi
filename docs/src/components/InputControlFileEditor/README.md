# InputControlFileEditor architecture and feature guide

This document explains the purpose, behavior, internal structure, and extension points of the `InputControlFileEditor` component. It is written primarily for AI coding agents and maintainers who need to change the editor without breaking document synchronization or discarding EMSolution data.

## Purpose

`InputControlFileEditor` is a browser-only editor for EMSolution input control files. It combines a general Monaco-based structured-data editor with guided editors for EMSolution's `16_Material_Properties` and `17_Field_Source` definitions.

The component is designed to:

- open and edit one or more JSON input control files locally in the browser;
- represent a document as JSON, YAML, or compatible TOML while retaining one canonical JSON-compatible value;
- compare two open documents in a split view;
- navigate nested structures with cursor-aware breadcrumbs;
- save back to a selected file when the browser provides a writable file handle, or download JSON as a fallback;
- provide a schema-driven Field Source editor for recognized EMSolution inputs;
- provide a context-aware Material Properties editor for volume and surface materials;
- preserve unknown properties and unsupported definitions instead of silently deleting them.

This component does not upload files to a server. Browser security may prevent it from knowing the original full path of a selected file.

## Non-negotiable invariants

Changes to this component should preserve these rules:

1. `OpenDocument.canonicalValue` is the shared JSON-compatible representation used to synchronize formats and guided editors.
2. `OpenDocument.text` is the JSON text that will be saved, even when another representation is currently visible.
3. Valid YAML or TOML edits must update the canonical value and regenerate the JSON draft.
4. Invalid alternate-format drafts must not overwrite the last valid canonical value.
5. Guided Field Source edits must be staged against a deep clone and applied only through `updateCanonicalDocument`.
6. Unknown properties must survive normal guided editing and normalization.
7. Unsupported Field Source entries must remain raw-editable.
8. Validation warnings are advisory; structural errors block the Field Source modal's Apply action.
9. The focused split pane is the target of toolbar actions. If no comparison pane is focused, the primary document is used.
10. Files are saved as JSON. YAML and TOML comments are not preserved in the JSON save result.
11. Guided Material Property edits use a deep-cloned staged `16_Material_Properties` object and apply only through `updateCanonicalDocument`.
12. Missing Material Properties are editable, but an existing malformed root or non-array material collection disables the guided action.
13. Optional `MAT_NAME`, legacy nonlinear-parameter spelling, vendor fields, and unsupported material structures must survive guided edits.
14. Material validation warnings are advisory; structural errors block Apply.

## High-level data flow

```text
File / drag-and-drop
        |
        v
JSON FormatDraft ----parse----> canonicalValue
        ^                            |
        |                            +----serialize----> YAML FormatDraft
        |                            |
        |                            +----serialize----> TOML FormatDraft
        |                            |
        |                            +----deep clone----> Guided modal
        |                                                  |
        +--------- updateCanonicalDocument <----Apply------+
        |
        v
JSON file handle write or browser download
```

The canonical value is updated only after a representation parses successfully or a guided modal applies a valid staged value.

## Module map

| File | Responsibility |
| --- | --- |
| `index.tsx` | Browser-only Docusaurus boundary and lazy loading. Prevents Monaco and browser APIs from running during server rendering. |
| `InputControlFileEditorClient.tsx` | Main application state, file opening, tabs, split view, format switching, Monaco integration, saving, dirty state, fullscreen mode, and modal orchestration. |
| `structuredFormats.ts` | JSON/YAML/TOML parsing, serialization, formatting, symbol generation, and TOML/JSON compatibility checks. |
| `jsonSymbols.ts` | Structured symbol trees, cursor trails, breadcrumb data, unique display names, and browser-window titles. |
| `emSolutionModel.ts` | Shared EMSolution detection, plain-object checks, deep cloning, and `SERIES_ID`/`TIME_ID` reference collection. |
| `fieldSourceModel.ts` | Supported Field Source schemas, defaults, conditional fields, nested-row schemas, entry inspection, immutable replacement, normalization, summaries, and validation. |
| `FieldSourceEditorModal.tsx` | Unified Field Source master/detail workflow, source CRUD, nested-row CRUD, raw JSON repair, confirmation behavior, staging, and Apply/Cancel handling. |
| `materialPropertyModel.ts` | Material schemas, context-aware defaults, immutable helpers, surface-type inspection, legacy aliases, summaries, and validation. |
| `MaterialPropertyEditorModal.tsx` | Unified General/Volume/Surface material workflow, CRUD, optional property groups, raw repair, staging, and Apply/Cancel handling. |
| `networkModel.ts` | NETWORK component schemas, immutable transformations, reference discovery, normalization, summaries, and validation. |
| `NetworkEditorModal.tsx` | Reusable NETWORK component editor. It can render as a standalone modal or as an embedded panel inside the Field Source modal. |
| `circuitModel.ts` | CIRCUIT series and power-supply transformations, matrix conversion/remapping, normalization, and validation. |
| `CircuitEditorModal.tsx` | Reusable CIRCUIT editor for source series, power supplies, symmetric matrices, and connection matrices. |
| `EditorIcon.tsx` | Shared inline SVG icon set. |
| `styles.module.css` | Styling for the editor shell, panes, tabs, breadcrumbs, modals, tables, matrices, validation states, and responsive layouts. |
| `*.test.ts` / `*.test.tsx` | Model and integration coverage. |

## Main document state

### `OpenDocument`

Each open file has an `OpenDocument` record in `InputControlFileEditorClient.tsx`.

Important fields:

- `id`: stable in-memory identity used by Monaco model URIs and React state;
- `name`: original filename;
- `displayName`: unique tab label when files share a filename;
- `text`: current JSON save payload;
- `savedText`: last successfully saved JSON payload, used for dirty-state detection;
- `revision`: canonical revision counter;
- `activeFormat`: `json`, `yaml`, or `toml`;
- `canonicalValue`: the last valid JSON-compatible value, or `undefined` when JSON is invalid;
- `formatDrafts`: lazily created per-format Monaco drafts;
- `handle`: optional File System Access API handle used for direct writes.

### `FormatDraft`

A format draft contains:

- editable `text`;
- `lastValidText`, used to discard invalid alternate-format edits;
- a unique Monaco `modelUri`;
- `sourceRevision`, indicating which canonical revision produced the draft;
- parse `issues` for editor markers and validation status;
- structured `roots` used by breadcrumbs.

JSON is created when a file opens. YAML and TOML drafts are created lazily when the user switches formats.

## General editor features

### Opening files

- Accepts multiple `.json`, `application/json`, or `text/json` files.
- Uses `showOpenFilePicker` when supported so later saves can write to the selected file.
- Falls back to a hidden standard file input.
- Supports drag-and-drop and attempts to retain dropped file handles where available.
- Rejects non-JSON files and reports rejected or unreadable filenames in the global status area.
- Creates unique display names for duplicate filenames.

### Editing and validation

- Uses one Monaco model per document and representation.
- Parses a draft after a short debounce.
- Enables JSON diagnostics with comments disabled and trailing commas treated as errors.
- Adds Monaco markers for YAML and TOML parser issues.
- Matches the site's light or dark color mode.
- Includes folding, sticky scroll, bracket-pair coloring, word wrapping, and format-on-paste.

### Format synchronization

- JSON, YAML, and TOML are views of the same canonical value.
- A valid edit increments the document revision.
- A valid YAML or TOML edit regenerates the JSON draft immediately.
- A stale alternate draft is regenerated when its `sourceRevision` does not match the canonical revision.
- Switching away from an invalid or not-yet-validated YAML/TOML draft is blocked.
- The user can discard an invalid alternate draft and return to its `lastValidText`.
- TOML is disabled when the canonical value contains unsupported structures, including `null`, a non-object root, incompatible mixed arrays, dates, unsafe numbers, or other non-JSON values.

### Navigation and comparison

- Tabs manage multiple open files and show a modified indicator.
- A second document can be shown in a split comparison pane.
- Toolbar actions target the most recently focused visible pane.
- Breadcrumbs follow the current cursor through objects and arrays.
- Breadcrumb menus list sibling symbols and navigate Monaco to the selected offset.
- The browser-window title reflects the active file or split pair.
- The complete editor shell can enter fullscreen mode; guided modals portal into the fullscreen element when necessary.

### Saving and dirty state

- `Ctrl+S` / `Cmd+S` saves the focused document.
- A retained writable file handle is preferred.
- If direct writing fails or is unavailable, the editor downloads a JSON file.
- Dirty tabs compare `text` with `savedText` and also account for uncommitted alternate-format drafts.
- Closing a dirty tab requires confirmation.
- Navigating away from the page with dirty documents triggers the browser's unload warning.

## EMSolution recognition

`isEmSolutionInput` recognizes a document when either:

- `metaData.type` is `EMSolution_Input`; or
- at least two of `0_Release_Number`, `1_Execution_Control`, and `2_Analysis_Type` exist.

Recognized inputs show `Edit Field Sources` and `Edit Material Properties`, even when the corresponding section is absent. The Field Source action is disabled when:

- the active YAML/TOML representation has invalid uncommitted edits; or
- `17_Field_Source` exists but is not an array.

The Material Properties action is disabled when `16_Material_Properties` is not an object or either current-format material collection exists but is not an array.

## Unified Material Properties editor

`MaterialPropertyEditorModal` stages a deep-cloned material object and applies a complete canonical root only after validation succeeds. A missing section begins with `EXTEND_TOTAL_for_COIL: 0` and empty volume/surface arrays.

The General section edits `EXTEND_TOTAL_for_COIL` and optional `THIN_CRITERION`. The Volume section provides searchable master/detail CRUD for `16_1_3D_Element_Properties`, including optional `MAT_NAME`, potential regions, electric properties, magnetic properties, advanced anisotropy/hysteresis/complex-permeability/iron-loss blocks, and optional material flags. New-row defaults use `2_Analysis_Type`, while every documented group remains available in every analysis mode.

The Surface section supports `SURFACE_IMPEDANCE`, `GAP_ELEMENT`, `THIN_CONDUCTOR`, and `SHELL_COIL`, including nonlinear impedance and anisotropic thin-conductor settings. `Nonlinear_Parameters` and the legacy `Nonliear_Parameters` spelling are both editable without renaming the original key.

Non-object volume rows, unknown or malformed surface rows, and multi-definition surface rows use raw JSON repair. Unknown surface definitions are advisory; malformed and multi-definition structures block Apply. Updates replace only selected keys, and removing an optional group or changing a surface type requires confirmation.

## Unified Field Source editor

`FieldSourceEditorModal` owns a deep-cloned staged root document. Cancel leaves the open document unchanged. Apply normalizes supported special definitions and sends the new root through `updateCanonicalDocument`, which regenerates every existing representation and marks the document dirty.

### Master view

The source list shows:

- array index;
- recognized type;
- `SERIES_ID` when present;
- a concise type-specific summary;
- validation state;
- edit, duplicate, move, and delete actions.

Users can search all entry JSON, filter by type/status, and add new definitions. Source deletion and type replacement require confirmation. Deleting the final entry leaves `"17_Field_Source": []`.

### Detail view

For supported generic definitions, fields are generated from `FIELD_SOURCE_SCHEMAS`. Each control shows:

- a readable label;
- the canonical EMSolution JSON key;
- units where applicable;
- enum meanings;
- field help text;
- a link to the official definition documentation.

Nested `data` rows support add, duplicate, reorder, and delete operations. COIL rows can also change element type with confirmation.

### Supported Field Source definitions

| Type | Guided behavior |
| --- | --- |
| `COIL` | Top-level settings plus `UNIF`, `LOOP`, `GCE`, `ARC`, `FGCE`, `FARC`, `MESH`, `LOOP-`, `GCE-`, `ARC-`, `MESH-`, `LINE`, `DIPO`, and `EXMAG` rows. |
| `ELMCUR` | Internal-current regions with inflow/outflow faces and conductivity settings. |
| `SDEFCOIL` | Surface-defined coil regions with exactly four boundary surface IDs. |
| `PHICOIL` | Potential-current conductor rows. |
| `DCCURR` | Multi-material conductor groups with paired material/conductivity arrays. |
| `SUFCUR` | Single surface-current definition. |
| `SUFCUR2` | Multi-conductor surface-current rows. |
| `MAGNET` | Conditional layouts for `INPUT_TYPE` 0 through 5, including per-element, harmonic, formula, nonlinear, and temperature-dependent forms. |
| `CIRCUIT` | Embedded specialized circuit panel. |
| `NETWORK` | Embedded specialized network panel. |
| `EPOTSUF` | Equipotential surface source with conditional charge-unit input. |
| `POTNODE` | Node IDs paired with potential values. |

`EPOTNODE` is recognized as a legacy alias for `POTNODE`. Normalization retains the original `EPOTNODE` key unless the user explicitly converts the source type.

### Unknown and malformed data

The Field Source model classifies each array entry as:

- `known`: exactly one supported definition key; its definition body is validated separately and may still require raw repair;
- `unknown`: no supported definition key;
- `multiple`: more than one supported definition key;
- `malformed`: the Field Source array entry itself is not an object.

Unknown definitions remain available through raw JSON editing and produce an advisory warning. Malformed entries, malformed supported definition bodies, or multi-definition structures produce errors and must be repaired before Apply.

At all guided levels, updates begin with cloned existing objects and replace only known keys. This preserves vendor fields, future EMSolution properties, comments stored as JSON properties, and additions such as `MAGNET.data[].M`.

## NETWORK editor

The NETWORK panel supports these component types:

`FEM`, `R`, `L`, `M`, `C`, `CPS`, `VPS`, `D1`, `D2`, `EQ`, `TABLE`, `TAB`, `SETV`, `SETI`, `SWITCH`, and `VR`.

Features include:

- component search and type filtering;
- add, edit, raw edit, duplicate, reorder, and delete;
- automatic IDs for newly created components where appropriate;
- TABLE dataset editing with paired current/voltage arrays;
- SWITCH timing interval editing;
- reference-aware selectors for source series, time functions, inductors, table IDs, and element IDs;
- structural validation for IDs, node references, order-sensitive references, arrays, switch intervals, and known component requirements;
- warnings for unresolved cross-document references where the data can still be preserved.

When several NETWORK definitions exist, the occurrence corresponding to the selected Field Source row opens initially. The occurrence selector can still navigate among all NETWORK definitions.

## CIRCUIT editor

The CIRCUIT panel manages:

- region-factor and region-parallel settings;
- ordered `SERIES_IDS`;
- power supplies and their IDs, types, time references, and initial currents;
- inductance and resistance matrices;
- connection matrices between source series and power supplies;
- matrix storage modes and normalization;
- matrix remapping when series or power supplies are added, moved, duplicated, or removed.

Unknown properties on the CIRCUIT object, matrix objects, and power-supply rows are retained.

## Validation model

Field Source validation returns issues with a severity, JSON-like path, message, and source index.

Errors block Apply. Examples include:

- non-object definitions;
- invalid or missing required numbers and enums;
- incorrect three-component vectors;
- incorrect fixed array sizes;
- mismatched paired arrays;
- unknown MAGNET input modes;
- malformed NETWORK/CIRCUIT dimensions or matrices;
- multiple supported definitions in one Field Source array entry.

Warnings remain advisory. Examples include:

- unsupported raw definitions;
- unresolved time/reference IDs when sufficient reference data exists;
- electric-potential sources used outside the documented static analysis modes.

NETWORK and CIRCUIT validation is delegated to `validateNetwork` and `validateCircuit` so their existing rules remain authoritative.

## Modal and accessibility behavior

- The unified editor uses a portal and traps keyboard focus within the modal.
- Escape closes the current embedded NETWORK/CIRCUIT panel first, then closes the outer modal when pressed from the master or generic detail view.
- Dirty embedded panels and dirty outer drafts require confirmation before being discarded.
- Closing restores focus to the toolbar action that opened the modal.
- Actions have accessible labels, and validation/status regions use semantic roles.
- Responsive styles collapse wide grids and tables for smaller viewports.

## Common extension tasks

### Add or change a generic Field Source field

1. Update the relevant entry in `FIELD_SOURCE_SCHEMAS`.
2. Choose the correct field kind: integer, number, string, enum, vector, or numeric array.
3. Add units, enum labels, defaults, descriptions, exact/minimum lengths, and `visibleWhen` conditions.
4. Add cross-field validation in `validateFieldSourceEntry` when a schema field alone cannot express the rule.
5. Add model tests and at least one integration test if UI behavior changes.

Do not hand-code a new generic input in `FieldSourceEditorModal` unless the schema system cannot represent it.

### Add a new Field Source type

1. Add the canonical key to `FIELD_SOURCE_TYPES`.
2. Add its complete schema to `FIELD_SOURCE_SCHEMAS`.
3. Add a row schema or type-specific row resolver if it owns nested `data` rows.
4. Extend creation, validation, normalization, and summary logic if needed.
5. Decide how malformed and legacy forms should be classified.
6. Add documentation-link, schema, creation, validation, preservation, and round-trip tests.

### Add or change a Material Property field

1. Update the appropriate base, group, or surface schema in `materialPropertyModel.ts`.
2. Add a safe default only when the field belongs to a user-added optional group or a new material skeleton.
3. Extend cross-field validation for alternative arrays, analysis-mode guidance, or referenced curve IDs.
4. Keep legacy aliases in accessors rather than normalizing stored keys.
5. Add model coverage and an integration test for visible UI behavior and unknown-key preservation.

### Add a NETWORK component

1. Add the type to `NETWORK_COMPONENT_TYPES`.
2. Define its fields and help text in `NETWORK_COMPONENT_SCHEMAS`.
3. Update creation, duplication, normalization, summaries, and validation where the type has special behavior.
4. Add specialized React controls only for structures that ordinary fields cannot represent.
5. Add model and component regression tests.

### Change CIRCUIT matrices

Keep storage-mode conversion in `circuitModel.ts`, not in React rendering code. Any series or power-supply list transformation must remap the related matrices through the model helpers so row/column identities remain aligned.

### Change format synchronization

Treat this as high risk. Review all of the following together:

- `updateDraftText`;
- `updateParsedDraft`;
- `updateCanonicalDocument`;
- `selectDocumentFormat`;
- `discardInvalidDraft`;
- `saveDocument`;
- dirty-state and unload-warning logic.

Never update only the visible draft after a guided edit; the JSON payload, canonical value, existing alternate drafts, revision numbers, symbols, and validation issues must remain synchronized.

## Tests and verification

Tests live beside the implementation:

- `structuredFormats.test.ts`: parsing, serialization, compatibility, symbols, and formatting;
- `jsonSymbols.test.ts`: symbol trails, names, and titles;
- `networkModel.test.ts`: NETWORK transformations and validation;
- `circuitModel.test.ts`: CIRCUIT matrix transformations and validation;
- `fieldSourceModel.test.ts`: source schemas, variants, defaults, preservation, validation, legacy handling, and round trips;
- `materialPropertyModel.test.ts`: material schemas, defaults, surface classification, advanced validation, aliases, preservation, and round trips;
- `InputControlFileEditorClient.test.tsx`: file workflows, format switching, split targeting, unified modal behavior, nested/source CRUD, raw repair, focus, cancel/apply, and NETWORK/CIRCUIT regressions.

Run from the `docs` directory:

```powershell
npm test
npm run typecheck
npm run build
```

For Field Source changes, the minimum focused verification is:

```powershell
npm test -- --run src/components/InputControlFileEditor/fieldSourceModel.test.ts src/components/InputControlFileEditor/InputControlFileEditorClient.test.tsx
```

For Material Property changes, use:

```powershell
npm test -- --run src/components/InputControlFileEditor/materialPropertyModel.test.ts src/components/InputControlFileEditor/InputControlFileEditorClient.test.tsx
```

## External reference

The schema labels and descriptions are based on the official EMSolution input control documentation:

<https://emsolution-ssil.github.io/EMSolutionDocs/handbook/inputControl/17_Field_Source.html>

<https://emsolution-ssil.github.io/EMSolutionDocs/handbook/inputControl/16_Material_Properties.html>

<https://emsolution-ssil.github.io/EMSolutionDocs/handbook/inputControl/16_1_3D_Element_Properties.html>

<https://emsolution-ssil.github.io/EMSolutionDocs/handbook/inputControl/16_1_2_ES_3D_Element_Properties.html>

<https://emsolution-ssil.github.io/EMSolutionDocs/handbook/inputControl/16_2_2D_Element_Properties.html>

When documentation and existing files differ, preserve the original data, add compatibility handling where safe, and avoid destructive normalization.
