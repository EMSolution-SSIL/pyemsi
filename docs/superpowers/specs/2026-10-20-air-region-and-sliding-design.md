# Air Region and Sliding Interface for FreeCAD Studies: Design

Date: 2026-10-20
Status: decisions agreed in conversation, waiting for spec review
Branch: `feature/freecad-addon`

## 1. Goal

Today the user must build the air region by hand: cut the coil and core from an
air box with Part booleans, then take a simple copy of the result, because the
Study drops a body that another listed body is built from (`geometry.collect`).
The copy does not follow later changes. With a rotor and a stator the work
doubles and the sliding surface must be meshed by hand as well.

This step makes the air automatic:

- An **Air Region** item gives only the outer shape. The mesher fills it around
  every body of the Study. Bodies stay in the main geometry as they are, and the
  air follows any body that is added, removed or changed.
- For sliding motion, a **Sliding Interface** item splits the air into a fixed
  part and a moving part. The two sides are meshed with the same uniform
  division along the motion, which is also written as `SLIDE_NDIV`.
- A script builds a set of example models covering 2D and 3D, static and
  sliding, and every air shape, so the user can check each mesh by hand.

## 2. Background

Facts from EMSolutionDocs (`files/handbook/inputControl/2_Analysis_Type.rst`,
`12_Geometry.rst`, `14_Periodic_Boundary_Conditions.rst`, `19_Motoin.rst`):

- `MOTION(2)`: 1 = the whole mesh or a `COIL` source moves; 2 = slide motion;
  3 = mesh deformation. Motions cannot be combined for 2 and 3.
- Slide motion (`MOTION` = 2): the moving part is a separate mesh file
  `rotor_mesh` (3D) or `rotor_mesh2D` (2D); several are allowed
  (`rotor_mesh2`, ...). Rotation is only about the **global Z axis**, angle zero
  on the x axis. Translation is allowed too.
- The slide surface is given by **slide edges** (3D: line elements in
  `rotor_mesh`) or **slide points** (2D: point elements in `rotor_mesh2D`) that
  carry `SLIDE_MAT_ID`, or by a straight segment (`LINE_INPUT` = 1). A slide
  edge is the generatrix of the slide surface. Its ends may lie on the axis,
  which allows a disc-shaped surface (axial gap).
- `SLIDE_NDIV`: divisions along the motion over one period. The handbook says
  accuracy is best when it equals the mesh division, and that the two sides may
  differ. `FITNESS` is a tolerance for nodes that almost coincide.
- Periods: rotation `CYCLIC` = 2/3 with `ANGLE` = the meshed angle;
  translation `CYCLIC` = 1 with `DXYZ` = the mesh length along the motion.
  `SYMMETRY` = 1 is anti-periodic. Several slide faces are allowed (the
  handbook example has two planes, a mover between two stators).
- 2D planes: XY is planar analysis (`GEOMETRY` = 1); ZX (y = 0) is
  axisymmetric (`GEOMETRY` = 2, 3) with X as the radius.
- A working 2D slide model from the user (a 45° IPM motor sector,
  `transient.json` with `pre_geom2D.msh` and `rotor_mesh2D.msh`) shows:
  - `CYCLIC` = 2, `SYMMETRY` = 1, `ANGLE` = 45, `SLIDE_NDIV` = 90,
    `SLIDE_MAT_ID` = 99, `FITNESS` = 0.01.
  - The slide circle (r = 80.575 mm) is the outer edge of the rotor file and the
    inner edge of the stator file. Both files have the same 91 nodes on it,
    every 0.5°: 90 divisions = `SLIDE_NDIV`.
  - The slide point is one point element (Gmsh type 15) in `rotor_mesh2D`
    only, at angle 0 on the slide circle, physical group `0 99 "slide_point"`.
  - The two periodic edges (θ = 0° and θ = 45°) have the same node radii in each
    file.
  - The air gap is split at the slide circle: rotor air `MAT_ID` 40, stator air
    `MAT_ID` 41.
  - Each file numbers its nodes from 1 by itself; slide nodes appear in both
    files with their own tags. Elements are mostly quads, some triangles.
- The user confirmed that periodic boundaries must have matching nodes.
- Already built: `Movement` ("No movement", "Sliding motion") and the Main /
  Moving geometry regions on the Study, Gmsh `fragment` of all bodies with an
  overlap error in `mesher.py` / `mesher2d.py`, transfinite edges and bodies,
  Recombine, and Validate Study.

## 3. Decisions

1. **Scope: static and slide motion only.** Deform (`MOTION` = 3) and mesh or
   coil motion (`MOTION` = 1) are left for later. Motion in an axisymmetric
   (ZX) Study is not supported now.
2. **The mesher builds the air, not FreeCAD.** No Part boolean is made in the
   document, so `geometry.collect` never drops a body because of the air.
3. **Air has the lowest priority.** After `fragment`, a piece inside the Air
   Region and inside a body belongs to the body. A piece only inside the Air
   Region is air. Two bodies that overlap are still an error, as today.
4. **Air Region is a Study item**, in a new folder `Air Regions`. It is a shape
   object (`Part::FeaturePython`) that holds only the outer shape. It is shown
   transparent so it does not hide the bodies. It gets a `MAT_ID` and a
   material like a body, and its outer faces can be picked for mesh sizes.
   It is not listed in the main geometry. One Air Region per Study in this step.
5. **Air shapes.**
   - Box (3D) / Rectangle (2D): size and centre, or "bounding box of the
     bodies + padding %".
   - Sector: inner radius, outer radius, start and end angle, and height in 3D.
     It covers circle, half circle, quarter circle, ring and crescent, and their
     cylinders.
   - Custom: any body the user made becomes the outer shape.
   - In a ZX Study only a half disc with its flat side on the Z axis and a
     rectangle starting on the axis are allowed.
6. **Sliding Interface is a Study item**, used only when `Movement` is
   "Sliding motion". One or more per Study. Types:

   | Dimension | Type | User gives | Surface |
   |---|---|---|---|
   | 2D XY | Rotational | radius | circle or arc about Z |
   | 2D XY | Linear | position, motion axis (X or Y) | line |
   | 3D | Rotational, radial gap | radius | cylinder about Z |
   | 3D | Rotational, axial gap | z position | disc or ring in a plane z = const |
   | 3D | Linear | position, normal axis, motion axis | plane |

   The surface always spans the whole Air Region across. Its extent (height,
   angle range, length) comes from the Air Region, so the user does not give it.
7. **Same uniform division on both sides.** The item has `N` along the motion
   (over the meshed period) and, in 3D, `N` along the generatrix. The surface
   is meshed transfinite so both sides have the same nodes. The triangle
   diagonals all point one way, so the mesh is unchanged by a shift of one
   division. `N` along the motion is the `SLIDE_NDIV` value.
8. **One Gmsh model, two files.** The whole model, fixed and moving, is meshed
   at once, so the slide surface is shared. Elements are then written to
   `pre_geom(2D)` (fixed side) and `rotor_mesh(2D)` (moving side). Each file
   numbers its nodes from 1; nodes on the slide surface appear in both files.
   The slide point (2D: one point element at the start angle or start position
   on the slide line) or slide edge (3D: line elements along the generatrix
   there) goes into `rotor_mesh(2D)` only, with its own `SLIDE_MAT_ID`, as in
   the user's sample.
9. **Fixed and moving air.** The interface cuts the air into pieces. A piece
   that touches only Moving bodies is moving air; a piece that touches only
   fixed bodies is fixed air. Each side gets its own `MAT_ID`
   (`<Air> fixed`, `<Air> moving`). A piece that touches both or neither is an
   error that names the interface.
10. **Periods come from the air.** A sector Air Region gives `ANGLE` = its
    angle; a linear model gives `DXYZ` = the Air Region length along the motion.
    The two periodic boundaries (sector sides, or the two ends of a linear
    period) are meshed with matching nodes through Gmsh `setPeriodic`, in both
    files. This covers the bodies cut by those boundaries as well as the air.
11. **Slide values are reported, not written into the input file.** The add-on
    does not write input files yet. Run Mesh prints `SLIDE_NDIV`,
    `SLIDE_MAT_ID`, `ANGLE` or `DXYZ`, and a ready-to-paste
    `14_Periodic_Boundary_Conditions` block. Writing them into the input file
    waits for the input-file coupling work.
12. **Examples outside the repository.** A script in the repository builds the
    example models; its output goes to `C:\Users\hamed\Desktop\delme\air_examples`
    by default (a command-line argument changes it). The same case builders are
    used by pytest.

## 4. Validation (Validate Study and Run Mesh)

One clear line each, naming the objects:

- A body is not fully inside the Air Region.
- A body crosses a Sliding Interface.
- A Moving body is on the fixed side, or a fixed body on the moving side.
- A rotational interface whose axis is not the global Z axis.
- Sliding motion in a ZX Study.
- An air shape that is not allowed in a ZX Study.
- An air piece touching both sides or neither (decision 9).
- A sector angle or period length that the division `N` does not split into
  whole steps, if it is not a whole number of divisions.
- Sliding motion without a Sliding Interface, or an interface in a static
  Study (warning).
- Overlapping solid bodies (unchanged).

## 5. Job file and mesher

- The job gets `"air"`: the BREP of the outer shape, its `MAT_ID`(s) and size.
- The job gets `"slides"`: per interface, type, BREP of the surface, `N` values,
  `SLIDE_MAT_ID`, and which bodies are moving.
- `mesher.py` / `mesher2d.py`:
  1. Import bodies, air shape and slide surfaces; `fragment` them together.
  2. Give each 3D (or 2D) piece its owner: a body if any body contains it,
     else air (decision 3). Split air pieces by side (decision 9).
  3. Make the slide surface and its edges transfinite with the given `N`.
  4. Mesh once. Write the fixed side to `pre_geom(2D).msh` and the moving side
     to `rotor_mesh(2D).msh`, plus the slide edge or slide point elements.
  5. Print the MAT_ID table and the slide values (decision 11).

## 6. Add-on changes

- `objects.py`: `AirRegion` and `SlidingInterface` proxies, an `Air Regions`
  folder (with Sliding Interfaces inside), ID keys for air sides and
  `SLIDE_MAT_ID`.
- `geometry.py`: air shape building; nothing changes in `collect`.
- `validation.py`: the checks in section 4.
- `jobwriter.py`: the `"air"` and `"slides"` job keys; the rotor file name.
- `commands.py`, `taskpanels.py`: Add Air Region and Add Sliding Interface
  commands and panels; Materials panel lists the air sides as rows.
- `geometry.export_unavailable`: stop blocking sliding motion.

## 7. Example models

Each model gets its own folder with the `.FCStd`, the mesh files, a short report
(elements per `MAT_ID`, nodes on each side of each slide surface, whether they
match) and a checklist of what to look at in the mesh.

Static:

| # | Dimension | Air shape | Content | What to check |
|---|---|---|---|---|
| 1 | 2D XY | Rectangle | C core + coil | air around the bodies, no overlap |
| 2 | 2D XY | Full circle | simple cross-section | round outer boundary |
| 3 | 2D XY | Half circle | same, symmetric | straight symmetry edge |
| 4 | 2D XY | Quarter circle | same | two symmetry edges |
| 5 | 2D XY | Crescent (hollow sector) | ring-shaped | inner radius |
| 6 | 2D XY | Custom | user shape | air priority |
| 7 | 2D ZX | Half disc on the Z axis | solenoid + plunger | x ≥ 0, edge on the axis |
| 8 | 2D ZX | Rectangle on the Z axis | same | same |
| 9 | 3D | Box | core + coil (like `comp_test`) | today's problem, solved |
| 10 | 3D | Full cylinder | same | |
| 11 | 3D | Quarter cylinder | symmetric | symmetry faces |
| 12 | 3D | Hollow sector | ring-shaped | |

Slide:

| # | Dimension | Type | Feature | What to check |
|---|---|---|---|---|
| 13 | 2D XY | Rotational | full 360° motor | N points on the circle, both sides match |
| 14 | 2D XY | Rotational | 90° sector (`ANGLE`) | N divisions on the arc, arc ends |
| 15 | 2D XY | Linear | one slide line | `DXYZ` = period length |
| 16 | 2D XY | Linear | two slide lines (mover between) | both lines |
| 17 | 3D | Rotational, radial | 360° cylinder | N_θ × N_z on the cylinder |
| 18 | 3D | Rotational, radial | 90° sector | |
| 19 | 3D | Rotational, axial gap | disc slide surface | radial generatrix |
| 20 | 3D | Linear | flat slide surface | N along × N across |

Error cases (Validate must refuse each with a clear message):

| # | Problem |
|---|---|
| E1 | A body sticks out of the air |
| E2 | A body crosses the slide surface |
| E3 | Rotation axis is not the global Z axis |
| E4 | Sliding motion in the ZX plane |
| E5 | A Moving body on the fixed side |
| E6 | Two solid bodies overlap (today's behaviour stays) |

## 8. Tests

- Case builders in `tests/freecad_addon/` shared by pytest and the example
  script.
- `test_mesher.py` / `test_mesher2d.py`: air fills around bodies; body wins over
  air; both sides of each slide surface have the same nodes and `N` divisions;
  slide edge or point elements are in the rotor file with `SLIDE_MAT_ID`;
  periodic boundaries have matching nodes in each file.
- A reference check: rebuild the user's 45° sample as example 14 and compare
  its slide and periodic node layout with the sample's files.
- `test_study.py`: each check in section 4; job content.
- `gui_smoke.py`: add an Air Region and a Sliding Interface and run Run Mesh.

## 9. Open points for review

- **3D slide edge placement.** The 2D slide point is settled by the user's
  sample. For 3D, one generatrix at the start angle is assumed by analogy;
  no 3D slide sample has been checked yet.
- **Transfinite on a full 360° cylinder.** The seam may make a transfinite
  surface fragile in Gmsh; the surface may need to be split in parts.
- **Side rule (decision 9).** An air pocket touching no body, e.g. a closed
  hole, would be an error; it may need an explicit side instead.
- **Several Air Regions** (e.g. a separate `MAT_ID` for the air inside a coil)
  are left out; priority between air items would be needed.
- **Not verified with EMSolution.** No generated `rotor_mesh` has been run
  through the solver yet.

## 10. Not in this step

Deform motion (`MOTION` = 3, deform air layer, `deform_mesh`, control volumes),
mesh or coil motion (`MOTION` = 1), motion in axisymmetric Studies, several Air
Regions, combined motions, writing the input file.
