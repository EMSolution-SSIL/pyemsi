# Air Region and Sliding Interface Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Studies get an automatic air region and, for sliding motion, sliding interfaces whose two sides are meshed with matching nodes and written to `pre_geom(2D)` and `rotor_mesh(2D)`; a script builds example models for checking by hand.

**Architecture:** FreeCAD-side items (`AirRegion`, `SlidingInterface`) hold only outer shapes and settings; `airshapes.py` builds their shapes and splits the air into cells. The job file carries the air, the slide surfaces, the moving air cells and the period; the Gmsh scripts fragment everything, give overlapping pieces to bodies, make slide surfaces transfinite, link periodic boundaries, and write one or two mesh files.

**Tech Stack:** FreeCAD 1.1 (Part, BOPTools), Gmsh Python API, PySide, pytest via pixi.

**Spec:** `docs/superpowers/specs/2026-10-20-air-region-and-sliding-design.md`

## Global Constraints

- Run everything through pixi: `pixi run pytest tests/freecad_addon/...`, `pixi run lint`, `pixi run format` (only files you changed).
- Ruff, line length 120, double quotes. Never reorder imports. No new lint rules.
- `mesher.py`, `mesher2d.py`, `meshcommon.py` never import FreeCAD. `objects.py`, `geometry.py`, `airshapes.py`, `validation.py` have no GUI code; GUI lives in `commands.py` and `taskpanels.py`.
- GUI changes also need `pixi run freecad tests\freecad_addon\gui_smoke.py`; last line of `%TEMP%\ems_gui_smoke.txt` must be `PASS`.
- Air always has the lowest priority; two overlapping solid bodies stay an error.
- Scope: static and slide motion (`MOTION` = 2) only. No deform, no `MOTION` = 1, no motion in a ZX Study.
- One Air Region per Study.
- Rotation is about the global Z axis only. Slide point / slide edge goes into the rotor file only, at the start angle or start position, with its own `SLIDE_MAT_ID`.
- Both sides of a slide surface get the same uniform division; `Divisions` = `SLIDE_NDIV` (over the meshed period).
- Periodic boundaries have matching nodes in every file (Gmsh `setPeriodic`).
- Each written mesh file numbers its nodes from 1; slide nodes appear in both files.
- Example output default folder: `C:\Users\hamed\Desktop\delme\air_examples` (outside the repo; argument overrides it).
- Commit messages end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Never `--no-verify`.

## Decisions this plan adds to the spec

These fill gaps the spec leaves open; the reviewer should check them against the spec.

1. **Side of the air is decided by cells, not by touching (refines decision 9).** The interfaces cut the Air Region into cells (`airshapes.cells`). A cell holding Moving bodies is moving, one holding fixed bodies is fixed. The mesher gets the moving cells as BREPs, fragments them with the rest, and every air piece inside a moving cell is moving air. An enclosed air pocket therefore follows its cell, and the "touching neither" case becomes "a cell with no bodies" (error).
2. **A full 360° interface is built in two halves** (split at 0° and 180°), so every slide curve/face has 2 ends/4 corners for transfinite meshing. `Divisions` must be even for a full revolution.
3. **Padding is a one-shot fit.** The Box panel has "Fit to bodies" with a padding %; it sets centre and sizes once. A body later outside the air is caught by validation.
4. **No separate axis check (spec section 4, E3).** Rotational interfaces are always built about the global Z axis, so a machine on another axis shows up as "crosses the Sliding Interface"; that message adds "Rotation is about the global Z axis; put the machine axis on Z." The "whole number of divisions" check holds by construction, because `Divisions` is defined over the period.
5. **Air material and size.** One Material assignment on the Air Region covers both sides. Air size = the Study default, or a Mesh Size item that references the whole Air Region. Air cannot be recombined or structured in this step.
6. **Periods.** A Sector Air Region with angle < 360° is always periodic (rotation about Z by its angle). A Box Air Region with a Linear interface is periodic along the motion axis by its length. Otherwise no periodic linking.
7. **Linear interfaces need a Box Air Region**, so the period length is defined.
8. **Units in the report.** Meshes are in mm (`UNIT` = 1); the printed `DXYZ` is in m, as the handbook gives it.

## Review Focus

1. A body exactly on the slide surface (rotor iron outer radius = interface radius): it must be accepted (not "crosses"), and the slide nodes must still match.
2. A Study saved before this change (no `AirRegionsGroup`): opening it must add the folder and keep every ID.
3. Renaming or deleting the Air Region after Run Mesh: IDs for `#fixed`/`#moving` keys must survive a rename and not be reused after delete.
4. A full-circle 2D interface where Gmsh's fragment adds extra points on the circle (a body vertex on it): the halves split further; division must be shared out (`_share`) and the node count stay `Divisions`.
5. Periodic linking when the user's geometry is not periodic (a body cut at 0° but not at 45°): one clear error naming the place, not a Gmsh crash.

Each line has its test in the owning task (Tasks 1, 2, 9, 9, 9).

---

## Part A: Static air

### Task 1: Air Region item and its shapes

**Files:**
- Create: `freecad_addon/emsolution/airshapes.py`
- Modify: `freecad_addon/emsolution/objects.py` (new `AirRegionsFolder`, `AirRegion`, `FOLDERS`, `Study.onDocumentRestored`, `make_air_region`, `air_regions`)
- Test: `tests/freecad_addon/test_air.py` (new; same setUp as `StudyTest`: new doc, Study in Manual mode, saved to a temp folder)

**Interfaces:**
- Produces:
  - `objects.AirRegionsFolder(Folder)`, `LABEL = "Air Regions"`; `FOLDERS` gains `("AirRegionsGroup", AirRegionsFolder)` (last).
  - `objects.AirRegion(_Named)` on `Part::FeaturePython`, properties in group `"Air"`: `AirShape` enum `["Box", "Sector", "Custom"]`; `Center` (`App::PropertyVector`, default origin); `Length`, `Width`, `Height` (`App::PropertyLength`, 100 mm each); `InnerRadius` (0), `OuterRadius` (100) (`App::PropertyLength`); `StartAngle` (0), `EndAngle` (360) (`App::PropertyAngle`); `ZMin` (`App::PropertyDistance`, -50 mm; bottom of a 3D sector); `Source` (`App::PropertyLinkGlobal`). `execute(obj)` sets `obj.Shape = airshapes.air_shape(obj, airshapes.study_plane(owner_study(obj)))`.
  - `objects.make_air_region(study, shape="Box", **props) -> obj` (Label "Air", sets props, adds to `AirRegionsGroup`, attaches `taskpanels.ViewProviderAir` when GUI runs — Task 5 defines it; until then guard with `hasattr`).
  - `objects.air_regions(study) -> list`.
  - `objects.ensure_folders(study)`: adds any folder in `FOLDERS` the Study lacks; called from `Study.onDocumentRestored`.
  - `airshapes.study_plane(study) -> str`: `"3D"` for a 3D Study; for 2D the plane of the first main body face (`geometry.plane_of`), default `"XY"`.
  - `airshapes.air_shape(air, plane) -> Part.Shape`: 3D a solid; XY a face in z = 0; ZX a face in y = 0.
    - Box: 3D box centred on `Center` with `Length` (x), `Width` (y), `Height` (z). XY rectangle `Length` × `Width`. ZX rectangle `Length` (x) × `Width` (z).
    - Sector: ring sector about the Z axis from `StartAngle` to `EndAngle`, radii `InnerRadius`–`OuterRadius`; 3D extruded from `ZMin` by `Height`. In ZX: half disc / half ring centred on (0, 0, `Center.z`), x ≥ 0 (angles ignored).
    - Custom: `geometry.global_shape(Source)`; `Source` None raises `ValueError("Air Region <Label>: choose a body for the Custom shape")`.
  - `airshapes.fit_box(bodies, padding, plane) -> (App.Vector, float, float, float)`: centre, length, width, height of the bodies' global bound box grown by `padding` % on each side (2D: height 0).

- [ ] **Step 1: Write the failing tests** in `test_air.py`:
  - `test_new_study_has_air_regions_folder`: `make_study` → `study.AirRegionsGroup.Label == "Air Regions"`.
  - `test_restored_old_study_gets_air_folder_and_keeps_ids`: make study + box + `update_ids`; delete `AirRegionsGroup` object and its property (simulates an old file); save, close, reopen; assert folder exists and `MatIds` unchanged.
  - `test_box_air_3d_is_centred_solid`: `make_air_region(study, "Box", Center=App.Vector(5,0,0), Length=20, Width=10, Height=4)`; recompute; `obj.Shape.Volume == pytest.approx(800)`, bound box XMin 15−20/2… (assert XMin == -5, XMax == 15).
  - `test_sector_air_2d_xy_quarter_ring_area`: 2D Study with one face body in z = 0; Sector inner 10, outer 20, 0–90°; area `== approx(pi*(400-100)/4)`; all vertices z == 0.
  - `test_sector_air_zx_is_half_disc_on_axis`: 2D Study with a face in y = 0; Sector outer 30; `BoundBox.XMin == 0`, `XMax == 30`, `YMax == 0`, area `approx(pi*900/2)`.
  - `test_custom_air_without_source_raises`: Custom, no Source → recompute leaves the object invalid; `airshapes.air_shape(obj, "3D")` raises `ValueError` with "choose a body".
  - `test_fit_box_adds_padding`: two boxes spanning x 0–20, y 0–10, z 0–10; `fit_box(..., 50, "3D")` → centre (10, 5, 5), sizes (40, 20, 20).
- [ ] **Step 2: Run** `pixi run pytest tests/freecad_addon/test_air.py -v` — expect failures (missing module/attributes).
- [ ] **Step 3: Implement** `airshapes.py` and the `objects.py` additions above. Sector faces: `Part.Face` from `Part.makeCircle` arcs + radial lines (or `Part.makeCylinder(r, h, base, dir, angle)` minus the inner one for 3D); rotate `StartAngle`.
- [ ] **Step 4: Run** the same command — all pass. Also `pixi run pytest tests/freecad_addon/test_study.py` (folder count changes must not break it).
- [ ] **Step 5: Commit** `git add freecad_addon/emsolution/airshapes.py freecad_addon/emsolution/objects.py tests/freecad_addon/test_air.py` — "Air Region item: Box, Sector and Custom outer shapes".

### Task 2: IDs and materials for the air

**Files:**
- Modify: `freecad_addon/emsolution/objects.py` (`volume_keys`, `_owner`, `id_rows`, `material_rows`, `assignment_problem`, `bodies_without_material`, new `assignable`, `air_keys`, `key_name`)
- Test: `tests/freecad_addon/test_air.py`

**Interfaces:**
- Consumes: Task 1 `air_regions`.
- Produces:
  - `objects.air_keys(study) -> list[str]`: no movement: `[air.Name]`; sliding: `[f"{air.Name}#fixed", f"{air.Name}#moving"]`. (Interface keys are added to `volume_keys` in Task 8.)
  - `volume_keys(study)` = body names (Task 7 widens bodies to moving ones) + `air_keys(study)`.
  - `_owner(study, key)` resolves the objects of `key.split("#")[0].split("|")`.
  - `objects.key_name(study, key) -> str`: body → `volume_name(body)`; `X` → `clean(air.Label)`; `X#fixed` / `X#moving` → `clean(air.Label) + "_fixed"` / `"_moving"`.
  - `id_rows` lists every `volume_keys` entry with `key_name`.
  - `objects.assignable(study) -> list`: bodies + Air Regions. `material_rows`, `bodies_without_material`, `assignment_problem` use it (an Air Region can get a Material).

- [ ] **Step 1: Write the failing tests:**
  - `test_air_gets_mat_id_after_bodies`: bodies A, B + Box air → `update_ids` → `MatIds == {"A": "1", "B": "2", "<air.Name>": "3"}`; `id_rows` last row name `"Air"`.
  - `test_air_id_survives_rename_and_is_not_reused_after_delete` (Review Focus 3): rename air → same ID; delete air, add body C → C gets 4.
  - `test_air_region_can_get_a_material`: `assignment_problem(study, [air]) == ""`; after `assign`, `material_rows` contains a row whose first cell is `"Air"`.
  - `test_missing_air_material_is_warned`: `bodies_without_material` includes the air until assigned.
- [ ] **Step 2: Run** `pixi run pytest tests/freecad_addon/test_air.py -v` — new tests fail.
- [ ] **Step 3: Implement** the interfaces above.
- [ ] **Step 4: Run** `test_air.py` and `test_study.py` — pass.
- [ ] **Step 5: Commit** — "Air Region gets a MAT_ID and a material like a body".

### Task 3: Validation for the static air

**Files:**
- Modify: `freecad_addon/emsolution/validation.py` (new `_air(study, bodies, r)` called from `validate` after `_settings`)
- Modify: `freecad_addon/emsolution/airshapes.py` (new `outside(body_shape, air_shape, plane) -> float`)
- Test: `tests/freecad_addon/test_air.py`

**Interfaces:**
- Produces: `airshapes.outside(...)`: volume (3D) or area (2D) of `body_shape.cut(air_shape)`.
- Error texts (exact):
  - `"Only one Air Region per Study: " + labels + ". Delete the others."` (item = second region)
  - `f"{body.Label} is not fully inside Air Region {air.Label}."` (item = air, refs = [(body, "")]) when `outside > 1e-6 * body measure`
  - `f"Air Region {air.Label}: in a ZX (axisymmetric) Study use a half disc or a rectangle starting on the Z axis."` when ZX and (Box with `Center.x - Length/2 < 0`, or Custom)
  - `f"Air Region {air.Label}: {e}"` when `air_shape` raises `ValueError`
  - `f"Air Region {air.Label}: the outer radius must be larger than the inner radius."` and `"…: the end angle must be larger than the start angle (at most 360° more)."`

- [ ] **Step 1: Write the failing tests:** `test_two_air_regions_is_an_error`, `test_body_outside_air_is_an_error_naming_it`, `test_body_inside_air_passes` (no problems from `_air`), `test_zx_box_left_of_axis_is_an_error`, `test_zx_half_disc_passes`, `test_custom_without_source_is_an_error`, `test_bad_radii_and_angles_are_errors`. Each asserts the exact text above appears in `[p.text for p in validation.errors(validation.validate(study))]`.
- [ ] **Step 2: Run** — fail.
- [ ] **Step 3: Implement** `_air` and `outside`.
- [ ] **Step 4: Run** `test_air.py`, `test_study.py` — pass.
- [ ] **Step 5: Commit** — "Validate the Air Region: one per Study, bodies inside, ZX shapes".

### Task 4: Job and meshers fill the static air

**Files:**
- Modify: `freecad_addon/emsolution/jobwriter.py` (`check` returns the air too; `write_job` writes `"air"`)
- Modify: `freecad_addon/emsolution/meshcommon.py` (new `claim_air`)
- Modify: `freecad_addon/emsolution/mesher.py`, `freecad_addon/emsolution/mesher2d.py` (`build` imports and claims the air)
- Test: `tests/freecad_addon/test_mesher.py`, `tests/freecad_addon/test_mesher2d.py`, `tests/freecad_addon/test_air.py`

**Interfaces:**
- Consumes: Tasks 1–3.
- Produces:
  - Job key (static): `"air": {"name": str, "mat_id": int, "file": "geometry/air.brep", "size": float}`; absent when the Study has no Air Region. Size: smallest whole-body Mesh Size on the air, else `DefaultMeshSize`.
  - `meshcommon.claim_air(air_tags: list[int], owner: dict[int, str]) -> list[int]`: the air's final top-dimension tags that no body owns, sorted. Raises `JobError("the air region is fully covered by bodies")` when empty.
  - Both `build`s: the air file is imported after the bodies (dimension 3 or 2), fragmented with everything, then `claim_air`; the air's physical group is `addPhysicalGroup(dim, tags, air["mat_id"], name=air["name"])`; the air's tags join `by_size` with `air["size"]`. The body overlap check stays as it is and ignores the air.
  - `run_job` prints `MAT_ID {id:>6}  {name}` for the air after the bodies.

- [ ] **Step 1: Write the failing tests:**
  - `test_mesher2d.py::test_air_fills_around_body_and_body_wins`: square body 0–1 + air rectangle −1–2; groups: body triangles > 0, air triangles > 0; total meshed area of air group == 9 − 1 (sum triangle areas, tolerance 1e-6); no node of air triangles strictly inside the body square.
  - `test_mesher.py::test_air_fills_around_box`: box body + air box 3× larger; air group volume == 27 − 1 (tet volumes).
  - `test_mesher2d.py::test_air_covered_by_bodies_fails_cleanly`: air == the body → last stderr line `"ERROR: the air region is fully covered by bodies"`.
  - `test_air.py::test_job_has_air_with_default_size`: write_job → `job["air"] == {"name": "Air", "mat_id": 2, "file": "geometry/air.brep", "size": 5.0}` and the BREP exists.
  - `test_air.py::test_air_mesh_size_item_applies`: Mesh Size 2 mm on `(air, "")` → `job["air"]["size"] == 2.0`.
  - `test_air.py::test_air_face_mesh_size_is_exported`: Mesh Size 1 mm on `(air, "Face1")` → one `job["sizes"]` entry with one BREP file.
- [ ] **Step 2: Run** `pixi run pytest tests/freecad_addon/test_mesher.py tests/freecad_addon/test_mesher2d.py tests/freecad_addon/test_air.py -v` — new tests fail.
- [ ] **Step 3: Implement.** Keep `check`'s 3-tuple (callers in `studymaterials.py:193` and `test_study.py` unpack it); add `jobwriter.air_size(study) -> float` for the size. Faces, edges and vertices of the Air Region in a Mesh Size item go into `job["sizes"]` like body sub-elements (spec decision 4): treat the air's Name as included in `check`'s `sized` filter.
- [ ] **Step 4: Run** the three files — pass. Run `pixi run pytest tests/freecad_addon` — all pass.
- [ ] **Step 5: Commit** — "Mesher fills the Air Region around the bodies; bodies win".

### Task 5: Air Region command, panel and view

**Files:**
- Modify: `freecad_addon/emsolution/commands.py` (new `AddAirRegion`, registered as `EMS_AddAirRegion`, toolbar/menu next to Mesh Size)
- Modify: `freecad_addon/emsolution/taskpanels.py` (new `ViewProviderAir`, `AirRegionPanel`)
- Create: `freecad_addon/icons/airregion.svg` (simple, same style as existing icons)
- Modify: `freecad_addon/InitGui.py` if commands are listed there
- Test: `tests/freecad_addon/gui_smoke.py`

**Interfaces:**
- Consumes: Tasks 1–3 (`make_air_region`, `fit_box`, validation texts).
- Produces:
  - `AddAirRegion.Activated`: refuses with `warn("This Study already has an Air Region.")` when one exists; otherwise opens a transaction, `make_air_region(study, "Box")`, runs `fit_box(assignable bodies, 50, plane)` into it when the Study has bodies, and opens `AirRegionPanel(obj, new=True)`.
  - `ViewProviderAir`: Transparency 80, `DisplayMode` "Flat Lines" in 3D, double-click opens `AirRegionPanel`.
  - `AirRegionPanel(obj, new=False)`: shape combo (in 2D "Box" shows as "Rectangle"; in ZX only "Rectangle" and "Half disc", mapped to Box/Sector), fields shown per shape (Box: centre x/y/z, length, width, height; Sector: inner/outer radius, start/end angle, z min, height; Custom: "pick a body" via current selection), "Fit to bodies" button + padding % (Box only). OK commits, Cancel aborts the transaction (same pattern as `ItemPanel`).
- [ ] **Step 1: Add smoke steps** to `gui_smoke.py` after the existing Run Mesh: run `EMS_AddAirRegion`, assert a panel opened and the Box encloses every body; press OK; run it again and assert the "already has" warning; Run Mesh; assert the log shows the air `MAT_ID` line.
- [ ] **Step 2: Run** `pixi run freecad tests\freecad_addon\gui_smoke.py`; last line of `%TEMP%\ems_gui_smoke.txt` is `FAIL`.
- [ ] **Step 3: Implement** the command, view provider, panel and icon.
- [ ] **Step 4: Run** the smoke test — `PASS`. Run `pixi run pytest tests/freecad_addon` — pass.
- [ ] **Step 5: Commit** — "Add Air Region command and panel".

### Task 6: Example builder and the static cases

**Files:**
- Create: `tests/freecad_addon/cases.py` (case builders, shared by pytest and the script)
- Create: `tests/freecad_addon/meshreport.py` (reads meshes, makes the report; never imports FreeCAD)
- Create: `tests/freecad_addon/build_examples.py` (script)
- Create: `tests/freecad_addon/test_examples.py`

**Interfaces:**
- Produces:
  - `cases.Case` dataclass: `name: str`, `build: Callable[[App.Document], Study]`, `checklist: list[str]`, `expect_error: str = ""` (substring of a validation error for E-cases).
  - `cases.CASES: list[Case]`, names `"01_rect_2d"` … `"12_hollow_sector_3d"`, `"E1_body_outside_air"`, `"E6_bodies_overlap"` in this task (the rest come in Tasks 11 and 13). Geometry per spec section 7, in mm, built from Part primitives and `Part.Face`; every case assigns one library material to every body and the air so validation has no warnings.
  - `cases.run_case(case, out_dir) -> str`: makes `out_dir/<name>/`, builds a new document, saves `<name>.FCStd` there, runs `validation.validate`; for an E-case returns the error texts; otherwise `jobwriter.write_job` and the mesher subprocess (`mesher.py` or `mesher2d.py` by dimension, `sys.executable`), then `meshreport.report(case_dir, job)`; writes `report.txt` and returns its text.
  - `meshreport.groups(msh_path) -> dict[int, tuple[str, int]]`: MAT_ID → (name, element count) via the Gmsh API.
  - `meshreport.report(case_dir, job) -> str`: MAT_ID table, then (from Task 11) slide and periodic checks, then the case checklist.
  - `build_examples.py [out_dir] [--only NAME ...] [--sample DIR]`: default out_dir `C:\Users\hamed\Desktop\delme\air_examples`; runs `run_case` for each case and prints one line per case: `OK name`, `ERROR name: text` (expected for E-cases) or `FAILED name: text`.
  - `test_examples.py`: one test per case via `pytest.mark.parametrize("case", CASES, ids=...)`; non-E cases: report has a row for every body and the air with count > 0; E-cases: `expect_error` is in the returned text.

- [ ] **Step 1: Write** `test_examples.py` and `cases.py` with the case list (builders included: they are test fixtures).
- [ ] **Step 2: Run** `pixi run pytest tests/freecad_addon/test_examples.py -v` — fails until `run_case`/`meshreport` exist.
- [ ] **Step 3: Implement** `run_case`, `meshreport.groups`, `meshreport.report`, `build_examples.py`.
- [ ] **Step 4: Run** `pixi run pytest tests/freecad_addon/test_examples.py -v` — pass. Run `pixi run python tests/freecad_addon/build_examples.py` and check the folder has 14 case folders, each with `.FCStd`, `pre_geom(2D).msh`, `report.txt` (E-cases: `report.txt` with the error).
- [ ] **Step 5: Commit** — "Example models for the static air, with reports and checklists".

---

## Part B: Sliding motion, 2D

### Task 7: Moving bodies in IDs, materials and the job; sliding no longer blocked

**Files:**
- Modify: `freecad_addon/emsolution/objects.py` (`study_bodies`, `assignable`, `volume_keys`)
- Modify: `freecad_addon/emsolution/geometry.py` (`export_unavailable` no longer refuses "Sliding motion")
- Modify: `freecad_addon/emsolution/jobwriter.py` (`check`'s `volumes` also hold the moving bodies, after the main ones — take them from `geometry.setup`'s second value; job lists `"moving": [mat_id, ...]`)
- Modify: `freecad_addon/emsolution/taskpanels.py` (remove the "Sliding-interface configuration will be added…" text)
- Test: `tests/freecad_addon/test_air.py`, `tests/freecad_addon/test_study.py` (update the `sliding motion still blocked` tests: they now assert that sliding is no longer refused as "planned for a later phase"; the "needs a Sliding Interface" error comes in Task 9)

**Interfaces:**
- Produces:
  - `objects.study_bodies(study) -> list`: main bodies, then moving bodies when `Movement == "Sliding motion"`, no duplicates. Replaces `_main_bodies` inside `assignable` and `volume_keys`.
  - Job key `"moving": [int]`: MAT_IDs of the moving bodies (absent when static).
- [ ] **Step 1: Write the failing tests:** `test_moving_bodies_get_ids_after_main_bodies`, `test_moving_body_can_get_a_material`, `test_job_lists_moving_mat_ids`, and change the "sliding still blocked" assertions in `test_study.py` as above.
- [ ] **Step 2: Run** — fail.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `pixi run pytest tests/freecad_addon` — pass.
- [ ] **Step 5: Commit** — "Moving geometry gets IDs, materials and goes into the job".

### Task 8: Sliding Interface item, slide shapes and air cells

**Files:**
- Modify: `freecad_addon/emsolution/objects.py` (`SlidingInterface`, `make_sliding_interface`, `sliding_interfaces`; `volume_keys` gains interface keys)
- Modify: `freecad_addon/emsolution/airshapes.py` (`slide_surface`, `slide_marker`, `cells`, `cell_of`, `period`)
- Test: `tests/freecad_addon/test_air.py`

**Interfaces:**
- Produces:
  - `objects.SlidingInterface(_Named)` on `Part::FeaturePython`, group `"Sliding"`: `Kind` enum `["Rotational", "Axial gap", "Linear"]`; `AirRegion` (`App::PropertyLink`); `Radius` (`App::PropertyLength`, 50); `Position` (`App::PropertyDistance`, 0); `NormalAxis`, `MotionAxis` enums `["X", "Y", "Z"]` (defaults "Y", "X"); `Divisions` (`App::PropertyIntegerConstraint`, (90, 2, 100000, 2)); `CrossDivisions` ((10, 1, 100000, 1)). Lives in `AirRegionsGroup`. `execute` sets `Shape = slide_surface(...)`.
  - `objects.make_sliding_interface(study, kind, **props) -> obj` (links the Study's Air Region), `objects.sliding_interfaces(study)`.
  - `volume_keys` adds `[iface.Name for iface in sliding_interfaces]` when sliding; `key_name` → `clean(iface.Label)`. These IDs are the `SLIDE_MAT_ID`s.
  - `airshapes.slide_surface(iface, air_shape, plane) -> Part.Shape`: a large curve/surface intersected with `air_shape` (`common`), so it spans the air. 2D Rotational: arc/circle radius `Radius` about Z; Linear: line `NormalAxis` = `Position`. 3D Rotational: cylinder face about Z; Axial gap: plane z = `Position`; Linear: plane `NormalAxis` = `Position`. A result covering 360° is split at 0° and 180° into two pieces.
  - `airshapes.slide_marker(iface, surface, plane) -> Part.Shape`: 2D: the `Part.Vertex` at angle `start` (Rotational: `StartAngle` of a Sector air, else 0°) on the circle, or the line's end with the smallest motion-axis coordinate (Linear). 3D: the generatrix `Part.Edge` there (Rotational: vertical line; Axial gap: radial line; Linear: line across the motion at its minimum).
  - `airshapes.cells(air_shape, surfaces) -> list[Part.Shape]`: `BOPTools.SplitAPI.slice(air_shape, surfaces, "Split")` pieces (solids in 3D, faces in 2D).
  - `airshapes.cell_of(body_shape, cells) -> int | None`: index of the one cell holding ≥ 1 − 1e-6 of the body's measure; `None` when it crosses.
  - `airshapes.period(study) -> dict | None`: Sector air with `EndAngle − StartAngle < 360` → `{"kind": "rotation", "angle": deg, "start": StartAngle}`; Box air with a Linear interface → `{"kind": "translation", "vector": [L, 0, 0]}` along `MotionAxis` with `L` = Box size on that axis, plus `"start"` = Box minimum on that axis; else `None`.
- [ ] **Step 1: Write the failing tests:**
  - `test_full_circle_interface_is_two_half_arcs`: 2D, Sector air R 100 0–360, Rotational r 42.5 → 2 edges, total length `2*pi*42.5`.
  - `test_sector_interface_spans_the_sector`: air 0–45°, r 80.575 → 1 edge, length `pi/4*80.575`.
  - `test_linear_interface_spans_box`: Box x 0–80, Linear Y at 11 → line from (0, 11) to (80, 11).
  - `test_cylinder_interface_3d_halves`: 3D Sector air h 100 → 2 faces, total area `2*pi*42.5*100`.
  - `test_marker_2d_is_point_at_start_angle` / `test_marker_3d_is_vertical_generatrix`.
  - `test_cells_and_cell_of`: rotor disc r 40 and stator ring 45–80, interface r 42.5 → 2 cells; rotor in the inner cell, stator outer; a disc r 44 → `None`.
  - `test_body_on_slide_surface_is_not_crossing` (Review Focus 1): rotor disc radius exactly 42.5 → inner cell, not `None`.
  - `test_period_sector_and_linear`: 45° sector → `{"kind": "rotation", "angle": 45.0, "start": 0.0}`; Box x 0–80 + Linear X → vector `[80, 0, 0]`; full circle → `None`.
  - `test_interface_gets_slide_mat_id`: sliding Study → `MatIds` has the interface key; `id_rows` names it.
- [ ] **Step 2: Run** `pixi run pytest tests/freecad_addon/test_air.py -v` — fail.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** — pass.
- [ ] **Step 5: Commit** — "Sliding Interface item: slide surface, marker, air cells and period".

### Task 9: Validation for sliding

**Files:**
- Modify: `freecad_addon/emsolution/validation.py` (new `_slides(study, r)` after `_air`)
- Test: `tests/freecad_addon/test_air.py`

**Interfaces:**
- Consumes: Task 8.
- Error texts (exact; warnings marked):
  - `"Sliding motion needs an Air Region and at least one Sliding Interface."`
  - warning: `f"Sliding Interface {i.Label} is not used: the Study has no movement."`
  - `"Sliding motion is not supported in a ZX (axisymmetric) Study."`
  - `f"Sliding Interface {i.Label}: a Linear interface needs a Box Air Region."`
  - `f"Sliding Interface {i.Label}: Divisions must be even for a full 360° interface (it is meshed in two halves)."`
  - `f"Sliding Interface {i.Label} does not cut the Air Region."` (empty `slide_surface`)
  - `f"{body.Label} crosses a Sliding Interface."` + for Rotational/Axial kinds `" Rotation is about the global Z axis; put the machine axis on Z."`
  - `f"Moving body {m.Label} and fixed body {f.Label} are on the same side of the Sliding Interfaces."`
  - `f"Part of the air between Sliding Interfaces holds no body; its side is unknown. Move an interface or add the body."`
  - `"No body is in the moving geometry."` when sliding and the Moving region is empty
- [ ] **Step 1: Write the failing tests**, one per text, plus `test_valid_2d_motor_has_no_slide_problems`.
- [ ] **Step 2: Run** — fail.
- [ ] **Step 3: Implement** `_slides`; compute cells once per validate.
- [ ] **Step 4: Run** `pixi run pytest tests/freecad_addon` — pass.
- [ ] **Step 5: Commit** — "Validate sliding: interfaces, sides, crossings, divisions".

### Task 10: Slide job

**Files:**
- Modify: `freecad_addon/emsolution/jobwriter.py` (`write_job` slide keys; `rotor_file(study)`)
- Test: `tests/freecad_addon/test_air.py`

**Interfaces:**
- Produces (job keys, sliding only):
  - `"rotor_file"`: `<simulation folder>/rotor_mesh2D.msh` (2D) or `rotor_mesh.msh` (3D); `jobwriter.rotor_file(study) -> str`.
  - `"air"` gets `"sides": {"fixed": {"mat_id", "name"}, "moving": {"mat_id", "name"}}` instead of top-level `mat_id`/`name` (names from `key_name`).
  - `"moving_cells": ["geometry/cell_<k>.brep", ...]`: the cells on the moving side.
  - `"slides": [{"name", "kind": "rotational"|"axial"|"linear", "files": ["geometry/slide_<id>_<k>.brep"], "marker": "geometry/marker_<id>.brep", "divisions": int, "cross_divisions": int (3D only), "slide_mat_id": int, "full": bool}]`.
  - `"periodic"`: `airshapes.period(study)` or absent.
- [ ] **Step 1: Write the failing test** `test_slide_job_2d_sector`: the 45° case geometry (rotor r 30–78, stator 82–149, shaft r < 30 moving, interface r 80.575, `Divisions` 90) → assert `rotor_file` ends with `rotor_mesh2D.msh`, `slides[0]` has `divisions == 90`, `full is False`, `kind == "rotational"`, `periodic == {"kind": "rotation", "angle": 45.0, "start": 0.0}`, one moving cell file, all files exist.
- [ ] **Step 2: Run** — fail.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `pixi run pytest tests/freecad_addon` — pass.
- [ ] **Step 5: Commit** — "Write the sliding interfaces, moving cells and period into the job".

### Task 11: 2D slide meshing: transfinite slide, periodic link, two files, report

**Files:**
- Modify: `freecad_addon/emsolution/meshcommon.py` (`apply_slides`, `apply_periodic`, `write_split`, `slide_report`, `run` writes two files)
- Modify: `freecad_addon/emsolution/mesher2d.py` (`build` imports cells, slides, markers; returns the split)
- Modify: `tests/freecad_addon/meshreport.py` (slide and periodic checks), `tests/freecad_addon/cases.py` (cases 13–16, E2, E4, E5; E3 is 3D and comes in Task 13), `tests/freecad_addon/build_examples.py` (`--sample`)
- Test: `tests/freecad_addon/test_mesher2d.py`, `tests/freecad_addon/test_examples.py`

**Interfaces:**
- Consumes: Task 10 job keys.
- Produces:
  - `build(job, folder)` may return `split = {"fixed": [(dim, tags, id, name)], "moving": [(dim, tags, id, name)]}`; `meshcommon.run` then writes both files instead of one: fixed → `job["mesh_file"]`, moving (+ marker group) → `job["rotor_file"]`, each through scratch files and `os.replace`, and still writes the whole-model `mesh.unv`.
  - `meshcommon.split_air(air_tags, moving_cell_tags) -> (list[int], list[int])`: fixed and moving air tags.
  - `meshcommon.apply_slides(slides, mapped, dim) -> dict[int, list[int]]`: for each slide, its final curves (2D) or faces (3D); a full slide gets `divisions/2` per half, a sector/linear one `divisions`; when fragment split a half further, share with `_share` by length (Review Focus 4); `setTransfiniteCurve(tag, n+1)`; in 3D faces `setTransfiniteSurface(face, "Left", corners)` with `cross_divisions` on the other curves. Returns `{slide_mat_id: marker final tags}`. Errors: `JobError(f"sliding interface {name}: {file} did not merge with the model")`.
  - `meshcommon.apply_periodic(periodic, dim)`: entities of dimension `dim-1` on the boundary of the model that lie on the source plane (θ = `start`, or motion-axis coordinate = `start`) get `setPeriodic(dim-1, [target], [source], affine)` with the rotation by `angle` about Z or translation by `vector`; the target is the entity on the other plane whose centre of mass matches the transformed source centre within 1e-6 × model size. No partner → `JobError(f"periodic boundaries do not match: the piece at {_at(...)} has no partner on the other side")` (Review Focus 5).
  - `meshcommon.write_split(groups, path, version)`: copies the listed physical groups' elements into a new discrete Gmsh model with nodes renumbered from 1 and writes it.
  - `meshcommon.slide_report(job) -> list[str]`: per slide `SLIDE_NDIV`, `SLIDE_MAT_ID`; `ANGLE` (deg) or `DXYZ` (m, = mm / 1000); then a `"14_Periodic_Boundary_Conditions"` JSON block (`CYCLIC` 2 for rotation, 1 for translation, `SYMMETRY` 1 written with a comment line "set SYMMETRY to 0 for a periodic, 1 for an anti-periodic model", `SLIDE_CONDITION` per slide with `FITNESS` 0.01), then `"Meshes are in mm: use UNIT = 1 in 10_1_Input_Files."`. `run_job` prints it after the MAT_ID table.
  - `meshreport.slide_check(fixed_msh, rotor_msh, on_slide) -> (int, int, bool)`: node counts on the slide in each file and whether the coordinate sets are equal (1e-9).
  - `meshreport.periodic_check(msh, period) -> bool`.
  - `build_examples.py --sample DIR`: for `14_sector_motor_2d`, compares the slide node angles and the slide point angle with `DIR/pre_geom2D.msh` / `DIR/rotor_mesh2D.msh` and adds the result to the report.
- [ ] **Step 1: Write the failing tests** in `test_mesher2d.py` (job + BREPs written with Gmsh like the existing tests):
  - `test_full_circle_slide_has_n_nodes_on_both_sides`: rotor disc r 40, stator ring 45–80, air disc r 100, slide circle halves r 42.5, `divisions` 72 → `pre_geom2D.msh` and `rotor_mesh2D.msh` both have exactly 72 nodes at r = 42.5, equal coordinates, angles every 5°.
  - `test_rotor_file_has_slide_point_at_start_angle`: rotor file has a dim-0 physical group `slide_mat_id` with one point element at (42.5, 0); the stator file has no dim-0 group.
  - `test_each_file_numbers_nodes_from_one`: both files: min node tag 1, max == node count.
  - `test_air_split_by_side`: fixed air group in the stator file only, moving air group in the rotor file only.
  - `test_sector_slide_and_periodic_edges_match`: the 45° sector, `divisions` 90 → 91 slide nodes every 0.5° in both files; in each file the node radii on θ = 0 equal those on θ = 45°.
  - `test_body_vertex_on_slide_circle_keeps_n_nodes` (Review Focus 4): a stator tooth corner on the slide circle → still 72 nodes.
  - `test_nonperiodic_geometry_fails_cleanly` (Review Focus 5): a body cut by θ = 0 but not by 45° → last stderr line starts with `"ERROR: periodic boundaries do not match"`.
  - `test_linear_two_slides_and_translation_period`: case 16 geometry → both lines have 33 nodes in both files; nodes at x = 0 equal nodes at x = 80 shifted.
  - `test_slide_report_lines`: stdout contains `SLIDE_NDIV 90`, `SLIDE_MAT_ID`, `ANGLE 45`, `UNIT = 1`.
  - `test_examples.py`: cases 13–16 report `slide nodes match: yes` and `periodic: yes` where a period exists; E2, E4, E5 expect their Task 9 texts.
- [ ] **Step 2: Run** `pixi run pytest tests/freecad_addon/test_mesher2d.py tests/freecad_addon/test_examples.py -v` — fail.
- [ ] **Step 3: Implement** in the order: `split_air`, `apply_slides`, `apply_periodic`, `write_split` + `run` change, `slide_report`, then `mesher2d.build`, then the report and cases.
- [ ] **Step 4: Run** `pixi run pytest tests/freecad_addon` — pass. Run `pixi run python tests/freecad_addon/build_examples.py --only 14_sector_motor_2d --sample "C:\Users\hamed\Downloads\Teams\transient\transient"` and read the comparison lines in its report.
- [ ] **Step 5: Commit** — "2D sliding: matching slide and periodic nodes, stator and rotor files, slide report".

### Task 12: Sliding Interface command and panel

**Files:**
- Modify: `freecad_addon/emsolution/commands.py` (`AddSlidingInterface` → `EMS_AddSlidingInterface`; active only when `Movement == "Sliding motion"`)
- Modify: `freecad_addon/emsolution/taskpanels.py` (`SlidingInterfacePanel`; the Study panel's Movement row shows a hint "Add an Air Region and a Sliding Interface" when sliding without them)
- Modify: `freecad_addon/emsolution/runner.py` (`load_result` message names both written files when `rotor_file` is in the job)
- Create: `freecad_addon/icons/slidinginterface.svg`
- Test: `tests/freecad_addon/gui_smoke.py`

**Interfaces:**
- `AddSlidingInterface.Activated`: refuses with `warn("Add an Air Region first.")` without one; else `make_sliding_interface(study, "Rotational" if Sector air else "Linear")` and opens the panel.
- `SlidingInterfacePanel(obj, new=False)`: kind combo (2D: Rotational, Linear; 3D: all three), Radius (Rotational), Position + normal axis (Axial gap: fixed Z; Linear), motion axis (Linear), Divisions, Cross divisions (3D only). Shows the computed angle per division (`360/Divisions` or span/Divisions) as a read-only line.
- [ ] **Step 1: Add smoke steps:** a 2D Study with sliding motion, rotor and stator faces, Air Region (Sector), Add Sliding Interface (radius between them, Divisions 72), OK, Run Mesh; assert both `pre_geom2D.msh` and `rotor_mesh2D.msh` exist and the log contains `SLIDE_NDIV 72`.
- [ ] **Step 2: Run** the smoke test — `FAIL`.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** the smoke test — `PASS`; `pixi run pytest tests/freecad_addon` — pass.
- [ ] **Step 5: Commit** — "Add Sliding Interface command and panel".

---

## Part C: Sliding motion, 3D

### Task 13: 3D slide meshing and the 3D examples

**Files:**
- Modify: `freecad_addon/emsolution/mesher.py` (`build` imports air, cells, slides, markers; returns the split; marker group is dim 1 line elements)
- Modify: `freecad_addon/emsolution/meshcommon.py` only if a 3D need is missing (e.g. 3-corner half discs for an Axial gap interface that reaches the axis)
- Modify: `tests/freecad_addon/cases.py` (cases 17–20)
- Test: `tests/freecad_addon/test_mesher.py`, `tests/freecad_addon/test_examples.py`

**Interfaces:**
- Consumes: Tasks 10–11 (`apply_slides`, `apply_periodic`, `split_air`, `write_split`, `slide_report`).
- [ ] **Step 1: Write the failing tests** in `test_mesher.py`:
  - `test_radial_slide_cylinder_matches`: rotor cylinder r 40 h 50, stator ring 45–80, air cylinder r 100 h 100, slide cylinder r 42.5 halves, `divisions` 72, `cross_divisions` 10 → both files have the same node set on r = 42.5: 72 × 11 nodes; z levels every 10 mm; angles every 5°.
  - `test_rotor_file_has_slide_edge_at_start_angle`: dim-1 group `slide_mat_id` in `rotor_mesh.msh` with 10 line elements along (42.5, 0, z); none in `pre_geom.msh`.
  - `test_slide_triangles_same_after_one_division`: the slide-surface triangles of the rotor file rotated by 5° coincide with its own triangles (diagonals one way).
  - `test_axial_gap_disc_reaching_axis`: rotor disc z 0–10, stator z 12–22, slide plane z 11 over the full air radius → nodes on z = 11 match in both files; slide edge is radial.
  - `test_linear_3d_plane_and_period`: case 20 geometry → slide plane nodes 33 × 9 in both files; faces x = 0 and x = 80 have matching nodes in each file.
  - `test_examples.py`: cases 17–20 report matches; also `E3_axis_not_z` expects `"Rotation is about the global Z axis"`.
- [ ] **Step 2: Run** `pixi run pytest tests/freecad_addon/test_mesher.py tests/freecad_addon/test_examples.py -v` — fail.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `pixi run pytest tests/freecad_addon` — pass; `pixi run lint` — pass; smoke test — `PASS`. Run `pixi run python tests/freecad_addon/build_examples.py` (all cases) and check every line is `OK` or the expected `ERROR`.
- [ ] **Step 5: Commit** — "3D sliding: cylinder, axial-gap and linear interfaces; 3D examples".

### Task 14: Final check

- [ ] **Step 1:** `pixi run pytest tests/freecad_addon` — all pass; `pixi run lint` — pass; `pixi run format` on the changed files leaves no diff.
- [ ] **Step 2:** Run the GUI smoke test — `PASS`.
- [ ] **Step 3:** Rebuild all examples into `C:\Users\hamed\Desktop\delme\air_examples` with `--sample "C:\Users\hamed\Downloads\Teams\transient\transient"`, and list for the user what could not be checked automatically: EMSolution itself has not run any generated `rotor_mesh` (spec section 9).
- [ ] **Step 4:** Mark the spec status "implemented" and commit.
