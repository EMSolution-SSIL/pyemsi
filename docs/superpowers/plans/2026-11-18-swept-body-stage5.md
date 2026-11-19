# Stage 5: 3D prism layers Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A Skin Layer with `QuadLayers` ticked in a 3D Study grows prism layers inward from the body's real surface and fills the core with tetrahedra. Bodies with sharp edges, or with cuts that are not flat and square to the surface, get today's graded tetrahedra, with a Validate warning and a mesher note.

**Architecture:** A new mesher module `meshlayers.py` works like `meshsweep.py`:
- gmsh meshes the body's curves and real faces in the main model, with the body's volume and its cut faces hidden.
- At the 3D stage, the layered mesh is built from that surface mesh in numpy: nodes moved inward along mean normals, prisms between the copies, caps on the flat cut faces, and the core in a gmsh sub-model.
- Nothing is written to the main model until the whole body's mesh is built. It then goes onto the body's volume and cut faces, and gmsh meshes the rest (`MeshOnlyEmpty`), as for swept bodies.
- If the build fails, the body is unhidden and meshed as today.
- Symmetric cells reuse Stage 4's hand-mesh path. Their seams with their own copies get one cap, moved onto the other seam, and the seam's rim curves are paired periodic.

**Tech Stack:** Python 3.11, gmsh 4.15.2, numpy, FreeCAD 1.1 (jobwriter and validation only), pixi.

**Spec:** `docs/superpowers/specs/2026-11-17-swept-body-prism-layers-design.md`: section 6, spike result 7.2, section 8 Stage 5, calls 6, 8 and 9 in section 11.

## Global Constraints

- **Mesher process:** `meshlayers.py` is a mesher module. It never imports FreeCAD, and it imports its siblings by plain module name (`import meshcommon`, not relative). Add it to the mesher module list in `AGENTS.md`.
- **GUI-free modules:** `jobwriter.py` and `validation.py` stay GUI-free. GUI code is only in `taskpanels.py`.
- **Formatting:**
  - Ruff, line length 120. Format with `pixi run format`, then revert its change to `freecad_addon/emsolution/highlight.py`.
  - Never sort or reorder imports.
  - `pixi run lint` must pass.
- **Tests:**
  - `pixi run -e addon test-addon`.
  - A GUI change needs the smoke test: `pixi run -e addon freecad tests\freecad_addon\gui_smoke.py` from PowerShell with a timeout, then read the last line of `%TEMP%\ems_gui_smoke.txt`.
- **Layers:** the first layer is δ / ElementsPerDepth, the ratio is 1.2, and the total is LayerDepth · δ (spec 6).
  - Number of layers: the n whose geometric sum h·(1.2ⁿ − 1)/0.2 (h = δ / ElementsPerDepth) is closest to LayerDepth · δ, with n ≥ 1.
  - All heights are then scaled so they sum to exactly LayerDepth · δ.
- **Surface triangles:** today's graded skin sizes (`meshcommon.skin_refinements`) unchanged (spec 6).
- **Smooth bodies only** (spec call 6):
  - Two real faces of the body meet with their normals turning by at most 15° along their shared curve.
  - A cut face is planar, and the real faces meet it within 30° of square (|real normal · cut normal| ≤ 0.5).
  - Every curve of a cut face is shared with a real face of the same body.
  - Anything else gets graded tetrahedra.
- **Real surface:** in an ordinary Study, `meshcommon.real_boundary(3, [vol])`. In a cell job, the entry's `"faces"` plus faces against other cell volumes that are not images (as `meshsweep._real_faces`). Every other face of the body is a cut.
- **No silent fallback** (spec anti-goal): every body that asked for prism layers and does not get them prints exactly one mesher note.
- **Unchanged mesh:** a Study without `QuadLayers` ticked in 3D gives the same mesh as before, node for node.
- **Never push or merge.**

**Exact texts.** `{s}` is the Skin Layer's Label, `{name}` the body's display name, `{e}` the skin entry's name, `{m}` the MAT_ID.

Validate warnings:
- V1: `Skin Layer {s}: {name} has sharp edges on its surface; prism layers need a smooth surface, so it gets graded tetrahedra.`
- V2: `Skin Layer {s}: {name} is cut by a curved face or at a slant; prism layers need flat cuts square to its surface, so it gets graded tetrahedra.`
- V3: `Skin Layer {s}: {name} is a sweep; a Swept Body on it gives fewer and better elements than prism layers.`
- V4 (the existing free-object warning, 3D words): `Skin Layer {s}: prism layers are not made on free objects of a Study with Symmetric Groups; {name} gets graded tetrahedra.`
- V5 (the existing recombined warning, 3D words): `Skin Layer {s}: {name} is recombined; it gets the graded layer but no prism layers.`
- V6: `Skin Layer {s}: {name} meets a copy of another cell object on a cut; prism layers need its cuts to be seams with its own copies, so it gets graded tetrahedra.`

Mesher notes (through `meshcommon._note`):
- N1: `Skin Layer {e}: MAT_ID {m} has a sharp edge on its surface; graded tetrahedra instead of prism layers`
- N2: `Skin Layer {e}: MAT_ID {m} is cut by a curved face or at a slant; graded tetrahedra instead of prism layers`
- N3: `Skin Layer {e}: MAT_ID {m}: the prism layers would fold (the layer is too deep for its curves); graded tetrahedra instead`
- N4: `Skin Layer {e}: MAT_ID {m}: gmsh could not fill the core inside the prism layers ({gmsh's message}); graded tetrahedra instead`
- N5: `Skin Layer {e}: MAT_ID {m} meets a copy of another cell on a cut; graded tetrahedra instead of prism layers`
- N6: `Skin Layer: the 3D algorithm is set to Delaunay so the mesh can meet the prism layers`. Only when the user's Algorithm3D is not 1 and no swept body already printed the Swept Body note.

## Review Focus

- **A layer deeper than a curve allows** (the spike's r 2.4 busbar, or a thin wire with a 2 δ layer): this must never write folded prisms. Expect note N3, today's mesh, and the job still meshing. Task 1 tests the fold count, Task 2 the end-to-end fallback.
- **Cut faces against another body** (a wire end against a terminal): the neighbour meets the layer's quads. Expect pyramids from Delaunay and no unmatched faces. Task 2 test `test_layered_wire_end_against_terminal`.
- **Two Skin Layers on one body, or one Skin Layer on a body with several solids** (a coil compound): the first skin in job order makes the layers, as `apply_quad_layers` does in 2D. Each solid is layered on its own. Task 2 test `test_layered_two_solids_one_mat_id`.
- **Element count through the write** (the spike lost 9 of 3898 core tetrahedra between building and the written file): the written body has exactly the prisms and core tetrahedra that were built. Task 2 test `test_layered_sphere_in_air`.
- **Global gmsh options leak through sub-models:** options are global, so a sub-model that changes `Mesh.MeshOnlyVisible`, `Mesh.MeshSizeMax` or the like and does not restore them changes the main model's air mesh. Task 1 test `test_core_restores_options`.

---

### Task 1: Layer builder (`meshlayers.py`, pure numpy plus gmsh sub-models)

**Files:**
- Create: `freecad_addon/emsolution/meshlayers.py`
- Modify: `AGENTS.md` (add `meshlayers.py` to the mesher module list)
- Test: `tests/freecad_addon/test_meshlayers.py`

**Interfaces:**
- Produces:
  - `heights(depth: float, per_depth: float, layer: float) -> list[float]`: the cumulative heights of the n layers.
  - `class LayerFailed(Exception)`: has `kind` (`"fold"` or `"core"`) and `detail` (str, gmsh's message for `"core"`).
  - `normals(X, tris, fixed) -> np.ndarray (n, 3)`. `X` is (n, 3), `tris` is (m, 3) indexes oriented outward, and `fixed` is {node index: unit vector} (the rim nodes). The result is the angle-weighted mean of the triangles' outward unit normals; fixed nodes take their given vector. Unit length.
  - `folded(layers: list[np.ndarray], tris) -> int`: prisms with a corner volume ≤ 0, checked at all three corners on both the bottom and the top triangle, as in the spike.
  - `cap(loop: np.ndarray (k, 3), holes: list[np.ndarray], size: float) -> (interior coords (q, 3), triangles (t, 3))`. Triangle indexes count the loop first, then the holes in order, then the interior nodes. It is meshed in its own model as a `geo` plane surface whose lines get 2 nodes each.
  - `core(inner: np.ndarray, tris, caps: list[(coords, tris)], size_in: float, size_out: float) -> (interior coords (q, 3), tets (t, 4))`. Indexes count `inner` first, then each cap's interior nodes in order. It is meshed in a sub-model:
    - the inner surface and the caps are discrete surfaces in one `geo` surface loop and volume;
    - Algorithm3D 1;
    - sizes from a Threshold on the Distance to the inner surface, `size_in` at 0 growing to `size_out` at 2 · `size_out`.
    - A gmsh exception becomes `LayerFailed("core", message)`.
  - `build(X, tris, rims, heights, size_in, size_out, seams=()) -> Layered`:
    - `rims`: {cut face tag: `Rim(plane_normal, edges (k, 2) node indexes, normal {node index: unit vector})`}.
    - `seams`: (slave face, master face, 4x4 row-major list) triples. The slave's cap is the master's cap moved by the matrix, its nodes matched to the slave's rim by nearest point.
    - `Layered` is a dataclass: `coords` (N, 3) of the new nodes; `where` (N,) entries `(3, 0)` for the volume or `(2, face tag)` for a cut face; `prisms` (p, 6) and `tets` (t, 4) indexing `X` then `coords`; `faces` {cut face tag: (quads (a, 4), triangles (b, 3))} indexing the same way.
    - Raises `LayerFailed("fold")` when `folded(...) > 0`.
    - Prism node order is bottom (a, c, b), top (a′, c′, b′) for an outward triangle (a, b, c), so gmsh's Jacobian is positive.

- [ ] **Step 1: Write the failing tests** in `tests/freecad_addon/test_meshlayers.py`.
  - A helper meshes an OCC shape's surface in gmsh at a given size and returns `X` and the outward `tris`.
  - Tests:
    - `test_heights`: `heights(1, 2, 2)` == pytest.approx([0.5494, 1.2088, 2.0])
      - n = 3; raw sums 0.5, 1.1, 1.82; scaled × 2 / 1.82.
      - `heights(1, 4, 1)` has its first value within 10% of 0.25 and its last == 1.0.
    - `test_sphere_layers`: sphere r 5, size 1, `heights(1, 2, 2)`.
      - `len(layered.prisms) == 3 * len(tris)` and `folded == 0`.
      - Core tets > 0.
      - Every tet's signed volume > 0.
      - Every node of `layered.coords` with `where == (3, 0)` is inside the sphere by at least 0.5 − 1e-9.
    - `test_rounded_busbar_layers`: box 20 x 10 x 8 with all 12 edges filleted r 3, size 1: no fold, core tets > 0.
    - `test_thin_strip_folds`: box 20 x 8 x 5 with all edges filleted r 2.4. `build` raises `LayerFailed` with kind `"fold"` or `"core"`.
    - `test_wire_with_cut_ends`: cylinder r 1, length 10, size 0.2, layer heights for δ 0.2, 2 per depth, LayerDepth 2. The two end discs are cuts, with `Rim` normals taken from the cylinder.
      - `faces[c]` has `len(edges) * 3` quads and > 0 triangles.
      - No fold.
      - The faces of all elements that only one element has are exactly the outer side triangles plus the cut-face elements.
    - `test_seam_cap_moved`: the quarter torus (R 4, r 1, cut by x ≥ 0, y ≥ 0) with `seams=[(slave, master, rotation by 90° about z)]`. The slave cap's coordinates equal the master's rotated within 1e-9 × size.
    - `test_core_restores_options`:
      - Set `Mesh.MeshOnlyVisible` 1, `Mesh.MeshSizeMax` 7, `Mesh.MeshSizeExtendFromBoundary` 0 and `Mesh.Algorithm3D` 10.
      - Run `core` and `cap`.
      - All four are unchanged, and the current model is the one set before.

- [ ] **Step 2: Run them, expect failure.** Run `pixi run -e addon pytest tests/freecad_addon/test_meshlayers.py -v`. Expected: ImportError, no `meshlayers`.

- [ ] **Step 3: Implement `meshlayers.py`** with the interfaces above. The spike scripts are the reference algorithm. Keep the per-triangle loops in numpy (`np.add.at` for the normals, vectorised corner volumes).
  - Every gmsh option a sub-model sets is saved and restored in a `finally`.
  - The sub-model is removed, and the caller's model is current again.
  - The module docstring says what the module does and that it never imports FreeCAD.

- [ ] **Step 4: Run the tests, expect PASS.** Run `pixi run -e addon pytest tests/freecad_addon/test_meshlayers.py -v`, then `pixi run lint`.

- [ ] **Step 5: Commit** with the message `FreeCAD add-on: prism layer builder for 3D skins (meshlayers)`.

### Task 2: Prism layers in ordinary 3D Studies (job key, mesher, generate)

**Files:**
- Modify: `freecad_addon/emsolution/jobwriter.py:329` (`"quads"` in 3D too)
- Modify: `freecad_addon/emsolution/meshlayers.py` (add `apply_layers`)
- Modify: `freecad_addon/emsolution/mesher.py` (call it after `meshsweep.apply_swept`; report line)
- Modify: `freecad_addon/emsolution/meshcommon.py` (`generate`, `_mesh_swept`)
- Test: `tests/freecad_addon/test_mesher.py` (a new class beside the swept tests, using the same `run_job`, `vol`, `geo` and `open_msh` helpers)

**Interfaces:**
- Consumes: Task 1's `build`, `heights`, `LayerFailed` and `Rim`.
- Produces:
  - `meshlayers.apply_layers(job, body_vols, sizes, skin_faces=None) -> list[int]`, called at the end of `mesher.build`. It returns the volumes it will layer.
    - It goes through the `job["skin"]` entries with `"quads"`, in order. The first entry wins per MAT_ID.
    - MAT_IDs that are swept, structured or recombined are skipped, as in `apply_quad_layers`.
    - For each volume of a MAT_ID it decides the real faces and cuts (Global Constraints), and checks smoothness and cuts before generate: notes N1 and N2, no layers.
    - It extends three job keys:
      - `job["layer_tags"]`: the volumes.
      - `job["layer_hidden"]`: the volume and its cut faces as dimtags.
      - `job["swept_add"]`: one `add(d)` per volume, which does nothing for d < 3.
    - At d == 3, `add` reads the real faces' surface mesh and orients it outward with the CAD normal, as in spike 7.2b. It then calls `build`, writes nodes and elements with explicit tags from `getMaxNodeTag` and `getMaxElementTag` (parametric coordinates on cut faces from `getParametrization`), and appends the MAT_ID to `job["layered"]`.
    - On `LayerFailed` it writes nothing, unhides that volume's `layer_hidden`, and prints N3 or N4.
    - `size_in` is the median edge of the inner surface; `size_out` is `sizes[mat_id]`.
    - Rim normals are the adjacent real face's CAD normal at the node (`getParametrization` and `getNormal`, signed by the face's orientation in the volume), projected into the cut plane.
  - `meshcommon.generate`: takes the hand-mesh path when `job.get("swept_tags") or job.get("layer_tags")`. `_mesh_swept` hides `layer_hidden` without `recursive`, sets the Delaunay and pyramid options for layers as for swept bodies (note N6), and unhides them in its `finally`.
  - `mesher.run_job` prints `Prism layers    {volume name}` for each MAT_ID in `job["layered"]`.

- [ ] **Step 1: Record today's checksum.** At the current HEAD (before any change), take a 3D job: a copper bar 10 x 4 x 100 at size 4 in a 30 mm air box, with a Skin Layer at 1 kHz, LayerDepth 3 and `"quads": false`. Hash its node coordinates the way `test_ordinary_swept_unchanged_by_stage4` does. Put the hash into `test_graded_skin_unchanged_by_stage5`.

- [ ] **Step 2: Write the failing tests.** Each runs a job through `run_job` and opens the mesh.
  - `test_graded_skin_unchanged_by_stage5`: the Step 1 job gives the recorded hash.
  - `test_layered_sphere_in_air`: copper sphere r 5, size 2, in a box of 40 at size 4. Skin depth 1, 2 per depth, LayerDepth 2, `"quads": true`.
    - The sphere's elements are prisms and tetrahedra only.
    - Prisms == 3 × the triangles on its face, and core tets == the count `build` made (read from a debug print or by rebuilding: the implementer's choice).
    - No unmatched faces (the spike's face count).
    - Air min SICN > 0.2.
    - stdout has `Prism layers` and the sphere's name.
  - `test_layered_disc_falls_back`: cylinder r 6, height 3. stdout has N1 for its MAT_ID. Tetrahedra only, and the same node hash as the same job with `"quads": false`.
  - `test_layered_fold_falls_back`: the r 2.4 busbar of Task 1. stdout has N3 or N4. Tetrahedra only, and the job succeeds.
  - `test_layered_wire_through_box`: wire r 1 along x, its ends on the box's faces. Prisms > 0, no unmatched faces, and the end faces carry quads and triangles.
  - `test_layered_wire_end_against_terminal`: as above, but one end against a copper block 4 x 4 x 4 (tetrahedra). The block has pyramids, and there are no unmatched faces.
  - `test_layered_two_solids_one_mat_id`: two spheres r 3, 10 apart, under one MAT_ID. Both layered: prism count == 3 × the triangles of both faces.
  - `test_layered_slanted_cut`: a wire r 1 whose end is cut by a plane at 45°. N2, tetrahedra only.

- [ ] **Step 3: Run them, expect failure.** Run `pixi run -e addon pytest tests/freecad_addon/test_mesher.py -k "layered or stage5" -v`. Expected: the layered tests fail (no prisms), and the checksum test passes.

- [ ] **Step 4: Implement** the interfaces above. In `jobwriter.skin_entries`, `"quads"` becomes `bool(item.QuadLayers and quads)`; leave its docstring's "2D only" line out. Check that `mesher2d` and `meshsweep` read `"quads"` only for 2D sections, so 2D jobs are unchanged.

- [ ] **Step 5: Run the tests, expect PASS.** Run `pixi run -e addon pytest tests/freecad_addon/test_mesher.py tests/freecad_addon/test_mesher2d.py tests/freecad_addon/test_meshsweep.py -v`, then `pixi run lint`.

- [ ] **Step 6: Commit** with the message `FreeCAD add-on: prism layers in 3D Skin Layers (ordinary Studies)`.

### Task 3: Validate, panel and property text

**Files:**
- Modify: `freecad_addon/emsolution/validation.py`, `_skin_layers` (about lines 327-410), plus a new `_sharp_3d`
- Modify: `freecad_addon/emsolution/taskpanels.py:1427-1430` (checkbox in 3D)
- Modify: `freecad_addon/emsolution/objects.py:381` (tooltip)
- Test: `tests/freecad_addon/test_study.py` (the two asserts of the old warning at about 2219 and 2524 change)

**Interfaces:**
- Consumes: `validation.free_faces`, `geometry.global_shape`, `sweeps.recognise_body`.
- Produces:
  - `_sharp_3d(study, body, shape, bodies, layer) -> str | None`: `"edge"` (V1), `"cut"` (V2), or None.
    - Real faces: faces shared with another meshed body or inside the Air Region (as 2D `_sharp` decides its edges). For a cell object: its faces toward other cell objects of its groups and its `free_faces`.
    - Cuts: the rest of the body's faces.
    - The checks are those of the Global Constraints, sampled at the quarter points of each shared edge.
  - In `_skin_layers`, for a 3D Study with `QuadLayers`:
    - The warning "quad layers are made in 2D Studies only; ignored." is gone.
    - V4 replaces the free-object warning in 3D, and V5 the recombined one. The 2D texts are unchanged.
    - V1 or V2 when `_sharp_3d` says so.
    - V3 when `sweeps.recognise_body(shape)` finds a sweep and the body is in no Swept Body item.
    - V6 for a cell object one of whose cuts lies against a copy of another cell object of its group. Use the same face test as Stage 4's check of a swept cell against another cell's copy.
    - Each warning highlights `[(b, "")]`.
  - Panel: the checkbox shows in both dimensions, labelled `Quad layers` in 2D and `Prism layers` in 3D.
  - Property tooltip: `Quad layers (2D) or prism layers (3D) along smooth surfaces`.

- [ ] **Step 1: Write the failing tests** in `tests/freecad_addon/test_study.py`, next to the existing Skin Layer tests.
  - `test_prism_layers_no_ignored_warning`: a 3D sphere with QuadLayers. No warning containing "2D Studies only".
  - `test_prism_layers_sharp_edges`: a 3D box with QuadLayers gives exactly V1.
  - `test_prism_layers_slanted_cut`: a cylinder in a Box Air Region that cuts it at 45°. V2.
  - `test_prism_layers_sweep_hint`: a straight cylinder ending on the Air Region's faces. V3, and no V1 or V2.
  - `test_prism_layers_free_object`: a grouped 3D Study, a free object with QuadLayers. V4.
  - The two existing asserts at about lines 2219 and 2524 now expect no "2D Studies only" warning.
  - Rerun the existing `test_core_code_knows_no_device`.

- [ ] **Step 2: Run them, expect failure.** Run `pixi run -e addon pytest tests/freecad_addon/test_study.py -k "prism_layers or skin" -v`.

- [ ] **Step 3: Implement** the interfaces above.

- [ ] **Step 4: Run the tests, expect PASS.** Run `pixi run -e addon pytest tests/freecad_addon/test_study.py tests/freecad_addon/test_rules_end_to_end.py -v`, then `pixi run lint`.

- [ ] **Step 5: Smoke test.** From PowerShell: `pixi run -e addon freecad tests\freecad_addon\gui_smoke.py` with a timeout, then read the last line of `%TEMP%\ems_gui_smoke.txt`. Expected: `PASS`.

- [ ] **Step 6: Commit** with the message `FreeCAD add-on: Validate and panel for 3D prism layers`.

### Task 4: Prism layers on cells of Symmetric Groups

**Files:**
- Modify: `freecad_addon/emsolution/meshlayers.py` (`apply_layers` in cell jobs: real faces, and cuts that must be seams)
- Modify: `freecad_addon/emsolution/meshgroups.py`: `_with_swept`, `_swept_faces`, `_check_swept_seams`, and the deferred pairing given to `_generate_cell`
- Test: `tests/freecad_addon/test_meshgroups.py` (or `test_symmetric_study3d.py`, wherever Stage 4's swept-cell tests live; put these beside them)

**Interfaces:**
- Consumes: Task 2's `layer_tags`, `layer_hidden` and `swept_add`. Stage 4's `_seam_transforms`, `meshsym._twin`, `meshsym._side_seams` and `_image_faces`.
- Produces:
  - `_with_swept` also carries `layer_tags`, `layer_hidden`, `layered` and `layer_seams`. Its missing-mesh refusal applies to swept entries only: layers may fall back.
  - The faces of the layered volumes are added to the `skip` lists of `meshsym._periodic` and `pair_images`, like a swept cell's.
  - Before generate, meshgroups puts every (slave, master, transform) seam pair among a layered volume's own faces into the list `job["layer_seams"]` that `apply_layers` created. The master is the face with the lower tag. The `add` closures read that list at d == 3.
  - The deferred hook (`swept_periodic`) also calls `gmsh.model.mesh.setPeriodic(1, slave rim curves, master rim curves, transform)` for those pairs, so the two rims get the same nodes.
  - At d == 3, a cut face of a layered cell that is neither in a seam pair nor on the model boundary gives note N5 and graded tetrahedra.
  - `_check_swept_seams` also checks layered volumes, with the same message wording but "the layered cell" for "the swept cell".

- [ ] **Step 1: Probe (a spike step, not committed).** In a cell model of the quarter round ring (R 20, r 3, 4 copies about z), try curve-only pairing, `setPeriodic(1, ...)` on the rim curves, with the seam faces skipped. Check that the rims come out node for node, and that generate and the copy succeed.
  - If gmsh refuses curve pairing on faces that are not paired, fall back to pairing the seam faces: `setPeriodic(2, ...)` before d == 2, with the hidden faces left empty, and the hand caps written at d == 3.
  - Write the result into the spec at the end of 7.2, one paragraph: what was tried, and which is used.

- [ ] **Step 2: Write the failing tests.**
  - `test_layered_ring_cells`: the quarter ring cell with a Skin Layer at 10 kHz copper and QuadLayers.
    - The whole ring has prisms in all 4 copies.
    - Every node on a seam plane is shared by both neighbouring copies: the counts on the seams match, and there are no unmatched faces.
    - The prisms are the same count in each copy.
  - `test_layered_cell_against_other_cell_falls_back`: a coil quarter (the layered cell) whose cut faces lie against copies of a tetrahedral tooth cell. Note N5, tetrahedra only in the coil, and the job succeeds.
  - `test_ordinary_cells_unchanged_by_stage5`: a symmetric job of Stage 4 (SW-S2's sector ring with QuadLayers off). Its node hash as at the current HEAD; record it before changing code, as in Task 2 Step 1.

- [ ] **Step 3: Run them, expect failure.** Run `pixi run -e addon pytest tests/freecad_addon/test_meshgroups.py -k "layered or stage5" -v`.

- [ ] **Step 4: Implement** the interfaces above, with Step 1's pairing.

- [ ] **Step 5: Run the tests, expect PASS.** Run `pixi run -e addon pytest tests/freecad_addon/test_meshgroups.py tests/freecad_addon/test_symmetric_study3d.py tests/freecad_addon/test_meshfrozen.py -v`, then `pixi run lint`.

- [ ] **Step 6: Commit** with the message `FreeCAD add-on: prism layers on symmetric cells`.

### Task 5: Catalogue rows PL-01 to PL-04 and PL-S1

**Files:**
- Modify: `experiments/refinement_catalogue/rows.py` (a `# --- 3D prism layers, Stage 5` section after the SW-S rows)
- Modify: `experiments/refinement_catalogue/build_catalogue.py:100-104`. For ids starting `PL-`, today is the same Study with every Skin Layer's `QuadLayers` off; the Skin Layers are kept.
- Modify: `experiments/refinement_catalogue/make_page.py` if its captions need "today (graded skin)" and "new (prism layers)" for PL rows.

**Interfaces:**
- Consumes: `bar_study`, `pad_air`, `skin(study, body, f=, sigma=, quads=True)`, `sw_report`, `free_faces_inside`, and Stage 4's `sws2` cell setup.
- Produces: these rows, each with an `_after` check that prints the counts of today and new, the air's min SICN, and its verdict. All are in copper.

| Row | Case | Check |
|---|---|---|
| PL-01 | Round wire r 3 x 100 at size 2, 10 kHz, as SW-02. Padding Box with 0 along z, so the ends are on the Air Region's faces (cuts). | Prisms and tetrahedra in the wire. No free faces inside. Validate shows V3. The text also names SW-02's swept count for comparison. |
| PL-02 | Busbar 12 x 6 x 60, all edges filleted r 2, size 2, 10 kHz (δ 0.66, so r ≥ 3 δ), Padding Box 20 | Prisms > 0, no free faces inside |
| PL-03 | Sphere r 5, size 2, 10 kHz, Padding Box 20 | Prisms == 3 × the sphere's surface triangles, no free faces inside |
| PL-04 | Disc r 6 x 3, size 2, 10 kHz, Padding Box 20 | Validate V1, mesher note N1, tetrahedra only (falls back). Expected "meshes". |
| PL-S1 | Round ring R 20, r 3, at 10 kHz, as a Symmetric Group of 4 quarter cells | Prisms in all copies, no free faces inside |

The cut pictures follow `SW_CUT`: a clip through the axis, and an `across` cut for the wire and the busbar.

- [ ] **Step 1: Add the rows and the today rule.**
- [ ] **Step 2: Build the PL rows.** Run `pixi run -e addon python experiments/refinement_catalogue/build_catalogue.py --only PL-01 PL-02 PL-03 PL-04 PL-S1` in the background. Expected: every row matches.
- [ ] **Step 3: Rebuild every row.** Run the whole catalogue. Expected: all rows match (57 + 5 = 62), and `catalogue.html` is regenerated in `C:\Users\hamed\Desktop\delme\refinement_studies`.
- [ ] **Step 4: Commit** with the message `Refinement catalogue: Stage 5 rows (prism layers)`.

### Task 6: Final check

- [ ] **Step 1:** Run `pixi run -e addon test-addon`. Expected: all pass.
- [ ] **Step 2:** Run `pixi run lint`. Expected: clean. Then `git status`: no stray formatting changes, and `highlight.py` is untouched.
- [ ] **Step 3:** Run the smoke test as in Task 3 Step 5. Expected: `PASS`.
- [ ] **Step 4:** Update the memory file `swept-body-prism-layers.md` with the Stage 5 commits, row numbers and limits, and its line in `MEMORY.md`.
