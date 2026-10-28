# Split cell bodies in a Symmetric Mesh (problem definition and PRD)

Status: proposal, implemented 2026-10-28 (see the update below). Scope: 2D only, as in `2026-10-23-symmetric-mesh-design.md` (3D is out for now).

Update 2026-10-28, after the merge of the face-pick work (`2026-10-27-face-mesh-settings-design.md`): R1 is
implemented. R4 is implemented in its small form: a Boolean Fragments with no Mirror or Polar Array below it is one
cell body with several faces. Mesh settings take its faces through the face picks, a face clicked on the top is that
block of the cell, and Materials stay on the pieces of the top. R2 still works, and both ways are now written into
step 1 of section 3 of the symmetric-mesh spec. R3 is implemented as an overlap check in Validate Study: the cell is
tested against each of its copies, and a cell body that overlaps one is named, with the point where. Every leaf is in
the cell, so a cell body cut by the full drawing can only come from such an overlap.

## 1. Problem

A user wants one drawn face of a cell to become several pieces, for example one stator-air face cut into two so the
pieces can get different Materials. The natural way in FreeCAD is a cutting sketch or line plus a Part Boolean Fragments
(or Slice apart) on the cell. The Symmetric Mesh does not support this, and it fails in confusing ways.

Reproduction: `experiments/symmetric_spike/test.FCStd`. The cells `stator_air_cell` and `core_cell` are Boolean
Fragments of a face and a divider sketch (`stator_air_div`, `core_div`), placed in `stator_cell`, then mirrored,
polar-arrayed and fragmented.

Two errors appear in sequence:

1. `Mesher: vol_3.brep: expected 2D entities, got [(1, 12)]`. The chain walker (`symmetry._walk`) treats every drawn
   object below a Fragments as a cell body. The divider sketch has a shape and nothing under it, so it counts as a body.
   It is exported as a body and gmsh reads it as a curve.
2. If the dividers are ignored, `copy lands outside the drawing near (59.6881, 14.2679)`. The cell bodies are then the
   undivided faces. The mesh of an undivided face runs across the divider, so its elements straddle two pieces of the
   full drawing. The landing check (`meshsym._land`) needs every element centre to be inside exactly one piece, and
   fails. Here the point is on `stator_air_face` (29.27 mm²) and on a 6 mm² piece of the full Fragments.

Root cause: the cell bodies are the leaf objects under the chain, and a Fragments below a cell is read as "only
splits, moves nothing". The split it makes never reaches the mesh, so cell bodies and pieces disagree.

## 2. Goals

- A user can cut a cell face into pieces and give each piece its own Material.
- A wrong setup gives one clear message in Validate Study, never a mesher error naming a BREP file or coordinates.
- No Explode steps for the user (spec anti-goal, section 1).

## 3. Non-goals

- 3D. Mirror and rotation only, XY plane only (as in the symmetric-mesh spec).
- Cutting by anything other than the existing Part tools (no add-on drawing tool).

## 4. Requirements

R1 (must). A cell body that has no face (sketch, line, wire) is refused in Validate Study. The message names the object
and says: a cell body must be a face; to cut a cell, draw each piece as its own face.

R2 (must). The supported way to cut a cell is to draw each piece as its own face (two sketches, two Part Faces sharing
the divider edge) and put those faces in the cell compound. The final Fragments joins the shared edges, so the pieces
mesh conformally. This should be written into the user documentation and the symmetric-mesh spec, section 3, step 1.

R3 (should). Validate Study also checks, before the mesher, that each cell body lies inside one piece of the full
drawing (or that its pieces add up), and names the body if not. Today this is found only in the mesher.

R4 (could, larger). Accept a Fragments or Slice inside a cell and use its faces as the cell bodies. These faces are not
document objects, so this needs sub-element cell bodies: mesh settings (sizes, transfinite, recombine) and Materials
keyed by (body, face), and `job.json` and the BREP export changed to match. Do this only if R2 proves too hard for
users.

## 5. Acceptance

- R1: a cell compound containing a sketch or line is refused in Validate Study; unit test in `test_symmetry.py`.
- R2: a sample document with a cell drawn as two faces meshes with no errors, 0 inverted elements, and the two pieces
  carry their own Material IDs.
- R3: a cell whose face is cut by the full drawing but not in the cell is refused before the mesher runs.

## 6. Open questions

- Is R2 good enough, or do users expect to cut after drawing (R4)?
- Should Validate Study offer a hint when it sees a cell Fragments with a divider (suggest the two-face way)?
