# Mesh refinements, Stage 4: Skin Layer — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A Skin Layer item that puts fine elements inside conductors along their real surface, sized from the skin
depth (with a calculator in its panel). In 2D it can also make quad layers on smooth bodies. It works in ordinary and
symmetric Studies, and comes with the Stage 4 catalogue rows.

**Architecture:** A new `SkinLayer` object in the Mesh Sizes folder picks whole conductor bodies. The jobwriter writes
it as a `"skin"` list on each job that meshes those bodies. The mesher turns each skin body into a Refine Near entry:
- a whole-body pick of that body, limited to it;
- fine size δ / ElementsPerDepth up to `min(1, LayerDepth) · δ`, growing to the body's own size at `LayerDepth · δ`.

From there the existing machinery does the rest:
- the real surface, which skips cut faces;
- the Restrict to the body;
- the partner faces on periodic seams;
- the size rules inside `mesh_region` for free objects (Stages 1 and 2).

Quad layers (2D only) add a gmsh `BoundaryLayer` field on top, only on bodies whose layer has no sharp corner. A body
with a sharp corner gets the graded triangles and a note. If gmsh still fails, the mesher drops the quad layers and
meshes again (spike and user's decision: spec 5.2, "Spike result: quad layers").

**Tech Stack:** FreeCAD 1.1 add-on (Python 3.11, PySide), gmsh 4.15.2 Python API, numpy, pytest via pixi.

**Spec:** `docs/superpowers/specs/2026-11-14-mesh-refinements-design.md`: sections 5.2 (with the spike result and the
user's decision), 6, 7.1–7.3, 8, 9 (Stage 4), 10 and 12.1, 12.2, 12.6–12.8. Read them before starting.

## Global Constraints

- Run everything through pixi:
  - `pixi run -e addon test-addon`
  - `pixi run -e addon pytest tests/freecad_addon/<file> -k <name>`
  - `pixi run lint`
  - `pixi run format`, then revert its change to the unrelated `highlight.py` if it makes one.
  - Never `pip install`.
- Branch `freecad/mesh-refinements` (Stage 3 ends at `96d4b4b`). Commit per task, never `--no-verify`, never push or merge.
- Ruff:
  - line length 120, double quotes;
  - no trailing comma on a construct that fits on one line;
  - never reorder imports;
  - format only files you changed.
- Module rules:
  - The mesher modules (`meshcommon.py`, `mesher.py`, `mesher2d.py`, `meshgroups.py`, `meshfrozen.py`) never import FreeCAD.
  - GUI code goes only in `commands.py`, `taskpanels.py` and `labels.py`.
  - `objects.py`, `jobwriter.py` and `validation.py` stay GUI-free.
- A Study without a Skin Layer writes no `"skin"` key and meshes exactly as before.
- Defaults (spec 5.2, 12.1):
  - `SkinDepth` 1 mm, `ElementsPerDepth` 2, `LayerDepth` 3, `QuadLayers` False;
  - `Frequency` 50 Hz, `Conductivity` 5.8e7 S/m, `RelativePermeability` 1.
- Skin depth formula: `SkinDepth = 1000 · sqrt(2 / (2π f μ0 μr σ))` mm, with μ0 = 4π·1e-7.
  - Copper (σ 5.8e7) at 50 Hz gives ≈ 9.35 mm.
  - Aluminium (σ 3.5e7) at 1 kHz gives ≈ 2.69 mm.
- Graded fields, per skin body:
  - Threshold `SizeMin = δ / ElementsPerDepth`, `SizeMax` = the body's own size (the job's size for that MAT_ID);
  - `DistMin = min(1, LayerDepth) · δ`, `DistMax = LayerDepth · δ`, `StopAtDistMax = 1`;
  - Restrict to the body and its boundary.
- Quad layers (2D, smooth bodies only): `BoundaryLayer` with `CurvesList` = the body's real boundary,
  `ExcludedSurfacesList` = every other surface, `Size = δ / ElementsPerDepth`, `Ratio = 1.2`,
  `Thickness = LayerDepth · δ`, `Quads = 1`, set with `setAsBoundaryLayer`. The graded fields stay as well.
- "Smooth" means:
  - at every point where two layer curves meet, the curve direction turns by at most 15°;
  - no layer curve has a radius of curvature below `LayerDepth · δ`.
- Units are mm. Property group `"EMSolution"`.
- GUI changes need the smoke test. Run `pixi run -e addon freecad tests\freecad_addon\gui_smoke.py` from PowerShell
  (Git Bash strips the backslashes and FreeCAD hangs). The last line of `%TEMP%\ems_gui_smoke.txt` must be `PASS`.

## Review Focus

1. **A conductor sharing an edge with another body** (a bar on an iron block): the layer runs inside the conductor
   along the shared edge, and the neighbour keeps its own size. Task 4 test: `test_skin_stays_inside_the_conductor_2d`.
2. **A conductor on the domain boundary** (a half wire on a symmetry plane): no fine layer along the cut line, away
   from the real surface. Task 4 test: `test_skin_skips_the_symmetry_plane_2d`.
3. **QuadLayers on a rectangular bar:** the mesh does not fail. The bar gets graded triangles and the mesher prints
   the note. Task 6 test: `test_quad_layers_fall_back_on_a_bar`.
4. **LayerDepth below 1** (a layer thinner than δ): the fine size reaches `LayerDepth · δ` and nothing breaks; there is
   no negative growth. Task 4 test: `test_skin_layer_thinner_than_delta`.
5. **A skin body with its own Mesh Size:** the core grows to that size, not the default. A Mesh Size smaller than the
   skin's fine size wins. Task 4 test: `test_skin_grows_to_the_body_mesh_size`.

---

### Task 1: The Skin Layer object

**Files:**
- Modify: `freecad_addon/emsolution/objects.py`. Where each change goes:
  - the proxy after `AirGrading`;
  - `make_skin_layer` after `make_air_grading`;
  - `skin_layers` after `air_gradings`;
  - `skin_depth` and `body_mu_r` near `whole_body_size`;
  - `is_item`, `_size_text`, `air_refusal`.
- Test: `tests/freecad_addon/test_study.py`

**Interfaces:**
- Produces:
  - `class SkinLayer(_Proxy)`, with properties:
    - `References` (`App::PropertyLinkSubListGlobal`, "Conductors with a skin layer (whole bodies)");
    - `SkinDepth` (`App::PropertyLength`, "Skin depth δ");
    - `ElementsPerDepth` (`App::PropertyFloatConstraint`, "Elements per skin depth; fine size = δ / this");
    - `LayerDepth` (`App::PropertyFloatConstraint`, "How deep the layer reaches, in skin depths");
    - `QuadLayers` (`App::PropertyBool`, "2D: quad layers along smooth surfaces");
    - `Frequency` (`App::PropertyFloat`, "Calculator: frequency in Hz");
    - `Conductivity` (`App::PropertyFloat`, "Calculator: conductivity in S/m");
    - `RelativePermeability` (`App::PropertyFloat`, "Calculator: relative permeability").
    - Each FloatConstraint has a lower bound just above 0 (`(value, 0.01, 1000.0, 0.5)`).
  - `make_skin_layer(study, refs, depth=1.0) -> obj`. Label `"SkinLayer"`. The other properties get their defaults
    (Global Constraints). `RelativePermeability` is `body_mu_r` of the first referenced body, when it has one.
  - `skin_layers(study) -> list`: the Skin Layer items in tree order.
  - `skin_depth(frequency, conductivity, mu_r) -> float`, in mm (the formula in Global Constraints).
  - `body_mu_r(study, body) -> float | None`: the scalar `relative_permeability` of the body's library material
    record, else None. Find the body → material link through the existing material helpers (`material_owners`,
    `materials`, `studymaterials.record_material`).
  - `_size_text(item)`: `f"δ {depth:g} mm, {per:g}/δ, {layer:g}δ"`, plus `", quads"` when `QuadLayers` is on.
  - `is_item` covers the class. `air_refusal` refuses the air for `SkinLayer`, using the existing
    "recombined or structured" text pattern: `f"Air Region {names} cannot have a Skin Layer."`.

- [ ] **Step 1: Write the failing tests** in `StudyTest`:
  - `test_skin_depth_formula`:
    - `skin_depth(50, 5.8e7, 1)` ≈ 9.35 (places=2);
    - `skin_depth(1000, 3.5e7, 1)` ≈ 2.69 (places=2).
  - `test_skin_layer_defaults_and_row`:
    - a box body and `make_skin_layer(study, [(a, "")], 2.69)`;
    - it has the defaults;
    - `skin_layers` returns it;
    - `mesh_size_rows(study)[-1][2][1] == "δ 2.69 mm, 2/δ, 3δ"`;
    - with `QuadLayers = True` the row ends `", quads"`.
  - `test_skin_layer_refuses_the_air`: `air_refusal(objects.SkinLayer, [air])` gives the message.
  - `test_skin_layer_mu_r_from_the_material`:
    - give the body a library material with `relative_permeability` 1000;
    - the new item's `RelativePermeability` is 1000;
    - a body with no material gives 1.
- [ ] **Step 2: Run** `pixi run -e addon pytest tests/freecad_addon/test_study.py -k skin -v`. Expected: FAIL
  (`make_skin_layer` missing).
- [ ] **Step 3: Implement.** Follow `RefineNear` / `AirGrading`.
- [ ] **Step 4: Run** `test_study.py` in full. Expected: PASS.
- [ ] **Step 5: Commit** `FreeCAD add-on: Skin Layer item`.

---

### Task 2: Validation of Skin Layer

**Files:**
- Modify: `freecad_addon/emsolution/validation.py` (`_kind`, `_settings`)
- Test: `tests/freecad_addon/test_study.py`, `tests/freecad_addon/test_symmetric_study.py`

**Interfaces:**
- Consumes: Task 1.
- Produces these exact problems (`validation.validate(study)`), `label` the item's Label, `name` the
  `objects.display_name(body)`:
  - Error, a sub-element pick: `f"Skin Layer {label}: pick whole conductors, not {body.Label}.{sub}."`.
  - Error, the air: the `air_refusal` message, through the existing path for items that refuse the air.
  - Errors:
    - `f"Skin Layer {label}: the skin depth must be greater than 0."`;
    - `f"Skin Layer {label}: elements per depth must be greater than 0."`;
    - `f"Skin Layer {label}: the layer depth must be greater than 0."`.
  - Warning, a 3D Study with `QuadLayers`: `f"Skin Layer {label}: quad layers are made in 2D Studies only; ignored."`.
  - Warning, the layer fills the body, i.e. `LayerDepth · δ > thickness / 2`:
    `f"Skin Layer {label}: the layer ({d:g} mm) is deeper than half of {name} (about {t:.2g} mm thick); the whole body is skin, so a Mesh Size of {fine:g} mm on it does the same."`.
    - 3D thickness is `validation.thickness(shape)` (4V / A).
    - 2D thickness is 4 · Area / perimeter of the face (the diameter of a round wire). Add it as
      `thickness_2d(face)` beside `thickness`.
  - Warning, 2D with `QuadLayers`, a body with a sharp corner on its layer:
    `f"Skin Layer {label}: {name} has sharp corners on its surface; quad layers need a smooth surface, so it gets graded triangles."`.
    - A layer edge is an edge of the body's face that is shared with another meshed face, or that lies inside the Air
      Region's face (not on its outline).
    - A corner counts when two layer edges meet and the tangent turns by more than 15°.
    - A curved layer edge with a radius below `LayerDepth · δ` counts too.
  - Warning, `QuadLayers` on a free object of a Study with Symmetric Groups:
    `f"Skin Layer {label}: quad layers are not made on free objects of a Study with Symmetric Groups; {name} gets graded triangles."`.
  - Warning, a body that also has a Transfinite Body or Recombine item:
    `f"Skin Layer {label}: {name} is structured or recombined, and that wins; the Skin Layer does nothing there."`.
  - `_kind` entry `objects.SkinLayer: "Skin Layer"`, so the existing `_links` messages apply.
- **Ruling:** a conductor edge on a symmetric seam lies inside the Air Region's face, so Validate may warn about a
  corner there that the mesher doesn't see (the mesher drops seams). Cost: a stray warning in a rare case.

- [ ] **Step 1: Write the failing tests:**
  - `test_skin_layer_settings_are_checked`: `SkinDepth` 0 gives the depth error. The FloatConstraints' lower bound
    of 0.01 may make 0 unreachable; test the two other checks only if FreeCAD lets the value reach 0, and say in the
    report which can.
  - `test_skin_layer_on_a_face_is_refused`.
  - `test_skin_layer_quads_in_3d_warns`.
  - `test_skin_layer_filling_the_body_warns`: a 2D disk r 2 with δ 1, layer 3 warns; layer 1 does not.
  - `test_skin_layer_quads_on_a_bar_warns_and_on_a_wire_not` (2D, both in an Air Region).
  - `test_skin_layer_quads_on_a_half_wire_not` (2D, a half disk whose straight edge lies on the Air Region's
    outline: no warning).
  - `test_skin_layer_on_a_recombined_body_warns`.
  - In `test_symmetric_study.py`, `test_skin_layer_quads_on_a_free_object_warns` (motor fixture plus `add_free`).
- [ ] **Step 2: Run** `pixi run -e addon pytest tests/freecad_addon/test_study.py tests/freecad_addon/test_symmetric_study.py -k skin -v`.
  Expected: FAIL.
- [ ] **Step 3: Implement.** Run the checks only for items with a meshed reference, as Refine Near does.
- [ ] **Step 4: Run** both test files in full. Expected: PASS.
- [ ] **Step 5: Commit** `FreeCAD add-on: validate Skin Layer`.

---

### Task 3: Skin Layer in job.json

**Files:**
- Modify: `freecad_addon/emsolution/jobwriter.py`. Add a new `skin_entries`, called wherever `refine_entries` is called:
  - `write_job` (ordinary);
  - each cell job (`_group_entry`, ~line 351);
  - each free job (`write_groups`).
- Test: `tests/freecad_addon/test_study.py`, `tests/freecad_addon/test_symmetric_study.py`

**Interfaces:**
- Consumes: Task 1.
- Produces `skin_entries(study, ids, quads=True) -> list[dict]`:
  - `ids` is the same `{body Name: [MAT_ID, ...]}` map `refine_entries` takes.
  - One entry per item with a whole-body reference in `ids`, in tree order:
    `{"name": <Label>, "mat_ids": [...], "depth": <SkinDepth>, "per_depth": <ElementsPerDepth>, "layer": <LayerDepth>, "quads": <bool>}`.
  - `"quads"` is `item.QuadLayers and study.Dimension == "2D" and quads`. Free jobs pass `quads=False`.
  - Callers set `job["skin"]` only when the list is non-empty.
  - The air never appears (Validate refuses it; skip an air reference here too).

- [ ] **Step 1: Write the failing tests:**
  - `test_job_without_skin_has_no_skin_key` (passes already).
  - `test_skin_goes_to_the_job`: a 3D box with δ 2.69 gives
    `job["skin"] == [{"name": "SkinLayer", "mat_ids": [m], "depth": 2.69, "per_depth": 2.0, "layer": 3.0, "quads": False}]`.
  - `test_skin_quads_only_in_2d`: the same item with `QuadLayers` gives `True` in a 2D Study and `False` in 3D.
  - In `test_symmetric_study.py`:
    - `test_skin_goes_to_the_cell_job`: a skin on a cell object sits on that group's cell job.
    - `test_skin_on_a_free_object_has_no_quads`: a skin on a free object sits on its free job with
      `"quads": False`.
- [ ] **Step 2: Run** `pixi run -e addon pytest tests/freecad_addon/test_study.py tests/freecad_addon/test_symmetric_study.py -k skin -v`.
  Expected: the new-key tests FAIL with `KeyError: 'skin'`.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** both files. Expected: PASS.
- [ ] **Step 5: Commit** `FreeCAD add-on: write Skin Layer to the mesh job`.

---

### Task 4: The graded skin in the 3D and 2D meshers

**Files:**
- Modify: `freecad_addon/emsolution/meshcommon.py`:
  - add `skin_refinements` after `apply_refinements`;
  - `apply_refinements` uses `entry.get("label", "Refine Near")` in its notes.
- Modify: `freecad_addon/emsolution/mesher.py` and `mesher2d.py` (`build`): add `skin_refinements(...)` to `picks`
  (each with `{}` picked entities) before the `apply_refinements` call.
- Modify: `freecad_addon/emsolution/meshgroups.py` `_free_rules`: same label in its note.
- Test: `tests/freecad_addon/test_mesher.py`, `tests/freecad_addon/test_mesher2d.py`

**Interfaces:**
- Consumes: Task 3's `"skin"` entries.
- Produces `skin_refinements(entries, sizes) -> list[dict]`, one Refine Near entry per (skin entry, MAT_ID):
  `{"name": e["name"], "label": "Skin Layer", "files": [], "whole": [m], "fine": depth / per_depth, "fine_distance": min(1, layer) * depth, "coarse": sizes[m], "growth": layer * depth - fine_distance, "limit_to": [m]}`.
  - `sizes` is the `{mat_id: size}` map both `build`s already make for Air Grading. Compute it before the
    `apply_refinements` call if it comes later today.
  - The result rides in `job["refine_fields"]`, so free jobs (`_free_rules`) and cell seams (`_refine_partners`) pick
    it up without more code.
- Geometry for the tests, from the spike (spec 5.2):
  - **3D:** aluminium block 40 × 40 × 20, δ 2.69, body size 8, in an air box of 200 at size 20.
  - **2D:**
    - round wire r 5, δ 1, body size 3, in an air square of 120 at size 6;
    - bar 20 × 10 with the same sizes;
    - half wire on y = 0;
    - bar on an iron block.
  - Measure the mean element edge in bands of depth below the real surface: 0–δ, δ–2δ, 2δ–3δ, beyond 3δ.

- [ ] **Step 1: Write the failing tests:**
  - `test_skin_grades_the_block_3d`:
    - mean edge within δ < 0.75 × δ (asked δ/2 = 1.35);
    - beyond 3δ > 0.6 × 8;
    - fewer elements in the block than a block at a uniform 1.35;
    - measure and comment the numbers.
  - `test_skin_grades_the_wire_2d`: within δ < 0.6; beyond 3δ > 1.5 (spike 0.47–0.50 and 1.66–2.43).
  - `test_skin_stays_inside_the_conductor_2d` (Review Focus 1): the bar on an iron block; the block's triangles within
    1 mm of the shared edge have a mean edge > 1.5, while the bar's < 0.6.
  - `test_skin_skips_the_symmetry_plane_2d` (Review Focus 2):
    - the half wire;
    - the line elements on y = 0 at least 3δ from the arc have a mean > 1.5;
    - near the arc they are fine.
  - `test_skin_layer_thinner_than_delta` (Review Focus 4): layer 0.5 meshes, with fine edges within 0.5.
  - `test_skin_grows_to_the_body_mesh_size` (Review Focus 5):
    - the 2D wire at body size 2: beyond 3δ, mean ≈ 2 (between 1.4 and 2.6);
    - the same wire with an extra whole-body size of 0.3 (a smaller Constant): the layer is 0.3, not 0.5.
  - `test_skin_with_no_real_surface_notes`: a 2D body alone (no air, no neighbour) gets
    `"Skin Layer <name>: MAT_ID <m> has no face shared with another region; it refines nothing"` in stderr and return
    code 0.
- [ ] **Step 2: Run** `pixi run -e addon pytest tests/freecad_addon/test_mesher.py tests/freecad_addon/test_mesher2d.py -k skin -v`.
  Expected: FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** both mesher test files in full. Expected: PASS (no key, no change).
- [ ] **Step 5: Commit** `FreeCAD add-on: graded Skin Layer in the meshers`.

---

### Task 5: Skin Layer in symmetric Studies

**Files:**
- Test only, unless a test fails: `tests/freecad_addon/test_meshgroups.py`. If one does, fix it in the module the
  failure points to.

**Interfaces:**
- Consumes: Task 4 (the skin rides in `refine_fields`).
- Fixtures: the Stage 2 refine tests near line 1130 (`plate_in_air`, `sector_group`, `air_2d`, `mean_edge`, `add_free`
  patterns).

- [ ] **Step 1: Write the tests:**
  - `test_skin_on_a_cell_conductor_copies_2d`:
    - a 2D sector group with a conductor in the cell and a skin on it;
    - every copy's conductor has the same fine band (mean edge within δ < 0.6 × body size) as the cell;
    - the seam faces get no layer (line elements on the seam, farther than 3δ from the real surface, are at body size).
  - `test_skin_on_a_free_conductor_grades_its_volume_3d`:
    - a free plate with a skin (graded, `quads` False);
    - the plate's tets within δ of its surface have a mean edge < 0.75 × δ;
    - beyond 3δ they are at body size.
  - `test_skin_on_a_free_conductor_2d`: the same in 2D.
- [ ] **Step 2: Run** `pixi run -e addon pytest tests/freecad_addon/test_meshgroups.py -k skin -v`. Expected: PASS if
  Task 4's reuse holds. Any failure is a real gap: fix it, and say in the report what was missing.
- [ ] **Step 3: Run** `test_meshgroups.py`, `test_symmetric_study.py`, `test_symmetric_study3d.py`. Expected: PASS.
- [ ] **Step 4: Commit** `FreeCAD add-on: Skin Layer tests in symmetric Studies` (plus any fix).

---

### Task 6: Quad layers (2D)

**Files:**
- Modify: `freecad_addon/emsolution/meshcommon.py`:
  - `apply_quad_layers` after `skin_refinements`;
  - `generate` retries without the boundary layers when gmsh fails with them.
- Modify: `freecad_addon/emsolution/mesher2d.py` (`build`): call `apply_quad_layers` after `apply_refinements`.
- Test: `tests/freecad_addon/test_mesher2d.py`, `tests/freecad_addon/test_meshgroups.py`

**Interfaces:**
- Consumes: Task 3 entries with `"quads": True`, Task 4.
- Produces:
  - `apply_quad_layers(entries, body_tags, recombined=()) -> list[int]`: one `BoundaryLayer` field per smooth skin
    body with `quads` (settings in Global Constraints), returning their tags.
    - The layer curves are `real_boundary(2, tags)`.
    - A body that is not smooth gets
      `_note(f"Skin Layer {name}: MAT_ID {m} has a sharp corner on its surface; graded triangles instead of quad layers")`.
    - A body in `recombined` (the job's `recombine` MAT_IDs, and transfinite bodies) gets no layer and
      `_note(f"Skin Layer {name}: MAT_ID {m} is structured or recombined; no quad layers")`.
    - Corner turn: compare the curves' tangents at their shared end points (`gmsh.model.getDerivative` at the
      parametrisation bounds).
    - Radius: `gmsh.model.getCurvature` sampled at about 20 parameters per curve (a straight line has 0).
  - `generate(job, dim)`: when `gmsh.model.mesh.generate` raises and boundary-layer fields exist (the job keeps
    their tags in `job["quad_layer_fields"]`), it:
    - removes those fields;
    - clears the mesh;
    - prints `_note("Skin Layer: gmsh could not make the quad layers; graded triangles instead")`;
    - generates once more.
    - Without boundary-layer fields, the error propagates as today.

- [ ] **Step 1: Write the failing tests** (geometry of Task 4):
  - `test_quad_layers_on_a_wire`:
    - the wire's elements include quads (spike: 252 quads, 95 triangles at δ 1, 2/δ, 3δ);
    - the air has no quads;
    - the quads lie within 3δ + 0.5 of the surface.
  - `test_quad_layers_on_a_half_wire`: quads in the conductor; the job does not fail.
  - `test_quad_layers_fall_back_on_a_bar` (Review Focus 3): return code 0, no quads, the sharp-corner note in stderr,
    and the graded band as in Task 4.
  - `test_quad_layers_on_two_wires`: both wires get quads (two `BoundaryLayer` fields).
  - `test_quad_layers_retry`: monkeypatch the smooth check to accept the bar; the mesh still succeeds, with the retry
    note and no quads.
  - In `test_meshgroups.py`, `test_quad_layers_on_a_cell_wire_copy`: a 2D sector cell with a round wire and quads;
    every copy has the same number of quads as the cell.
- [ ] **Step 2: Run** `pixi run -e addon pytest tests/freecad_addon/test_mesher2d.py tests/freecad_addon/test_meshgroups.py -k quad_layers -v`.
  Expected: FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `test_mesher2d.py`, `test_meshgroups.py` and `test_mesher.py` in full. Expected: PASS.
- [ ] **Step 5: Commit** `FreeCAD add-on: Skin Layer quad layers in 2D`.

---

### Task 7: Command, panel, labels and icon

**Files:**
- Create: `freecad_addon/icons/skinlayer.svg`
- Modify:
  - `freecad_addon/emsolution/commands.py`: `AddSkinLayer`, `REFINEMENTS`, the dropdown tooltip, `COMMANDS`,
    `context_names`;
  - `freecad_addon/emsolution/taskpanels.py`: an `ITEM_PICKS` entry and the Skin Layer rows in `ItemPanel`;
  - `freecad_addon/emsolution/labels.py`: `KINDS`, `tag_text`, `description`;
  - `tests/freecad_addon/gui_smoke.py`.

**Interfaces:**
- Consumes: Task 1 (`make_skin_layer`, `skin_depth`, `body_mu_r`) and Task 2's messages.
- Produces:
  - **Command `EMS_SkinLayer`:**
    - MenuText `"Skin Layer"`, ToolTip `"Fine elements inside conductors along their surface, sized from the skin depth"`,
      icon `skinlayer`.
    - Activated: `refs = objects.to_cells(study, taskpanels.selected_mesh_refs())`, then `gate` and
      `make_skin_layer(study, refs)` through `_create_and_edit(study, "Add Skin Layer", ...)`, as Refine Near.
  - `REFINEMENTS = ("EMS_RefineNear", "EMS_SkinLayer", "EMS_AirGrading")`; the dropdown ToolTip is
    `"Refine Near, Skin Layer or Air Grading"`.
  - `context_names`: whole-body picks (`"Body"` without sub-elements, and `"Cell"`) gain `"EMS_SkinLayer"` after
    `"EMS_RefineNear"`. `"Air"` gains nothing.
  - **`ITEM_PICKS[objects.SkinLayer]`:**
    - whole bodies only (`objects.pick_body`), no air;
    - list label `"Conductors"`, gate kinds `("Body",)`, whole `True`;
    - hint `"Select the conductors (whole bodies) in the 3D view or the tree."`.
  - **Panel rows after Name:**
    - "Skin depth δ" (`_length_box`), "Elements per depth" and "Layer depth (× δ)" (float spin boxes, minimum 0.01);
    - "Quad layers" checkbox, shown in 2D Studies only;
    - a group **"Skin depth calculator"** with:
      - "Frequency (Hz)", "Conductivity (S/m)" and "Relative permeability" fields;
      - a **Calculate** button and a result label.
    - Calculate:
      - with all three inputs > 0, sets the δ box to `skin_depth(...)` and the label to `f"δ = {d:.3g} mm"`;
      - otherwise the label says `"Frequency, conductivity and permeability must be greater than 0."` and δ stays.
    - μr starts from `body_mu_r` of the first pick when the item is new and the pick has a material.
    - `accept` writes all properties; `unsaved()` reports each.
  - **Labels:** `KINDS["SkinLayer"] = ("#087f5b", "L", "Skin layer")`; `tag_text` gives the `_size_text` text with the
    panel's unsaved values; `description` gives `f"Skin layer: {tag_text}"`.
  - **Icon:** 64 × 64 SVG in the style of `refinenear.svg` / `airgrading.svg`: a conductor cross-section whose cells
    are thin along the rim and coarse in the middle, with a badge bottom right.

- [ ] **Step 1: Update the smoke test first:**
  - the expected `context_menu()` list for a whole-body pick gains `"EMS_SkinLayer"`;
  - add a step: select a body, `Gui.runCommand("EMS_SkinLayer")`, set frequency 1000, conductivity 3.5e7, μr 1, press
    Calculate, accept;
  - assert `abs(objects.skin_layers(study)[0].SkinDepth.Value - 2.69) < 0.01`;
  - assert Validate shows no Skin Layer error.
- [ ] **Step 2: Run the smoke test** (PowerShell): `pixi run -e addon freecad tests\freecad_addon\gui_smoke.py`, then
  `Get-Content "$env:TEMP\ems_gui_smoke.txt" -Tail 3`. Expected: `FAIL`.
- [ ] **Step 3: Implement** the command, menu and context entries, the panel, the labels and the icon. Render the icon
  with Qt beside `refinenear.svg` and `airgrading.svg` and look at it.
- [ ] **Step 4: Run** the smoke test (`PASS`), `pixi run -e addon test-addon` (all pass) and `pixi run lint` (clean).
- [ ] **Step 5: Commit** `FreeCAD add-on: Skin Layer command, panel and icon`.

---

### Task 8: The Stage 4 review catalogue rows

**Files:**
- Modify: `experiments/refinement_catalogue/rows.py` (the rows) and `build_catalogue.py` (the "today" copy also
  deletes `objects.skin_layers(study)`).

**Interfaces:**
- Consumes: the whole add-on, and the helpers in `rows.py` (`study_of`, `done`, `block`, `motor`, `cell`, `rns5`'s
  free object).
- Rows (spec 9, Stage 4, plus SL-08 for a free object). Sizes are mm. Pictures of 3D rows are cut through the
  conductor:

| id | Study | Skin Layer | after-check |
|---|---|---|---|
| SL-01 | 3D: aluminium block 40 × 40 × 20 in an Air Region, block size 8 | calculator 1 kHz, σ 3.5e7 (δ 2.69), 2/δ, 3δ | block elements today vs new printed |
| SL-02 | SL-01 at 5 kHz (δ 1.20) | the same | — |
| SL-03 | 2D: round copper wire r 30, size 10 | calculator 50 Hz, σ 5.8e7 (δ 9.35), graded | — |
| SL-04 | SL-03 with `QuadLayers` | quads | quads counted in the wire > 0 |
| SL-05 | 2D: rectangular bar 40 × 10, δ 2, size 6 | `QuadLayers` | no quads; the sharp-corner note and Validate warning printed |
| SL-06 | 2D symmetric: a conductor (round bar) in the RN-S1 motor cell | graded | every copy's bar refined like the cell |
| SL-07 | 2D: wire r 3 with δ 2, layer 3 | — | the "layer is deeper than half" warning printed |
| SL-08 | 3D symmetric: the RN-S5 free object as a conductor | graded | — |

- [ ] **Step 1: Add the rows.** Run
  `pixi run -e addon python experiments/refinement_catalogue/build_catalogue.py --only SL-01 SL-02 SL-03 SL-04 SL-05 SL-06 SL-07 SL-08`.
  Expected: all `match: true`.
- [ ] **Step 2: Look at every new picture** and fix the rows whose picture does not show the layer (zoom on the
  conductor, cut plane). Re-run with `--only`.
- [ ] **Step 3: Run the whole catalogue.** Expected: every row (RN, RN-S, AG, SL) matches, exit code 0.
- [ ] **Step 4: Commit** `Refinement catalogue: Stage 4 rows (Skin Layer)`.

---

### Task 9: Stage 4 check and hand-over

- [ ] **Step 1: Run** `pixi run -e addon test-addon` (all pass), `pixi run lint` (clean), and the GUI smoke test
  (`PASS`).
- [ ] **Step 2: Hand over** `C:\Users\hamed\Desktop\delme\refinement_studies\catalogue.html`, as in Stages 1–3.
- [ ] **Step 3: Stop.** Don't merge or push; the user reviews the SL rows first.
