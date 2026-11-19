# Mesh refinements, Stage 3: Air Grading — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** An Air Grading item that makes the air's element size grow from the bodies' surface sizes to a far size over
a growth distance, in ordinary and symmetric Studies, 2D and 3D, with and without sliding motion, plus the Stage 3
catalogue rows.

**Architecture:** A new `AirGrading` object in the Mesh Sizes folder picks one air (the Air Region, or in a Study with
Symmetric Groups a free object that is air). The jobwriter writes it as a `"air_grading"` list on the job that holds
that air. In ordinary jobs, and in the surface mesh of free jobs, the mesher sets gmsh fields:
- the air's volume and its outer faces get a `Constant` at the far size;
- the faces the air shares with bodies keep the air's own size;
- an `Extend` from those shared faces, restricted to the air, grows the size between them.

Inside `meshfrozen.mesh_region` (the air around copies), boundary interpolation is switched off and an `Extend` on the
region's frozen boundary does the growing. The spike of 2026-11-15 (spec 7.3, "Spike result: Air Grading") measured
every piece.

**Tech Stack:** FreeCAD 1.1 add-on (Python 3.11, PySide), gmsh 4.15.2 Python API, numpy, pytest via pixi.

**Spec:** `docs/superpowers/specs/2026-11-14-mesh-refinements-design.md`: sections 5.3, 6, 7.3 (both spike results), 8
and 9 (Stage 3), and 12.1, 12.3 and 12.9. Read them before starting.

## Global Constraints

- Run everything through pixi:
  - `pixi run -e addon test-addon`
  - `pixi run -e addon pytest tests/freecad_addon/<file> -k <name>`
  - `pixi run lint`
  - `pixi run format`, then revert its change to the unrelated `highlight.py` if it makes one.
  - Never `pip install`.
- Branch `freecad/mesh-refinements` (Stage 2 ends at `48ee22a`). Commit per task, never `--no-verify`, never push or merge.
- Ruff:
  - line length 120, double quotes;
  - no trailing comma on a construct that fits on one line;
  - never reorder imports;
  - format only files you changed.
- Module rules:
  - The mesher modules (`meshcommon.py`, `mesher.py`, `mesher2d.py`, `meshgroups.py`, `meshfrozen.py`) never import FreeCAD.
  - GUI code goes only in `commands.py`, `taskpanels.py` and `labels.py`.
  - `objects.py`, `jobwriter.py` and `validation.py` stay GUI-free.
- A Study without Air Grading writes no `"air_grading"` key and meshes exactly as before. `mesh_region` called without
  `grading` behaves exactly as before.
- Defaults (spec 12.1):
  - `GrowthDistance = 10 × DefaultMeshSize`;
  - `FarSize = 0`, meaning the air's own size: its smallest whole-body Mesh Size, else the default size.
- The faces the air shares with bodies keep today's size, the smaller of the body's size and the air's size. A far size
  larger than the air's size never coarsens them (spec 12.9).
- Fields:
  - `Extend` with `DistMax = growth`, `SizeMax = far`, `Power = 1`.
  - Every `Threshold` has `StopAtDistMax = 1`.
  - All fields join the background `Min` through `meshcommon.add_to_background`.
- Units are mm. Property group `"EMSolution"`.
- GUI changes need the smoke test. Run `pixi run -e addon freecad tests\freecad_addon\gui_smoke.py` from PowerShell
  (Git Bash strips the backslashes and FreeCAD hangs). The last line of `%TEMP%\ems_gui_smoke.txt` must be `PASS`.

## Review Focus

1. **A far size above the air's size:** the faces the air shares with a body keep the smaller of the body's size and
   the air's size. Task 4 test: `test_far_size_does_not_coarsen_the_body_surface`.
2. **A body touching the domain boundary** (a symmetry plane of a half model): the air's face (2D: line) on that plane
   grades away from the body instead of jumping to the far size. The spike showed it jumps unless the `Restrict` lists
   the outer faces, the 3D `Extend` lists the shared faces' curves, and 2D gets the point threshold. Task 4 tests:
   `test_air_face_on_the_domain_boundary_grades_3d` and `..._2d`.
3. **A sliding Study with a structured gap:** the sliding surface keeps its divisions. Task 4 test:
   `test_sliding_divisions_unchanged_with_air_grading`.
4. **Air Grading and Refine Near on the same air:** both act, and the smaller size wins. Task 4 test:
   `test_air_grading_and_refine_near_on_the_air_both_apply`.
5. **The air beside copies in a free job:** the air's surface next to a copy grows from the copy's frozen edges and
   does not jump to the far size. The volume grows from the whole frozen boundary. Task 6 tests:
   `test_air_grading_grades_the_air_around_copies_3d` and `..._2d`.

---

### Task 1: The Air Grading object

**Files:**
- Modify: `freecad_addon/emsolution/objects.py`. Where each change goes:
  - the proxy after `RefineNear` (~line 332);
  - `make_air_grading` after `make_refine_near` (~936);
  - `air_gradings` after `refine_items` (~966);
  - `is_item` (~1635);
  - `_size_text` (~1724).
- Test: `tests/freecad_addon/test_study.py`

**Interfaces:**
- Produces:
  - `class AirGrading(_Proxy)`, with properties:
    - `References` (`App::PropertyLinkSubListGlobal`, "The air whose element size grows");
    - `GrowthDistance` (`App::PropertyLength`, "Distance over which the air's size grows to the far size");
    - `FarSize` (`App::PropertyLength`, "Element size far from the bodies; 0 = the air's own size").
  - `make_air_grading(study, refs=None, growth=None, far=0.0) -> obj`. Label `"AirGrading"`.
    - `refs` None means `[(air, "")]` for the Study's Air Region when there is one, else `[]`.
    - `growth` None means `10 * DefaultMeshSize`.
  - `air_gradings(study) -> list`: the Air Grading items in tree order.
  - `whole_body_size(study, body) -> float`: the smallest whole-body Mesh Size on body, else `DefaultMeshSize`.
    `jobwriter.air_size` gives the same value for the Air Region; leave it as it is.
  - `far_size(item) -> float`: `FarSize` when it is > 0, else `whole_body_size` of its first referenced body. With no
    reference, the default size.
  - `_size_text(item)`: `f"grows over {growth:g} mm to {far_size(item):g} mm"`.
  - `is_item` covers the class; `item_refs` needs no change (it returns `References`).
  - `air_refusal` needs no change: Air Grading is meant for the air.

- [ ] **Step 1: Write the failing tests** in `StudyTest`. Find how the existing tests make an Air Region: search
  `make_air_region` in `test_study.py` / `test_air.py`.

```python
def test_air_grading_defaults_and_row(self):
    a = self.box("A")
    air = self.air_region()  # the existing helper, or objects.make_air_region as the air tests do
    self.study.MeshSizesGroup.DefaultMeshSize = 4.0
    item = objects.make_air_grading(self.study)
    self.assertEqual(objects.item_refs(item), [(air, "")])
    self.assertEqual((item.GrowthDistance.Value, item.FarSize.Value), (40.0, 0.0))
    self.assertEqual(objects.air_gradings(self.study), [item])
    self.assertTrue(objects.is_item(item))
    self.assertEqual(objects.mesh_size_rows(self.study)[-1][2][1], "grows over 40 mm to 4 mm")

def test_air_grading_far_size_reads_the_air_size(self):
    self.box("A")
    air = self.air_region()
    objects.make_mesh_size(self.study, 12.0, [(air, "")])
    item = objects.make_air_grading(self.study, growth=50.0)
    self.assertEqual(objects.far_size(item), 12.0)
    item.FarSize = 30.0
    self.assertEqual(objects._size_text(item), "grows over 50 mm to 30 mm")
```

- [ ] **Step 2: Run them to see them fail**

Run: `pixi run -e addon pytest tests/freecad_addon/test_study.py -k air_grading -v`
Expected: FAIL, `module 'emsolution.objects' has no attribute 'make_air_grading'`.

- [ ] **Step 3: Implement** the proxy, `make_air_grading`, `air_gradings`, `whole_body_size`, `far_size`, and the
  `is_item` and `_size_text` branches. Follow `RefineNear` / `make_refine_near`.

- [ ] **Step 4: Run** `pixi run -e addon pytest tests/freecad_addon/test_study.py -v`. Expected: PASS.

- [ ] **Step 5: Commit** `FreeCAD add-on: Air Grading item`.

---

### Task 2: Validation of Air Grading

**Files:**
- Modify: `freecad_addon/emsolution/validation.py` (`_kind` ~167, `_settings` ~232)
- Test: `tests/freecad_addon/test_study.py`, `tests/freecad_addon/test_symmetric_study.py`

**Interfaces:**
- Consumes: Task 1.
- Produces these exact problems (`validation.validate(study)`):
  - Error, a referenced body that is not an air: `f"Air Grading {label}: {name} is not an air. Pick the Air Region (or, in a Study with Symmetric Groups, a free object that is air)."`.
    - An air is an Air Region, or a free body (not a cell object) in a Study with Symmetric Groups.
    - `name` is `objects.display_name(body)`.
  - Error, a sub-element pick: `f"Air Grading {label}: pick the whole air, not {body.Label}.{sub}."`.
  - Error, an air referenced by more than one Air Grading, on the later items: `f"Air Grading {label}: {name} already has Air Grading {first.Label}; one per air."`.
  - Error: `f"Air Grading {label}: the growth distance must be greater than 0."`.
  - `_kind` entry `objects.AirGrading: "Air Grading"`, so the existing `_links` messages apply (deleted air, unmeshed
    body).
  - No `FarSize ≥ 0` check: `App::PropertyLength` clamps negatives to 0. This is the Stage 1 ruling on `FineDistance`.

- [ ] **Step 1: Write the failing tests:**
  - `test_air_grading_settings_are_checked`: growth 0 gives the growth error.
  - `test_air_grading_on_a_body_is_refused`: a box body gives the "is not an air" error.
  - `test_air_grading_on_an_air_face_is_refused`: `(air, "Face1")` gives the whole-air error.
  - `test_two_air_gradings_on_one_air`: the second item gets the "already has" error and the first gets none.
  - In `test_symmetric_study.py`, `test_air_grading_on_a_free_object_is_allowed_and_on_a_cell_refused`:
    - use the motor fixture plus `add_free` from Stage 2's tests;
    - a free body gives no Air Grading error;
    - a cell object gives the "is not an air" error.

- [ ] **Step 2: Run** `pixi run -e addon pytest tests/freecad_addon/test_study.py tests/freecad_addon/test_symmetric_study.py -k air_grading -v`.
  Expected: FAIL (a `KeyError` in `_kind`, or missing messages).

- [ ] **Step 3: Implement.** Run the checks only for items with a meshed reference, as Refine Near does.

- [ ] **Step 4: Run** both test files in full. Expected: PASS.

- [ ] **Step 5: Commit** `FreeCAD add-on: validate Air Grading`.

---

### Task 3: Air Grading in job.json

**Files:**
- Modify: `freecad_addon/emsolution/jobwriter.py`. Add a new `air_grading_entries`, called from `write_job` (ordinary
  branch, after `refine`) and from `write_groups` (per free job, after `refine`).
- Test: `tests/freecad_addon/test_study.py`, `tests/freecad_addon/test_symmetric_study.py`

**Interfaces:**
- Consumes: Task 1 (`air_gradings`, `far_size`).
- Produces `air_grading_entries(study, ids) -> list[dict]`:
  - `ids` is `{body or air Name: [MAT_ID, ...]}`, the same map the `refine_ids` of both callers hold. A sliding air
    has both side MAT_IDs.
  - One entry per item whose referenced body is in `ids`, in tree order:
    `{"name": <Label>, "mat_ids": [<MAT_ID>, ...], "growth": <GrowthDistance>, "far": <far_size(item)>}`.
  - The callers set `job["air_grading"]` only when the list is non-empty.
- **Ruling (a deviation from spec 6.3):** a list with `mat_ids`, not a single `{"growth", "far"}` dict. A symmetric
  free job can hold an Air Region and a free object that is air, and the mesher must know which bodies are graded.

- [ ] **Step 1: Write the failing tests:**
  - `test_job_without_air_grading_has_no_air_grading_key` (passes already).
  - `test_air_grading_goes_to_the_job`:
    - a box and an Air Region;
    - an Air Grading with growth 50 and far 0, with an air whole-body Mesh Size of 12;
    - expect `job["air_grading"] == [{"name": "AirGrading", "mat_ids": [air MAT_ID], "growth": 50.0, "far": 12.0}]`.
  - `test_air_grading_on_a_sliding_air_lists_both_sides`: reuse the sliding set-up that the Stage 1 test
    `test_refine_near_limited_to_a_sliding_air_lists_both_sides` uses.
  - In `test_symmetric_study.py`, `test_air_grading_goes_to_the_free_job_of_its_air`: the entry sits on the fixed
    free job with the Air Region's MAT_ID; a grading on a free object sits on that object's side.

- [ ] **Step 2: Run** `pixi run -e addon pytest tests/freecad_addon/test_study.py tests/freecad_addon/test_symmetric_study.py -k air_grading -v`.
  Expected: the new-key tests FAIL with `KeyError: 'air_grading'`.

- [ ] **Step 3: Implement.**

- [ ] **Step 4: Run** both files and `test_air.py`. Expected: PASS.

- [ ] **Step 5: Commit** `FreeCAD add-on: write Air Grading to the mesh job`.

---

### Task 4: Air Grading fields in the 3D and 2D meshers

**Files:**
- Modify: `freecad_addon/emsolution/meshcommon.py`, adding `graded_air` and `apply_air_grading` after
  `apply_refinements`.
- Modify: `freecad_addon/emsolution/mesher.py` and `mesher2d.py` (`build`):
  - call `graded_air` on `by_size` before `apply_size_fields`;
  - call `apply_air_grading` after `apply_refinements`;
  - store the result as `job["air_grading_fields"]`.
- Test: `tests/freecad_addon/test_mesher.py`, `tests/freecad_addon/test_mesher2d.py`

**Interfaces:**
- Consumes: the `"air_grading"` entries of Task 3.
- Produces (meshcommon):
  - `graded_air(by_size, entries, body_tags, sizes, dim, same_body=()) -> dict`, for each entry:
    - Its MAT_IDs' top-dimension tags come out of `by_size` (they no longer get the air's size with
      `IncludeBoundary`).
    - Its inner boundary goes into `by_size[air size][dim - 1]`, where `air size = sizes[mat_id]`. The inner boundary
      is `real_boundary(dim, tags)` of the entry's tags joined, using `same_body` for the two sides of a sliding air.
    - Returns `{entry name: (tags, inner, outer)}`, where `outer` is the air's other (dim-1) boundary entities.
  - `apply_air_grading(entries, graded, sizes, dim) -> [(entry, extend field)]`, for each entry:
    - a `Constant` at `far` on the air's tags (`IncludeBoundary = 0`);
    - a `Constant` at `far` on `outer` (`IncludeBoundary = 1`);
    - an `Extend` listing the inner boundary: `SurfacesList` plus the inner faces' curves in `CurvesList` in 3D,
      `CurvesList` in 2D;
    - a `Restrict` of that `Extend` to the air's tags and `outer`, with `IncludeBoundary = 1`;
    - per distinct start size, a `Distance` on the meeting points → `Threshold` (`SizeMin` = that size,
      `SizeMax = far`, `DistMin = 0`, `DistMax = growth`, `StopAtDistMax = 1`), restricted to the outer curves:
      - the meeting points are the end points of outer curves that are not on the inner boundary, where they touch
        the inner boundary;
      - the start size of a point is the smallest size of the bodies whose boundary holds it, and the air's size;
      - `sizes` is `{mat_id: size}` of every body and air side in the job, the same map `graded_air` takes.
    - An entry with an empty inner boundary gets
      `_note(f"Air Grading {name}: the air touches no body; it is meshed at the far size")` and only the two
      Constants.
- Test helper: `air_grading(name="Grow", mat_ids=(...), growth=60.0, far=20.0)` builds an entry.
- Geometry for the tests:
  - **3D:** the spike's block (−10..10, −10..10, −5..5) at size 2 in the air box (−100..100)³ at size 20.
  - **2D:** the rectangle (−10..10, −5..5) in the square (−100..100)².
  - Measure the mean element edge in bands of distance from the block. The numbers in the comments are the spike's;
    assert loosely: "graded < 0.7 × today" in the 3–10 band, "> 0.6 × far" in the 50–80 band.

- [ ] **Step 1: Write the failing tests:**
  - `test_air_grading_grows_from_the_block` (3D): band 3–10 (spike: 4.86 graded against 9.20 today) and band 50–80
    (25.8).
  - `test_far_size_larger_than_the_air_size` (3D): far 40 gives fewer elements than today, and band 50–80 > 30.
  - `test_far_size_does_not_coarsen_the_body_surface` (Review Focus 1):
    - block size 30 in air size 20, far 40;
    - the block's surface triangles' mean edge is ≤ 22, i.e. the air's size wins over the block's 30, as today.
  - `test_air_face_on_the_domain_boundary_grades_3d` (Review Focus 2):
    - a half model, block (−10..10, −10..10, 0..5) in air (−100..100, −100..100, 0..100);
    - the air's triangles on z = 0 in band 3–10 have a mean edge < 0.7 × today's (spike 3.54 against 6.17).
  - `test_air_grading_grows_from_the_rectangle_2d`: as the 3D test, in 2D (spike 3.55 against 10.8).
  - `test_air_face_on_the_domain_boundary_grades_2d` (Review Focus 2):
    - rectangle (−10..10, 0..5) in (−100..100, 0..100);
    - the air's line elements on y = 0 in band 3–10 have a mean < 0.7 × today's (spike 3.22 against 8.61).
  - `test_sliding_divisions_unchanged_with_air_grading` (Review Focus 3):
    - take the 2D sliding job of the existing sliding tests (search `"sliding motion"` in `test_mesher2d.py`);
    - add an Air Grading on both air sides;
    - the node count on the sliding circle equals that of the run without it.
  - `test_air_grading_and_refine_near_on_the_air_both_apply` (Review Focus 4):
    - 2D, an Air Grading plus a Refine Near on one outer edge of the air box (fine 2, coarse 20, growth 30);
    - nodes within 5 of that edge are ≥ 3 × those of the Air Grading alone.
  - `test_air_grading_with_no_body_notes`: an air alone gets the note in stderr and return code 0.

- [ ] **Step 2: Run** `pixi run -e addon pytest tests/freecad_addon/test_mesher.py tests/freecad_addon/test_mesher2d.py -k air_grading -v`.
  Expected: FAIL on the size assertions.

- [ ] **Step 3: Implement** `graded_air` and `apply_air_grading`, and wire them into both `build`s.

- [ ] **Step 4: Run** both mesher test files in full. Expected: PASS, including every existing test (no key, no change).

- [ ] **Step 5: Commit** `FreeCAD add-on: Air Grading fields in the meshers`.

---

### Task 5: Air Grading inside mesh_region

**Files:**
- Modify: `freecad_addon/emsolution/meshfrozen.py` (`mesh_region`, `_region_3d`, `_region_2d`, `_size_field`)
- Test: `tests/freecad_addon/test_meshfrozen.py`

**Interfaces:**
- Produces `mesh_region(V, facets, outer, inners, size, dim, rules=(), grading=None)`.
  - `grading` is `{"growth": float, "far": float}` or None. With it:
    - the region's options set `Mesh.MeshSizeExtendFromBoundary = 0` and `Mesh.MeshSizeMax = far`, in place of the
      body's size;
    - an `Extend` lists every boundary surface of the region (3D: the discrete surfaces of all rings; 2D: every
      polygon line), with `DistMax = growth`, `SizeMax = far`, `Power = 1`;
    - it is joined with the rules' Thresholds by one `Min` as the background field.
  - Without `grading`, the code path and the mesh are as today.
- Test helper: build frozen facets as the spike did:
  - a gmsh surface mesh of the block (size 2) inside the box (size 20);
  - copy `frozen()` from the spike into the test module as `_two_shells(dim)`.

- [ ] **Step 1: Write the failing tests:**
  - `test_grading_none_is_unchanged`: same node and element counts as a call without the argument.
  - `test_grading_grows_from_the_frozen_boundary_3d`: growth 20 and far 20 give a band 3–10 mean edge > 1.2 × the
    ungraded (spike 6.85 against 5.27), and fewer elements (8.3k against 14.2k).
  - `test_grading_far_size_above_the_region_size_3d`: far 40 gives fewer elements than far 20.
  - `test_grading_grows_from_the_frozen_boundary_2d`: as 3D (spike 5.31 against 3.37).
  - `test_grading_with_rules`: a rule's points still refine near them (the mean edge within 1 of the points is < 0.6 ×
    the grading-only run).
  - The frozen nodes keep their positions in every test; the existing `FrozenError` check covers it.

- [ ] **Step 2: Run** `pixi run -e addon pytest tests/freecad_addon/test_meshfrozen.py -k grading -v`. Expected: FAIL.

- [ ] **Step 3: Implement.**

- [ ] **Step 4: Run** `test_meshfrozen.py` and `test_meshgroups.py`. Expected: PASS.

- [ ] **Step 5: Commit** `FreeCAD add-on: Air Grading inside the air around copies`.

---

### Task 6: Air Grading on the air around copies (free jobs)

**Files:**
- Modify: `freecad_addon/emsolution/meshgroups.py`:
  - `_carry_size_picks` also retargets `Extend` lists (`SurfacesList` at dim 2, `CurvesList` at dim 1);
  - `_rebuild` and `_open_lines` add the frozen lines to the gradings;
  - `mesh_free` and `_mesh_free_entity` pass `grading`.
- Test: `tests/freecad_addon/test_meshgroups.py`

**Interfaces:**
- Consumes:
  - Task 4: `built["air_grading_fields"]`, i.e. `[(entry, extend field)]`;
  - Task 5: `mesh_region(..., grading)`.
- Produces:
  - **The free model's surface mesh, `generate(dim - 1)`:**
    - The faces (2D: lines) that `_leave_room` puts under copies count as the air's inner boundary, so the faces
      beside them grow from the copies' frozen edges.
    - In 3D, the frozen polygon lines that `_rebuild` makes (`polygon`) are added to each grading's `Extend`
      `CurvesList`.
    - In 2D, the frozen pieces that `_open_lines` makes are added to the inner boundary of the point thresholds, and
      their end points become meeting points.
    - The far `Constant` on outer faces drops the faces that were replaced (`_carry_size_picks` already empties
      replaced lists; check it covers the Constant on `outer`).
  - **`_mesh_free_entity(survey, side, V, dim, rules=(), grading=None)`** passes
    `{"growth": e["growth"], "far": e["far"]}` to `mesh_region` when the body's MAT_ID is in an entry's `mat_ids`.
    `mesh_free` finds the entry from `free_job.get("air_grading", [])`.
- Tests (fixtures: `plate_in_air`, `air_entry`, `sector_group`, `air_2d`, `mean_edge`; see the Stage 2 tests near
  line 1130):
  - `test_air_grading_grades_the_air_around_copies_3d` (Review Focus 5):
    - the ring of copies with the air BOX at size 6 (`air_entry(..., size=6.0)`);
    - an Air Grading on MAT_ID 30 with far 12 and growth 10;
    - expect fewer air elements than without the grading;
    - expect a mean edge within 2 mm of the copies below 0.6 × far;
    - measure both and put the numbers in the comments, as Stage 2 did.
  - `test_air_grading_grades_the_air_around_copies_2d`: the same with `sector_group` and `air_2d`.
  - `test_air_face_beside_a_copy_grades_3d` (Review Focus 5):
    - the air's surface triangles within 2 mm of the copies' frozen edges have a mean edge < 0.6 × far;
    - this must fail before the frozen lines are added to the `Extend`. Show that in the report.
  - `test_no_air_grading_free_job_unchanged`: the same element counts as before for a free job with no key.

- [ ] **Step 1: Write the failing tests.**
- [ ] **Step 2: Run** `pixi run -e addon pytest tests/freecad_addon/test_meshgroups.py -k air_grading -v`. Expected: FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `test_meshgroups.py`, `test_meshfrozen.py`, `test_symmetric_study.py` and
  `test_symmetric_study3d.py`. Expected: PASS.
- [ ] **Step 5: Commit** `FreeCAD add-on: Air Grading on the air around copies`.

---

### Task 7: Command, panel, labels and icon

**Files:**
- Create: `freecad_addon/icons/airgrading.svg`
- Modify:
  - `freecad_addon/emsolution/commands.py`: `AddAirGrading`, `REFINEMENTS`, the dropdown tooltip, `COMMANDS`,
    `context_names`;
  - `freecad_addon/emsolution/taskpanels.py`: an `ITEM_PICKS` entry and the Air Grading rows in `ItemPanel`;
  - `freecad_addon/emsolution/labels.py`: `KINDS`, `tag_text`, `description`;
  - `tests/freecad_addon/gui_smoke.py`.

**Interfaces:**
- Consumes: Task 1 (`make_air_grading`, `far_size`, `whole_body_size`) and Task 2's messages.
- Produces:
  - **Command `EMS_AirGrading`:**
    - MenuText `"Air Grading"`, ToolTip `"Grow the air's element size from the bodies' surface sizes to a far size"`,
      icon `airgrading`.
    - Activated: `refs = objects.to_cells(study, taskpanels.selected_mesh_refs())`. With no refs it takes the Study's
      Air Region (`make_air_grading(study)`); otherwise `gate(study, [b for b, _ in refs])` and
      `make_air_grading(study, refs)`, through `_create_and_edit(study, "Add Air Grading", ...)`.
  - `REFINEMENTS = ("EMS_RefineNear", "EMS_AirGrading")`; the dropdown ToolTip is `"Refine Near or Air Grading"`.
  - `context_names`:
    - `"Air"` gives `["EMS_Material", "EMS_MeshSize", "EMS_RefineNear", "EMS_AirGrading"]`;
    - other picks gain nothing (a free body as air is picked through the panel or the command).
  - **`ITEM_PICKS[objects.AirGrading]`:**
    - picks whole bodies and the Air Region from the selection (`objects.pick_body`);
    - list label `"Air"`, gate kinds `("Body",)`, whole `True`, air allowed;
    - hint `"Select the Air Region in the tree (or, in a Study with Symmetric Groups, a free object that is air)."`
      for both dimensions;
    - the panel's `air =` test includes `objects.AirGrading`.
  - **Panel rows after Name:**
    - "Growth distance" (`_length_box`);
    - "Far size" (`_length_box(minimum=0.0)`), with a label beside it: `f"0 = the air's size ({size:g} mm)"`, where
      `size` is `objects.whole_body_size` of the first pick (or the Study's Air Region), recomputed when the picks
      change.
    - `accept` writes both; `unsaved()` reports `GrowthDistance` and `FarSize`.
  - **Labels:**
    - `KINDS["AirGrading"] = ("#1864ab", "G", "Air grading")`;
    - `tag_text` gives `f"→ {far:g} mm over {growth:g}"`, using the far size resolved as in `far_size` with the
      panel's unsaved values;
    - `description` gives `f"Air grading: {tag_text}"`.
  - **Icon:** 64 × 64 SVG in the style of `refinenear.svg` / `meshsize.svg` (meshed square `#a9dca1`/`#1e6b2c`, badge
    bottom right). The mesh cells grow larger from a small body at one side to the far side.

- [ ] **Step 1: Update the smoke test first:**
  - the expected `context_menu()` lists for an Air Region pick gain `"EMS_AirGrading"`;
  - add a step: with nothing selected, `Gui.runCommand("EMS_AirGrading")`, set growth 30 and far 0, accept;
  - assert `objects.air_gradings(study)[0].GrowthDistance.Value == 30` and that its reference is the Air Region;
  - assert Validate shows no Air Grading error.
- [ ] **Step 2: Run the smoke test** (PowerShell): `pixi run -e addon freecad tests\freecad_addon\gui_smoke.py`, then
  `Get-Content "$env:TEMP\ems_gui_smoke.txt" -Tail 3`. Expected: `FAIL`.
- [ ] **Step 3: Implement** the command, menu and context entries, the panel rows, the labels and the icon. Render the
  icon with Qt beside `refinenear.svg` and look at it.
- [ ] **Step 4: Run** the smoke test (`PASS`), `pixi run -e addon test-addon` (all pass) and `pixi run lint` (clean).
- [ ] **Step 5: Commit** `FreeCAD add-on: Air Grading command, panel and icon`.

---

### Task 8: The Stage 3 review catalogue rows

**Files:**
- Modify: `experiments/refinement_catalogue/rows.py` (the rows) and `build_catalogue.py` (the "today" copy also
  deletes `objects.air_gradings(study)`).

**Interfaces:**
- Consumes: the whole add-on, and the Stage 1/2 helpers in `rows.py` (`study_of`, `done`, `magnet_2d`, `block`, `motor`,
  `cell`, `rns6`'s structured band).
- Rows (spec 9, Stage 3). Sizes are mm. Each row is a set-up with a large air and a small body size, so the grading is
  visible:

| id | Study | Air Grading | after-check |
|---|---|---|---|
| AG-01 | 2D: the RN-01 magnet in a Padding Air Region of 200 × 200, air size 20, magnet 2 | growth 60, far 0 | air elements today vs new printed |
| AG-02 | 3D: magnet block 40 × 20 × 10 in an Air Region box of 300, air size 30, magnet 3 | growth 80, far 0 | — |
| AG-03 | AG-01 with far 60 | far override | air elements fewer than today |
| AG-04 | the RN-08 sliding 2D Study (structured gap), air size 10 | growth 30 | nodes on the sliding circle equal in new and today (reuse `rn08_after`) |
| AG-05a/b | AG-01 with a second Air Grading / with the Air Grading on the magnet | refused: Task 2 messages | — |
| AG-S1 | 2D symmetric: the RN-S1 motor cell in an Air Region with free air around the copies, air size 10 | growth 30, far 0 | air elements and the band near copies printed |
| AG-S2 | 3D symmetric: the RN-S4 cell, Air Region box around the copies, air size 8 | growth 25, far 0 | — |

- [ ] **Step 1: Add the rows.** Run
  `pixi run -e addon python experiments/refinement_catalogue/build_catalogue.py --only AG-01 AG-02 AG-03 AG-04 AG-05a AG-05b AG-S1 AG-S2`.
  Expected: all `match: true`.
- [ ] **Step 2: Look at every new picture** and fix the rows whose picture does not show the grading (zoom, clip).
  Re-run with `--only`.
- [ ] **Step 3: Run the whole catalogue.** Expected: every row (RN, RN-S, AG) matches, exit code 0.
- [ ] **Step 4: Commit** `Refinement catalogue: Stage 3 rows (Air Grading)`.

---

### Task 9: Stage 3 check and hand-over

- [ ] **Step 1: Run** `pixi run -e addon test-addon` (all pass), `pixi run lint` (clean), and the GUI smoke test
  (`PASS`).
- [ ] **Step 2: Hand over** `C:\Users\hamed\Desktop\delme\refinement_studies\catalogue.html`, the same as Stages 1
  and 2.
- [ ] **Step 3: Stop.** Stage 4 (Skin Layer) starts only after the user has reviewed the AG rows. Don't merge or push.
