# Mesh refinements, Stage 2: Refine Near in symmetric Studies — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refine Near meshes in Studies with Symmetric Groups, 2D and 3D, on cell objects (inside the cell, copied with
it) and on free objects and the Air Region (graded into the free volumes meshed around the frozen copies), plus the
Stage 2 review catalogue rows RN-S1..RN-S6.

**Architecture:** The jobwriter gives each group's cell job and each free job the `"refine"` entries whose picks lie on
its bodies, so the existing `build` fields (Stage 1) apply in both. Three mesher additions make that correct in
symmetric jobs: (1) the cell's refinements also measure from the periodic partner of a picked seam; (2) face
replacement in the free model (`_rebuild`, `_open_lines`) retargets refinement fields like Mesh Size fields, and
`Restrict` lists the limit bodies' faces so it survives the removal of their volumes; (3) `meshfrozen.mesh_region`
takes size rules (`Distance` on the picked entities' mesh nodes → `Threshold`), chosen by the 7.3 spike, so the free
volumes and the air around copies grade as asked.

**Tech Stack:** FreeCAD 1.1 add-on (Python 3.11), gmsh 4.15.2 Python API, numpy, pytest via pixi.

**Spec:** `docs/superpowers/specs/2026-11-14-mesh-refinements-design.md`, sections 6.3, 6.4, 7 (with the 7.3 spike
result), 9 (Stage 2 rows), 10. Read it first; this plan argues from it. Stage 1's code is on the branch: read
`meshcommon.apply_refinements`, `jobwriter.refine_entries` and the Refine Near checks in `validation.py` before
changing them.

## Global Constraints

- Run everything through pixi: `pixi run -e addon test-addon`, `pixi run -e addon pytest tests/freecad_addon/<file> -k <name>`,
  `pixi run lint`, `pixi run format` (it also reformats the unrelated `highlight.py`: revert that file). Never `pip install`.
- Branch `freecad/mesh-refinements` (Stage 1 is on it); commit per task; never `--no-verify`.
- Ruff, line length 120, double quotes; no trailing commas on constructs that fit on one line; never reorder imports;
  format only files you changed.
- Mesher modules (`meshcommon.py`, `mesher.py`, `mesher2d.py`, `meshgroups.py`, `meshfrozen.py`, `meshsym.py`) never
  import FreeCAD and import each other by bare module name. `objects.py`, `jobwriter.py`, `validation.py` stay GUI-free.
- Every Threshold uses `StopAtDistMax = 1`. A job without `"refine"` entries meshes exactly as before (same element
  and node counts); a symmetric job without them likewise.
- Cell items never reach the air or free objects around the copies (spec 7.1, user's decision): a cell job holds only
  its cells' picks; the free volumes get rules only from free jobs' entries.
- Transfinite settings win: the sliding interface's divisions and structured air gaps keep their node counts.
- Messages follow `validation.py`'s house style: `Refine Near {label}: ...` ending with a full stop.
- Units are mm.

## Review Focus

1. A Refine Near picked on a seam face (curve in 2D) that gmsh makes the periodic *copy* (slave): without the partner
   the seam is meshed coarse from its master → Task 3 test `test_refine_on_either_seam_refines_both`.
2. A free face picked for refinement that lies partly under copies, so `_rebuild` replaces it → Task 2 test
   `test_carry_retargets_refinement_fields`.
3. Limit to a free body whose volume `_rebuild` removes: its faces must stay refined → Task 2 test
   `test_restrict_keeps_faces_when_volumes_go`.
4. The sample points added to the `mesh_region` model must not come back as nodes no element uses → Task 4 test
   `test_rules_leave_no_unused_nodes`.
5. One item with picks on a cell object and on a free body: both jobs get an entry and their BREP files don't
   collide → Task 1 test `test_refine_near_on_a_cell_and_a_free_body_goes_to_both_jobs`.

---

### Task 1: Refine Near in symmetric jobs and validation

**Files:**
- Modify: `freecad_addon/emsolution/jobwriter.py` (`refine_entries`, `_group_entry`, `write_groups`)
- Modify: `freecad_addon/emsolution/validation.py` (the Refine Near loop, ~line 245)
- Test: `tests/freecad_addon/test_symmetric_study.py` (replace `test_refine_near_is_refused_with_symmetric_groups`)

**Interfaces:**
- Consumes: `objects.make_refine_near(study, refs, fine=None, coarse=None, growth=None, fine_distance=0.0, limit_to=())`,
  `objects.refine_items`, `objects.cell_bodies(study)`, `objects.symmetric_groups(study)`, `sides.moving(study)`,
  `symcases.add_free`, `symcases.add_air_region`.
- Produces:
  - `refine_entries(study, folder, ids, prefix="")`: as today, files named `geometry/{prefix}refine_<k>_<j>_<n>.brep`.
  - Cell job `symmetric["groups"][g]["job"]["refine"]` (only when non-empty): picks on that group's cells, `whole` and
    `limit_to` in the cell job's local ids (`ids = {cell.Name: [n]}`), prefix `g{number}_`.
  - Free job `symmetric["free"][s]["job"]["refine"]`: picks on that side's free bodies and (fixed side) the Air Region,
    MAT_IDs as the free job uses them, prefix `free_{side}_`.
  - New warning (exact text): `Refine Near {label}: {name} in Limit to is meshed apart from its picks (a Symmetric Group's cell objects are meshed on their own); it has no effect there.`
    When no meshed Limit to body shares a part with any pick: `Refine Near {label}: no body in Limit to is meshed with its picks; the refinement is skipped.`
    A "part" is: the group, for a cell object of that group; `free fixed` / `free moving` for a free body by its side;
    `free fixed` for the Air Region.

- [ ] **Step 1: Write the failing tests** in `test_symmetric_study.py`, on the `motor` fixture (add a free body with
  `symcases.add_free` where a test needs one):
  - `test_refine_near_on_a_cell_goes_to_the_cell_job`: a whole-body pick on a stator cell → `Validate` has no error;
    `groups[0]["job"]["refine"][0]["whole"] == [<that cell's local id>]`, no `"refine"` in the free jobs.
  - `test_refine_near_on_a_free_body_goes_to_the_free_job`: a face pick on a free body → the fixed free job's entry has
    one file starting `geometry/free_fixed_refine_`, no `"refine"` in any cell job.
  - `test_refine_near_on_a_cell_and_a_free_body_goes_to_both_jobs`: one item picking both → one entry in each job, and
    all file names in the job are distinct.
  - `test_refine_near_limit_to_across_parts_warns`: picks on a cell, Limit to the Air Region → the "no body in Limit to
    is meshed with its picks" warning, and no job has a `"refine"` key.
  - `test_refine_near_limit_to_partly_across_parts_warns`: picks on a cell, Limit to that cell and the Air Region →
    the "meshed apart from its picks" warning naming the air, and the cell job's entry has `limit_to == [<cell id>]`.

- [ ] **Step 2: Run** `pixi run -e addon pytest tests/freecad_addon/test_symmetric_study.py -k refine_near` — Expected: FAIL
  (the Stage 1 refusal).

- [ ] **Step 3: Implement.** Remove the Stage 1 refusal. Add the `prefix` parameter. Call `refine_entries` from
  `_group_entry` and from `write_groups` after `_body_job`, writing `"refine"` only when non-empty. In `validation.py`
  compute each body's part (helper `_mesh_part(study, body)`, GUI-free) and add the two warnings beside the Stage 1
  "not meshed by the Study" ones; a body counted there is not also counted here.

- [ ] **Step 4: Run** the tests above plus `pixi run -e addon pytest tests/freecad_addon/test_study.py -k refine` — Expected: PASS.

- [ ] **Step 5: Commit** `FreeCAD add-on: Refine Near in symmetric Studies writes cell and free jobs`.

---

### Task 2: Refinement fields survive the free model's face replacement

**Files:**
- Modify: `freecad_addon/emsolution/meshcommon.py` (`apply_refinements`), `mesher.py`, `mesher2d.py`,
  `freecad_addon/emsolution/meshgroups.py` (`_carry_size_picks`)
- Test: `tests/freecad_addon/test_meshgroups.py` (in-process gmsh, like the existing in-process uses of `meshgroups`)

**Interfaces:**
- Produces:
  - `apply_refinements(items, body_tags, dim, same_body=())` returns `[(entry, distance_field)]`, one per field made.
  - `build` (3D and 2D) stores that list in `job["refine_fields"]` (the caller's job dict, as it stores `"unwritten"`).
  - `Restrict` of a Limit to lists the limit bodies' volumes (faces in 2D) **and** their boundary entities of dimension
    `dim - 1` explicitly (still `IncludeBoundary = 1`).
  - `_carry_size_picks(replaced, dim)` retargets the entity lists of dimension `dim` in `Constant`, `Distance` and
    `Restrict` fields (`replaced = {old: [new, ...]}`, `[]` drops the entity).

- [ ] **Step 1: Write the failing tests:**
  - `test_carry_retargets_refinement_fields`: a box model with a `Distance` on face 1 and a `Restrict` on volume 1 and
    face 1; `_carry_size_picks({1: [7, 8]}, 2)` → Distance `SurfacesList == [7, 8]`, Restrict `SurfacesList` holds 7
    and 8 and not 1.
  - `test_restrict_keeps_faces_when_volumes_go`: `apply_refinements` with `limit_to` a box volume → the Restrict lists
    the box's six faces; after `_carry_size_picks({vol: []}, 3)` its `VolumesList` is empty and the faces are still
    listed.
  - `test_apply_refinements_returns_its_distance_fields`: two entries → two `(entry, field)` pairs, each field of type
    `Distance`.
- [ ] **Step 2: Run** `pixi run -e addon pytest tests/freecad_addon/test_meshgroups.py -k "carry or restrict_keeps or returns_its"` — Expected: FAIL.
- [ ] **Step 3: Implement** the three changes above.
- [ ] **Step 4: Run** those tests and `pixi run -e addon pytest tests/freecad_addon/test_mesher.py tests/freecad_addon/test_mesher2d.py -k "refine or limit or size"` — Expected: PASS (Stage 1 behaviour unchanged).
- [ ] **Step 5: Commit** `FreeCAD add-on: refinement fields follow replaced faces and keep their limit faces`.

---

### Task 3: Cell refinements measure from both sides of a periodic seam

**Files:**
- Modify: `freecad_addon/emsolution/meshgroups.py` (`mesh_cell`, new `_refine_partners(dim)`)
- Test: `tests/freecad_addon/test_meshgroups.py` (`GroupJobTest`)

**Interfaces:**
- Consumes: the Distance fields of the cell model (every `Distance` field in a cell model is a refinement's).
- Produces: `_refine_partners(dim)`: for every `Distance` field and every list dimension `d < dim`, adds to the list
  each listed entity's periodic master (`gmsh.model.mesh.getPeriodic(d, [tag])`) and every entity whose master is a
  listed one. Called in `mesh_cell` right after `meshsym._periodic(...)` and before `pair_images`.

- [ ] **Step 1: Write the failing tests** (2D, `sector_group((10, 20, 0, 30), self.TWELVE, self.IRON)` with a
  `"refine"` entry in its job: `files` one BREP line written with `write_line`, fine 0.25, coarse 2, growth 3):
  - `test_refine_on_either_seam_refines_both`: run once with the line on the 0° seam, once on the 30° seam. In both
    meshes the nodes on the 0° and the 30° seam of the cell (r 10..20) are at least `10 / 0.25 * 0.8 = 32` each.
  - `test_refine_in_a_cell_stays_in_the_cell`: a 2D group with a free air (`self.air_2d`) and a refine entry in the cell
    job only → the air's element count equals that of the same job without the entry.
- [ ] **Step 2: Run** `pixi run -e addon pytest tests/freecad_addon/test_meshgroups.py -k "either_seam or stays_in_the_cell"` — Expected: the seam test FAILs for the seam gmsh makes the copy.
- [ ] **Step 3: Implement** `_refine_partners` and the call.
- [ ] **Step 4: Run** the two tests and `pixi run -e addon pytest tests/freecad_addon/test_meshgroups.py tests/freecad_addon/test_meshsym.py` — Expected: PASS.
- [ ] **Step 5: Commit** `FreeCAD add-on: a refinement on a periodic seam refines its partner`.

---

### Task 4: Size rules in mesh_region

**Files:**
- Modify: `freecad_addon/emsolution/meshfrozen.py` (`mesh_region`, `_region_3d`, `_region_2d`)
- Test: `tests/freecad_addon/test_meshfrozen.py`

**Interfaces:**
- Produces: `mesh_region(V, facets, outer, inners, size, dim, rules=())`. A rule is
  `{"points": ndarray (n, 3), "fine", "fine_distance", "coarse", "growth"}`. Per rule with points: model points at the
  points (geo in 3D, occ in 2D, in the region model) → `Distance` (`PointsList`) → `Threshold` (`SizeMin` fine,
  `SizeMax` coarse, `DistMin` fine_distance, `DistMax` fine_distance + growth, `StopAtDistMax = 1`); several rules
  joined by a `Min`; set as the background field. Rules with no points are skipped. The returned V2 holds only the
  nodes the returned elements use (frozen nodes keep their numbers; the new ones are numbered after `len(V)` in tag
  order, as today).

- [ ] **Step 1: Write the failing tests** (a closed triangulated cube shell of side 4, surface size 0.5, meshed with
  `size = 0.5`):
  - `test_rule_grades_from_its_points`: a rule with points on one corner (all shell nodes within 0.5 of (0, 0, 0)),
    fine 0.1, coarse 0.5, growth 2 → mean tet edge within 0.5 of the corner < 0.6 × that without the rule, and mean tet
    edge farther than 3 from it within 10 % of the run without the rule.
  - `test_rules_leave_no_unused_nodes`: with the rule, every node index `>= len(V)` of V2 is used by an element.
  - `test_no_rules_mesh_unchanged`: `rules=()` gives the same element counts and V2 as before the change (compare with a
    call without the `rules` argument).
  - `test_rule_without_points_is_ignored`: a rule with `points` of shape (0, 3) gives the mesh of no rules.
  - `test_rule_grades_from_its_points_2d`: the same idea on a square polygon of side 4 (`dim = 2`).
- [ ] **Step 2: Run** `pixi run -e addon pytest tests/freecad_addon/test_meshfrozen.py -k rule` — Expected: FAIL (`rules` unknown).
- [ ] **Step 3: Implement.** Keep the frozen-node checks as they are.
- [ ] **Step 4: Run** `pixi run -e addon pytest tests/freecad_addon/test_meshfrozen.py` — Expected: PASS.
- [ ] **Step 5: Commit** `FreeCAD add-on: mesh_region takes refinement size rules`.

---

### Task 5: Free regions grade from free refinements

**Files:**
- Modify: `freecad_addon/emsolution/meshgroups.py` (`mesh_free`, `_mesh_free_entity`, new `_free_rules(built, dim)`)
- Test: `tests/freecad_addon/test_meshgroups.py` (`GroupJobTest`)

**Interfaces:**
- Consumes: `built["refine_fields"]` (Task 2), `mesh_region(..., rules)` (Task 4).
- Produces: `_free_rules(built, dim) -> [(entry, points)]`, called after `generate(settings, dim - 1)`: for each
  `(entry, distance)` the entities now in the Distance field's lists (after any carry), and the unique coordinates of
  their mesh nodes (`gmsh.model.mesh.getNodes(d, tag, includeBoundary=True)`). `_mesh_free_entity(survey, side, V,
  dim, rules=())` passes to `mesh_region` the rules whose `entry["limit_to"]` is empty or holds the body's MAT_ID.

- [ ] **Step 1: Write the failing tests:**
  - `test_free_refinement_grades_the_air_3d`: a 3D group of copies, a free plate body and the air (follow
    `test_plate_shares_nodes_with_two_copies_of_the_bar` and `air_3d`); a `"refine"` entry in the free job, whole pick on
    the plate, fine 0.25, coarse = the air's size, growth 6. Assert in the air: the mean tet edge in the band
    2..4 mm from the plate is below a bound you measure, and the test fails when run with
    `patch="meshgroups._free_rules = lambda built, dim: []"`.
  - `test_free_refinement_grades_the_air_2d`: the same in 2D with a curve pick on the air's outer boundary (fine 0.5,
    coarse 4, growth 20, the air 6). The same patch makes it fail.
  - `test_free_refinement_limited_to_the_plate_leaves_the_air`: Limit to the plate → the air's element count is within
    5 % of the count without the entry.
  - `test_free_pick_under_copies_meshes`: the picked free face lies wholly under a copy (its carry leaves no entities)
    → the job meshes, exit code 0.
- [ ] **Step 2: Run** `pixi run -e addon pytest tests/freecad_addon/test_meshgroups.py -k free_refinement` — Expected: FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `pixi run -e addon pytest tests/freecad_addon/test_meshgroups.py tests/freecad_addon/test_symmetric_study.py tests/freecad_addon/test_symmetric_study3d.py` — Expected: PASS.
- [ ] **Step 5: Commit** `FreeCAD add-on: free objects' refinements grade the free volumes and the air around copies`.

---

### Task 6: The Stage 2 review catalogue rows

**Files:**
- Modify: `experiments/refinement_catalogue/rows.py` (new rows), `build_catalogue.py` / `make_page.py` only if a row
  needs it.

**Interfaces:**
- Consumes: the Stage 1 catalogue (`CASES`, `--only`, `after(folder)` checks, `results.json`, `catalogue.html`), the
  symmetric Study builders in `tests/freecad_addon/symcases.py` (`motor_study`, `motor_study_3d`, `group`, `add_free`,
  `add_air_region`, `transfinite_layer`).
- Rows (spec 9, Stage 2). "today" deletes the Refine Near items as in Stage 1. Sizes in mm:

| id | Study | Refine Near |
|---|---|---|
| RN-S1 | 2D motor (`symcases.motor_study`) | the magnet's corners on the rotor cell (vertices), fine 0.3, coarse 2, growth 4 |
| RN-S2 | RN-S1's model | a tooth-tip edge picked on a **copy** in the drawing (mapped by `to_cells`); the check: the job's entry is on the cell |
| RN-S3 | 2D sector cell with periodic seams | a seam edge, fine 0.3, coarse 2, growth 3; the check: both seams of the cell have equal node counts, more than today |
| RN-S4 | 3D motor (`motor_study_3d`) | a magnet face on the rotor cell, fine 0.5, coarse 3, growth 5; cut through the magnet |
| RN-S5 | 2D motor plus a free body in the air (e.g. a sensor block outside the stator) | the free body (whole), fine 0.3, coarse = the air's size, growth 10; the air around it grades |
| RN-S6 | 2D sliding symmetric motor with a structured gap (`transfinite_layer`, as in the sliding symmetric tests) | the stator teeth tips, fine 0.3, coarse 2, growth 3; the check: nodes on the sliding circle equal in new and today |

- [ ] **Step 1: Write the rows** (and their `after` checks).
- [ ] **Step 2: Run** `pixi run -e addon python experiments/refinement_catalogue/build_catalogue.py --only RN-S1 RN-S2 RN-S3 RN-S4 RN-S5 RN-S6`, then the whole catalogue — Expected: every row `match: true`, exit 0.
- [ ] **Step 3: Look at every new picture** and fix rows whose picture does not show the refinement (cut, zoom).
- [ ] **Step 4: Commit** `Refinement catalogue: Stage 2 rows (Refine Near in symmetric Studies)`.

---

### Task 7: Stage 2 check and hand-over

- [ ] **Step 1: Run** `pixi run -e addon test-addon` (all pass) and `pixi run lint` (clean). No GUI file changes, so no
  smoke test, unless a task touched one (then run it from PowerShell).
- [ ] **Step 2: Hand over** `C:\Users\hamed\Desktop\delme\refinement_studies\catalogue.html` (the RN-S rows) and the row
  folders.
- [ ] **Step 3: Stop.** Stage 3 (Air Grading) starts only after the user has reviewed the RN-S rows. Don't merge.
