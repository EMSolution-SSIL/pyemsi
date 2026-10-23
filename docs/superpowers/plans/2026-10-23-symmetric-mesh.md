# Symmetric Mesh (2D) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A 2D Study can mesh only a cell and copy that mesh by the Mirror / Polar Array objects that built the full
geometry. Every copy takes the MAT_ID of the Material on the piece (face) it lands on.

**Architecture:**
- **FreeCAD side.** `symmetry.py` reads the transforms from the object chain. `objects.py` gets a `SymmetricMesh`
  item and Materials on pieces. `validation.py` gets the new rules. `jobwriter.py` writes a cell job: the cell bodies
  with local ids, so the existing `mesher2d.build` meshes the cell unchanged, plus a `"symmetric"` block (transforms,
  pieces, slide).
- **Mesher side.** `meshsym.py` (no FreeCAD) meshes the cell with `build`, finds which piece each copy lands on, copies
  the mesh, and writes the same files as today. It reuses `write_split` for the fixed and moving sides.

**Tech Stack:** Python 3.11, FreeCAD 1.1.0 (Part, Draft, BOPTools), gmsh 4.15.2, pytest, Pixi.

**Spec:** `docs/superpowers/specs/2026-10-23-symmetric-mesh-design.md`. The prototypes it cites are in `experiments/`
(not committed); `experiments/gmsh_symmetry/motor_cell.py::copy_mesh` and `experiments/symmetric_spike/` are the
reference for Tasks 1 and 5.

## Global Constraints

- **Running things:** run everything through Pixi.
  - Add-on tests: `pixi run -e addon test-addon`. The baseline is 400 passing; it must stay green.
  - Format: `pixi run format`. Lint: `pixi run lint`.
- **Code style:** Ruff, line length 120. Never reorder imports. Mark side-effect imports with `# noqa: F401 - <reason>`.
- **Process boundaries:**
  - `meshsym.py`, `mesher2d.py` and `meshcommon.py` run in the mesher process and must never import FreeCAD.
  - `symmetry.py`, `objects.py`, `validation.py` and `jobwriter.py` contain no GUI code.
  - GUI code lives in `commands.py` and `taskpanels.py`.
- **GUI changes (Task 6)** also need the smoke test: `pixi run -e addon freecad tests\freecad_addon\gui_smoke.py`,
  then the last line of `%TEMP%\ems_gui_smoke.txt` must be `PASS`.
- **v1 scope (spec §2, §6, §8):**
  - 2D only, XY plane only, mirror and rotation steps only.
  - No Air Region in a Study with a Symmetric Mesh.
  - Sliding Interfaces must be Rotational, full turn, marker at 0°.
- **This plan narrows spec §8 ("at least one item per side"):** v1 allows **exactly one Symmetric Mesh item per side**.
  The side's Main (or Moving) geometry must be exactly that item's top object. Several items on one side would need
  copies of different cells to share nodes, which nothing here builds.
- **Transforms:** 4×4 affine, row major, 16 floats: the form gmsh's `setPeriodic` takes and the experiments use.
  Positions are global, in mm.
- **Material on pieces:** an assignment with pieces gets one MAT_ID, keyed in `MatIds` by the assignment's `Name`. Its
  group name is `volume_name(assignment)`, from the assignment's Label, which is the name the user typed.

## Review Focus

1. **The user changes the array count after assigning pieces.** Face numbers shift. Validate Study must list the
   pieces that have no Material, or two of them, and never raise. (Test in Task 3.)
2. **A body in the chain is deleted, or `Top` is empty.** Validation must give an error on the item, not a traceback.
   (Test in Task 3.)
3. **The whole drawing is moved:** a Placement on the array or the Fragments object. The transforms must still be
   right, so the coverage check passes and the mesh lands on the drawing. (Test in Task 1.)
4. **A Study without sliding motion and one Symmetric Mesh item** must mesh into one `.msh` with no `rotor_file`.
   (Test in Task 7.)
5. **Main geometry holding the top object plus one ordinary body** must be refused with a clear message, because v1
   cannot mix them. (Test in Task 3.)

---

### Task 1: Read the copy transforms from the FreeCAD objects

**Files:**
- Create: `freecad_addon/emsolution/symmetry.py`
- Create: `tests/freecad_addon/symcases.py`, the shared fixture: the spike motor as FreeCAD objects
- Test: `tests/freecad_addon/test_symmetry.py`

**Interfaces:**
- Produces:
  - `symmetry.SymmetryError(Exception)`.
  - `symmetry.read_chain(top) -> tuple[list, list[list[float]]]`: (cell bodies in first-seen order, transforms). The
    identity comes first.
  - `symmetry.apply(m, p) -> list[float]`, the point p (x, y, z) moved by m.
  - `symmetry.det(m) -> float`, the 3×3 determinant.
  - `symcases.motor_doc(doc) -> dict` builds the spike's geometry in `doc` and returns
    `{"stator_cells": [...], "rotor_cells": [...], "stator_top": obj, "rotor_top": obj}`.
    - Stator cell, 0..15°: `StatorIronCell` (r 36..60 minus the half slot), `CoilCell` (r 37..50, 10..15°),
      `StatorAirCell` (r 35..36).
    - Rotor cell, 0..22.5°: `RotorIronCell` (r 10..30), `MagnetCell` (r 30..34, 4.5..22.5°), `RotorAirCell`
      (r 30..35 minus the magnet).
    - Chain: `Part::Compound` → `Part::Mirroring` (normal ⟂ to the 15° / 22.5° line) → `Part::Compound`(cell, mirror)
      → `Draft.make_polar_array(…, number=12|8, angle=360)` → `BOPTools.SplitFeatures.makeBooleanFragments`. The
      top is the Fragments object.
    - Port this from `experiments/symmetric_spike/build_doc.py::chain` without the Explode loop and the `Material`
      strings.

- [ ] **Step 1: Write the failing tests** in `test_symmetry.py`, using a new document per test:
  - `test_stator_chain_gives_24_copies_of_3_cells`: `cells == stator_cells` and `len(transforms) == 24`. The identity
    is first. Exactly 12 transforms have `det < 0`.
  - `test_copies_land_on_the_fragments`: for every cell face and transform, the moved centre of mass lies on a face of
    the top's shape (`distToShape < 1e-6`). Then sum the cell areas per top face they land on: the sums must equal the
    face areas (rel 1e-6).
  - `test_moved_drawing_still_lands` (Review Focus 3): set the polar array's `Placement` to a 10° turn about Z,
    recompute, and run the same landing check against the moved top.
  - `test_unknown_object_in_chain_is_refused`: put a `Part::Cut` between the compound and the array.
    `SymmetryError` names its Label and TypeId.
  - `test_leaves_with_different_copies_are_refused`: compound the stator cell compound with a body that is not
    mirrored. `SymmetryError` names that body.
  - `test_mirror_out_of_plane_is_refused`: a Mirroring normal `(0, 0, 1)` gives `SymmetryError`. So does an array
    `Axis` other than Z.

- [ ] **Step 2: Run them and check that they fail**

  Run: `pixi run -e addon pytest tests/freecad_addon/test_symmetry.py -q`
  Expected: FAIL, `ModuleNotFoundError: emsolution.symmetry`.

- [ ] **Step 3: Implement `read_chain` by recursion over the table in spec §4**
  - **Leaf:** any other `Part::Feature` that has no chain role → `[identity]`.
  - **Compound** (`Part::Compound`) → the union over `Links`.
  - **Mirroring** (`Part::Mirroring`) → `M ∘ t` for each `t` of `Source`. Build `M` from the global `Base` and
    `Normal`.
  - **Draft polar array** (`ArrayType == "polar"`) → `R(k·step) ∘ t`.
    - `step = Angle / NumberPolar` when `abs(Angle) == 360`, else `Angle / (NumberPolar - 1)`. Check this against
      Draft's own code in FreeCAD 1.1.
    - Rotate about `Center`. `Axis` must be ±Z and `IntervalAxis` zero.
  - **Boolean Fragments** (`BOPTools` FeaturePython with `Objects`) → the union over `Objects`.
  - **Placement:**
    - Compose every object's own `Placement` the way FreeCAD applies it to its shape. The landing tests decide
      whether this is right.
    - Dedupe the transforms per leaf (rounded to 1e-9), then require every leaf's set to be equal.
  - **Helpers:** port `rotation`, `mirror_line`, `compose`, `apply` and `det` from
    `experiments/gmsh_symmetry/motor_cell.py`.

- [ ] **Step 4: Run them and check that they pass**

  Same command. Expected: 6 passed.

- [ ] **Step 5: Format, lint, commit**

  ```bash
  pixi run format && pixi run lint
  git add freecad_addon/emsolution/symmetry.py tests/freecad_addon/symcases.py tests/freecad_addon/test_symmetry.py
  git commit -m "Symmetric mesh: read the copy transforms from Mirror and Polar Array objects"
  ```

### Task 2: Symmetric Mesh item, Materials on pieces, MAT_ID keys

**Files:**
- Modify: `freecad_addon/emsolution/objects.py`. Touches `Material` (line 210), `assignment_label` (716),
  `sync_labels` (751), `is_item` / `item_refs` (892–905), `_size_text` (961), `material_rows` (907),
  `assignment_problem` (1010), `volume_keys` (1032).
- Modify: `tests/freecad_addon/symcases.py`: add `motor_study(doc) -> study`.
- Test: `tests/freecad_addon/test_symmetric_study.py`

**Interfaces:**
- Consumes: `symmetry.read_chain`, `SymmetryError`, `symcases.motor_doc`.
- Produces:
  - `objects.SymmetricMesh`, a proxy. Properties:
    - `Top`: `App::PropertyLinkGlobal`.
    - `Cells`: `App::PropertyLinkListGlobal`, read-only.
    - `Steps`: `App::PropertyStringList`, read-only.
    - `execute` fills `Cells` and `Steps` from `read_chain`: one line per step, e.g. `mirror (0, 0) 15°` or
      `rotate (0, 0) 30° × 12`. On `SymmetryError` it leaves them empty.
  - `objects.make_symmetric_mesh(study, top) -> obj`, stored in `MeshSizesGroup`.
  - `objects.symmetric_items(study) -> list`.
  - `objects.is_symmetric(study) -> bool`.
  - `objects.cell_bodies(study) -> list`: the leaves of every item whose chain reads, deduped by Name.
  - `Material.Pieces`: `App::PropertyLinkSubListGlobal`, "Faces made of this material".
  - `objects.assign_pieces(study, name, pieces, lib, potential) -> Material`. `pieces` is `[(body, "FaceN")]`, the
    Label is `name` and `Body` stays None.
  - `objects.piece_assignments(study) -> list`.
  - `symcases.motor_study(doc)` returns the Study built on `motor_doc`:
    - 2D, sliding motion. Main = `stator_top`, Moving = `rotor_top`.
    - Two Symmetric Mesh items.
    - A Rotational Sliding Interface at R 35 with 144 divisions. It has no Air Region; see Task 3 for how it validates.
    - Piece assignments by the face's position (CoM radius and angle, as `build_doc.py` does by area):
      - one each: `StatorIron`, `StatorAir`, `RotorIron`, `RotorAir`;
      - `Coil01`..`Coil12`, the two half faces of slot k each;
      - `MagnetN` and `MagnetS`.
- Behaviour:
  - `assignment_label(m)` returns `m.Label` unchanged for a piece assignment, and `sync_labels` leaves it alone.
  - `item_refs(m)` lists the pieces.
  - `_size_text` gives `"symmetric"` for the new item.
  - `volume_keys(study)`: when `is_symmetric`, it is `[m.Name for m in piece_assignments(study)]` plus the Sliding
    Interfaces when sliding, and no body keys.
  - `assignment_problem` accepts the cell bodies as well as `assignable(study)`.
  - `material_rows`: when `is_symmetric`, one row per piece assignment:
    `(None, item_refs(m), [m.Label, lib, MAT_ID, potential])`.
  - `SlidingInterface.execute` (objects.py 573) today raises "it needs an Air Region". In a symmetric Study it sets
    `Shape` to the full circle of `Radius` in the XY plane instead (spec §6: no Air Region).

- [ ] **Step 1: Write the failing tests:**
  - `test_item_shows_cells_and_steps`: Steps are `["mirror (0, 0) 15°", "rotate (0, 0) 30° × 12"]` and there are
    3 Cells.
  - `test_piece_assignment_gets_one_mat_id_keyed_by_itself`: after `update_ids`, the MatIds keys are exactly the 20
    assignment Names plus the interface. No body Name is a key.
  - `test_piece_assignment_label_is_kept_on_sync`: rename the library material, run `sync_labels`, and the Label is
    still `Coil01`.
  - `test_mesh_size_on_a_cell_body_is_allowed`: `assignment_problem(study, [CoilCell]) == ""`.
  - `test_save_reload_keeps_pieces_and_item`: round-trip the document as `test_study_survives_save_and_reload` does.
  - `test_sliding_interface_without_air_has_a_circle`: the motor study's interface recomputes without error, and its
    Shape is one closed edge of radius 35.

- [ ] **Step 2: Run them and check that they fail**

  Run: `pixi run -e addon pytest tests/freecad_addon/test_symmetric_study.py -q`
  Expected: FAIL, `AttributeError: module 'emsolution.objects' has no attribute 'make_symmetric_mesh'`.

- [ ] **Step 3: Implement the Interfaces above in `objects.py`**

- [ ] **Step 4: Run the new file and the whole add-on suite**

  Run: `pixi run -e addon pytest tests/freecad_addon/test_symmetric_study.py -q`, then `pixi run -e addon test-addon`.
  Expected: 6 passed, and the suite stays green.

- [ ] **Step 5: Format, lint, commit**: "Symmetric mesh: item, Materials on pieces, MAT_IDs per assignment"

### Task 3: Validation rules

**Files:**
- Modify: `freecad_addon/emsolution/validation.py`:
  - `validate` (55): when symmetric, check mesh settings against the cell bodies.
  - `_links` (111): no warning for a piece assignment's empty `Body`.
  - New `_symmetric(study, main, moving, r)`, which replaces `_air`, `_slides` and `_materials` in symmetric
    Studies.
  - `_names` (455): when symmetric, the names are the piece assignment names plus the interfaces.
- Test: `tests/freecad_addon/test_symmetric_study.py` (add to it)

**Interfaces:**
- Consumes: Task 2's objects API and `symmetry.read_chain`.
- Produces: error texts that tests match by substring. The words in quotes below must appear.

Each rule raises `r.error` on the item named (spec §6–7, plus this plan's one-item-per-side rule):
- the item's chain fails to read: the error gives the `SymmetryError` text, on the item;
- `Top` is empty: "has no top object";
- more than one item on one side, or Main / Moving holding anything other than that side's top: "only one Symmetric
  Mesh per side";
- an Air Region in the Study: "Air Region";
- the Study plane is not XY: "XY plane";
- a whole-body assignment on a top: "pieces";
- a face of a top with no assignment, or with two: "no Material" / "two Materials", naming `Body.FaceN`;
- an assignment with pieces on both sides: "both sides";
- a piece on a body that is not a top: "not a Symmetric Mesh top";
- a Mesh Size, Transfinite or Recombine item referencing a top: "copies are not meshed";
- a Sliding Interface that is not Rotational: "Rotational";
- `Divisions % len(transforms) != 0` for an item: "divisions", giving the copy count.

- [ ] **Step 1: Write the failing tests**, one per rule, plus:
  - `test_motor_study_validates_clean`: no errors and no warnings.
  - `test_changing_array_count_reports_pieces` (Review Focus 1): set the stator array's NumberPolar to 6, recompute
    and validate. Assert "no Material" or "two Materials" is among the errors, and that nothing raises.
  - `test_deleted_cell_body_is_an_error` (Review Focus 2): remove `CoilCell` and validate. The errors include one on
    the stator item.
  - `test_extra_body_in_main_is_refused` (Review Focus 5): add a plain face body to MainObjects. "only one Symmetric
    Mesh per side" is among the errors.

- [ ] **Step 2: Run them and check that they fail**

  Run: `pixi run -e addon pytest tests/freecad_addon/test_symmetric_study.py -q -k "validat or refused or reports or error"`
  Expected: FAIL (no such errors yet).

- [ ] **Step 3: Implement `_symmetric` and the changes to `validate` and `_names`**

- [ ] **Step 4: Run the file and the whole suite** and check that both pass.

- [ ] **Step 5: Format, lint, commit**: "Symmetric mesh: validation rules"

### Task 4: The job for a symmetric Study

**Files:**
- Modify: `freecad_addon/emsolution/jobwriter.py`:
  - `check` (40): when symmetric, `bodies` = `objects.cell_bodies(study)`.
  - `write_job` (181): use `ids[body.Name]` in place of the four `int(study.MatIds[body.Name])` lookups. When
    symmetric, skip the Air Region and `write_slides`.
  - New `write_symmetric(study, folder, ids) -> dict`.
- Test: `tests/freecad_addon/test_symmetric_study.py` (add to it)

**Interfaces:**
- Consumes: Tasks 1–2.
- Produces the job keys that `meshsym` (Task 5) reads:
  - `job["bodies"]`: the cell bodies in the usual form, with `mat_id` = a **local id** 1..n in `cell_bodies` order.
    `sizes`, `transfinite` and `recombine` refer to these local ids, so `mesher2d.build` meshes the cell unchanged.
  - `job["symmetric"]`:
    - `"sides"`: a list of entries, each with:
      - `"side"`: `"fixed"` or `"moving"`;
      - `"cells"`: the local ids;
      - `"transforms"`: lists of 16 floats;
      - `"pieces"`: `[{"mat_id", "name", "file"}]`, one `geometry/piece_<n>.brep` per face, with the assignment's
        MAT_ID and `volume_name`.
    - `"slide"`: `{"name", "kind": "rotational", "radius", "divisions", "slide_mat_id", "full": True}`. Only when
      sliding.
  - No `"air"`, `"slides"`, `"moving"` or `"periodic"` keys in a symmetric job.

- [ ] **Step 1: Write the failing test** `test_job_has_cell_bodies_and_symmetric_block`. Save the motor study to
  `tmp_path` (`write_job` needs a saved document), call `write_job`, and load the JSON. Assert:
  - 6 bodies with ids 1..6;
  - two sides with 24 and 16 transforms;
  - 120 pieces whose files exist;
  - 20 distinct piece MAT_IDs that equal `study.MatIds` of the assignments;
  - `slide.divisions == 144`;
  - `"air" not in job`.

- [ ] **Step 2: Run it and check that it fails**

  Run: `pixi run -e addon pytest tests/freecad_addon/test_symmetric_study.py -q -k job_has`
  Expected: FAIL (`KeyError: 'symmetric'`).

- [ ] **Step 3: Implement it**

- [ ] **Step 4: Run the file and the whole suite** and check that both pass.

- [ ] **Step 5: Format, lint, commit**: "Symmetric mesh: write the cell job"

### Task 5: The mesher: mesh the cell, copy, label, write

**Files:**
- Create: `freecad_addon/emsolution/meshsym.py`
- Modify: `freecad_addon/emsolution/meshcommon.py`. Extract from `run` (683):
  - `generate(job, dim)`: options, ElementOrder, Optimize, the transfinite-fallback check, `generate`;
  - `publish(outputs)`: the `os.replace` loop and its PermissionError.

  `run` then calls both, with no change in behaviour.
- Modify: `freecad_addon/emsolution/mesher2d.py::run_job` (144): when `"symmetric" in job`, call
  `meshsym.run(job_path, build)` and print its report.
- Test: `tests/freecad_addon/test_meshsym.py`. Its jobs are written by hand, the way `test_mesher2d.py` does
  (`write_sectors` etc.); it needs no FreeCAD.

**Interfaces:**
- Consumes: the job of Task 4, `mesher2d.build`, `meshcommon.generate / publish / write_split / slide_report /
  JobError`.
- Produces: `meshsym.run(job_path, build) -> job`. It writes `job["mesh_file"]`, plus `job["rotor_file"]` when
  sliding, and `mesh.unv` beside the job.
  1. Build the cell with `build(job, folder)` in one model, holding the cells of both sides.
  2. Sliding: every curve whose ends are both at `radius` gets `divisions × arc angle / 360` + 1 transfinite nodes.
     If that is not a whole number, or an end is off the `360° / divisions` grid that starts at 0°, raise `JobError`:
     "sliding interface <name>: the cell's arc …".
  3. `generate(job, 2)`.
  4. Per side, for each cell entity:
     - take 3 element centres, then for each transform move them and find the piece that contains all of them. Load
       the pieces into a second gmsh model and use `gmsh.model.isInside(2, tag, xyz)`. If none or several pieces
       match, raise `JobError` "copy lands outside the drawing near (x, y)".
     - Add the entity's area (`occ.getMass`) to that piece.
  5. Coverage: every piece's sum must equal its area (rel 1e-6). Otherwise raise `JobError` "not symmetric: piece
     <name> (<file>) …".
  6. Copy every side into one model, `"full"`: port `copy_mesh` from the experiment, with the labels precomputed in
     step 4. Mirrored copies get `mesh.reverse`. Then `removeDuplicateNodes`, renumber, one physical group per
     MAT_ID, and write `mesh.unv`.
  7. Sliding: split by side, with `write_split`.
     - The fixed side's groups go to `mesh.msh`, then to `mesh_file`.
     - The moving side's groups go to `rotor.msh`, then to `rotor_file`. Add the slide marker: a discrete point
       entity holding a type-15 element on the node at (radius, 0), physical group `slide_mat_id`.

     Without sliding, write the full model to `mesh.msh`. Then `publish`.
  8. `run_job` prints `MAT_ID <id> <name>` per piece assignment. When sliding, it prints
     `slide_report({"slides": [slide]})`.

- [ ] **Step 1: Write the failing tests** (each `subprocess.run`s `mesher2d.py`, as `Mesher2DTest.run_job` does):
  - `test_copies_cover_the_ring_without_gaps`:
    - Cell: two bodies, sectors r 10..20 and r 20..30, 0..45°.
    - Transforms: 4 rotations × {identity, mirror at 45°}.
    - Pieces: 16 sectors, 45° wide, MAT_IDs 1 and 2 by radius.
    - Expect: groups 1 and 2 only, and minSJ ≥ 0 everywhere. Edges used once lie only at r = 10 or 30 (reuse the
      facet count from `motor_cell.report`).
  - `test_each_copy_takes_its_piece_mat_id`: as above, but the outer ring's pieces alternate ids 2 and 3 every 45°.
    Expect 3 groups with equal element counts for 2 and 3.
  - `test_asymmetric_drawing_is_refused`: one outer piece is 44° wide and its neighbour 46°. Expect returncode 1 and
    `"not symmetric"` in stderr.
  - `test_sliding_sides_match`:
    - Fixed cell: r 35..60, 0..15°, 24 transforms (mirror 15°, rotate 30° × 12).
    - Moving cell: r 10..35, 0..22.5°, 16 transforms.
    - divisions 144.
    - Expect: both files have 144 nodes on r = 35 at the same angles (round(angle, 6) % 360, the spike's fix), and
      `meshreport._point(rotor_file)` finds the marker at (35, 0).
  - `test_divisions_off_the_grid_are_refused`: divisions 100. Expect `"sliding interface"` in stderr.
  - `test_structured_cell_stays_quads`: the cell has one transfinite and recombined body. Expect quadrangles in the
    output and minSJ ≥ 0.

- [ ] **Step 2: Run them and check that they fail**

  Run: `pixi run -e addon pytest tests/freecad_addon/test_meshsym.py -q`
  Expected: FAIL. The mesher ignores `"symmetric"` and meshes the cell alone, so the assertions fail.

- [ ] **Step 3: Extract `generate` / `publish` and check that nothing changed**

  Run: `pixi run -e addon pytest tests/freecad_addon/test_mesher2d.py tests/freecad_addon/test_mesher.py -q`
  Expected: PASS.

- [ ] **Step 4: Implement `meshsym.run` and the `run_job` dispatch**

- [ ] **Step 5: Run the tests and check that they pass**: `test_meshsym.py`, then the whole suite.

- [ ] **Step 6: Format, lint, commit**: "Symmetric mesh: mesh the cell, copy it, MAT_IDs from the pieces"

### Task 6: GUI: the Symmetric Mesh command and Materials on faces

**Files:**
- Modify: `freecad_addon/emsolution/commands.py`:
  - add `AddSymmetricMesh`;
  - add `"EMS_SymmetricMesh"` to `COMMANDS` (326), after `EMS_Recombine`;
  - in `AssignMaterial.Activated`, when the selection has faces of a Symmetric Mesh top, call
    `taskpanels.ask_piece_assignment`.
- Modify: `freecad_addon/emsolution/taskpanels.py`: add `ask_piece_assignment(study, pieces)`. It asks for a name with
  the existing text prompt, then a library material and potential with `AssignDialog`, and calls
  `objects.assign_pieces` inside one transaction.
- Create: `freecad_addon/icons/symmetric.svg`. Copy the style of the existing icons.
- Modify: `tests/freecad_addon/gui_smoke.py`: add a step. It builds `symcases.motor_study`, runs the command on the
  stator Fragments, and asserts the item's Steps have 2 lines.

**Interfaces:**
- Consumes: `objects.make_symmetric_mesh`, `objects.assign_pieces`, `objects.symmetric_items`.
- `AddSymmetricMesh.Activated` needs exactly one selected object, which must be in the Study's Main or Moving geometry.
  Otherwise it warns "Select the object built from the cell (the Fragments or Array) first." It then calls
  `_create(study, "Add Symmetric Mesh", lambda: objects.make_symmetric_mesh(study, top))`.

- [ ] **Step 1: Write the smoke-test step**
- [ ] **Step 2: Run the smoke test and check that it fails**

  Run: `pixi run -e addon freecad tests\freecad_addon\gui_smoke.py`
  Expected: the last line of `%TEMP%\ems_gui_smoke.txt` is `FAIL`, naming the missing command.

- [ ] **Step 3: Implement the command, `ask_piece_assignment` and the icon**
- [ ] **Step 4: Run the smoke test again** and check that it gives `PASS`. Then run `pixi run -e addon test-addon`.
- [ ] **Step 5: Format, lint, commit**: "Symmetric mesh: command and Materials on faces"

### Task 7: End to end, from the FreeCAD Study to the mesh files

**Files:**
- Test: `tests/freecad_addon/test_symmetric_study.py` (add to it)

**Interfaces:**
- Consumes: everything above, and `cases.MESHERS["2D"]` to run the mesher as a subprocess.

- [ ] **Step 1: Write the tests:**
  - `test_motor_meshes_end_to_end`:
    - `motor_study` → save → `write_job` → run the mesher. Expect returncode 0.
    - `meshreport.groups(mesh_file)` is the fixed side's assignment names.
    - `groups(rotor_file)` is the moving side's names plus the interface.
    - There are 144 slide nodes on both sides at the same angles.
    - stdout has 20 `MAT_ID` lines.
  - `test_static_study_writes_one_file` (Review Focus 4):
    - Only the stator: Movement "No movement", one item, no Sliding Interface.
    - Expect returncode 0, `mesh_file` exists, and `"rotor_file" not in job`.
- [ ] **Step 2: Run them and check that they pass**

  Run: `pixi run -e addon pytest tests/freecad_addon/test_symmetric_study.py -q -k "end_to_end or one_file"`
  Expected: PASS. If a test fails, the bug is in the task that owns that stage: fix it there, not here.

- [ ] **Step 3: Run the full suite**, then commit: "Symmetric mesh: end-to-end tests"
