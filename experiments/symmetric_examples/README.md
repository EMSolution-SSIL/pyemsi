# Symmetric Group examples (2D)

Seven Studies for trying the Symmetric Group live. Examples 1 to 4 and 7 open fully set up and mesh as they are. The
challenges then break or extend them. Examples 5 and 6 are broken on purpose: they show the copies of a cell
overlapping, which Validate Study refuses. Every result quoted below was checked headless with
`pixi run -e addon python experiments/symmetric_examples/build_examples.py --challenges` (0 inverted elements by
signed area, 0 gaps between copies). That command also rebuilds the files.

## Before you start

- FreeCAD loads the add-on through the Mod folder link. Start FreeCAD with `pixi run -e addon freecad`.
- To point the link at a checkout, run `pixi run -e addon install-addon` in it.
- The build script uses whatever the link points at, and it says which one on its first line (`add-on: ...`).

## The workflow

1. Draw one cell: the cell objects, each a face (a solid in 3D). A cell object may be a Boolean Fragments, to cut it
   into blocks.
2. Select them and click **Symmetric Group**. In its panel, add the rules in order: mirror first, then rotate the
   results, or any order you need (a translation too). The drawing shows every copy at once, and the cells are hidden
   after OK, so that clicks land on the drawing. No Mirror, Polar Array or Fragments is needed.
3. Name the parts. Each row (a face of a cell object) is one part, each copy a part of its own, parts merged across
   chosen rules, or a table with a name per copy (the table dialog can generate a three-phase winding).
4. OK makes one Material per part. To give it a library material, click a copy on the drawing and click Assign
   Material; **All parts of this object** in that panel sets every part of the same cell object at once.
5. A drawing made with Mirror, Polar Array and Boolean Fragments can still fill a group: select its top object and
   click **Read from drawing** in the panel.

The cell objects are not in the Study's Main or Moving geometry. The Main geometry holds only free objects, bodies
meshed as usual around the copies. With sliding motion, the group's Side says whether it is fixed or moving.

The drawing in examples 1 to 3 is the spike motor. Stator cell, 0 to 15°: `StatorIronCell`, `CoilCell` (37 to 50 mm,
10 to 15°) and `StatorAirCell` (35 to 36 mm). Rotor cell, 0 to 22.5°: `RotorIronCell`, `MagnetCell`, `RotorAirCell`.
The stator's rules are a mirror at 15° and a rotation of 30° × 12; the rotor's a mirror at 22.5° and 45° × 8.

## 1. Motor with sliding motion (`1_motor_sliding`)

12 slots and 8 poles. Two groups, `Stator` (Fixed) and `Rotor` (Moving), a Rotational Sliding Interface at R 35 with
144 divisions and no Air Region. Every row is named by a table: `StatorIron`, `StatorAir`, `Coil01` to `Coil12` (the
two halves of a slot are one coil), `RotorIron`, `MagnetN`, `MagnetS` and `RotorAir`.

- **As is:** Run Mesh writes `pre_geom2D.msh` and `rotor_mesh2D.msh`, 8328 triangles in total, and 18 MAT_IDs.
- **Look at:** the group panel (its rules, rows and the summary "24 copies, 14 parts"), and the Materials panel (one
  row per part).
- **Challenge A:** change the stator's rotation count to 11 (the step stays 30°). Expect
  *the table of CoilCell has 24 names, the group makes 22 copies* (one per row), and
  *the divisions (144) must be a multiple of the 11 turns of Stator's cell objects*.
- **Challenge B:** set Divisions to 100. Expect *must be a multiple of the 12 turns of Stator's cell objects* and
  *… of the 8 turns of Rotor's cell objects*.
- **Challenge C:** delete the Material `Coil05`. Expect *Parts with no Material: Coil05. Open the group and choose
  their Material.*
- **Challenge D:** add a small circle face (a bolt hole in one tooth) to the stator group's cell objects. Expect
  *cell body StatorIronCell overlaps BoltHole near (54.5295, 7.17894), by 7.07 mm². Cell objects may only touch:
  make them with Part Slice or Boolean Fragments, or cut one out of the other.* and *Parts with no Material:
  BoltHole*. The way to a hole is to cut it out of the iron cell: then every tooth has one.

## 2. Stator with a structured coil, set from picks on the drawing (`2_stator_structured`)

The stator alone, no movement. `CoilCell` has a Transfinite Body and a Recombine. The two Transfinite Edges items
(`coil arcs 4 el`, `coil sides 8 el`) were made from edges picked on the drawing. A pick there becomes the cell's
edge, and a slot wall becomes the edge of both `CoilCell` and `StatorIronCell`.

- **As is:** 768 quads (24 coil halves × 4 × 8) and 4824 triangles elsewhere. Every coil copy has the same grid.
- **Look at (GUI only):**
  - Open `coil sides 8 el` and look at its rows: each slot wall is listed on both cells.
  - In a new Recombine, click a coil face on any copy (for example slot 7, mirrored). The row says `CoilCell`.
  - In a new Transfinite Body, click a coil face, Ctrl+click a coil corner on another copy, then Add selection. You
    get the `CoilCell` row (a one-face cell is stored whole) and one corner, on `CoilCell` only, although
    `StatorIronCell` has that vertex too.
- **Challenge:** put the outer coil arc (r 50) in its own Transfinite Edges with 5 elements (remove it from
  `coil arcs 4 el`). Expect *structured body CoilCell: face at (42.7714, 9.48219, 0) opposite sides have 8/8 and 5/4
  elements; they must match*.

## 3. Split coil: a Boolean Fragments as a cell object (`3_split_coil`)

The coil is cut in two by an arc at r 43. `CoilFragments` is a Boolean Fragments of `CoilCell` and `CoilDivider`,
and it is a cell object of the group in the coil's place. It is **one cell object with two faces**, so two rows.
Face1 is the outer block (43 to 50) and Face2 the inner block (37 to 43). Materials: a two-layer winding, so each block
is a coil of its own. Each slot has `CoilNNInner` (its two inner blocks) and `CoilNNOuter` (its two outer blocks),
`Coil01Inner` to `Coil12Outer`, plus `StatorIron` and `StatorAir`. Only the outer block is structured and recombined,
through face picks `(CoilFragments, Face1)`.

- **As is:** 384 quads (24 outer blocks × 4 × 4), 5136 triangles in the rest. 26 MAT_IDs.
- **Look at (GUI only):** a face click on the drawing is that block:
  - In the Transfinite Body panel, click an inner block on any copy. The row is `CoilFragments.Face2`, not the whole
    `CoilFragments`.
  - Click the outer block on another copy. You get "Nothing new to add" (`Face1` is already in the list).
  - Click an iron face. The row is `StatorIronCell` (a one-face cell is stored whole).
  - Do the same in a Recombine panel.
- **Challenge A:** add the inner block (`CoilFragments.Face2`, picked on any copy) to the Transfinite Body. Expect
  *Transfinite Body TransfiniteBody: CoilFragments Face2 has edges without Transfinite Edges: Edge5, Edge6, Edge7*.
  Then give its inner arc 4 elements and its two sides 3 elements. It meshes: the inner blocks become structured
  triangles (5376 in all), because only Face1 is recombined.
- **Challenge B:** add `CoilDivider` itself to the group's cell objects (not inside a Fragments). Expect
  *cell object CoilDivider has no face; a cell object must be a face. To cut a cell into blocks, put its face and the
  cutting sketch in a Boolean Fragments and use that in the group.*

## 4. Your PRD reproduction file (`4_prd_test_file`)

A copy of `experiments/symmetric_spike/test.FCStd`, the file from the split-cell PRD, where `stator_air_cell` and
`core_cell` are Fragments of a face and a divider sketch. It was saved with the older Symmetric Mesh item, which
Validate now refuses: *Symmetric Mesh Symmetric Mesh001 is from an older version. Add a Symmetric Group; Read from
drawing fills it from stator_fragments.* The script does what you would do, on a fresh copy each run:

- Read from drawing on `stator_fragments` proposes the cells `coil_face_cell`, `stator_air_cell` (2 faces) and
  `core_cell` (3 faces), with a mirror at 15° and a rotation of 30° × 6.
- The older item and its Materials are deleted, and `stator_fragments` leaves the Main geometry: the group draws it.
- Parts: each coil copy separate (`coil_face_cell_1` to `_12`), and one part each for `stator_air` and `core`, named
  by tables across their faces.
- **As is:** it validates clean and meshes, 828 triangles, 14 MAT_IDs.
- **Try:** structure the blocks of `core_cell` by clicking them on the drawing, as in example 3.

## 5. A cell object past the mirror's plane (`5_coil_past_mirror_line`)

Broken on purpose. The coil is drawn 10 to 17° in a 0 to 15° cell, so it reaches 2° past the mirror's plane and
overlaps its own mirrored copy (13 to 20°). Everything else is as in example 2, with a Material on every part.

- **Validate Study:** *Symmetric Group Stator: cell body CoilCell overlaps a mirrored copy of CoilCell near (42.3219,
  11.3401), by 39.5 mm². The copies of a cell object may only touch: keep every cell object clear of its own copies,
  and check the rules (a mirror's plane, a rotation's step and count, a translation's vector).* The point is the
  middle of the overlap, at 15°, and clicking the row highlights `CoilCell`.

## 6. Thirteen copies of a 30° pitch (`6_thirteen_copies`)

Broken on purpose. Example 2's cells, but the rotation spreads 13 copies of the 30° slot pitch over 360°, so they are
27.7° apart and each copy overlaps the next by 2.3°.

- **Validate Study:** *Symmetric Group Stator: cell body StatorIronCell overlaps a mirrored copy of StatorIronCell
  near (48.9868, 0.986649), by 46.4 mm². …* (the same advice). The point is at 1.2°, where the last copy reaches over
  the first (0 to 2.3°).

## 7. The split coil drawn as two faces (`7_coil_two_faces`)

Example 3's coil cut the other way: `CoilOuterCell` (43 to 50) and `CoilInnerCell` (37 to 43) are two cell objects
that share the arc at r 43. No Fragments.

- **As is:** meshes, 5808 triangles, 26 MAT_IDs (the same two-layer coils `Coil01Inner` to `Coil12Outer` as
  example 3), 0 inverted, 0 gaps. The two faces mesh node to node along the arc they share.

## Known limits

- A model is all 2D or all 3D. No Air Region in a symmetric Study: draw the air, as a cell object or a free object.
- Sliding is Rotational about Z only, over the full turn. A group that reaches the sliding surface may only turn about
  Z through the origin or mirror in a plane that contains Z (or in z = const).
- Copies of two groups on the same side may not touch: put them in one group, or draw a free object between them.
- A vertex picked on the drawing, with no face of its cells in the same selection, becomes a corner of every cell
  object that has it. Validation then names any that lie on none of the item's structured faces.
