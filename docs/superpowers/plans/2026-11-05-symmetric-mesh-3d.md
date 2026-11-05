# Symmetric Mesh 3D Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Symmetric Mesh (mesh the cell, copy the mesh) works in 3D Studies, with Materials on solids, copied
excitation surfaces and Rotational sliding motion.

**Architecture:** `meshsym.py` becomes dimension-generic (`dim` 2 or 3) and `mesher.py` hands symmetric jobs to it
the way `mesher2d.py` does. The add-on side (validation, job writer, Material panel) gains the 3D forms of the 2D
rules: solids for faces, volumes for areas, a cylinder for the sliding circle. The chain reader (`symmetry.py`) is
unchanged apart from its error texts.

**Tech Stack:** Python 3.11, gmsh Python API (mesher process, no FreeCAD), FreeCAD 1.1 Part/Draft (add-on), pytest.

**Spec:** `docs/superpowers/specs/2026-11-05-symmetric-mesh-3d-design.md` (builds on
`docs/superpowers/specs/2026-10-23-symmetric-mesh-design.md`). Read both.

## Global Constraints

- Work on a branch `feature/symmetric-mesh-3d` off `main`; never commit to `main` directly.
- Run everything through Pixi. Add-on tests: `pixi run -e addon pytest tests/freecad_addon/<file> -k <name>`; whole
  suite: `pixi run -e addon test-addon`.
- `meshsym.py`, `mesher.py`, `mesher2d.py`, `meshcommon.py` never import FreeCAD. GUI code only in `commands.py` /
  `taskpanels.py`.
- Ruff only, line length 120, double quotes; `pixi run format` and `pixi run lint` before each commit; never reorder
  imports; never `--no-verify`. `highlight.py` is unformatted on purpose: keep it out of commits.
- 2D behaviour must not change: every existing test in `tests/freecad_addon/` keeps passing at every commit.
- Mirror planes contain the Z axis, polar arrays turn about Z (unchanged chain rules). No z = 0 mirror, no
  translations, no Air Region, Rotational sliding only, full turn.
- Only nodes must match across the sliding cylinder; nothing re-triangulates it (spec §6).
- Commit messages end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Review Focus

- A cell body that is a face (or a top made of faces) in a 3D Study: a named Validate error, never a mesher crash
  (test in Task 4).
- An excitation face that two copies share, or that the cell is not split at: counted once / refused naming the face,
  not silently half-covered (tests in Task 2).
- A sliding cylinder that one side's cells do not reach over the whole height: refused, naming the side (test in
  Task 3).
- A face click on a Material panel with no picked point (tree selection) or on a face between two solids where the
  far side cannot be told: the panel asks, it never guesses (test in Task 6).
- Old 2D symmetric documents and jobs: unchanged output (the whole 2D suite at every task, and Task 1's dispatch test).

---

### Task 1: Dimension-generic cell meshing and copying (no excitations, no sliding)

**Files:**
- Modify: `freecad_addon/emsolution/meshsym.py`
- Modify: `freecad_addon/emsolution/mesher.py` (dispatch, `--check`)
- Create: `tests/freecad_addon/test_meshsym3d.py`

**Interfaces:**
- Produces: `meshsym.run(job_path, build, dim=2) -> dict`, `meshsym.check(job_path, build, dim=2) -> None`,
  `meshsym.report(job) -> list[str]` (unchanged names; 2D callers pass nothing new). `mesher.run_job` and
  `mesher.check_job(job_path, build)` route a job with a `"symmetric"` key to `meshsym` with `dim=3`.
- Produces (job format, 3D): `{"model_name", "mesh_file", "options", "volumes": [{"mat_id", "name", "file",
  "size"}], "surfaces": [], "sizes": [], "symmetric": {"sides": [{"side", "cells", "transforms", "pieces"}]}}`;
  cell `file`s and piece `file`s hold solids. No `"dimension"` key (as in normal 3D jobs).
- Produces (test helpers in `test_meshsym3d.py`): `write_sector_solids(path, *sectors)` with
  `sector = (inner, outer, a0, a1, z0, z1)` (the 2D `add_sector` face extruded from z0 to z1);
  `mesh_check_3d(path, radii, heights) -> (kinds: set[str], inverted: int, loose: int)`.

- [ ] **Step 1: Write the test helpers and failing tests** in `test_meshsym3d.py`, modelled on
  `MeshSymTest` in `test_meshsym.py` (reuse its `rotation`, `mirror_line`, `compose`, `chain`). `mesh_check_3d`
  counts an element inverted when the signed volume of these corner tetrahedra is ≤ 0: tet (0,1,2,3), hex (0,1,3,4),
  prism (0,1,2,3), pyramid (0,1,3,4); and counts loose element faces: faces used by one element whose nodes are not
  all on a cylinder of `radii` or a plane z in `heights`. Ring job: cells r 10..20 (id 1) and 20..30 (id 2), 0..45°,
  z 0..10, `chain(45, 90, 4)`, pieces 8 inner sectors (MAT_ID 1) and 8 outer ones.

```python
def test_copies_cover_the_ring_without_gaps(self):
    r = self.ring_job()
    self.assertEqual(r.returncode, 0, r.stderr)
    kinds, inverted, loose = mesh_check_3d(self.files()[0], (10, 30), (0, 10))
    self.assertEqual((inverted, loose), (0, 0))

def test_each_copy_takes_its_piece_mat_id(self):  # outer pieces alternate MAT_ID 2 and 3
    r = self.ring_job(outer_ids=(2, 3) * 4)
    self.assertEqual(r.returncode, 0, r.stderr)
    self.assertEqual(set(groups(self.files()[0])), {1, 2, 3})

def test_asymmetric_drawing_is_refused(self):  # one outer piece cut at 50° instead of 45°
    r = self.ring_job(outer_cuts=[0, 50, 90, 135, 180, 225, 270, 315, 360])
    self.assertNotEqual(r.returncode, 0)
    self.assertIn("not symmetric", r.stderr)
    self.assertIn("mm³", r.stderr)

def test_pure_rotation_seams_conform(self):  # cell 0..90°, transforms rotation(90 k): periodic faces needed
    ...  # assert returncode 0 and loose == 0

def test_seams_that_do_not_match_are_refused(self):  # patch="meshsym._periodic = lambda *a, **k: None"
    ...  # assert returncode != 0 and "do not match" in stderr

def test_structured_cell_stays_hexes(self):  # Transfinite Body + Recombine on cell id 2 (whole body)
    ...  # assert "Hexahedron 8" in kinds and inverted == 0

def test_check_runs_the_symmetric_checks_and_writes_nothing(self):
    ...  # --check on the asymmetric job fails with "not symmetric"; on the good job prints "CHECK OK", no .msh
```

- [ ] **Step 2: Run them to verify they fail**
  Run: `pixi run -e addon pytest tests/freecad_addon/test_meshsym3d.py -v`
  Expected: FAIL (`mesher.py` ignores `"symmetric"` and meshes `volumes` normally, or errors).

- [ ] **Step 3: Make `meshsym` dimension-generic and dispatch from `mesher.py`.**
  `dim` flows from `run`/`check` into `_mesh` and every helper; `generate(job, dim)`. Per helper, the 3D form is:
  - `_side_curves` → the side's cell boundary entities of `dim - 1` (`_side_seams`); `_periodic` matches faces with
    the 3D `_same` (equal mass, corner points moved within tol, 3 inner sample points of `c` moved lie on `d` by
    `getClosestPoint(2, d, …)`; sample points from `getParametrizationBounds(2, c)` and `getValue(2, c, [u, v])`
    pairs) and calls `setPeriodic(dim - 1, [d], [c], m)`.
  - `_cell_entities`: entities of dimension `dim`; the stored measure is `getMass(dim, e)`.
  - `_land`: `import_brep(…, dim)`, `isInside(dim, …)`; coverage message says `mm³` in 3D, `mm²` in 2D:
    `not symmetric: piece {name} ({file}) has a volume of {v:.6g} mm³, but the copies of the cell landing on it cover {got:.6g} mm³`.
  - `_copy`: `addDiscreteEntity(dim, …)`, physical groups of `dim`. `mesh.reverse` already handles 3D types.
  - `_side_edges` / `_conform` / `_outline`: element faces of the side's `dim`-elements
    (`getElementFaceNodes(typ, 3, …)` for triangles and `(typ, 4, …)` for quads, keyed by sorted node tuples) checked
    against the outer boundary faces of the side's pieces (fragment the piece solids; boundary faces adjacent to one
    solid; `getClosestPoint(2, …)`). Message unchanged: `the copies of the cell do not match near (x, y, z) …`
    (3D adds z).
  - `_marker`, `_slide_arcs`, `_on_circle` stay 2D-only until Task 3; `_mesh` raises
    `JobError("3D sliding is not supported yet")` for a 3D job with a slide (removed in Task 3).
  In `mesher.py` add `_symmetric(job_path)`, `check_job(job_path, build)` and the `run_job` branch exactly as in
  `mesher2d.py`, with `dim=3`, and pass `check_job` to `main` as `mesher2d.py` does.

- [ ] **Step 4: Run the new tests and the whole add-on suite**
  Run: `pixi run -e addon pytest tests/freecad_addon/test_meshsym3d.py tests/freecad_addon/test_meshsym.py tests/freecad_addon/test_mesher.py -v`, then `pixi run -e addon test-addon`
  Expected: all PASS.

- [ ] **Step 5: Format, lint, commit**
  `pixi run format`, `pixi run lint`, then
  `git add freecad_addon/emsolution/meshsym.py freecad_addon/emsolution/mesher.py tests/freecad_addon/test_meshsym3d.py`
  and commit "Symmetric mesh: mesh and copy a 3D cell".

---

### Task 2: Copied excitation surfaces

**Files:**
- Modify: `freecad_addon/emsolution/meshsym.py`
- Test: `tests/freecad_addon/test_meshsym3d.py`

**Interfaces:**
- Consumes: Task 1's 3D `_mesh` / `_copy` (the `split` it returns: `{side: {mat_id: (name, entities)}}`).
- Produces (job format): each side may hold `"excitations": [{"smat_id": int, "name": str, "files": [rel, ...]}]`,
  each file one face of the top (the picked excitation faces of that side). Output: a 2D physical group
  `(smat_id, name)` per excitation in the side's file; `report` adds one `SMAT_ID {id:>6}  {name}` line per
  excitation, after the MAT_ID lines.
- Produces: `_copy` returns `(split, surfaces)` where `surfaces = {side: {smat_id: (name, entities)}}`; `run` writes
  them with the side's groups (`write_split` with dim-2 groups, or the single file without sliding).

- [ ] **Step 1: Write the failing tests** (ring job from Task 1, with excitations on the fixed side):

```python
def test_excitation_on_an_outer_top_face_gets_its_smat_id(self):
    # excitation face: top face (z = 10) of outer piece 20..30, 0..45°; SMAT_ID 101
    ...  # returncode 0; groups(msh)[101] == ("Exc", n) with n > 0; its triangles' area sums to the face area (1e-6)

def test_excitation_face_shared_by_two_copies_counts_once(self):
    # excitation face: the radial face at 45°, r 10..20, z 0..10, between the inner cell and its mirrored copy
    ...  # returncode 0; the group's area equals the face's area once (not twice)

def test_excitation_face_not_split_by_the_cell_is_refused(self):
    # excitation face: top face of outer sector 20..30, 0..30° (ends inside a copy)
    ...  # returncode != 0; "excitation Exc" in stderr and "cover" in stderr

def test_excitation_lines_are_reported(self):
    ...  # a "SMAT_ID    101  Exc" line in stdout
```

- [ ] **Step 2: Run them to verify they fail**
  Run: `pixi run -e addon pytest tests/freecad_addon/test_meshsym3d.py -k excitation -v`
  Expected: FAIL (no excitation group written).

- [ ] **Step 3: Implement `_land_surfaces(sides, folder, dim) -> labels` and the surface copy in `_copy`.**
  For each cell boundary face entity (dim 2) and each transform: move 3 element centres; the patch lands on an
  excitation face when all lie on it (`getClosestPoint(2, f, …)` within tol, and inside its bounds). A patch landing on
  no excitation face is not copied as a surface. Dedupe: a landed patch is keyed by the sorted node coordinates
  after the transform (rounded to tol); a key seen before (the shared face of two copies) is neither copied twice
  nor counted twice. Coverage per excitation face: the landed patches' areas add up to the face's area (1e-6
  relative), else
  `JobError(f"excitation {name}: the copies of the cell cover {got:.6g} of the {area:.6g} mm² of {file}; the cell must be split where the face ends")`.
  Copied surface entities share the copied volume nodes (same offsets), so `removeDuplicateNodes` joins them; mirrored
  surface copies are reversed with the volumes.

- [ ] **Step 4: Run the tests and the whole add-on suite**
  Run: `pixi run -e addon pytest tests/freecad_addon/test_meshsym3d.py -v`, then `pixi run -e addon test-addon`
  Expected: all PASS.

- [ ] **Step 5: Format, lint, commit** "Symmetric mesh: copy excitation surfaces in 3D".

---

### Task 3: 3D sliding motion on the cylinder

**Files:**
- Modify: `freecad_addon/emsolution/meshsym.py`
- Test: `tests/freecad_addon/test_meshsym3d.py`

**Interfaces:**
- Consumes: Tasks 1–2.
- Produces (job format): `job["symmetric"]["slide"] = {"name", "kind": "rotational", "radius", "divisions",
  "cross_divisions", "slide_mat_id", "full": True}`; `job["rotor_file"]`. Output: fixed side to `mesh_file`, moving
  side to `rotor_file`; the moving file holds a dim-1 physical group `slide_mat_id` of line elements along the 0°
  generatrix of the cylinder (the marker), as 3D sliding writes now.

- [ ] **Step 1: Write the failing tests.** Two-side job: fixed cell r 20..30, moving cell r 10..20, both 0..45°,
  z 0..10, `chain(45, 90, 4)`, slide R 20, divisions 16, cross_divisions 4. Add `slide_nodes(msh, r) -> set` (rounded
  coordinates of nodes on the cylinder) to the test file.

```python
def test_sliding_sides_have_the_same_nodes_on_the_cylinder(self):
    ...  # returncode 0; slide_nodes(fixed) == slide_nodes(rotor); len == 16 * (4 + 1)

def test_marker_line_is_on_the_moving_side_only(self):
    ...  # rotor file has dim-1 group slide_mat_id with 4 line elements at angle 0, r 20; fixed file has none

def test_divisions_off_the_grid_are_refused(self):  # divisions 12: a 45° cell arc gets 1.5
    ...  # returncode != 0; "whole number" in stderr

def test_side_short_of_the_cylinder_height_is_refused(self):  # moving cell z 0..8, fixed z 0..10
    ...  # returncode != 0; "moving side" in stderr and "cylinder" in stderr

def test_z_cut_off_the_cross_grid_is_refused(self):  # fixed cell split at z = 3 (2 solids), cross_divisions 4
    ...  # returncode != 0; "cross_divisions" in stderr
```

- [ ] **Step 2: Run them to verify they fail**
  Run: `pixi run -e addon pytest tests/freecad_addon/test_meshsym3d.py -k "sliding or marker or divisions or cylinder or cross" -v`
  Expected: FAIL with "3D sliding is not supported yet".

- [ ] **Step 3: Implement the cylinder forms:** `_slide_faces_sym(slide, sides)` (3D twin of `_slide_arcs`),
  `_on_cylinder(slide, sides, split)` (twin of `_on_circle`), `_marker_line(slide)` (twin of `_marker`); `_mesh` calls
  the 2D or 3D one by `dim` and the "not supported" error goes.
  - Cylinder faces of a side's cells: boundary faces whose corner and sample points all lie at radius R (tol
    1e-6 R). Height range of the cylinder = z range of all sides' cylinder faces together; every side's faces must
    cover it at every angle of its cell (sum of face areas = 2π R / copies × height), else
    `sliding interface {name}: the cells of the {side} side do not reach over the whole cylinder (radius R, z z0..z1)`.
  - Arcs: share of `divisions` as in 2D (`whole number`, ends on the `360 / divisions` grid from 0°). Lines along z:
    `cross_divisions × length / height` elements; every z cut must be on that grid, else
    `sliding interface {name}: a cut at z = {z:g} is off the grid of {cross_divisions} cross_divisions over z z0..z1`.
  - `setTransfiniteSurface` on each cylinder face with `"Left"` and corners in the same order as `_slide_faces` in
    `meshcommon.py` (reuse its corner ordering helper if it can be called per face; otherwise copy its rule).
  - `_on_cylinder`: each side has exactly `divisions × (cross_divisions + 1)` nodes on the cylinder, one at each grid
    point; nodes only (spec §6).
  - `_marker_line`: line elements between consecutive nodes at angle 0 on the cylinder, a discrete dim-1 entity on the
    moving side, physical group `slide_mat_id`.
  - `run` writes per side with `write_split` as in 2D, adding the dim-1 marker group to the moving side and each
    side's excitation groups.

- [ ] **Step 4: Run the tests and the whole add-on suite**
  Run: `pixi run -e addon pytest tests/freecad_addon/test_meshsym3d.py -v`, then `pixi run -e addon test-addon`
  Expected: all PASS.

- [ ] **Step 5: Format, lint, commit** "Symmetric mesh: 3D sliding on the cylinder".

---

### Task 4: Study rules for 3D symmetric Studies

**Files:**
- Modify: `freecad_addon/emsolution/symmetry.py` (error texts only)
- Modify: `freecad_addon/emsolution/objects.py` (`surface_keys`, `SlidingInterface.execute`, piece helpers)
- Modify: `freecad_addon/emsolution/validation.py` (`_symmetric`, `_overlaps`, `_pieces`, `_moved`, `_links`)
- Modify: `tests/freecad_addon/symcases.py` (3D fixture)
- Create: `tests/freecad_addon/test_symmetric_study3d.py`

**Interfaces:**
- Produces: `symcases.motor_doc_3d(doc, height=10)` (motor_doc's cell faces extruded `0..height` as solids; same
  chains) and `symcases.motor_study_3d(doc)` (3D Study, sliding, R 35, Divisions 144, CrossDivisions 2, Materials
  on `SolidN` pieces grouped by `_piece_name` of each solid's centre, and one Excitation `Coil01Ends` on the two
  z = height faces of Coil01's solids).
- Produces: `objects.piece_kind(study) -> "Face" | "Solid"` (2D → "Face", 3D → "Solid"); `objects.surface_keys`
  in a symmetric 3D Study keys excitations on Symmetric Mesh tops (`f"{e.Name}|{top.Name}"`).
- Produces: `SlidingInterface.execute` in a symmetric 3D Study sets `Shape` to the cylinder face of `Radius` over
  the z range of the Study's tops.

- [ ] **Step 1: Write the failing tests** in `test_symmetric_study3d.py` (fixture `motor3d` like `motor` in
  `test_symmetric_study.py`, reusing its `_texts` / `_has` helpers by import):

```python
def test_motor_3d_validates_clean(motor3d): assert _texts(motor3d) == []
def test_chain_reads_24_and_16_copies_of_solids(motor3d): ...  # Steps and Cells as in 2D; cells have Solids
def test_mirror_error_does_not_say_2d(motor3d): ...  # a z-tilted Normal: message has "contain the Z axis", not "2D"
def test_cell_body_that_is_a_face_is_refused(motor3d): ...  # replace CoilCell's shape by a face: "has no solid"
def test_overlap_is_measured_by_volume(motor3d): ...  # coil 10..17° solid: "overlaps a mirrored copy", "mm³", z shown
def test_solid_without_material_is_an_error(motor3d): ...  # delete Coil05: "Pieces with no Material: StatorFragments.Solid"
def test_excitation_on_a_top_gets_a_smat_id(motor3d): ...  # update_ids: SmatIds has f"{exc.Name}|{top.Name}"
def test_excitation_on_a_cell_body_is_refused(motor3d): ...  # "pick the faces on the drawing"
def test_sliding_interface_shape_is_the_cylinder(motor3d): ...  # one face, radius 35, z 0..10
def test_divisions_must_fit_the_copy_count_3d(motor3d): ...  # Divisions 100: "multiple of the 24 copies"
def test_2d_motor_still_validates_clean(motor): ...  # imported fixture from test_symmetric_study
```

- [ ] **Step 2: Run them to verify they fail**
  Run: `pixi run -e addon pytest tests/freecad_addon/test_symmetric_study3d.py -v`
  Expected: FAIL ("A Symmetric Mesh needs a 2D Study in the XY plane.").

- [ ] **Step 3: Implement.**
  - `symmetry.py`: both mirror messages become `the mirror plane must contain the Z axis`.
  - `validation._symmetric`: the plane check refuses only a 2D Study not in XY
    (`A Symmetric Mesh needs a 3D Study or a 2D Study in the XY plane.`); cells need `Shape.Solids` in 3D
    (`cell body X has no solid; a cell body must be a solid …`, the Fragments advice with "solid" for "face").
  - `_overlaps`: in 3D compare `common.Volume` against `1e-6 * min(volumes)`; message unit `mm³`, point
    `(x, y, z)` from the largest solid of `common`.
  - `_pieces` / `_moved`: `objects.piece_kind(study)` replaces the literal `"Face"` / `Shape.Faces`
    (`Shape.Solids` in 3D).
  - Excitations: `_links` already checks them in 3D; add in `_symmetric`: an excitation reference on a cell body →
    `Excitation {label} refers to {cell}: copies are not where it is drawn. Pick the faces on the drawing.`
  - `objects.surface_keys`: `included` = tops of Symmetric Mesh items when symmetric.
  - `SlidingInterface.execute`: 3D symmetric → `Part.makeCylinder(R, h, V(0, 0, z0)).Faces[0]` (the side face) from
    the tops' bound box; 2D unchanged.

- [ ] **Step 4: Run the tests and the whole add-on suite**
  Run: `pixi run -e addon pytest tests/freecad_addon/test_symmetric_study3d.py tests/freecad_addon/test_symmetric_study.py -v`, then `pixi run -e addon test-addon`
  Expected: all PASS.

- [ ] **Step 5: Format, lint, commit** "Symmetric Study: 3D validation, solids as pieces".

---

### Task 5: Job writer and end-to-end 3D mesh

**Files:**
- Modify: `freecad_addon/emsolution/jobwriter.py` (`write_job`, `write_symmetric`, `check`)
- Test: `tests/freecad_addon/test_symmetric_study3d.py`

**Interfaces:**
- Consumes: Task 4 (`motor3d` fixture, `surface_keys`), Tasks 1–3 job format.
- Produces: a 3D symmetric `job.json` exactly in the Task 1–3 format: `volumes` = cell bodies (local ids), `surfaces`
  = `[]`, pieces exported per `SolidN`, side `excitations` from the Excitations whose references are on that side's
  top (one file per face, SMAT_ID from `study.SmatIds[f"{e.Name}|{top.Name}"]`), slide block with
  `cross_divisions`.

- [ ] **Step 1: Write the failing tests:**

```python
def test_job_3d_has_cells_solids_and_excitations(motor3d):
    ...  # "volumes" ids 1..6; job["surfaces"] == []; 24 / 16 transforms; pieces are solids (120 files);
         # fixed side excitations == [{"smat_id": …, "name": "Coil01Ends", "files": [2 files]}];
         # slide has cross_divisions == 2

def test_symmetric_3d_job_meshes_into_both_files(motor3d):
    ...  # mesher.py --check prints "CHECK OK"; run: returncode 0; MAT_ID groups of both files == piece ids;
         # SMAT_ID group of Coil01Ends in the fixed file only; slide nodes equal on both sides (r 35);
         # mesh_check_3d(…) inverted == 0 on both files; marker dim-1 group only in the rotor file
```

  Keep the fixture coarse (DefaultMeshSize 4, height 10) so the end-to-end test stays under ~60 s.

- [ ] **Step 2: Run them to verify they fail**
  Run: `pixi run -e addon pytest tests/freecad_addon/test_symmetric_study3d.py -k job -v`
  Expected: FAIL (pieces exported as faces / no excitations block).

- [ ] **Step 3: Implement.** In `check`, a symmetric Study returns `surfaces = []` (its excitations go to the
  symmetric block). In `write_symmetric`, pieces iterate `SolidN` subs in 3D (unchanged code path, the sub names
  already come from `m.Pieces`); per side add `"excitations"` from `objects.excitations(study)` refs on that side's
  top via `export_subs(folder, top, faces, f"exc_{smat_id}")`; add `cross_divisions` when 3D. `write_job` already
  writes `volumes` for 3D; check it does not write `job["surfaces"]` entries for symmetric Studies.

- [ ] **Step 4: Run the tests and the whole add-on suite**
  Run: `pixi run -e addon pytest tests/freecad_addon/test_symmetric_study3d.py -v`, then `pixi run -e addon test-addon`
  Expected: all PASS.

- [ ] **Step 5: Format, lint, commit** "Symmetric Study: write and mesh 3D jobs".

---

### Task 6: Picking solids in the Material panel (GUI)

**Files:**
- Modify: `freecad_addon/emsolution/objects.py` (pure helper)
- Modify: `freecad_addon/emsolution/taskpanels.py` (`MaterialPanel.__init__`, `picks`, hint text)
- Modify: `freecad_addon/emsolution/commands.py` (`AddMaterial.Activated`: face picks on a top become solids in 3D)
- Modify: `tests/freecad_addon/gui_smoke.py`
- Test: `tests/freecad_addon/test_symmetric_study3d.py`

**Interfaces:**
- Produces: `objects.piece_solid(shape, face: str, picked: App.Vector | None, view_dir: App.Vector | None) -> str | None`:
  the `SolidN` of `shape` that has `face`; for a face of two solids, the one containing `picked + view_dir * eps`
  (eps = 1e-4 × the shape's bound-box diagonal); `None` when the face has two solids and `picked` or `view_dir` is
  `None` or neither solid contains the point.
- Produces: `taskpanels.selected_piece_solids(study) -> list[tuple[body, str]]` for a 3D symmetric Study: each
  clicked face of a top as `(top, SolidN)`; for a `None` answer the panel asks with a choice of the two solids
  (`QInputDialog.getItem`, items `"SolidA"`, `"SolidB"`), and skips the pick on Cancel.

- [ ] **Step 1: Write the failing headless tests** for `piece_solid` on the `motor3d` StatorFragments:

```python
def test_outer_face_gives_its_solid(motor3d): ...  # the iron's outer cylinder face -> the iron solid's SolidN
def test_shared_face_gives_the_solid_behind_it(motor3d):
    ...  # a coil/iron wall face, picked point on it, view_dir pointing into the coil -> the coil's SolidN
def test_shared_face_without_a_view_is_undecided(motor3d): ...  # picked None -> None
```

- [ ] **Step 2: Run them to verify they fail**
  Run: `pixi run -e addon pytest tests/freecad_addon/test_symmetric_study3d.py -k solid -v`
  Expected: FAIL (`piece_solid` not defined).

- [ ] **Step 3: Implement `piece_solid`, then the panel.** `MaterialPanel`: in a 3D symmetric Study the gate stays
  `("Face",)`, `picks()` uses `selected_piece_solids`, the list shows `SolidN`, the hint reads
  `Click a face of each solid of the drawing in the 3D view; its solid is taken.`, and `owned_text` says "solid".
  Picked points come from `Gui.Selection.getSelectionEx()[i].PickedPoints`, the view direction from
  `Gui.ActiveDocument.ActiveView.getViewDirection()`. `AddMaterial.Activated` turns top face picks into solids the
  same way before opening the panel. 2D unchanged.

- [ ] **Step 4: Extend the GUI smoke test** after the 2D Symmetric Mesh block: build `symcases.motor_study_3d` in a
  new document; select `StatorFragments` `Face1` (an outer face) and run `EMS_Material`; assert the panel's
  `current` is `[(top, "SolidK")]` for the solid that has Face1; accept with a new name; assert the assignment's
  `Pieces` holds that solid. Then run the smoke test:
  `pixi run -e addon freecad tests\freecad_addon\gui_smoke.py` and read the last line of `%TEMP%\ems_gui_smoke.txt`.
  Expected: `PASS`.

- [ ] **Step 5: Run the whole add-on suite**
  Run: `pixi run -e addon test-addon`
  Expected: all PASS.

- [ ] **Step 6: Format, lint, commit** "Material panel: pick solids of a 3D symmetric drawing".
