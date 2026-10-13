# Study Material Library Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give FreeCAD Studies a Material Library of editable material copies from EMS Material Manager, link per-body `MAT_ID` assignments to them, tag the mesh with `MAT_ID` / `SMAT_ID`, and provide a builder for the input file's `16_1_3D_Element_Properties` section.

**Architecture:** `objects.py` gains a Material Library folder with `LibraryMaterial` objects (canonical JSON in a hidden string property) and `Material` assignments gain a `LibraryMaterial` link and `Potential`. A new `studymaterials.py` adapts those objects to the `ems_material` `MaterialRepository` protocol and builds 16.1 entries through the library's `EMSolutionInputAdapter`. Temporary GUI stand-ins (`materialstandins.py`) provide a picker and open the library's own editor window on the Study.

**Tech Stack:** FreeCAD 1.1.0 (pixi env, Python 3.11, PySide6), `ems-material-manager` 0.1.x (PyPI), gmsh, unittest run by pytest.

**Spec:** [docs/superpowers/specs/2026-10-13-study-material-library-design.md](../specs/2026-10-13-study-material-library-design.md)

## Global Constraints

- Run everything through pixi: `pixi run pytest ...`, `pixi run python ...`. Never `pip install`.
- Ruff only, line length **120**, double quotes. Format only files you changed: `pixi run ruff format <files>`. `pixi run lint` must pass.
- **Never sort or reorder imports.** Add new imports next to related ones.
- `objects.py`, `geometry.py`, `jobwriter.py` and `mesher.py` must not import `ems_material`. `mesher.py` must not import FreeCAD.
- No back-compat: old properties are replaced, not migrated; no `onDocumentRestored` upgrade code.
- Commit messages end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Never use `--no-verify`.
- User-visible names: folder **Material Library**; ID column words **MAT_ID** / **SMAT_ID**; empty material shown as **— none —**.
- Dependency: `ems-material-manager>=0.1,<0.2`; `pyproject.toml` and `pixi.lock` committed together.

## Review Focus

1. **A Library Material deleted while assignments link to it.** The tree delete is refused with the names of the assignments (Task 6). A scripted `doc.removeObject` clears the link, and the 16.1 builder then names the assignment instead of crashing (Task 5 test `test_deleted_library_material_is_reported`).
2. **Importing a material whose ID is already in the Study.** Nothing is created and the error names the ID; the picker greys such rows out (Task 4 test `test_import_refuses_ids_already_in_the_study`, Task 6 smoke).
3. **Non-ASCII material names** (Japanese or Persian) survive save and reload in `Record` and in the tree label (Task 3 test `test_library_material_survives_save_and_reload`).
4. **Materials with no magnetic data** (copper with only conductivity) still give a valid 16.1 entry with `MU` 1.0 and no curves (Task 5 test `test_material_without_magnetic_data_is_linear`).
5. **Undo after a repository write** restores the previous record in one step and does not leave half-written objects (Task 4 test `test_each_write_is_one_undo_step`).

---

## File Structure

| File | Responsibility |
|---|---|
| `freecad_addon/emsolution/objects.py` (modify) | Study folders, `LibraryMaterial`, `Material` assignment properties, `MatIds` / `SmatIds` tables, row helpers. No `ems_material`. |
| `freecad_addon/emsolution/geometry.py` (modify) | Remove the Materials main mode. |
| `freecad_addon/emsolution/jobwriter.py` (modify) | Checks without the Materials mode; job fields `mat_id` / `smat_id`. |
| `freecad_addon/emsolution/mesher.py` (modify) | Read `mat_id` / `smat_id`. |
| `freecad_addon/emsolution/studymaterials.py` (create) | `StudyMaterialRepository`, `import_materials`, `library_root`, `study_material_rows`, `material_properties`. No GUI. |
| `freecad_addon/emsolution/materialstandins.py` (create, temporary) | `MaterialPicker` dialog, `pick_materials`, `open_editor`. Deleted when the upstream widgets ship. |
| `freecad_addon/emsolution/taskpanels.py` (modify) | Library folder panel, `ViewProviderLibraryMaterial`, Material item panel combo and POTENTIAL, ID dialog words. |
| `freecad_addon/emsolution/commands.py` (modify) | Add Material opens the item panel. |
| `tests/freecad_addon/materialdata.py` (create) | Canonical material dicts shared by the tests. |
| `tests/freecad_addon/test_study.py` (modify) | Manual main mode, renamed IDs, Material Library objects. |
| `tests/freecad_addon/test_mesher.py` (modify) | Renamed job fields. |
| `tests/freecad_addon/test_studymaterials.py` (create) | Repository, import, root lookup and builder tests. |
| `tests/freecad_addon/gui_smoke.py` (modify) | GUI flow with the Material Library. |
| `pyproject.toml`, `pixi.lock` (modify) | Dependency. |

---

### Task 1: Remove the Materials main mode and the old-file restore code

**Files:**
- Modify: `freecad_addon/emsolution/objects.py` (class `Study`, `make_study`, `bodies_without_material`, `volume_keys`, `surface_keys`, `id_rows`)
- Modify: `freecad_addon/emsolution/geometry.py:87-101` (`region`)
- Modify: `freecad_addon/emsolution/jobwriter.py:36-115` (`check`)
- Modify: `freecad_addon/emsolution/taskpanels.py:216-220, 360-361`
- Test: `tests/freecad_addon/test_study.py`, `tests/freecad_addon/gui_smoke.py`

**Interfaces:**
- Consumes: nothing new.
- Produces: `Study.MainMode` / `MovingMode` choices are exactly `["Unassigned", "Container", "Manual"]`. `objects.volume_keys(study)` returns the main-region body Names. `jobwriter.check(study)` keeps its return value `(volumes, surfaces, elements)`. Test helpers `StudyTest.include(*bodies)` and `StudyTest.mat(label, bodies)` exist for later tasks.

- [ ] **Step 1: Switch the test fixture to Manual mode and add the helpers**

In `tests/freecad_addon/test_study.py`, replace the `setUp` line `self.study.MainMode = "Materials"  # retain coverage of the legacy workflow` with:

```python
        self.study.MainMode = "Manual"  # bodies join the main geometry through self.mat()
```

Add these helpers right after `box()`:

```python
    def include(self, *bodies):
        """Add bodies to the Study's main geometry (Manual mode)."""
        self.study.MainObjects = list(dict.fromkeys([*self.study.MainObjects, *bodies]))

    def mat(self, label, bodies):
        """A material on bodies that are also in the main geometry."""
        self.include(*bodies)
        return objects.make_material(self.study, label, bodies)
```

- [ ] **Step 2: Move the tests onto the helpers**

In `test_study.py`, replace every `objects.make_material(self.study, ` with `self.mat(` **except** in these tests, which keep `objects.make_material(self.study, ...)` because they set their own geometry source: `test_selected_geometry_controls_export_and_filters_other_assignments`, `test_selection_ids_survive_material_changes_and_follow_live_membership`, `test_items_may_link_to_bodies_inside_a_part`.

Then make these edits:

- `test_deleted_body_id_is_not_reused`: after `c = self.box("C", 20)` add `self.include(c)`.
- `test_set_id_refuses_duplicates_and_raises_counter`: after `c = self.box("C", 20)` add `self.include(c)`.
- `test_new_volume_ids_skip_numbers_used_by_surfaces`: before `objects.materials(self.study)[0].References += [b]` add `self.include(b)`.
- `test_folder_overview_rows`: after the line `size = objects.make_mesh_size(...)` add `self.include(c)` (C is main geometry without a material).
- `test_unsaved_document_is_refused_before_ids_or_files_change`: replace `study.MainMode = "Materials"` with `study.MainMode = "Manual"`, and after `doc.recompute()` add `study.MainObjects = [box]`.
- `test_second_study_replaces_the_mesh_and_keeps_its_own_scratch_folder`: replace the two lines `second.MainMode = "Materials"` and `objects.make_material(second, "Air", [self.box("B", 10)])` with:

```python
        b = self.box("B", 10)
        second.MainMode, second.MainObjects = "Manual", [b]
        objects.make_material(second, "Air", [b])
```

- `test_two_studies_restore_their_sources_settings_and_ids`: delete the two lines `self.assertNotIn("LegacyOutput", first.PropertiesList)` and `self.assertNotIn("OutputFolder", first.PropertiesList)`.
- Delete these tests entirely: `test_new_study_has_no_output_properties`, `test_check_no_materials`, `test_check_excitation_on_body_without_material`, `test_check_mesh_size_on_body_without_material`, `test_check_part_container_is_refused`, `test_check_link_is_refused`, `test_old_study_upgrade_preserves_settings_ids_and_drops_output_properties`.

In `tests/freecad_addon/gui_smoke.py` (not run until Task 6, but keep it consistent now):
- replace `study.MainMode = "Materials"  # legacy workflow remains supported` with
  `study.MainMode, study.MainObjects = "Manual", [doc.A, doc.B]`;
- replace `assert study.MainMode == "Materials"` with `assert study.MainMode == "Manual"`.

Add this test in the `# --- tree objects ---` section:

```python
    def test_main_geometry_has_no_materials_mode(self):
        for prop in ("MainMode", "MovingMode"):
            self.assertEqual(self.study.getEnumerationsOfProperty(prop), ["Unassigned", "Container", "Manual"])
        self.assertFalse(hasattr(self.study.Proxy, "onDocumentRestored"))
```

- [ ] **Step 3: Run the tests to see the new test fail**

Run: `pixi run pytest tests/freecad_addon/test_study.py -q`
Expected: FAIL in `test_main_geometry_has_no_materials_mode` (the enumeration still contains `"Materials"`). Other failures are allowed at this point.

- [ ] **Step 4: Rewrite `Study` without the legacy setup**

In `freecad_addon/emsolution/objects.py`, replace the whole `class Study` (from `class Study(_Proxy):` up to and including `onDocumentRestored`) with:

```python
class Study(_Proxy):
    def __init__(self, obj):
        obj.Proxy = self
        obj.addProperty("App::PropertyEnumeration", "MshVersion", "EMSolution", "Gmsh file format version (ASCII)")
        obj.MshVersion = ["4.1", "2.2"]
        obj.addProperty("App::PropertyMap", "VolumeIds", "IDs", "Body Name -> volume ID")
        obj.addProperty("App::PropertyMap", "SurfaceIds", "IDs", "'Excitation Name|Body Name' -> surface ID")
        obj.addProperty("App::PropertyInteger", "NextVolumeId", "IDs", "Next volume ID")
        obj.NextVolumeId = 1
        obj.addProperty("App::PropertyInteger", "NextSurfaceId", "IDs", "Next surface ID")
        obj.NextSurfaceId = 1001
        for prop, _ in FOLDERS:
            obj.addProperty("App::PropertyLink", prop, "EMSolution", "")
        obj.addProperty("App::PropertyLink", "MeshResult", "EMSolution", "")
        for prop in ("VolumeIds", "SurfaceIds", "NextVolumeId", "NextSurfaceId"):
            obj.setEditorMode(prop, 1)  # read-only: edit through the ID table
        for prop in [g for g, _ in FOLDERS] + ["MeshResult"]:
            obj.setEditorMode(prop, 2)  # hidden
        obj.addProperty("App::PropertyEnumeration", "Dimension", "Setup")
        obj.Dimension = ["3D", "2D"]
        obj.setEditorMode("Dimension", 1)  # choose at creation; assignments depend on it
        obj.addProperty("App::PropertyEnumeration", "Movement", "Setup")
        obj.Movement = ["No movement", "Sliding motion"]
        for region in ("Main", "Moving"):
            mode, source, refs = region + "Mode", region + "Source", region + "Objects"
            obj.addProperty("App::PropertyEnumeration", mode, "Geometry")
            setattr(obj, mode, ["Unassigned", "Container", "Manual"])
            obj.addProperty("App::PropertyLinkGlobal", source, "Geometry")
            obj.addProperty("App::PropertyLinkListGlobal", refs, "Geometry")
            for prop in (mode, source, refs):
                obj.setEditorMode(prop, 2)  # edit together in the Study panel
```

In `make_study`, delete the two lines:

```python
    if dimension == "2D":
        study.MainMode = "Unassigned"
```

- [ ] **Step 5: Simplify the ID key and row helpers**

In `objects.py`, replace `bodies_without_material`, `volume_keys`, `surface_keys` and `id_rows` with:

```python
def bodies_without_material(study):
    """Main-geometry bodies without a material."""
    have = {b.Name for m in materials(study) for b in m.References}
    return [b for b in _main_bodies(study) if b.Name not in have]


def _main_bodies(study):
    from . import geometry

    return geometry.region(study, "Main")[0]


def volume_keys(study):
    return [b.Name for b in _main_bodies(study)]


def surface_keys(study):
    included = set(volume_keys(study))
    return list(
        dict.fromkeys(
            f"{e.Name}|{b.Name}" for e in excitations(study) for b, _ in subs_by_body(e) if b.Name in included
        )
    )
```

```python
def id_rows(study):
    """Rows for the ID table dialog: (table, key, name, id), volumes first."""
    rows = []
    material_of = {b.Name: m for m in materials(study) for b in m.References}
    for name in volume_keys(study):
        if name in study.VolumeIds:
            body = study.Document.getObject(name)
            mat = material_of.get(name)
            label = item_name(mat, body) if mat else f"No material: {body.Label}"
            rows.append(("VolumeIds", name, label, int(study.VolumeIds[name])))
    for e in excitations(study):
        for b, _ in subs_by_body(e):
            key = f"{e.Name}|{b.Name}"
            if key in study.SurfaceIds:
                rows.append(("SurfaceIds", key, item_name(e, b), int(study.SurfaceIds[key])))
    return rows
```

- [ ] **Step 6: Remove the mode from `geometry.region`**

In `freecad_addon/emsolution/geometry.py`, in `region`, replace

```python
    if mode == "Materials":
        roots = [b for m in objects.materials(study) for b in m.References]
    elif mode == "Container":
```

with

```python
    if mode == "Container":
```

- [ ] **Step 7: Rewrite `jobwriter.check` for main geometry only**

In `freecad_addon/emsolution/jobwriter.py`, replace the body of `check` from `unavailable = geometry.export_unavailable(study)` down to (and including) the loop `for e, b, faces in surfaces: _check_subs("Excitation", e, b, faces)` with:

```python
    unavailable = geometry.export_unavailable(study)
    if unavailable:
        raise StudyError(unavailable)
    bodies, _, errors = geometry.setup(study)
    if errors:
        raise StudyError("\n".join(errors))
    material_of = {b.Name: (b, []) for b in bodies}  # main geometry order
    for m in objects.materials(study):
        for b in m.References:
            if b.Name in material_of:
                material_of[b.Name][1].append(m)
    missing = [b for b, ms in material_of.values() if not ms]
    if missing:
        raise StudyError(
            "Main geometry has bodies with no material: "
            + ", ".join(f"{b.Label} ({b.Name})" for b in missing)
            + ". Assign one material to each body."
        )
    for b, ms in material_of.values():
        if len(ms) > 1:
            raise StudyError(f"Body {b.Label} has more than one material: " + ", ".join(m.Label for m in ms))
    surfaces = [
        (e, b, faces) for e in objects.excitations(study) for b, faces in objects.subs_by_body(e) if b.Name in material_of
    ]
    sized = [
        (s, b, subs) for s in objects.mesh_sizes(study) for b, subs in objects.subs_by_body(s) if b.Name in material_of
    ]
    for e, b, faces in surfaces:
        _check_subs("Excitation", e, b, faces)
```

Further down in `check`, replace

```python
    size_items = dict.fromkeys(s for s, _, _ in sized) if selected else objects.mesh_sizes(study)
```

with

```python
    size_items = dict.fromkeys(s for s, _, _ in sized)
```

(The removed solid and link checks are covered by `geometry.collect`, which only accepts `Part::Feature` objects with exactly one solid.)

- [ ] **Step 8: Remove the mode from the task panels**

In `freecad_addon/emsolution/taskpanels.py`, `FolderView.__init__`, replace

```python
        if study.MainMode != "Materials":
            notice = QtWidgets.QLabel("Only assignments on the selected geometry are exported.")
            notice.setWordWrap(True)
            layout.addWidget(notice)
```

with

```python
        notice = QtWidgets.QLabel("Only assignments on the selected geometry are exported.")
        notice.setWordWrap(True)
        layout.addWidget(notice)
```

In `StudyView.refresh`, delete the two lines:

```python
            if name == "Main" and study.Dimension == "3D":
                combo.addItem("Material assignments (existing 3D workflow)", "mode:Materials")
```

- [ ] **Step 9: Run the tests**

Run: `pixi run pytest tests/freecad_addon -q`
Expected: all PASS.

- [ ] **Step 10: Format, lint, commit**

```bash
pixi run ruff format freecad_addon/emsolution/objects.py freecad_addon/emsolution/geometry.py freecad_addon/emsolution/jobwriter.py freecad_addon/emsolution/taskpanels.py tests/freecad_addon/test_study.py
pixi run lint
git add freecad_addon/emsolution/objects.py freecad_addon/emsolution/geometry.py freecad_addon/emsolution/jobwriter.py freecad_addon/emsolution/taskpanels.py tests/freecad_addon/test_study.py tests/freecad_addon/gui_smoke.py
git commit -m "Remove the Materials main-geometry mode and the old Study upgrade code

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

If `ruff format` reformats lines you did not change in `geometry.py` (it is not yet Ruff-formatted), revert those hunks with `git checkout -p` before committing; only your changed lines may differ.

---

### Task 2: Rename the ID tables to `MatIds` / `SmatIds` and the job fields to `mat_id` / `smat_id`

**Files:**
- Modify: `freecad_addon/emsolution/objects.py` (`Study.__init__`, `material_rows`, `excitation_rows`, `update_ids`, `set_id`, `id_rows`)
- Modify: `freecad_addon/emsolution/jobwriter.py` (`write_job`)
- Modify: `freecad_addon/emsolution/mesher.py` (`build`, `run`)
- Modify: `freecad_addon/emsolution/taskpanels.py` (`IdTableDialog`)
- Test: `tests/freecad_addon/test_study.py`, `tests/freecad_addon/test_mesher.py`, `tests/freecad_addon/gui_smoke.py`

**Interfaces:**
- Consumes: Task 1's `volume_keys` / `surface_keys`.
- Produces: Study properties `MatIds` (body Name → `MAT_ID` string), `SmatIds` (`"Excitation Name|Body Name"` → `SMAT_ID` string), `NextMatId` (starts 1), `NextSmatId` (starts 1001). `objects.set_id(study, table, key, new_id)` with `table` in `("MatIds", "SmatIds")`. `id_rows` tuples use `"MatIds"` / `"SmatIds"`. job.json volume `{"mat_id", "name", "file", "size"}`, surface `{"smat_id", "name", "mat_id", "files"}`.

- [ ] **Step 1: Update the tests to the new names**

In `tests/freecad_addon/test_study.py`, apply these replacements across the whole file:

| Old | New |
|---|---|
| `VolumeIds` | `MatIds` |
| `SurfaceIds` | `SmatIds` |
| `NextVolumeId` | `NextMatId` |

(This covers `ids()`, `set_id` table arguments, `id_rows` expectations, the restore subprocess code string and the `study.VolumeIds` assertions.)

In `test_job_json_contents`, replace the expected `"volumes"` and `"surfaces"` with:

```python
                "volumes": [
                    {"mat_id": 1, "name": "A", "file": "geometry/vol_1.brep", "size": 2.0},
                    {"mat_id": 2, "name": "B", "file": "geometry/vol_2.brep", "size": 5.0},
                ],
                "surfaces": [
                    {
                        "smat_id": 1001,
                        "name": "Terminal_In_A",
                        "mat_id": 1,
                        "files": ["geometry/surf_1001_1.brep", "geometry/surf_1001_2.brep"],
                    }
                ],
```

Add to the `# --- IDs ---` section:

```python
    def test_study_has_mat_and_smat_tables_only(self):
        for prop in ("MatIds", "SmatIds", "NextMatId", "NextSmatId"):
            self.assertIn(prop, self.study.PropertiesList)
        for prop in ("VolumeIds", "SurfaceIds", "NextVolumeId", "NextSurfaceId"):
            self.assertNotIn(prop, self.study.PropertiesList)
        self.assertEqual((self.study.NextMatId, self.study.NextSmatId), (1, 1001))
```

In `tests/freecad_addon/test_mesher.py`:
- `vol()` returns `{"mat_id": id_, "name": name, "file": "geometry/" + file, "size": size}`.
- The three surface dicts (around lines 116, 305, 346) become `{"smat_id": 1001, "name": ..., "mat_id": 1, "files": [...]}` (keep each one's `name` and `files`).

In `tests/freecad_addon/gui_smoke.py`, replace `assert study.VolumeIds["A"] == "7"` with `assert study.MatIds["A"] == "7"`.

- [ ] **Step 2: Run the tests to see them fail**

Run: `pixi run pytest tests/freecad_addon -q`
Expected: FAIL (`AttributeError: ... MatIds`, and mesher `KeyError: 'id'`).

- [ ] **Step 3: Rename in `objects.py`**

In `Study.__init__`, replace the four ID property lines and their editor-mode loop with:

```python
        obj.addProperty("App::PropertyMap", "MatIds", "IDs", "Body Name -> MAT_ID")
        obj.addProperty("App::PropertyMap", "SmatIds", "IDs", "'Excitation Name|Body Name' -> SMAT_ID")
        obj.addProperty("App::PropertyInteger", "NextMatId", "IDs", "Next MAT_ID")
        obj.NextMatId = 1
        obj.addProperty("App::PropertyInteger", "NextSmatId", "IDs", "Next SMAT_ID")
        obj.NextSmatId = 1001
```

and

```python
        for prop in ("MatIds", "SmatIds", "NextMatId", "NextSmatId"):
            obj.setEditorMode(prop, 1)  # read-only: edit through the ID table
```

Replace `update_ids` and `set_id` with:

```python
def update_ids(study):
    """Give every body a MAT_ID and every (excitation, body) pair an SMAT_ID; drop entries that are gone.

    Counters only grow, so a dropped ID is never handed out again.
    """
    vkeys, skeys = volume_keys(study), surface_keys(study)
    vol = {k: v for k, v in study.MatIds.items() if k in vkeys}
    surf = {k: v for k, v in study.SmatIds.items() if k in skeys}
    used = {int(v) for v in list(vol.values()) + list(surf.values())}

    def give(table, keys, counter):
        for key in keys:
            if key not in table:
                while counter in used:
                    counter += 1
                table[key] = str(counter)
                used.add(counter)
                counter += 1
        return counter

    study.NextMatId = give(vol, vkeys, study.NextMatId)
    study.NextSmatId = give(surf, skeys, study.NextSmatId)
    study.MatIds, study.SmatIds = vol, surf


def set_id(study, table, key, new_id):
    """table: "MatIds" or "SmatIds". Raises ValueError for a bad or duplicate ID."""
    ids = dict(getattr(study, table))
    if key not in ids:
        raise ValueError(f"unknown entry {key}")
    if new_id < 1:
        raise ValueError("IDs must be 1 or more")
    taken = {int(v) for t in ("MatIds", "SmatIds") for k, v in getattr(study, t).items() if (t, k) != (table, key)}
    if new_id in taken:
        raise ValueError(f"ID {new_id} is already used")
    ids[key] = str(new_id)
    setattr(study, table, ids)
    counter = "NextMatId" if table == "MatIds" else "NextSmatId"
    top = max(int(v) for v in ids.values())
    setattr(study, counter, max(getattr(study, counter), top + 1))
```

In `id_rows`, `material_rows` and `excitation_rows`, replace `study.VolumeIds` → `study.MatIds`, `study.SurfaceIds` → `study.SmatIds`, `"VolumeIds"` → `"MatIds"`, `"SurfaceIds"` → `"SmatIds"`.

- [ ] **Step 4: Rename in `jobwriter.write_job`**

Replace the two loops that fill `job["volumes"]` and `job["surfaces"]` with:

```python
    for body, mat, size in volumes:
        mat_id = int(study.MatIds[body.Name])
        rel = f"geometry/vol_{mat_id}.brep"
        global_shape(body).exportBrep(os.path.join(folder, rel))
        job["volumes"].append({"mat_id": mat_id, "name": objects.item_name(mat, body), "file": rel, "size": size})
    for exc, body, faces in surfaces:
        smat_id = int(study.SmatIds[f"{exc.Name}|{body.Name}"])
        job["surfaces"].append(
            {
                "smat_id": smat_id,
                "name": objects.item_name(exc, body),
                "mat_id": int(study.MatIds[body.Name]),
                "files": export_subs(folder, body, faces, f"surf_{smat_id}"),
            }
        )
```

- [ ] **Step 5: Rename in `mesher.py`**

In `build`:
- `body_vols[v["id"]] = tags` → `body_vols[v["mat_id"]] = tags`
- `surf_tags = {s["id"]: [] for s in surfs}` → `surf_tags = {s["smat_id"]: [] for s in surfs}`
- `surf_tags[s["id"]] += ...` → `surf_tags[s["smat_id"]] += ...`
- `body_vols[s["volume_id"]]` → `body_vols[s["mat_id"]]`
- `if not surf_tags[s["id"]] or not set(surf_tags[s["id"]]) <= boundary:` → use `s["smat_id"]` in both places
- `gmsh.model.addPhysicalGroup(3, body_vols[v["id"]], v["id"], name=v["name"])` → `gmsh.model.addPhysicalGroup(3, body_vols[v["mat_id"]], v["mat_id"], name=v["name"])`
- `gmsh.model.addPhysicalGroup(2, sorted(set(surf_tags[s["id"]])), s["id"], name=s["name"])` → `gmsh.model.addPhysicalGroup(2, sorted(set(surf_tags[s["smat_id"]])), s["smat_id"], name=s["name"])`
- `extend(body_vols[v["id"]])` → `extend(body_vols[v["mat_id"]])`
- comment `# volume id -> list of final 3D tags` → `# MAT_ID -> list of final 3D tags`

In `run`, replace

```python
    for item in job["volumes"] + job["surfaces"]:
        print(f"{item['id']:>6}  {item['name']}")
```

with

```python
    for item in job["volumes"]:
        print(f"MAT_ID  {item['mat_id']:>6}  {item['name']}")
    for item in job["surfaces"]:
        print(f"SMAT_ID {item['smat_id']:>6}  {item['name']}")
```

- [ ] **Step 6: ID dialog words**

In `taskpanels.py`, `IdTableDialog.__init__`, replace

```python
            kind = "Volume" if table == "VolumeIds" else "Surface"
```

with

```python
            kind = "MAT_ID" if table == "MatIds" else "SMAT_ID"
```

- [ ] **Step 7: Run the tests**

Run: `pixi run pytest tests/freecad_addon -q`
Expected: all PASS.

- [ ] **Step 8: Format, lint, commit**

```bash
pixi run ruff format freecad_addon/emsolution/objects.py freecad_addon/emsolution/jobwriter.py freecad_addon/emsolution/mesher.py freecad_addon/emsolution/taskpanels.py tests/freecad_addon/test_study.py tests/freecad_addon/test_mesher.py tests/freecad_addon/gui_smoke.py
pixi run lint
git add freecad_addon/emsolution tests/freecad_addon
git commit -m "Number Study bodies with MAT_ID and excitation faces with SMAT_ID

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: Material Library folder, `LibraryMaterial` objects and assignment properties

**Files:**
- Create: `tests/freecad_addon/materialdata.py`
- Modify: `freecad_addon/emsolution/objects.py`
- Modify: `freecad_addon/emsolution/taskpanels.py` (`FolderView` header/row mapping only)
- Test: `tests/freecad_addon/test_study.py`

**Interfaces:**
- Consumes: Task 2's `MatIds`.
- Produces (all in `objects`):
  - `MaterialLibraryFolder` (LABEL `"Material Library"`), `FOLDERS` starts with `("MaterialLibraryGroup", MaterialLibraryFolder)`.
  - `class LibraryMaterial(_Proxy)` with properties `Record` (str, hidden), `MaterialId` (str, read-only), `Family` (str, read-only).
  - `make_library_material(study, record_json: str) -> obj` (Label = record name).
  - `library_materials(study) -> list`, `material_users(lib) -> list` (assignments linking `lib`).
  - `Material` assignment has `LibraryMaterial` (`App::PropertyLink`, may be `None`) and `Potential` (`App::PropertyIntegerConstraint`, default 0, min 0).
  - `material_rows(study)` cells: `[assignment, material label or "— none —", body, MAT_ID or "–", str(Potential)]`.
  - `library_rows(study)` → `[(lib, [(body, "")...], [Label, Family, MaterialId, "user1, user2"])]`.
  - `NO_MATERIAL = "— none —"`.
- Test fixture module `tests/freecad_addon/materialdata.py`: `record(material_id, name, family, properties)` → canonical dict; constants `STEEL`, `COPPER`, `AIR` (property dicts).

- [ ] **Step 1: Create the shared test data**

Create `tests/freecad_addon/materialdata.py`:

```python
"""Canonical material records (ems_material JSON v1) for the addon tests."""

STEEL = {
    "general": {"density": {"type": "scalar", "value": 7650, "unit": "kg/m^3"}},
    "electromagnetic": {
        "BH_curve": {
            "type": "curve",
            "x": {"name": "H", "unit": "A/m", "values": [0, 100, 1000]},
            "y": {"name": "B", "unit": "T", "values": [0, 1, 1.5]},
        },
        "electrical_conductivity": {"type": "scalar", "value": 2e6, "unit": "S/m"},
        "iron_loss_ke": {"type": "scalar", "value": 5e-5, "unit": "W/kg/T^2/Hz^2"},
        "iron_loss_kh": {"type": "scalar", "value": 0.02, "unit": "W/kg/T^2/Hz"},
    },
}
COPPER = {"electromagnetic": {"electrical_conductivity": {"type": "scalar", "value": 5.8e7, "unit": "S/m"}}}
AIR = {"electromagnetic": {"relative_permeability": {"type": "scalar", "value": 1, "unit": "1"}}}


def record(material_id, name, family="generic", properties=None, version="1.0.0"):
    return {
        "schema": "ems_material",
        "schema_version": "1.0",
        "material_id": material_id,
        "material_version": version,
        "identity": {
            "name": name,
            "family": family,
            "manufacturer": None,
            "grade": None,
            "description": None,
            "aliases": [],
            "tags": [],
        },
        "properties": properties or {},
        "provenance": {"source_type": "USER_INPUT", "reference": None, "date": None, "notes": None},
        "version_metadata": {"author": "test", "updated_at": "2026-10-13T00:00:00+00:00", "change_note": "fixture"},
    }
```

- [ ] **Step 2: Write the failing tests**

In `tests/freecad_addon/test_study.py`, add after `from emsolution import geometry, jobwriter, objects`:

```python
from .materialdata import STEEL, record
```

Add to the `# --- tree objects ---` section:

```python
    def lib(self, material_id="user:steel", name="Steel", family="electrical_steel"):
        return objects.make_library_material(self.study, json.dumps(record(material_id, name, family, STEEL)))

    def test_library_material_mirrors_its_record(self):
        lib = self.lib()
        self.assertEqual((lib.Label, lib.MaterialId, lib.Family), ("Steel", "user:steel", "electrical_steel"))
        self.assertEqual(lib.getEditorMode("Record"), ["Hidden"])
        self.assertEqual(lib.getEditorMode("MaterialId"), ["ReadOnly"])
        self.assertEqual(objects.library_materials(self.study), [lib])
        self.assertFalse(objects.is_item(lib))
        self.assertIsNone(objects.pick_body(lib))

    def test_material_assignment_links_a_library_material_and_potential(self):
        a = self.box("A")
        lib = self.lib()
        mat = self.mat("Iron", [a])
        self.assertIsNone(mat.LibraryMaterial)
        self.assertEqual(mat.Potential, 0)
        mat.LibraryMaterial, mat.Potential = lib, 2
        self.assertEqual(objects.material_users(lib), [mat])
        objects.update_ids(self.study)
        self.assertEqual(objects.material_rows(self.study), [(mat, [(a, "")], ["Iron", "Steel", "A", "1", "2"])])
        self.assertEqual(
            objects.library_rows(self.study), [(lib, [(a, "")], ["Steel", "electrical_steel", "user:steel", "Iron"])]
        )

    def test_library_material_survives_save_and_reload(self):
        lib = objects.make_library_material(
            self.study, json.dumps(record("user:copper", "銅 مس Copper", "conductor"), ensure_ascii=False)
        )
        mat = self.mat("Coil", [self.box("A")])
        mat.LibraryMaterial, mat.Potential = lib, 3
        path = os.path.join(self.tmp.name, "lib.FCStd")
        self.doc.saveAs(path)
        App.closeDocument(self.doc.Name)
        self.doc = App.openDocument(path)
        study = objects.find_study(self.doc)
        (lib,) = objects.library_materials(study)
        (mat,) = objects.materials(study)
        self.assertEqual(json.loads(lib.Record)["identity"]["name"], "銅 مس Copper")
        self.assertEqual(lib.Label, "銅 مس Copper")
        self.assertEqual((lib.MaterialId, mat.LibraryMaterial, mat.Potential), ("user:copper", lib, 3))
```

Update `test_folders_keep_their_names` expected list to:

```python
        self.assertEqual(
            [f.Label for f in self.study.Group], ["Material Library", "Materials", "Excitations", "Mesh Sizes"]
        )
```

Update `test_folder_overview_rows` material expectations to:

```python
        self.assertEqual(
            objects.material_rows(self.study),
            [
                (mat, [(a, "")], ["Copper", "— none —", "A", "1", "0"]),
                (mat, [(b, "")], ["Copper", "— none —", "B", "2", "0"]),
                (empty, [], ["Iron", "— none —", "", "", "0"]),
            ],
        )
```

and its last assertion to:

```python
        self.assertEqual(objects.material_rows(self.study)[2], (mat, [(d, "")], ["Copper", "— none —", "D", "–", "0"]))
```

- [ ] **Step 3: Run the tests to see them fail**

Run: `pixi run pytest tests/freecad_addon/test_study.py -q`
Expected: FAIL with `AttributeError: module 'emsolution.objects' has no attribute 'make_library_material'`.

- [ ] **Step 4: Implement the objects**

In `freecad_addon/emsolution/objects.py`, add `import json` above `import re`.

After `def ref_label(...)`, add:

```python
NO_MATERIAL = "— none —"
```

Add the folder class before `class MaterialsFolder`:

```python
class MaterialLibraryFolder(Folder):
    LABEL = "Material Library"
```

Change `FOLDERS` to:

```python
FOLDERS = (
    ("MaterialLibraryGroup", MaterialLibraryFolder),
    ("MaterialsGroup", MaterialsFolder),
    ("ExcitationsGroup", ExcitationsFolder),
    ("MeshSizesGroup", MeshSizesFolder),
)
```

Replace `class Material(_Named)` with:

```python
class Material(_Named):
    """An assignment: bodies made of a Material Library entry, with their potential region."""

    def __init__(self, obj):
        obj.Proxy = self
        self.add_group_name(obj)
        obj.addProperty("App::PropertyLinkListGlobal", "References", "EMSolution", "Bodies made of this material")
        obj.addProperty("App::PropertyLink", "LibraryMaterial", "EMSolution", "Material from the Material Library")
        obj.addProperty("App::PropertyIntegerConstraint", "Potential", "EMSolution", "POTENTIAL: 0 total, 1+ reduced")
        obj.Potential = (0, 0, 1000000, 1)


class LibraryMaterial(_Proxy):
    """A Study copy of a material: canonical ems_material JSON, edited in the Study."""

    def __init__(self, obj):
        obj.Proxy = self
        obj.addProperty("App::PropertyString", "Record", "EMSolution", "Canonical material JSON")
        obj.addProperty("App::PropertyString", "MaterialId", "EMSolution", "material_id in the record")
        obj.addProperty("App::PropertyString", "Family", "EMSolution", "Material family in the record")
        obj.setEditorMode("Record", 2)  # hidden: edit through the Material Library
        for prop in ("MaterialId", "Family"):
            obj.setEditorMode(prop, 1)

    def onChanged(self, obj, prop):
        if prop == "Record" and obj.Record and not obj.Document.Restoring:
            data = json.loads(obj.Record)
            obj.MaterialId = data["material_id"]
            obj.Family = data["identity"]["family"]
```

After `make_material`, add:

```python
def make_library_material(study, record_json):
    """record_json: canonical ems_material JSON. The Label is the material's name."""
    name = json.loads(record_json)["identity"]["name"]
    obj = _add(study, "MaterialLibraryGroup", LibraryMaterial, name)
    obj.Record = record_json
    return obj
```

After `def mesh_sizes(study)`, add:

```python
def library_materials(study):
    return list(study.MaterialLibraryGroup.Group)


def material_users(lib):
    """Assignments of lib's Study that link to it."""
    return [m for m in materials(owner_study(lib)) if m.LibraryMaterial == lib]
```

Replace `material_rows` with:

```python
def material_rows(study):
    """Rows for the Materials panel: (assignment, refs, [name, material, body, MAT_ID, POTENTIAL])."""
    rows = []
    for m in materials(study):
        lib = m.LibraryMaterial.Label if m.LibraryMaterial else NO_MATERIAL
        rows += [
            (m, [(b, "")], [display_name(m), lib, b.Label, study.MatIds.get(b.Name, "–"), str(m.Potential)])
            for b in m.References
        ] or [(m, [], [display_name(m), lib, "", "", str(m.Potential)])]
    return rows


def library_rows(study):
    """Rows for the Material Library panel: (material, refs of its users, [name, family, ID, used by])."""
    rows = []
    for lib in library_materials(study):
        users = material_users(lib)
        refs = [(b, "") for m in users for b in m.References]
        rows.append((lib, refs, [lib.Label, lib.Family, lib.MaterialId, ", ".join(m.Label for m in users)]))
    return rows
```

- [ ] **Step 5: Show the new folder in the task panel table mapping**

In `taskpanels.py`, `FolderView.__init__`, add the Material Library entry at the top of the mapping (Task 6 adds its buttons):

```python
            objects.MaterialLibraryFolder: (["Name", "Family", "Material ID", "Used by"], objects.library_rows),
            objects.MaterialsFolder: (["Assignment", "Material", "Body", "MAT_ID", "POTENTIAL"], objects.material_rows),
```

(replacing the old `objects.MaterialsFolder` line).

- [ ] **Step 6: Run the tests**

Run: `pixi run pytest tests/freecad_addon -q`
Expected: all PASS.

- [ ] **Step 7: Format, lint, commit**

```bash
pixi run ruff format freecad_addon/emsolution/objects.py freecad_addon/emsolution/taskpanels.py tests/freecad_addon/test_study.py tests/freecad_addon/materialdata.py
pixi run lint
git add freecad_addon/emsolution/objects.py freecad_addon/emsolution/taskpanels.py tests/freecad_addon/test_study.py tests/freecad_addon/materialdata.py
git commit -m "Add the Study Material Library and link Material assignments to it

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: `ems-material-manager` dependency and the Study material repository

**Files:**
- Modify: `pyproject.toml`, `pixi.lock`
- Create: `freecad_addon/emsolution/studymaterials.py`
- Test: `tests/freecad_addon/test_studymaterials.py`

**Interfaces:**
- Consumes: `objects.make_library_material`, `objects.library_materials`, `objects.material_users`, `objects.owner_study`.
- Produces (in `studymaterials`):
  - `class StudyMaterialRepository(study, on_change=None)` implementing the `ems_material.MaterialRepository` protocol; `on_change()` is called after every committed write.
  - `SOURCE = "Study"`.
  - `import_materials(study, materials) -> list` of new `LibraryMaterial` objects; raises `ems_material.MaterialAlreadyExistsError` (nothing created) when an ID is already in the Study.
  - `library_root() -> str | None`.
  - `record_material(lib) -> ems_material.Material`.

- [ ] **Step 1: Add the dependency**

```bash
pixi add --pypi "ems-material-manager>=0.1,<0.2"
pixi add "qtpy>=2.4"
```

Then mirror them in `[project] dependencies` of `pyproject.toml` (the list that already has `"ems-file-format-converter"`), adding after `"gmsh",`:

```toml
    "ems-material-manager>=0.1,<0.2",
    "qtpy>=2.4",
```

Do **not** use the `[gui]` extra: it pulls PySide6 and matplotlib from PyPI over the conda packages. Check:

Run: `pixi run python -c "import ems_material, qtpy; from ems_material.gui import MaterialManagerWindow; print(ems_material.__file__, qtpy.API_NAME)"`
Expected: a path inside `.pixi\envs\default` and `PySide6`.

- [ ] **Step 2: Write the failing tests**

Create `tests/freecad_addon/test_studymaterials.py`:

```python
"""Study Material Library tests. Run from the repo root: pixi run pytest tests/freecad_addon/test_studymaterials.py"""

import dataclasses
import json
import os
import tempfile
import unittest
from unittest import mock

import FreeCAD as App

from ems_material import (
    MaterialAlreadyExistsError,
    MaterialConflictError,
    MaterialManager,
    MaterialNotFoundError,
    ReadOnlyMaterialError,
    material_from_dict,
)
from emsolution import objects, studymaterials

from .materialdata import AIR, COPPER, STEEL, record


def material(material_id, name, properties, family="generic"):
    return material_from_dict(record(material_id, name, family, properties))


class StudyCase(unittest.TestCase):
    def setUp(self):
        self.doc = App.newDocument("M")
        self.doc.UndoMode = 1
        self.tmp = tempfile.TemporaryDirectory()
        self.study = objects.make_study(self.doc)
        self.study.MainMode = "Manual"
        self.changes = []
        self.repo = studymaterials.StudyMaterialRepository(self.study, on_change=lambda: self.changes.append(1))

    def tearDown(self):
        App.closeDocument(self.doc.Name)
        self.tmp.cleanup()

    def box(self, name, x=0.0):
        b = self.doc.addObject("Part::Box", name)
        b.Placement.Base = App.Vector(x, 0, 0)
        self.doc.recompute()
        return b


class RepositoryTest(StudyCase):
    def test_create_get_list_and_search(self):
        steel = material("user:steel", "Steel", STEEL, "electrical_steel")
        self.repo.create(steel)
        self.repo.create(material("user:air", "Air", AIR))
        self.assertEqual(self.repo.get("user:steel"), steel)
        self.assertEqual([m.material_id for m in self.repo.list()], ["user:steel", "user:air"])
        self.assertEqual([m.material_id for m in self.repo.search(text="ste")], ["user:steel"])
        self.assertEqual([m.material_id for m in self.repo.search(family="generic")], ["user:air"])
        self.assertEqual(self.repo.list_sources(), ("Study",))
        self.assertEqual(self.repo.source_for("user:air"), "Study")
        self.assertTrue(self.repo.is_writable("user:air"))
        self.assertEqual(len(self.changes), 2)
        with self.assertRaises(MaterialNotFoundError):
            self.repo.get("user:nothing")

    def test_create_refuses_a_duplicate_id(self):
        self.repo.create(material("user:air", "Air", AIR))
        with self.assertRaises(MaterialAlreadyExistsError):
            self.repo.create(material("user:air", "Other air", AIR))
        self.assertEqual(len(objects.library_materials(self.study)), 1)

    def test_update_checks_the_expected_version_and_renames(self):
        air = self.repo.create(material("user:air", "Air", AIR))
        newer = dataclasses.replace(
            air, material_version="1.0.1", identity=dataclasses.replace(air.identity, name="Air gap")
        )
        self.repo.update(newer, expected_version="1.0.0")
        (lib,) = objects.library_materials(self.study)
        self.assertEqual((lib.Label, self.repo.get("user:air").material_version), ("Air gap", "1.0.1"))
        with self.assertRaises(MaterialConflictError):
            self.repo.update(newer, expected_version="1.0.0")

    def test_duplicate_makes_a_user_copy(self):
        self.repo.create(material("user:steel", "Steel", STEEL, "electrical_steel"))
        copy = self.repo.duplicate(
            "user:steel", new_material_id="user:steel_b", new_name="Steel B", author="me", updated_at="2026-10-13"
        )
        self.assertEqual((copy.name, copy.material_version, copy.parent_ref), ("Steel B", "1.0.0", "user:steel@1.0.0"))
        self.assertEqual(copy.properties, self.repo.get("user:steel").properties)

    def test_delete_is_refused_while_an_assignment_uses_the_material(self):
        self.repo.create(material("user:air", "Air", AIR))
        (lib,) = objects.library_materials(self.study)
        mat = objects.make_material(self.study, "Gap", [self.box("A")])
        mat.LibraryMaterial = lib
        self.assertFalse(self.repo.is_deletable("user:air"))
        with self.assertRaisesRegex(ReadOnlyMaterialError, "Gap"):
            self.repo.delete("user:air")
        mat.LibraryMaterial = None
        self.repo.delete("user:air")
        self.assertEqual(objects.library_materials(self.study), [])

    def test_each_write_is_one_undo_step(self):
        air = self.repo.create(material("user:air", "Air", AIR))
        self.repo.update(dataclasses.replace(air, material_version="1.0.1"))
        self.doc.undo()
        self.assertEqual(self.repo.get("user:air").material_version, "1.0.0")
        self.doc.undo()
        self.assertEqual(objects.library_materials(self.study), [])

    def test_json_export_and_import(self):
        self.repo.create(material("user:air", "Air", AIR))
        path = os.path.join(self.tmp.name, "air.material.json")
        self.repo.export_json("user:air", path)
        self.repo.delete("user:air")
        self.assertEqual(self.repo.import_json(path).material_id, "user:air")

    def test_material_manager_accepts_the_repository(self):
        manager = MaterialManager(repository=self.repo)
        steel = manager.repository.create(material("user:steel", "Steel", STEEL, "electrical_steel"))
        self.assertEqual(manager.update(steel).material_id, "user:steel")
        self.assertEqual([m.name for m in manager.list()], ["Steel"])


class ImportTest(StudyCase):
    def test_import_copies_records_unchanged(self):
        steel = material("ieej:50a350", "50A350", STEEL, "electrical_steel")
        (lib,) = studymaterials.import_materials(self.study, [steel])
        self.assertEqual(studymaterials.record_material(lib), steel)
        self.assertEqual(lib.Label, "50A350")
        self.assertEqual(self.doc.UndoNames[:1], ["Import materials"])

    def test_import_refuses_ids_already_in_the_study(self):
        studymaterials.import_materials(self.study, [material("user:air", "Air", AIR)])
        with self.assertRaisesRegex(MaterialAlreadyExistsError, "user:air"):
            studymaterials.import_materials(
                self.study, [material("user:copper", "Copper", COPPER), material("user:air", "Air", AIR)]
            )
        self.assertEqual([o.MaterialId for o in objects.library_materials(self.study)], ["user:air"])


class LibraryRootTest(unittest.TestCase):
    def test_environment_then_remembered_root(self):
        with tempfile.TemporaryDirectory() as root, tempfile.TemporaryDirectory() as other:
            settings = os.path.join(other, "settings.json")
            env = {"EMS_MATERIAL_MANAGER_ROOT": root, "EMS_MATERIAL_MANAGER_SETTINGS_PATH": settings}
            with mock.patch.dict(os.environ, env):
                self.assertTrue(os.path.samefile(studymaterials.library_root(), root))
            env["EMS_MATERIAL_MANAGER_ROOT"] = ""
            with mock.patch.dict(os.environ, env):
                self.assertIsNone(studymaterials.library_root())
                with open(settings, "w", encoding="utf-8") as fh:
                    json.dump(
                        {
                            "schema": "ems_material_product_exchange_settings",
                            "schema_version": "1.0",
                            "library_root": other,
                        },
                        fh,
                    )
                self.assertTrue(os.path.samefile(studymaterials.library_root(), other))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Run the tests to see them fail**

Run: `pixi run pytest tests/freecad_addon/test_studymaterials.py -q`
Expected: FAIL with `ImportError: cannot import name 'studymaterials'`.

- [ ] **Step 4: Implement `studymaterials.py`**

Create `freecad_addon/emsolution/studymaterials.py`:

```python
"""Study Material Library <-> EMS Material Manager (ems_material). No GUI code here."""

import os
from dataclasses import replace

from ems_material import (
    MaterialAlreadyExistsError,
    MaterialConflictError,
    MaterialNotFoundError,
    ReadOnlyMaterialError,
    VersionMetadata,
    load_material,
    material_from_json,
    material_to_json,
    save_material,
)

from . import objects

SOURCE = "Study"
ROOT_ENV = "EMS_MATERIAL_MANAGER_ROOT"


def record_material(lib):
    return material_from_json(lib.Record)


def library_root():
    """The Material Manager root shared with eMotorSolution, or None when none is set."""
    env = os.environ.get(ROOT_ENV)
    if env and os.path.isdir(env):
        return env
    from ems_material.gui.product_exchange import remembered_library_root  # imports qtpy

    root = remembered_library_root()
    return str(root) if root else None


def _transaction(study, title, change):
    doc = study.Document
    doc.openTransaction(title)
    try:
        result = change()
    except Exception:
        doc.abortTransaction()
        raise
    doc.commitTransaction()
    doc.recompute()
    return result


def import_materials(study, materials):
    """Copy library materials into the Material Library as one undo step. Returns the new objects."""
    have = {o.MaterialId for o in objects.library_materials(study)}
    taken = [m.material_id for m in materials if m.material_id in have]
    if taken:
        raise MaterialAlreadyExistsError("Already in the Material Library: " + ", ".join(taken))
    texts = [material_to_json(m) for m in materials]
    return _transaction(study, "Import materials", lambda: [objects.make_library_material(study, t) for t in texts])


class StudyMaterialRepository:
    """The ems_material MaterialRepository protocol over a Study's Material Library.

    Every write is one FreeCAD transaction; on_change() runs after it is committed.
    """

    def __init__(self, study, on_change=None):
        self.study = study
        self.on_change = on_change

    def _objects(self):
        return {o.MaterialId: o for o in objects.library_materials(self.study)}

    def _object(self, material_id):
        obj = self._objects().get(material_id)
        if obj is None:
            raise MaterialNotFoundError(f"Material not found in the Material Library: {material_id}")
        return obj

    def _write(self, title, change):
        result = _transaction(self.study, title, change)
        if self.on_change is not None:
            self.on_change()
        return result

    def list(self):
        return tuple(record_material(o) for o in objects.library_materials(self.study))

    def get(self, material_id):
        return record_material(self._object(material_id))

    def create(self, material):
        if material.material_id in self._objects():
            raise MaterialAlreadyExistsError(f"Material already in the Material Library: {material.material_id}")
        text = material_to_json(material)
        self._write("Add material", lambda: objects.make_library_material(self.study, text))
        return material

    def update(self, material, *, expected_version=None):
        obj = self._object(material.material_id)
        current = record_material(obj)
        if expected_version is not None and current.material_version != expected_version:
            raise MaterialConflictError(
                f"Expected {expected_version}, found {current.material_version} for {material.material_id}"
            )
        text = material_to_json(material)

        def change():
            obj.Record = text
            obj.Label = material.name

        self._write("Edit material", change)
        return material

    def duplicate(
        self, source_id, *, new_material_id, new_name, author, updated_at, change_note="Duplicated material"
    ):
        source = self.get(source_id)
        origin = f"{source.material_id}@{source.material_version}"
        copy = replace(
            source,
            material_id=new_material_id,
            material_version="1.0.0",
            identity=replace(source.identity, name=new_name),
            provenance=replace(
                source.provenance,
                source_type="USER_INPUT",
                reference=origin,
                notes="Duplicated from an existing material",
            ),
            version_metadata=VersionMetadata(author, updated_at, change_note),
            parent_ref=origin,
        )
        return self.create(copy)

    def delete(self, material_id):
        obj = self._object(material_id)
        users = objects.material_users(obj)
        if users:
            raise ReadOnlyMaterialError(f"{obj.Label} is used by: " + ", ".join(m.Label for m in users))
        self._write("Delete material", lambda: self.study.Document.removeObject(obj.Name))

    def search(self, *, family=None, text=None, manufacturer=None, tags=()):
        text_query = text.casefold() if text else None
        tag_query = {t.casefold() for t in tags}
        found = []
        for m in self.list():
            identity = m.identity
            if family and identity.family.casefold() != family.casefold():
                continue
            if manufacturer and (identity.manufacturer or "").casefold() != manufacturer.casefold():
                continue
            if tag_query and not tag_query <= {t.casefold() for t in identity.tags}:
                continue
            words = [m.material_id, identity.name, identity.grade or "", identity.manufacturer or ""]
            haystack = " ".join(words + list(identity.aliases) + list(identity.tags)).casefold()
            if text_query and text_query not in haystack:
                continue
            found.append(m)
        return tuple(found)

    def import_json(self, source):
        return self.create(load_material(source))

    def export_json(self, material_id, destination):
        save_material(self.get(material_id), destination)

    def source_for(self, material_id):
        self._object(material_id)
        return SOURCE

    def is_writable(self, material_id):
        self._object(material_id)
        return True

    def is_deletable(self, material_id):
        return not objects.material_users(self._object(material_id))

    def list_sources(self):
        return (SOURCE,)
```

- [ ] **Step 5: Run the tests**

Run: `pixi run pytest tests/freecad_addon -q`
Expected: all PASS. If `test_material_manager_accepts_the_repository` fails in catalog validation, print the error: the fixture's property paths and units must match the library's default `property_definitions.v1.json`; fix the fixture in `materialdata.py`, not the repository.

- [ ] **Step 6: Format, lint, commit**

```bash
pixi run ruff format freecad_addon/emsolution/studymaterials.py tests/freecad_addon/test_studymaterials.py
pixi run lint
git add pyproject.toml pixi.lock freecad_addon/emsolution/studymaterials.py tests/freecad_addon/test_studymaterials.py
git commit -m "Store Study materials through an ems_material repository over the Material Library

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: The 16.1 builder

**Files:**
- Modify: `freecad_addon/emsolution/studymaterials.py`
- Test: `tests/freecad_addon/test_studymaterials.py`

**Interfaces:**
- Consumes: `jobwriter.check(study)` → `(volumes=[(body, assignment, size)], ...)`, `jobwriter.StudyError`, `objects.update_ids`, `objects.item_name`, `record_material` (Task 4).
- Produces:
  - `study_material_rows(study) -> list[tuple[int, str, int, Material]]`: `(MAT_ID, MAT_NAME, POTENTIAL, material)` sorted by MAT_ID. Runs `jobwriter.check` and `objects.update_ids`. Raises `StudyError` naming an assignment without a Library Material.
  - `material_properties(rows) -> dict` with keys `"16_Material_Properties"` (→ `{"16_1_3D_Element_Properties": [...]}`) and `"20_BH_Curve"` (list). Raises `StudyError` naming the material on adapter errors.

- [ ] **Step 1: Write the failing tests**

Append to `tests/freecad_addon/test_studymaterials.py` (before `if __name__ == "__main__":`), and add `from emsolution.jobwriter import StudyError` after `from emsolution import objects, studymaterials`:

```python
STEEL_ENTRY = {
    "ElectricProperty": {"conductivity": {"SIGMA": 2e6}},
    "MagneticProperty": {
        "MU": 1.0,
        "BH_CURVE_ID": 1,
        "IRON_LOSS": {"COORD_ID": 0, "MASS_DENSITY": 7650.0, "KE": 5e-5, "KH": 0.02},
    },
}
STEEL_CURVE = {"H": [0.0, 100.0, 1000.0], "B": [0.0, 1.0, 1.5]}


class BuilderTest(unittest.TestCase):
    def test_three_bodies_share_one_material_and_one_curve(self):
        steel = material("user:steel", "Steel", STEEL, "electrical_steel")
        rows = [(1, "Stator", 0, steel), (2, "Rotor", 1, steel), (3, "Shaft", 0, steel)]
        out = studymaterials.material_properties(rows)
        entries = out["16_Material_Properties"]["16_1_3D_Element_Properties"]
        self.assertEqual(
            entries,
            [
                {"MAT_ID": 1, "MAT_NAME": "Stator", "POTENTIAL": 0, **STEEL_ENTRY},
                {"MAT_ID": 2, "MAT_NAME": "Rotor", "POTENTIAL": 1, **STEEL_ENTRY},
                {"MAT_ID": 3, "MAT_NAME": "Shaft", "POTENTIAL": 0, **STEEL_ENTRY},
            ],
        )
        self.assertEqual(out["20_BH_Curve"], [{"BH_CURVE_ID": 1, "BH_CURVE_NAME": "Steel", "data": STEEL_CURVE}])
        entries[0]["MagneticProperty"]["MU"] = 5.0
        self.assertEqual(entries[1]["MagneticProperty"]["MU"], 1.0, "entries share a dict")

    def test_curve_ids_are_sequential_across_materials(self):
        a = material("user:a", "Steel A", STEEL, "electrical_steel")
        b = material("user:b", "Steel B", STEEL, "electrical_steel")
        out = studymaterials.material_properties([(1, "X", 0, a), (2, "Y", 0, b), (3, "Z", 0, a)])
        entries = out["16_Material_Properties"]["16_1_3D_Element_Properties"]
        self.assertEqual([e["MagneticProperty"]["BH_CURVE_ID"] for e in entries], [1, 2, 1])
        self.assertEqual([(c["BH_CURVE_ID"], c["BH_CURVE_NAME"]) for c in out["20_BH_Curve"]], [(1, "Steel A"), (2, "Steel B")])

    def test_material_without_magnetic_data_is_linear(self):
        out = studymaterials.material_properties(
            [(4, "Coil", 0, material("user:copper", "Copper", COPPER)), (5, "Gap", 0, material("user:air", "Air", AIR))]
        )
        self.assertEqual(
            out["16_Material_Properties"]["16_1_3D_Element_Properties"],
            [
                {
                    "MAT_ID": 4,
                    "MAT_NAME": "Coil",
                    "POTENTIAL": 0,
                    "ElectricProperty": {"conductivity": {"SIGMA": 5.8e7}},
                    "MagneticProperty": {"MU": 1.0},
                },
                {"MAT_ID": 5, "MAT_NAME": "Gap", "POTENTIAL": 0, "MagneticProperty": {"MU": 1.0}},
            ],
        )
        self.assertEqual(out["20_BH_Curve"], [])

    def test_adapter_errors_name_the_material(self):
        props = json.loads(json.dumps(STEEL))
        del props["general"]
        with self.assertRaisesRegex(StudyError, "Bad steel.*density"):
            studymaterials.material_properties([(1, "A", 0, material("user:bad", "Bad steel", props))])


class StudyRowsTest(StudyCase):
    def test_rows_follow_mat_ids_with_body_names_and_potential(self):
        a, b = self.box("A"), self.box("B", 10)
        self.study.MainObjects = [a, b]
        (lib,) = studymaterials.import_materials(self.study, [material("user:steel", "Steel", STEEL)])
        mat = objects.make_material(self.study, "Iron", [a, b])
        mat.LibraryMaterial, mat.Potential = lib, 1
        rows = studymaterials.study_material_rows(self.study)
        self.assertEqual([(r[0], r[1], r[2], r[3].material_id) for r in rows], [(1, "A", 1, "user:steel"), (2, "B", 1, "user:steel")])

    def test_assignment_without_a_material_is_named(self):
        a = self.box("A")
        self.study.MainObjects = [a]
        objects.make_material(self.study, "Iron", [a])
        with self.assertRaisesRegex(StudyError, "Iron has no material from the Material Library"):
            studymaterials.study_material_rows(self.study)

    def test_deleted_library_material_is_reported(self):
        a = self.box("A")
        self.study.MainObjects = [a]
        (lib,) = studymaterials.import_materials(self.study, [material("user:air", "Air", AIR)])
        mat = objects.make_material(self.study, "Gap", [a])
        mat.LibraryMaterial = lib
        self.doc.removeObject(lib.Name)
        with self.assertRaisesRegex(StudyError, "Gap has no material from the Material Library"):
            studymaterials.study_material_rows(self.study)
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `pixi run pytest tests/freecad_addon/test_studymaterials.py -q`
Expected: FAIL with `AttributeError: module 'emsolution.studymaterials' has no attribute 'material_properties'`.

- [ ] **Step 3: Implement the builder**

In `studymaterials.py`, add `import copy` above `import os`, add `from ems_material.adapters import EMSolutionInputAdapter` after the `from ems_material import (...)` block, and change `from . import objects` to:

```python
from . import jobwriter, objects
from .jobwriter import StudyError
```

Append:

```python
def study_material_rows(study):
    """[(MAT_ID, MAT_NAME, POTENTIAL, material)] for the Study's bodies, in MAT_ID order."""
    volumes, _, _ = jobwriter.check(study)
    objects.update_ids(study)
    rows = []
    for body, mat, _size in volumes:
        if mat.LibraryMaterial is None:
            raise StudyError(f"{mat.Label} has no material from the Material Library.")
        rows.append(
            (int(study.MatIds[body.Name]), objects.item_name(mat, body), mat.Potential, record_material(mat.LibraryMaterial))
        )
    return sorted(rows, key=lambda r: r[0])


def material_properties(rows):
    """16_Material_Properties.16_1_3D_Element_Properties and 20_BH_Curve for rows of study_material_rows().

    One entry per row; B-H curves once per material, numbered from 1 in first-use order.
    """
    adapter = EMSolutionInputAdapter()
    entries, curves, entry_of = [], [], {}
    for mat_id, mat_name, potential, material in rows:
        if material.material_id not in entry_of:
            try:
                payload = adapter.export_material(material).payload
            except (ValueError, TypeError) as exc:
                raise StudyError(f"Material {material.name}: {exc}") from None
            renumber = {}
            for curve in payload["bh_curves"]:
                renumber[curve["BH_CURVE_ID"]] = len(curves) + 1
                curves.append({**copy.deepcopy(curve), "BH_CURVE_ID": len(curves) + 1})
            entry = copy.deepcopy(payload["material"])
            magnetic = entry.get("MagneticProperty", {})
            if "BH_CURVE_ID" in magnetic:
                magnetic["BH_CURVE_ID"] = renumber[magnetic["BH_CURVE_ID"]]
            if "BH_CURVE_XYZ" in magnetic:
                xyz = magnetic["BH_CURVE_XYZ"]
                xyz["BH_XYZ_ID"] = [renumber[i] for i in xyz["BH_XYZ_ID"]]
            entry_of[material.material_id] = entry
        entry = copy.deepcopy(entry_of[material.material_id])
        entry.update(MAT_ID=mat_id, MAT_NAME=mat_name, POTENTIAL=potential)
        entries.append(entry)
    return {"16_Material_Properties": {"16_1_3D_Element_Properties": entries}, "20_BH_Curve": curves}
```

- [ ] **Step 4: Run the tests**

Run: `pixi run pytest tests/freecad_addon -q`
Expected: all PASS.

- [ ] **Step 5: Format, lint, commit**

```bash
pixi run ruff format freecad_addon/emsolution/studymaterials.py tests/freecad_addon/test_studymaterials.py
pixi run lint
git add freecad_addon/emsolution/studymaterials.py tests/freecad_addon/test_studymaterials.py
git commit -m "Build the 16_1_3D_Element_Properties entries and B-H curves from a Study

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 6: GUI: Material Library panel, stand-in picker and editor, assignment panel

**Files:**
- Create: `freecad_addon/emsolution/materialstandins.py`
- Modify: `freecad_addon/emsolution/taskpanels.py`
- Modify: `freecad_addon/emsolution/objects.py` (`_make_folder` / `_add` attach the right view provider)
- Modify: `freecad_addon/emsolution/commands.py` (`AddMaterial`)
- Test: `tests/freecad_addon/gui_smoke.py`

**Interfaces:**
- Consumes: `studymaterials.StudyMaterialRepository(study, on_change)`, `studymaterials.import_materials`, `studymaterials.library_root`, `objects.library_rows`, `objects.material_users`, `objects.library_materials`, `objects.NO_MATERIAL`.
- Produces:
  - `materialstandins.MaterialPicker(manager, taken, parent=None)` (`QDialog`; `.list` is the `QListWidget`; `.selected()` → list of `Material`).
  - `materialstandins.pick_materials(study, parent)` → list of new `LibraryMaterial` objects (empty on cancel).
  - `materialstandins.open_editor(study, material_id=None)` → the `MaterialManagerWindow` (one per Study).
  - `taskpanels.ViewProviderLibraryMaterial`, `taskpanels.refresh_library_views()`.
  - `ItemPanel` for a `Material` has `.material` (`QComboBox`, item data = `LibraryMaterial` Name or `""`) and `.potential` (`QSpinBox`).

- [ ] **Step 1: Extend the GUI smoke test (the failing test)**

In `tests/freecad_addon/gui_smoke.py`:

1. (Task 1 already switched the smoke Study to Manual mode.)

2. After `Gui.runCommand("EMS_Material")` add `Gui.Control.closeDialog()` (Add Material now opens its panel).

3. Replace `first_column = {...}` with:

```python
    first_column = {
        "Name": "Material Library",
        "Assignment": "Materials",
        "Excitation": "Excitations",
        "Mesh size": "Mesh Sizes",
    }
```

4. Replace `rows = {"Materials": 2, "Excitations": 1, "Mesh Sizes": 2}` with `rows = {"Material Library": 0, "Materials": 2, "Excitations": 1, "Mesh Sizes": 2}`, and the loop header `for folder in (study.MaterialsGroup, study.ExcitationsGroup, study.MeshSizesGroup):` with `for folder in (study.MaterialLibraryGroup, study.MaterialsGroup, study.ExcitationsGroup, study.MeshSizesGroup):`.

5. (Task 1 already changed the later `MainMode` assertion.)

6. Before `log.append("folder panels ok")`, insert the Material Library flow:

```python
    from emsolution import materialstandins, studymaterials
    from ems_material import JsonMaterialRepository, MaterialManager, material_from_dict

    def record(material_id, name):
        return material_from_dict(
            {
                "schema": "ems_material",
                "schema_version": "1.0",
                "material_id": material_id,
                "material_version": "1.0.0",
                "identity": {"name": name, "family": "generic", "manufacturer": None, "grade": None,
                             "description": None, "aliases": [], "tags": []},
                "properties": {"electromagnetic": {"relative_permeability": {"type": "scalar", "value": 1, "unit": "1"}}},
                "provenance": {"source_type": "USER_INPUT", "reference": None, "date": None, "notes": None},
                "version_metadata": {"author": "smoke", "updated_at": "2026-10-13T00:00:00+00:00", "change_note": "x"},
            }
        )

    root = tempfile.mkdtemp()
    master = JsonMaterialRepository(root)
    master.create(record("user:air", "Air"))
    master.create(record("user:iron", "Iron"))
    (lib,) = studymaterials.import_materials(study, [record("user:air", "Air")])
    assert isinstance(lib.ViewObject.Proxy, taskpanels.ViewProviderLibraryMaterial)
    picker = materialstandins.MaterialPicker(MaterialManager(repository=master), {"user:air"})
    items = [picker.list.item(i) for i in range(picker.list.count())]
    disabled = [i.text() for i in items if not i.flags() & taskpanels.QtCore.Qt.ItemIsEnabled]
    assert len(items) == 2 and len(disabled) == 1 and disabled[0].startswith("Air"), [i.text() for i in items]
    next(i for i in items if i.text().startswith("Iron")).setSelected(True)
    assert [m.material_id for m in picker.selected()] == ["user:iron"]
    picker.reject()
    window = materialstandins.open_editor(study, "user:air")
    assert window.isVisible() and materialstandins.open_editor(study) is window
    window.close()
    panel = taskpanels.ItemPanel(mat)
    panel.material.setCurrentIndex(panel.material.findData(lib.Name))
    panel.potential.setValue(2)
    Gui.Control.showDialog(panel)
    panel.accept()
    assert mat.LibraryMaterial == lib and mat.Potential == 2, (mat.LibraryMaterial, mat.Potential)
    select(study.MaterialLibraryGroup.Name)
    assert shown_folders()["Material Library"].item(0, 3).text() == mat.Label
    taskpanels.warn = lambda text: log.append("refused: " + text)
    assert lib.ViewObject.Proxy.onDelete(lib.ViewObject, []) is False, "deleted a used material"
    assert objects.library_materials(study) == [lib]
    log.append("material library ok")
```

(The `rows` check for `"Material Library": 0` runs before this block, so the table is empty there.)

Run (PowerShell, repo root): `pixi run freecad tests\freecad_addon\gui_smoke.py; Get-Content "$env:TEMP\ems_gui_smoke.txt"`
Expected: last line `FAIL` (no `materialstandins` module yet).

- [ ] **Step 2: Create the stand-ins module**

Create `freecad_addon/emsolution/materialstandins.py`:

```python
"""Temporary Material Manager GUI for the Material Library: a picker and the library's own editor window.

Delete this module when ems_material ships MaterialPickerDialog and MaterialEditorWidget
(docs/superpowers/specs/2026-10-13-ems-material-manager-widgets-prd.md).
"""

import FreeCADGui as Gui
from PySide import QtCore, QtWidgets

from ems_material import MaterialManager, MaterialManagerError

from . import objects, studymaterials

_editors = {}  # (document name, Study Name) -> MaterialManagerWindow


class MaterialPicker(QtWidgets.QDialog):
    """Search the Material Manager and pick materials; IDs in taken cannot be picked."""

    def __init__(self, manager, taken, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import from Material Manager")
        self.manager, self.taken = manager, set(taken)
        self.search = QtWidgets.QLineEdit()
        self.search.setPlaceholderText("Search name, ID, manufacturer, tag…")
        self.list = QtWidgets.QListWidget()
        self.list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.search)
        layout.addWidget(self.list)
        layout.addWidget(buttons)
        self.resize(480, 520)
        self.search.textChanged.connect(self.fill)
        self.fill()

    def fill(self, *_):
        text = self.search.text().strip()
        self.list.clear()
        for m in self.manager.search(text=text) if text else self.manager.list():
            item = QtWidgets.QListWidgetItem(f"{m.name} — {m.family} ({self.manager.source_for(m.material_id)})")
            item.setData(QtCore.Qt.UserRole, m.material_id)
            if m.material_id in self.taken:
                item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEnabled & ~QtCore.Qt.ItemIsSelectable)
                item.setToolTip("already in Material Library")
            self.list.addItem(item)

    def selected(self):
        return [self.manager.get(i.data(QtCore.Qt.UserRole)) for i in self.list.selectedItems()]


def _root(parent):
    root = studymaterials.library_root()
    if root:
        return root
    root = QtWidgets.QFileDialog.getExistingDirectory(parent, "Material Manager root (folder with manager.config.json)")
    if not root:
        return None
    from ems_material.gui.product_exchange import remember_library_root

    remember_library_root(root)  # shared with eMotorSolution
    return root


def pick_materials(study, parent=None):
    """Ask for materials and copy them into the Material Library. Returns the new objects."""
    parent = parent or Gui.getMainWindow()
    root = _root(parent)
    if root is None:
        return []
    try:
        manager = MaterialManager(root)
        taken = {o.MaterialId for o in objects.library_materials(study)}
        dialog = MaterialPicker(manager, taken, parent)
        if dialog.exec() != QtWidgets.QDialog.Accepted:
            return []
        return studymaterials.import_materials(study, dialog.selected())
    except MaterialManagerError as exc:
        QtWidgets.QMessageBox.warning(parent, "Material Manager", str(exc))
        return []


def open_editor(study, material_id=None):
    """The library's editor window on the Study's Material Library; one per Study."""
    from ems_material.gui import MaterialManagerWindow
    from . import taskpanels

    key = (study.Document.Name, study.Name)
    window = _editors.get(key)
    if window is None:
        repository = studymaterials.StudyMaterialRepository(study, on_change=taskpanels.refresh_library_views)
        window = MaterialManagerWindow(MaterialManager(repository=repository), Gui.getMainWindow())
        window.setWindowTitle(f"Material Library — {study.Label}")
        window.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        window.destroyed.connect(lambda *_: _editors.pop(key, None))
        _editors[key] = window
    window.reload_materials(select_id=material_id)
    window.show()
    window.raise_()
    window.activateWindow()
    return window
```

- [ ] **Step 3: Material Library view provider and folder panel**

In `taskpanels.py`, add `import weakref` after `from collections import Counter`.

Add after `class ViewProviderFolder`:

```python
def warn(text):
    QtWidgets.QMessageBox.warning(Gui.getMainWindow(), "EMSolution", text)


class ViewProviderLibraryMaterial(_ViewProvider):
    """A Material Library entry: material icon; double-click edits it; deleting a used one is refused."""

    def attach(self, vobj):
        super().attach(vobj)
        vobj.addDisplayMode(coin.SoGroup(), "Default")

    def getDisplayModes(self, vobj):
        return ["Default"]

    def getDefaultDisplayMode(self):
        return "Default"

    def getIcon(self):
        return icon("material")

    def doubleClicked(self, vobj):
        from . import materialstandins

        materialstandins.open_editor(objects.owner_study(vobj.Object), vobj.Object.MaterialId)
        return True

    def onDelete(self, vobj, subelements):
        users = objects.material_users(vobj.Object)
        if users:
            warn(f"{vobj.Object.Label} is used by: " + ", ".join(m.Label for m in users))
            return False
        return True
```

Add before `class FolderView`:

```python
_library_views = weakref.WeakSet()  # open Material Library panels


def refresh_library_views():
    for view in list(_library_views):
        view.fill()
```

In `FolderView.__init__`, move the table filling into a method so it can refresh. Replace

```python
        self.rows = rows(study)
```

with

```python
        self.row_source = rows
        self.rows = rows(study)
```

and replace

```python
        for r, (_item, _refs, cells) in enumerate(self.rows):
            for c, text in enumerate(cells):
                self.table.setItem(r, c, QtWidgets.QTableWidgetItem(text))
        self.table.resizeColumnsToContents()
```

with

```python
        self.fill()
```

Then, right after `layout.addWidget(self.table)`, add:

```python
        if isinstance(folder.Proxy, objects.MaterialLibraryFolder):
            buttons = QtWidgets.QHBoxLayout()
            for text, slot in (
                ("Import from Material Manager…", self.import_materials),
                ("Edit…", self.edit_material),
                ("Delete", self.delete_materials),
            ):
                button = QtWidgets.QPushButton(text)
                button.clicked.connect(slot)
                buttons.addWidget(button)
            layout.addLayout(buttons)
            _library_views.add(self)
```

Add these methods to `FolderView`:

```python
    def fill(self):
        if self.study.Document is None:  # the document was closed
            return
        self.rows = self.row_source(self.study)
        self.table.setRowCount(len(self.rows))
        for r, (_item, _refs, cells) in enumerate(self.rows):
            for c, text in enumerate(cells):
                self.table.setItem(r, c, QtWidgets.QTableWidgetItem(text))
        self.table.resizeColumnsToContents()

    def selected_items(self):
        return [self.rows[r][0] for r in sorted({i.row() for i in self.table.selectedIndexes()})]

    def import_materials(self):
        from . import materialstandins

        if materialstandins.pick_materials(self.study, self.form):
            self.fill()

    def edit_material(self):
        from . import materialstandins

        selected = self.selected_items()
        materialstandins.open_editor(self.study, selected[0].MaterialId if selected else None)

    def delete_materials(self):
        selected = self.selected_items()
        used = [lib for lib in selected if objects.material_users(lib)]
        if used:
            return warn("In use, not deleted: " + ", ".join(lib.Label for lib in used))
        doc = self.study.Document
        doc.openTransaction("Delete materials")
        for lib in selected:
            doc.removeObject(lib.Name)
        doc.commitTransaction()
        doc.recompute()
        self.fill()
```

Change `open_item` so a Material Library row opens the editor:

```python
    def open_item(self, row, _column):
        item = self.rows[row][0]
        if isinstance(item.Proxy, objects.LibraryMaterial):
            from . import materialstandins

            materialstandins.open_editor(self.study, item.MaterialId)
        elif self.study.Dimension == "3D":
            Gui.Control.showDialog(ItemPanel(item))
```

- [ ] **Step 4: Attach the view provider when objects are created**

`objects.py` has no GUI code, so attach it where objects are made in the GUI. In `studymaterials.import_materials` and `StudyMaterialRepository.create`, objects are made through `objects.make_library_material`; add the view provider there, guarded like `_make_folder` does. In `objects.make_library_material`, after `obj.Record = record_json`, add:

```python
    if getattr(obj, "ViewObject", None) is not None:  # GUI running
        from . import taskpanels

        taskpanels.ViewProviderLibraryMaterial(obj.ViewObject)
```

(This mirrors `_make_folder`, which already imports `taskpanels` lazily for the folder view provider.)

- [ ] **Step 5: Material item panel: Material combo and POTENTIAL**

In `ItemPanel.__init__`, after the `self.size` block (before `self.refs = ...`), add:

```python
        self.material = self.potential = None
        if isinstance(obj.Proxy, objects.Material):
            self.material = QtWidgets.QComboBox()
            self.material.addItem(objects.NO_MATERIAL, "")
            for lib in objects.library_materials(study):
                self.material.addItem(lib.Label, lib.Name)
            current = obj.LibraryMaterial.Name if obj.LibraryMaterial else ""
            self.material.setCurrentIndex(self.material.findData(current))
            layout.addRow("Material", self.material)
            self.potential = QtWidgets.QSpinBox()
            self.potential.setRange(0, 1000000)
            self.potential.setValue(obj.Potential)
            layout.addRow("POTENTIAL", self.potential)
```

In `ItemPanel.accept`, after the `if self.size is not None:` block, add:

```python
        if self.material is not None:
            name = self.material.currentData()
            self.obj.LibraryMaterial = doc.getObject(name) if name else None
            self.obj.Potential = self.potential.value()
```

- [ ] **Step 6: Add Material opens its panel**

In `commands.py`, `AddMaterial.Activated`, replace

```python
        if name:
            _create(study, "Add Material", lambda: objects.make_material(study, name, bodies))
```

with

```python
        if name:
            obj = _create(study, "Add Material", lambda: objects.make_material(study, name, bodies))
            Gui.Control.showDialog(taskpanels.ItemPanel(obj))
```

- [ ] **Step 7: Run all tests and the GUI smoke test**

Run: `pixi run pytest tests/freecad_addon -q`
Expected: all PASS.

Run (PowerShell, repo root): `pixi run freecad tests\freecad_addon\gui_smoke.py; Get-Content "$env:TEMP\ems_gui_smoke.txt"`
Expected: lines include `material library ok`, last line `PASS`. If it fails, read the traceback in that file. FreeCAD may report a crash on quit after `PASS`; that is known and fine.

- [ ] **Step 8: Format, lint, commit**

```bash
pixi run ruff format freecad_addon/emsolution/materialstandins.py freecad_addon/emsolution/taskpanels.py freecad_addon/emsolution/objects.py freecad_addon/emsolution/commands.py tests/freecad_addon/gui_smoke.py
pixi run lint
git add freecad_addon/emsolution tests/freecad_addon/gui_smoke.py
git commit -m "Add the Material Library panel, Material Manager stand-ins and assignment controls

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

If `ruff format` reformats untouched code in `commands.py` (not yet Ruff-formatted), revert those hunks with `git checkout -p` before committing.
