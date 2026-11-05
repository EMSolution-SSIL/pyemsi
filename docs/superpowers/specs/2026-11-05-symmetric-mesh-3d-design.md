# Symmetric Mesh for 3D FreeCAD Studies: Requirements and Design

Date: 2026-11-05
Status: agreed in conversation, waiting for review
Branch: `main` (the dev branch)
Builds on: `2026-10-23-symmetric-mesh-design.md` (the 2D design, "the 2D spec" below). Read that first: everything
it says holds in 3D unless this document changes it.
Evidence: `experiments/gmsh_symmetry/c_mesh_copy_3d.py` and `e_transfinite.py` copy 3D cell meshes (tets, hexes,
pyramids, mirrored and rotated) with 0 inverted elements and 0 non-conforming facets.

## 1. Goal

The same feature as in 2D, for 3D Studies. The user models one 3D cell (for a motor, typically a 2D cell extruded to
the stack length), builds the full model from it with Mirror and Polar Array, and gets a full-model mesh in which
every copy has exactly the cell's mesh. Each piece of the drawing (now a **solid**) gets its own Material, as in 2D,
so every coil copy can be its own excitation region. Only the cell is meshed.

Success: a 3D version of the 2D motor example (`experiments/symmetric_examples/1_motor_sliding`, extruded) validates
and meshes, with sliding motion and excitation surfaces, and with 0 inverted elements and 0 gaps between copies.

## 2. Scope

- In: 3D Studies; mirror planes that contain the Z axis and polar arrays about Z (the same chain as in 2D); mesh
  settings on the cell (sizes, Transfinite Body / Edges, Recombine); Materials on solids of the top; **excitation
  surfaces** (copied, section 5); **sliding motion**, Rotational, full turn (section 6).
- Out (later): mirror planes not through the Z axis, in particular the z = 0 mirror of a motor stack (the user parked
  this; the cell spans the whole stack height for now); translations / linear arrays; Air Regions in a symmetric
  Study; Axial gap and Linear sliding.
- Anti-goal (unchanged): the user never has to Explode compounds. Mixed Studies (some bodies copied, some meshed
  normally) stay out, as in 2D.

## 3. The user's workflow

1. Model the cell as solids, every solid inside the cell (between the mirror plane and the face the array turns), so
   copies only touch. As in 2D, the air is modelled in the cell: no Air Region. With sliding, the air gap is split
   at the sliding cylinder into a stator part and a rotor part, both solids of their cells.
2. Build the full model with the same objects as in 2D (Compound, Part Mirror, Draft Polar Array, Boolean Fragments).
   The top object goes in Main (and Moving with sliding).
3. Add a Symmetric Mesh item on the top object, as in 2D.
4. **Materials on pieces = solids of the top.** In the Material panel the user clicks a **face** in the 3D view; the
   panel takes the **solid that face belongs to**, lists it as `SolidN` of the top and highlights it (decided by the
   user). Inner solids (a coil inside iron) are reached by hiding or making the iron transparent, as usual in FreeCAD;
   nothing extra is added for that.
5. **Excitations on faces of the top**, picked as in a normal 3D Study (a click stays a face).
6. Mesh settings on the cell bodies, or picked on any copy and moved to the cell (`objects.to_cells`, as now).
7. Sliding Interface: Rotational, Radius, Divisions, CrossDivisions; no Air Region.
8. Validate Study, Run Mesh. Output as today for 3D: `pre_geom.msh` (+ `rotor_mesh.msh` with sliding), `mesh.unv`.

## 4. The chain (`symmetry.py`)

Unchanged rules and transforms: mirror normals with no z component, polar arrays about Z with no axial interval. The
error texts that say "2D, XY plane only" must not say that in a 3D Study (they say the mirror plane must contain the
Z axis). A Boolean Fragments with no Mirror/Array below it is one cell body, now with several **solids** (the 3D form
of the split cell).

## 5. The mesher

`mesher.py` hands a job with a `"symmetric"` key to `meshsym` the way `mesher2d.py` does; `meshsym` works for
`dim` 2 and 3. Per side, in 3D:

1. Build the cell with `mesher.build` (cells imported as solids, settings applied as today).
2. Sliding: section 6.
3. **Periodic seams:** for faces `c != d` of the cell with `T(c) == d` for one of the side's transforms, mesh `d` as a
   copy of `c` (`setPeriodic(2, …)`); same rules as the 2D curve version (one master per face, a master is no copy;
   a face a transform maps onto itself needs nothing). The match test is the 3D form of `_same`: same area, the same
   corner points after the transform, and sample points of `c` moved lie on `d`. Without this the rotated seams do
   not share nodes (`c_mesh_copy_3d.py --mode rotate-free`: 5920 non-conforming facets).
4. Mesh to 3D (`generate(job, 3)`).
5. **Landing and coverage of Materials:** as in 2D, with solids for faces and volume for area: element centres of
   each cell volume entity, moved by each transform, must lie inside exactly one piece solid; the copies landing on
   each piece must add up to its volume.
6. **Copy** volumes as discrete 3D entities (reverse mirrored copies, merge duplicate nodes, renumber), as in 2D.
7. **Excitation surfaces (copied):** the cell's surface mesh is copied with the same transforms. Each copied surface
   patch that lands on a picked excitation face (its element centres lie on that face) gets that excitation's SMAT_ID
   and name, exactly like a volume copy gets the MAT_ID of the piece it lands on. Coverage: the patches landing on
   each excitation face add up to its area; otherwise refuse, naming the face (the cell is not split where the
   excitation face ends, or the drawing is not symmetric). Excitation faces must come out as 2D physical groups in
   the same file as their body's volumes, as `mesher.py` writes them now (the moving side's file with sliding).
8. **Conformity check:** every element face used by only one element of a side lies on the outer boundary of that
   side's pieces (the 3D form of `_conform` / `_outline`): otherwise refuse, naming the place.

`--check` (Validate Study's mesher check) runs steps 1 to 8 without writing, as in 2D.

## 6. Sliding motion

"Similar to 2D" (the user). The sliding surface is the **cylinder** of the interface's Radius about Z, without an Air
Region; the slide marker is the line on that cylinder at 0° (a discrete line entity on the moving side), which is
what 3D sliding writes now.

- Each side's cell must have faces on the cylinder (both sides must reach it), and the cylinder must run over the
  whole height of the drawing, so it separates the moving side from the fixed one.
- On each cell's cylinder faces: transfinite, with the share of `Divisions` around Z that the face's angle gets
  (whole number, ends on the 360° / Divisions grid from 0°, as in 2D), and `CrossDivisions` along Z over the
  cylinder's height. The faces use the same triangle direction / corner order as 3D sliding does now
  (`_slide_faces`), so a shift by one division gives the same surface mesh.
- After copying, each side has the same nodes on the cylinder (the 3D form of `_on_circle`); otherwise refuse.
- **Only the nodes have to match** (decided by the user): EMSolution needs the same nodes on both sides of the
  sliding surface, not the same triangles. A mirrored copy flips the triangle diagonals on its part of the cylinder,
  so each side's cylinder has bands of both diagonal directions, and the bands of the two sides need not line up
  (stator cells 15°, rotor cells 22.5°). That is accepted; the check compares nodes only, and nothing re-triangulates.
- Validation as in 2D: one interface, Rotational only, Divisions a multiple of each side's copy count.

## 7. Add-on objects, panels, validation

- **Material pieces:** `Pieces` holds `(top, "SolidN")` in 3D; `PieceCentres` the solid centres. Every solid of a top
  has exactly one assignment; the 2D checks for gone / moved / missing / double pieces and for one side per
  assignment apply with solids for faces.
- **Material panel:** in a symmetric 3D Study the gate accepts face clicks on a top and turns each into its solid.
  A face shared by two solids: take the solid on the far side of the face from the camera, the one being looked at
  through the hidden or transparent neighbour (my call). If that cannot be told, ask the user which of the two.
- **Excitations:** allowed in symmetric 3D Studies, on faces of the top object. An excitation on a cell body is
  refused ("pick the faces on the drawing"); its copies are not where the user sees them.
- **Symmetric Mesh item:** unchanged; its command is available in 3D Studies.
- **Validate Study (`_symmetric`):** a 3D Study or a 2D XY Study; cells must have solids in 3D (faces in 2D); the
  overlap check (`_overlaps`) compares volumes in 3D (`common.Volume` against a small share of the smaller volume);
  the overlap point's z is shown too. Everything else as in 2D.
- **Job (`write_symmetric`):** pieces exported as solids; the excitation faces of the top exported with their
  SMAT_IDs; cells use the 3D `volumes` list. The slide block gets `cross_divisions` in 3D.

## 8. Decided by me (Claude), not by the user; check these

- Excitation faces land on copies by element centres with an area coverage check (the user said "copied, like 2D";
  the landing rule is mine).
- A face shared by two solids picks the solid on the far side from the camera.
- An excitation on a cell body is refused rather than moved to the drawing.
- The sliding cylinder must span the whole height of the drawing.
- Success is judged on an extruded version of the 2D motor example.
- An excitation face that two copies share (it lies between them) counts once toward its area in the coverage check.
- Excitation faces travel in the job's `symmetric` block (per side, with SMAT_ID, name and file), not in
  `job["surfaces"]`, because the top they lie on is not among the meshed volumes.

## 9. Left to the builder

- How `meshsym` is made dimension-generic (one module with `dim`, or small 2D / 3D helpers).
- Tolerances of the landing, coverage, seam and cylinder checks.
- How the panel finds the far-side solid of a clicked face (pick point and view direction, or another way).
- The 3D example files (extrude the 2D examples in `experiments/symmetric_examples/build_examples.py`, or new ones),
  unit tests in `tests/freecad_addon/`, and the GUI smoke test for picking solids.
