# SPIKE: symmetric mesh from a FreeCAD drawing (throwaway)

```
pixi run -e addon python experiments/symmetric_spike/build_doc.py      # -> motor2d.FCStd
pixi run -e addon python experiments/symmetric_spike/mesh_doc.py --gui # -> stator.msh, rotor.msh, opens gmsh
pixi run -e addon freecad experiments/symmetric_spike/motor2d.FCStd    # look at the tree
```

**What the user does** (`build_doc.py` does it in code):

1. Draws two cells. The stator cell (0..15°) is half a tooth plus half a slot. The rotor cell (0..22.5°) is half a pole.
2. Makes the full geometry: cell compound → Part Mirror → compound → Draft Polar Array → Boolean Fragments → Explode.
3. Gives every piece a material. Here that is the string property `Material`. Many bodies share one, for example both
   halves of a coil, or all 24 stator iron pieces.
4. Adds `SymMesh_Stator` / `SymMesh_Rotor`. Each has `Cell` (the cell bodies) and `Steps`
   (`mirror x y deg`, `rotate x y deg count`, applied in order).

**What Run Mesh does** (`mesh_doc.py`):

1. Meshes only the cell bodies. The mesh settings are on the cell: sizes, and the magnet is transfinite and recombined.
2. Copies the mesh by the steps.
3. Gives every copied piece the material of the drawn body it lands in.
4. Checks that the copies cover every drawn body exactly.

## Findings

- **Explode has to be done three times** (array → copies → cell/mirror → pieces). The result is 120 objects in the tree
  and 3 levels of `GrExplode` groups. It works, but it is clumsy for a user.
- **Materials come from the drawing, not from the cell.** One magnet cell became MagnetN and MagnetS, and one coil cell
  became Coil01..Coil12. Each pair of half coils joined into one material.
- **Stator and rotor have different cells** (15° and 22.5°), so there are two Symmetric Mesh items. They go to separate
  files, like the add-on's fixed and moving sides. The nodes on the sliding circle (r = 35) are not shared, which is
  correct for a sliding interface.
- **Sliding divisions have to be split per cell.** The cell's arc of the sliding circle gets
  `divisions × cell angle / 360°` elements, and that must be a whole number for **every** side's cell. Here it is
  144 = a multiple of lcm(24, 16) = 48, so the stator cell arc gets 6 elements and the rotor cell arc gets 9. Both
  sides then have 144 nodes on the same 2.5° grid. Without this the two sides do not match. In the add-on, Validate
  Study can check that the number divides.
- **The air is drawn in each cell** (the stator and rotor halves of the air gap), so no Air Region is needed.
- The check found 0 inverted and 0 non-conforming elements, and all 120 bodies were covered exactly. Only 166 + 275
  nodes were meshed for the whole machine (3648 + 4088 nodes).
