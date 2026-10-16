# Recombine per Body for FreeCAD Studies: Requirements and Design

Date: 2026-10-16
Status: agreed in conversation, waiting for review
Branch: `feature/freecad-addon`
Replaces: the global Recombine switch of
[2026-10-15-transfinite-mesh-design.md](2026-10-15-transfinite-mesh-design.md)
(decision 6, rule R8, the `Recombine` row in section 5, `Mesh.RecombineAll` in
sections 7 and 8).

## 1. Goal

Let the user choose **which bodies** get quads (2D) or hexahedra / quad faces
(3D), and **which Gmsh recombination algorithm** is used. Same idea in 2D and
3D, one code path in the mesher, and no Gmsh crash: faces Gmsh cannot
recombine stay triangles with a note, or (when a structured body needs them)
give a clear error.

Priorities, in order (from the user): long-term maintainability and clean
design; then the basic and important recombine features; fancy features later.

## 2. Why the global switch goes

The global Bool set `Mesh.RecombineAll`, which puts quads on **every** surface.

- In 3D a quad face between two tetrahedral bodies needs pyramids on both
  sides. Gmsh stops with `Pyramid top vertex already classified on volume 2
  (!= 3) - non-manifold quad boundaries not supported yet`. This happened on a
  real model (structured Core, unstructured Air and Coil touching each other).
- The temporary fix (3D: quads only on Transfinite Body faces, `RecombineAll`
  turned off in `meshcommon.run`) works, but gives one checkbox two meanings,
  one for 2D and one for 3D. That hidden rule is what this design removes.

The global switch exists only in uncommitted work on this branch, so no
released document depends on it.

## 3. Background (checked with the Gmsh in `pixi.lock`)

- `gmsh.model.mesh.setRecombine(2, face)` recombines one surface. This is the
  only per-entity recombine Gmsh supports well.
- 2D: quads next to triangles are fine; the shared edges keep the same nodes.
- 3D:
  - A transfinite volume whose faces are all recombined gives hexahedra.
  - A recombined face of an unstructured (tetrahedral) volume gets one layer of
    pyramids on that side. Works only when **at most one** side of the face is
    tetrahedral.
  - Frontal and HXT volume algorithms refuse quad faces on a tetrahedral
    volume; Delaunay works (rule R8 of the transfinite spec).
- `Mesh.RecombinationAlgorithm` is **global** in Gmsh (no per-surface value):

  | Value | Name | Result (tested on a 2D square, mesh size 0.2) |
  |---|---|---|
  | 1 | Blossom (Gmsh default) | all quads (37); can leave triangles when a face has an odd number of them (Gmsh warns) |
  | 0 | Simple | quad-dominant: 28 quads + 5 triangles |
  | 3 | Blossom full-quad | all quads, smaller (53) |
  | 2 | Simple full-quad | all quads, smaller (53) |

  Full-quad prints `Full-quad recombination only compatible with transfinite
  meshes if those are performed first`. In the test (structured face, full-quad
  face, triangle face side by side) the structured face kept its 16 quads and
  all shared edges kept matching nodes. On structured faces the algorithm
  makes no difference.
- Tried on the real model and rejected for now: `Mesh.Recombine3DAll`
  (Air and Coil stayed 100% tetrahedra) and `Mesh.SubdivisionAlgorithm = 2`
  (did not finish in 5 minutes).

## 4. Scope

In scope:

- **Recombine** item: whole bodies that get recombined. 2D and 3D.
- **Recombination algorithm**: one global setting in the Mesh Sizes folder.
- 3D face rules that replace the pyramid crash with triangles + NOTE, or a
  clear error when a structured body needs the face.
- Removing the global `Recombine` switch and the temporary fix.

Not in scope (later, if needed):

- Recombine on single faces.
- Recombination angle (`setRecombine(2, tag, angle)`), Gmsh default kept.
- 3D hex-dominant (`Mesh.Recombine3DAll`), all-hex subdivision, extrusion.

## 5. Decisions

1. **A new item type `Recombine` in the Mesh Sizes folder**, same pattern as
   Mesh Size and Transfinite Body. It references whole bodies only.
   Rejected: the global switch (two meanings, crash), a switch on Transfinite
   Body (no 2D quads without a structured body; two ways to say "recombine").
2. **The mesher calls `setRecombine(2, face)` on every face of the chosen
   bodies**, in 2D (the body's faces) and 3D (the volume's boundary faces).
   `Mesh.RecombineAll` is never written. In 3D the rules in section 7 may leave
   some of those faces as triangles.
3. **In 3D any body may be chosen**, structured or not. A chosen structured
   body gives hexahedra; a chosen unstructured body gives pyramids at its
   surface, where the rules allow it.
3a. **A face Gmsh cannot recombine is left as triangles, with a NOTE**, when
   no hexahedral body needs it (user's choice). Example: a chosen Air touching
   an unstructured Coil keeps triangles on that shared face and quads on its
   other faces. Same pattern as the `NOTE:` lines of the transfinite feature.
   Only when a chosen structured body needs the face is it an error.
4. **The 3D rules are checked in the mesher, not in FreeCAD**: only Gmsh knows
   which faces are really shared after `fragment`. This includes R8 (Delaunay),
   which becomes exact: it applies only when a recombined face touches a
   tetrahedral volume.
5. **The recombination algorithm is global** (Gmsh has no per-surface value),
   stored on the Mesh Sizes folder, default Blossom (Gmsh's default).
6. **The same body in two Recombine items is allowed.** There is no setting
   that could conflict.
7. **No migration.** On load, a leftover `Recombine` property on the Mesh
   Sizes folder is removed. Documents saved with it (only the author's test
   files) mesh without recombine until a Recombine item is added.

## 6. Objects

### Recombine (`Recombine`)

| Property | Type | Meaning |
|---|---|---|
| `References` | `PropertyLinkSubListGlobal` | Whole bodies (empty sub-element only) |

Label default `Recombine`. Mesh Sizes panel row: size column `recombine`.

### Mesh Sizes folder

| Property | Type | Meaning |
|---|---|---|
| `RecombinationAlgorithm` | `PropertyEnumeration` | `Blossom`, `Simple`, `Blossom full-quad`, `Simple full-quad` (first = default) |
| ~~`Recombine`~~ | | removed (decision 7) |

`objects.py` gets `RECOMBINATION_ALGORITHMS = {"Blossom": 1, "Simple": 0,
"Blossom full-quad": 3, "Simple full-quad": 2}`, like `ALGORITHMS_2D`.
`onDocumentRestored` adds `RecombinationAlgorithm` when missing (Blossom) and
removes `Recombine` when present.

## 7. Rules

Checked in the mesher, 3D only, after `fragment` and the transfinite setup,
before `generate`. Each volume is one of:

- **hex**: in a Transfinite Body and in a Recombine item;
- **structured-tet**: in a Transfinite Body, not in a Recombine item;
- **tet**: not in a Transfinite Body.

For every candidate face (a boundary face of a chosen body), look at the
volumes on its sides (`getAdjacencies(2, face)`; a face on the outside has one
side). A face **can** be recombined when no side is structured-tet and at most
one side is tet (Gmsh puts pyramids on that one side).

- RC1. A candidate face that **cannot** be recombined and has **no hex side**
  stays triangles. One `NOTE:` line per pair of bodies (not per face), for
  example:
  `NOTE: recombine: faces between Air and Coil stay triangles (a quad face there would need pyramids on both sides)`.
  If every face of a chosen body stays triangles, the NOTE says so:
  `NOTE: recombine: Air has no face that can be recombined; it stays all triangles`.
- RC2. A candidate face that **cannot** be recombined but **has a hex side** is
  an error: the hex body needs all its faces as quads. This only happens when
  the other side is structured-tet. Error example:
  `ERROR: recombine: Core is structured and touches recombined structured body Yoke; add Core to a Recombine item too`.
- RC3 (was R8). If any face that **is** recombined touches a tet volume, the
  volume algorithm (`Mesh.Algorithm3D` in the job options) must be Delaunay (1).
- RC4. With a full-quad recombination algorithm (2 or 3), Gmsh halves the 1D mesh on the edges of
  every recombined face that is not a transfinite face, so a Transfinite Edges item on such an edge
  needs an even number of elements. Error example:
  `ERROR: recombine: full-quad needs an even number of elements on Transfinite Edges tedge_1 next to recombined body Air; use an even number or the Blossom or Simple algorithm`.

Summary of a face's sides (outside counts as nothing):

| Sides | Result |
|---|---|
| hex only, hex + hex, hex + tet, tet only | quads |
| tet + tet, tet + structured-tet (no hex side) | triangles + NOTE (RC1) |
| hex + structured-tet | error (RC2) |

Wording of NOTE and ERROR lines is the builder's call, but they name the
bodies. They do not name the Recombine item: the job only carries MAT_IDs (section 8).

2D has no extra rules.

`jobwriter.check` (FreeCAD side) only does what it does for other items:
references must be whole bodies of the Study (bodies outside the included set
are skipped, as for the other items). The old R8 check there is removed.

## 8. Job file

Both 2D and 3D jobs:

```
"options": { ..., "Mesh.RecombinationAlgorithm": 1 },   // always written
"recombine": [1, 3]                                      // MAT_IDs; only when the Study has Recombine items
```

A missing `"recombine"` key means none, so old jobs still work.
`Mesh.RecombineAll` is no longer written.

## 9. Mesher changes

- New shared function in `meshcommon.py`, e.g. `apply_recombine(job, body_tags,
  dim)`, called by both scripts after `apply_transfinite`:
  - collect the candidate faces of the chosen bodies (2D: the body's faces; 3D:
    boundary faces of its volumes);
  - in 3D, sort each face by the table in section 7: drop RC1 faces (print the
    NOTEs through the existing `_note`), raise `JobError` for RC2, then check
    RC3 on the faces that remain;
  - call `setRecombine(2, face)` once per remaining face.
  It needs to know which bodies are structured: from
  `job["transfinite"]["bodies"]` (MAT_IDs).
- Remove the temporary fix: the `setRecombine` call inside
  `apply_transfinite` and the `Mesh.RecombineAll = 0` line in `run`.
- The MAT_ID table printed at the end also marks recombined bodies
  (`Recombined   Core`), like `Structured`.

## 10. Add-on changes

- `objects.py`: `Recombine` proxy, `make_recombine(study, bodies)`,
  `recombine_items(study)`, `RECOMBINATION_ALGORITHMS`, folder property and
  restore code; `is_item`, `item_refs`, `_size_text` know the new item.
- `taskpanels.py`: `ItemPanel` handles `Recombine` (pick whole bodies, label
  "Bodies"). `MeshSettings`: the checkbox becomes a "Recombination algorithm"
  combo next to the surface/volume algorithm combos, tooltip says it applies to
  bodies in Recombine items.
- `commands.py`: `EMS_Recombine` command ("Recombine", tooltip "Mesh the
  selected bodies with quads (2D) or quad faces and hexahedra (3D)"), new icon
  `icons/recombine.svg`, on for 2D and 3D, in the toolbar and menu next to the
  transfinite commands.
- `jobwriter.py`: write `recombine` and the algorithm option; drop the old R8
  check and the `Recombine` → `RecombineAll` line in `mesh_options`.

## 11. Tests

- `test_mesher2d.py`: Recombine item on one of two touching faces gives quads
  there and triangles in the other; each algorithm value reaches Gmsh (Simple
  leaves triangles, Blossom full-quad gives only quads); structured face with
  Recombine gives only quads; no `recombine` key = triangles everywhere. Update
  the existing tests that use `Mesh.RecombineAll`.
- `test_mesher.py`: structured box with Recombine gives only hexahedra;
  structured + unstructured box both chosen gives hexahedra + pyramids;
  the Core / Air / Coil case (Core structured, Air and Coil unstructured and
  touching) meshes when only Core is chosen, and also when Core and Air are
  chosen: the Air–Coil faces stay triangles, Coil is all tetrahedra, one NOTE
  names Air and Coil; a chosen small box fully inside an unstructured big box
  (all its faces shared with tets) stays all tetrahedra and prints the "no face
  can be recombined" NOTE; RC2 error for a chosen structured box next to a structured
  box that is not chosen; RC3 error with Frontal. The test added for the
  temporary fix is kept, with its job changed to the new key.
- `test_study.py`: job content (`recombine` list, algorithm option, no
  `RecombineAll`); a document with the old `Recombine` property loads, loses it
  and writes a valid job; Recombine item on a body outside the Study is skipped.
- `gui_smoke.py`: replace the Recombine checkbox steps with creating a Recombine
  item and changing the algorithm, on a 2D and a 3D Study.

## 12. Left to the builder

- Exact NOTE and ERROR wording (must name the bodies).
- Icon design (same style as `transfinitebody.svg`).
- Update the transfinite spec and plan where they describe the global switch
  (point them here).
