# Symmetric meshes with gmsh: mesh a piece, copy the rest

Toy motor: 12 slots, 8 poles (see `motor_cell.py` for the dimensions). gcd(12, 8) = 4, so the machine repeats every
90°, and inside that it is mirror symmetric about 45°. The smallest piece to mesh, the **cell**, is 0..45°:
one magnet and one and a half slots. In 3D the stack is also mirrored about z = 0, so the 3D cell is z 0..20 only.

| Script | What it shows | Output |
|---|---|---|
| `b_mesh_copy_2d.py` | **B**: mesh the cell, copy the *mesh* 8 times through the gmsh API | `b_cell_2d.msh`, `b_full_2d.msh` |
| `a_periodic_2d.py` | **A**: copy the *geometry* 8 times, let gmsh copy the mesh (periodic surfaces) | `a_full_2d.msh` |
| `c_mesh_copy_3d.py` | **B** in 3D, with 3 choices of cell (`--mode mirror / rotate / rotate-free`) | `c_cell_3d_*.msh`, `c_full_3d_*.msh` |

Run with `pixi run python experiments/gmsh_symmetry/<script> [--gui]`, or open the `.msh` files in gmsh
(Tools > Visibility shows the physical groups). Every script ends with a check: elements per physical group,
inverted elements, and *non-conforming facets*, which are element edges/faces that only one element uses but that are
not on the outside of the model. These are where two copies failed to share nodes.

## Two ways to copy

**A. Copy the geometry, gmsh copies the mesh.** Build the full geometry from transformed copies of the cell
(`occ.copy` + `occ.affineTransform`), glue the copies with `fragment`, then call
`setPeriodic(2, [copy], [cell surface], transform)` for every surface of every copy. gmsh meshes only the cell
surfaces and copies their mesh onto the copies. Mirror transforms work too, and gmsh fixes the element orientation.

- Works **only in 2D**. In 3D gmsh accepts `setPeriodic(3, ...)` but meshes each volume on its own anyway. I tested this:
  a box and its mirror image get 2944 and 2968 tetrahedra. The volumes are conforming, but they are not copies.
- The copies must come from transforming the cell's geometry. Two circles drawn separately do not match: OCC puts the
  seam point of a full circle at angle 0, and the mirror image of that point is not a vertex of the other circle, so
  `setPeriodic` fails with "No corresponding point".

**B. Mesh the cell, copy the mesh.** Mesh only the cell, then build a new model from discrete entities. Each copy
gets its transformed nodes (with tags shifted so they don't clash) and the same element connectivity. After that:

1. Call `mesh.reverse()` on mirrored copies (det = -1). Otherwise every element is inverted.
2. Call `mesh.removeDuplicateNodes()` to merge the nodes where two copies meet.
3. Call `renumberNodes()` / `renumberElements()`.

This works the same in 2D and 3D, with any element type. It is also the cheapest option: only 1/8 (2D) or 1/16 (3D) of
the model is ever meshed. `copy_mesh()` in `motor_cell.py` is about 40 lines.

## When do the copies share nodes on the cuts?

Merging only works if both sides of every cut carry the same nodes. That depends on how you choose the cell:

- **Cut on a mirror plane:** the cut always matches, because the mirror maps it onto itself.
- **Cut between rotated copies:** the cell's 0° face and its 90° face must be meshed alike. You need
  `setPeriodic(dim-1, [face at 90°], [face at 0°], rotation 90°)` on the cell before meshing. The add-on already does
  this in `meshcommon.apply_periodic`.
- In the mirror+rotate cell here, the 0° face also matches without any constraint, because the combined transform
  (rotate 270° after mirroring at 45°) maps the 0° plane onto itself.

The 3D runs show it:

| `--mode` | cell | copies | non-conforming facets in the full model |
|---|---|---|---|
| `mirror` | 0..45°, z 0..20 | 16 | 0 |
| `rotate` (with setPeriodic) | 0..90°, z 0..20 | 8 | 0 |
| `rotate-free` (without) | 0..90°, z 0..20 | 8 | **5920** |

In 2D, a straight cut line usually gets the same 1D mesh on both ends even without constraints. Don't rely on that:
set the constraint anyway.

## Physical numbering (the part in question)

The cell has physical groups named only by **base name**: `rotor_iron`, `stator_iron`, `air`, `magnet`, `coil`,
`outer`. Each copy of each cell *entity* asks `physical(base, x, y)` which id it gets, where (x, y) is the centre of that
entity *after* the copy's transform. There are two kinds of group:

- **Shared**: iron, air, outer boundary. Every copy gets the same id, so the full model has one group (id 1, 2, 3, 10).
- **Indexed**: magnets, coils. The id comes from *where the copy landed*, not from which copy it is:
  pole = angle // 45° gives `magnet_p0_N` ... `magnet_p7_S` (101..108), and slot = round((angle - 15°) / 30°) gives
  `coil_s00_U` ... `coil_s11_W` (201..212).

Why position rather than copy index:

- It gives the same answer for rotated and mirrored copies. You never have to work out "mirror of rotation 3 is pole 7".
- A slot cut in half by the mirror line ends up as one group: both halves land at the same angle. `coil_s01` has 56
  elements, which is 2 × 28 half-slot elements.
- The rule has to look at each **entity** separately, not each physical group. The cell's `coil` group holds a whole
  slot and a half slot, and their common centroid lands between two slots. That was my first bug.
- Approaches A and B use the same rule and give exactly the same groups and counts (8900 nodes in 2D, both ways).

A real machine just needs a different `physical()`: a winding table (slot → phase and sign, double layer → two regions
per slot), magnet polarity, and the add-on's `mat_id`s. The mesh copying itself does not depend on it.

**Physics note.** A copied mesh is only a mesh. The solver sees the full machine, so nothing is assumed about the
fields: a z-mirrored coil still carries current in the same direction because it has the same id. This is different
from solving only the cell with (anti-)periodic or symmetry boundary conditions. There, the field has to be symmetric
too, and the "mirror" in a magnet or coil changes its sign.

## The add-on's case: full geometry, numbering from the user's materials (`d_full_geometry.py`)

In the add-on the user draws the whole machine, one body per FreeCAD object, each with a Material (MAT_ID), so there
is no "base name" to number from. The script works from that situation: magnets have two materials (N, S) and the
coils have three (U, V, W). It never uses a pole or slot rule:

1. Fragment the bodies **together with the symmetry cuts**. These are half-lines every 45° in 2D, or half-planes every
   45° plus z = 0 in 3D. The full model is now split into sectors.
2. **Match:** for each copy transform T and each cell entity e, find the full-model entity f that T(e) lands on (same
   centre of mass and size, like `apply_periodic` does). If anything is left over or not found, the geometry is not
   symmetric and the script stops (`--break` turns one coil 1° to show this).
3. **2D:** call `setPeriodic(2, [f], [e], T)` and mesh the full model as now. The physical groups are the bodies'
   MAT_IDs, unchanged. gmsh meshes only the cell and copies it.
4. **3D:** remove everything except the cell, mesh it, and copy the mesh. Copy c of e gets `MAT_ID(match[c, e])`.

The id never comes from the cell. The script prints that the cell's magnet is `magnet_N` in some copies and
`magnet_S` in others, and its coil `coil_U` or `coil_W`. Results: 2D 8912 nodes; 3D: only 2682 nodes are meshed,
36408 in the full model. Both have 0 inverted and 0 non-conforming elements.

## Transfinite and recombined bodies (`e_transfinite.py`)

Copying the mesh does not care how the cell was meshed. In `e_transfinite.py` the magnets and coils of the cell are
transfinite and recombined, and everything else is free. The full model then holds:

| | cell | full model (copies) | inverted elements | non-conforming facets |
|---|---|---|---|---|
| 2D | 1484 triangles, 140 quads | 11872 triangles, 1120 quads (8 copies) | 0 | 0 |
| 3D | 10037 tets, 700 hexes, 420 pyramids | 160592 tets, 11200 hexes, 6720 pyramids (16 copies) | 0 | 0 |

`mesh.reverse()` handles quads, hexes and pyramids of the mirrored copies as well as triangles and tets. So every mesh
setting the add-on has (sizes, Transfinite Edges, structured bodies, recombine) can stay exactly as it is, applied to
the cell.

## Open points for the add-on

- The cell's geometry: does FreeCAD give the cell directly (the user models a sector), or the full machine with the
  symmetry declared, so that we cut the cell out? `apply_periodic` already finds the matching faces on the cut planes.
- Sliding air gap: the rotor and stator copies must use the same angular step. gcd(slots, poles) already ensures this.
- Non-straight 3D parts (end windings) still have the rotational symmetry but not always the z mirror.
- EMSolution's own periodic / anti-periodic boundary conditions may make a full copied mesh unnecessary for many runs.
  Copying is for when the full model is needed.
