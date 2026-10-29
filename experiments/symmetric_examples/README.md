# Symmetric Mesh examples (2D, after the face-pick merge)

Seven Studies for trying the merged `feature/symmetric-mesh` branch live: the Symmetric Mesh and the face picks
together, plus the new split cell (a Boolean Fragments inside a cell). Examples 1 to 4 and 7 open fully set up and
mesh as they are. The challenges then break or extend them. Examples 5 and 6 are broken on purpose: they show the
case that PRD R3 is about. Every result quoted below was checked headless with
`pixi run -e addon python experiments/symmetric_examples/build_examples.py --challenges` (0 inverted elements by
signed area, 0 gaps between copies). That command also rebuilds the files.

## Before you start

- FreeCAD loads the add-on through the Mod folder link. Start FreeCAD with `pixi run -e addon freecad`.
- To point the link at a checkout, run `pixi run -e addon install-addon` in it.
- The build script uses whatever the link points at, and it says which one on its first line (`add-on: ...`).
- The cells and chain objects are hidden, so that clicks land on the top Fragments. They are still in the tree, and
  you can pick them there.

The drawing in examples 1 to 3 is the spike motor. Stator cell, 0 to 15°: `StatorIronCell`, `CoilCell` (37 to 50 mm,
10 to 15°) and `StatorAirCell` (35 to 36 mm). Rotor cell, 0 to 22.5°: `RotorIronCell`, `MagnetCell`, `RotorAirCell`.
Each cell is a Compound, then Mirror, then Compound, then Draft Polar Array, then Boolean Fragments (`StatorFragments`,
`RotorFragments`).

## 1. Motor with sliding motion (`1_motor_sliding`)

12 slots and 8 poles. Main = `StatorFragments`, Moving = `RotorFragments`, one Symmetric Mesh item each, a Rotational
Sliding Interface at R 35 with 144 divisions and no Air Region. The Materials are on pieces: `StatorIron`,
`StatorAir`, `Coil01` to `Coil12`, `RotorIron`, `MagnetN`, `MagnetS` and `RotorAir`.

- **As is:** Run Mesh writes `pre_geom2D.msh` and `rotor_mesh2D.msh`, 8328 triangles in total, and 18 MAT_IDs.
- **Look at:** the Symmetric Mesh item panel (its cells and steps), and the Materials panel (one row per piece group).
- **Challenge A:** set `StatorArray` Number Polar to 11. Expect, among others:
  *the divisions (144) must be a multiple of the 22 copies of Symmetric Mesh's cell*, and
  *the faces of Coil02, Coil03, … no longer exist on StatorFragments (did the array count or the cell change?)*.
- **Challenge B:** set Divisions to 100. Expect *must be a multiple of the 24 copies …* and *… of the 16 copies …*.
- **Challenge C:** delete the Material `Coil05`. Expect
  *Pieces with no Material: StatorFragments.Face26, StatorFragments.Face29*.
- **Challenge D:** break the symmetry. Add a small circle face (a bolt hole in one tooth) to the `Objects` of
  `StatorFragments`. Expect *BoltHole is not copied the same way as the other cell bodies*.

## 2. Stator with a structured coil, set from picks on the Fragments (`2_stator_structured`)

The stator alone, no movement. `CoilCell` has a Transfinite Body and a Recombine. The two Transfinite Edges items
(`coil arcs 4 el`, `coil sides 8 el`) were made from edges picked on `StatorFragments`. A pick there becomes the
cell's edge, and a slot wall becomes the edge of both `CoilCell` and `StatorIronCell`.

- **As is:** 768 quads (24 coil halves × 4 × 8) and triangles elsewhere. Every coil copy has the same grid.
- **Look at (GUI only):**
  - Open `coil sides 8 el` and look at its rows: each slot wall is listed on both cells.
  - In a new Recombine, click a coil face on any copy (for example slot 7, mirrored). The row says `CoilCell`.
  - In a new Transfinite Body, click a coil face, Ctrl+click a coil corner on another copy, then Add selection. You get the `CoilCell` row
    (a one-face cell is stored whole) and one corner, on `CoilCell` only, although `StatorIronCell` has that vertex
    too.
- **Challenge:** put the outer coil arc (r 50) in its own Transfinite Edges with 5 elements (remove it from
  `coil arcs 4 el`). Expect *structured body CoilCell: face at (42.77, 9.48, 0) opposite sides have 8/8 and 5/4
  elements; they must match*.

## 3. Split coil: a Boolean Fragments inside the cell (`3_split_coil`) (new)

The coil is cut in two by an arc at r 43. `CoilFragments` is a Boolean Fragments of `CoilCell` and `CoilDivider`, and
it sits in the stator cell where the coil was. It is **one cell body with two faces**. Face1 is the outer block
(43 to 50) and Face2 the inner block (37 to 43). Before this merge, the divider was taken as a cell body of its own
and the mesher failed. Materials: a two-layer winding, so each block is a coil of its own. Each slot has
`CoilNNInner` (its two inner blocks) and `CoilNNOuter` (its two outer blocks), `Coil01Inner` to `Coil12Outer`, plus
`StatorIron` and `StatorAir`. Only the outer block is structured and recombined, through face picks
`(CoilFragments, Face1)`.

- **As is:** 384 quads (24 outer blocks × 4 × 4), triangles in the inner blocks. 26 MAT_IDs.
- **Look at (GUI only):** this is the decision "a face click on the top is that block":
  - In the Transfinite Body panel, click an inner block on any copy. The row is `CoilFragments.Face2`, not the whole
    `CoilFragments`.
  - Click the outer block on another copy. You get "Nothing new to add" (`Face1` is already in the list).
  - Click an iron face. The row is `StatorIronCell` (a one-face cell is stored whole).
  - Do the same in a Recombine panel.
- **Challenge A:** add the inner block (`CoilFragments.Face2`, picked on any copy) to the Transfinite Body. Expect
  *Transfinite Body TransfiniteBody: CoilFragments Face2 has edges without Transfinite Edges: Edge5, Edge6, Edge7*.
  Then give its inner arc 4 elements and its two sides 3 elements. It meshes: the inner blocks become structured
  triangles, because only Face1 is recombined.
- **Challenge B:** put `CoilDivider` straight into `StatorCell`'s Links (not inside a Fragments). Expect
  *cell body CoilDivider has no face; a cell body must be a face. To cut a cell into blocks, put its face and the
  cutting sketch in a Boolean Fragments and use that in the cell.*

## 4. Your PRD reproduction file (`4_prd_test_file`)

A copy of `experiments/symmetric_spike/test.FCStd` from the branch. That is the file from the split-cell PRD, where
`stator_air_cell` and `core_cell` are Fragments of a face and a divider sketch. The script copies it once and leaves
the copy alone after that.

- **Before:** *Mesher: vol_3.brep: expected 2D entities, got [(1, 12)]*.
- **Now:** the cells read as `coil_face_cell`, `stator_air_cell` (2 faces) and `core_cell` (3 faces). It validates
  clean and meshes, with 8 MAT_IDs and 0 inverted elements.
- **Try:** structure the blocks of `core_cell` by clicking them on the Fragments, as in example 3.

## 5. A cell body past the mirror line (`5_coil_past_mirror_line`): PRD R3

Broken on purpose. The coil is drawn 10 to 17° in a 0 to 15° cell, so it reaches 2° past the mirror line and overlaps
its own mirrored copy (13 to 20°). Everything else is as in example 2, with Materials on every piece.

- **Validate Study:** *Symmetric Mesh: cell body CoilCell overlaps a mirrored copy of CoilCell near (42.3219,
  11.3401), by 39.5 mm². The copies of a cell may only touch: keep every cell body inside the cell, between the
  Mirror's line and the edge the Polar Array turns, and check the Polar Array's count and angle.* The point is the
  middle of the overlap, at 15°, and clicking the row highlights `CoilCell`.
- Before R3, Validate Study's own checks found nothing, and only the mesher check said *the copies of the cell do not
  match near (41.5993, 12.7182) on the fixed side: their meshes meet there without sharing nodes*.

## 6. Thirteen copies of a 30° pitch (`6_thirteen_copies`): PRD R3

Broken on purpose. Example 2's drawing, but `StatorArray` spreads 13 copies of the 30° slot pitch over 360°, so they
are 27.7° apart. Each copy overlaps the next by 2.3°, and the Fragments cuts the cell bodies there (104 pieces
instead of 72). The Materials are set on those 104 pieces, so the piece checks pass.

- **Validate Study:** *cell body StatorIronCell overlaps a mirrored copy of StatorIronCell near (48.9868, 0.986649),
  by 46.4 mm². …* (the same advice). The point is at 1.2°, where the last copy reaches over the first (0 to 2.3°).
- Before R3, only the mesher check said *copy lands outside the drawing near (35.427, 2.16673)*, a point of the copy
  that failed, not of the overlap.
- (On an existing Study, changing 12 to 13 also gives the "Pieces with no Material" messages of Challenge 1A.)

## 7. The split coil drawn as two faces (`7_coil_two_faces`): PRD R2

Example 3's coil cut the other way: `CoilOuterCell` (43 to 50) and `CoilInnerCell` (37 to 43) are two separate faces
that share the arc at r 43, both straight in the cell compound. No Fragments in the cell.

- **As is:** meshes, 5808 triangles, 26 MAT_IDs (the same two-layer coils `Coil01Inner` to `Coil12Outer` as
  example 3), 0 inverted, 0 gaps. The final Fragments joins the shared arc, so the blocks mesh node to node.

## Known limits (unchanged by the merge)

- 2D, XY plane only. No Air Region in a symmetric Study. Rotational sliding only, over the full turn.
- `FaceN` of the top can renumber when the array count or the cell changes. Validation says so (Challenge 1A).
- A vertex picked on the top, with no face of its cells in the same selection, becomes a corner of every cell body
  that has it. Validation then names any that lie on none of the item's structured faces.
