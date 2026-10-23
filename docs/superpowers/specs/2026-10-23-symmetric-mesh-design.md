# Symmetric Mesh for 2D FreeCAD Studies: Requirements and Design

Date: 2026-10-23
Status: agreed in conversation, waiting for review
Branch: `feature/freecad-addon`
Evidence: `experiments/gmsh_symmetry/` (gmsh only) and `experiments/symmetric_spike/` (a real FreeCAD document,
throwaway). Numbers below come from those runs.

## 1. Goal

Many models repeat: a motor's stator is one slot pitch repeated 12 times, and a slot pitch is half a slot mirrored.
The user draws the repeating piece (the **cell**) once, builds the full geometry from it with FreeCAD's own Mirror and
Polar Array, and puts the mesh settings on the cell. Run Mesh then meshes **only the cell** and copies that mesh,
mirrored and rotated, onto the rest of the model. The result is a full model (not a reduced one with symmetry boundary
conditions), with:

- identical meshes in every copy (exactly symmetric, no meshing noise between copies),
- far less meshing work (spike: 166 + 275 nodes meshed for a 3648 + 4088 node machine),
- a **Material per piece of the drawing**: the stator iron is one Material over all its copies, but each coil copy has
  its own Material, because coils are excitations with their own current and phase.

It is general, not motor-only: any 2D model made of copies of a cell by mirrors and rotations.

## 2. Scope

- In: 2D Studies; mirror and rotation steps in any order and number; transfinite, recombine and mesh sizes on the cell;
  sliding motion (one cell per side).
- Out (later): 3D (works in the gmsh experiments, `c_mesh_copy_3d.py`, `e_transfinite.py`, but not wanted now);
  translations (linear repeats); Air Regions together with a Symmetric Mesh.
- Anti-goal: anything that makes the user Explode compounds. The spike needed three levels of Explode (120 objects in
  nested groups) to give pieces their own Material. The user rejected that: the add-on handles pieces.

## 3. The user's workflow (agreed)

Example: 12 slots, 8 poles, rotor moves.

1. Draw the cells as faces. Stator cell, 0..15°: half a tooth, half a slot's coil, the stator half of the air gap.
   Rotor cell, 0..22.5°: rotor iron, half a magnet, the rotor half of the air gap. **The air is drawn in the cells**;
   no Air Region.
2. Build the full geometry from each cell with FreeCAD tools, for example: Compound(cell bodies) → Part Mirror →
   Compound(cell compound, mirror) → Draft Polar Array (12 × 30°) → Boolean Fragments. The final object (here the
   Fragments) is what goes into the Study's Main or Moving geometry.
3. New **Symmetric Mesh** item: the user picks that final object. The add-on reads the steps from the objects under it
   (section 4) and shows them (read-only) with the cell bodies it found.
4. Assign Materials. A Material can now reference **pieces** (faces) of a body, picked in the 3D view like Excitation
   faces, and several bodies or pieces at once. Example: one Material "Stator iron" on all 24 iron faces of the
   Fragments; one Material "Coil 01" on the two half-coil faces of slot 1.
5. Mesh settings (Mesh Size, Transfinite Body / Edges, Recombine) go on the **cell bodies**.
6. Sliding Interface: Radius and Divisions as today, but without an Air Region (section 6).
7. Validate Study, then Run Mesh. Output files are the same as today (`.msh`, `mesh.unv`; with sliding motion the
   fixed and the moving side in their own files).

## 4. Reading the steps from the objects

The Symmetric Mesh item links one object, the **top**. The add-on walks down its dependencies and gives every leaf
(a cell body) the set of transforms that place copies of it in the top's shape:

| Object | Transforms of the leaves below it |
|---|---|
| cell body (any other shape object; the leaf) | identity |
| `Part::Compound` | the union over its `Links` |
| `Part::Mirroring` | its mirror (`Base`, `Normal`) applied after each transform of `Source` |
| Draft polar array | rotation by k × step (k = 0..`NumberPolar`−1, about `Center`, `Axis` = Z) after each transform of `Base` |
| Boolean Fragments | the union over its `Objects` (it only splits; it moves nothing) |

Rules:
- Mirrors must have a normal in the XY plane, and rotations must be about the Z axis (2D).
- Every leaf under one item must end up with the **same** transform set. Otherwise refuse, naming the leaf. (Its copies
  are meshed and joined together, so the set has to be common.)
- Any other object type in the chain: refuse with its name and type.
- Placement matters: work with global shapes. The coverage check in section 5 catches any mistake made here, so a wrong
  transform can never make a wrong mesh silently.

The spike typed the steps by hand (`mirror x y deg`, `rotate x y deg count`); reading them from the objects replaces
that.

## 5. The mesher

Per Symmetric Mesh item:

1. Import the cell bodies, fragment them, and apply the mesh settings that reference them (unchanged code: sizes,
   transfinite, recombine).
2. Sliding: on the cell's arc of the sliding circle set `divisions × cell arc angle / 360°` elements (transfinite,
   uniform). This must be a whole number, and the arc's ends must lie on the grid. The spike used 144 divisions: stator
   cell arc 6, rotor cell arc 9, and both sides had 144 nodes at the same angles.
3. Mesh the cell.
4. Copy the mesh (`copy_mesh` in `experiments/gmsh_symmetry/motor_cell.py`):
   - each copy of each cell entity becomes a discrete entity with transformed nodes,
   - mirrored copies (det < 0) get `gmsh.model.mesh.reverse`,
   - then `removeDuplicateNodes`, `renumberNodes`, `renumberElements`.

   This keeps quads and transfinite structure (checked: 0 inverted elements in all runs).
5. **MAT_ID of a copy = the Material of the piece it lands on.** Take a few element centres of the cell entity, move
   them by the copy's transform, and find the drawn piece (face of a Main/Moving body) containing them. All of them
   must hit the same piece. That piece's Material gives the MAT_ID and name.
6. **Coverage check:** for every piece, the areas of the copies landing on it must add up to its area. Otherwise the
   drawing is not symmetric. Refuse, naming the piece. (`d_full_geometry.py --break`: one coil turned 1° is refused.)

With sliding motion, the fixed side's item(s) and the moving side's item(s) are written to their own files. Nodes on
the sliding circle are not merged across the sides, which is correct.

Why copying and not gmsh's own periodic copy: in 2D, `setPeriodic` on every copied surface also works (`a_periodic_2d.py`,
same result). But it needs the full geometry fragmented and meshed in gmsh, and it does not extend to 3D. Mesh copying
does both, and only the cell's geometry goes to gmsh.

## 6. Changes to the add-on objects

- **Material (assignment):** besides one `Body`, it can reference pieces: body faces, as a sub-element list like
  Excitation's `References`, possibly on several bodies. Known weakness: FreeCAD numbers faces, so changing the array
  count can move `Face12` to another piece. Validate Study lists piece → Material so a shift shows.
  - Pieces are allowed **only on the top objects of Symmetric Mesh items**. The normal 2D/3D meshers keep one MAT_ID
    per body, unchanged.
  - A top object gets its Materials **only** through pieces. A whole-body assignment on a top object is refused.
  - An assignment with pieces gets **one** MAT_ID, keyed by the assignment (in `MatIds` and `IdOwners`), not by a body.
    Whole-body assignments on ordinary bodies keep their per-body key as today.
  - Every piece of a top object has exactly one assignment: a missing one or two on the same piece is refused.
  - With sliding motion, one assignment may not hold pieces of both sides, because the moving side needs IDs of its
    own. Refuse it and ask for two Materials, for example "Air gap stator" and "Air gap rotor".
- **Symmetric Mesh item (new):** links the top object; shows the found cell bodies and steps read-only.
- **Mesh settings** may reference the cell bodies of a Symmetric Mesh item, although those bodies are not in the Main
  or Moving geometry. A mesh setting on a copy (a face of the top object) is refused: copies are not meshed, so it
  would do nothing.
- **Sliding Interface:** in a Study with a Symmetric Mesh it has no Air Region. Radius and Divisions place the circle.
  The fixed and moving sides come from the Main and Moving geometry, not from Air Region cells.
  - v1 supports only a Rotational interface over the full 360°, with the slide marker at 0°, and no `periodic` key.
  - The slide's `SLIDE_MAT_ID` and marker point group are written as today, so the output files look the same.
  - Linear and Axial gap interfaces, and a start angle other than 0°, are refused for now.
- **Plane:** v1 supports only XY-plane 2D Studies. A ZX-plane Study with a Symmetric Mesh is refused.

## 7. Validate Study: new checks

- The chain can be read (section 4), and all leaves share one transform set.
- Coverage (section 5, step 6), and every copy lands in exactly one piece.
- Every piece of a top object has a Material. With symmetric meshing, every body of the Study must be under a Symmetric
  Mesh item (v1: no mix of copied and normally meshed bodies).
- Sliding divisions give every cell's arc a whole number of elements.
- No Air Region in a Study with a Symmetric Mesh.
- No mesh setting on a copy.

## 8. Decided by me (Claude), not by the user; check these

- One Symmetric Mesh item per top object. With sliding motion that means at least one per side.
- The transform-set rules and the refusal of unknown object types in the chain (section 4).
- v1: all bodies of a symmetric Study go through Symmetric Mesh items; no Air Region.
- An assignment with pieces is keyed by the assignment for its MAT_ID.
- Pieces only on the top objects of Symmetric Mesh items, and those objects only through pieces (no whole-body
  assignment on them). Multi-body Materials elsewhere are not in v1.
- An assignment across the fixed and moving side is refused, not split automatically.
- Sliding Interface without an Air Region in symmetric Studies: Rotational, full turn, marker at 0° only.
- XY plane only.

## 9. Left to the builder

- Task panel layout of the Symmetric Mesh item and of picking pieces for a Material.
- How the job JSON carries items, transforms and pieces (the `.brep` per cell body pattern of `jobwriter` fits).
- Tolerances of the landing test and of the coverage check.
- Tests: reuse the spike's motor as a fixture (`build_doc.py` makes it headless); the gui smoke test for the new item.
