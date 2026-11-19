# Swept Body, Stage 1: straight sweeps — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A Swept Body item that meshes a straight 3D sweep (busbar, round wire, plate) by meshing its cross-section in
2D, with the body's Skin Layer, and copying it along the body into hexahedra and prisms. The air and the other bodies
mesh around it with matching nodes. It works in ordinary 3D Studies and comes with the Stage 1 catalogue rows.

**Architecture:**
- **FreeCAD side (GUI-free):** a new `SweptBody` object; a new module `sweeps.py` that recognises a body as a profile
  face moved along a chain of screw motions (Stage 1: one straight piece); validation; jobwriter entries `"swept"` in
  `_body_job`.
- **Mesher side (never FreeCAD):** a new module `meshsweep.py`:
  - meshes the profile face alone in its own gmsh model, with the skin (quad layers on smooth sections, a graded
    structured grid on four-sided sections, graded triangles otherwise);
  - copies the section to stations along the path into hexahedra and prisms;
  - writes those nodes and elements onto the body's own gmsh entities in the main model, with
    `Mesh.MeshOnlyEmpty = 1`, so gmsh meshes only the rest (spec section 4, option 1).

  The spike (Task 1) confirms option 1 before anything else is built.

**Tech Stack:** FreeCAD 1.1 add-on (Python 3.11, PySide), gmsh 4.15.2 Python API, numpy, pytest via pixi.

**Spec:** `docs/superpowers/specs/2026-11-17-swept-body-prism-layers-design.md`: all of it, especially sections 4,
5, 7.1, 8 (Stage 1) and 11. It builds on the Skin Layer of
`docs/superpowers/specs/2026-11-14-mesh-refinements-design.md` section 5.2. Read both before starting.

## Global Constraints

- Run everything through pixi:
  - `pixi run -e addon test-addon`
  - `pixi run -e addon pytest tests/freecad_addon/<file> -k <name>`
  - `pixi run lint`
  - `pixi run format`, then revert its change to the unrelated `highlight.py` if it makes one.
  - Never `pip install`.
- Branch: create `freecad/swept-body` from `freecad/mesh-refinements` (tip `908f31b`; Swept Body needs its Skin
  Layer). Commit per task, never `--no-verify`, never push or merge.
- Ruff:
  - line length 120, double quotes;
  - no trailing comma on a construct that fits on one line;
  - never reorder imports;
  - format only files you changed.
- Module rules (AGENTS.md):
  - `meshsweep.py` is a mesher module: it never imports FreeCAD, and it imports the other mesher modules by plain
    name (`import meshcommon`, `from meshcommon import ...`). Add it to whatever list `runner.py` or the tests use to
    find the mesher modules, if there is one.
  - `sweeps.py` is GUI-free (FreeCAD and Part only), like `geometry.py`. Add it to the list of GUI-free modules in
    AGENTS.md.
  - GUI code goes only in `commands.py`, `taskpanels.py` and `labels.py`.
- A Study without a Swept Body writes no `"swept"` key and meshes exactly as before (same element count and node
  coordinates).
- Defaults (spec 5.1): `PathSize` 0 and `SectionSize` 0, where 0 means the body's own size (its whole-body Mesh Size,
  else the default size: `objects.whole_body_size`).
- Grading (spec 5.3, 5.4 and call 7), wherever a skin applies: first step `δ / ElementsPerDepth`, ratio `1.2`, over
  `LayerDepth · δ`.
- Stage 1 recognises straight sweeps only. Revolved and helical bodies are refused with the reason
  `"only straight sweeps are made so far"`; Stages 2 and 3 lift that.
- Stage 1 is for ordinary 3D Studies only: Validate refuses Swept Body in a Study with Symmetric Groups (Stage 4 lifts
  that).
- Units are mm. Property group `"EMSolution"`.
- GUI changes need the smoke test. Run `pixi run -e addon freecad tests\freecad_addon\gui_smoke.py` from PowerShell
  (Git Bash strips the backslashes and FreeCAD hangs). The last line of `%TEMP%\ems_gui_smoke.txt` must be `PASS`.

**Ruling on spec 5.5 (Recombine):** the spec both refuses Recombine on a swept body and uses it for the section. This
plan uses it: Recombine on a swept body recombines the cross-section, giving hexahedra only. Transfinite Body on a
swept body is refused.

## Review Focus

1. **A round wire whose lateral face has a seam edge** (OCC closes a cylinder with a seam line along the path): every
   node on the seam is classified on that curve and the air meets the wire without free faces. Task 7 test:
   `test_swept_round_wire_is_conformal`.
2. **A busbar end against a terminal** (an end face that is not real surface for the skin but is shared): no grading
   toward that end, and the terminal's tetrahedra share the end face's nodes. Task 7 test:
   `test_swept_bar_end_on_a_terminal`.
3. **A bar cut by the domain's outer boundary** (a half bar on a symmetry plane): the cut face gets no skin grid, and
   the cut end gets no station grading. Task 6 test: `test_section_skips_cut_sides`; Task 7 test:
   `test_swept_bar_cut_end_is_not_graded`.
4. **A layer deeper than half the section** (δ large against a thin plate): the graded steps from both sides meet in
   the middle and nothing breaks. Task 6 test: `test_graded_positions_layer_fills_the_length`.
5. **A body that also has a Mesh Size or a Refine Near:** Validate warns that the sweep wins, and the mesh is the
   same as without them. Task 4 test: `test_swept_body_wins_over_mesh_size`; Task 7 test:
   `test_swept_ignores_size_fields`.

---

### Task 1: Spike 7.1, joining a hand-made mesh

**Files:**
- Create (throwaway, not committed): a script in the session scratchpad.
- Modify: `docs/superpowers/specs/2026-11-17-swept-body-prism-layers-design.md` (a "Spike result" paragraph at the
  end of 7.1, as in the refinement spec).

**Interfaces:**
- Produces: the decision between section 4's option 1 and option 2. The rest of this plan assumes option 1.

- [ ] **Step 1: Build the two shapes** in gmsh OCC in one model each: a bar 10 × 4 × 40 mm (along z) in an air box of
  60 × 60 × 100 at size 6, and a round wire r 0.45 mm along a helix of radius 1.2 and pitch 10 over 1.5 turns
  (litz1's strand) in an air box of 6 × 6 × 20 at size 0.6. Fragment; mesh the profile face alone in a second gmsh
  model (bar: transfinite 10 × 4 quads; wire: quad layers plus triangles); copy the section to stations
  (bar: 20 steps; wire: 60 steps, by the screw motion of the helix).
- [ ] **Step 2: Option 1.** Classify every node on the body's points, curves, faces or volume
  (`gmsh.model.getClosestPoint`, tolerance 1e-6 × model size), `addNodes` and `addElements` on each entity (points,
  lines on curves, triangles and quads on faces, hexahedra and prisms on the volume), set `Mesh.MeshOnlyEmpty = 1`,
  `generate(3)`.
- [ ] **Step 3: Check** each shape:
  - no element face used once inside the domain (only the air box's outer faces);
  - shared-face nodes shared (a node on the body's surface belongs to both a body element and an air element);
  - tetrahedra or pyramids against the body's quad faces: note which gmsh makes, if any;
  - gmsh min SICN of the air ≥ that of the same air around a tet-meshed body, minus 0.05;
  - air element count and time within 10 % of the same air around the body meshed with tetrahedra at the size of the
    body's surface elements.
- [ ] **Step 4: If option 1 fails,** try option 2 (`meshfrozen.mesh_region` around the frozen body) with the same
  checks.
- [ ] **Step 5: Record the result** in spec 7.1: numbers per shape and option, and how quad faces meet tetrahedra
  (gmsh pyramids, `meshfrozen.quad_pyramids`, or splitting the outer quads). **If neither option passes, stop and
  report to the user (spec call 11).** If only option 2 passes, stop and report too: Task 7 must be rewritten for it
  before going on.
- [ ] **Step 6: Commit** the spec change: `Swept Body: spike result for joining a hand-made mesh`.

---

### Task 2: The Swept Body object

**Files:**
- Modify: `freecad_addon/emsolution/objects.py`:
  - the proxy after `SkinLayer`;
  - `make_swept_body` after `make_skin_layer`;
  - `swept_bodies` after `skin_layers`;
  - `is_item`, `_size_text`, `air_refusal`.
- Test: `tests/freecad_addon/test_study.py`

**Interfaces:**
- Produces:
  - `class SweptBody(_Proxy)`, with properties:
    - `References` (`App::PropertyLinkSubListGlobal`, "Bodies meshed by sweeping their cross-section");
    - `StartFace` (`App::PropertyLinkSubListGlobal`, "Optional: the flat end face to start from, one per solid");
    - `PathSize` (`App::PropertyLength`, "Element length along the path; 0 = the body's size");
    - `SectionSize` (`App::PropertyLength`, "Element size in the cross-section away from the skin; 0 = the body's size").
  - `make_swept_body(study, refs, path_size=0.0) -> obj`. Label `"SweptBody"`, placed in the Mesh Sizes folder like
    the other items.
  - `swept_bodies(study) -> list`: the Swept Body items in tree order.
  - `_size_text(item)`: `"along body size"` when PathSize is 0, else `f"along {p:g} mm"`; plus
    `f", section {s:g} mm"` when SectionSize > 0; plus `", skin"` when a Skin Layer of the Study references the same
    body.
  - `is_item` covers the class. `air_refusal(objects.SweptBody, [air])` gives
    `f"Air Region {names} cannot be a Swept Body."`.

- [ ] **Step 1: Write the failing tests** in `StudyTest`:
  - `test_swept_body_defaults_and_row`: a box body, `make_swept_body(study, [(a, "")])`; the defaults hold;
    `swept_bodies` returns it; the row text is `"along body size"`; with `PathSize = 2` and `SectionSize = 0.5` it is
    `"along 2 mm, section 0.5 mm"`; with a Skin Layer on the box it ends `", skin"`.
  - `test_swept_body_refuses_the_air`.
- [ ] **Step 2: Run** `pixi run -e addon pytest tests/freecad_addon/test_study.py -k swept -v`. Expected: FAIL
  (`make_swept_body` missing).
- [ ] **Step 3: Implement.** Follow `SkinLayer`.
- [ ] **Step 4: Run** `test_study.py` in full. Expected: PASS.
- [ ] **Step 5: Commit** `FreeCAD add-on: Swept Body item`.

---

### Task 3: Recognising a straight sweep

**Files:**
- Create: `freecad_addon/emsolution/sweeps.py` (GUI-free; FreeCAD, Part, math only)
- Test: `tests/freecad_addon/test_sweeps.py`

**Interfaces:**
- Produces:
  - `Piece = namedtuple("Piece", "origin axis angle advance")`: a screw motion. `origin` and `axis` are 3-tuples
    (axis a unit vector), `angle` in degrees about the axis through origin, `advance` in mm along the axis. A straight
    piece has `angle == 0` and `advance` = its length; `origin` is then the profile's centre of mass.
  - `Sweep = namedtuple("Sweep", "profile end pieces closed")`: `profile` and `end` are face names of the solid
    (`"Face3"`; `end` is None when `closed`), `pieces` a list of `Piece`, `closed` a bool (always False in Stage 1).
  - `recognise(solid, start_face=None, tol=1e-6) -> Sweep | str`: a `Sweep`, or the reason it is not one (a string,
    for the Validate message). Reasons, exact text:
    - `"it has no flat end face that matches another end face moved"`;
    - `"the start face {face} is not a flat end face of it"`;
    - `"only straight sweeps are made so far"` (the two end faces match by a rotation or a screw motion, Stages 2-3);
    - `"a side face does not run straight from one end to the other"`;
    - `"its volume is not the start face swept to the end face"`.
  - `recognise_body(shape, start_faces=(), tol=1e-6) -> list[Sweep] | str`: one `Sweep` per solid of a multi-solid
    shape (spec call 10), in `shape.Solids` order. `start_faces` are face names of `shape`; each is matched to the
    solid holding it. The first refusal is returned as `f"solid {k}: {reason}"` when there are several solids, else
    the bare reason.
- Algorithm (straight): for each pair of planar faces (A, B) with the same area (relative 1e-6) and opposite outward
  normals, try `d` = B's centre of mass − A's. The pair is the sweep's ends when:
  - A translated by `d` coincides with B (`objects.coincident_faces`, already used by the jobwriter);
  - every other face has its normal perpendicular to `d` at 5 × 5 sample points (|n · d̂| < 1e-6);
  - `solid.Volume` = A's area × |d · n_A| (relative 1e-6).
  With `start_face`, only pairs with A = that face are tried. Without it, the first pair in face order wins; prefer
  the pair with the longest |d| when several match (a cube matches three ways; the result is any one of them).
  For a pair that matches only by a rotation, give the "only straight" reason (detect: same area, a rotation about
  the line where the two planes meet maps A onto B).

- [ ] **Step 1: Write the failing tests** (shapes built with Part in the test):
  - `test_box_is_a_straight_sweep`: `Part.makeBox(10, 4, 40)` with `start_face` = the z = 0 face gives one piece of
    advance 40 along (0, 0, 1) and `closed` False.
  - `test_round_wire_is_a_straight_sweep`: `Part.makeCylinder(0.45, 20)` (its lateral face has a seam) gives advance
    20; the profile is the bottom disc.
  - `test_oblique_extrusion`: a rectangle face extruded by (3, 0, 40) gives advance |(3, 0, 40)| along its unit
    vector.
  - `test_ring_is_not_straight_yet`: `Part.makeTorus(10, 2, pnt, dir, 0, 360, 90)` (a quarter ring) gives
    `"only straight sweeps are made so far"`.
  - `test_loft_is_refused`: a loft between a 10 × 10 and a 5 × 5 square gives the end-face reason.
  - `test_notched_bar_is_refused`: a box with a slot cut into one side face gives a refusal (side face or volume).
  - `test_two_solids`: a compound of two boxes gives two Sweeps; a compound of a box and a sphere gives
    `"solid 2: ..."`.
  - `test_start_face_not_an_end`: a side face as `start_face` gives the start-face reason.
- [ ] **Step 2: Run** `pixi run -e addon pytest tests/freecad_addon/test_sweeps.py -v`. Expected: FAIL (no module).
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** the file. Expected: PASS.
- [ ] **Step 5: Commit** `FreeCAD add-on: recognise straight sweeps`.

---

### Task 4: Validation of Swept Body

**Files:**
- Modify: `freecad_addon/emsolution/validation.py`: `_kind`, `_settings` (a new `_swept_bodies(study, included, bodies, r)`
  beside `_skin_layers`), and the 3D-quads warning in `_skin_layers`.
- Test: `tests/freecad_addon/test_study.py`, `tests/freecad_addon/test_symmetric_study.py`

**Interfaces:**
- Consumes: Task 2, Task 3 (`sweeps.recognise_body`).
- Produces these exact problems (`validation.validate(study)`), `label` the item's Label, `name`
  `objects.display_name(body)`:
  - Error, a sub-element pick: `f"Swept Body {label}: pick whole bodies, not {body.Label}.{sub}."`.
  - Error, the air: the `air_refusal` message, through the existing path.
  - Error, 2D Study: `f"Swept Body {label}: a 2D Study is already a cross-section; Swept Body is for 3D Studies."`.
  - Error, a Study with Symmetric Groups: `f"Swept Body {label}: Studies with Symmetric Groups are not swept yet."`.
  - Error, not a sweep: `f"Swept Body {label}: {name} is not a sweep: {reason}."` (reason from `recognise_body`).
  - Error, a body in two items: `f"Swept Body {label}: {name} is already in Swept Body {other}."`.
  - Error, with Transfinite Body: `f"Swept Body {label}: {name} also has Transfinite Body {other}; a body is swept or structured, not both."`.
  - Error, contact with a structured body (spec 5.5, user's decision): another Swept Body body, a Transfinite Body
    body or a 3D Recombine body that shares a face area with the body:
    `f"Swept Body {label}: {name} touches {other}, which is {what}; a swept body may touch only the air and unstructured bodies."`,
    `what` one of `"swept"`, `"structured"`, `"recombined"`. Solids of one multi-solid reference that touch each other
    give the same error with `other` = `name`.
  - Error, partial contact: for each face F of the body and each other meshed body B (not the Air Region), with
    `a = F.common(B.Shape).Area`: refused when `tol_area < a < F.Area − tol_area` (`tol_area` = 1e-6 × F.Area):
    `f"Swept Body {label}: {other} touches only part of {body.Label}.{face} of {name}; a swept body's faces must be touched whole or not at all."`.
  - Error, sliding: a body whose distance to a Sliding Interface's surface is below 1e-6:
    `f"Swept Body {label}: {name} touches the sliding interface {iface}; swept bodies must keep clear of it."`.
  - Warning, a Mesh Size or Refine Near that picks the body or its sub-elements:
    `f"{kind} {item_label}: {name} is swept, and that wins; the {kind} does nothing inside it."`.
  - The Skin Layer warning `"quad layers are made in 2D Studies only; ignored."` is not given for a swept body (its
    section makes quad layers by itself, spec 5.3).
  - `_kind` entry `objects.SweptBody: "Swept Body"`, so the existing `_links` messages apply.
  - Recombine on a swept body: no problem (the Ruling in Global Constraints).

- [ ] **Step 1: Write the failing tests** in `test_study.py` (3D box bodies in an Air Region unless said):
  - `test_swept_body_on_a_face_is_refused`.
  - `test_swept_body_in_2d_is_refused`.
  - `test_swept_body_not_a_sweep`: a sphere gives the end-face reason in the message.
  - `test_swept_body_twice_is_refused`.
  - `test_swept_body_with_transfinite_is_refused`.
  - `test_swept_bodies_touching_are_refused`: two boxes sharing a whole face, both swept: the contact error with
    `"swept"`.
  - `test_swept_body_on_a_tet_block_is_fine`: a bar 10 × 4 × 40 whose end face lies whole on a 30 × 30 × 10 block
    (not swept): no Swept Body problem.
  - `test_swept_body_partial_contact_is_refused`: a block touching half of the bar's side face: the partial-contact
    error naming that face.
  - `test_swept_body_wins_over_mesh_size` (Review Focus 5): a Mesh Size on the swept box gives the warning.
  - `test_swept_body_with_skin_quads_has_no_3d_warning`: a Skin Layer with `QuadLayers` on a swept box gives no
    "2D Studies only" warning; on an unswept box it still does.
  - `test_swept_body_recombine_is_fine`.
  - In `test_symmetric_study.py`, `test_swept_body_in_a_symmetric_study_is_refused`.
- [ ] **Step 2: Run** `pixi run -e addon pytest tests/freecad_addon/test_study.py tests/freecad_addon/test_symmetric_study.py -k swept -v`.
  Expected: FAIL.
- [ ] **Step 3: Implement.** Run the checks only for items with a meshed reference, as Skin Layer does. Run the
  contact and partial checks only on bodies that are sweeps (no point after a "not a sweep" error).
- [ ] **Step 4: Run** both files in full. Expected: PASS.
- [ ] **Step 5: Commit** `FreeCAD add-on: validate Swept Body`.

---

### Task 5: Swept Body in job.json

**Files:**
- Modify: `freecad_addon/emsolution/jobwriter.py`: a new `swept_entries(study, folder, ids, prefix="")` called from
  `_body_job`; `skin_entries` leaves out swept bodies.
- Test: `tests/freecad_addon/test_study.py`

**Interfaces:**
- Consumes: Tasks 2, 3.
- Produces `swept_entries(study, folder, ids, prefix="") -> list[dict]`, one entry per swept body in `ids`, in tree
  order; `_body_job` sets `job["swept"]` only when the list is non-empty:
  ```
  {"name": <region_name>, "mat_id": m, "path_size": <PathSize or the body's size>,
   "section_size": <SectionSize or the body's size>, "recombine": <bool: the body is in job["recombine"]>,
   "skin": {"depth": δ, "per_depth": n, "layer": k} | None,
   "solids": [{"profile": "geometry/<prefix>sweep_<m>_<k>.brep",
               "pieces": [{"origin": [x, y, z], "axis": [x, y, z], "angle": a, "advance": d}]}]}
  ```
  - `profile` is the profile face exported in global coordinates (`global_shape` / `export_subs`), one per solid.
  - `"skin"` comes from the first Skin Layer that references the body; that body is then left out of `job["skin"]`
    (a `skin_entries` entry whose `mat_ids` become empty is dropped).
  - A swept body that is in `job["recombine"]` stays there; the mesher reads `"recombine"` from the swept entry and
    skips swept MAT_IDs in `apply_recombine` (Task 7).
  - Numbers rounded as the other entries do (`round(x, 9)` if that is the house rule; follow `refine_entries`).

- [ ] **Step 1: Write the failing tests:**
  - `test_job_without_swept_has_no_swept_key` (passes already).
  - `test_swept_goes_to_the_job`: a box 10 × 4 × 40 at size 2, `PathSize` 4: `job["swept"]` has one entry with
    `path_size` 4, `section_size` 2, `skin` None, one solid with one piece of advance 40 along ±z, and the profile
    file exists and holds one planar face.
  - `test_swept_takes_the_skin`: with a Skin Layer δ 1 on the box, the entry's `skin` is
    `{"depth": 1.0, "per_depth": 2.0, "layer": 3.0}` and `"skin"` is not in the job.
  - `test_swept_two_solids`: a compound of two separate bars as one body gives two `solids`.
- [ ] **Step 2: Run** `pixi run -e addon pytest tests/freecad_addon/test_study.py -k swept -v`. Expected: the new
  tests FAIL with `KeyError: 'swept'`.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `test_study.py` and `test_symmetric_study.py`. Expected: PASS.
- [ ] **Step 5: Commit** `FreeCAD add-on: write Swept Body to the mesh job`.

---

### Task 6: The section and the swept volume mesh

**Files:**
- Create: `freecad_addon/emsolution/meshsweep.py` (mesher module: gmsh, numpy, `meshcommon`, `meshfrozen`)
- Test: `tests/freecad_addon/test_meshsweep.py`

**Interfaces:**
- Consumes: the `"swept"` entry format of Task 5; `meshcommon.skin_refinements`, `apply_refinements`,
  `apply_quad_layers`, `_smooth` (reuse them in the section model with explicit `faces` = the real curves).
- Produces:
  - `graded_positions(length, size, first=None, depth=0.0, ratio=1.2, ends=(True, True)) -> np.ndarray`: node
    positions from 0 to `length`, increasing.
    - Without `first`: `max(1, round(length / size))` equal steps.
    - With `first`, at each end in `ends`: steps `first · ratio^k`, each capped at `size`, until their sum reaches
      `depth` (the step that crosses `depth` is kept). The middle is split into `max(1, round(middle / size))` equal
      steps.
    - If the graded steps of both ends together exceed `length`, scale them down to fill it exactly (a layer filling
      the length; no middle).
  - `Section = namedtuple("Section", "xyz tri quad edges")`: section nodes in global coordinates (n × 3), triangles
    (t × 3) and quads (q × 4) as node indexes, and `edges`: `{curve key: ordered node indexes}` for each profile curve.
  - `section_mesh(entry, solid_index, real_curves, folder) -> Section`: meshes `solids[k]["profile"]` in a new gmsh
    model (`gmsh.model.add`, then `gmsh.model.setCurrent` back to the main model's name before returning).
    - `real_curves`: the profile curves (by index in `gmsh.model.getBoundary` order of the profile face) whose side
      faces are real surface; the others are cuts.
    - With `entry["skin"]` and at least one real curve:
      - four curves, all straight: transfinite curves with node positions from `graded_positions(curve length,
        section_size, first, depth, 1.2, ends)`, where `ends` grades only toward a real neighbouring side; transfinite
        surface, recombined: quads only;
      - else, smooth by `meshcommon._smooth` on the real curves: graded fields plus `BoundaryLayer` quad layers, as
        the 2D Skin Layer does;
      - else: graded fields only (triangles), and
        `_note(f"Swept Body {name}: the cross-section of MAT_ID {m} has sharp corners and is not four-sided; graded triangles, so prisms")`.
    - Without a skin: size `section_size`, recombined (quads) when `entry["recombine"]`.
  - `stations(piece, positions) -> list[np.ndarray]`: one 4 × 4 transform per position (straight: translation by
    `position · axis`).
  - `sweep(section, transforms, closed=False) -> tuple[np.ndarray, dict]`: nodes (n × 3) and `{5: hexahedra, 6: prisms}`
    (gmsh node order). Layer j joins station j and j + 1. Orientation: if the first element's Jacobian is negative,
    flip all with `meshfrozen.FLIP`.

- [ ] **Step 1: Write the failing tests:**
  - `test_graded_positions_uniform`: `graded_positions(40, 4)` is 0, 4, …, 40.
  - `test_graded_positions_both_ends`: `graded_positions(10, 2, first=0.5, depth=3)`: the first and last steps are
    0.5, the steps grow by 1.2 toward the middle, none exceeds 2, symmetric, ends at 10.
  - `test_graded_positions_one_end`: `ends=(True, False)`: the last step is the middle step, not 0.5.
  - `test_graded_positions_layer_fills_the_length` (Review Focus 4): `graded_positions(2, 2, first=0.5, depth=3)`
    ends at 2, increasing, symmetric.
  - `test_section_of_a_bar_is_a_graded_grid`: a 10 × 4 profile, skin δ 1, 2/δ, 3δ, section size 2, all four curves
    real: quads only, the smallest edge along each side ≈ 0.5, the middle edges ≤ 2.
  - `test_section_of_a_wire_has_quad_layers`: a disc r 5, δ 1: quads within 3δ + 0.5 of the rim, triangles inside.
  - `test_section_skips_cut_sides` (Review Focus 3): the 10 × 4 profile with one long side a cut: the grid is not
    graded toward that side (its nearest step is the middle size).
  - `test_section_of_an_l_has_triangles`: an L-shaped profile with a skin gives triangles and the note.
  - `test_sweep_counts`: a section of 40 quads swept over 10 stations gives 9 × 40 = 360 hexahedra, positive
    Jacobians, 10 × (section nodes) nodes.
- [ ] **Step 2: Run** `pixi run -e addon pytest tests/freecad_addon/test_meshsweep.py -v`. Expected: FAIL (no module).
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** the file. Expected: PASS.
- [ ] **Step 5: Commit** `FreeCAD add-on: swept volume mesh of a section`.

---

### Task 7: Swept bodies in the 3D mesher

**Files:**
- Modify: `freecad_addon/emsolution/meshsweep.py`: `apply_swept(job, folder, body_vols)`.
- Modify: `freecad_addon/emsolution/mesher.py` (`build`, `run_job`) and `meshcommon.py` (`generate`,
  `apply_recombine`; the size and refinement helpers skip swept volumes if they would touch them).
- Test: `tests/freecad_addon/test_mesher.py`

**Interfaces:**
- Consumes: Task 6, the job of Task 5, the spike result (option 1).
- Produces:
  - `apply_swept(job, folder, body_vols) -> list[int]`: for each `"swept"` entry and each solid, called at the end of
    `build` after `apply_periodic`, before slides (which Validate keeps clear):
    1. map the solid to its final volume tag (the tag of `body_vols[m]` whose bounding box matches the solid's
       profile swept, or `gmsh.model.isInside` on a profile point moved half way);
    2. find the real curves of the profile: a profile curve's side face is real when it is in
       `meshcommon.real_boundary(3, [tag])`; real end faces likewise (they grade the stations, spec call 7);
    3. `section_mesh`, `graded_positions` along each piece (with `first`, `depth` and the real ends only when there
       is a skin), `stations`, `sweep`;
    4. classify nodes on the volume's points, curves and faces and add nodes and elements as in the spike;
    5. return the swept volume tags; `job["swept_tags"]` keeps them.
  - `generate(job, dim)`: when `job.get("swept_tags")`, set `Mesh.MeshOnlyEmpty = 1` before meshing (and whatever
    the spike found for quad faces against tetrahedra).
  - `apply_recombine` skips swept MAT_IDs.
  - `run_job` prints `f"Swept           {item['name']}"` for each swept entry (same column as `"Structured      "`).
  - A job without `"swept"` takes none of these paths.

- [ ] **Step 1: Write the failing tests** (`MesherTest`; air box 60 × 60 × 100 at size 6, MAT_ID 2, unless said):
  - `test_swept_bar_meshes`: bar 10 × 4 × 40 (MAT_ID 1), swept with path size 4, no skin: return code 0; the bar's
    elements are hexahedra only, 10 layers; `"Swept           Bar"` in stdout.
  - `test_swept_bar_with_skin`: δ 1, 2/δ, 3δ, section size 2: the smallest hexahedron edge across each side ≈ 0.5,
    and the station steps near both ends ≈ 0.5 (both ends are real surface in air).
  - `test_swept_round_wire_is_conformal` (Review Focus 1): a cylinder r 0.45, length 20, in an air box
    6 × 6 × 30 at size 0.6, δ 0.2: every element face inside the domain is used twice (count faces of all 3D
    elements, pyramids included; the only once-used faces lie on the air box's outer faces); the wire has hexahedra
    and prisms.
  - `test_swept_bar_end_on_a_terminal` (Review Focus 2): the bar's end face lies whole on a 30 × 30 × 10 terminal
    (MAT_ID 3, tetrahedra), δ 1: no station grading at that end (last step = path size), grading at the free end, and
    the mesh is conformal as above.
  - `test_swept_bar_cut_end_is_not_graded` (Review Focus 3): the bar's end lies on the air box's outer face: no
    grading at that end.
  - `test_swept_ignores_size_fields` (Review Focus 5): the same bar with a Mesh Size of 0.5 on one of its faces gives
    the same bar elements as without it.
  - `test_swept_excitation_surface`: an excitation surface (SMAT_ID 10) on the bar's end face: the physical group has
    the end face's quads, as many as the section has.
  - `test_empty_swept_key_is_unchanged`: the skin block job of `test_skin_grades_the_block_3d` run with
    `"swept": []` gives the same node coordinates (`read_nodes`) as without the key. The existing mesher tests,
    unchanged and passing, pin the rest of "no key, no change".
- [ ] **Step 2: Run** `pixi run -e addon pytest tests/freecad_addon/test_mesher.py -k swept -v`. Expected: FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `test_mesher.py`, `test_mesher2d.py` and `test_meshgroups.py` in full. Expected: PASS.
- [ ] **Step 5: Commit** `FreeCAD add-on: swept bodies in the 3D mesher`.

---

### Task 8: Command, panel, labels and icon

**Files:**
- Create: `freecad_addon/icons/sweptbody.svg`
- Modify:
  - `freecad_addon/emsolution/commands.py`: `AddSweptBody`, `STRUCTURED`, `COMMANDS`, `context_names`;
  - `freecad_addon/emsolution/taskpanels.py`: `ITEM_PICKS` and the Swept Body rows in `ItemPanel`;
  - `freecad_addon/emsolution/labels.py`: `KINDS`, `tag_text`, `description`;
  - `tests/freecad_addon/gui_smoke.py`.

**Interfaces:**
- Consumes: Task 2, Task 4's messages.
- Produces:
  - **Command `EMS_SweptBody`:** MenuText `"Swept Body"`, ToolTip
    `"Mesh bodies that are a cross-section moved along a path: hexahedra and prisms, long along the path and fine across"`,
    icon `sweptbody`. Activated like `AddTransfiniteBody`: whole bodies, `gate(study, bodies, objects.SweptBody)`,
    `make_swept_body` through `_create_and_edit(study, "Add Swept Body", ...)`.
  - `STRUCTURED = ("EMS_TransfiniteBody", "EMS_SweptBody", "EMS_TransfiniteEdges", "EMS_Recombine")`.
  - `context_names`: in 3D Studies, the whole-body list that has `"EMS_TransfiniteBody"` gains `"EMS_SweptBody"`
    after it.
  - **`ITEM_PICKS[objects.SweptBody]`:** whole bodies only, no air; list label `"Bodies"`; hint
    `"Select the bodies to sweep (whole bodies) in the 3D view or the tree."`.
  - **Panel rows after Name:** "Length along the path" and "Section size" (`_length_box`, 0 shown as "body size"),
    and "Start face" with Add selection / Remove (faces only), as Transfinite Body's Corners list.
  - **Labels:** `KINDS["SweptBody"] = ("#1c7ed6", "W", "Swept body")`; `tag_text` gives the `_size_text` text with
    the panel's unsaved values; `description` gives `f"Swept body: {tag_text}"`.
  - **Icon:** 64 × 64 SVG in the style of `transfinite*.svg` / `skinlayer.svg`: a bar in perspective whose end face
    shows a grid finer at its rim, with long cells along the bar.

- [ ] **Step 1: Update the smoke test first:** the expected `context_menu()` list for a whole-body pick in 3D gains
  `"EMS_SweptBody"`; add a step: select a box body, `Gui.runCommand("EMS_SweptBody")`, set the length along the path
  to 4, accept; assert `objects.swept_bodies(study)[0].PathSize.Value == 4` and that Validate shows no Swept Body
  error.
- [ ] **Step 2: Run the smoke test** (PowerShell): `pixi run -e addon freecad tests\freecad_addon\gui_smoke.py`, then
  `Get-Content "$env:TEMP\ems_gui_smoke.txt" -Tail 3`. Expected: `FAIL`.
- [ ] **Step 3: Implement** the command, menu and context entries, the panel, the labels and the icon. Render the icon
  with Qt beside the transfinite icons and look at it.
- [ ] **Step 4: Run** the smoke test (`PASS`), `pixi run -e addon test-addon` (all pass) and `pixi run lint` (clean).
- [ ] **Step 5: Commit** `FreeCAD add-on: Swept Body command, panel and icon`.

---

### Task 9: The Stage 1 review catalogue rows

**Files:**
- Modify: `experiments/refinement_catalogue/rows.py` (the rows) and `build_catalogue.py` (the "today" copy also
  deletes `objects.swept_bodies(study)`, so "today" is the graded Skin Layer or the plain mesh).

**Interfaces:**
- Consumes: the whole add-on, and the helpers in `rows.py` (`study_of`, `done`, `block`, `skin`, `cases.fit_air`).
- Rows (spec 8, Stage 1). Sizes are mm; pictures are cut through the conductor across and along it:

| id | Study | Items | after-check |
|---|---|---|---|
| SW-01 | busbar 10 × 4 × 100, copper, size 4, in an Air Region | Skin Layer 1 kHz (δ 2.09); Swept Body, path size 4 | element counts today vs new printed; hexahedra only |
| SW-02 | round wire r 3 × 100, size 2 | Skin Layer 10 kHz (δ 0.66); Swept Body | quads in the section > 0; prisms and hexahedra |
| SW-03 | plate 100 × 100 × 2, aluminium, size 10 | Skin Layer 1 kHz (δ 2.69: fills the plate, warning shown); Swept Body | the "deeper than half" warning printed |
| SW-04 | busbar of SW-01 | Swept Body only, no skin | uniform hexahedra |
| SW-05 | refusals: a sphere swept; the Air Region swept; a swept bar with a Transfinite Body; two swept bars touching; a block on half of a swept bar's side | — | each Validate error printed, no mesh |
| SW-12 | busbar of SW-01 with its end face on a 40 × 40 × 10 terminal block | Skin Layer and Swept Body on the busbar | conformal (no free faces inside); no grading at the terminal end |

- [ ] **Step 1: Add the rows.** Run
  `pixi run -e addon python experiments/refinement_catalogue/build_catalogue.py --only SW-01 SW-02 SW-03 SW-04 SW-05 SW-12`.
  Expected: all `match: true`.
- [ ] **Step 2: Look at every new picture** and fix the rows whose picture does not show the swept mesh (zoom on the
  conductor, cut planes). Re-run with `--only`.
- [ ] **Step 3: Run the whole catalogue.** Expected: every row (RN, RN-S, AG, SL, SW) matches, exit code 0.
- [ ] **Step 4: Commit** `Refinement catalogue: Stage 1 rows (Swept Body)`.

---

### Task 10: Stage 1 check and hand-over

- [ ] **Step 1: Run** `pixi run -e addon test-addon` (all pass), `pixi run lint` (clean), and the GUI smoke test
  (`PASS`).
- [ ] **Step 2: Hand over** `C:\Users\hamed\Desktop\delme\refinement_studies\catalogue.html` with the SW rows.
- [ ] **Step 3: Stop.** Don't merge or push; the user reviews the SW rows before Stage 2 is planned.
