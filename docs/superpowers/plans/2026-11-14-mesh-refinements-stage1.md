# Mesh refinements, Stage 1: Refine Near in ordinary Studies — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A Refine Near item (fine size at picked faces, edges, vertices or bodies, growing to a coarse size over a
distance) that meshes in ordinary 2D and 3D Studies, with and without sliding motion, plus the Stage 1 review catalogue.

**Architecture:** A new `RefineNear` document object in the Mesh Sizes folder is validated, written to `job.json` as a
`"refine"` list (picked sub-elements exported as BREP files like Mesh Size picks), and turned by the mesher into gmsh
`Distance` → `Threshold` (→ `Restrict`) fields appended to the existing background `Min` field. Studies with Symmetric
Groups refuse the item in Stage 1 (Stage 2 adds them), so Stage 1 writes `"refine"` from `write_job`'s ordinary-Study
branch; Stage 2 moves it into `_body_job` (spec 6.3) for the cell and free jobs.

**Tech Stack:** FreeCAD 1.1 add-on (Python 3.11, PySide), gmsh 4.15.2 Python API, unittest/pytest via pixi.

**Spec:** `docs/superpowers/specs/2026-11-14-mesh-refinements-design.md` (sections 5.1, 6, 8, 9 Stage 1, 10). Read it
before starting; this plan argues from it.

## Global Constraints

- Run everything through pixi: `pixi run -e addon test-addon`, `pixi run -e addon pytest tests/freecad_addon/<file> -k <name>`,
  `pixi run lint`, `pixi run format`. Never `pip install`.
- Branch `freecad/mesh-refinements` off `main`; commit per task; never `--no-verify`.
- Ruff, line length 120, double quotes; don't add trailing commas to constructs that fit on one line; never reorder
  imports; format only files you changed.
- Mesher modules (`meshcommon.py`, `mesher.py`, `mesher2d.py`) never import FreeCAD. GUI code only in `commands.py`,
  `taskpanels.py` (and the other GUI modules AGENTS.md lists). `objects.py`, `jobwriter.py`, `validation.py` stay GUI-free.
- Every Threshold uses `StopAtDistMax = 1`. A Study without Refine Near items writes no `"refine"` key and meshes
  exactly as before.
- Units are mm. Property group of the new item: `"EMSolution"`.
- GUI changes need the smoke test: `pixi run -e addon freecad tests\freecad_addon\gui_smoke.py` from PowerShell (not Git
  Bash, which strips the backslashes), then the last line of `%TEMP%\ems_gui_smoke.txt` must be `PASS`.

## Review Focus

1. Refine Near on a face of the Air Region (e.g. near the outer boundary): the face must export from the air's built
   shape and merge in the mesher → Task 3 test `test_refine_near_on_an_air_face_goes_to_the_job`.
2. A large growth distance must not coarsen or cap anything outside its reach → Task 4 test
   `test_refine_near_does_not_cap_sizes_beyond_its_reach`.
3. `LimitTo` must leave the limited body's own boundary edges sized (a `Restrict` without the boundary gives one
   element per edge) → Task 4 test `test_limit_to_keeps_the_body_boundary_sized`.
4. A whole-body pick on a body with no neighbour (all its faces on the domain boundary) refines nothing and says so,
   rather than failing → Task 4 test `test_whole_body_pick_with_no_shared_face_notes_and_meshes`.
5. A structured (transfinite / sliding NDIV) edge next to a refinement keeps its division count → Task 5 test
   `test_transfinite_edge_keeps_its_count_next_to_a_refinement`.

---

### Task 1: The Refine Near object

**Files:**
- Modify: `freecad_addon/emsolution/objects.py` (proxy beside `MeshSize` ~line 320; `make_refine_near` beside
  `make_mesh_size` ~912; `refine_items` beside `mesh_sizes` ~1388; `is_item` ~1602; `_size_text` ~1689)
- Test: `tests/freecad_addon/test_study.py`

**Interfaces:**
- Produces:
  - `class RefineNear(_Proxy)` with properties `References` (`App::PropertyLinkSubListGlobal`), `FineSize`,
    `FineDistance`, `CoarseSize`, `GrowthDistance` (`App::PropertyLength`), `LimitTo` (`App::PropertyLinkListGlobal`).
  - `make_refine_near(study, refs, fine=None, coarse=None, growth=None, fine_distance=0.0, limit_to=()) -> obj`;
    defaults (spec 12.1): `fine = DefaultMeshSize / 2`, `coarse = DefaultMeshSize`, `growth = 5 * fine`. Label
    `"RefineNear"`.
  - `refine_items(study) -> list` (Refine Near items of the Mesh Sizes folder, tree order).
  - `_size_text(item)` for Refine Near: `f"{fine:g} → {coarse:g} mm over {growth:g} mm"`, plus
    `f" in {', '.join(display_name(b) for b in LimitTo)}"` when `LimitTo` is set.
  - `is_item` and `item_refs` cover it (`item_refs` returns `References` only).

- [ ] **Step 1: Write the failing tests** in `StudyTest`:

```python
def test_refine_near_defaults_and_row(self):
    a = self.box("A")
    self.study.MeshSizesGroup.DefaultMeshSize = 4.0
    item = objects.make_refine_near(self.study, [(a, "Edge1")])
    self.assertEqual((item.FineSize.Value, item.CoarseSize.Value, item.GrowthDistance.Value), (2.0, 4.0, 10.0))
    self.assertEqual(item.FineDistance.Value, 0.0)
    self.assertEqual(objects.refine_items(self.study), [item])
    self.assertTrue(objects.is_item(item))
    self.assertEqual(objects.item_refs(item), [(a, "Edge1")])
    self.assertEqual(objects.mesh_size_rows(self.study), [(item, [(a, "Edge1")], ["RefineNear", "2 → 4 mm over 10 mm", "A.Edge1"])])

def test_refine_near_row_names_its_limit(self):
    a = self.box("A")
    objects.make_refine_near(self.study, [(a, "Face2")], 0.4, 4, 10, limit_to=[a])
    self.assertEqual(objects.mesh_size_rows(self.study)[0][2][1], "0.4 → 4 mm over 10 mm in A")
```

- [ ] **Step 2: Run them to see them fail**

Run: `pixi run -e addon pytest tests/freecad_addon/test_study.py -k refine_near -v`
Expected: FAIL, `module 'emsolution.objects' has no attribute 'make_refine_near'`.

- [ ] **Step 3: Implement** the proxy, `make_refine_near`, `refine_items`, and the `is_item` / `_size_text` branches
  in `objects.py` (follow `MeshSize` / `make_mesh_size`; `_add(study, "MeshSizesGroup", RefineNear, "RefineNear")`).

- [ ] **Step 4: Run the tests to see them pass**

Run: `pixi run -e addon pytest tests/freecad_addon/test_study.py -k "refine_near or mesh_size or transfinite" -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add freecad_addon/emsolution/objects.py tests/freecad_addon/test_study.py
git commit -m "FreeCAD add-on: Refine Near item"
```

---

### Task 2: Validation of Refine Near

**Files:**
- Modify: `freecad_addon/emsolution/validation.py` (`_kind` ~167, `_links` ~177 needs nothing new beyond `_kind`,
  `_settings` ~231)
- Test: `tests/freecad_addon/test_study.py`

**Interfaces:**
- Consumes: `objects.RefineNear`, `objects.make_refine_near`, `objects.refine_items` (Task 1).
- Produces: these exact messages (`validation.validate(study)` problems):
  - error `f"Refine Near {label}: the fine size must be greater than 0."`
  - error `f"Refine Near {label}: the coarse size must not be smaller than the fine size."`
  - error `f"Refine Near {label}: the growth distance must be greater than 0."`
  - error `f"Refine Near {label}: the fine distance must not be negative."`
  - error (Study with Symmetric Groups) `f"Refine Near {label}: refinements in a Study with Symmetric Groups are not handled yet, a limit of the tool."`
  - warning (a `LimitTo` body the Study does not mesh, i.e. not in the `with_air` set) `f"Refine Near {label}: {display_name(body)} in Limit to is not meshed by the Study; it has no effect there."`
  - The existing `_links` messages apply with kind `"Refine Near"` (e.g. `"Refine Near X refers to nothing (were its bodies deleted?). Pick again or delete it."`).

- [ ] **Step 1: Write the failing tests**

```python
def problems(self, level=None):
    return [p.text for p in validation.validate(self.study) if level is None or p.severity == level]

def test_refine_near_settings_are_checked(self):
    a = self.box("A")
    item = objects.make_refine_near(self.study, [(a, "Edge1")], 0.0, 1.0, 0.0, fine_distance=-1.0)
    texts = self.problems()
    for end in ("the fine size must be greater than 0.", "the growth distance must be greater than 0.",
                "the fine distance must not be negative."):
        self.assertIn(f"Refine Near {item.Label}: {end}", texts)
    item.FineSize, item.CoarseSize, item.GrowthDistance, item.FineDistance = 2.0, 1.0, 5.0, 0.0
    self.assertIn(f"Refine Near {item.Label}: the coarse size must not be smaller than the fine size.", self.problems())

def test_refine_near_on_a_deleted_body_refers_to_nothing(self):
    self.box("A")
    b = self.box("B", 20)
    item = objects.make_refine_near(self.study, [(b, "Edge1")])
    self.doc.removeObject("B")
    self.doc.recompute()
    self.assertIn(f"Refine Near {item.Label} refers to nothing (were its bodies deleted?). Pick again or delete it.", self.problems())

def test_refine_near_limit_to_an_unmeshed_body_warns(self):
    a, b = self.box("A"), self.box("B", 20)
    self.exclude(b)
    item = objects.make_refine_near(self.study, [(a, "Edge1")], limit_to=[b])
    self.assertIn(f"Refine Near {item.Label}: B in Limit to is not meshed by the Study; it has no effect there.", self.problems(validation.WARNING))
```

  plus `test_refine_near_is_refused_with_symmetric_groups`: build the smallest grouped Study the existing tests use
  (find one with `objects.make_symmetric_group` in `tests/freecad_addon/test_symmetric_study.py` and reuse its
  helper), add a Refine Near on a cell object, assert the symmetric message above is in the errors.

- [ ] **Step 2: Run them to see them fail**

Run: `pixi run -e addon pytest tests/freecad_addon/test_study.py tests/freecad_addon/test_symmetric_study.py -k refine_near -v`
Expected: FAIL (`KeyError` in `_kind`, or the messages missing).

- [ ] **Step 3: Implement** `_kind` entry `objects.RefineNear: "Refine Near"`; the four setting checks in `_settings`
  (only for items with a meshed reference, like Mesh Size's check); the `LimitTo` warning (needs `with_air`, which
  `_settings` already receives as `included`); the symmetric refusal (`objects.is_grouped(study)`).

- [ ] **Step 4: Run the tests to see them pass**

Run: `pixi run -e addon pytest tests/freecad_addon/test_study.py tests/freecad_addon/test_symmetric_study.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add freecad_addon/emsolution/validation.py tests/freecad_addon/test_study.py tests/freecad_addon/test_symmetric_study.py
git commit -m "FreeCAD add-on: validate Refine Near"
```

---

### Task 3: Refine Near in job.json

**Files:**
- Modify: `freecad_addon/emsolution/jobwriter.py` (new `refine_entries`; called from `write_job` in the non-grouped
  branch after `job["air"]` is set)
- Test: `tests/freecad_addon/test_study.py`

**Interfaces:**
- Consumes: Task 1's object; `export_subs`, `meshed_shape` (existing).
- Produces: `refine_entries(study, folder, ids) -> list[dict]`, where `ids` is `{body or air Name: [MAT_ID, ...]}`
  (one MAT_ID per body; both side MAT_IDs `MatIds[f"{air}#fixed"]`, `MatIds[f"{air}#moving"]` for a sliding air).
  One entry per item, items in tree order, only items with at least one reference on a meshed body or the air:

```json
{"name": "<Label>", "files": ["geometry/refine_<k>_<j>_<n>.brep", "..."], "whole": [<MAT_ID>, "..."],
 "fine": 0.4, "fine_distance": 0.0, "coarse": 4.0, "growth": 10.0, "limit_to": [<MAT_ID>, "..."]}
```

  `k` = item number (1-based), `j` = body number within the item, `n` from `export_subs`. Whole-body picks go to
  `whole`, sub-element picks to `files`. `write_job` sets `job["refine"]` only when the list is non-empty.

- [ ] **Step 1: Write the failing tests**

```python
def test_job_without_refine_near_has_no_refine_key(self):
    a = self.box("A")
    self.assign([a])
    with open(jobwriter.write_job(self.study), encoding="utf-8") as fh:
        self.assertNotIn("refine", json.load(fh))

def test_refine_near_goes_to_the_job(self):
    a, b = self.box("A"), self.box("B", 10)
    self.assign([a, b])
    objects.make_refine_near(self.study, [(a, "Edge1"), (a, "Vertex1"), (b, "")], 0.4, 4, 10, 0.5, limit_to=[a])
    with open(jobwriter.write_job(self.study), encoding="utf-8") as fh:
        job = json.load(fh)
    ids = self.study.MatIds
    (entry,) = job["refine"]
    self.assertEqual(entry["name"], "RefineNear")
    self.assertEqual(len(entry["files"]), 2)
    self.assertTrue(all(os.path.exists(self.scratch(f)) for f in entry["files"]))
    self.assertEqual(entry["whole"], [int(ids[b.Name])])
    self.assertEqual(entry["limit_to"], [int(ids[a.Name])])
    self.assertEqual((entry["fine"], entry["fine_distance"], entry["coarse"], entry["growth"]), (0.4, 0.5, 4.0, 10.0))
```

  plus `test_refine_near_on_an_air_face_goes_to_the_job` (Review Focus 1): a body and an Air Region (copy how the
  existing air tests in `test_study.py`/`test_air.py` make one), a Refine Near on `(air, "Face1")`; assert one file
  is written, it exists, and its bounding box lies on the air's `Face1`.
  plus `test_refine_near_limited_to_a_sliding_air_lists_both_sides`: reuse an existing sliding-motion Study set-up
  from `test_study.py` or `test_air.py` (search `"Sliding motion"`), Refine Near limited to the Air Region; assert
  `limit_to` equals both side MAT_IDs.

- [ ] **Step 2: Run them to see them fail**

Run: `pixi run -e addon pytest tests/freecad_addon/test_study.py -k "refine" -v`
Expected: the "no refine key" test passes already; the others FAIL with `KeyError: 'refine'`.

- [ ] **Step 3: Implement** `refine_entries` and the call in `write_job`.

- [ ] **Step 4: Run the tests to see them pass**

Run: `pixi run -e addon pytest tests/freecad_addon/test_study.py tests/freecad_addon/test_air.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add freecad_addon/emsolution/jobwriter.py tests/freecad_addon/test_study.py
git commit -m "FreeCAD add-on: write Refine Near to the mesh job"
```

---

### Task 4: Refine Near fields in the 3D mesher

**Files:**
- Modify: `freecad_addon/emsolution/meshcommon.py` (new `background_fields`, `add_to_background`, `apply_refinements`
  near `apply_size_fields` ~line 18)
- Modify: `freecad_addon/emsolution/mesher.py` (`build`: import the refine files right after the transfinite files,
  before `add(...)` is first called; map them after `tf_maps`; call `apply_refinements` after `apply_size_fields`)
- Test: `tests/freecad_addon/test_mesher.py`

**Interfaces:**
- Consumes: the `"refine"` entries of Task 3.
- Produces (meshcommon, used again by Task 5 and Stage 2):
  - `add_to_background(fields: list[int]) -> None`: appends field tags to the existing background `Min` field's
    `FieldsList` (the field `apply_size_fields` made; same lookup as `meshgroups._new_size_field`).
  - `real_boundary(dim: int, tags: list[int]) -> list[int]`: the (dim-1) boundary entities of the given entities that
    touch a dim-entity outside them (faces shared with the air or other bodies; faces on the domain boundary and
    between pieces of the same body are left out; spec 5.2).
  - `apply_refinements(items: list[tuple[dict, dict[int, list[int]]]], body_tags: dict[int, list[int]], dim: int) -> None`:
    `items` = one `(entry, picked)` per refine entry, `picked` = `{entity dim: [final tags]}` from its files. Whole
    MAT_IDs add `real_boundary(dim, body_tags[m])` to `picked[dim - 1]`; a whole MAT_ID with an empty real boundary
    gets `_note(f"Refine Near {name}: MAT_ID {m} has no face shared with another region; it refines nothing there")`.
    Per entry: one `Distance` on all picked lists (`PointsList`/`CurvesList`/`SurfacesList`), `Sampling` per the rule
    below; one `Threshold` (`SizeMin = fine`, `SizeMax = coarse`, `DistMin = fine_distance`,
    `DistMax = fine_distance + growth`, `StopAtDistMax = 1`); with `limit_to`, a `Restrict` on the limited entities of
    dimension `dim` and their (dim-1) boundary (`IncludeBoundary`-like; add their curves too in 3D if Review Focus 3's
    test needs it). Appends the outer field of each entry with `add_to_background`. An entry whose picks are all
    empty adds no field.
  - Sampling rule: `n = ceil(diag / (fine / 2))` where `diag` is the bounding-box diagonal of the picked entities;
    clamp to [20, 500] when only points/curves are picked, [10, 100] when a surface is picked (gmsh samples surfaces
    on an n × n grid).
- mesher.py: a refine file that does not merge (no entity above it, the same test the size files use) raises
  `JobError(f"refine near {name}: {file} did not merge with the bodies")`.

- [ ] **Step 1: Write the failing tests** in `MesherTest`, using `write_box`, `write_line`, `write_rect`, `run_job`
  (`extra={"refine": [...]}`) and `read_nodes`:

```python
def refine(self, files=(), whole=(), fine=0.05, coarse=0.5, growth=0.3, fine_distance=0.0, limit_to=()):
    return {"name": "Near", "files": ["geometry/" + f for f in files], "whole": list(whole), "fine": fine,
            "fine_distance": fine_distance, "coarse": coarse, "growth": growth, "limit_to": list(limit_to)}

def test_refine_near_an_edge_grades_away_from_it(self):
    write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
    write_line(self.geo("refine_1_1_1.brep"), (0, 0, 0), (1, 0, 0))
    r = self.run_job([self.vol(1, "Box", "vol_1.brep")], extra={"refine": [self.refine(["refine_1_1_1.brep"])]})
    self.assertEqual(r.returncode, 0, r.stderr)
    nodes = read_nodes(os.path.join(self.dir, "pre_geom.msh"))
    near = sum(math.hypot(y, z) < 0.1 for x, y, z in nodes)
    far = sum(math.hypot(y - 1, z - 1) < 0.1 for x, y, z in nodes)
    self.assertGreater(near, 10 * max(far, 1))

def test_refine_near_does_not_cap_sizes_beyond_its_reach(self):  # Review Focus 2
    # the same box meshed with no refine key and with a refinement of coarse 0.2 whose reach (0.3) ends far from x = 1:
    # nodes within 0.25 of the x = 1 face differ by less than 20 %
    ...

def test_limit_to_keeps_the_refinement_in_that_body(self):
    # boxes 1 (x 0..1) and 2 (x 1..2), refine near the shared face x = 1 limited to MAT_ID 1:
    # nodes with 0.9 < x < 1 outnumber nodes with 1 < x < 1.1 by more than 5 x
    ...

def test_limit_to_keeps_the_body_boundary_sized(self):  # Review Focus 3
    # same set-up: the edge of box 1 from (0,0,0) to (0,1,0) (far from the face, on box 1's boundary) has at least
    # 1 / 0.5 + 1 = 3 nodes, i.e. it is not one element
    ...

def test_whole_body_pick_refines_only_shared_faces(self):
    # boxes 1 and 2 as above, whole = [1]: nodes near x = 1 (shared) outnumber nodes near x = 0 (domain boundary) by 5 x
    ...

def test_whole_body_pick_with_no_shared_face_notes_and_meshes(self):  # Review Focus 4
    # one box, whole = [1]: returncode 0 and "has no face shared with another region" in r.stderr
    ...

def test_refine_file_off_the_bodies_fails(self):
    # a line floating above the box: returncode 1, last stderr line has "ERROR:" and "refine near Near"
    ...
```

  Write the bodies marked `...` with the numbers in their comments (the assertions are those comments).

- [ ] **Step 2: Run them to see them fail**

Run: `pixi run -e addon pytest tests/freecad_addon/test_mesher.py -k "refine or limit_to or whole_body" -v`
Expected: FAIL (the refinement has no effect, so the density assertions fail; the "off the bodies" test passes for
the wrong reason or fails).

- [ ] **Step 3: Implement** `add_to_background`, `real_boundary`, `apply_refinements` in `meshcommon.py`, and the
  import/map/call in `mesher.build`.

- [ ] **Step 4: Run the tests to see them pass, and the whole mesher file**

Run: `pixi run -e addon pytest tests/freecad_addon/test_mesher.py -v`
Expected: PASS (all, including the existing tests).

- [ ] **Step 5: Commit**

```bash
git add freecad_addon/emsolution/meshcommon.py freecad_addon/emsolution/mesher.py tests/freecad_addon/test_mesher.py
git commit -m "FreeCAD add-on: Refine Near fields in the 3D mesher"
```

---

### Task 5: Refine Near in the 2D mesher

**Files:**
- Modify: `freecad_addon/emsolution/mesher2d.py` (`build`: import refine files with spans after the transfinite files;
  merge check with `_on_bodies(d, t, placed)` like the size files; call `apply_refinements(..., dim=2)`)
- Test: `tests/freecad_addon/test_mesher2d.py`

**Interfaces:**
- Consumes: `apply_refinements`, `real_boundary`, `add_to_background` (Task 4). In 2D, picks are points and curves,
  whole bodies give their real boundary curves, `limit_to` restricts surfaces and their boundary curves.

- [ ] **Step 1: Write the failing tests** in the 2D mesher test class, using its existing writers and `run_job`
  helper (mirror Task 4's helper `refine(...)`):
  - `test_refine_near_a_curve_grades_away_from_it_2d`: unit square at size 0.5, refine near its bottom edge (fine 0.05,
    coarse 0.5, growth 0.3): nodes with y < 0.1 outnumber nodes with y > 0.9 by more than 5 x.
  - `test_refine_near_a_vertex_2d`: refine near corner (0, 0): nodes within 0.1 of it ≥ 10.
  - `test_transfinite_edge_keeps_its_count_next_to_a_refinement` (Review Focus 5): the square with a transfinite top
    edge of 4 elements (use the file's transfinite helper) and a refinement on the left edge with growth 2.0 reaching
    the whole square: the top edge has exactly 5 nodes.
  - `test_whole_body_pick_refines_only_shared_curves_2d`: two squares side by side, whole = [1]: nodes near the shared
    edge x = 1 outnumber nodes near x = 0 by more than 3 x.

- [ ] **Step 2: Run them to see them fail**

Run: `pixi run -e addon pytest tests/freecad_addon/test_mesher2d.py -k "refine or transfinite_edge_keeps or whole_body" -v`
Expected: FAIL on the density assertions.

- [ ] **Step 3: Implement** the 2D import, merge check and call.

- [ ] **Step 4: Run the tests to see them pass**

Run: `pixi run -e addon pytest tests/freecad_addon/test_mesher2d.py tests/freecad_addon/test_mesher.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add freecad_addon/emsolution/mesher2d.py tests/freecad_addon/test_mesher2d.py
git commit -m "FreeCAD add-on: Refine Near fields in the 2D mesher"
```

---

### Task 6: Command, Refinement dropdown, panel and icons

**Files:**
- Create: `freecad_addon/icons/refinenear.svg`, `freecad_addon/icons/refinement.svg`
- Modify: `freecad_addon/emsolution/commands.py` (`AddRefineNear`; `Refinement` dropdown like `StructuredMesh`;
  `COMMANDS`, `TOOLBARS`, `MENU`, `context_names`)
- Modify: `freecad_addon/emsolution/taskpanels.py` (`ITEM_PICKS` entry; Refine Near settings in `ItemPanel`)
- Modify: `tests/freecad_addon/gui_smoke.py`

**Interfaces:**
- Consumes: Task 1 (`make_refine_near`, properties), Task 2 messages (Validate shows them).
- Produces:
  - Command `EMS_RefineNear`: MenuText `"Refine Near"`, ToolTip `"Fine elements at the selected faces, edges, vertices or bodies, growing to a coarse size"`, icon `refinenear`. Activated like `AddMeshSize`:
    `refs = objects.to_cells(study, taskpanels.selected_mesh_refs())`, `gate(study, [b for b, _ in refs])`,
    `_create_and_edit(study, "Add Refine Near", lambda: objects.make_refine_near(study, refs))`.
  - `REFINEMENTS = ("EMS_RefineNear",)` and dropdown command `EMS_Refinement` (MenuText `"Refinement"`, ToolTip
    `"Refine Near"`; Stages 3 and 4 add Air Grading and Skin Layer to the tuple and the tooltip), icon `refinement`.
  - `TOOLBARS` "EMSolution Mesh": `["EMS_MeshSize", "EMS_Refinement", "EMS_StructuredMesh", "EMS_SymmetricGroup"]`.
  - `MENU`: `*REFINEMENTS` right after `"EMS_MeshSize"`.
  - `context_names`: `"EMS_RefineNear"` right after `"EMS_MeshSize"` for every non-empty pick, including `"Air"`
    (`["EMS_Material", "EMS_MeshSize", "EMS_RefineNear"]`).
  - `ITEM_PICKS[objects.RefineNear]`: same tuple as `objects.MeshSize`'s.
  - Panel rows after Name: "Fine size", "Fine distance", "Coarse size", "Growth distance" (`_length_box`), then a
    "Limit to" list with its own Add selection / Remove buttons (whole bodies from the selection, via
    `objects.pick_body`, Air Region allowed), then the picks list. `accept` writes the four lengths and `LimitTo`;
    `unsaved()` reports them for the labels. The air gate allows Refine Near (`air = isinstance(obj.Proxy, (objects.MeshSize, objects.RefineNear))`).
  - Icons: 64 × 64 SVG in the style of `meshsize.svg` (green meshed square, `#a9dca1`/`#1e6b2c`, a badge circle bottom
    right). `refinenear.svg`: badge with a small target or converging arrows; `refinement.svg`: the dropdown's icon,
    the same mesh square getting denser toward one corner.

- [ ] **Step 1: Update the smoke test first**: expected `context_menu()` lists gain `"EMS_RefineNear"` after
  `"EMS_MeshSize"`; the `MENU`/`NAMES` assertion excludes `"EMS_Refinement"` as it excludes `"EMS_StructuredMesh"`;
  add a step after the Mesh Size steps: select `A` `Edge1`, `Gui.runCommand("EMS_RefineNear")`, set the panel's fine
  size to 0.5, add body `B` to Limit to, accept; assert `objects.refine_items(study)[0].FineSize.Value == 0.5` and
  its `LimitTo == [B]`; and that Validate shows no Refine Near error.

- [ ] **Step 2: Run the smoke test to see it fail**

Run (PowerShell): `pixi run -e addon freecad tests\freecad_addon\gui_smoke.py`, then
`Get-Content "$env:TEMP\ems_gui_smoke.txt" -Tail 3`
Expected: last line `FAIL` (unknown command or menu mismatch).

- [ ] **Step 3: Implement** the command, dropdown, menu, context entries, panel rows and the two icons.

- [ ] **Step 4: Run the smoke test and the add-on suite**

Run: the smoke command above → last line `PASS`; `pixi run -e addon test-addon` → all pass; `pixi run lint` → clean.

- [ ] **Step 5: Commit**

```bash
git add freecad_addon/icons/refinenear.svg freecad_addon/icons/refinement.svg freecad_addon/emsolution/commands.py freecad_addon/emsolution/taskpanels.py tests/freecad_addon/gui_smoke.py
git commit -m "FreeCAD add-on: Refine Near command, panel and icons"
```

---

### Task 7: The Stage 1 review catalogue

**Files:**
- Create: `experiments/refinement_catalogue/build_catalogue.py` (runner), `experiments/refinement_catalogue/rows.py`
  (the cases), `experiments/refinement_catalogue/render.py` (pictures), `experiments/refinement_catalogue/make_page.py`
  (the page)
- Modify: `experiments/.gitignore` (add `refinement_catalogue/**/*.FCStd`)

**Interfaces:**
- Consumes: the whole add-on (Tasks 1–6), `tests.freecad_addon.symcases.finish` and `mesh_and_read`, the FreeCAD path
  set-up of `experiments/symmetric_rules/success_list.py` (copy its `sys.path` lines; don't import it).
- Produces:
  - `rows.CASES`: `[(id, title, build, expected)]`, `build() -> study` (a new document), `expected` = `"meshes"` or a
    phrase of the refusal (Validate error or mesher `ERROR:` line), `picture` hints per row (`{"clip": "y"}` for 3D:
    cut plane through the refinement; `{"zoom": (x0, y0, x1, y1)}` optional).
  - `build_catalogue.py [--only ID ...]`: for each row, build, save the set-up Study to
    `experiments/refinement_catalogue/<id>/<id>.FCStd`, then mesh it into
    `C:\Users\hamed\Desktop\delme\refinement_studies\<id>\new\`; then delete its Refine Near items, save and mesh into
    `...\<id>\today\`. Writes `C:\Users\hamed\Desktop\delme\refinement_studies\results.json`:
    `[{"id", "title", "expected", "verdict" ("meshes" or the refusal text), "match": bool, "new": {"elements": {part: n}, "seconds"}, "today": {...}, "files": {...}}]`. Exit code 1 when a row does not match.
  - `render.py`: `render(msh_path, png_path, dim, clip=None, zoom=None)` with gmsh offscreen (`gmsh.fltk.initialize()`
    then `gmsh.write(png)`), 1000 × 800, entities coloured (`Mesh.ColorCarousel = 1`), 3D cut with `Mesh.Clip`,
    `General.ClipWholeElements`, `General.ClipOnlyDrawIntersectingVolume` (the recipe proven in the session's demos).
  - `make_page.py`: reads `results.json` and the pictures, writes `...\refinement_studies\catalogue.html` (one card per
    row: id, title, verdict, today/new pictures side by side, element counts per part for both, paths). Pictures
    embedded as data URIs.
- Rows (spec 9, Stage 1); sizes are mm, default mesh size 4 unless said:

| id | Study | Refine Near |
|---|---|---|
| RN-01 | 2D: rectangular magnet 40 × 10 in a Padding Air Region | its 4 corners (vertices), fine 0.3, coarse 4, growth 8 |
| RN-02 | 3D: magnet block 40 × 20 × 10 in an Air Region | one long edge, fine 0.5, coarse 4, growth 10 |
| RN-03 | 2D: stator ring with 6 teeth (r 30..50, teeth to r 31) and air | the teeth's tip edges, fine 0.4, coarse 3, growth 6 |
| RN-04 | 3D: two touching blocks (iron, copper) in air | their shared face, limited to the copper block |
| RN-05 | 3D: a copper block in air | the whole block |
| RN-06 | 2D: RN-01 plus a second Refine Near on one long edge (fine 0.6) and a Mesh Size 1 on another edge | smallest wins |
| RN-07 | 2D: RN-01's model | one outer edge of the Air Region, fine 1, coarse 4, growth 20 |
| RN-08 | 2D sliding: rotor disc r 25 with 4 surface magnets, stator ring r 30..50, Air Region, Rotational Sliding Interface (divisions 120) | the magnets (whole), fine 0.4, coarse 2, growth 3; the check: nodes on the sliding circle are equal in new and today |
| RN-09a/b/c | RN-01 with coarse < fine / growth 0 / the picked body deleted | refused: the Task 2 messages |

  For RN-08 build the sliding Study the way the existing ordinary sliding tests do (search `"Sliding motion"` in
  `tests/freecad_addon/test_air.py` / `test_study.py`); a row-specific `after(folder)` check counts nodes on the
  sliding circle in both meshes.

- [ ] **Step 1: Write `rows.py`, `render.py`, `make_page.py`, `build_catalogue.py`.**

- [ ] **Step 2: Run the catalogue**

Run: `pixi run -e addon python experiments/refinement_catalogue/build_catalogue.py`
Expected: every row `match: true`, exit code 0, `catalogue.html` and the pictures written.

- [ ] **Step 3: Look at every picture** (open the PNGs) and fix rows whose picture does not show the refinement
  clearly (cut plane, zoom). Re-run with `--only`.

- [ ] **Step 4: Commit**

```bash
git add experiments/refinement_catalogue experiments/.gitignore
git commit -m "Refinement catalogue: Stage 1 rows (Refine Near)"
```

---

### Task 8: Stage 1 check and hand-over

- [ ] **Step 1: Run** `pixi run -e addon test-addon` (all pass), `pixi run lint` (clean), the GUI smoke test (`PASS`).
- [ ] **Step 2: Publish** `catalogue.html` as an Artifact (private) and give the user the link plus the folder
  `C:\Users\hamed\Desktop\delme\refinement_studies` to open the Studies in FreeCAD.
- [ ] **Step 3: Stop.** Stage 2 starts only after the user has reviewed every row and their comments are addressed.
  Don't merge the branch; record the user's comments in the spec's status line.
