# Mesh refinements: Refine Near, Skin Layer, Air Grading (design)

Date: 2026-11-14. Status: draft for the user's review.

## 1. Intent

Low-frequency EM meshes need small elements in a few places (magnet edges, tooth tips, coil corners, conductor skins)
and large ones everywhere else, with a smooth change between them. The air gap of a motor is not one of them: rotor and
stator need the same divisions on the sliding surface, so users mesh the gap structured (Transfinite items), and
automatic refinement is not recommended there (user, 2026-11-14). Today the add-on has only Mesh Size items, each a gmsh `Constant`
field joined by `Min` with gmsh's own size sources switched off (`meshcommon.apply_size_fields`). That gives hard
steps: a fine size stops at the picked entity and the next element is the body's size, and the whole Air Region has one
size. Resolving a small feature in the air means making all the air fine (a 2D demo: 299k elements against 21k when graded).

This work adds three new mesh items to the Mesh Sizes folder. They are the first of several refinement types (zones,
probes and others may follow as further items), so each is its own item rather than options on Mesh Size.

| Item | Gmsh fields | Use |
|---|---|---|
| **Refine Near** | `Distance` + `Threshold` (+ `Restrict`) | fine elements at picked faces, edges, vertices or bodies, growing to a coarse size over a distance |
| **Skin Layer** | `Distance` + `Threshold` + `Restrict` (3D, 2D); `BoundaryLayer` (2D quad layers) | fine elements inside conductors along their surface, sized from the skin depth |
| **Air Grading** | `Extend` (+ `Restrict`) | the air's size grows from each body's surface size up to the air's size |

The throwaway demos in the scratchpad of the 2026-11-14 session showed each field working in gmsh 4.15.2 (the version
in pixi) and the option names were checked against it. Key facts they established are repeated where used below.

## 2. Goals, non-goals, anti-goals

Goals
- The three items, with task panels, toolbar buttons, menu entries, right-click entries and icons, in 2D and 3D
  Studies, with and without sliding motion.
- Working in ordinary Studies and in Studies with Symmetric Groups (cell objects, free objects, the air around the
  copies).
- A Skin Layer calculator: frequency, conductivity and relative permeability give the skin depth.
- A review catalogue (section 9) the user checks stage by stage before the next stage starts.

Non-goals (this round)
- Items 4 to 7 of the 2026-11-14 list: elements per circle, refinement zones (Box/Ball/Cylinder), embedded probes,
  a quality report for ordinary jobs. They come later as their own work.
- Storing conductivity in the materials. The Skin Layer keeps its own calculator inputs.
- Anisotropic fields, adaptive refinement from a solution.

Anti-goals (a failure even if it runs)
- A refinement that silently caps sizes elsewhere: every Threshold uses `StopAtDistMax = 1`, so outside its reach the
  item has no effect and the other sizes rule (without it, Threshold returns its coarse size everywhere and `Min`
  makes that a cap on the whole model).
- Changing the meshes of Studies that have none of the new items. With no new item, the job and the mesh are
  byte-for-byte what they are today.
- Copies in a symmetric Study that stop matching: refinement happens in the cell before copying, never per copy.

## 3. Constraints

- AGENTS.md: mesher modules never import FreeCAD; GUI code only in `commands.py`, `taskpanels.py`, `runner.py`,
  `labels.py`, `highlight.py`, `materialstandins.py`; `objects.py`, `jobwriter.py`, `validation.py` stay GUI-free.
  Ruff at 120 columns, no import reordering, `pixi run lint` clean, smoke test for GUI changes.
- Branch `freecad/mesh-refinements` off `main`, merged back when the stages are done.
- The mesher subprocess has numpy and gmsh, not scipy.
- Sizes combine as today: every field joins the one background `Min` field, so the smallest size wins.
- Units are mm throughout (the skin depth formula works in SI and converts).

## 4. Approaches considered

- **A. Growth settings on the existing Mesh Size.** One item to learn, but Mesh Size would mean two things and Air
  Grading does not fit it.
- **B. One Refinement item plus a Growth setting on the Air Region.** Fewer items; skin depth becomes a helper inside
  the Refinement panel.
- **C. Three separate items (chosen by the user).** Clear names, and new refinement types later become further items
  beside them without overloading one panel.

User's choice: C, "since we might add other types of mesh refinements too".

How sizes are computed (my call): gmsh fields wherever the mesher has CAD entities (ordinary jobs, cell jobs, the
surfaces of free jobs). The air and free volumes around frozen copies are meshed in a separate model built from mesh
facets only (`meshfrozen.mesh_region`), so the fields there need a different source of distance (section 7.3).
A Python size callback for every job was rejected: slower, and it would redo what `Restrict` and `IncludeBoundary`
already handle.

## 5. The items (user-facing)

All three live in the Mesh Sizes folder beside Mesh Size and the Transfinite items, appear in the Mesh Sizes panel's
table, show labels in the 3D view like the others, and are edited in an `ItemPanel`-style task panel (pick list, Add
selection / Remove, name field, settings).

### 5.1 Refine Near

Picks: faces, edges, vertices, or whole bodies (a whole body means its boundary: its faces in 3D, its edges in 2D).
The Air Region can be picked (its faces, e.g. near an outer boundary), like Mesh Size allows.

Properties (group "EMSolution"):

| Property | Type | Default | Meaning |
|---|---|---|---|
| `References` | LinkSubListGlobal | picks | what to refine near |
| `FineSize` | Length | half the default mesh size | size at the picks and within `FineDistance` |
| `FineDistance` | Length | 0 | how far the fine size reaches unchanged |
| `CoarseSize` | Length | the default mesh size | size reached at `FineDistance + GrowthDistance` |
| `GrowthDistance` | Length | 5 × FineSize | how far the size grows from fine to coarse |
| `LimitTo` | LinkListGlobal | empty | bodies (or the Air Region) the refinement is limited to; empty = everywhere |

Table text: `0.4 → 4 mm over 10 mm` (and ` in Body, …` when limited).

Fields: `Distance` on the picks (`Sampling` from the pick's length: about one sample per FineSize / 2 along a
curve, capped, see 7.1) → `Threshold` with `SizeMin = FineSize`, `SizeMax = CoarseSize`, `DistMin = FineDistance`,
`DistMax = FineDistance + GrowthDistance`, `StopAtDistMax = 1`. With `LimitTo`, wrapped in `Restrict` on those bodies'
final tags and their boundary entities (the demos showed a `Restrict` without the boundary leaves the boundary curves
unsized, i.e. one element per side).

### 5.2 Skin Layer

Picks: whole conductor bodies only (3D solids, 2D faces). The layer runs inside each body along its real surface:
the faces (edges in 2D) it shares with the air or with other bodies. Faces that are only cuts get no skin: faces on
the outer boundary of the meshed domain (a symmetry plane of a half model), faces on a periodic boundary
(`job["periodic"]`), and in a symmetric Study the cell faces that meet a copy (the seams `contact_table` finds).
A whole-body pick of Refine Near uses the same surface. (My call, from the builder check.) Not the Air Region.

| Property | Type | Default | Meaning |
|---|---|---|---|
| `References` | LinkSubListGlobal | picks | the conductors (whole bodies) |
| `SkinDepth` | Length | 1 mm | δ, the item's real setting; typed directly or filled by the calculator |
| `ElementsPerDepth` | FloatConstraint | 2 | fine size = δ / ElementsPerDepth |
| `LayerDepth` | FloatConstraint | 3 | the layer reaches LayerDepth × δ into the body |
| `QuadLayers` | Bool | False | 2D only: gmsh boundary-layer quads instead of graded triangles |
| `Frequency` | Float (Hz) | 50 | calculator input, kept for reference |
| `Conductivity` | Float (S/m) | 5.8e7 | calculator input, kept for reference |
| `RelativePermeability` | Float | 1 | calculator input; the panel fills it from the body's material when it has one |

Calculator (in the panel, not a separate dialog): frequency, conductivity, μr fields and a **Calculate** button that
sets `SkinDepth = 1000 · sqrt(2 / (2π f μ0 μr σ))` mm and shows the result. δ stays editable, so a user who knows δ
types it. Validation refuses non-positive inputs only when Calculate is pressed (the panel) and a non-positive
`SkinDepth` always (Validate).

Table text: `δ 2.7 mm, 2/δ, 3δ` (plus `, quads` when QuadLayers).

Fields, graded (3D, and 2D without QuadLayers): `Distance` from the body's boundary → `Threshold` with
`SizeMin = δ / ElementsPerDepth`, `SizeMax` = the body's own size (its whole-body Mesh Size or the default),
`DistMin = δ`, `DistMax = LayerDepth · δ`, `StopAtDistMax = 1` → `Restrict` to the body and its boundary.
The demo (aluminium block 40 × 40 × 20 mm, 1 kHz) gave 39.6k elements in the block against 61k for a uniformly fine
block.

Quad layers (2D, QuadLayers on): a `BoundaryLayer` field on the body's boundary curves with
`ExcludedSurfacesList` = every surface except the body (so layers grow inside it only), `Size = δ / ElementsPerDepth`
(first layer), `Ratio = 1.2`, `Thickness = LayerDepth · δ`, `Quads = 1`, set with `setAsBoundaryLayer` (a meshing
constraint, not part of `Min`). Shown working on a round wire in the demo. The air beside the conductor still sees the
boundary curves' size.

**Spike result (2026-11-15): quad layers.** δ 1, 2 per δ, 3δ, body size 3, in gmsh 4.15.2 (2D):
- The graded fields above work on every shape tried (bar 20 × 10, round wire r 5, half wire on a symmetry plane, a bar
  sharing an edge with another body): fine 0.48–0.50 within δ, 0.6–0.85 at 1–2δ, 1.2–1.9 at 2–3δ.
- The `BoundaryLayer` field alone leaves the surface spaced at the body's size (long thin quads), so quad layers are the
  `BoundaryLayer` plus the graded fields: round wire 252 quads in 5 layers, half wire 128 quads (a layer curve meeting a
  cut line at 90° is fine).
- It fails with "Edge not recovered" wherever two layer curves meet at a corner: the bar, the bar touching another body,
  a bar with corners rounded to r 1, polygons turning 22.5° or more at a corner. Polygons turning 15° (24 sides) or
  less work; a full disk works even at r 2.8 < 3δ. `FanPointsList` at the corners hangs; `PointsList`,
  `IntersectMetrics` and a thinner layer still fail.
- A layer built as geometry (the body inset by 3δ, the ring cut at each corner into trapezoids, each structured with a
  1.2 progression) meshes the bar: 480 quads in 4 layers.

**User's decision (2026-11-15), cell conductors:** a cell object's faces toward the free side (the Air Region around
the copies, free objects, copies of other groups) are real surface too, though the cell job sees nothing beyond them.
The jobwriter finds them in FreeCAD and passes them to the cell job as picked faces of the Skin Layer and of whole-body
Refine Near picks; Validate's corner check counts them.

**User's decision (2026-11-15):** quad layers use gmsh's `BoundaryLayer` on smooth bodies only. A body with a sharp
corner on its layer gets the graded triangles instead, with a Validate warning and a mesher note. The built-as-geometry
layer can come later as its own item.

### 5.3 Air Grading

Picks: the air: the Air Region (the usual case), or in a symmetric Study the drawn air the user meshes as a free
object. One Air Grading per air; Validate refuses a second on the same air.

| Property | Type | Default | Meaning |
|---|---|---|---|
| `References` | LinkSubListGlobal | the Study's Air Region when there is one | the air (whole body) |
| `GrowthDistance` | Length | 10 × default mesh size | over how far the air's size grows from the bodies' surface sizes to the far size |
| `FarSize` | Length | 0 | the size far from the bodies; 0 = the air's own size (its whole-body Mesh Size or the default) |

Table text: `grows over 50 mm to 40 mm` (far size shown resolved).

Fields (ordinary jobs): `Extend` with `SurfacesList` (3D) / `CurvesList` (2D) = the air's inner boundary (the
faces it shares with bodies), `DistMax = GrowthDistance`, `SizeMax = far size`, `Power = 1`; wrapped in `Restrict` to the
air and its boundary. The demo showed `Extend` takes the boundary to grow from, not the region to fill (given the air
surface it did nothing), and that it grows from the boundary's own sizes, so no fine size is needed. The far size
applies to the air's inside and its outer boundary only (a `Constant` restricted to the air volumes and the outer
faces). The faces the air shares with bodies keep today's size, the smaller of the body's size and the air's own size,
so a far size larger than the air's size never makes a body's surface coarser. (My call, from the builder check.)

## 6. Data flow

### 6.1 objects.py

- Three proxies `RefineNear`, `SkinLayer`, `AirGrading` (subclasses of `_Proxy`), `make_refine_near`,
  `make_skin_layer`, `make_air_grading`, listing helpers `refine_items`, `skin_layers`, `air_gradings`.
- `is_item`, `item_refs` (only `References`; `LimitTo` is shown in the panel), `_size_text`, `mesh_size_rows` and
  `air_refusal` (Skin Layer refuses the air) know the new classes.
- `to_cells` maps picks on a Symmetric Group's drawing to the cell, as for Mesh Size.

### 6.2 validation.py

`_kind` gains the three names; `_links` covers them (deleted bodies, sub-elements gone, bodies not meshed).
New checks in `_settings` (errors unless said):
- Refine Near: `FineSize > 0`, `CoarseSize ≥ FineSize`, `GrowthDistance > 0`, `FineDistance ≥ 0`; `LimitTo` bodies
  must be meshed by the Study (warning otherwise, like other refs).
- Skin Layer: whole bodies only; `SkinDepth > 0`, `ElementsPerDepth > 0`, `LayerDepth > 0`; QuadLayers in a 3D
  Study is a warning ("only 2D", ignored). Warning when `LayerDepth · δ` is more than half the body's thickness
  (`validation.thickness`): the whole body is skin, so a plain Mesh Size does the same.
- Air Grading: only an air (Air Region, or a free object in a symmetric Study); one per air; `GrowthDistance > 0`;
  `FarSize ≥ 0`.

### 6.3 jobwriter.py → job.json

`_body_job` writes new keys only when the items exist (so jobs without them are unchanged):

```json
"refine": [
  {"name": "Gap", "files": ["geometry/refine_1_1.brep", "..."], "whole": [3, 7],
   "fine": 0.4, "fine_distance": 0.5, "coarse": 4.0, "growth": 10.0, "limit_to": [3]}
],
"skin": [
  {"name": "Skin", "mat_ids": [5], "depth": 2.69, "per_depth": 2, "layer": 3, "quads": false}
],
"air_grading": {"growth": 50.0, "far": 40.0}
```

- `files` are the picked sub-elements exported like Mesh Size picks (`export_subs`); `whole` lists the MAT_IDs of
  whole-body picks (the mesher takes their boundary); `limit_to` lists MAT_IDs, with the air written as its MAT_ID
  (both sides' MAT_IDs when sliding).
- Skin Layer needs no files: its bodies are MAT_IDs already in the job.
- Air Grading sits on the job with the air (`job["air_grading"]`), or for a symmetric Study on the free job that holds
  the air.
- For a symmetric Study, `_group_entry` passes each cell job only the items on its cells (as it does for `elements`),
  and `write_groups` passes each free job the items on its free bodies and its air.

### 6.4 Mesher (meshcommon.py, mesher.py, mesher2d.py)

- `build` imports the refine files with the size files (one entity each, `_import_one`), so the fragment map places
  them; the same "did not merge with the bodies" check applies.
- A new `meshcommon.apply_refinements(job, refine_tags, body_vols, dim)` runs after `apply_size_fields`, adds its fields
  to the existing `Min` field's `FieldsList` (the way `meshgroups._new_size_field` already appends) and sets the
  `BoundaryLayer` fields. Body sizes needed by Skin Layer come from the job's volume entries.
- Whole-body picks and Skin Layer bodies use `getBoundary(..., combined=False)` of the body's final tags, the boundary
  of the union (combined) for a body cut into several pieces.
- A sliding job splits the air after `build`; the fields are set before the split and refer to final tags, so they
  work on both sides. `LimitTo` the air means both air MAT_IDs.
- Transfinite settings win over every field: gmsh ignores size fields on transfinite curves, surfaces and volumes, so
  a refinement or Air Grading next to a structured air gap or a sliding surface never changes its divisions (NDIV).
  A catalogue row checks this (RN-08, AG-04).
- `meshgroups._carry_size_picks` (which retargets `Constant` fields when a face is replaced) also retargets the
  `Distance`, `Restrict` and `Extend` entity lists.

## 7. Symmetric Studies

### 7.1 Cell objects

Cell jobs run the same `build`, so Refine Near and Skin Layer on cell objects work unchanged and the copies inherit the
refined mesh. An item on a cell object refines only the cell's own mesh; it does not reach the air or free objects
around the copies (user's decision, 2026-11-14: the air gap, the main air next to cells, is meshed structured, so
automatic refinement there is not wanted). Items that refine the air around copies are Air Grading and items on free
objects (7.3). Known limit (my call, to confirm in the catalogue): distances are measured inside the cell. A refinement
near a face on the cell's boundary does not reach across into the neighbouring copy, so the copy beside it is refined
only by its own image of the item. For a face shared by two copies (a periodic seam), the pick maps to one of the
cell's two boundary faces; the mesher also refines the partner face that `contact_table` pairs it with, so both sides
of the seam match. Picks the user makes on the drawing map to the cell through `to_cells`.

### 7.2 Free objects

A free job meshes its surfaces with gmsh (`generate(settings, dim - 1)`), so fields work on the free objects' surfaces.
Their volumes (faces in 2D) are then meshed by `meshfrozen.mesh_region` in a mesh-only model, which caps sizes at
the body's size and lets sizes spread in from the boundary (`Mesh.MeshSizeExtendFromBoundary = 1`). Refine Near and
Skin Layer on free objects therefore need the distance-based size inside `mesh_region` too (7.3).

### 7.3 Inside mesh_region (free volumes and the air around copies)

Today the air around copies already grows from the copies' surface sizes (`MeshSizeExtendFromBoundary = 1`), but with
no control over how fast. The new items reach this model as a list of size rules passed to `mesh_region`:
`{"kind": "threshold", "points": <xyz of the picked entity's mesh nodes>, ...}` and `{"kind": "grading", ...}`.

Stage 2 starts with a spike to choose how they are evaluated, in order of preference:
1. gmsh fields on the discrete model: `Distance` on the discrete surfaces/curves that hold the picked facets (and, for
   Air Grading, `Extend` on the frozen shell), then `Threshold`/`Restrict` as in ordinary jobs.
2. A size callback (`gmsh.model.mesh.setSizeCallback`) computing distance with numpy against the sampled nodes,
   chunked, with a bounding-box cut-off at `DistMax`.
The spike measures both on the catalogue's largest symmetric row and picks the first that is correct and under about
twice the current meshing time. The choice is recorded in this document before Stage 2's code. If neither passes, the
work stops there and the measurements go to the user, who decides between the slower option and leaving refinement
out of the air around copies for now. (My call, from the builder check.)

**Spike result (2026-11-14): option 1, a gmsh field on points.** Measured on catalogue Studies L-04 (3D, 145k tets of
air around copies, the largest), L-10 (3D, two free plates and air) and motor_sliding-air (2D, air around copies), with
a Refine Near on a free body (whole pick):
- The refinement on the free job alone (its surfaces graded by the ordinary fields, the volumes growing from them)
  already grades the air near a short growth (2 mm: 0.38 / 0.56 / 0.76 mm against 0.33 / 0.51 / 0.74 asked), but not a
  long one (6 mm: 0.54 against 0.38), and not at all where the picked faces are not refined (2D air: 1.9 mm throughout).
- A `Distance` field on `PointsList` (one model point per mesh node of the picked entities, read after the free surface
  mesh) → `Threshold`, set as the background field of the `mesh_region` model, follows the asked growth (6 mm: 0.49 /
  0.66 / 0.75 mm in 3D; 2D: 0.90 / 1.11 / 1.68 against 0.88 / 1.25 / 1.75). Time: +3 % on mesh_region (0.91 → 0.94 s
  for 77k tets; L-04 2.74 → 2.75 s). 20k points take 0.05 s to add.
- The numpy size callback (option 2) gives the same mesh at +40 % time; a discrete surface holding the picked facets
  gives the same as points but only for picks that lie on the region's own boundary. Both are dropped.
- Caveat for the code: gmsh meshes the added points as nodes, so `mesh_region` keeps only the nodes its elements use.
- Distances in the free region are measured from the picked entities' mesh nodes, so they are exact at the nodes and
  within half an element in between, the same order as the `Sampling` of ordinary jobs.

Air Grading on the air around copies grows from the frozen facets' own sizes (the copies' surface mesh) to the far
size over the growth distance; with no Air Grading the air stays as it is today.

**Spike result (2026-11-15): Air Grading.** Block 20 × 20 × 10 at size 2 in an air box 200 mm wide, air size 20,
growth 60 (mean edge in bands 0–3 / 3–10 / 10–25 / 25–50 / 50–80 mm from the block):
- Ordinary job, the fields of 5.3: today 2.48 / 9.20 / 18.6 / 27.4 / 28.2 (3D), graded 2.61 / 4.86 / 8.95 / 16.7 /
  25.8; far 40 gives 2.69 / 6.24 / 14.6 / 30.1 / 48.8 (fewer elements than today: 7.8k against 9.2k); 2D the same
  shape. Time unchanged.
- The air's faces on the domain boundary (a symmetry plane the block touches): the face's mesh jumps to the far size
  unless the `Restrict` also lists the air's outer faces (with `IncludeBoundary`) and, in 3D, the `Extend` also lists
  the curves of the inner faces (surfaces are meshed before any surface mesh exists to extend from): then 2.19 / 3.54 /
  6.73 / 12.2 / 19.0 against today's 2.30 / 6.17 / 18.0 / 19.7. In 2D a line on the plane is meshed before any curve
  mesh exists, so it gets a `Distance` on the points where the outer boundary meets the inner boundary → `Threshold`
  (from the size there to the far size over the growth distance, `StopAtDistMax = 1`) restricted to the outer curves:
  2.11 / 3.22 / 6.51 / 12.8 / 18.0 against 2.27 / 8.61 / 7.19 / 13.8 / 19.1.
- Inside `mesh_region` the air already grows by interpolation from the frozen boundary
  (`MeshSizeExtendFromBoundary = 1`, here 2.79 / 5.27 / 9.80 / 16.3 / 22.9 in 3D), and an `Extend` field there changes
  nothing while that option is on (the smaller size wins). With Air Grading, `mesh_region` turns it off and uses an
  `Extend` on all the region's boundary surfaces (3D) or lines (2D), `Mesh.MeshSizeMax` = the far size: growth 60
  gives 2.74 / 4.86 / 8.95 / 16.7 / 25.8, growth 20 gives 2.96 / 6.85 / 15.9 / 26.6 / 28.1 (8.3k against 14.2k
  elements), far 40 gives 7.2k elements. Time unchanged (L-04: 18.4 s either way).
- With Air Grading the air near bodies can get more elements than today (the grading is finer than today's jump when
  the growth is long); a far size above the air's size or a shorter growth gives fewer.

## 8. GUI

- `commands.py`: `AddRefineNear`, `AddSkinLayer`, `AddAirGrading` (`EMS_RefineNear`, `EMS_SkinLayer`,
  `EMS_AirGrading`), created and edited like Mesh Size (`_create_and_edit`, `gate`). A toolbar dropdown
  **Refinement** (like Structured Mesh) holding the three, in the "EMSolution Mesh" toolbar after Mesh Size; the menu
  lists them after Mesh Size; right-click: Refine Near for any pick, Skin Layer for whole bodies, Air Grading on the Air
  Region. Air Grading's command with nothing selected takes the Study's Air Region.
- `taskpanels.py`: the three panels follow `ItemPanel` (pick list, gate, labels, OK/Cancel transaction). Refine Near
  adds the four lengths and a **Limit to** list with Add selection / Remove. Skin Layer adds δ, elements per depth,
  layer depth, QuadLayers (shown in 2D only) and the calculator group (frequency, conductivity, μr, Calculate, the
  result). Air Grading adds growth distance and far size, with the resolved air size shown beside "0 = air's size".
- Icons: `refinenear.svg`, `skinlayer.svg`, `airgrading.svg` and `refinement.svg` (the dropdown) in `freecad_addon/icons`,
  drawn in the style of the set from commit 7825595.
- Labels in the 3D view use `_size_text`.

## 9. Stages and the review catalogue

Each stage ends with catalogue rows the user opens one by one and comments on; the next stage starts after their
review. Built like `experiments/symmetric_catalogue`: `experiments/refinement_catalogue/build_catalogue.py` builds each
row as a saved Study (set-up file in its own folder, git-ignored), meshes it into
`C:\Users\hamed\Desktop\delme\refinement_studies\<id>\`, and also meshes a "today" copy without the new items. A page
(an Artifact) shows, per row: what it shows, a gmsh picture of the new mesh and of today's (3D rows cut at a plane
through the refinement), element counts per part for both, and the file paths. `--only <ids>` rebuilds a few rows.

| Stage | Built | Rows (ids are proposals) |
|---|---|---|
| 1 | Refine Near in ordinary Studies (objects, validation, job, mesher, panel, command, icon) | RN-01 2D magnet corners (vertices); RN-02 3D magnet, an edge; RN-03 2D stator tooth tips (edges); RN-04 3D, a face limited to one body; RN-05 whole body; RN-06 two Refine Near + a Mesh Size overlapping (smallest wins); RN-07 a face of the Air Region; RN-08 sliding Study with a structured air gap: a refinement on the magnets beside it leaves the gap's divisions unchanged; RN-09 refusals (coarse < fine, zero growth, deleted pick) |
| 2 | Refine Near in symmetric Studies (spike 7.3 first) | RN-S1 2D cell, magnet corners; RN-S2 a pick on a copy mapped to the cell; RN-S3 a face on the periodic seam; RN-S4 3D cell; RN-S5 free object in a symmetric Study; RN-S6 sliding symmetric motor with a structured gap, refinement on the teeth |
| 3 | Air Grading, both kinds | AG-01 2D bodies in a large air box; AG-02 3D; AG-03 Far size override; AG-04 sliding with a structured gap: the gap is unchanged; AG-S1 air around symmetric copies 2D; AG-S2 3D; AG-05 refusals (two on one air, on a body) |
| 4 | Skin Layer: calculator, graded layer, 2D quad layers | SL-01 3D aluminium block 1 kHz; SL-02 same at 5 kHz; SL-03 2D round wire, graded; SL-04 2D round wire, quad layers; SL-05 2D rectangular bar, quad layers (corners); SL-06 cell conductor in a symmetric Study; SL-07 warning when the layer fills the body |

Each stage also keeps the add-on suite green (`pixi run -e addon test-addon`), lint clean, and runs the GUI smoke test
when it touches GUI code.

## 10. Testing

- Unit tests (GUI-free modules): property defaults, validation messages, job keys written only when items exist, the
  skin depth formula (copper 50 Hz ≈ 9.3 mm, aluminium 1 kHz ≈ 2.69 mm).
- Mesher tests in `tests/freecad_addon/test_mesher.py`, `test_mesher2d.py`, `test_meshgroups.py`: element counts and
  local sizes near the picks fall within bounds; a job without the new keys gives the same mesh as before (count and
  node coordinates).
- The catalogue rows as the end-to-end check per stage.

## 11. Left to the builder

- Exact `Distance` sampling rule (the demos used 200–500 samples on 250 mm circles and 40–60 on 40 mm faces); keep
  it bounded so huge faces stay fast.
- Panel layout details, wording of messages within the house style of `validation.py`.
- Icon artwork within the existing set's style.
- Whether `Restrict` needs the boundary curves of a 3D body's faces as well (the demos passed surfaces only in 3D and
  it worked).

## 12. Calls I made (for the user to check)

1. Defaults: Refine Near FineSize = half the default mesh size, CoarseSize = the default size, GrowthDistance =
   5 × FineSize; Skin Layer 2 elements per δ over 3δ; Air Grading growth = 10 × default size, far size = the air's size.
2. Skin Layer takes whole bodies only, and grows to the body's own size, not a size you enter.
3. One Air Grading per air; Air Grading reads the air's size rather than repeating it.
4. In symmetric cells, distances stop at the cell boundary, except that a pick on a periodic seam also refines the
   partner face. (Your decision: cell items never reach the air around copies.)
5. The three items share one toolbar dropdown "Refinement" rather than three buttons.
6. QuadLayers in a 3D Study is a warning (ignored), not an error.
7. μr in the calculator is prefilled from the body's material; conductivity is not stored in materials.
8. Skin Layer and whole-body picks skip faces that are only cuts: the domain's outer boundary, periodic boundaries and
   symmetric seams (5.2).
9. Air Grading's far size never coarsens a body's surface: the faces the air shares with bodies keep today's size
   (5.3).
10. If the Stage 2 spike finds no option fast and correct enough, work stops and you decide (7.3).
