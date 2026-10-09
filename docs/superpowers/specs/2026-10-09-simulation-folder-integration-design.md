# Simulation Folder Integration for FreeCAD Studies: Design

Date: 2026-10-09
Status: approved in conversation, waiting for spec review
Branch: `feature/freecad-addon`

## 1. Goal

Make Run Mesh write its mesh where EMSolution reads it: into the simulation
folder, under the fixed file name the solver expects. Input control files in
that folder then run against the mesh without any copying or renaming.

## 2. Background

- An EMSolution project is a folder (the *run_dir*). It holds the input
  control files, the mesh files and the results. pyemsi opens this folder in
  its explorer, and *New FreeCAD Document* already saves the `.FCStd` into the
  current explorer folder.
- EMSolution runs as `EMSolution.exe -b -d <run_dir> -f <input_file>`. The
  input file name is free; several input files in one folder are common and
  they are run one at a time.
- An input file does not name its mesh. `10_1_Input_Files.INPUT_MESH_FILE`
  selects only the format, and the solver reads fixed names from the run_dir
  (handbook `run/1-inputFiles.rst`, `mesh_files.rst`):
  - `pre_geom`: 3D mesh, read when `GEOMETRY(12)` = 0.
  - `pre_geom2D`: 2D mesh, read when `GEOMETRY(12)` = 1, 2, 3 or 4.
  - `rotor_mesh` / `rotor_mesh2D`: moving part in sliding motion.
  - The extension identifies the format. Gmsh is `INPUT_MESH_FILE` = `11` or
    `"GMSH"`, extension `.msh` (supported since the 2025/11 release; the
    handbook's file list does not mention it yet).
- `GEOMETRY(12)` = 4 is the 2D_to_3D tool: EMSolution expands `pre_geom2D`
  (and `rotor_mesh2D`) into a 3D mesh and writes `pre_geom` itself. The
  expansion settings live in the input file, not in the mesh.
- Today each Study has an `OutputFolder` property. Empty means
  `<document>_mesh/<Study Name>/` next to the `.FCStd` (or `<document>_mesh/`
  for legacy Studies, flagged by `LegacyOutput`). That folder receives
  `job.json`, `geometry/*.brep`, `<Label>.msh` and `<Label>.unv`. Run Mesh
  rejects two Studies of one document that resolve to the same folder.

## 3. Decisions

1. **The simulation folder is the folder that contains the `.FCStd`.** The user
   keeps the FreeCAD file inside the simulation folder. A Study has no output
   folder setting. To use another simulation folder, the user saves the
   document there.
2. **Run Mesh writes the fixed EMSolution name.** A 3D Study writes
   `pre_geom.msh`; a 2D Study writes `pre_geom2D.msh`. Whether a 2D mesh is
   solved in 2D or expanded to 3D is the input file's choice, not the Study's.
3. **Last Run Mesh wins.** Several Studies may target the same folder. Each
   Run Mesh replaces the fixed-name file, and the input files use whatever is
   there. This is the intended workflow: the user meshes a Study, then runs
   the input files against it. No confirmation dialog and no record of which
   Study produced the file (see section 8).
4. **Gmsh working files live in `.pyemsi/`.** The scratch folder is
   `<simulation folder>/.pyemsi/freecad/<FCStd file stem>/<Study Name>/`,
   created when missing. `Study Name` is FreeCAD's internal object name, so
   renaming a Study (its Label) keeps the same folder. Separate FCStd files
   and separate Studies never share a scratch folder.
5. **The user may start from the FreeCAD file** and create input files
   afterwards (by hand today, with a future wizard later). Nothing in this
   design depends on an input file existing.

## 4. Folder layout

```
<simulation folder>/
├── Motor.FCStd
├── input.json, input_*.json          user / future wizard
├── pre_geom.msh                      Run Mesh, 3D Study
├── pre_geom2D.msh                    Run Mesh, 2D Study (once 2D meshing exists)
└── .pyemsi/
    └── freecad/<FCStd file stem>/<Study Name>/
        ├── job.json
        ├── geometry/*.brep
        └── mesh.unv                  read back only for display in FreeCAD
```

## 5. Changes

All changes are in `freecad_addon/emsolution/` and its tests. pyemsi itself is
unchanged: it already creates `.pyemsi/` and gives it an explorer icon.

### `jobwriter.py`

- Replace `output_folder(study)` with:
  - `simulation_folder(study)`: the directory of `study.Document.FileName`.
    Raises `StudyError("Save the document in the simulation folder first.")`
    when the document has never been saved.
  - `scratch_folder(study)`: `simulation_folder/.pyemsi/freecad/<stem>/<Name>`.
  - `mesh_file(study)`: `simulation_folder/` + `pre_geom` + (`2D` for a 2D
    Study) + `.msh`. This is the only place the name rule lives.
- `write_job` writes `job.json` and `geometry/` into the scratch folder
  (`os.makedirs(..., exist_ok=True)`) and adds `"mesh_file"`, the absolute path
  from `mesh_file(study)`, to the job.
- Remove the check that rejects two Studies sharing an output folder.

### `mesher.py`

- Write the `.msh` to `job["mesh_file"]` and the `.unv` to `mesh.unv` next to
  `job.json`. Print the `.msh` path. Still no FreeCAD imports.

### `runner.py`

- `load_result` reads `mesh.unv` from the job's folder.
- The console report names the file, the folder and the Study, for example
  `pre_geom.msh written to C:\...\Motor from Study Stator 3D`, followed by
  `(replaced existing file)` when the file existed before the run, and a
  reminder that input files need `INPUT_MESH_FILE` = `"GMSH"` (11). Whether
  the file existed is checked before the mesher starts.

### `objects.py`

- New Studies no longer get `OutputFolder` or `LegacyOutput`.
- `onDocumentRestored` removes those two properties from older documents
  (`removeProperty`, only when present), so they do not show in the property
  editor. The remaining upgrade logic is unchanged.

### `taskpanels.py`

- Remove the Output folder field and its save handler from the Study panel.
- The notice shows `Writes <simulation folder>\pre_geom.msh`, or the unsaved
  document error.

## 6. Error handling

| Situation | Behaviour |
|---|---|
| Document never saved | Run Mesh stops with the `StudyError` above; the panel notice shows the same text. |
| `.pyemsi/` missing | Created by `makedirs`. |
| Target `.msh` exists | Replaced; the report says so. |
| Target `.msh` locked (open elsewhere) | Gmsh fails; the existing runner error dialog shows the mesher's message. |
| Non-ASCII folder or file name | Must keep working, as the current Persian-path test requires. |

## 7. Testing

Existing tests that set `study.OutputFolder` instead save the document into a
temporary folder (`tests/freecad_addon/test_study.py`, `gui_smoke.py`).

- `pre_geom.msh` is written next to the `.FCStd`; `job.json`, `geometry/` and
  `mesh.unv` are under `.pyemsi/freecad/<stem>/<Name>/`.
- Two Studies in one document: the second Run Mesh replaces `pre_geom.msh`,
  and their scratch folders differ.
- `mesh_file` returns `pre_geom2D.msh` for a 2D Study.
- An unsaved document raises the `StudyError`.
- A document saved in a folder with Persian letters meshes successfully
  (adapts `test_output_folder_with_persian_letters`).
- Restoring a document that has `OutputFolder` and `LegacyOutput` removes both
  and keeps IDs, settings and links (adapts the existing upgrade test).
- `test_mesher.py`: jobs carry `mesh_file`; the `.msh` lands there and the
  `.unv` beside `job.json`.
- Remove the tests for the shared-output-folder rejection and the legacy
  `<document>_mesh` path.

## 8. Not in this change

- **Provenance.** No record of which FCStd and Study wrote the current
  `pre_geom.msh`, and no confirmation before replacing it. Add a small
  `.pyemsi/meshes.json` and a confirmation if users lose track of which Study
  is meshed.
- **`rotor_mesh.msh` / `rotor_mesh2D.msh`.** Added together with
  sliding-motion meshing, which is disabled today. `mesh_file` then returns
  one path per region.
- **Input control file edits.** Setting `INPUT_MESH_FILE` = `"GMSH"` belongs
  to the future input control file wizard.
- **Unsaved documents** are not saved automatically; the user saves them.

## 9. To verify with the real EMSolution executable

- A run with `INPUT_MESH_FILE` = `"GMSH"` reads `pre_geom.msh` from the
  run_dir.
- With `GEOMETRY(12)` = 4, the `pre_geom` that EMSolution generates does not
  replace or get confused with `pre_geom.msh`.
