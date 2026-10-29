# Structured mesh examples (2D and 3D)

Seven Studies to try face picks, corners and partly structured regions: four in 2D and three in 3D. Each opens set up and meshes as it is.
The challenges then break or extend it. Every expected result below was checked headless with
`pixi run -e addon python experiments/structured_examples/build_examples.py --challenges`, which also rebuilds the files.

The files were made without the GUI, so the inputs of each Fragments object are hidden and there are no Materials yet.
In all four, Main geometry is the `Geometry` group (Container mode).

## 1. Ring sectors: curved blocks

A quarter ring (r 20 to 40, 0 to 90 degrees) cut into 6 blocks with arc sides: 2 rings × 3 sectors.
It has: `arcs 8 el` (Uniform), `radials 5 el bump` (Bump 0.3), and a whole-body Transfinite Body and Recombine.

- **As is:** all quads, curved rows, nodes bunched at both ends of each radial line.
- **Challenge:** move one outer arc (r = 40, 0 to 30 degrees) into a new Transfinite Edges with 9 elements.
  Expect: *opposite sides have 8/9 and 5/5 elements; they must match*.
  Leaving it in `arcs 8 el` as well gives *Edge… is in Transfinite Edges arcs 8 el and …* instead.

## 2. Mixed: structure some faces, leave the rest

One Fragments body with 4 faces: two squares `block_a` and `block_b`, a 5-sided `roof` on top of them, and `holed`
(a plate with a round hole) on the right. The Transfinite Body picks only the two square faces. The Recombine picks
those two faces and the holed face.

- **As is:** quads in the squares, triangles in the roof, free (unstructured) quads around the hole.
- **Challenge A:** add the roof face to the Transfinite Body. First expect Validate Study to list its edges
  without Transfinite Edges. Give the two slopes 4 el and the two short sides 3 el. Expect
  *has 6 boundary points and 5 corners on it; it needs 3 or 4 (choose Corners …)*.
  Then pick the 4 corners (0,10), (20,10), (20,18), (0,18): it meshes. The bottom is 4 + 4 elements and so is the top.
  `2_mixed_partial_roof_solved.FCStd` is the solved version.
- **Challenge B:** put the holed face in its own Transfinite Body and give its edges counts. Expect
  *has a closed edge (circle?); it cannot be structured*.
- **Challenge C:** add `block_a`'s face to a second Transfinite Body. Expect
  *mixed_fragments.Face1 is in Transfinite Body TransfiniteBody and TransfiniteBody001*.

## 3. T-junction: a face with 5 boundary points

A tall block (10 × 20) beside two 10 × 10 blocks, so the middle of the tall block's right side has a point where no
corner is. `long 8 el` is the tall left edge; `short 4 el` is every other edge (two of them make the right side: 4 + 4).

- **As is:** meshes, with the note *has 5 boundary points; using the 4 where the boundary turns as corners*.
- **Challenge:** set `long 8 el` to 7. Expect *opposite sides have 4/4 and 8/7 elements; they must match*.
  Also try choosing all 5 points as Corners. Expect *… 5 corners on it; it needs 3 or 4*.

## 4. Coil traced by its neighbour (the coil_cell fix)

`coil_cell` is a face from a sketch. `air_sketch` traces the coil's left edge as external geometry, and
`air_fragments` = air_cell + air_top. Before the fix, the coil disappeared from the Study.

- **As is:** the Materials panel offers both `coil_cell` and `air_fragments`. Validate Study gives no
  *not meshed on its own* warning. Everything meshes to quads.
- **Challenge:** in `air_top_sketch`, widen the rectangle to x = 15 so that it also covers the coil.
  Then pick the edges again in Transfinite Edges (they are renumbered). Expect
  *face at (7.5, 15, 0) opposite sides have 8/4 and 4/4 elements*: the bottom is now split by the coil's corner.

# 3D

In 3D a Transfinite Body takes whole bodies only: every solid of the body is structured, and each must have
5 or 6 faces. To leave a part unstructured, make it a separate body rather than a piece of the Fragments.
Recombine turns the structured solids into hexahedra; a 5-face solid (a wedge) also gets prisms along its
collapsed edge.

## 5. Ring sectors, extruded

Example 1 extruded 10 mm: 6 solids with curved faces. It has `arcs 8 el`, `radials 5 el bump` and `axial 3 el`.

- **As is:** 720 hexahedra, nothing else.
- **Challenge A:** pick a single face into the Transfinite Body. Expect
  *pick whole solids in a 3D Study (ring_fragments.Face1)*.
- **Challenge B:** give one outer arc on the bottom (r = 40, 0 to 30 degrees, z = 0) 9 elements. Expect
  *face at (38.2, 10.2, 5) opposite sides have 3/3 and 9/8 elements*. It is the outer curved face that refuses.

## 6. Partly structured: a core beside a free body

`core_fragments` = two 10 mm boxes plus a wedge (5 faces) on top of `box_a`, all structured and recombined.
`holed_block` is a separate body against `box_b` with a round hole through it, left alone.

- **As is:** 176 hexahedra and 16 prisms in the core, 437 tetrahedra in the holed block, and 16 pyramids on the
  face where the hexahedra meet the tetrahedra.
- **Challenge A:** add `holed_block` to the Transfinite Body and give its edges counts. Expect
  *structured body holed_block: volume has 7 faces, needs 5 or 6*.
- **Challenge B:** delete the Recombine. It still meshes, but as structured tetrahedra only (1484), no hexahedra.

## 7. T-junction in 3D

The 2D T-junction extruded: a tall block (10 × 10 × 20) beside two 10 mm cubes. The tall block's side face is split
in two, so the tall block has 7 faces.

- **As is:** refused. Expect *piece at (5, 5, 10) has 7 faces, needs 5 or 6 (split by a touching body, or slice it
  further)*. In 2D the same shape works, because a face may have extra boundary points; a solid may not have
  extra faces.
- **Fix:** `7_3d_t_junction_sliced.FCStd` builds the tall block as two cubes. Then all edges are 4 el, giving
  256 hexahedra.
