# 2D Mesh Generation for FreeCAD Studies: Design

Date: 2026-10-15
Status: design agreed in conversation, waiting for spec review
Branch: `feature/freecad-addon`

## 1. Goal

Run Mesh on a 2D Study writes `pre_geom2D.msh` with Gmsh, where EMSolution
reads it. Today a 2D Study can be created and its geometry checked, but Run
Mesh and the assignment panels are switched off for it.

Scope is meshing only: bodies with their `MAT_ID`, and mesh sizes.
Excitations are not part of this step. They will be replaced later by complete
field sources based on the EMSolution docs, so 2D gets no excitation support
now.

## 2. Background

Facts from EMSolutionDocs (`files/handbook/mesh_files.rst`,
`additional_input/1_2D_to_3D.rst`, `inputControl/12_Geometry.rst`):

- A 2D mesh holds nodes plus planar triangles and quads (carry `MAT_ID`),
  two-node line elements (`SMAT_ID`) and point elements (slide interface).
  This step writes only the triangles.
- The plane is XY for planar analysis (`GEOMETRY` = 1) and ZX, y = 0, for
  axisymmetric analysis (`GEOMETRY` = 2, 3). `GEOMETRY` = 4 expands XY in z or
  ZX in theta. The input file chooses the use; the mesh does not.
- Already built: `Dimension` on the Study, 2D face checks in
  `geometry.collect`, the file name `pre_geom2D.msh` in `jobwriter.mesh_file`,
  and the folder layout from the simulation folder spec.

## 3. Decisions

1. **A separate `mesher2d.py`.** Structured meshes (a later step) differ a lot
   between 2D and 3D, so 2D gets its own Gmsh script. `mesher.py` is not
   changed in behaviour.
2. **Small shared module `meshcommon.py`.** Holds what both scripts do the
   same: read the job, apply user options, write `.msh` / `.unv`, replace the
   target file, print the one-line `ERROR:`. No copied code. `mesher.py` moves
   its own copies of these into it.
3. **The job file says `"dimension"`.** The runner starts `mesher.py` for `"3D"`
   and `mesher2d.py` for `"2D"`. A missing key means `"3D"`, so old jobs work.
4. **Plane: XY or ZX, found from the geometry.** All faces must lie in z = 0 or
   all in y = 0 (tolerance 1e-7 as today). Anything else is an error that names
   the object. No new Study setting.
5. **Bodies are faces.** A body is one or more planar faces, one `MAT_ID` for
   all of them, as in 3D where a body is one material.
6. **Mesh settings reused.** Surface algorithm, size factor, min/max size,
   smoothing and the Mesh Sizes folder apply. The volume algorithm is ignored.
7. **Not in this step:** excitations, sliding motion, point elements, structured
   meshes.

## 4. Job file (2D)

```
{
  "dimension": "2D",
  "model_name", "msh_version", "mesh_file", "options": same as 3D,
  "bodies": [{mat_id, name, size, file}],
  "sizes":  [{name, size, files: [...]}]
}
```

A body's BREP file holds its face, or a compound of its faces. A size file holds a
face, an edge or a vertex. The 3D key `volumes` is not reused, so a 2D job
cannot be mistaken for a 3D one.

## 5. `mesher2d.py` steps

1. Read the job. Start Gmsh with terminal output on.
2. Import each body file (2D entities) and each size file (0D, 1D or 2D).
3. Fragment all together in one call so touching bodies share edges.
4. Check bodies do not overlap. A size entity that did not merge with a body
   is an error naming it.
5. Physical groups: body faces get `MAT_ID`, named after the body.
6. Size fields: constant fields by size and one `Min` field as in 3D, with
   `SurfacesList`, `CurvesList` and `PointsList`.
7. Apply the user options, `Mesh.ElementOrder` 1, `generate(2)`.
8. Write `.msh` and `mesh.unv` to the scratch folder, then replace
   `pre_geom2D.msh`. Print the MAT_ID table.

## 6. Add-on changes

- `geometry.collect`: for 2D, require the one plane to be XY or ZX.
- `geometry.export_unavailable`: stop blocking 2D. Sliding motion still blocks.
- `jobwriter.check` / `write_job`: build the 2D job (section 4). The 3D path
  is untouched. A 2D Study ignores any excitation objects.
- `runner.py`: choose the script from `dimension`.
- `commands.py`, `taskpanels.py`: turn on Run Mesh and the Material and Mesh
  Size panels for 2D. The Excitation command stays off for 2D. Remove the
  "planned for a later phase" messages that Run Mesh now makes untrue.
- Mesh size selection in 2D accepts faces, edges and vertices of a body.

## 7. Errors

One clear line each, as in 3D: not in an allowed plane, bodies overlap, size
entity did not merge, two group names equal after cleaning, target file
read-only.

## 8. Tests

- `tests/freecad_addon/test_mesher2d.py`, same style as `test_mesher.py`:
  one square, two touching squares (shared edge), mesh sizes on a face / edge /
  point, overlap error, size not merged error, ZX plane, the `.msh` has the
  expected physical groups and only triangles.
- `test_study.py`: 2D check and job content, plane error, 2D no longer blocked,
  sliding motion still blocked.
- `gui_smoke.py`: Run Mesh on a 2D Study writes `pre_geom2D.msh`.

## 9. Open points for review

- **ZX plane.** Gmsh keeps y = 0 coordinates in the file. I assume EMSolution
  accepts that without extra conversion.
- **Not verified with EMSolution.** I have not run a generated 2D mesh through
  the solver. That is the first check after implementation.

## 10. Not in this step

Excitations and field sources, sliding motion (`rotor_mesh2D` with point
elements), structured meshes, writing the input file or `2D_to_3D` file.
