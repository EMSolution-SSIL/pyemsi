# Symmetric Mesh by Rules: Requirements and Design

Date: 2026-11-09
Status: written after the brainstorm, waiting for the user's review
Branch: written on `feature/symmetric-mesh-3d`
Changes: `2026-10-23-symmetric-mesh-design.md` (2D) and `2026-11-05-symmetric-mesh-3d-design.md` (3D). Their mesher
ideas hold (mesh the cell, copy the mesh, periodic seams, sliding grid, copied excitation surfaces) unless this
document changes them. The way the copies are defined, and how Materials are given, is replaced.
Evidence: the catalogue of 72 examples, https://claude.ai/artifact/EeB3vxYUjFhPQ1mAWdRURy (IDs such as M3-10 below refer
to it), and throwaway gmsh tests whose meshes are in `C:\Users\hamed\Desktop\delme\frozen_air_meshes` (section 9).

## 1. Why

Today's Symmetric Mesh reads a chain of Part Mirror, Draft Polar Array, Compound and Boolean Fragments objects
(`symmetry.read_chain`). It does not detect symmetry from the shape, but the user still has to draw in the way the
reader expects, and it is too narrow:

- mirror planes must contain Z, polar arrays must be about Z, translations are refused;
- every cell body in an item must have the same copies, and there is one item per side;
- nothing can be meshed normally beside the copies, so there is no air around whole coils or strands;
- Materials are clicked on pieces, so a 36-slot phase grouping is 72 clicks and depends on FreeCAD face numbers.

The user wants to say it directly: these are my cell objects, these are the mirrors and rotations in this order, about
these axes, and this is what each object becomes afterwards. Of the 72 examples, 29 work today, 4 work partly, 32 are
refused and 7 are traps the tool has to catch.

**The logic is general (the user's rule).** The examples illustrate the model and test it. They are not the cases to
implement. So:

- The rule engine, validation and mesher know only cell objects, rigid transforms, part names and free objects. They know
  nothing of motors, slots, coils, strands or air, and no code tests for a kind of device or for a name.
- Something may be refused for only three reasons: the geometry does not fit (overlaps, mismatched seams), the solver
  cannot do it (sliding about Z, axisymmetry), or the method does not handle that case yet, and then the message says so.
- Knowledge of a device lives only in optional helpers that fill in general fields, such as the winding generator.

## 2. Scope

**In**

- 3D Studies and 2D Studies (a Study is all 2D or all 3D).
- Any number of **groups**, each with its own cell objects and its own ordered rules. A rotor has rules of its own.
- Rules: mirror about any plane, rotation about any axis with a step and a count, translation. Any order. Each rule acts
  on everything made so far, so "mirror first, then rotate the results" is two rules.
- Per object, what its copies become: one part, each copy separate, merged across chosen rules, or named by a table.
- A winding table, separate from the rules, with a generator for distributed, fractional-slot and concentrated
  two-layer windings.
- Whole objects that reach past their sector: distributed coils with curved end turns (M3-10), twisted and double-skew
  Litz strands (L-01 to L-13).
- Objects **meshed normally beside the copies**, in particular air drawn by the user.
- Mixed structured and unstructured cells: quads and triangles in 2D, hexahedra, prisms, tetrahedra and pyramids in 3D.
- Sliding motion as today: Rotational about Z, one interface, with a Z mirror now allowed.
- An optional helper that reads an existing Mirror / Polar Array drawing and fills in the rules.

**Later (not in this work)**

| What | Example |
|---|---|
| Panel entry for a screw step (rotate and move as one rule); the engine takes it already (section 4.1) | M3-03 |
| Panel entry for mirror and rotate as one step; the engine takes it already | M3-05 |
| Removing one copy (a fault study) | M2-09 |
| Two groups that touch directly with different repeats | M3-08 |
| Merging what touches, as a part mode (a table does it today) | R-06 |
| Trimming a body at a mirror plane | T-04 |
| More than one Sliding Interface; Axial or Linear sliding | M2-13 |
| Detecting rules from a shape with no Mirror / Array objects behind it | |
| Formulas in the rule fields | |

**Anti-goals**

- Coils and strands are never cut at a sector boundary to make them fit a cell (the user rejected M3-11).
- Twisted wires are never built from slices (the user rejected R-10). Skew is part of the drawn strand.
- The automatic Air Region does not come into symmetric Studies. It stays for non-symmetric Studies only.
- The user never has to Explode compounds, and never has to draw Mirror or Polar Array objects to get a symmetric mesh.
- A wrong mesh is never produced silently: anything that does not fit is refused, naming the object and the place.

## 3. The user's workflow

1. Draw the cell objects as ordinary solids (3D) or faces (2D). Objects that repeat as a wedge stay inside the wedge. A
   coil or strand that should stay whole is drawn whole, even when it reaches past the wedge.
2. If there is air that does not repeat, draw it as an ordinary body, usually a plain block or cylinder over everything.
   The copies are cut out of it when meshing. Put it in the Main or Moving geometry.
3. Add a **Symmetric Group** for each set of objects with the same rules. In its panel: pick the cell objects, add the
   rules, and for each object choose what its copies become. The drawing of the full model appears in the 3D view as
   the rules are edited (order matters, T-01 and T-02, so the result has to be visible). The panel states the number of
   copies and parts.
4. For a winding, open the object's table and generate it from slots, pole pairs and coil span, then edit it if needed.
5. Choose the Material of each part. One choice can cover all parts of an object.
6. Mesh settings go on the cell objects, or are picked on the drawing and moved to the cell, as today (`to_cells`).
7. Excitations are picked on faces of the group's drawing, as on the top object today.
8. Validate Study, Run Mesh. The output files are the same as today.

What this looks like for some of the examples (illustrations only, nothing below is special-cased):

| Example | Group | Rules | Cell objects and what they become |
|---|---|---|---|
| M2-15, 36 slots, 4 poles, two layers | Stator | Rotate Z 10° × 36 | Iron, slot air, gap band: one part. Top side, bottom side: table |
| | Rotor (moving) | Mirror y = 0; Rotate Z 90° × 4 | Iron, rotor air: one part. V magnet leg: merged across rule 1 |
| M3-10, curved end turns | Stator | Mirror z = 0; Rotate Z 15° × 24 | Iron: one part. Half coil, whole: merged across rule 1, or table. Air: drawn, not in a group |
| M3-12, switched reluctance | Stator | Mirror y = 0; Mirror z = 0; Rotate Z 30° × 12 | Iron: one part. Quarter coil: merged across rules 1 and 2 |
| M3-07, shaft along X, locked rotor | Stator | Rotate X 7.5° × 48 | As a Z motor. Air gap: drawn, not in a group. A Sliding Interface is refused |
| | Rotor | Mirror y = 0; Rotate X 45° × 8 | Iron: one part. Magnet: merged across rule 1 |
| R-07, rod, one eighth drawn | Rod | Mirror x = 0; Mirror y = 0; Mirror z = 0 | Rod, air: one part each |
| L-06, 7 × 7 double skew | Centre strand | (no rules) | The straight strand on the axis |
| | Strands | Rotate Z 60° × 6 | The ring strand of the centre bundle and the 7 whole strands of one outer bundle: each copy separate. Air: drawn |
| L-07, the same mesh, 7 parts | as L-06 | as L-06 | The same strands, parts named by a table: one per bundle |
| D-07, three-core cable | Cores; Armour | Rotate Z 120° × 3; Rotate Z 9° × 40 | Bedding between them: drawn, not in a group |
| D-08, Helmholtz pair, ZX | Coil | Mirror z = 0 | Coil: each copy separate. Air: one part |

## 4. The model

| Term | Meaning |
|---|---|
| **Group** | A set of cell objects meshed together once, with one ordered list of rules. One side (fixed or moving). |
| **Cell object** | A body in a group. A body with several solids (faces in 2D), such as a Boolean Fragments that splits a cell, has one row per solid, so each block can have its own parts. |
| **Rule** | One mirror, rotation or translation. |
| **Copy** | One position of a cell object, identified by one index per rule. |
| **Part** | A named set of copies, possibly from several cell objects. A part is one MAT_ID, one volume or surface group, one Material. |
| **Free object** | A body in the Main or Moving geometry that is in no group. It is meshed normally. |

### 4.1 Rules

All values are in global coordinates, mm and degrees.

| Kind | Values | Copies |
|---|---|---|
| Mirror | a point on the plane, its normal | 2: as is, mirrored |
| Rotate | a point on the axis, the axis direction, step, count | count, the original included |
| Translate | a vector, count | count, the original included |

- To the engine a rule is one rigid motion G and a count, giving the copies G^0 to G^(n-1). Mirror, Rotate and Translate
  are only ways to enter G. The mesher receives plain transforms and never sees the kind of rule.
- Rules are applied in list order. With rules R1 to Rm, the copy with indices (i1, ..., im) has the transform
  Rm^im ∘ ... ∘ R1^i1. The all-zero copy is the identity, the drawn cell.
- Copies are numbered with the **last rule as the slowest index**, so a table for "Mirror, then Rotate" reads slot by slot.
- A group with no rules is allowed: its objects are meshed once and frozen like any other copy. This is how a centre
  strand sits among rotated strands (L-02).
- A rotation that stops short of 360° is allowed with a warning (T-03, M2-12): the tool cannot tell a slip from a sector.
- 2D XY Study: a mirror normal must lie in the plane, a rotation axis must be parallel to Z, a translation in the plane.
- 2D ZX Study (axisymmetric, new): mirrors with a normal along Z, translations along Z, no rotations.
- In-plane or axis limits apply only in 2D. In 3D anything goes, and only sliding narrows it (section 7.5).

### 4.2 Parts

Each cell object row has one of four modes. They all do one thing: give every copy a part name.

| Mode | Copies in the same part | Typical use |
|---|---|---|
| One part | all | stator iron, air gap |
| Each copy separate | none | strands |
| Across chosen rules | those that differ only in the ticked rules | the two halves of a coil across a Z mirror |
| Table | those with the same name in the object's table | windings, N/S magnets, one odd magnet (M2-10) |

- A part name used by several objects on the same side is one part: bars and end rings of a cage (M3-06), both layers
  of a phase belt (M2-15), the strands of a bundle (L-07). A part need not be connected.
- A name used on both sides of a Sliding Interface is refused, as today: the moving side needs its own IDs.
- **Parts do not change the mesh.** Copies share nodes wherever they touch, whichever part they are in. Choosing parts
  only sets which group each element belongs to, so the same mesh can have 49 parts or 7 (L-06, L-07).

### 4.3 Winding table

The rules build the mesh and the table assigns the parts, because the two repeat differently: a 27-slot stator repeats
its mesh every 13.3° and its winding every 120° (M2-16), and a mirrored cell can carry a winding that is not
mirror-symmetric (M2-18).

The table holds one part name per copy of any object, editable by hand, and means nothing more than that. An optional
three-phase generator can fill it. It is the only motor-specific code, and all it writes is names in the table:

- Inputs: slots Ns (default: the rotation rule's count), pole pairs p, coil span y, and which row is the top layer and
  which the bottom layer. A whole-coil object (M3-10) is one row.
- The slot of a copy is found from the angle of its centre about the rotation axis, so a mirrored cell works.
- Sector of the coil whose top side is in slot k: `((k*p*360 + 30*Ns) % (360*Ns)) // (60*Ns)`, with sectors in the order
  A+, C−, B+, A−, C+, B−.
- The bottom layer of slot k takes the sector of coil k − y, plus 3 (the return side). So one table and a span give both
  layers. With y = 1 this also gives concentrated windings (M2-08).
- Options: one part per phase and direction (the default, names `A+`, `A-`, ...), or one part per coil.

The default model of a motor is a distributed winding. Concentrated windings are for machines such as switched
reluctance.

### 4.4 Free objects

Everything in the Main or Moving geometry that is not in a group is a free object. It gets a Material as an ordinary
body. It is meshed normally, around the frozen surfaces of the copies on its side.

- The user may draw the air solid, right over the copies, or with holes. The tool cuts at mesh level (section 7.4), with
  no boolean against the copies.
- The general rule: a free object's mesh is bounded by whatever of its own surface the copies leave uncovered, and by
  the copies' surfaces inside it. Copies may sit inside it, lie flush against whole faces of it, or meet a planar face of
  it in any pattern. A copy crossing a curved face of it is not handled yet, because holes were only tested in planar
  faces. That is refused, and the message says it is a limit of the tool, not a fault in the model.
- Two groups with different repeats that would meet (a locked rotor in its stator) are joined by a free object drawn
  between them, flush against both: the air gap as a ring.
- Mesh Size works on free objects. A free object with frozen holes cannot be Transfinite; that is refused.
- The automatic Air Region is refused in a symmetric Study, as today (`validation.py`, `_symmetric`).

### 4.5 Reading rules from a drawing

A button in the group's panel: pick an existing Mirror / Polar Array chain and the tool fills in the cell objects and the
rules, which the user then accepts or edits. `symmetry.read_chain` and `symmetry.steps` become this helper, with the
limits on Z removed. Branches of the chain with different copies are proposed as separate groups. A chain whose copies
cannot be written as an ordered rule list gets an explanation instead of a guess.

## 5. Add-on objects and panels

- **Symmetric Group** replaces the Symmetric Mesh item (`objects.SymmetricMesh`, command `EMS_SymmetricMesh`). It holds
  the cell objects, each row's part mode and table, the rules and the side. It produces the drawing: a compound of all
  the copies, updated when anything changes, visible and pickable in the 3D view. No boolean is run on it.
- **Side:** fixed or moving, set in the panel and shown only for Sliding motion. Cell objects are not listed in the Main
  or Moving geometry; a body that is both is refused.
- **Materials:** one assignment per part, created when the part appears and listed in the Study as today. It stores the
  group and part name in place of today's `Pieces` / `PieceCentres`, so it no longer depends on face numbers. Clicking
  the drawing selects the part of the copy clicked. One action sets the library material of all parts of a cell object.
  When a change of rules removes a part, its assignment goes too and the panel says so.
- **Mixed Studies:** `is_symmetric` today switches whole code paths (`validation._symmetric` replaces the air, slide and
  Material checks; `objects` and `jobwriter` branch the same way). These must now handle groups and free objects
  together. Free objects follow the ordinary path.
- **Excitations:** on faces of a group's drawing, as on the top today, or on faces of free objects as in any Study.
- **Mesh settings:** on cell objects, or picked on the drawing and moved to the cell (`to_cells`), as today.
- **Old Studies:** this feature has never been in a release (no tag contains it), so nothing converts automatically. An
  old Symmetric Mesh item shows an error asking for a new group, and the reading helper fills that group from the old
  chain. Materials are given again. The examples and tests are moved to the new item.

## 6. Validate Study

Refused, naming the object and rule or place:

- A rule with a zero normal, axis or vector, a count below 2, or limits broken in 2D (section 4.1).
- A rule that makes two copies identical (for example, the same mirror twice, or a rotation running past a full turn).
- A copy overlapping another copy of the same group (T-04, T-05), using today's `_overlaps`, which tests the cell against
  each copy. Touching is fine.
- Copies of two groups on the same side touching or overlapping: "put them in one group, or draw a normally meshed body
  between them".
- A free object in a relation not allowed by section 4.4, or crossing a Sliding Interface (section 7.5).
- A part with no Material; a part name on both sides; a table of the wrong length or with an empty name.
- A cell object with no solid (face in 2D); a body in two groups, or both a cell object and in the Main or Moving geometry.
- An Air Region in a symmetric Study.
- Sliding: section 7.5.

Warned:

- A rotation that does not close.
- After meshing, the number of elements below a quality threshold, per part (section 9 explains why).

Mismatched seams (T-06) surface when meshing and are refused then (section 7.2, step 6).

## 7. The mesher

Runs in the mesher process (`meshsym`, no FreeCAD imports). `--check` runs all of it without writing, as today.

### 7.1 Job

The `symmetric` block carries per group: the side, the cell objects (one BREP each, as today), the transforms, and for each
cell object row and copy the part (MAT_ID, name). `_land`, `_outline` and the piece BREPs go away: where a copy lands is
known from the rules. Free objects travel as ordinary `bodies` / `volumes`, marked as free.

### 7.2 Each group

1. Build the group's cell in its own gmsh model, with the mesh settings applied as today (`mesher.build`). Objects of
   other groups do not influence it.
2. Sliding, if the group reaches the interface (section 7.5).
3. Seams: faces of the cell that a transform maps onto each other are meshed as copies (`_periodic`, as today).
4. Contact across copies: section 7.3.
5. Generate to the Study's dimension. Copy by the transforms. Mirrored copies have reversed connectivity. Join coincident
   nodes within the group.
6. Refuse if the copies do not fit: any element facet shared by 3 or more elements, or a total shared facet area between
   copies that differs from the contact area computed from the geometry. The second check replaces `_conform` and catches
   T-06.

Scale: case 7 of section 9 has about 490,000 copied elements. The spike copied and joined them with numpy arrays; today's
`_copy` is a Python loop over nodes and may not keep up.

### 7.3 Contact between whole objects and other copies

A wedge's seams are covered by step 3. A whole object is different. The slot of one iron wedge touches the top side of
coil 0 and the bottom side of coil −5 (M3-10 pressed against the slot walls), and the iron has to carry nodes matching both.

This happens while the cell model is built, before meshing. For a pair of cell objects A and B of a group and a transform
T other than the identity, if T(A) touches B over an area that the seams of step 3 do not already cover:

1. Bring the contact patch back to A with the inverse of T and split A along it, so A's faces pair one to one with those of its image.
2. Add the image T(A) to the cell model and fragment it with B.
3. Mesh each face of the image as a copy of its face on A (`setPeriodic`, paired by centre of mass).
4. Drop the image's elements after meshing. The real coil −5 is the copy made in step 5 of section 7.2.

### 7.4 Free objects: frozen surfaces (3D)

1. Boundary of the copies of a side: the element faces used by exactly one element. Contact and seam faces drop out
   by themselves.
2. Put a pyramid on every frozen quad, before gmsh sees it: apex at centroid + normal × 0.3 × sqrt(area), the normal
   pointing away from the element that owns the quad. The tool builds these and assigns them to the free object. gmsh
   then sees only triangles. (Left to gmsh, its pyramids plus `Mesh.Optimize` left faces shared by 4 tetrahedra.)
3. Mesh the free object's own OCC faces to triangles. Facets of the copies lying on a planar free face are removed
   from the frozen set, and that face gets polygon holes through the exact end-edge nodes (each polygon edge transfinite
   with 2 nodes). A free face entirely covered by copies is dropped.
4. Add the frozen triangles and the free surface as discrete surfaces, `gmsh.model.mesh.createTopology()`, then
   `geo.addSurfaceLoop` (outer first, then one per inner shell) and `geo.addVolume`, `geo.synchronize()`. Shells outside
   the free object (found by a point test) are left out.
5. `Mesh.Algorithm3D = 1`, `Mesh.Renumber = 0` (gmsh renumbers otherwise), `generate(3)`.
6. Refuse unless every frozen face is on the boundary of the new elements and no node of the copies moved.

Removing the copies can split a free object into disconnected regions: a stator running the free object's full height
leaves a bore and an outside. Each region is meshed with its own loops, and all of them belong to that free object.

In 2D the same idea: free edges, chained into loops, become OCC plane surfaces with polygon holes (2-node transfinite
lines), and the nodes are joined afterwards.

Several free objects that touch each other are fragmented first, as in an ordinary Study, and each is meshed with the
shells it contains.

### 7.5 Sliding

- Rotational about Z, one interface, as today. Rule axes elsewhere are accepted by the rules and refused only by the
  Sliding Interface, which names the rule (T-07). For a group that reaches the cylinder, only these are allowed: rotations
  about Z through the origin, mirrors containing Z, and mirrors of z = const.
- The surface must be covered by copied cell objects on both sides. **A free object may not touch it.** So air near the
  gap is a copied cell object (a band, reaching the full height of the drawing), and free air lies outside that band.
- Node grid, marker line and the "only the nodes have to match" rule are as in the 3D spec.
- A Z mirror is new with sliding, and two places in `meshsym` assume all copies are around Z: `_slide_faces_sym` computes
  the needed area as 2πr / copies, and takes the z range from the cell's faces. They must use the rotation count and the
  full height of the drawing. The check in `validation._interfaces` that divisions are a multiple of the copies must use
  the rotation count too.

### 7.6 Output

All elements go into one model as discrete entities, physical groups by part (MAT_ID) and free object. Excitations use
today's copied-surface logic (`_land_surfaces`, with the drawing's faces), and excitations on free faces are physical
groups of the free object's surface mesh. Files as today: `.msh`, `mesh.unv`, and `rotor.msh` with sliding.

## 8. Success

1. Unit tests of the rule engine: transforms and numbering, T-01 against T-02, each part mode, the winding generator
   against the tables in M2-15 to M2-18.
2. These validate and mesh inside the add-on, each with 0 inverted elements, no facet in 3 or more elements, every frozen face
   kept: the existing sliding motor example redone with rules; M2-15; M3-02 (Z mirror) with sliding; M3-07; M3-10 with
   drawn air; M3-12; R-07; L-06 and L-07 with drawn air; D-07; D-08.
3. An arrangement from no catalogue passes the same way: arbitrary solids, oblique mirror planes and rotation axes,
   several groups, free objects. The examples of item 2 pass with no code that knows about them.
4. `gui_smoke.py` covers creating a group, adding rules, seeing the drawing and picking a part.
5. The user solves one mesh with EMSolution from each family: mixed free air and copies, and pyramids against frozen hexahedra.

The plan should start with what is untested (section 9), sliding first.

## 9. What is known and what is not

Tested in gmsh, outside the add-on. In every case: each frozen face kept, watertight, 0 inverted.

| File | Case | Elements | Worst air min SICN (below 0.1) |
|---|---|---|---|
| 1 | 7 strands in air | tet | 0.121 (0) |
| 2 | 49 double-skew strands in air, 4.6 s | tet | 0.076 (3) |
| 3 | 49 strands ending on the air's end planes | tet | 0.003 (145) |
| 4 | 24 interleaved half coils in air | tet | 0.001 (11,390) |
| 5 | Tooth coils touching iron, 2 mirrors and rotation | tet | 0.064 (3) |
| 6 | Distributed coils, 0.3 mm clearance from iron | tet | 0.001 (22,390) |
| 7 | Distributed coils touching iron across copies | tet | 0.001 (22,104) |
| 8, 9 | 2D, structured coils and gap, free iron and slot air, rotated and mirrored | quad, tri | 0.754, 0.760 (0) |
| 10 | Hexahedral coils touching tetrahedral iron | hex, tet, pyramid | 0.076 (3) |
| 11 | Stator extruded in layers, free air | hex, prism, tet, pyramid | 0.209 (0) |

Shared iron and coil surface equals the expected area exactly in 5, 7 and 10. For scale: meshing the 49 strands as a
whole model took about 150 s with 294 poor elements, against 4.6 s and 3 here.

**Not tested:**

- Sliding together with free air, or with a Z mirror.
- An EMSolution solve on any of these meshes.
- Several free objects touching; excitations on free faces; a free object split into regions in 3D (done by hand in 2D).
- Pyramids on frozen quads with a narrow gap in front of them.
- Step 1 of section 7.3 as a general method. The test split the coil by hand with one plane.

**Known weakness:** the poor elements in cases 4, 6 and 7 come with the coil surface drawn as a ruled loft, which is a stack
of thin strips. In case 4 nearly all of them touch those thin triangles. The curved coil is the cause, not the method: straight
hexahedral and extruded coils have none. Spline lofts are not the way out, as they gave a 10% low volume and bad booleans. The
surface mesh of such a cell needs improving (try `gmsh.model.mesh.setCompound` over the strips); until then the tool reports the
poor elements (section 6).

## 10. Evidence for the builder

The spike scripts are throwaway and live only in the session's temporary folder. Sections 7.3 and 7.4 are their recipe.
Meshes: open with `pixi run gmsh "<file>"`, and hide Air under Tools > Visibility. Solids: `delme\curved_end_windings`
(diamond lap coil and racetrack tooth coil) and `delme\double_skew_litz`. A distributed end turn is a diamond: straight sloped
arms in two radial layers with the layer change at a rounded nose. `Part.makeLoft(wires, True, ruled=True)`.

## 11. Decided by the user

- The user specifies cell objects and rules by hand; detection is an optional helper.
- Mirror and rotation with their axes and counts, in order (mirror first, then rotate the results), in any direction.
- Objects differ in what they become: stator core fused, coils in many parts, air gap fused.
- A rotor has its own rules. A model is all 2D or all 3D.
- Symmetry accepts arbitrary axes although sliding is Z only.
- Motors default to distributed windings; concentrated is for cases such as switched reluctance. Top and bottom layers
  matter, especially with fractional slots. Curved end windings for both.
- Coils and strands stay whole objects (M3-10 yes, M3-11 no).
- The automatic Air Region is for non-symmetric meshes only. With symmetry the user draws the air.
- Litz wires are varied, mainly 3D, no slices, double skew included. R-10 dropped.
- Some cells structured and others unstructured must work together, in 2D and 3D.
- The examples are only examples: the logic must be general, not specific to them.

## 12. Decided by me (Claude), not by the user; check these

The first three matter most.

1. The tool makes the full drawing from the rules. Mirror and Polar Array objects are no longer needed, and the old chain
   only feeds the reading helper.
2. A part is exactly one MAT_ID and one Material. Assignments are created per part, not picked.
3. The new item replaces the old one with no automatic conversion, because the feature has never been released.
4. Translation is in (5 examples use it), though the user named only mirror and rotation.
5. The "Later" table in section 2, in particular the step-skew rotor M3-03 and groups touching directly (M3-08).
6. Touching groups are refused; the way out is one group, or a drawn body between them. So a locked rotor needs its air
   gap drawn as a ring.
7. Free objects stay off the sliding surface, so air near the gap is a copied band.
8. The helper reads drawings only; it does not detect symmetry from a bare shape.
9. ZX Studies accept mirrors along Z and translations along Z, nothing else.
10. The side is set on the group, not through the Main / Moving lists.
11. A centre strand is a group with no rules, instead of a per-object choice of which rules apply.
12. Four part modes. "Merge what touches" waits; a table does it.
13. The winding generator is three-phase and covers two-layer windings and whole coils. Anything else is typed into the
    table.
14. Rules that make identical copies are refused rather than quietly merged as today.

## 13. Left to the builder

- Panel layout, quick presets for common planes and axes, picking a plane or axis in the 3D view.
- How the drawing is made available for picking without a dependency cycle (a Study object cannot be linked from
  geometry the Study depends on).
- How rules and tables are stored on the object.
- Tolerances, and the quality threshold of the warning.
- Which files split up. `symmetry.py` is the natural home of the rule engine (no GUI) and `meshsym.py` of the mesher;
  frozen surfaces may deserve a module of their own.
- Whether seams (section 7.2, step 3) and images (section 7.3) become one mechanism.
- The example documents and test fixtures.
