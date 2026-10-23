# Transfinite (Structured) Mesh for FreeCAD Studies: Requirements and Design

Date: 2026-10-15
Status: requirements agreed in conversation, waiting for spec review
Branch: `feature/freecad-addon`

## 1. Goal

Let the user mesh chosen bodies of a 2D or 3D Study as a structured grid with
Gmsh Transfinite, and optionally get quads / hexahedra with one global
Recombine switch. Everything else in the model keeps meshing as today.

## 2. Scope

In scope:

- **Transfinite Body**: makes whole bodies structured (2D: their faces; 3D:
  their volume and all its faces), with optional manual corners.
- **Transfinite Edges**: fixed number of elements on chosen edges, Uniform or
  Bump distribution.
- **Recombine**: one global switch for `Mesh.RecombineAll`.
- Both Study dimensions, 2D and 3D.

Not in scope (later steps, if needed):

- Extrude / 2.5D layered meshes.
- Progression and edge direction (needs a direction the user can see).
- Triangle arrangement for structured triangles (`Left`/`Right`/`Alternate`);
  Gmsh's default is used.
- Unstructured hex-dominant meshing (`Mesh.Recombine3DAll`).
- Corners of a volume (`setTransfiniteVolume` corner list). A 3D body must
  have 5 or 6 faces.

## 3. Background

- Gmsh: `setTransfiniteCurve(tag, nNodes, meshType, coef)` with meshType
  `Progression` or `Bump`; `setTransfiniteSurface(tag, cornerTags=[])` needs
  3 or 4 corners (found automatically when the face has exactly 3 or 4 boundary
  points); `setTransfiniteVolume(tag)` needs 5 or 6 faces, all transfinite.
  A transfinite curve's node count overrides size fields on that curve.
- EMSolution supports every element this step can produce (triangles, quads,
  tetrahedra, pyramids, hexahedra).
- Already built: `MeshSize` objects and the Mesh Sizes folder with global mesh
  settings, `mesher.py` (3D), `mesher2d.py` (2D), shared `meshcommon.py`, size
  files imported and merged by one `fragment` call.

## 4. Decisions

1. **Two new object types in the Mesh Sizes folder** (approach A), same pattern
   as `MeshSize`. Rejected: a Mode on `MeshSize` (one object with many
   meanings) and one Structured object per body with an edge table (hard panel,
   shared edges repeated).
2. **Every edge of a structured body must belong to a Transfinite Edges
   object.** No automatic node counts. One object can hold many edges, so this
   is little extra work.
3. **Count is given in elements.** The job writes `elements + 1` nodes for Gmsh.
4. **Only Uniform and Bump.** Both are symmetric, so edge direction does not
   matter.
5. **Bad shape = error and stop.** No silent fallback to an unstructured mesh.
6. **Recombine is global**, a Bool that sets `Mesh.RecombineAll`. The user
   accepts what this means: in 2D unstructured faces become quad-dominant; in
   3D the walls of tetrahedral volumes become quads, so Gmsh adds pyramids
   there.
   Replaced by [2026-10-16-recombine-design.md](2026-10-16-recombine-design.md): per-body Recombine item.
7. **Transfinite Edges are also allowed on unstructured bodies.** They only fix
   the nodes of those edges.
8. **Touching bodies are handled where possible, and the user is told.** Gmsh's
   `fragment` makes touching bodies share geometry. It renumbers everything
   (harmless: the fragment map tracks every input) and can split an edge where
   another body's vertex lies on it. The mesher then:
   - shares the edge's elements between its pieces by length (each piece at
     least 1, the total stays `Elements`); a Bump edge cannot be shared, so a
     split Bump edge is an error;
   - finds the corners of a face that now has more than 4 boundary points: the
     points where the boundary turns (a point on a straight run is not a
     corner). Chosen `Corners` win over this.
   Each of these prints one `NOTE:` line, which FreeCAD's Report view shows as a
   warning. In 3D a split edge nearly always comes with a split face, which no
   tool can mesh as one structured volume, so R5 still stops it.

## 5. Objects

### Transfinite Body (`TransfiniteBody`)

| Property | Type | Meaning |
|---|---|---|
| `References` | `PropertyLinkSubListGlobal` | Whole bodies (empty sub-element only) |
| `Corners` | `PropertyLinkSubListGlobal` | Optional vertices of those bodies, used as face corners |

### Transfinite Edges (`TransfiniteEdges`)

| Property | Type | Meaning |
|---|---|---|
| `References` | `PropertyLinkSubListGlobal` | Edges of any body |
| `Elements` | `PropertyIntegerConstraint` | Elements per edge, min 1, default 10 |
| `Distribution` | `PropertyEnumeration` | `Uniform`, `Bump` |
| `BumpCoefficient` | `PropertyFloat` | Gmsh Bump coef, default 0.5, used only for `Bump` |

### Mesh Sizes folder

| Property | Type | Meaning |
|---|---|---|
| `Recombine` | `PropertyBool` | Sets `Mesh.RecombineAll`; default off |

Replaced by [2026-10-16-recombine-design.md](2026-10-16-recombine-design.md): per-body Recombine item.

Old documents: the folder gets `Recombine` on load if missing (off), so old
Studies mesh as before.

## 6. Rules

Checked in FreeCAD by `jobwriter.check` (before Gmsh starts):

- R1. Every edge of a body in a Transfinite Body is in some Transfinite Edges
  object.
- R2. No edge is in two Transfinite Edges objects; no body is in two Transfinite
  Body objects.
- R3. Every corner vertex belongs to a body of the same Transfinite Body object.
- R8. In 3D with Recombine on, the volume algorithm must be Delaunay. Gmsh's
  Frontal and HXT refuse quads on a volume boundary (checked with Gmsh 4.x).
  Replaced by [2026-10-16-recombine-design.md](2026-10-16-recombine-design.md): per-body Recombine item.

Checked in the mesher (they depend on the shape after `fragment`):

- R4. A face with 3 or 4 boundary points uses them as corners. A face with more
  uses the chosen corners lying on it, or else the points where its boundary
  turns (decision 8); either way there must be exactly 3 or 4. Faces with a
  hole or a closed edge (circle) cannot be structured.
- R5. In 3D, each structured volume has 5 or 6 faces.
- R6. On each structured face, the two opposite sides have the same total
  number of elements. A side is the chain of edges between two corners.
- R7. A transfinite edge or corner file did not merge with the bodies: error,
  as for mesh sizes today. A split Bump edge, a split edge with fewer elements
  than pieces, and one edge (or piece) given two different element counts or
  distributions by two items are also errors.

R6 for 4 corners: opposite sides match. For 3 corners Gmsh collapses the first
corner, so the two sides that meet there must match: the mesher picks a corner
where they do, and stops with an error if no two sides match. Gmsh only warns
(and meshes the face unstructured) when a transfinite face or volume fails, so
as a safety net the mesher also stops with an error when Gmsh logs "cannot be
meshed using the transfinite algorithm". A hole is checked before the corners,
so a face with a hole always gets the "not one loop" error.

Every error is one line naming the object, body (and face when known) and the
reason. Example: `ERROR: structured body Core: face 3 has 6 boundary points
and 0 chosen corners on it; it needs 3 or 4 corners`.

Notes for what the mesher fixed by itself (decision 8), on stderr, for example:
`NOTE: Transfinite Edges Sides: tedge_1_2.brep was split into 2 pieces by a
touching body; elements 2 + 2` and `NOTE: structured body Core: face 1 has 5
boundary points; using the 4 where the boundary turns as corners`.

Mesh Size items on a transfinite edge are allowed and have no effect there.

## 7. Job file

Added to both the 2D and 3D job:

```
"options": { ..., "Mesh.RecombineAll": 1 },   // only when Recombine is on
"transfinite": {                               // only when the Study has transfinite items
  "bodies": [{"name", "mat_id", "corner_files": [...]}],
  "edges":  [{"name", "nodes", "distribution", "coef", "files": [...]}]
}
```

Replaced by [2026-10-16-recombine-design.md](2026-10-16-recombine-design.md): per-body Recombine item.

`nodes` = `Elements + 1`. Edge and corner BREP files are written like mesh
size files (one edge or one vertex each). A missing `"transfinite"` key means
none, so old jobs still work.

## 8. Mesher changes

- Both mesher scripts import the edge and corner files with the size files and
  pass them through the same `fragment` call, keeping the output map.
- New shared function in `meshcommon.py`, called by both scripts after the
  physical groups and size fields, before `generate`:
  1. `setTransfiniteCurve` for each edge entity (`Progression` with coef 1 for
     Uniform, `Bump` with `coef`).
  2. For each structured body: check R4 to R6 for each face, then
     `setTransfiniteSurface(face, cornerTags=...)`; in 3D check R5 and call
     `setTransfiniteVolume`.
- `Mesh.RecombineAll` reaches Gmsh through the existing options loop in
  `meshcommon.run`; no new code there.
  Replaced by [2026-10-16-recombine-design.md](2026-10-16-recombine-design.md): per-body Recombine item.
- The MAT_ID table at the end of the run also prints the structured bodies.

## 9. Add-on changes

- `objects.py`: the two proxy classes, `make_transfinite_body`,
  `make_transfinite_edges`, list helpers, `Recombine` on the folder.
- `taskpanels.py`: two panels in the style of the Mesh Size panel. Body panel:
  pick bodies, optional corner vertices. Edges panel: pick edges, Elements,
  Distribution, BumpCoefficient (shown only for Bump).
- `commands.py`: two commands with icons, on for 2D and 3D.
- `jobwriter.py`: R1 to R3, write edge and corner files, the `transfinite` key
  and `options.recombine`.

## 10. Tests

- `test_mesher2d.py`: structured square, only quads with Recombine and the right
  count; triangles without Recombine; Bump changes node spacing; structured
  square next to an unstructured face; 5-point face with 4 chosen corners and
  with corners found by angle; an edge split by a touching body shares its
  elements and prints a NOTE; errors for R4, R6, R7 (split Bump edge included).
- `test_mesher.py`: structured box gives only hexahedra with Recombine; box next
  to an unstructured body gives pyramids; errors for R4, R5, R6.
- `test_study.py`: job content, R1 to R3 errors, old Study without `Recombine`
  still writes a valid job.
- `gui_smoke.py`: create both objects on a 2D and a 3D Study and Run Mesh.

## 11. Open points

- **Fragment splits faces.** Split edges and extra points are handled
  (decision 8). A split face is not: the user has to cut the structured body in
  FreeCAD so it matches its neighbour. R5 says so.
- **Corners by angle** are exact for straight edges. On curved edges a point
  where two arcs meet smoothly is not a corner; where they meet at an angle it
  is. When that guess is wrong, the user picks `Corners`.
