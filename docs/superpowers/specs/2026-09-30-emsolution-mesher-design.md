# EMSolution Mesher for FreeCAD: Design (version 1)

Date: 2026-09-30
Status: draft, waiting for review

## 1. Goal

A FreeCAD addon that prepares 3D meshes for the EMSolution electromagnetic
solver. The user draws the geometry in FreeCAD, assigns materials, marks
excitation surfaces and sets mesh sizes in a model tree, then clicks one
button. The result is a Gmsh `.msh` file in which every body and every
excitation surface is a named group with a stable ID number.

## 2. Scope

**In version 1**

- 3D bodies only, meshed with first-order tetrahedra.
- Tree with Materials, Excitations and Mesh Sizes. Items can be added,
  edited, renamed and deleted.
- One mesh size per Mesh Size item, applied to its bodies, faces, edges and
  vertices (a Gmsh `Constant` field), plus a default size for bodies
  without one.
- Fixed ID numbers that survive re-meshing, editable by the user.
- Gmsh runs in a separate background process, so FreeCAD cannot crash or
  freeze because of it.
- The finished mesh is shown in FreeCAD.
- Windows, with FreeCAD 1.1 and its bundled Python and Gmsh (Gmsh 4.15.2
  was confirmed to work in `bin\python.exe` on 2026-09-30).

**Not in version 1** (planned later, see section 12)

- 2D geometry and 2D meshes
- Structured (transfinite/hex) meshes
- Writing EMSolution's input file (material values, excitation values)
- Boundary layers, second-order elements, other element types
- Linux and macOS

## 3. User workflow

1. Draw bodies in FreeCAD (PartDesign Bodies or any object whose shape is
   exactly one solid; bodies may sit inside an App::Part).
2. Click **New Study**.
3. Select bodies and click **Material**, then give the material a name
   (for example "Copper").
4. Select faces and click **Excitation**, then give it a name (for example
   "Terminal_In").
5. Optionally, select bodies, faces, edges or vertices and click
   **Mesh Size**, then enter a size.
6. Click **Run Mesh**.
7. Hand the `.msh` file to EMSolution.

## 4. Repository and installation

The addon has its own repository at `C:\Users\eskandarih\EMSolution-FreeCAD`.
A directory link at `%APPDATA%\FreeCAD\v1-1\Mod\EMSolution` points to it.

```
EMSolution-FreeCAD/
├── package.xml            addon metadata
├── InitGui.py             registers the workbench
├── emsolution/
│   ├── objects.py         Study, Material, Excitation, MeshSize, ID table
│   ├── commands.py        toolbar buttons
│   ├── taskpanels.py      edit dialogs
│   ├── jobwriter.py       tree → job file + geometry files
│   ├── runner.py          starts the mesher, shows progress, loads result
│   └── mesher.py          job file → .msh  (no FreeCAD imports)
├── icons/
└── tests/
    ├── test_mesher.py     runs with plain Python + gmsh
    └── test_study.py      runs in FreeCADCmd
```

Each file has one job. `mesher.py` must never import FreeCAD, so it can be
run and tested alone.

## 5. Tree objects

```
EMSolution Study
├── Materials
├── Excitations
├── Mesh Sizes
└── Mesh Result      (created by Run Mesh)
```

**Study** (group object)

| Property | Type | Default | Meaning |
|---|---|---|---|
| OutputFolder | path | empty | Empty = folder `<document name>_mesh` next to the `.FCStd` |
| DefaultMeshSize | length | 5 mm | Size for bodies without a Mesh Size item |
| MshVersion | choice | 4.1 | `4.1` or `2.2`, ASCII |
| VolumeIds | map | empty | body internal Name → volume ID |
| SurfaceIds | map | empty | `<excitation Name>|<body Name>` → surface ID |
| NextVolumeId | integer | 1 | next volume ID to hand out |
| NextSurfaceId | integer | 1001 | next surface ID to hand out |

The Materials, Excitations and Mesh Sizes folders are plain groups created
together with the Study.

**Material**: the user-visible Label is the material name. Property
`References` is a list of bodies.

**Excitation**: the Label is the excitation name. Property `References` is a
list of (body, `FaceN`) pairs. Selected faces are resolved to the body that
owns them.

**Mesh Size**: property `Size` (length) and `References`, a list of
(body, sub-element) pairs: an empty sub-element means the whole body,
otherwise `FaceN`, `EdgeN` or `VertexN`. Files from before this change stored
a plain list of bodies; it is converted on load.

**Mesh Result**: a FEM mesh object used for display only. It is replaced on
every successful run.

Double-clicking any item opens its edit dialog. Double-clicking the Study
opens the ID table (section 6).

## 6. IDs and names

**Names** follow the pattern `<item Label>_<body Label>`, for example
`Copper_Body` or `Terminal_In_Body001`. Every character outside `A–Z a–z 0–9 _ -`
becomes `_`.

**Volume IDs**

- One ID per body. The ID belongs to the body, not to its material:
  changing a body from Copper to Iron keeps the ID and changes only the
  name.
- Keyed by the body's internal Name, so renaming its Label does not change
  the ID.
- A body without an ID gets `NextVolumeId`, which then increases by 1. IDs
  are assigned in tree order (material order, then body order within
  each material) during Run Mesh.

**Surface IDs**

- One ID per (excitation, body) pair. All faces an excitation selects on
  one body go into one group. For example, Terminal_In with Body.Face6 and
  Body.Face7 becomes the single group `Terminal_In_Body`.
- Handed out from `NextSurfaceId` (starting at 1001) in the same way.

**Rules**

- Deleted IDs are never reused, because the counters only increase.
- Entries for bodies or excitations that no longer exist are removed from
  the table during Run Mesh. Their numbers stay retired.
- The ID table dialog lists body/excitation, name and ID, and allows
  editing IDs. It refuses an ID that is already used anywhere in the table
  (volume or surface). After an edit, the counters are raised above the
  highest ID in use.

## 7. Checks before meshing

Run Mesh stops with a message naming the body or face if:

1. there is no Study, or it has no materials
2. a referenced object no longer exists
3. a referenced body is not exactly one solid
4. a body has no material, or more than one (only bodies referenced by
   some tree item are considered)
5. an excitation face belongs to a body with no material
6. a Mesh Size item has a size ≤ 0, or the default size is ≤ 0
7. the document is unsaved and OutputFolder is empty (the user is asked to
   save or pick a folder)

A Mesh Size face, edge or vertex that the body does not have is an error,
like a missing excitation face.

If a body is in several Mesh Size items, the smallest size wins. This is
not an error. A face, edge or vertex size only changes the body size near
that entity, and only when it is smaller than the body size.

## 8. Job file and geometry export

The job writer creates in the output folder:

```
<output folder>/
├── job.json
└── geometry/
    ├── vol_1.brep        one per body, named by volume ID
    ├── surf_1001_1.brep  one per selected face: surface ID, face counter
    └── size_1_1.brep     one per Mesh Size face/edge/vertex: entry, counter
```

Shapes are exported in global coordinates, including App::Part
placement. It uses the same method as FreeCAD FEM:
`getPropertyOfGeometry()`, `transformed(identity)`, then setting
`getGlobalPlacement()`. Lengths are in millimetres (FreeCAD's internal
unit).

`job.json`:

```json
{
  "model_name": "Study",
  "msh_version": 4.1,
  "volumes": [
    {"id": 1, "name": "Copper_Body", "file": "geometry/vol_1.brep", "size": 1.0}
  ],
  "surfaces": [
    {"id": 1001, "name": "Terminal_In_Body", "volume_id": 1,
     "files": ["geometry/surf_1001_1.brep"]}
  ],
  "sizes": [
    {"name": "MeshSize001", "size": 0.5, "files": ["geometry/size_1_1.brep"]}
  ]
}
```

Each volume already carries its effective size (Mesh Size item or default),
so the mesher needs no size rules. `sizes` has one entry per (Mesh Size
item, body) pair with faces, edges or vertices. Paths are relative to `job.json`.
`model_name` is the Study Label passed through the name cleanup.

## 9. Mesher (`mesher.py`)

Usage: `python.exe mesher.py <job.json>`

1. Read `job.json`. Start Gmsh with terminal output on.
2. Import each volume file. Each must give exactly one 3D entity.
3. Import each surface file. Each must give exactly one 2D entity. Import
   each size file. Each must give exactly one 0D, 1D or 2D entity.
4. Fragment all imported entities together in one call (first entity as
   the object, the rest as tools) with both removed. This glues touching
   bodies so they share faces and nodes.
5. Use the returned map (one entry per input, in input order) to find:
   - the final volume(s) of each body
   - the final surface(s) of each excitation file
6. **Overlap check:** a final volume that appears under two bodies means
   the bodies overlap → error naming both.
7. **Merge check:** every final surface of an excitation must be on the
   boundary of its body's final volumes. If not, the face did not merge
   (usually a rounding difference) → error naming the excitation and body.
8. Create physical groups with the IDs and names from the job:
   dimension 3 for volumes, dimension 2 for excitation surfaces.
9. Mesh sizes: group volumes and size entities by size. A size entity with
   nothing above it (no volume, face or edge it bounds) did not merge →
   error naming the Mesh Size item. One `Constant` field per distinct size
   (`VIn` = size, `VolumesList`, `SurfacesList`, `CurvesList`, `PointsList`,
   `IncludeBoundary` = 1). A `Min` field
   over them is the background field. Turn off size from points,
   curvature and boundary extension, so only the fields decide.
10. `Mesh.Algorithm3D` = 1 (Delaunay), `Mesh.ElementOrder` = 1,
    `Mesh.Optimize` = 1. Generate the 3D mesh.
11. Write `<model_name>.msh` (the requested MSH version, ASCII) and
    `<model_name>.unv` (for display in FreeCAD). Because physical groups
    exist, only elements in them are saved: tetrahedra of all bodies and
    triangles of the excitation surfaces.
12. Print the ID → name list. Exit code 0.

**On any error:** print `ERROR: <message>` as the last line on stderr, call
`gmsh.finalize()`, and exit with code 1.

## 10. Running from FreeCAD (`runner.py`)

1. Run the checks in section 7. Update the ID table. Write the job file and
   geometry files.
2. Start `<FreeCAD home>\bin\python.exe mesher.py job.json` with QProcess,
   so FreeCAD stays responsive.
3. Stream the mesher's output to the Report view. A small dialog shows
   "Meshing…" with a Cancel button that kills the process.
4. **Success:** load the `.unv` into the Mesh Result object (created or
   replaced), recompute, and print the output paths.
5. **Failure or cancel:** show the `ERROR:` line (or "cancelled") in a
   message box. The document is unchanged except for the ID table
   update.

The ID table is saved in the document, so IDs given out in a failed run
stay assigned to their bodies.

## 11. Testing

**Mesher tests** (`tests/test_mesher.py`, standard `unittest`, run with
FreeCAD's `python.exe`). Test geometry is built with Gmsh's own box
function and saved as BREP files, so FreeCAD is not needed:

- two touching boxes → groups 1 and 2 with the correct names; nodes on the
  shared face are shared (conformal)
- box plus one of its faces as an excitation → surface group 1001 exists
  and its triangles lie on that face
- two sizes → the smaller-size box has more elements per volume
- two overlapping boxes → exit code 1 and an overlap error
- a face offset from its box → exit code 1 and a merge error

**Study tests** (`tests/test_study.py`, run with `FreeCADCmd`):

- IDs are assigned in tree order and stay the same after adding a body
- renaming a body Label keeps its ID and changes its name
- a deleted body's ID is not reused
- a duplicate ID edit is refused
- checks in section 7 produce their messages
- `job.json` content matches a small hand-built document

**Manual checklist** (buttons and dialogs): create a study, add each item
type, edit, rename, delete, run the mesh, cancel a run, view the result,
edit the ID table.

## 12. Later steps (each gets its own design)

1. 2D geometry → 2D mesh
2. Structured meshes
3. More mesh-field types per body (distance-based refinement and others)
4. EMSolution input file (material and excitation values)
