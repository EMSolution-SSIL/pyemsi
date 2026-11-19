# Swept Body, Stage 2: revolved sweeps and closed rings — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Swept Body also meshes bodies revolved about an axis: a part ring (a busbar bend) and a closed ring (a
winding turn without pitch, a toroidal conductor), in ordinary 3D Studies. It comes with the Stage 2 catalogue rows.

**Architecture:** Stage 1's pipeline stays. Three things change:
- `sweeps.py` recognises a revolved piece (`angle` ≠ 0, `advance` 0). It does so from two end faces related by a
  rotation, or, for a closed ring, from faces that all turn about one axis.
- A closed ring has no end face, so its profile is a planar cut of the solid. `Sweep` gains a `face` field holding the
  profile as a `Part.Face`, and the jobwriter exports that face for every solid.
- `meshsweep.stations` rotates about the axis. Station spacing is arc length at the section's centroid radius. A
  closed sweep joins its last station to the first.

The mesher's joining (`_join`, `MeshOnlyEmpty`) is unchanged. It must also handle the seam curves that OCC leaves on
revolved faces.

**Tech Stack:** FreeCAD 1.1 add-on (Python 3.11), gmsh 4.15.2 Python API, numpy, pytest via pixi.

**Spec:** `docs/superpowers/specs/2026-11-17-swept-body-prism-layers-design.md` (sections 5.2, 5.4, 8 Stage 2, 11).
Stage 1 is built: `docs/superpowers/plans/2026-11-17-swept-body-stage1.md` and branch `freecad/swept-body`
(tip `406f083`). Read the spec's 5.2 and the "Spike result" in 7.1 first.

## Global Constraints

- Everything through pixi:
  - `pixi run -e addon test-addon`
  - `pixi run -e addon pytest tests/freecad_addon/<file> -k <name>`
  - `pixi run lint`
  - `pixi run format`, then revert its change to `highlight.py`.
- Branch `freecad/swept-body` (continue on it). Commit per task, never `--no-verify`, never push or merge.
- Ruff:
  - line length 120, double quotes;
  - no trailing comma on a construct that fits on one line;
  - never reorder imports;
  - format only files you changed.
- Module rules (AGENTS.md):
  - mesher modules (`meshsweep.py`, `meshcommon.py`, ...) never import FreeCAD;
  - `sweeps.py`, `jobwriter.py` and `validation.py` stay GUI-free.
- A Study without a Swept Body meshes exactly as before. Stage 1 straight sweeps mesh as before: their node
  coordinates must not change.
- Grading where a skin applies: first step `δ / ElementsPerDepth`, ratio `1.2`, over `LayerDepth · δ`. It runs toward
  a real end face, with Stage 1's rule: not a cut, and not shared with a body that has its own skin. A closed ring has
  no ends.
- Revolved station spacing: arc length measured at the profile's centroid radius `rc` (distance from the axis to the
  profile face's centre of mass). A piece of angle θ has length `rc · θ` (θ in radians), split with
  `graded_positions(rc · θ, path_size, ...)`, and each position p becomes the angle `p / rc`.
- A helical body (end faces related by a screw motion) is still refused, with the reason
  `"only straight and revolved sweeps are made so far"` (replaces Stage 1's `"only straight sweeps are made so far"`
  everywhere it is used). Stage 3 lifts this.
- Units mm, angles in degrees in the job (`"angle"`), as Stage 1's `Piece`.

## Review Focus

1. **A closed ring whose lateral faces have seams** (OCC revolves a profile into faces with a seam edge at one angle):
   every seam node is classified on its curve; no free faces inside. Task 3 test: `test_swept_closed_ring_is_conformal`.
2. **A ring segment's two planar end faces in air** (a 90° bend): both ends graded with a skin, the steps near the
   ends ≈ δ / ElementsPerDepth in arc length at `rc`. Task 3 test: `test_swept_bend_grades_both_ends`.
3. **A closed ring has no duplicate nodes** where the last station meets the first, and no zero-volume elements.
   Task 3 test: `test_sweep_closed_ring_joins` (unit) and the conformity test above.
4. **A rotation-like body that is not a revolution** (a box whose two side faces happen to match by a rotation, or a
   slot corner) is not called a revolution. Task 1 tests: Stage 1's `test_notched_bar_is_refused` and
   `test_box_without_start_face` stay green; new `test_l_block_is_not_revolved`.
5. **A straight Stage 1 job is unchanged:** a busbar's node coordinates before and after this stage are equal. Task 3
   test: `test_straight_sweep_unchanged_by_stage2`.

---

### Task 1: Recognising revolved sweeps and closed rings

**Files:**
- Modify: `freecad_addon/emsolution/sweeps.py`
- Test: `tests/freecad_addon/test_sweeps.py`

**Interfaces:**
- Produces:
  - `Sweep = namedtuple("Sweep", "profile end pieces closed face")`:
    - `face` is the profile as a `Part.Face` in the solid's coordinates: the start end face, or for a closed ring the
      cut;
    - `profile` and `end` stay face names (both None for a closed ring).

    Update every Stage 1 construction of `Sweep`.
  - A revolved piece: `Piece(origin, axis, angle, 0.0)`.
    - `origin` is the axis point nearest the profile's centre of mass.
    - `axis` is a unit vector, its sign chosen so that a positive `angle` turns the start face onto the end face.
    - `angle` is in degrees, in (0, 360]. It is 360 for a closed ring.
  - `NOT_STRAIGHT` becomes `"only straight and revolved sweeps are made so far"` (helices).
  - New reason, exact text: `"its faces do not all turn about one axis"`, for a body with no end faces that is not a
    closed ring.
- Algorithm:
  - **Part ring.** Stage 1's `_rotation_maps` already finds two end faces related by a rotation, with every other
    face turning about the line. Instead of returning `NOT_STRAIGHT`, return the piece. Add the volume check: Pappus,
    `solid.Volume` = profile area × `rc` × θ (relative 1e-6).
  - **Closed ring** (no end-face pair found):
    - every face is planar with its normal along a common axis, or a surface of revolution about it (cylinder, cone,
      torus, sphere, `SurfaceOfRevolution`). Find the axis from the first non-planar face; check the others with
      `_turns_about`.
    - The profile is the solid cut by the half-plane through the axis. Use `solid.common` with a large planar face
      bounded on one side by the axis, then take the resulting face.
    - Place the half-plane at the angle of an existing meridian edge of the solid, if it has one. A meridian edge is
      a straight or curved edge lying in a plane through the axis: OCC's seam edges, or the joint of two half rings.
      This puts section nodes on the seam curves. Else use angle 0 about the axis, from a perpendicular built from
      the axis direction.
    - Check the volume by Pappus with θ = 2π.
  - Helical ends (a rotation plus a shift along the axis) keep the refusal, with the new `NOT_STRAIGHT` text.

- [ ] **Step 1: Write the failing tests** (shapes built with Part):
  - `test_quarter_ring_is_revolved`:
    - `Part.makeTorus(20, 3, V(0, 0, 0), V(0, 0, 1), -180, 180, 90)` gives one piece with angle 90, advance 0, axis
      ±z, origin on the z axis, `closed` False;
    - `face` is a disc of area π·9.
  - `test_rect_bend_is_revolved`: a 10 × 4 rectangle in the xz plane at x 20..30, revolved 90° about z
    (`face.revolve(V(0,0,0), V(0,0,1), 90)`), gives angle 90.
  - `test_closed_torus_is_a_ring`: `Part.makeTorus(20, 3)` gives `closed` True, angle 360, `profile` None, and
    `face.Area` ≈ π·9.
  - `test_closed_rect_ring`: a 10 × 4 rectangle revolved 360° gives a ring. Its `face` lies in a plane through the
    axis and holds a vertex of the solid's seam edge (the cut is at the seam).
  - `test_l_block_is_not_revolved` (Review Focus 4): an L-shaped extrusion gives a straight sweep or a refusal, never
    a revolved piece.
  - `test_cone_frustum_ring`: a revolved trapezoid (a ring with conical faces) gives a ring.
  - `test_sphere_is_refused`: a sphere gives a refusal (no profile cut gives a valid sweep: the Pappus check fails).
  - `test_helix_still_refused`: a helical pipe gives `"only straight and revolved sweeps are made so far"`. Build it
    with `Part.makeHelix` and `Part.Wire(...).makePipeShell([circle], True, True)`. If FreeCAD cannot make a solid
    that way, replace it with a box rotated and shifted in a way whose ends match by a screw motion.
  - Update the Stage 1 test that expects `"only straight sweeps are made so far"` on the quarter torus: it now expects
    a revolved piece.
- [ ] **Step 2: Run** `pixi run -e addon pytest tests/freecad_addon/test_sweeps.py -v`. Expected: FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `test_sweeps.py`, `test_study.py -k swept`. Expected: PASS (Validate and jobwriter still work
  for straight sweeps).
- [ ] **Step 5: Commit** `FreeCAD add-on: recognise revolved sweeps and closed rings`.

---

### Task 2: Revolved sweeps in Validate and job.json

**Files:**
- Modify: `freecad_addon/emsolution/jobwriter.py` (`swept_entries`), `freecad_addon/emsolution/validation.py`
  (anything that assumed straight pieces or a profile face name)
- Test: `tests/freecad_addon/test_study.py`

**Interfaces:**
- Consumes: Task 1.
- Produces:
  - `swept_entries` exports `sweep.face`, in global coordinates, as each solid's `"profile"`, for straight and revolved
    sweeps alike (a straight sweep's `face` is its start face, so its file is unchanged).
  - A solid entry gains `"closed": bool`.
  - A revolved piece is written as `{"origin": [...], "axis": [...], "angle": a, "advance": 0.0}` in global
    coordinates.
  - Validate accepts revolved and closed bodies. The contact and partial-contact checks run unchanged. A closed ring
    has no StartFace, so a StartFace on a closed ring is an error:
    `f"Swept Body {label}: {name} is a closed ring; it has no start face. Remove the start face."`.

- [ ] **Step 1: Write the failing tests:**
  - `test_swept_ring_goes_to_the_job`: a closed rect ring writes one solid with `"closed": true`, one piece of angle
    360. The profile file holds one planar face whose plane contains the axis.
  - `test_swept_bend_goes_to_the_job`: a 90° bend writes angle 90 and `"closed": false`.
  - `test_swept_ring_start_face_is_refused`.
  - `test_swept_ring_is_valid`: a closed ring in an Air Region gives no Swept Body problem.
- [ ] **Step 2: Run** `pixi run -e addon pytest tests/freecad_addon/test_study.py -k swept -v`. Expected: the new
  tests FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `test_study.py`. Expected: PASS.
- [ ] **Step 5: Commit** `FreeCAD add-on: revolved Swept Bodies in Validate and the mesh job`.

---

### Task 3: Revolved and closed sweeps in the mesher

**Files:**
- Modify: `freecad_addon/emsolution/meshsweep.py`: `stations`, `_transforms`, `_volume_of`, `apply_swept`, `_join`
  where seams need it.
- Test: `tests/freecad_addon/test_meshsweep.py`, `tests/freecad_addon/test_mesher.py`

**Interfaces:**
- Consumes: Task 2's job entries (`"closed"`, revolved pieces).
- Produces:
  - `stations(piece, positions, rc=None) -> list[np.ndarray]`. A straight piece is unchanged. For a revolved piece,
    the positions are arc lengths at `rc` (required), and each transform is the rotation about
    (`origin`, `axis`) by `position / rc` radians.
  - `_transforms` measures each piece's length as `advance` (straight) or `rc · radians(angle)` (revolved). `rc` is
    the distance from the axis to the section's centroid. It also composes pieces, each starting where the last
    ended (Stage 3 will chain mixed pieces; Stage 2 needs one piece). A closed ring has no graded ends, and its last
    position (360°) is dropped; `sweep(..., closed=True)` joins the ring.
  - `_volume_of` maps a solid to its volume by the bounding box of the profile swept along the piece. For a
    rotation, use the box of the profile's corner and centroid points rotated in 10° steps, plus the end. Or use
    `gmsh.model.isInside` at the profile centroid rotated half way. Take whichever is simpler and correct for a
    closed ring.
  - Real curves and real end faces are found by geometry at the half-way station, as Stage 1 does, rotated. A closed
    ring has no end faces.
  - `_join` must classify the section's nodes on OCC seam curves of the revolved faces, and the face elements beside
    the seam. If a periodic face's parametrisation gives a wrong `u` at the seam (0 against 2π), take the
    parametrisation from the neighbouring node, or skip parametric coordinates for that face's nodes. The spike found
    `getParametrization` needed on curves; check what surfaces need.

- [ ] **Step 1: Write the failing tests:**
  - In `test_meshsweep.py`:
    - `test_stations_rotate`: a revolved piece about z through the origin, rc 20, positions 0 and 20·π/2 give the
      identity and a 90° rotation.
    - `test_sweep_closed_ring_joins` (Review Focus 3): a 4-quad section swept closed over 36 stations gives 36 × 4
      hexahedra, 36 × (section nodes) nodes (no duplicates), and positive Jacobians.
  - In `test_mesher.py`, air box 120 × 120 × 60 at size 8 unless said:
    - `test_swept_closed_ring_is_conformal` (Review Focus 1): a closed 10 × 4 rectangle ring (inner radius 20),
      skin δ 1:
      - hexahedra only in the ring;
      - no inner free faces;
      - the ring's element count = section quads × stations;
      - the steps along the ring at `rc` within 25 % of the path size.
    - `test_swept_torus`: `Part`-free BREP of a torus R 20, r 3 (write it with gmsh OCC `addTorus` and export, as the
      Stage 1 tests write their shapes), skin δ 0.5: hexahedra and prisms, conformal.
    - `test_swept_bend_grades_both_ends` (Review Focus 2): a 90° rect bend ending in air, skin δ 1: the first and last
      angular steps at `rc` within 25 % of 0.5; middle steps ≈ path size.
    - `test_straight_sweep_unchanged_by_stage2` (Review Focus 5): Stage 1's `test_swept_bar_with_skin` job gives the
      same bar node coordinates as stored in the test. Generate them once at this task's base commit and store a
      checksum (rounded coordinates sorted, then hashed) in the test.
- [ ] **Step 2: Run** `pixi run -e addon pytest tests/freecad_addon/test_meshsweep.py tests/freecad_addon/test_mesher.py -k "swept or stations or sweep" -v`.
  Expected: the new tests FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `test_meshsweep.py`, `test_mesher.py`, `test_mesher2d.py`, `test_meshgroups.py` in full.
  Expected: PASS.
- [ ] **Step 5: Commit** `FreeCAD add-on: revolved and closed sweeps in the mesher`.

---

### Task 4: The Stage 2 review catalogue rows

**Files:**
- Modify: `experiments/refinement_catalogue/rows.py`

**Interfaces:**
- Consumes: the whole add-on and the SW helpers in `rows.py` (`pad_air`, `sw_report`, `free_faces_inside`). The
  "today" copy keeps the Skin Layers and deletes only the Swept Body items (as for the SW rows).
- Rows (spec 8, Stage 2). Each prints per-part counts today vs new, the air's min SICN and the count below 0.1, and
  free faces inside:

| id | Study | Items | after-check |
|---|---|---|---|
| SW-06 | winding turn: a closed ring of 10 × 4 rectangular section, inner radius 20, copper, size 4, Padding Box air | Skin Layer 1 kHz (δ 2.09); Swept Body | hexahedra only; no free faces inside |
| SW-07 | toroidal conductor: torus R 20, r 3, size 2 | Skin Layer 10 kHz (δ 0.66); Swept Body | hexahedra and prisms; no free faces inside |
| SW-08 | busbar bend: 10 × 4 section revolved 90° about an axis 30 from its inner side, size 4 | Skin Layer 1 kHz; Swept Body | hexahedra only; graded steps at both ends |

Pictures: cut through the ring's plane (z = mid-height) and across the section.

- [ ] **Step 1: Add the rows.** Run `pixi run -e addon python experiments/refinement_catalogue/build_catalogue.py --only SW-06 SW-07 SW-08`.
  Expected: all match.
- [ ] **Step 2: Look at every new picture.** Fix the rows whose picture does not show the swept mesh, then re-run.
- [ ] **Step 3: Run the whole catalogue in the background.** Expected: every row matches.
- [ ] **Step 4: Commit** `Refinement catalogue: Stage 2 rows (revolved Swept Body)`.

---

### Task 5: Stage 2 check and hand-over

- [ ] **Step 1: Run** `pixi run -e addon test-addon` (all pass) and `pixi run lint` (clean). Run the GUI smoke test
  only if GUI code changed.
- [ ] **Step 2: Hand over** `C:\Users\hamed\Desktop\delme\refinement_studies\catalogue.html` with the SW-06 to SW-08
  rows.
- [ ] **Step 3: Stop.** Don't merge or push; the user reviews the rows before Stage 3 is planned.
