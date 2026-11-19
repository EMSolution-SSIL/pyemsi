# Swept Body, Stage 3: helices and joined pieces — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Swept Body also meshes helical bodies (a litz strand, a coil turn with pitch) and bodies whose path is a
chain of straight, arc and helical pieces (a busbar bent line + arc + line), in ordinary 3D Studies. It comes with
the Stage 3 catalogue rows, including litz1's strand as the user built it.

**Architecture:** Stages 1 and 2 already carry the general model: a `Piece` is a screw motion (`angle`, `advance`),
and `meshsweep._chain` composes pieces. This stage adds three things:
- **Recognition (`sweeps.py`).**
  - A helical piece is fitted from a lateral edge that runs from the start face to the end face. The projected
    circle gives the axis, the accumulated angle gives `angle`, and the axial rise gives `advance`. This also covers
    whole-turn helices, whose end faces match by a plain translation.
  - A chain is found by walking from the start face through groups of side faces. Each group's far boundary is a
    planar cross-section wire.
  - One generic check replaces the per-kind side-face checks: every side face is invariant under its piece's screw
    motion.
- **The mesher.** Helical stations, one shared station at every joint between pieces, and real curves and end faces
  found per piece.
- **A FreeCAD pipe whose profile twists along a helix.** This is litz1's default `DiscreteTrihedron` mode. A round
  profile gives the same solid as a Frenet pipe, but its seam edge does not follow the screw motion, so the hand
  mesh cannot meet it. The spike (Task 1) decides between two options:
  - (a) refuse it, with "make the pipe with Frenet mode";
  - (b) have the jobwriter export, for a recognised sweep, the solid rebuilt from its profile and pieces (an exact
    screw sweep), when it equals the original within tolerance.

**Tech Stack:** FreeCAD 1.1 add-on (Python 3.11), gmsh 4.15.2, numpy, pytest via pixi.

**Spec:** `docs/superpowers/specs/2026-11-17-swept-body-prism-layers-design.md` (sections 2, 5.2, 5.4, 7.1 spike
result, 8 Stage 3, 11). Stages 1–2: plans `2026-11-17-swept-body-stage1.md` and `-stage2.md`, branch
`freecad/swept-body` (tip `b4a0693`).

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
- A Study without a Swept Body meshes exactly as before. Stage 1 straight sweeps keep their node coordinates
  (`test_straight_sweep_unchanged_by_stage2`). Stage 2 ring, torus and bend tests stay green.
- **Path length of a piece:** the length of the profile centroid's path, `sqrt((rc·θ)² + advance²)`, where θ is in
  radians and `rc` is the distance of the profile centroid from the axis. A straight piece has length `advance`, a
  revolved one `rc·θ`. A turned piece (θ ≠ 0) keeps Stage 2's minimum of `ceil(angle / 30°)` steps.
- **Station at s along a helical piece** (`0 ≤ s ≤ L`): rotation about (`origin`, `axis`) by θ·s/L, then translation
  by `advance·s/L` along `axis`.
- **Joints:** every joint between two pieces is a station. Pieces with mixed real/cut sides use one section mesh; a
  profile curve is real when its side face is real in any piece.
- **Grading:** toward a real end face (first piece's start, last piece's end) only, with Stage 1's rule.
- **Volume check for any screw piece:** `V = A · |n · (θ·(axis × (c − origin)) + advance·axis)|`, with A the profile
  area, n its unit normal, c its centroid and θ in radians. Relative tolerance 1e-6, summed over the pieces of a
  chain. This reduces to Stage 1's check (θ = 0) and Pappus (advance 0).
- **The refusal for what is still not handled** (free-form spline paths, lofts, twisting profiles if the spike picks
  (a)) uses the exact texts below. `NOT_STRAIGHT` ("only straight and revolved sweeps are made so far") is retired.
  - `"its path is not made of straight, arc and helical pieces"`;
  - `"the profile twists along the path; make the pipe with Frenet mode"` (only if (a)).

## Review Focus

1. **A whole-turn coil** (ends related by a plain translation of one pitch): recognised as a helix with angle 360·k,
   not refused as a bad straight sweep. Task 2 test: `test_whole_turn_coil_is_a_helix`.
2. **litz1's strand as the user built it** (`DiscreteTrihedron` pipe on a Part Helix, 1.5 turns): it either meshes,
   (b), or is refused with the Frenet message, (a). It never fails late in the mesher. Task 5 row: SW-13.
3. **Joints where the side faces change** (line → arc): the section nodes at the joint lie on the joint curves, and
   there are no free faces inside. Task 4 test: `test_swept_bent_busbar_is_conformal`.
4. **A chain with a cut side in one piece only** (a bent busbar half on a symmetry plane): the curve is real (it is
   real in another piece), the mesh is conformal, and a note is printed. Task 4 test:
   `test_swept_chain_mixed_real_sides`.
5. **Stage 1–2 shapes still recognised the same way:** box, cylinder, ring, torus and bend give the same pieces as
   before. Task 2: the existing `test_sweeps.py` tests stay green unchanged, except the retired helix text.

---

### Task 1: Spike: helices from FreeCAD pipes

**Files:**
- Throwaway scripts in the scratchpad only. Modify the spec: add a "Spike result (Stage 3)" paragraph at the end of
  7.1, not committed (specs stay untracked).

**Interfaces:**
- Produces the decisions the rest of the plan reads:
  1. How to fit a screw piece from FreeCAD helix pipes: the lateral edge fit described above, or something better.
  2. Whether option (b) works: rebuild the solid from the profile and pieces with `Part.Wire(helix).makePipeShell([profile_wire], True, True)` in Frenet mode, or `Part.makeHelix` with `isFrenet`. Check that it equals the original (volume, `distToShape` of sample points both ways) and meshes through the Stage 2 mesher path (export, `meshsweep`, conformal) where the original does not.
- Shapes:
  - litz1's strand (rebuild in a fresh document like litz1: Part Helix r 1.2, pitch 10, height 15; circle r 0.45;
    PartDesign AdditivePipe, or Part Sweep with `Frenet = False` and the default transition);
  - the same strand with Frenet;
  - a whole-turn coil turn (rectangle 2 × 4, helix r 20, pitch 6, 1 turn, Frenet);
  - a rectangular profile on a non-Frenet helix (does the profile really twist, so that (b) changes the shape and
    must be refused?).

- [ ] **Step 1:** For each shape, record whether the lateral-edge fit gives axis, angle and advance (and the error),
  the volume-check error, and whether a side face is invariant under the screw within tolerance.
- [ ] **Step 2:** Try (b) on the round non-Frenet strand. Record equality and the mesher result (conformal or not,
  air min SICN).
- [ ] **Step 3:** Decide (a) or (b) and record it in spec 7.1, with numbers. Rule: (b) only if the rebuilt solid
  equals the original within 1e-6 × size and meshes conformally. A twisting non-round profile (shape changed) is
  refused either way. **If neither the fit nor the rebuild works for litz1's strand, stop and report to the user.**

---

### Task 2: Recognising helices and chains

**Files:**
- Modify: `freecad_addon/emsolution/sweeps.py`
- Test: `tests/freecad_addon/test_sweeps.py`

**Interfaces:**
- Consumes: Task 1's decision.
- Produces:
  - Helical pieces `Piece(origin, axis, angle, advance)` with both non-zero. The axis sign gives positive `angle` from
    start to end; `advance` is signed along `axis`.
  - Chains: `Sweep.pieces` has several pieces, in path order, each starting where the last ended.
  - `_invariant(face, piece, origin_state, tol) -> bool`: the side-face check. Points sampled on the face (inside its
    trimmed domain: use `face.Surface` with `face.isInside` or the face's tessellation vertices), moved by fractions
    0.25, 0.5 and 0.75 of the piece's motion, still lie on the face (`distToShape` < tol). This replaces
    `_runs_along` and `_turns_about` for every piece kind; keep the old functions only if something else uses them.
  - The volume check from Global Constraints, for every piece kind.
  - The new reason texts from Global Constraints, replacing `NOT_STRAIGHT`.
  - If Task 1 picks (a): the twisting-profile reason when the round-profile seam check fails. That is, the side
    surface is invariant but a seam edge is not. If (b): `Sweep` gains `rebuild: bool`, true when the solid must be
    exported rebuilt.
- Algorithm (chain walk):
  1. Start from the start face, given or found as in Stage 1–2.
  2. The current boundary is that face's outer wire. The side faces touching the current boundary, plus the faces
     reached from them through edges that are neither on the current boundary nor planar cross-section wires, form
     the piece.
  3. The piece's far boundary is the set of its edges shared with the next group of faces (or the end face). They
     must form a closed planar wire congruent with the profile.
  4. Fit the screw that maps the current boundary onto the far boundary: try translation, then rotation (Stage 2),
     then the helix edge fit.
  5. Check `_invariant` on the piece's faces, then continue from the far boundary.
  6. Stop at a planar end face (open path) or back at the start boundary (closed path; Stage 2's ring stays a
     one-piece ring).

  A body with one group is Stage 1–2's single piece: the existing tests must give the same pieces.

- [ ] **Step 1: Write the failing tests:**
  - `test_helix_strand_is_a_helix`: a round profile r 0.45 on a Frenet helix r 1.2, pitch 10, 1.5 turns gives one
    piece with angle 540, advance 15, an axis along the helix axis, and an origin on it.
  - `test_whole_turn_coil_is_a_helix` (Review Focus 1): a 2 × 4 rectangle on a Frenet helix r 20, pitch 6, 1 turn
    gives angle 360 and advance 6.
  - `test_bent_busbar_is_a_chain`: a 10 × 4 profile swept along line 30 + arc r 20 90° + line 30 (a Part wire,
    `makePipeShell` Frenet) gives three pieces: advance 30, angle 90, advance 30.
  - `test_spline_path_is_refused`: a pipe along a B-spline gives `"its path is not made of straight, arc and helical pieces"`.
  - `test_non_frenet_strand` gives the (a) reason or `rebuild` True, per Task 1.
  - `test_loft_is_still_refused`.
  - Update the Stage 2 tests that expect the helix refusal.
- [ ] **Step 2: Run** `pixi run -e addon pytest tests/freecad_addon/test_sweeps.py -v`. Expected: FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `test_sweeps.py` and `test_study.py -k swept`. Expected: PASS; the box, cylinder, ring, torus,
  bend and tube results are unchanged.
- [ ] **Step 5: Commit** `FreeCAD add-on: recognise helical and chained sweeps`.

---

### Task 3: Helices and chains in Validate and job.json

**Files:**
- Modify: `freecad_addon/emsolution/jobwriter.py`, `validation.py`
- Test: `tests/freecad_addon/test_study.py`

**Interfaces:**
- Consumes: Task 2.
- Produces:
  - Pieces of every kind are written as Stage 1–2 do. A chain writes all its pieces.
  - If (b): when `rebuild` is true, the body's `geometry/vol_<m>.brep` holds the rebuilt solid, made from the profile
    and the pieces in global coordinates. The jobwriter builds it with the same Part calls the spike used, and checks
    it equals the original. If it does not, Validate refuses the body with the twisting-profile reason. Neighbours'
    files are unchanged.
  - Validate: no new messages beyond the reasons, and every Stage 1–2 check runs as before.

- [ ] **Step 1: Write the failing tests:**
  - `test_swept_helix_goes_to_the_job`: the 1.5-turn strand writes one piece with angle 540, advance 15.
  - `test_swept_chain_goes_to_the_job`: the bent busbar writes three pieces in order, each starting where the last
    ended (the start of piece 2 is the end of piece 1 within 1e-6).
  - If (b): `test_swept_rebuilt_strand_exports_the_rebuilt_solid`. The vol file's solid has the screw-invariant seam,
    and its volume is within 1e-6 of the original's.
- [ ] **Step 2: Run** `pixi run -e addon pytest tests/freecad_addon/test_study.py -k swept -v`. Expected: the new
  tests FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `test_study.py`. Expected: PASS.
- [ ] **Step 5: Commit** `FreeCAD add-on: helical and chained Swept Bodies in Validate and the mesh job`.

---

### Task 4: Helices and chains in the mesher

**Files:**
- Modify: `freecad_addon/emsolution/meshsweep.py` (`stations`, `_chain`, `_transforms`, real curves per piece)
- Test: `tests/freecad_addon/test_meshsweep.py`, `tests/freecad_addon/test_mesher.py`

**Interfaces:**
- Consumes: Task 3's job entries.
- Produces:
  - `stations(piece, positions, rc=None)` handles helical pieces (Global Constraints). The positions are path lengths
    along the centroid path.
  - `_chain` / `_transforms` use the path-length formula for every piece and put a station at every joint. Positions
    are made per piece: graded at the chain's real ends only, with the turned-piece minimum and the vertex-angle cuts
    of Stage 2 for each turned piece.
  - Real curves: a profile curve is real when its side face is real at any piece's half-way station.
    `_note(f"Swept Body {name}: a side of MAT_ID {m} is a cut in one piece and real in another; it gets the skin everywhere")`
    when they differ.

- [ ] **Step 1: Write the failing tests:**
  - In `test_meshsweep.py`:
    - `test_stations_helix`: a piece with angle 360 and advance 6 about z, rc 20: s = L/2 gives a 180° rotation plus
      a rise of 3.
    - `test_chain_joints_are_stations`: line 30 + arc 90° (rc 25) + line 30 at path size 4. The transforms include
      the exact joint positions, and consecutive stations never repeat.
  - In `test_mesher.py` (shapes written with gmsh OCC: `addPipe` along a wire, or `addHelix`-like points; follow how
    Stage 1–2 tests build theirs):
    - `test_swept_helix_strand_is_conformal`: the 1.5-turn round strand (r 0.45, helix r 1.2, pitch 10) in an air box
      6 × 6 × 25, skin δ 0.2. It has hexahedra and prisms, no inner free faces, and stations every path size along the
      helix within 25 %.
    - `test_swept_coil_turn`: the whole-turn 2 × 4 coil turn: hexahedra only, conformal.
    - `test_swept_bent_busbar_is_conformal` (Review Focus 3): hexahedra only, conformal, a station at each joint.
    - `test_swept_chain_mixed_real_sides` (Review Focus 4): the bent busbar cut in half by the air box's outer face
      along one straight leg only. Conformal, and the note is printed.
    - The Stage 1 checksum test and the Stage 2 ring, torus and bend tests stay green.
- [ ] **Step 2: Run** `pixi run -e addon pytest tests/freecad_addon/test_meshsweep.py tests/freecad_addon/test_mesher.py -k "swept or stations or chain" -v`.
  Expected: the new tests FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** the four mesher test files in full. Expected: PASS.
- [ ] **Step 5: Commit** `FreeCAD add-on: helical and chained sweeps in the mesher`.

---

### Task 5: The Stage 3 review catalogue rows

**Files:**
- Modify: `experiments/refinement_catalogue/rows.py`

**Interfaces:**
- Consumes: the whole add-on and the SW helpers. Shapes are built with FreeCAD Part or PartDesign as a user would.
  Each row prints per-part counts today vs new, the air's min SICN with the count below 0.1, free faces inside, and
  steps along the path.

| id | Study | Items | after-check |
|---|---|---|---|
| SW-09 | one litz strand: round r 0.45 on a Frenet helix r 1.2, pitch 10, 1.5 turns, copper, size 0.3, Padding Box air | Skin Layer 100 kHz (δ 0.21); Swept Body | hexahedra and prisms; conformal |
| SW-10 | coil turn: 2 × 4 rectangle on a Frenet helix r 20, pitch 6, 1 turn | Skin Layer 10 kHz (δ 0.66); Swept Body | hexahedra only; conformal |
| SW-11 | bent busbar: 10 × 4 along line 30 + arc r 20 90° + line 30 | Skin Layer 1 kHz (δ 2.09); Swept Body | hexahedra only; a station at each joint; graded both ends |
| SW-13 | litz1's strand as the user built it: open `C:\Users\hamed\Desktop\delme\litz\litz1.FCStd` read-only, copy the strand body into a fresh Study (save nothing back), one strand in air | Skin Layer 100 kHz; Swept Body | (b): meshes conformally; (a): the Validate refusal with the Frenet message is printed |

- [ ] **Step 1: Add the rows.** Run `pixi run -e addon python experiments/refinement_catalogue/build_catalogue.py --only SW-09 SW-10 SW-11 SW-13`.
  Expected: all match.
- [ ] **Step 2: Look at every new picture** (cut through the helix axis, and across the section). Fix the rows whose
  picture does not show the swept mesh.
- [ ] **Step 3: Run the whole catalogue in the background.** Expected: every row matches.
- [ ] **Step 4: Commit** `Refinement catalogue: Stage 3 rows (helical and chained Swept Body)`.

---

### Task 6: Stage 3 check and hand-over

- [ ] **Step 1: Run** `pixi run -e addon test-addon` (all pass) and `pixi run lint` (clean).
- [ ] **Step 2: Hand over** the catalogue with the SW-09 to SW-13 rows, and the spike's decision on litz1's
  non-Frenet pipe.
- [ ] **Step 3: Stop.** Don't merge or push; the user reviews before Stage 4 (symmetric cells, litz1 whole) is
  planned.
