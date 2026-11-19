# Swept Body, Stage 4: Symmetric Studies — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A Swept Body works on the cell objects of a Symmetric Group in 3D. The cell is swept once and copied like
any other cell, and the air is meshed around the copies. The stage's review rows are litz1 as a whole (6 strands,
the strand as the cell) and a winding sector as a cell.

**Architecture:** A cell job is already a normal body job (`jobwriter._group_entry` calls `_body_job`, which writes
`job["swept"]`). It is built and generated in a model of its own (`meshgroups.mesh_cell`), copied by
`meshfrozen.copy_mesh`, and the free side (Air Region, free objects) is meshed around the frozen copies, with
`meshfrozen.quad_pyramids` on their quad faces. Transfinite Body cells already go this way. So Stage 4 is mostly
four things:
- **Validation:** let the cells through.
- **Real surface of a swept cell:** in the cell model nothing lies beyond the cell, so the faces toward the free
  side must come from the job (`validation.free_faces`), as they already do for Skin Layer faces of cells.
- **Seams with copies:** faces a swept cell shares with its own copies are already conformal by construction,
  because both ends are the same section, moved. They must not be re-meshed or made periodic by gmsh over the hand
  mesh.
- **Refusals:** the cases a structured cell is refused for (an extra vertex on an edge, a split) also refuse a swept
  cell.

The spike (Task 1) checks this on the two real cases before anything is built.

**Tech Stack:** FreeCAD 1.1 add-on (Python 3.11), gmsh 4.15.2, numpy, pytest via pixi.

**Spec:** `docs/superpowers/specs/2026-11-17-swept-body-prism-layers-design.md` (sections 2, 4, 8 Stage 4, 11 calls
9 and 10). Stages 1–3: plans `2026-11-17-swept-body-stage1.md` to `-stage3.md`, branch `freecad/swept-body`, tip
`6c3a914`.

## Global Constraints

- Everything through pixi:
  - `pixi run -e addon test-addon`
  - `pixi run -e addon pytest tests/freecad_addon/<file> -k <name>`
  - `pixi run lint`
  - `pixi run format`, then revert its change to `highlight.py`.
- Branch `freecad/swept-body` (continue). Commit per task, never `--no-verify`, never push or merge.
- Ruff:
  - line length 120, double quotes;
  - no trailing comma on a construct that fits on one line;
  - never reorder imports;
  - format only files you changed.
- Module rules:
  - mesher modules never import FreeCAD;
  - `sweeps.py`, `jobwriter.py` and `validation.py` stay GUI-free.
- Unchanged meshes:
  - A Study without a Swept Body meshes exactly as before.
  - An ordinary Study (no Symmetric Groups) with a Swept Body meshes exactly as at `6c3a914`.
  - `test_straight_sweep_unchanged_by_stage2` and the Stage 2 and 3 mesher tests stay green.
- **Spec call 9:** in a Study with Symmetric Groups, Swept Body applies to cell objects only. A free object in a
  Swept Body is refused.
- **Real surface of a swept cell:** its faces toward the free side, `validation.free_faces(study, group, body)`.
  - The side curves of the section get the skin only where their side face is one of these faces.
  - An end is graded only when its end face is one of them (and not shared with a skinned body, Stage 1's rule).
  - A seam with a copy, or a cut of the domain, is neither skinned nor graded.
- **Exact texts.** Use these where validation or the mesher refuses or warns:
  - free object: `"Swept Body {item}: {name} is a free object; in a Study with Symmetric Groups only cell objects are swept."`
  - vertex on an edge: `"group {group}: the swept cell {name} would need a mesh node on its edge where an edge of a copy ends on it; meshing that is not handled yet, a limit of the tool, not of the drawing"`
  - split: `"group {group}: the swept cell {name} would have to be split where a copy touches part of its face; meshing that is not handled yet, a limit of the tool, not of the drawing"`
  - seam that does not pair the sweep's own sections (only if the spike keeps this case refused): `"group {group}: the swept cell {name} meets a copy on a face whose mesh the copy cannot share; meshing that is not handled yet, a limit of the tool, not of the drawing"`
  - The text `"Studies with Symmetric Groups are not swept yet."` is retired.

## Review Focus

- **An Excitation on a swept cell's end face** (litz1's strand ends). The group's excitation patches (`meshsym._cell_patches`, `_land_surfaces`) must land on the copied swept mesh's end quads in every copy. The test goes in Task 4.
- **A group with mirror transforms.** A swept cell copied by a mirror must keep positive hexahedra and prisms (`meshfrozen.FLIP`). Its seam with the mirrored copy must be refused when the section is not mirror-symmetric, or be conformal. The test goes in Task 4.
- **A Swept Body that picks both a cell and a free object.** The cell is swept, the free object is refused with the exact text, and nothing is half-written to the job. The test goes in Task 2.
- **The free air around many swept copies** (6 strands, 8 sectors). It must have no free faces inside and no element with SICN ≤ 0; the min SICN is printed. The checks go in the Task 6 rows.
- **An ordinary Study with a Swept Body.** It must mesh as at `6c3a914` (node checksum). The test goes in Task 4.

---

### Task 1: Spike — swept cells in symmetric Studies

**Files:**
- Scratch only, in the session scratchpad. Record the result as a "Stage 4" paragraph at the end of spec 7.1
  (uncommitted, like the Stage 1–3 spike notes).

**Interfaces:**
- Produces: the decisions Tasks 2–4 branch on:
  - (S) seams: leave a swept cell's faces out of `meshsym._periodic` and `pair_images` (preferred), or let gmsh pair
    them;
  - (M) mirror seams: conformal as built, or refused with the seam text;
  - (P) the free-side air beside swept copies meshes with `quad_pyramids` as for Transfinite Body cells (yes/no).

- [ ] **Step 1: Bypass validation's grouped refusal in a scratch copy.** Take a scratch copy of the job, written by
  hand or by `write_job` with the refusal patched in memory, not in the repo. Mesh two cases:
  - **litz1:** open `C:\Users\hamed\Desktop\delme\litz\litz1.FCStd` from a temporary copy, never saving the
    original. Put a Swept Body on the strand cell, with a Skin Layer at 100 kHz and Layer Depth 2 δ.
  - **A 45° sector of a ring:** a 2 × 4 rectangle (radial × axial) at rc 20, revolved 45° about z, as the cell of a
    group of 8 rotations, with a Skin Layer at 10 kHz, in a Padding Box air.
- [ ] **Step 2: Record for each case:**
  - whether the cell meshes;
  - whether the copies join, with the number of free faces inside;
  - whether the air around the copies meshes, with its min SICN;
  - where gmsh touches the hand mesh on seams (periodic or images);
  - which faces the cell model sees as real (expected: all of them, which is wrong; Task 3 fixes it).
- [ ] **Step 3: Mirror.** Try the sector with a mirror group (4 rotations × mirror), if the group editor allows it in
  a script. Record (M).
- [ ] **Step 4: Stop rule.** If the air around swept copies cannot be made conformal by either seam choice, stop.
  Report this to the controller; the user decides, as for the Stage 1 spike.

### Task 2: Validation — swept cells allowed, free objects refused

**Files:**
- Modify: `freecad_addon/emsolution/validation.py` (`_swept_bodies` and its contact checks)
- Test: `tests/freecad_addon/test_study.py`

**Interfaces:**
- Consumes: `objects.is_grouped`, `objects.cell_bodies`, `_is_free(study, body)`.
- Produces: in a grouped 3D Study, a Swept Body on cell objects passes Validate. Its contact rule is checked as
  follows:
  - Seams with copies of the same group are allowed.
  - Other contacts follow Stage 1: air and unstructured bodies, whole faces.
  - The cell's neighbours are its other cell objects, the free side (the Air Region, free objects) and copies of
    other groups.

- [ ] **Step 1: Write the failing tests:**
  - `test_swept_cell_validates`: a grouped Study (the sector group of Task 1, built with the existing group test
    helpers in `test_study.py`) with a Swept Body on the cell has no Swept Body error.
  - `test_swept_free_object_refused`: the same Study with a free bar in the Swept Body gets exactly the free-object
    text. The cell in the same item gets no error.
  - `test_swept_cell_touching_part_of_a_copy`: a cell touched by a copy of another group over part of a face gets
    Stage 1's partial-contact text.
- [ ] **Step 2: Run them.** Expected: FAIL, with "Studies with Symmetric Groups are not swept yet."
- [ ] **Step 3: Implement.**
  - Drop the grouped refusal.
  - Refuse free objects (`_is_free`) with the exact text.
  - Run the contact check against the cell's neighbours. The faces toward its own copies are seams; they are
    allowed, and `meshgroups` checks them.
- [ ] **Step 4: Run** `pixi run -e addon pytest tests/freecad_addon/test_study.py -k swept`. Expected: PASS.
- [ ] **Step 5: Commit** `FreeCAD add-on: Swept Body on the cells of a Symmetric Group`.

### Task 3: Jobwriter — a swept cell's real faces

**Files:**
- Modify: `freecad_addon/emsolution/jobwriter.py` (`swept_entries`, `_group_entry`, `swept_names`)
- Test: `tests/freecad_addon/test_study.py`

**Interfaces:**
- Consumes: `validation.free_faces(study, group, body)`, `export_subs` (it maps faces onto a rebuild).
- Produces: in a cell job, each swept entry has `"free_faces": [relative BREP paths]`, the cell's faces toward the
  free side. The files are named `geometry/<prefix>swept_free_<MAT_ID>_<n>.brep`. Ordinary jobs have no
  `"free_faces"` key, so their job is unchanged.
  - `swept_entries(study, folder, ids, found, prefix="", group=None)`: with `group`, it writes `free_faces`.
  - `swept_names(study, found=None)`: with `found`, it returns only the bodies that got a swept entry. This is the
    Stage 1 parked finding: a body skipped by `swept_entries` keeps its Skin Layer entry.

- [ ] **Step 1: Write the failing tests:**
  - `test_swept_cell_job_has_free_faces`: the sector cell's entry lists its free faces, which are the inner, outer,
    top and bottom faces (4 files). The two cut faces toward the copies are not among them.
  - `test_swept_entry_unchanged_outside_groups`: an ordinary Study's swept entry has no `free_faces`.
  - `test_skin_kept_for_unswept_body`: a body in a Swept Body item that `swept_entries` skipped keeps its `skin`
    entry.
- [ ] **Step 2: Run them.** Expected: FAIL.
- [ ] **Step 3: Implement.** Pass `group` from `_group_entry` through `_body_job` to `swept_entries`.
- [ ] **Step 4: Run** `pixi run -e addon pytest tests/freecad_addon/test_study.py -k "swept or skin"`. Expected:
  PASS.
- [ ] **Step 5: Commit** `FreeCAD add-on: a swept cell's faces toward the free side go to its job`.

### Task 4: Mesher — swept cells, seams and refusals

**Files:**
- Modify:
  - `freecad_addon/emsolution/meshsweep.py` (`apply_swept`, `_graded_end`)
  - `freecad_addon/emsolution/meshgroups.py` (`prepare_images`, `mesh_cell`)
  - `freecad_addon/emsolution/meshsym.py` (`_periodic`), if decision (S) needs it
- Test: `tests/freecad_addon/test_mesher.py`, `tests/freecad_addon/test_meshsweep.py`

**Interfaces:**
- Consumes: the `"free_faces"` files of Task 3 and the spike's (S), (M) and (P).
- Produces:
  - **Real surface.** When an entry has `"free_faces"`, the real faces of its volume are the faces matching those
    files. Match them the way `mesher._whole_faces` does: centre of mass, area and bounding box within TOL × size.
    These faces replace `real_boundary` and `_graded_end`'s adjacency test for that entry. Without the key,
    behaviour is unchanged.
  - **Seams.** By (S), the faces of a swept cell are left out of the periodic and image pairing. The hand mesh
    already matches across seams.
  - **Refusals.**
    - Swept MAT_IDs join `structured` in `prepare_images`, so the vertex and split cases refuse with the exact
      swept texts.
    - A cell model whose seam with a copy does not map one end section onto the other (or a side onto itself) is
      refused with the seam text, if (M) says so.

- [ ] **Step 1: Write the failing tests:**
  - `test_swept_sector_cell_is_conformal`: the 8-sector ring as a group job (a mesher-level job written by hand, as
    the existing group tests in `test_mesher.py` do). Assert:
    - every element of the cell copies is a hexahedron;
    - no free faces inside;
    - no element with SICN ≤ 0;
    - the cut faces carry no skin grading: the first step along the path is the plain size step;
    - the outer face gets the skin's first layer, 0.66 / ElementsPerDepth.
  - `test_swept_strand_cell_copies`: a helical strand cell with 6 rotation copies in air. Assert hexahedra and
    prisms in all 6, the air conformal, and min SICN > 0.
  - `test_swept_cell_excitation_on_every_copy`: an excitation on the strand cell's end face lands on the end quads
    of all 6 copies.
  - `test_swept_mirrored_cell`: by (M), either a conformal mesh with positive volumes, or the seam text.
  - `test_swept_cell_needing_a_vertex_is_refused`: a cell whose copy's edge ends on its edge gets the vertex text.
  - `test_ordinary_swept_unchanged_by_stage4`: the SW-01 busbar job gives node coordinates identical to a checksum
    recorded at `6c3a914`. Record the checksum before changing code.
- [ ] **Step 2: Run them.** Expected: FAIL, except the unchanged checksum, which passes before and after.
- [ ] **Step 3: Implement**, as described in Produces.
- [ ] **Step 4: Run** `pixi run -e addon pytest tests/freecad_addon/test_mesher.py tests/freecad_addon/test_meshsweep.py -k swept`.
  Expected: PASS, with the Stage 1–3 tests still green.
- [ ] **Step 5: Commit** `FreeCAD add-on: swept cells in the symmetric mesher`.

### Task 5: Stage 3 leftovers

The final review of Stage 3 asked for these tests. A test that fails shows a bug: fix it in the module the test
names.

**Files:**
- Test: `tests/freecad_addon/test_mesher.py`, `tests/freecad_addon/test_study.py`
- Modify: only if a test fails.

- [ ] **Step 1: Add the tests:**
  - `test_swept_left_handed_helix`: a strand on a left-handed helix (negative advance) meshes conformally. Its
    steps sum to the path length.
  - `test_swept_end_against_terminal_with_excitation`: a busbar's end face shared whole with a tetrahedral terminal,
    with an excitation on that shared face. The excitation lands on the shared face. The mesh is conformal, with no
    pyramid fallback note.
  - `test_standard_coil_with_leads_rebuilt`: a non-Frenet round coil with straight leads (line + 2-turn helix +
    line), built with `test_sweeps.helix_pipe` and Part pipes. It is rebuilt and recognised as 3 pieces, its job
    meshes, and an excitation on a lead's end face lands.
- [ ] **Step 2: Run them.** Fix in place what fails, with the failing test first.
- [ ] **Step 3: Commit** `FreeCAD add-on: tests for left-handed helices, terminals and coils with leads`.

### Task 6: The Stage 4 review catalogue rows

**Files:**
- Modify: `experiments/refinement_catalogue/rows.py`

**Interfaces:**
- Consumes: the whole add-on and the SW helpers (`bar_study`, `skin`, `ring_text`, `sw_report`, `strand_study`,
  `litz1_strand`).
- Each row prints:
  - per-part counts, today (graded Skin Layer cells) against new;
  - the air's min SICN and the count below 0.1;
  - free faces inside;
  - the number of copies meshed.

| id | Study | Items | after-check |
|---|---|---|---|
| SW-S1 | litz1 whole: `C:\Users\hamed\Desktop\delme\litz\litz1.FCStd`, opened from a temporary copy, nothing saved back; its group of 6 strands as built | Skin Layer 100 kHz, Layer Depth 2 δ; Swept Body on the strand cell | 6 copies of hexahedra + prisms; no free faces inside; air min SICN > 0; litz1's excitations (if any) land on every strand end |
| SW-S2 | winding sector: 2 × 4 rectangle at rc 20, 45° sector cell, 8 rotations, Padding Box air, size 1 | Skin Layer 10 kHz; Swept Body on the cell | hexahedra only; no free faces inside; skin on the inner, outer, top and bottom faces only; no grading at the cut faces |
| SW-S3 | the SW-S2 Study plus a free bar in the same Swept Body | as SW-S2 | Validate prints the free-object text; the cell is still swept |

- [ ] **Step 1: Add the rows.** Run `pixi run -e addon python experiments/refinement_catalogue/build_catalogue.py --only SW-S1 SW-S2 SW-S3`.
  Expected: all match.
- [ ] **Step 2: Look at every new picture.** A cut across the strands and a cut through a sector seam must show the
  swept mesh in every copy.
- [ ] **Step 3: Run the whole catalogue in the background.** Expected: every row matches, 54 + 3.
- [ ] **Step 4: Commit** `Refinement catalogue: Stage 4 rows (swept cells)`.

### Task 7: Stage 4 check and hand-over

- [ ] **Step 1: Run** `pixi run -e addon test-addon` (all pass) and `pixi run lint` (clean). There are no GUI
  changes, so no smoke test is needed. If a GUI file changed, run the smoke test as AGENTS.md says.
- [ ] **Step 2: Hand over** the catalogue with SW-S1 to SW-S3 and the spike's decisions (S), (M) and (P).
- [ ] **Step 3: Stop.** Don't merge or push. The user reviews the rows before Stage 5 (spike 7.2, 3D prism layers)
  is planned.
