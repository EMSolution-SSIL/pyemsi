# Per-Body Material Assignments Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace named, multi-body `Material` assignments with one link-based assignment per body (body, library material, POTENTIAL), assigned in bulk from a selection, and let meshing run without materials.

**Architecture:** `objects.Material` keeps only `Body` (global link), `LibraryMaterial` (link) and `Potential`; `objects.assign` / `objects.unassign` are the only way to create or remove one, so a body has at most one assignment per Study. Mesh group names come from body labels (`objects.volume_name`), so `jobwriter.check` no longer looks at materials; only `studymaterials.study_material_rows` (the 16.1 builder input) requires them. The GUI gets one `AssignDialog` used by the toolbar command, the Materials panel and a tree double-click.

**Tech Stack:** FreeCAD 1.1.0 (pixi env, Python 3.11, PySide6), `ems-material-manager` 0.1.x, gmsh, unittest run by pytest.

**Spec:** [docs/superpowers/specs/2026-10-13-study-material-library-design.md](../specs/2026-10-13-study-material-library-design.md) — revised 2026-10-14, sections 3 (decisions 1, 4, 5, 5a), 4.3, 5, 6, 7.4, 10.

## Global Constraints

- Run everything through pixi: `pixi run pytest ...`, `pixi run python ...`. Never `pip install`.
- Ruff only, line length **120**, double quotes. Format only files you changed: `pixi run ruff format <files>`. `pixi run lint` must pass.
- **Never sort or reorder imports.** Add new imports next to related ones.
- `objects.py`, `geometry.py`, `jobwriter.py` and `mesher.py` must not import `ems_material`.
- No back-compat: `GroupName` and `References` disappear from `Material`; no migration code.
- Formatting-only changes go in their own commit, whose hash is added to `.git-blame-ignore-revs` (Task 0).
- Commit messages end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Never use `--no-verify`.
- User-visible words: **— none —** (`objects.NO_MATERIAL`) for no material; **MAT_ID** / **SMAT_ID**; command **Assign Material**; panel button **Assign…**.
- Assignment tree label: `"<body label>: <material label>"`. Nothing may read it.

## Review Focus

1. **A body deleted while it has an assignment.** The assignment's `Body` becomes `None`; rows, IDs, `bodies_without_material`, `sync_labels` and the 16.1 builder must skip it without crashing, and "used by" messages still name it (Task 2 test `test_assignment_of_a_deleted_body_is_ignored`).
2. **The same body twice in one assign call, or re-assigned later.** Still exactly one assignment object for that body (Task 2 test `test_assign_makes_one_assignment_per_body`).
3. **A body outside the main geometry with an assignment.** It still shows in the Materials panel (so it can be removed) and does not block meshing or the builder (Task 2 tests `test_folder_overview_rows`, `test_multiple_studies_have_independent_ownership_and_ids`).
4. **Meshing with no assignments at all.** `write_job` succeeds and names volumes by body label; the builder names every body that has no material (Task 1 test `test_bodies_without_materials_are_meshed_and_listed`, Task 1 test `test_body_without_an_assignment_is_named`).
5. **"— none —" chosen in the dialog for bodies that have no assignment.** Nothing is created and nothing fails (Task 3 smoke step).

## File Map

- `freecad_addon/emsolution/commands.py` — Task 0 format only; Task 3 `AddMaterial` → `AssignMaterial`.
- `freecad_addon/emsolution/jobwriter.py` — Task 1: `check` drops material rules, `volumes = [(body, size)]`.
- `freecad_addon/emsolution/objects.py` — Task 1: `volume_name`, `item_name` for excitations only, `id_rows`. Task 2: per-body `Material`, `assign`, `unassign`, `assignment_of`, `assignment_label`, `sync_labels`, `user_labels`, rows.
- `freecad_addon/emsolution/studymaterials.py` — Task 1: `study_material_rows` names missing bodies. Task 2: uses `assignment_of`; delete message uses `user_labels`.
- `freecad_addon/emsolution/taskpanels.py` — Task 3: `AssignDialog`, `apply_assignment`, `ask_assignment`, Materials panel, item panel and view provider changes.
- `tests/freecad_addon/test_study.py`, `tests/freecad_addon/test_studymaterials.py` — Tasks 1–2.
- `tests/freecad_addon/gui_smoke.py` — Task 3.

Between Task 2 and Task 3 the GUI code still refers to `References` on materials; unit tests pass, the GUI smoke test does not. Run the smoke test only at the end of Task 3.

---

### Task 0: Format `commands.py` on its own

`commands.py` is not Ruff-formatted yet, and the pre-commit hook would reformat it inside the Task 3 commit.

**Files:**
- Modify: `freecad_addon/emsolution/commands.py` (formatting only)
- Modify: `.git-blame-ignore-revs`

- [ ] **Step 1: Format**

Run: `pixi run ruff format freecad_addon/emsolution/commands.py`
Expected: `1 file reformatted`

- [ ] **Step 2: Check the diff is formatting only**

Run: `git diff --stat` and `pixi run lint`
Expected: only `commands.py` changed; lint passes.

- [ ] **Step 3: Commit**

```bash
git add freecad_addon/emsolution/commands.py
git commit -m "Ruff format commands.py

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

- [ ] **Step 4: Record the hash**

Append to `.git-blame-ignore-revs` (keep the existing style: blank line, comment, hash):

```
# Ruff format for commands
<full hash from: git rev-parse HEAD>
```

```bash
git add .git-blame-ignore-revs
git commit -m "Skip the commands.py format commit in blame

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 1: Mesh without materials; name volumes by body

**Files:**
- Modify: `freecad_addon/emsolution/objects.py` (`item_name`, new `volume_name`, `id_rows`)
- Modify: `freecad_addon/emsolution/jobwriter.py` (`check`, `write_job`)
- Modify: `freecad_addon/emsolution/studymaterials.py` (`study_material_rows`)
- Test: `tests/freecad_addon/test_study.py`, `tests/freecad_addon/test_studymaterials.py`

**Interfaces:**
- Produces: `objects.volume_name(body) -> str` (`clean(body.Label)`); `objects.item_name(item, body)` for Excitations only; `jobwriter.check(study) -> (volumes, surfaces, elements)` with `volumes = [(body, size_mm)]`; `study_material_rows` raises `StudyError("These bodies have no material from the Material Library: A, B")`.

- [ ] **Step 1: Change the tests**

In `tests/freecad_addon/test_study.py`:

Delete `test_check_two_materials` entirely.

In `test_smallest_mesh_size_wins`, change `self.assertEqual(volumes[0][2], 2.0)` to `self.assertEqual(volumes[0][1], 2.0)`.

Replace `test_missing_selected_materials_are_named_before_ids_or_files_change` with:

```python
    def test_bodies_without_materials_are_meshed_and_listed(self):
        a, b = self.box("A"), self.box("B", 10)
        self.study.MainMode, self.study.MainObjects = "Manual", [a, b]
        self.assertEqual(geometry.export_unavailable(self.study), "")
        with open(jobwriter.write_job(self.study), encoding="utf-8") as fh:
            job = json.load(fh)
        self.assertEqual([(v["mat_id"], v["name"]) for v in job["volumes"]], [(1, "A"), (2, "B")])
        self.assertEqual(objects.bodies_without_material(self.study), [a, b])
```

Replace `test_selection_ids_survive_material_changes_and_follow_live_membership` with:

```python
    def test_ids_follow_live_membership_of_the_selected_geometry(self):
        a, b, c = self.box("A"), self.box("B", 10), self.box("C", 20)
        source = self.doc.addObject("App::DocumentObjectGroup", "Stator")
        source.addObject(a)
        source.addObject(b)
        self.study.MainMode, self.study.MainSource = "Container", source
        objects.update_ids(self.study)
        self.assertEqual(self.study.MatIds, {"A": "1", "B": "2"})
        self.assertEqual([r[2] for r in objects.id_rows(self.study)], ["A", "B"])
        source.removeObject(b)
        source.addObject(c)
        objects.update_ids(self.study)
        self.assertEqual(self.study.MatIds, {"A": "1", "C": "3"})
```

Replace `test_selected_geometry_rejects_conflicting_materials_and_invalid_sources` with:

```python
    def test_selected_geometry_rejects_a_missing_container(self):
        self.study.MainMode, self.study.MainObjects = "Manual", [self.box("A")]
        self.study.MainMode = "Container"
        self.assertStudyError("Selected container is missing")
```

In `tests/freecad_addon/test_studymaterials.py`, class `StudyRowsTest`, replace `test_assignment_without_a_material_is_named` and `test_deleted_library_material_is_reported` with:

```python
    def test_body_without_an_assignment_is_named(self):
        a, b = self.box("A"), self.box("B", 10)
        self.study.MainObjects = [a, b]
        (lib,) = studymaterials.import_materials(self.study, [material("user:air", "Air", AIR)])
        objects.make_material(self.study, "Gap", [a]).LibraryMaterial = lib
        with self.assertRaisesRegex(StudyError, "no material from the Material Library: B$"):
            studymaterials.study_material_rows(self.study)

    def test_assignment_without_a_material_is_named(self):
        a = self.box("A")
        self.study.MainObjects = [a]
        objects.make_material(self.study, "Iron", [a])
        with self.assertRaisesRegex(StudyError, "no material from the Material Library: A$"):
            studymaterials.study_material_rows(self.study)

    def test_deleted_library_material_is_reported(self):
        a = self.box("A")
        self.study.MainObjects = [a]
        (lib,) = studymaterials.import_materials(self.study, [material("user:air", "Air", AIR)])
        objects.make_material(self.study, "Gap", [a]).LibraryMaterial = lib
        self.doc.removeObject(lib.Name)
        with self.assertRaisesRegex(StudyError, "no material from the Material Library: A$"):
            studymaterials.study_material_rows(self.study)
```

- [ ] **Step 2: Run them to see them fail**

Run: `pixi run pytest tests/freecad_addon/test_study.py tests/freecad_addon/test_studymaterials.py -k "smallest or without_materials or live_membership or missing_container or without_an_assignment or without_a_material or deleted_library" -v`
Expected: FAIL — `write_job` raises "bodies with no material", `volumes[0][1]` is a Material, `id_rows` still says "No material: A", builder messages differ.

- [ ] **Step 3: Implement**

`freecad_addon/emsolution/objects.py`, replace `item_name`:

```python
def volume_name(body):
    """MAT_NAME and the volume's mesh group name."""
    return clean(body.Label)


def item_name(item, body):
    """An excitation's surface group name on one body."""
    return f"{clean(display_name(item))}_{clean(body.Label)}"
```

In `id_rows`, replace the volume loop body and drop `material_of`:

```python
def id_rows(study):
    """Rows for the ID table dialog: (table, key, name, id), volumes first."""
    rows = []
    for name in volume_keys(study):
        if name in study.MatIds:
            body = study.Document.getObject(name)
            rows.append(("MatIds", name, volume_name(body), int(study.MatIds[name])))
    for e in excitations(study):
```

(the excitation loop stays as it is).

`freecad_addon/emsolution/jobwriter.py`, in `check`: replace the docstring's first line `volumes  = [(body, material, size_mm)] in tree order` with `volumes  = [(body, size_mm)] in main geometry order`, then replace everything from `material_of = {b.Name: (b, []) for b in bodies}` down to and including the `surfaces = [...]` / `sized = [...]` comprehensions with:

```python
    bodies = list({b.Name: b for b in bodies}.values())  # main geometry order
    included = {b.Name for b in bodies}
    surfaces = [
        (e, b, faces) for e in objects.excitations(study) for b, faces in objects.subs_by_body(e) if b.Name in included
    ]
    sized = [(s, b, subs) for s in objects.mesh_sizes(study) for b, subs in objects.subs_by_body(s) if b.Name in included]
```

and replace the `volumes = ...` and `names = [objects.item_name(m, b) ...]` lines with:

```python
    volumes = [(b, size.get(b.Name, settings.DefaultMeshSize.Value)) for b in bodies]
    names = [objects.volume_name(b) for b, _ in volumes]
```

In `write_job`:

```python
    for body, size in volumes:
        mat_id = int(study.MatIds[body.Name])
        rel = f"geometry/vol_{mat_id}.brep"
        global_shape(body).exportBrep(os.path.join(folder, rel))
        job["volumes"].append({"mat_id": mat_id, "name": objects.volume_name(body), "file": rel, "size": size})
```

`freecad_addon/emsolution/studymaterials.py`, replace `study_material_rows`:

```python
def study_material_rows(study):
    """[(MAT_ID, MAT_NAME, POTENTIAL, material)] for the Study's bodies, in MAT_ID order."""
    volumes, _, _ = jobwriter.check(study)
    objects.update_ids(study)
    have = {b.Name: m for m in objects.materials(study) for b in m.References}
    missing = [b.Label for b, _ in volumes if b.Name not in have or have[b.Name].LibraryMaterial is None]
    if missing:
        raise StudyError("These bodies have no material from the Material Library: " + ", ".join(missing))
    rows = [
        (int(study.MatIds[b.Name]), objects.volume_name(b), have[b.Name].Potential, record_material(have[b.Name].LibraryMaterial))
        for b, _ in volumes
    ]
    return sorted(rows, key=lambda r: r[0])
```

(Ruff will wrap the long tuple; run the formatter in Step 5.)

- [ ] **Step 4: Run the addon tests**

Run: `pixi run pytest tests/freecad_addon -v`
Expected: all PASS.

- [ ] **Step 5: Format, lint, commit**

```bash
pixi run ruff format freecad_addon/emsolution/objects.py freecad_addon/emsolution/jobwriter.py freecad_addon/emsolution/studymaterials.py tests/freecad_addon/test_study.py tests/freecad_addon/test_studymaterials.py
pixi run lint
git add freecad_addon/emsolution/objects.py freecad_addon/emsolution/jobwriter.py freecad_addon/emsolution/studymaterials.py tests/freecad_addon/test_study.py tests/freecad_addon/test_studymaterials.py
git commit -m "Mesh bodies without materials and name volumes by body label

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: One link-based assignment per body

**Files:**
- Modify: `freecad_addon/emsolution/objects.py`
- Modify: `freecad_addon/emsolution/studymaterials.py`
- Test: `tests/freecad_addon/test_study.py`, `tests/freecad_addon/test_studymaterials.py`

**Interfaces:**
- Consumes: `objects.volume_name`, `objects.NO_MATERIAL`, `objects._add`, `objects._main_bodies` (Task 1 / existing).
- Produces (all in `objects`):
  - `Material` proxy with properties `Body` (`App::PropertyLinkGlobal`), `LibraryMaterial` (`App::PropertyLink`), `Potential` (`App::PropertyIntegerConstraint`, 0..1000000). No `GroupName`, no `References`. `make_material` is removed.
  - `assignment_of(study) -> {body Name: Material}` (assignments whose `Body` is not `None`).
  - `assignment_label(m) -> str` — `"<body label>: <material label or — none —>"`.
  - `assign(study, bodies, lib, potential) -> [Material]` — one per entry of `bodies` (same object for a repeated body). No transaction.
  - `unassign(study, bodies) -> None` — removes those bodies' assignments. No transaction.
  - `sync_labels(study) -> None` — rewrites stale assignment labels.
  - `user_labels(lib) -> [str]` — body label per user; the assignment label if its body is gone.
  - `material_rows(study) -> [(body, [(body, "")], [body label, material, MAT_ID, POTENTIAL])]`.

- [ ] **Step 1: Change the test helpers and mechanical call sites**

In `tests/freecad_addon/test_study.py`, replace the `mat` helper with:

```python
    def steel(self):
        """The Study's Steel library material, made on first use."""
        found = [o for o in objects.library_materials(self.study) if o.MaterialId == "user:steel"]
        return found[0] if found else self.lib()

    def assign(self, bodies, potential=0, lib=None):
        """Assignments on bodies that are also in the main geometry; lib defaults to Steel."""
        self.include(*bodies)
        return objects.assign(self.study, bodies, lib or self.steel(), potential)
```

(`lib` is defined further down the class; keep it where it is.)

Then, in every test that only needs bodies in the main geometry, replace `self.mat("<anything>", [x, y])` with `self.include(x, y)` (keep the argument order). This applies to: `test_ids_follow_tree_order_and_stay_after_adding_a_body`, `test_surface_ids_one_per_excitation_and_body`, `test_rename_keeps_id_and_changes_name` (also delete its line `mat.Label = "Iron"` and the `mat =` binding), `test_deleted_body_id_is_not_reused`, `test_set_id_refuses_duplicates_and_raises_counter`, `test_new_volume_ids_skip_numbers_used_by_surfaces`, `test_mesh_settings_go_to_the_job`, `test_check_min_size_above_max_size`, `test_check_not_one_solid`, `test_check_zero_size`, `test_check_missing_face`, `test_smallest_mesh_size_wins`, `test_names_equal_after_cleanup_are_refused`, `test_simulation_folder_with_spaces_and_persian_letters`, `test_second_study_replaces_the_mesh_and_keeps_its_own_scratch_folder`, `test_body_in_app_part_is_exported_in_global_coordinates`, `test_job_json_contents`, `test_face_edge_and_vertex_sizes_go_to_the_job`, `test_check_missing_edge`, `test_written_job_meshes`, `test_two_studies_restore_their_sources_settings_and_ids`, `test_deferred_export_cannot_change_ids_or_write_files`.

Delete these lines (the bodies are already included on the line before):
- `objects.materials(self.study)[0].References += [c]` (two tests) and `objects.materials(self.study)[0].References += [b]`.
- In `test_unsaved_document_is_refused_before_ids_or_files_change`: `objects.make_material(study, "Copper", [box])`.
- In `test_second_study_replaces_the_mesh_and_keeps_its_own_scratch_folder`: `objects.make_material(second, "Air", [b])`.
- In `test_selected_geometry_controls_export_and_filters_other_assignments`: both `objects.make_material(...)` lines.

Rename `test_group_names_keep_the_typed_name_when_freecad_renames_the_label` to `test_volume_names_are_body_labels_and_survive_reload`, and replace its lines from `air, a, b = ...` through `objects.update_ids(self.study)` with:

```python
        air, a, b = self.box("Air"), self.box("A", 10), self.box("B", 20)
        self.include(air, a, b)
        objects.update_ids(self.study)
```

(the rest of that test stays.)

- [ ] **Step 2: Rewrite the tests that use assignments**

In `tests/freecad_addon/test_study.py`:

`test_only_solid_bodies_can_be_picked`: replace `mat = self.mat("Copper", [box])` with `(mat,) = self.assign([box])`.

Replace `test_items_may_link_to_bodies_inside_a_part` with:

```python
    def test_items_may_link_to_bodies_inside_a_part(self):
        # plain links may not reach into an App::Part; FreeCAD warns on every recompute
        (mat,) = self.assign([self.box("A")])
        self.assertEqual(mat.getTypeIdOfProperty("Body"), "App::PropertyLinkGlobal")
        for item in (objects.make_excitation(self.study, "In", []), objects.make_mesh_size(self.study, 1.0, [])):
            self.assertTrue(item.getTypeIdOfProperty("References").endswith("Global"), item.Name)
```

`test_study_survives_save_and_reload`: replace `self.mat("Copper", [a])` with `self.assign([a])`, and after the `assertIsInstance` line add `self.assertEqual(objects.materials(study)[0].Body.Name, "A")`.

Replace `test_material_assignment_links_a_library_material_and_potential` with these four tests:

```python
    def test_assign_makes_one_assignment_per_body(self):
        a, b = self.box("A"), self.box("B", 10)
        steel, air = self.lib(), self.lib("user:air", "Air", "generic")
        first = self.assign([a, b], 2, steel)
        self.assertEqual([(m.Body, m.LibraryMaterial, m.Potential) for m in first], [(a, steel, 2), (b, steel, 2)])
        self.assertEqual([m.Label for m in first], ["A: Steel", "B: Steel"])
        self.assertFalse(hasattr(first[0], "GroupName") or hasattr(first[0], "References"))
        again = objects.assign(self.study, [b, b], air, 0)
        self.assertEqual(again, [first[1], first[1]])
        self.assertEqual(objects.materials(self.study), first)
        self.assertEqual((first[1].LibraryMaterial, first[1].Potential, first[1].Label), (air, 0, "B: Air"))
        self.assertEqual(objects.material_users(steel), [first[0]])
        self.assertEqual(objects.user_labels(steel), ["A"])
        self.assertEqual(objects.assignment_of(self.study), {"A": first[0], "B": first[1]})
        objects.unassign(self.study, [a, self.box("C", 20)])
        self.assertEqual(objects.materials(self.study), [first[1]])
        self.assertEqual(objects.library_rows(self.study)[1], (air, [(b, "")], ["Air", "generic", "user:air", "B"]))

    def test_assignment_label_follows_renamed_body_and_material(self):
        a = self.box("A")
        (m,) = self.assign([a])
        a.Label = "Core"
        m.LibraryMaterial.Label = "M330"
        objects.sync_labels(self.study)
        self.assertEqual(m.Label, "Core: M330")

    def test_assignment_of_a_deleted_body_is_ignored(self):
        a, b = self.box("A"), self.box("B", 10)
        lib = self.steel()
        self.assign([a, b], lib=lib)
        self.doc.removeObject("B")
        self.assertEqual(list(objects.assignment_of(self.study)), ["A"])
        self.assertEqual([r[2][0] for r in objects.material_rows(self.study)], ["A"])
        self.assertEqual(objects.bodies_without_material(self.study), [])
        self.assertEqual(objects.user_labels(lib), ["A", "B: Steel"])
        objects.sync_labels(self.study)  # must not fail on the orphan

    def test_body_outside_the_main_geometry_keeps_its_row(self):
        a, outside = self.box("A"), self.box("Outside", 20)
        self.include(a)
        objects.assign(self.study, [outside], self.steel(), 1)
        objects.update_ids(self.study)
        self.assertEqual(
            objects.material_rows(self.study),
            [
                (a, [(a, "")], ["A", "— none —", "1", ""]),
                (outside, [(outside, "")], ["Outside", "Steel", "–", "1"]),
            ],
        )
        self.assertEqual(objects.bodies_without_material(self.study), [a])
```

`test_library_material_survives_save_and_reload`: replace the two lines

```python
        mat = self.mat("Coil", [self.box("A")])
        mat.LibraryMaterial, mat.Potential = lib, 3
```

with `self.assign([self.box("A")], 3, lib)`. The rest stays (it reloads and checks `mat.LibraryMaterial`, `mat.Potential`).

In `test_folder_overview_rows`, replace the start up to and including the `material_rows` assertion with:

```python
        a, b, c = self.box("A"), self.box("B", 10), self.box("C", 20)
        ma, _mb = self.assign([a, b])
        exc = objects.make_excitation(self.study, "In", [(a, "Face1"), (a, "Face2")])
        size = objects.make_mesh_size(self.study, 1.5, [(a, ""), (c, "Edge1")])
        self.include(c)
        objects.update_ids(self.study)
        self.assertEqual(
            objects.material_rows(self.study),
            [
                (a, [(a, "")], ["A", "Steel", "1", "0"]),
                (b, [(b, "")], ["B", "Steel", "2", "0"]),
                (c, [(c, "")], ["C", "— none —", "3", ""]),
            ],
        )
```

keep the excitation and mesh-size assertions, change `self.assertEqual(objects.item_refs(mat), [(a, ""), (b, "")])` to `self.assertEqual(objects.item_refs(ma), [(a, "")])`, keep the `is_item` and `bodies_without_material` (`["C"]`) lines, and replace the last three lines (`d = ...`, `mat.References += [d]`, the `material_rows(...)[2]` assertion) with:

```python
        d = self.box("D", 30)
        objects.assign(self.study, [d], ma.LibraryMaterial, 4)
        self.assertEqual(objects.material_rows(self.study)[3], (d, [(d, "")], ["D", "Steel", "–", "4"]))
```

Replace `test_multiple_studies_have_independent_ownership_and_ids` with:

```python
    def test_multiple_studies_have_independent_ownership_and_ids(self):
        second = objects.make_study(self.doc, "2D", "Cross-section")
        a = self.box("A")
        (material,) = self.assign([a])
        copper = objects.make_library_material(second, json.dumps(record("user:copper", "Copper", "conductor")))
        (other,) = objects.assign(second, [a], copper, 0)
        objects.update_ids(self.study)
        self.assertIsNone(objects.find_study(self.doc))
        self.assertEqual(objects.owner_study(material), self.study)
        self.assertEqual(objects.owner_study(other), second)
        self.assertEqual(objects.owner_study(second.MeshSizesGroup), second)
        self.assertIsNone(objects.owner_study(a))  # a reference does not imply ownership
        self.assertEqual(second.MatIds, {})
        self.assertEqual(objects.assignment_of(second), {"A": other})
        self.assertEqual(len(objects.material_rows(second)), 1)
```

`test_new_study_requires_geometry_even_when_materials_exist`: replace `objects.make_material(study, "Iron", [self.box("A")])` with:

```python
        steel = objects.make_library_material(study, json.dumps(record("user:steel", "Steel", "electrical_steel", STEEL)))
        objects.assign(study, [self.box("A")], steel, 0)
```

`test_bodies_without_materials_are_meshed_and_listed` (from Task 1): append

```python
        self.assign([a])
        self.assertEqual(objects.bodies_without_material(self.study), [b])
```

In `tests/freecad_addon/test_studymaterials.py`:

Replace `test_delete_is_refused_while_an_assignment_uses_the_material` with:

```python
    def test_delete_is_refused_while_an_assignment_uses_the_material(self):
        self.repo.create(material("user:air", "Air", AIR))
        (lib,) = objects.library_materials(self.study)
        a = self.box("A")
        objects.assign(self.study, [a], lib, 0)
        self.assertFalse(self.repo.is_deletable("user:air"))
        with self.assertRaisesRegex(ReadOnlyMaterialError, "used by: A$"):
            self.repo.delete("user:air")
        objects.unassign(self.study, [a])
        self.repo.delete("user:air")
        self.assertEqual(objects.library_materials(self.study), [])
```

In `StudyRowsTest`:
- `test_rows_follow_mat_ids_with_body_names_and_potential`: replace the two lines `mat = objects.make_material(...)` / `mat.LibraryMaterial, mat.Potential = lib, 1` with `objects.assign(self.study, [a, b], lib, 1)`.
- `test_body_without_an_assignment_is_named`: replace `objects.make_material(self.study, "Gap", [a]).LibraryMaterial = lib` with `objects.assign(self.study, [a], lib, 0)`.
- `test_assignment_without_a_material_is_named`: replace the body with:

```python
        a = self.box("A")
        self.study.MainObjects = [a]
        (lib,) = studymaterials.import_materials(self.study, [material("user:air", "Air", AIR)])
        objects.assign(self.study, [a], lib, 0)[0].LibraryMaterial = None
        with self.assertRaisesRegex(StudyError, "no material from the Material Library: A$"):
            studymaterials.study_material_rows(self.study)
```

- `test_deleted_library_material_is_reported`: replace `objects.make_material(self.study, "Gap", [a]).LibraryMaterial = lib` with `objects.assign(self.study, [a], lib, 0)`.

- [ ] **Step 3: Run them to see them fail**

Run: `pixi run pytest tests/freecad_addon/test_study.py tests/freecad_addon/test_studymaterials.py -v`
Expected: FAIL with `AttributeError: module 'emsolution.objects' has no attribute 'assign'` (and similar).

- [ ] **Step 4: Implement the model**

`freecad_addon/emsolution/objects.py`, replace class `Material`:

```python
class Material(_Proxy):
    """An assignment: one body, its Material Library entry and its potential region. Made by assign()."""

    def __init__(self, obj):
        obj.Proxy = self
        obj.addProperty("App::PropertyLinkGlobal", "Body", "EMSolution", "Body made of this material")
        obj.addProperty("App::PropertyLink", "LibraryMaterial", "EMSolution", "Material from the Material Library")
        obj.addProperty("App::PropertyIntegerConstraint", "Potential", "EMSolution", "POTENTIAL: 0 total, 1+ reduced")
        obj.Potential = (0, 0, 1000000, 1)
```

Delete `make_material`. After `make_library_material`, add:

```python
def assignment_of(study):
    """{body Name: assignment} for the Study's assignments whose body still exists."""
    return {m.Body.Name: m for m in materials(study) if m.Body is not None}


def assignment_label(m):
    """The tree label "<body>: <material>"; FreeCAD keeps labels unique, so it cannot be the body's label."""
    lib = m.LibraryMaterial.Label if m.LibraryMaterial else NO_MATERIAL
    return f"{m.Body.Label}: {lib}" if m.Body else m.Label


def assign(study, bodies, lib, potential):
    """Give each body lib and potential, updating its assignment or adding one. Returns them in body order."""
    have = assignment_of(study)
    out = []
    for body in bodies:
        m = have.get(body.Name)
        if m is None:
            m = _add(study, "MaterialsGroup", Material, body.Label)
            m.Body = body
            if getattr(m, "ViewObject", None) is not None:  # GUI running
                from . import taskpanels

                taskpanels.ViewProviderItem(m.ViewObject)
            have[body.Name] = m
        m.LibraryMaterial, m.Potential = lib, potential
        m.Label = assignment_label(m)
        out.append(m)
    return out


def unassign(study, bodies):
    """Remove the assignments of bodies; bodies without one are skipped."""
    have = assignment_of(study)
    for body in bodies:
        m = have.pop(body.Name, None)
        if m is not None:
            study.Document.removeObject(m.Name)


def sync_labels(study):
    """Rewrite assignment labels after a body or material was renamed."""
    for m in materials(study):
        label = assignment_label(m)
        if m.Label != label:
            m.Label = label
```

After `material_users`, add:

```python
def user_labels(lib):
    """For messages: the body label of each assignment using lib, or the assignment label if the body is gone."""
    return [m.Body.Label if m.Body else m.Label for m in material_users(lib)]
```

Replace `item_refs`:

```python
def item_refs(item):
    """[(body, sub)] of a Material, Excitation or Mesh Size; sub "" = the whole body."""
    if isinstance(item.Proxy, Material):
        return [(item.Body, "")] if item.Body else []
    return [(b, s) for b, subs in item.References for s in subs]
```

Replace `material_rows`:

```python
def material_rows(study):
    """Rows for the Materials panel: (body, refs, [body, material, MAT_ID, POTENTIAL]).

    Every main-geometry body, then bodies outside it that still have an assignment.
    """
    have = assignment_of(study)
    main = _main_bodies(study)
    inside = {b.Name for b in main}
    rows = []
    for b in main + [m.Body for m in have.values() if m.Body.Name not in inside]:
        m = have.get(b.Name)
        lib = m.LibraryMaterial.Label if m and m.LibraryMaterial else NO_MATERIAL
        rows.append((b, [(b, "")], [b.Label, lib, study.MatIds.get(b.Name, "–"), str(m.Potential) if m else ""]))
    return rows
```

In `library_rows`, replace the two lines building `refs` and the row with:

```python
        refs = [(m.Body, "") for m in users if m.Body]
        rows.append((lib, refs, [lib.Label, lib.Family, lib.MaterialId, ", ".join(user_labels(lib))]))
```

Replace `bodies_without_material`:

```python
def bodies_without_material(study):
    """Main-geometry bodies without an assignment."""
    have = assignment_of(study)
    return [b for b in _main_bodies(study) if b.Name not in have]
```

`freecad_addon/emsolution/studymaterials.py`:
- In `study_material_rows`, replace `have = {b.Name: m for m in objects.materials(study) for b in m.References}` with `have = objects.assignment_of(study)`.
- In `StudyMaterialRepository.delete`, replace the `raise` line with:

```python
            raise ReadOnlyMaterialError(f"{obj.Label} is used by: " + ", ".join(objects.user_labels(obj)))
```

- [ ] **Step 5: Check nothing else uses the old properties**

Grep for `make_material|GroupName|\.References` in `freecad_addon/emsolution/objects.py`, `jobwriter.py`, `studymaterials.py`.
Expected: `GroupName` only in `_Named`, `display_name`, `_add`; `.References` only for Excitation and Mesh Size code; no `make_material`.

- [ ] **Step 6: Run the addon tests**

Run: `pixi run pytest tests/freecad_addon -v`
Expected: all PASS.

- [ ] **Step 7: Format, lint, commit**

```bash
pixi run ruff format freecad_addon/emsolution/objects.py freecad_addon/emsolution/studymaterials.py tests/freecad_addon/test_study.py tests/freecad_addon/test_studymaterials.py
pixi run lint
git add freecad_addon/emsolution/objects.py freecad_addon/emsolution/studymaterials.py tests/freecad_addon/test_study.py tests/freecad_addon/test_studymaterials.py
git commit -m "Store one link-based material assignment per body

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: Assign dialog, Assign Material command and Materials panel

**Files:**
- Modify: `freecad_addon/emsolution/taskpanels.py`
- Modify: `freecad_addon/emsolution/commands.py`
- Test: `tests/freecad_addon/gui_smoke.py`

**Interfaces:**
- Consumes: `objects.assign`, `objects.unassign`, `objects.assignment_of`, `objects.sync_labels`, `objects.user_labels`, `objects.library_materials`, `objects.NO_MATERIAL`, `objects.material_rows` rows whose item is the body (Task 2).
- Produces (in `taskpanels`): `apply_assignment(study, bodies, lib, potential)` (one transaction; `lib=None` removes), `AssignDialog(study, bodies, parent=None)` with attributes `material` (`QComboBox`, data = library object Name or `""`) and `potential` (`QSpinBox`), `ask_assignment(study, bodies)` (runs the dialog modally; the smoke test replaces it).

- [ ] **Step 1: Update the smoke test**

All edits in `tests/freecad_addon/gui_smoke.py`.

a. Replace

```python
    commands.ask_text = lambda title, label, default: {"Material": "Copper", "Excitation": "Terminal In"}[title]
```

with

```python
    commands.ask_text = lambda title, label, default: {"Excitation": "Terminal In"}[title]
    asked = []  # bodies the Assign dialog was opened for; the modal dialog is driven directly below
    taskpanels.ask_assignment = lambda study, bodies: asked.append([b.Name for b in bodies])
```

b. In the commands block: delete `Gui.Control.closeDialog()` right after `Gui.runCommand("EMS_Material")`. Replace

```python
    (mat,) = objects.materials(study)
```

with

```python
    assert asked == [["A", "B"]], asked
    assert objects.materials(study) == [], "the command assigned before the dialog"
```

delete `assert [b.Name for b in mat.References] == ["A", "B"], mat.References`, change `for item in (mat, exc, size, fine):` to `for item in (exc, size, fine):`, and in the visibility check replace `mat` with `exc` (`Gui.Selection.addSelection(doc.Name, exc.Name)` and `assert exc.ViewObject.isVisible(), "the eye hid an item"`).

b2. In the `first_column` dict, change the key `"Assignment": "Materials"` to `"Body": "Materials"` (the Materials table's first header).

c. Delete the whole "panel ok" block: from `panel = taskpanels.ItemPanel(mat)` (the one followed by `panel.name.setText("Iron")`) through `log.append("panel ok")`.

d. Replace the Materials-row double-click block

```python
    select(study.MaterialsGroup.Name)
    shown_folders()["Materials"].cellDoubleClicked.emit(1, 0)
    for _ in range(5):
        Gui.updateGui()
    assert task_buttons() == ["Cancel", "OK"], ("item panel did not open from the row", task_buttons())
    assert shown_folders() == {}, "folder panel shown beside the edit dialog"
    Gui.Control.closeDialog()
    for _ in range(5):
        Gui.updateGui()
    assert list(shown_folders()) == ["Materials"], "folder panel not back after the edit"
```

with

```python
    select(study.MaterialsGroup.Name)
    shown_folders()["Materials"].cellDoubleClicked.emit(1, 0)
    assert asked[-1] == ["B"], ("Assign dialog not asked for the row's body", asked)
    select(study.ExcitationsGroup.Name)
    shown_folders()["Excitations"].cellDoubleClicked.emit(0, 0)
    for _ in range(5):
        Gui.updateGui()
    assert task_buttons() == ["Cancel", "OK"], ("item panel did not open from the row", task_buttons())
    assert shown_folders() == {}, "folder panel shown beside the edit dialog"
    Gui.Control.closeDialog()
    for _ in range(5):
        Gui.updateGui()
    assert list(shown_folders()) == ["Excitations"], "folder panel not back after the edit"
```

e. Replace the block

```python
    panel = taskpanels.ItemPanel(mat)
    panel.material.setCurrentIndex(panel.material.findData(lib.Name))
    panel.potential.setValue(2)
    Gui.Control.showDialog(panel)
    panel.accept()
    assert mat.LibraryMaterial == lib and mat.Potential == 2, (mat.LibraryMaterial, mat.Potential)
    select(study.MaterialLibraryGroup.Name)
    assert shown_folders()["Material Library"].item(0, 3).text() == mat.Label
```

with

```python
    dialog = taskpanels.AssignDialog(study, [doc.A, doc.B])
    assert dialog.material.currentData() == lib.Name, "an unassigned body did not default to the first material"
    dialog.potential.setValue(2)
    dialog.accept()
    mat, mat_b = objects.materials(study)
    assert (mat.Body, mat.LibraryMaterial, mat.Potential, mat.Label) == (doc.A, lib, 2, "A: Air"), mat.Label
    assert doc.UndoNames[0] == "Assign material", doc.UndoNames
    dialog = taskpanels.AssignDialog(study, [doc.B])
    assert (dialog.material.currentData(), dialog.potential.value()) == (lib.Name, 2)
    dialog.material.setCurrentIndex(dialog.material.findData(""))
    dialog.accept()
    assert objects.materials(study) == [mat] and doc.UndoNames[0] == "Remove material", doc.UndoNames
    doc.undo()
    assert [m.Body for m in objects.materials(study)] == [doc.A, doc.B], "undo did not bring the assignment back"
    select(study.MaterialsGroup.Name)
    shown_folders()["Materials"].selectAll()
    (assign_button,) = [
        b for b in Gui.getMainWindow().findChildren(QtWidgets.QPushButton) if b.isVisible() and b.text() == "Assign…"
    ]
    assign_button.click()
    assert asked[-1] == ["A", "B"], asked
    select(study.MaterialLibraryGroup.Name)
    assert shown_folders()["Material Library"].item(0, 3).text() == "A, B"
```

f. Add, right after the `assign_button.click()` assertion, the "— none —" on unassigned bodies case (Review Focus 5):

```python
    extra = doc.addObject("Part::Box", "Extra")
    doc.recompute()
    dialog = taskpanels.AssignDialog(study, [extra])
    dialog.material.setCurrentIndex(dialog.material.findData(""))
    dialog.accept()
    assert objects.assignment_of(study).get("Extra") is None
    doc.removeObject("Extra")
```

g. In the highlight block: change

```python
    select(mat.Name)
    assert shown_refs[-1] == [("A", ""), ("B", "")], shown_refs
```

to

```python
    select(mat.Name)
    assert shown_refs[-1] == [("A", "")], shown_refs
```

and delete the lines after `assert shown_refs[-1] == [("B", "")], shown_refs` up to and including `Gui.Control.closeDialog()` (the Materials double-click no longer opens a task dialog), keeping `highlight.show = real_show` and `log.append("highlight ok")`.

h. In the workbench block, change `Gui.Control.showDialog(taskpanels.ItemPanel(mat))` to `Gui.Control.showDialog(taskpanels.ItemPanel(exc))`.

i. Near the end, replace

```python
    mat.References = [doc.B]
    view.refresh()
    assert "A (A)" in view.diagnostics.text()
    assert view.run_button.isEnabled(), "missing materials disabled generation"
    mat.References = [doc.A, doc.B]
    view.refresh()
```

with

```python
    taskpanels.apply_assignment(study, [doc.A], None, 0)
    view.refresh()
    assert view.diagnostics.text() == "", view.diagnostics.text()  # meshing does not need materials
    assert view.run_button.isEnabled(), "a body without a material disabled generation"
```

and change `log.append("selected geometry mesh and missing-material validation ok")` to `log.append("selected geometry mesh without materials ok")`.

- [ ] **Step 2: Implement the dialog and helpers**

`freecad_addon/emsolution/taskpanels.py`, after `selected_mesh_refs()` add:

```python
def apply_assignment(study, bodies, lib, potential):
    """Assign lib and potential to bodies, or remove their assignments when lib is None; one undo step."""
    doc = study.Document
    doc.openTransaction("Remove material" if lib is None else "Assign material")
    if lib is None:
        objects.unassign(study, bodies)
    else:
        objects.assign(study, bodies, lib, potential)
    doc.commitTransaction()
    doc.recompute()


class AssignDialog(QtWidgets.QDialog):
    """Material and POTENTIAL for bodies; "— none —" removes their assignments."""

    def __init__(self, study, bodies, parent=None):
        super().__init__(parent or Gui.getMainWindow())
        self.study, self.bodies = study, list(bodies)
        self.setWindowTitle("Assign Material")
        layout = QtWidgets.QFormLayout(self)
        names = ", ".join(b.Label for b in self.bodies[:5])
        if len(self.bodies) > 5:
            names += f" and {len(self.bodies) - 5} more"
        shown = QtWidgets.QLabel(names)
        shown.setWordWrap(True)
        layout.addRow("Bodies", shown)
        libraries = objects.library_materials(study)
        self.material = QtWidgets.QComboBox()
        for lib in libraries:
            self.material.addItem(lib.Label, lib.Name)
        self.material.addItem(objects.NO_MATERIAL, "")
        self.potential = QtWidgets.QSpinBox()
        self.potential.setRange(0, 1000000)
        current = objects.assignment_of(study).get(self.bodies[0].Name)
        if current is not None:
            lib = current.LibraryMaterial
            self.material.setCurrentIndex(self.material.findData(lib.Name if lib else ""))
            self.potential.setValue(current.Potential)
        layout.addRow("Material", self.material)
        layout.addRow("POTENTIAL", self.potential)
        if not libraries:
            note = QtWidgets.QLabel("The Material Library is empty: import materials from its folder first.")
            note.setWordWrap(True)
            layout.addRow(note)
        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def accept(self):
        name = self.material.currentData()
        lib = self.study.Document.getObject(name) if name else None
        apply_assignment(self.study, self.bodies, lib, self.potential.value())
        super().accept()


def ask_assignment(study, bodies):
    AssignDialog(study, bodies).exec()
```

- [ ] **Step 3: Wire the Materials panel**

In `FolderView.__init__`:
- Change the Materials header line to:

```python
            objects.MaterialsFolder: (["Body", "Material", "MAT_ID", "POTENTIAL"], objects.material_rows),
```

- At the very start of `__init__`, after `self.study = study`, add:

```python
        if isinstance(folder.Proxy, objects.MaterialsFolder):
            objects.sync_labels(study)  # the tree shows "<body>: <material>"
```

- Replace the `if isinstance(folder.Proxy, objects.MaterialsFolder):` block at the end with:

```python
        if isinstance(folder.Proxy, objects.MaterialsFolder):
            assign = QtWidgets.QPushButton("Assign…")
            assign.setToolTip("Give the selected rows' bodies a material (Ctrl/Shift to select several rows)")
            assign.clicked.connect(self.assign_rows)
            layout.addWidget(assign)
            bodies = objects.bodies_without_material(study)
            if bodies:
                missing = QtWidgets.QLabel(
                    "No material (the input file needs one for every body): " + ", ".join(b.Label for b in bodies)
                )
                missing.setWordWrap(True)
                missing.setStyleSheet("color: #c00000")
                layout.addWidget(missing)
```

Add a method next to `selected_items`:

```python
    def assign_rows(self):
        bodies = self.selected_items()
        if not bodies:
            return warn("Select one or more rows first.")
        ask_assignment(self.study, bodies)
        self.fill()
```

Replace `open_item`:

```python
    def open_item(self, row, _column):
        item = self.rows[row][0]
        if isinstance(getattr(item, "Proxy", None), objects.LibraryMaterial):
            from . import materialstandins

            materialstandins.open_editor(self.study, item.MaterialId)
        elif self.study.Dimension != "3D":
            return
        elif isinstance(self.folder_proxy, objects.MaterialsFolder):
            ask_assignment(self.study, [item])
            self.fill()
        else:
            Gui.Control.showDialog(ItemPanel(item))
```

and in `__init__` store the proxy: add `self.folder_proxy = folder.Proxy` next to `self.study = study`. (Material rows hold bodies, whose `Proxy` may not exist — hence `getattr`.)

- [ ] **Step 4: View provider, item panel, library delete message**

`ViewProviderItem.doubleClicked`:

```python
    def doubleClicked(self, vobj):
        obj = vobj.Object
        if isinstance(obj.Proxy, objects.Material):
            if obj.Body is not None:
                ask_assignment(objects.owner_study(obj), [obj.Body])
        else:
            Gui.Control.showDialog(ItemPanel(obj))
        return True
```

`ItemPanel` now serves Excitations and Mesh Sizes only:
- Docstring: `"""Edit name, size (Mesh Size only) and references of an Excitation or Mesh Size."""`
- Replace the `self.bodies_only = ...` / `if self.bodies_only: ... elif ...: ... else: ...` block with:

```python
        if isinstance(obj.Proxy, objects.Excitation):
            self.pick, label = selected_faces, "Faces"
        else:
            self.pick, label = selected_mesh_refs, "Bodies, faces,\nedges, vertices"
```

- Delete the `self.material = self.potential = None` line and the whole `if isinstance(obj.Proxy, objects.Material):` block that builds the combo and spin box.
- In `accept`, delete the `if self.material is not None:` block, and replace

```python
        if self.bodies_only:
            self.obj.References = [b for b, _ in self.current]
        else:
            self.obj.References = list(self.current)
```

with `self.obj.References = list(self.current)`.

`ViewProviderLibraryMaterial.onDelete`: replace the `warn(...)` line with

```python
            warn(f"{vobj.Object.Label} is used by: " + ", ".join(objects.user_labels(vobj.Object)))
```

- [ ] **Step 5: The command**

`freecad_addon/emsolution/commands.py`, replace class `AddMaterial` with:

```python
class AssignMaterial(_StudyCommand):
    def GetResources(self):
        return {
            "Pixmap": icon("material"),
            "MenuText": "Assign Material",
            "ToolTip": "Give the selected bodies a material from the Material Library",
        }

    def Activated(self):
        study = assignment_study()
        if study is None:
            return
        bodies = taskpanels.selected_bodies()
        if not bodies:
            return warn("Select one or more bodies first.")
        taskpanels.ask_assignment(study, bodies)
```

and in `COMMANDS` change `"EMS_Material": AddMaterial()` to `"EMS_Material": AssignMaterial()` (keep the key; `InitGui.py` uses it).

- [ ] **Step 6: Unit tests still pass**

Run: `pixi run pytest tests/freecad_addon -v`
Expected: all PASS.

- [ ] **Step 7: Run the GUI smoke test**

Run: `pixi run freecad tests\freecad_addon\gui_smoke.py`, then read `%TEMP%\ems_gui_smoke.txt` (PowerShell: `Get-Content "$env:TEMP\ems_gui_smoke.txt"`).
Expected: last line `PASS`. On `FAIL`, the traceback above it names the failing assertion; fix the code or, if the smoke step itself is wrong, fix the step and say so in the commit message.

- [ ] **Step 8: Format, lint, commit**

```bash
pixi run ruff format freecad_addon/emsolution/taskpanels.py freecad_addon/emsolution/commands.py tests/freecad_addon/gui_smoke.py
pixi run lint
git add freecad_addon/emsolution/taskpanels.py freecad_addon/emsolution/commands.py tests/freecad_addon/gui_smoke.py
git commit -m "Assign a material to many bodies at once from the selection or the Materials panel

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: Final check

- [ ] **Step 1:** `pixi run pytest tests/freecad_addon -v` — all PASS.
- [ ] **Step 2:** `pixi run lint` — passes. `pixi run ruff format --check freecad_addon/emsolution/objects.py freecad_addon/emsolution/jobwriter.py freecad_addon/emsolution/studymaterials.py freecad_addon/emsolution/taskpanels.py freecad_addon/emsolution/commands.py` — no changes.
- [ ] **Step 3:** Grep the addon for `make_material`, `GroupName` on materials, `.References` on materials, `"Assignment"` header, `"Run Mesh will stop"` — none left.
- [ ] **Step 4:** By hand in FreeCAD (`pixi run freecad`): select three bodies with Ctrl, Assign Material → pick a material → OK; the Materials folder shows three rows; select two rows, Assign… → "— none —" → OK; Ctrl+Z restores them.
