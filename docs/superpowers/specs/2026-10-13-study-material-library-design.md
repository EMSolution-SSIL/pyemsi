# Study Material Library and 16.1 Material Assignments: Design

Date: 2026-10-13
Status: approved in conversation, waiting for spec review
Branch: `feature/freecad-addon`
Companion: [EMS Material Manager widgets PRD](2026-10-13-ems-material-manager-widgets-prd.md)

## 1. Goal

Give FreeCAD Studies real material physics, taken from EMS Material Manager
(`ems-material-manager`, the EMSolution material-data master), and number the
mesh so that its physical group tags are the `MAT_ID` / `SMAT_ID` values that
EMSolution's `16_Material_Properties` uses. Prepare the `16_1_3D_Element_Properties`
section of the input control file so that the future input-file editor only has
to call one function.

## 2. Background

- EMS Material Manager (repo `EMSolution-SSIL/EMS_MaterialManager`, PyPI
  `ems-material-manager` 0.1.0) is owned by us. It stores canonical material
  records (`Material`, JSON v1: identity, scalar and curve properties with units,
  provenance) in a configured root (`manager.config.json`, `User` writable
  source, read-only reference sources). Its `EMSolutionInputAdapter` turns a
  material into a 16.1 entry plus `20_BH_Curve` records. Its Qt editor
  `MaterialManagerWindow` works on any `MaterialRepository`.
- Section 16.1 (`EMSolutionDocs/files/handbook/inputControl/16_1_3D_Element_Properties.rst`):
  each entry has `MAT_ID`, `POTENTIAL`, `ElectricProperty`, `MagneticProperty`
  and optional flags. In practice every body gets its own `MAT_ID`, so three
  iron bodies give three entries with the same physics; results are reported
  per `MAT_ID`.
- Today a Study has Materials (name + bodies), Excitations (name + faces) and
  Mesh Sizes. `Study.VolumeIds` gives each body an ID, `Study.SurfaceIds` each
  (excitation, body) pair. Gmsh physical groups use those IDs. Materials carry
  no physics. The Study also supports a legacy "Materials" main-geometry mode
  and restores properties of older documents.
- The add-on is not public. Older `.FCStd` files need not open.

## 3. Decisions

1. **Two folders.** A new **Material Library** folder holds the Study's own
   copies of materials. The **Materials** folder holds *assignments* that
   link a Material Library entry to bodies.
2. **Copies are independent.** Importing copies the library record into the
   Study. The copy keeps no origin, no link and no status relative to the
   Material Manager. It is edited in the Study and travels with the `.FCStd`,
   so a shared document works on any machine.
3. **Physics only from the Material Library** (no inline values on
   assignments). Air, copper and so on are ordinary materials.
4. **Per-body `MAT_ID`.** Each body with an assignment gets its own `MAT_ID`;
   `MAT_NAME` is the cleaned body label. One assignment over three bodies
   writes three 16.1 entries.
5. **An assignment carries only `POTENTIAL`** besides its material and bodies.
   Permeability form and iron-loss form follow the library adapter's `auto`
   rules; a user who needs another form edits or duplicates the Study copy.
6. **Mesh tags are the IDs.** In 3D, volume physical groups are tagged with
   `MAT_ID`, excitation surface groups with `SMAT_ID`. (In a future 2D Study,
   surfaces take `MAT_ID` and lines `SMAT_ID`; nothing 2D is built now.)
7. **Material Manager root is shared with eMotorSolution**:
   `EMS_MATERIAL_MANAGER_ROOT`, else the remembered root in
   `%APPDATA%\EMSolution\ems_material_product_exchange.json`, else ask once and
   remember it.
8. **Temporary stand-ins for the GUI.** Until EMS Material Manager ships
   `MaterialEditorWidget` and `MaterialPickerDialog` (see the PRD), the add-on
   uses a small picker of its own and opens the full `MaterialManagerWindow`
   on the Study.
9. **No back-compat.** Old properties are replaced, not migrated. The legacy
   "Materials" main-geometry mode and the restore-time upgrade code are removed.
10. **Out of scope:** 16.2 surface properties, the Excitations → Field Sources
    rework, writing the input control file, 2D meshing, PACKING / COORD_ID /
    `is_*` flags.

## 4. Data model

### 4.1 Study

- Folders, in tree order: `MaterialLibraryGroup` (**Material Library**),
  `MaterialsGroup`, `ExcitationsGroup`, `MeshSizesGroup`. All are created by
  `make_study`.
- ID tables (group `IDs`, read-only in the property editor):
  - `MatIds`: map body Name → `MAT_ID`; `NextMatId` starts at 1.
  - `SmatIds`: map `"Excitation Name|Body Name"` → `SMAT_ID`; `NextSmatId`
    starts at 1001.
  - These replace `VolumeIds`, `SurfaceIds`, `NextVolumeId`, `NextSurfaceId`.
- `MainMode` choices: `Unassigned`, `Container`, `Manual` (no `Materials`).
- Removed: `onDocumentRestored` property cleanup (`OutputFolder`,
  `LegacyOutput`) and the `legacy` argument of `add_setup`.

### 4.2 `LibraryMaterial` (new, `App::FeaturePython` in Material Library)

| Property | Type | Notes |
|---|---|---|
| `Label` | | Name in the tree; free to rename |
| `Record` | `App::PropertyString`, hidden | Canonical JSON (`material_to_json` / `Material.to_dict()`) |
| `MaterialId` | `App::PropertyString`, read-only | Mirrors `Record.material_id` |
| `Family` | `App::PropertyString`, read-only | Mirrors `Record.identity.family` |

- `material_id` is unique within a Study.
- Deleting a `LibraryMaterial` that an assignment links to is refused; the
  message names the assignments.

### 4.3 `Material` (assignment, in Materials)

| Property | Type | Default |
|---|---|---|
| `GroupName` | String | as today |
| `References` | LinkListGlobal (bodies) | as today |
| `LibraryMaterial` | `App::PropertyLink` | empty |
| `Potential` | `App::PropertyIntegerConstraint` (≥ 0) | 0 |

An empty `LibraryMaterial` is allowed for meshing. Only the 16.1 builder
rejects it.

## 5. IDs and meshing

- `update_ids` keeps its rules on the renamed tables: every body with an
  assignment gets a `MAT_ID`, every (excitation, body) an `SMAT_ID`; counters
  only grow; dropped IDs are not reused; `set_id` still edits single IDs.
- With the Materials mode gone, the set of volumes is the main region from
  `geometry.region(study, "Main")`. Every body in it must have exactly one
  assignment (existing `jobwriter.check` rules).
- `job.json` volume entries: `{"mat_id", "name" (MAT_NAME), "file", "size"}`.
  Surface entries: `{"smat_id", "name", "mat_id" (owning body), "files"}`.
- `mesher.py` tags each volume physical group with `mat_id`, each surface group
  with `smat_id`, and names them with `name`. It prints the ID → name table.
- `check` also rejects two bodies whose `MAT_NAME`s are equal after cleaning
  (existing duplicate-name rule).

## 6. Modules

- `objects.py`: folders, `LibraryMaterial`, `Material`, ID tables, row
  helpers. No `ems_material` import.
- `studymaterials.py` (new, no GUI, imports `ems_material`):
  - `StudyMaterialRepository(study)`: the library's `MaterialRepository`
    protocol over `LibraryMaterial` objects: `list`, `get`, `search`,
    `create`, `update` (`expected_version` conflict check), `duplicate`,
    `delete` (refuses in-use), `import_json`, `export_json`, `source_for`
    (`"Study"`), `is_writable` (true), `is_deletable` (false while in use),
    `list_sources` (`("Study",)`). Each write is one FreeCAD transaction.
    Any extra attribute that `MaterialManagerWindow` reads from its repository
    is provided too (checked during planning).
  - `import_materials(study, materials)`: creates `LibraryMaterial` objects in
    one transaction; raises on an ID already in the Study.
  - `library_root()`: env var, remembered root, else `None` (the GUI then asks
    with a folder dialog and calls `remember_library_root`).
  - `material_properties(rows)`: the 16.1 builder (section 8).
  - `study_material_rows(study)`: `[(mat_id, mat_name, potential, Material)]`
    in `MAT_ID` order; raises `StudyError` for an assignment without a
    `LibraryMaterial`.
- `materialpicker.py` (new, temporary): the stand-in picker dialog.
- `taskpanels.py` / `commands.py`: panels and commands (section 7).
- `jobwriter.py`, `geometry.py`, `mesher.py`: renamed IDs, Materials mode
  removed.

`objects.py`, `jobwriter.py` and `mesher.py` must work without
`ems_material` installed. The Material Library panel shows an install message
if the import fails.

## 7. User interface

### 7.1 Material Library folder panel

- Table: **Name**, **Family**, **Material ID**, **Used by** (assignment labels).
- **Import from Material Manager…** resolves the root (asks with a folder
  dialog and remembers it if needed) and opens the picker.
- **Edit…** opens the stand-in editor with the selected row preselected.
- **Delete** removes the selected materials, refusing ones in use.

### 7.2 Stand-in picker (temporary)

A dialog with a search box and a multi-select list (name, family, source)
backed by `MaterialManager(root).search(text=…)`. Materials whose ID is already
in the Study are disabled and marked "already in Material Library". OK calls
`import_materials`.

### 7.3 Stand-in editor (temporary)

**Edit…** opens a non-modal
`MaterialManagerWindow(MaterialManager(repository=StudyMaterialRepository(study)))`,
one per Study, re-focused when already open. New, Duplicate, Delete, Import,
Export and Save act on the Material Library. The task panel table refreshes
after each save. Known limitation: a FreeCAD undo while the window is open
shows stale values until the window's Refresh.

### 7.4 Materials (assignments)

- **Add Material** asks for a name, takes the selected bodies, then opens the
  item panel.
- Item panel: the existing body list, plus a **Material** combo (Material
  Library entries, or "— none —") and a **POTENTIAL** spin box (≥ 0).
- Materials folder table: **Assignment**, **Material**, **Body**, **MAT_ID**,
  **POTENTIAL**.
- ID table dialog headers: **MAT_ID** / **SMAT_ID**.

## 8. The 16.1 builder

`material_properties(rows) -> dict`, a pure function (no FreeCAD).

- For each distinct `ems_material.Material` in `rows`, call
  `EMSolutionInputAdapter().export_material(material)` once (default
  `ExportSelection`, i.e. `auto`).
- For each row, deep-copy that material's 16.1 entry and set `MAT_ID`,
  `MAT_NAME`, `POTENTIAL`.
- Emit each material's B-H curves once. Curve IDs are sequential across the
  Study starting at 1, in first-use order. Rewrite `BH_CURVE_ID` and
  `BH_CURVE_XYZ.BH_XYZ_ID` in every entry using that material. Curve names are
  the material's name, plus `_x` / `_y` / `_z` for anisotropic curves.
- Result:

  ```json
  {
    "16_Material_Properties": {"16_1_3D_Element_Properties": [ ... ]},
    "20_BH_Curve": [ ... ]
  }
  ```

- Adapter `ValueError` / `TypeError` are re-raised as `StudyError` naming the
  material.
- Not connected to any file or command yet. The future input-file editor calls
  `material_properties(study_material_rows(study))`.

## 9. Dependency

`pixi add --pypi "ems-material-manager[gui]>=0.1,<0.2"`; commit
`pyproject.toml` and `pixi.lock` together. FreeCAD runs from the pixi
environment, so the add-on can import it.

## 10. Testing

`pixi run pytest tests/freecad_addon`.

- `test_studymaterials.py` (new):
  - Repository: create / get / update / `expected_version` conflict /
    duplicate / delete refused while in use / list / search; save and reopen
    the `.FCStd`; one undo reverts one write.
  - Import: record copied unchanged; duplicate ID refused.
  - Builder: three bodies on one steel give three entries and one curve with
    matching IDs; two curve materials give sequential curve IDs; an `MU`-only
    material gives no curves; `POTENTIAL` carried through; an assignment
    without a material and iron loss without density raise `StudyError` with
    the name.
- `test_study.py`: `MatIds` / `SmatIds`, the Material Library folder, Manual
  main mode instead of the removed Materials mode; legacy-restore tests removed.
- `test_mesher.py`: physical group tags and names equal the job's `mat_id` /
  `smat_id` / `name`.
- `gui_smoke.py`: opens the Material Library panel and the Material item panel;
  constructs the picker and the editor window without driving them.

## 11. Later

- Replace the stand-ins with `MaterialEditorWidget` (embedded in the task
  panel) and `MaterialPickerDialog` once EMS Material Manager ships them.
- Input control file editor uses `material_properties`.
- 16.2 surface properties with `SMAT_ID`; Excitations become Field Sources.
- 2D Studies: surfaces tagged `MAT_ID`, lines `SMAT_ID`.
