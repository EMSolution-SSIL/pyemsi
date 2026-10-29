# Material Task Panel Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Every Material gets a name you choose and is edited in a task panel with an editable selection. That name is used in the mesh and the input file.

**Architecture:** The non-GUI logic lives in `objects.py`. That covers the name, label and suggestion; moving refs between Materials; face centres; and the volume names used by the job writer and validation. Unit tests drive it. A new `MaterialPanel` in `taskpanels.py` is a thin GUI over those functions, modelled on `ItemPanel`. The old `AssignDialog` shrinks to the several-bodies dialog, and the GUI smoke test is rewritten for the panel.

**Tech Stack:** FreeCAD 1.1 scripted objects (Python 3.11), PySide (Qt), pytest / unittest under pixi `addon` env.

**Spec:** `docs/superpowers/specs/2026-10-29-material-task-panel-design.md`

## Global Constraints

- Run everything through pixi: unit tests with `pixi run -e addon pytest tests/freecad_addon/<file> -k <name>`, all add-on tests with `pixi run -e addon test-addon`, lint with `pixi run lint`, format with `pixi run format`.
- `objects.py` has no GUI code (apart from attaching view providers). GUI goes in `taskpanels.py` and `commands.py`.
- Ruff, line length 120. Never sort or reorder imports. Don't run `ruff check --fix` across the codebase.
- Tree label of every Material: `<name>: <material>`. If there is no library material: `<name>: — none —` (`objects.NO_MATERIAL`).
- Suggested-name clash suffix: `_2`, `_3`, …
- Move confirmation text, title `Move to this Material?`, body:
  `These already belong to another Material:\n• Coil (in "Copper")\n…\n\nA body can have only one Material. Move them to "Iron"?`
  For faces, use `A face can have only one Material.` and entries like `Drawing.Face3 (in "Copper")`. Buttons: `Move`, `Cancel`.
- Emptied-Material note: `"Copper" will be removed: it has nothing left.`
- Air Region Material name field note: `Named after its Air Region; rename it there.`
- Panel warning when several bodies are added at once: `A Material holds one body: select one, or use Assign Material with several bodies selected to give each its own Material.`
- `_moved` warning advice: `remove and add it again in its Material's panel` (replaces `reassign it`).
- Old files must keep their mesh names and MAT_NAMEs when opened.

## Review Focus

- Renaming a body after it has a Material: the mesh/MAT_NAME stays the Material's name and the tree label doesn't change. Test in Task 2.
- Two Materials whose names are equal after `clean()` (`Coil 1` / `Coil_1`): validation reports duplicate group names. Test in Task 2.
- Cancel on a new Material after Add selection moved a body from another Material: the other Material is untouched. Smoke step in Task 5.
- A Material whose body was deleted (orphan) during migration, label sync and suggestion: no exception. Test in Task 1.
- An Air Region's Material picked into another Material's panel, or bulk-assigned: the Air keeps its own Material, with only lib/POTENTIAL updated. Tests in Task 3 (bulk) and Task 5 (panel gate).

---

### Task 1: Material name, label, suggestion and migration

**Files:**
- Modify: `freecad_addon/emsolution/objects.py`: `Material.__init__` / `onDocumentRestored` (~212-235), `assignment_label`, `assign`, `sync_labels`, `assign_pieces` (~760-845)
- Test: `tests/freecad_addon/test_study.py`, `tests/freecad_addon/test_symmetric_study.py`, `tests/freecad_addon/symcases.py:131` (only if its call needs the new label)

**Interfaces:**
- Produces:
  - `Material` has `App::PropertyString GroupName` (group `EMSolution`, doc `"Name used in the mesh group names"`). It does **not** sync GroupName from Label: Material stays a `_Proxy`, not a `_Named`.
  - `assignment_label(m) -> str`: `f"{display_name(m)}: {lib label or NO_MATERIAL}"`.
  - `set_material_name(m, name: str) -> None`: sets `GroupName = name`, then `Label = assignment_label(m)`.
  - `name_taken(study, name: str, own=None) -> bool`: True if another Material's `GroupName` (case-sensitive) equals `name`. `own` is excluded.
  - `suggest_name(study, refs: list[tuple[body, str]], lib, own=None) -> str`. Rules:
    - no refs: `""`.
    - first ref sub is `""`: `display_name(body)`.
    - otherwise: `lib.Label` if lib is set, else `display_name(refs[0][0])`.
    - Then `_2`, `_3`… until `not name_taken(...)`.
  - `assign(study, bodies, lib, potential, name=None) -> list[Material]`. When it makes a new Material, its name is `name or suggest_name(study, [(body, "")], lib)`. Bulk semantics are changed in Task 3; here only naming changes.
  - `assign_pieces(study, name, pieces, lib, potential)` sets the name through `set_material_name`.
  - `sync_labels(study)` sets `Label = assignment_label(m)` for every Material.
  - `Material.onDocumentRestored`: if `GroupName` is missing, adds it with this value:
    - `display_name(m.Body)` if there is a Body.
    - `m.Label` if there are Pieces.
    - `m.Label` otherwise.
    Then `Label = assignment_label(m)`, then `purgeTouched`.

- [ ] **Step 1: Update and add tests in `test_study.py`**
  - `test_assignment_label_follows_renamed_body_and_material` becomes `test_assignment_label_follows_material_not_body`. After `a.Label = "Core"; lib.Label = "M330"; sync_labels`, assert `m.Label == "A: M330"` and `m.GroupName == "A"`.
  - In the existing assign test, change `assertFalse(hasattr(first[0], "GroupName") ...)` to assert `first[0].GroupName == "A"` and `not hasattr(first[0], "References")`. The labels `["A: Steel", "B: Steel"]` stay.
  - `test_suggest_name`:
    - Box B labelled `Coil` with no Materials gives `"Coil"`.
    - After `assign([a], name="Coil")` (box A), `suggest_name(study, [(b, "")], lib)` gives `"Coil_2"`.
    - With `own=` A's Material it gives `"Coil"`.
    - Empty refs give `""`.
  - `test_assign_takes_a_name`: `assign(study, [a], lib, 0, name="Core")` gives `GroupName == "Core"` and `Label == "Core: Steel"`.
  - `test_old_material_gets_group_name_on_restore`: assign A, then `m.removeProperty("GroupName"); m.Label = "A: Steel"; m.Proxy.onDocumentRestored(m)`. Assert `GroupName == "A"` and `Label == "A: Steel"`. Do the same with the body deleted first (orphan): no exception, and `GroupName == "A: Steel"`.

- [ ] **Step 2: Update tests in `test_symmetric_study.py`**
  - `test_piece_assignment_gets_one_mat_id_keyed_by_itself`: count `GroupName == "Coil01"` instead of `Label`.
  - `test_piece_assignment_label_is_kept_on_sync` becomes `test_piece_assignment_label_shows_name_and_material`. After the library rename and sync, `coil.GroupName == "Coil01"` and `coil.Label == "Coil01: Renamed"`.
  - `test_suggest_name_for_faces`: with library `Steel`, `suggest_name(motor, [(top, "Face1")], lib)` starts with `"Steel"` and is not taken. With `lib=None` it starts with `display_name(top)`.

- [ ] **Step 3: Run and see them fail**

Run: `pixi run -e addon pytest tests/freecad_addon/test_study.py tests/freecad_addon/test_symmetric_study.py -k "label or suggest or restore or takes_a_name or mat_id_keyed"`
Expected: FAIL (`suggest_name` is not defined, the GroupName assertions fail).

- [ ] **Step 4: Implement the Interfaces above in `objects.py`**

- [ ] **Step 5: Run the two test files in full**

Run: `pixi run -e addon pytest tests/freecad_addon/test_study.py tests/freecad_addon/test_symmetric_study.py`
Expected: PASS. Any remaining failure that reads `m.Label` as a name should read `GroupName` / `display_name(m)` instead. `test_duplicate_assignment_labels_are_refused` must now set `GroupName` (it passes after Task 2).

- [ ] **Step 6: Commit** `objects.py` and the tests: `Material: a typed name in GroupName; tree label is "<name>: <material>"`.

---

### Task 2: The Material name in the mesh, MAT_NAME and validation

**Files:**
- Modify: `freecad_addon/emsolution/objects.py`: `volume_name` (~22), `key_name` (~1240), new `region_name`
- Modify: `freecad_addon/emsolution/jobwriter.py:260,301,341`
- Modify: `freecad_addon/emsolution/validation.py:527` (`_names`)
- Test: `tests/freecad_addon/test_study.py`

**Interfaces:**
- Consumes: `Material.GroupName` and `display_name(m)` (Task 1).
- Produces: `region_name(study, body) -> str`:
  - body is not an Air Region and has a whole-body Material (`assignment_of(study)`): `clean(display_name(material))`;
  - otherwise: `volume_name(body)`.
  - `key_name(study, key)` uses `region_name` for body keys. Air keys and Sliding Interface keys are unchanged. That way `studymaterials.study_material_rows` (MAT_NAME) and the ID table follow without edits.

- [ ] **Step 1: Write the tests**
  - `test_mesh_name_is_the_material_name`: box `A`, `assign([a], name="Core")`, `jobwriter.write_job(...)` (use the helper existing job tests use). In job.json `volumes[0]["name"] == "Core"`, and `objects.key_name(study, "A") == "Core"`.
  - `test_mesh_name_without_material_is_the_body_label`: box `A` included with no Material, so `volumes[0]["name"] == "A"`.
  - `test_renaming_the_body_keeps_the_mesh_name`: after `a.Label = "Other"`, `key_name` is still `"Core"` and `m.Label == "Core: Steel"`.
  - `test_material_names_equal_after_clean_are_refused`: two boxes with Materials named `Coil 1` and `Coil_1`. `validation` reports an error containing `"group names are the same"` (use the existing `_has`-style helper or `validation.check`).
  - `test_air_keeps_its_own_mesh_name`: an Air Region with a Material named `X` (set GroupName directly). `key_name(study, air.Name) == "Air"`.

- [ ] **Step 2: Run them**

Run: `pixi run -e addon pytest tests/freecad_addon/test_study.py -k "mesh_name or equal_after_clean or air_keeps"`
Expected: FAIL. The name is `"A"`, not `"Core"`.

- [ ] **Step 3: Implement `region_name`, use it in `key_name`, `jobwriter` (3 places, all have `study`), and `validation._names` (non-symmetric branch, bodies only; air keys stay on `key_name`)**

- [ ] **Step 4: Run the whole add-on suite**

Run: `pixi run -e addon test-addon`
Expected: PASS. The symmetric tests already use `volume_name(m)`, which reads `GroupName` through `display_name`.

- [ ] **Step 5: Commit**: `Mesh group names and MAT_NAME come from the Material's name`.

---

### Task 3: Refs, moves and face centres (the panel's model)

**Files:**
- Modify: `freecad_addon/emsolution/objects.py`: new functions next to `assign` / `assign_pieces`; `piece_centres`; `assign` bulk semantics
- Modify: `freecad_addon/emsolution/validation.py:722` (`_moved` text)
- Test: `tests/freecad_addon/test_study.py`, `tests/freecad_addon/test_symmetric_study.py`

**Interfaces:**
- Consumes: Task 1's naming.
- Produces:
  - `air_material(study, air) -> Material | None`: the Material whose `Body` is that Air Region.
  - `make_material(study) -> Material`: an empty Material in the Materials folder, no refs, GroupName `""`, view provider attached when the GUI is running (as `assign_pieces` does). The panel calls it inside its open transaction.
  - `material_owners(study, refs, own=None) -> list[tuple[tuple[body, str], Material]]`:
    - For each ref, the other Material that already holds it, in ref order; refs without an owner are left out.
    - Whole-body refs (`sub == ""`) are matched by `Body`; face refs by `item_refs(m)` of the piece Materials.
  - `emptied_by(study, refs, own=None) -> list[Material]`: the owners from `material_owners` that would have no refs left once these refs leave them.
  - `apply_material(study, m, name, lib, potential, refs, kept=frozenset()) -> None`. Not a transaction (the caller holds it). It:
    1. Removes `refs` from their other owners. An owner left empty is removed with `Document.removeObject`. A piece owner keeps the `PieceCentres` of the faces it still has.
    2. Whole-body (`refs[0][1] == ""`): `m.Body = refs[0][0]`. Pieces: `m.Pieces = refs` (grouped per body, as `assign_pieces` stores them). `PieceCentres`: the stored centre for every `(body.Name, sub)` in `kept` that `m` already had; a fresh `CenterOfMass` for every other face.
    3. `m.LibraryMaterial, m.Potential = lib, potential`; `set_material_name(m, name)`.
  - `assign(study, bodies, lib, potential, name=None)` bulk semantics:
    - Each body ends with exactly one Material, named `name or suggest_name(...)`, with lib/potential set.
    - A non-air body that had a Material has it replaced. Its old Material is renamed to the suggestion, or removed and a new one made (builder's choice); the visible result is the same.
    - An Air Region's existing Material keeps its name, and only lib/potential change.
    - `unassign` is unchanged.

- [ ] **Step 1: Write the tests (whole bodies, in `test_study.py`)**
  - `test_material_owners_and_emptied`: A has Material `Copper`, B has `Steel`. Then `material_owners(study, [(a,""),(b,"")])` returns `[((a,""), copper), ((b,""), steel)]`, and with `own=copper` it returns only steel's entry. `emptied_by(...)` returns `[copper, steel]`.
  - `test_apply_material_moves_a_body`: `m = make_material(study)`, then `apply_material(study, m, "Iron", lib, 2, [(a, "")])`. Now `m.Body == a`, `m.Label == "Iron: Steel"`, `Potential == 2`, Copper is gone from `materials(study)`, and `assignment_of(study)["A"] is m`.
  - `test_bulk_assign_replaces_but_keeps_air_name`: A has `Core`, and an Air Region whose Material is named `Air`. `assign(study, [a, air], lib2, 1)` leaves A's Material named `"A"` with lib2, and the air's Material still named `"Air"` with lib2 and potential 1. `len(materials(study)) == 2`.

- [ ] **Step 2: Write the tests (pieces, in `test_symmetric_study.py`)**
  - `test_apply_material_moves_faces_and_keeps_centres`:
    - Take two piece Materials P and Q from the motor fixture.
    - Move one face of Q to P with `kept` = all of P's current refs.
    - Then P has the face, Q lost it, `len(P.PieceCentres) == len(item_refs(P))`, and P's old centres are unchanged (compare vectors).
  - `test_readded_face_gets_a_fresh_centre`:
    - Set P's first stored centre to `App.Vector(1e6, 0, 0)`, so `validation` reports "has moved".
    - Call `apply_material` with the same refs and `kept` without that face.
    - The warning is gone, and its text, when present, contains `"remove and add it again in its Material's panel"` (check the text before the fix).
  - `test_moving_last_face_removes_the_owner`: move all of Q's faces to P. Q is no longer in `materials(motor)`.

- [ ] **Step 3: Run them**

Run: `pixi run -e addon pytest tests/freecad_addon/test_study.py tests/freecad_addon/test_symmetric_study.py -k "owners or apply_material or bulk_assign or readded or last_face"`
Expected: FAIL (names not defined).

- [ ] **Step 4: Implement the Interfaces and change the `_moved` text**

- [ ] **Step 5: Run the whole add-on suite**

Run: `pixi run -e addon test-addon`
Expected: PASS.

- [ ] **Step 6: Commit**: `Materials: move refs between Materials; keep face centres of faces left in place`.

---

### Task 4: The Air Region's Material follows its name

**Files:**
- Modify: `freecad_addon/emsolution/objects.py` (new `rename_air_region`)
- Modify: `freecad_addon/emsolution/commands.py:212` (`AddAirRegion`)
- Modify: `freecad_addon/emsolution/taskpanels.py` (`AirRegionPanel.accept`, ~1717)
- Test: `tests/freecad_addon/test_study.py`

**Interfaces:**
- Consumes: `air_material` (Task 3), `set_material_name` (Task 1).
- Produces: `rename_air_region(study, air, name: str) -> None`. It sets `air.Label = name`, `air.GroupName = name`, and, if `air_material(study, air)` exists, `set_material_name(that, name)`.
  - `AddAirRegion` passes `name=objects.display_name(air)` to `assign`.
  - `AirRegionPanel.accept` calls `rename_air_region` in place of its two property lines.

- [ ] **Step 1: Test** `test_renaming_air_renames_its_material`. Make an Air Region, `assign(study, [air], lib, 0, name="Air")`, then `rename_air_region(study, air, "Gap")`. Assert `air.GroupName == "Gap"`, the Material's `GroupName == "Gap"`, its `Label == "Gap: <lib>"`, and `key_name(study, air.Name) == "Gap"`.
- [ ] **Step 2: Run it**: `pixi run -e addon pytest tests/freecad_addon/test_study.py -k renaming_air`. Expected: FAIL.
- [ ] **Step 3: Implement, and wire up the command and the panel**
- [ ] **Step 4: Run** `pixi run -e addon test-addon`. Expected: PASS.
- [ ] **Step 5: Commit**: `Air Region: its Material is named after it`.

---

### Task 5: MaterialPanel, entry points, several-bodies dialog, smoke test

**Files:**
- Modify: `freecad_addon/emsolution/taskpanels.py`:
  - add `MaterialPanel` after `ItemPanel`;
  - `AssignDialog` (~140-190) becomes `BulkAssignDialog`;
  - remove `ask_assignment`, `ask_piece_assignment`, `edit_piece_assignments`, `is_piece_assignment` (if unused) and `apply_assignment` (the smoke test is updated);
  - `ViewProviderItem.doubleClicked` (~970);
  - `FolderView.assign_rows` and `open_item` (~565-620).
- Modify: `freecad_addon/emsolution/commands.py:112-137` (`AssignMaterial`)
- Test: `tests/freecad_addon/gui_smoke.py`

**Interfaces:**
- Consumes: `make_material`, `apply_material`, `material_owners`, `emptied_by`, `suggest_name`, `name_taken`, `air_material`, `is_symmetric`, `assignable`, `assignment_problem`, `picked_bodies`, `selected_faces`, `ItemGate`, `highlight`.
- Produces:
  - `MaterialPanel(obj, new=False, refs=())` with the attributes the smoke test drives:
    - `name` (QLineEdit), `material` (QComboBox, data = library object Name), `potential` (QSpinBox)
    - `refs` (QListWidget), `current` (list of refs), `note` (QLabel)
    - methods `add_selection()`, `remove()`, `accept() -> bool`, `reject() -> bool`
    - `confirm_move(text) -> bool`, a method so the smoke test can replace it; the default shows a `QMessageBox` with buttons `Move` / `Cancel`.
  - `BulkAssignDialog(study, bodies)`: material combo and POTENTIAL. On accept it asks `confirm_move` for owned non-air bodies and calls `objects.assign` inside one transaction `"Assign material"`.
  - `open_material_panel(study, refs)`: the shared entry point. It opens a transaction `"Assign material"`, calls `make_material` and shows `MaterialPanel(m, new=True, refs=refs)`.

Behaviour to implement (from the spec, the sections "The panel", "Suggested name", "Moving", "Several bodies at once", "Entry points"):
- **Gate.** Normal Study: `ItemGate(study, ANY_SUB, True, air=True)` with whole bodies. Symmetric: faces of Symmetric Mesh tops only. Picks use `picked_bodies(study)`, or the top faces `AssignMaterial` collects today.
- **Refusals** go through `warn`, using the existing `assignment_problem` messages, the "Materials go on the faces (pieces) of …" message for tops, and the several-bodies warning from Global Constraints.
- **Air Regions:** another Material's Air Region is refused (`warn("An Air Region keeps its own Material: open it from the Air Region's row.")`). In an Air Region's own Material, Name is read-only with the note from Global Constraints, and Add/Remove are disabled.
- **Name suggestion:**
  - It is refilled on Add selection and on a material change until the user edits the field (`textEdited` sets a flag).
  - When the panel opens for an existing Material, the flag starts set.
  - The suggestion is computed with `own=self.obj`.
- **Add selection:**
  - `material_owners(..., own=self.obj)` lists the picks that belong to another Material. If any do, one `confirm_move` lists all of them. Cancel drops those picks and keeps the rest.
  - After each list change, `note` shows the emptied-Material line for each `emptied_by` result (one line each), and hides itself when there are none.
- **`kept`:** the initial refs minus any ref removed during the session. A removed-then-re-added ref is not in `kept`.
- **OK:**
  - It refuses with `warn` and returns False when the list is empty, the name is empty, no material is chosen (or the library is empty, which shows the existing library-empty note), or `name_taken(study, name, own=obj)`.
  - Otherwise it calls `apply_material` (a new panel uses the open transaction; an existing one opens `"Edit " + obj.Label`), commits, recomputes, closes the gate and the highlight, and closes the dialog.
- **Cancel:** new → `abortTransaction`; existing → nothing changed. In both cases it closes the gate and the highlight.
- **`AssignMaterial.Activated`:**
  - Several bodies selected in a normal Study → `BulkAssignDialog`.
  - Otherwise → `open_material_panel(study, refs)`, where refs are the picks (possibly empty).
  - Nothing selected no longer warns. The tops-without-faces warning stays.
  - `IsActive` is False while `Gui.Control.activeDialog()`.
- **Double-click** on a Material in the tree → `Gui.Control.showDialog(MaterialPanel(obj))`, unless a dialog is open.
- **`FolderView`:**
  - Double-clicking a row opens its Material's panel. A row whose body has no Material opens `open_material_panel(study, [(body, "")])`.
  - **Assign…** with one row behaves the same. With several rows (normal Study) it opens `BulkAssignDialog`. In a symmetric Study each row is a Material, so it opens the panel for the first row.

- [ ] **Step 1: Rewrite the smoke-test Material sections in `tests/freecad_addon/gui_smoke.py`**
  - Replace the `ask_assignment` / `ask_piece_assignment` stubs (lines ~40-41, ~1324-1343) with a `RecordedMaterialPanel` subclass that records opened panels, like `RecordedPanel` does for `ItemPanel`. Set `confirm_move` to a recorder that returns the next queued answer.
  - Replace every `AssignDialog` / `apply_assignment` use (~315-355, ~1160, ~1383-1412) with panel or bulk-dialog driving. The assertions must cover these cases:
    1. `EMS_Material` with A selected opens a new panel, with `name.text() == "A"` and A in the list. Pick the library material, OK, and the tree has `A: <lib>`.
    2. `EMS_Material` with nothing selected opens an empty panel. OK is refused (log `refused:` …). Cancel leaves `len(materials)` unchanged.
    3. Double-click A's Material, type the name `Core`, OK: `GroupName == "Core"`. Reopen it: the name stays `Core` after Add selection.
    4. New panel, Add selection with A (which has `Core`): `confirm_move` gets text containing `A (in "Core")` and `"Core" will be removed`, and answers Move. Cancel the panel: `Core` still exists on A. Do it again and press OK: `Core` is gone and the new Material has A.
    5. Same as 4 with `confirm_move` answering Cancel: A is not added.
    6. `EMS_Material` with A and B selected opens `BulkAssignDialog`, not a panel. Accept it: A and B have Materials named `A` and `B`.
    7. Symmetric study: `EMS_Material` with two top faces opens a panel listing both, with the name suggested from the library material. OK makes a piece Material. Reopen it, Remove one face, OK: `len(item_refs) == 1`.
    8. A failing `apply_material` (monkeypatched to raise, as the old `assign_pieces` failure step does) leaves no new Material behind.
- [ ] **Step 2: Implement `MaterialPanel`, `BulkAssignDialog`, `open_material_panel` and the entry points above, and remove the old dialog functions**
- [ ] **Step 3: Run unit tests and lint**

Run: `pixi run -e addon test-addon` then `pixi run lint`
Expected: PASS, no lint findings.

- [ ] **Step 4: Run the GUI smoke test**

Run: `pixi run -e addon freecad tests\freecad_addon\gui_smoke.py`, then read the last line of `%TEMP%\ems_gui_smoke.txt`.
Expected: `PASS` (a crash report on quit after PASS is normal).

- [ ] **Step 5: Commit**: `Material: task panel with an editable selection, move confirmation and several-bodies assign`.
