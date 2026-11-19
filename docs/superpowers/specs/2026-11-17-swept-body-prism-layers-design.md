# Swept Body and 3D prism layers (design)

Status: draft after builder check, 2026-11-17, awaiting the user's approval. Follows the mesh refinements work
([2026-11-14-mesh-refinements-design.md](2026-11-14-mesh-refinements-design.md), all 4 stages built on
`freecad/mesh-refinements`).

## 1. Intent

In 3D the Skin Layer today makes graded tetrahedra: fine at the surface, coarser inside. Tetrahedra are the same size
in every direction, so resolving a skin of δ / 2 also makes the conductor that fine along its whole length. On long
conductors (litz strands, busbars, winding turns, coil turns) and on thin plates this costs far more elements than
the physics needs. 2D already has quad layers; 3D has nothing structured.

The user wants two new 3D meshing methods, for every conductor shape they work with: litz bundles, busbars,
transformer windings, coil turns and eddy-current plates (user, 2026-11-17: "all of the mentioned shapes").

1. **Swept Body**: mesh a body's cross-section once in 2D (with its skin) and copy it along the body, giving
   hexahedra and prisms that are long along the conductor and thin across the skin.
2. **3D prism layers**: the Skin Layer's `QuadLayers` setting works in 3D, growing prism layers inward from the
   surface mesh, for conductors that are not sweeps.

## 2. Goals, non-goals, anti-goals

Goals
- Swept Body for every body that is a profile moved along a path of straight lines, circular arcs and helices
  (screw motions), including closed rings and paths made of several such pieces joined smoothly.
- The cross-section carries the body's Skin Layer: quad layers on smooth sections, a graded structured grid on
  rectangular sections (busbar, plate edges), graded triangles on the rest.
- 3D prism layers inside a Skin Layer body with `QuadLayers` on.
- Both work in ordinary and symmetric Studies (a swept or layered cell is copied like any other cell; litz1).
- Neighbours (air, other bodies) mesh around the structured body with matching nodes on the shared faces.

Non-goals (this round)
- Paths with free-form curves (B-splines). Validate refuses them with a clear message.
- Sweeps whose profile twists relative to the path other than by the screw motion itself, or changes size (lofts).
- Structured meshing of the air gap (that stays Transfinite, as today).
- A swept body touching the sliding interface surface (refused in this round).

Anti-goals (a failure even if it runs)
- A mesh that does not conform where a structured body meets its neighbours (hanging nodes, gaps, overlaps).
- Silent fallback: when a body cannot be swept or layered the user is told why (Validate or a mesher note), and the
  body is meshed as today.
- Changing the mesh of a Study that does not use the new items (same element count and node coordinates as before).

## 3. Approaches

- **A. Two separate features, sweep first (chosen by the user, 2026-11-17).** Swept Body is a new item next to
  Transfinite Body; prism layers are the Skin Layer's `QuadLayers` made to work in 3D. Each does one clear thing; the
  sweep gives the big savings and also helps without a skin (laminations, long bars).
- B. Prism layers first. Works on any body, but the surface and core stay isotropic tetrahedra, so long conductors
  save much less.
- C. One Skin Layer setting Graded / Prisms / Swept. Simplest panel, but ties a meshing method to skin depth.

## 4. How the structured body joins the rest of the mesh

Both methods mesh the structured body by hand (numpy) and then let gmsh mesh everything else around it. Two ways;
the Stage 1 spike (7.1) picks one:

1. **Pre-mesh in the CAD model (preferred if it works).** In the normal job, before `generate`, write the body's
   nodes and elements onto its own gmsh entities (`gmsh.model.mesh.addNodes` / `addElements` on the volume, its
   boundary faces, curves and points, nodes classified on the entity they lie on) and set `Mesh.MeshOnlyEmpty = 1`
   (available in the pinned gmsh 4.15.2), so gmsh meshes only the other entities and uses the body's face meshes as
   their boundary. Shared faces then match by construction.
2. **Frozen body (fallback).** Treat the body like a symmetric copy: its mesh is frozen and the region around it is
   meshed from facets by `meshfrozen.mesh_region`, the path free objects and the Air Region already use around copies.

Quad faces of hexahedra and prisms that touch tetrahedra get pyramids (`meshfrozen.quad_pyramids`, used today for
structured cells) or, if the spike shows gmsh does it, gmsh's own quad-to-tet transition.

## 5. Swept Body

### 5.1 Item

New proxy `SweptBody` (objects.py), command `EMS_SweptBody` (toolbar dropdown with Transfinite Body and Recombine,
right-click on a body), task panel in the `ItemPanel` style, icon `sweptbody.svg`, label `_size_text`-style text.

| Property | Type | Default | Meaning |
|---|---|---|---|
| `References` | LinkSubListGlobal | picks | whole bodies to sweep |
| `StartFace` | LinkSubListGlobal | empty | optional: the profile face of each body; empty = found automatically |
| `PathSize` | Length | 0 | element length along the path; 0 = the body's own size (its Mesh Size or the default) |
| `SectionSize` | Length | 0 | element size inside the cross-section away from the skin; 0 = the body's own size |

Table text: `along 2 mm` (plus `, section 0.5 mm` when set). If the body also has a Skin Layer, the section uses it
(5.3) and the table adds `, skin`.

### 5.2 Recognising the sweep (jobwriter, GUI-free)

The jobwriter reads the body's shape in FreeCAD (Part API, no GUI) and describes the sweep as a list of **pieces**,
each a screw motion: axis point, axis direction, angle, and advance along the axis.
- straight piece: angle 0, advance = length (extrusion, bar, plate);
- revolved piece: advance 0 (ring segment, winding turn without pitch, toroid);
- helical piece: both (litz strand, coil turn with pitch).

Steps:
1. Profile: `StartFace` if given, else a planar face whose partner (the face at the far end) is the same face moved by
   a rigid motion; a closed ring has no end faces and the profile is a planar cut through the body, normal to the
   path, at a point the jobwriter picks (where the cut ends up is the builder's call; the cut must not create a face
   in the final mesh groups).
2. Path: from the lateral faces' edges that run along the path (lines, circles, helices). A helix comes through OCC as
   a B-spline approximation; recognise it by fitting a screw motion to the edge within tolerance (the builder picks
   the tolerance; litz1's strand is the test case).
3. Check: the body must equal the profile swept along the pieces (volume within tolerance, and a few planar cuts
   along the path matching the moved profile). If not, Validate refuses with what failed ("the far end is not the
   start face moved", "the path has a free-form curve").

A body whose CAD history is a Pad, Pocket-free Extrusion, Revolution, Helix or Pipe (Part or PartDesign) is the
common case, but recognition works on the shape, not the history, so a Body built from several features still works.

The job gets `"swept": [{"mat_id", "profile": <BREP of the profile face>, "pieces": [...], "path_size",
"section_size", "skin": <the body's Skin Layer settings or null>}]`.

### 5.3 The cross-section mesh (mesher process)

The profile face is meshed in 2D in the mesher process, with the body's Skin Layer applied as in 2D Studies:
- smooth section (no corner where layer curves meet, the 2D rule of the existing spec 5.2): `BoundaryLayer` quad
  layers plus the graded fields, as the 2D Skin Layer does;
- rectangular section (four straight sides, the usual busbar and plate): a structured quad grid, graded toward each
  side: first element δ / ElementsPerDepth at the surface, growing by 1.2 until LayerDepth · δ, then SectionSize
  (gmsh transfinite curves with a progression or bump; the builder picks which);
- any other section: graded triangles (as the 3D graded Skin Layer, but in 2D); prisms result. Mesher note as today
  for a cornered body.
- No Skin Layer: the section meshed at SectionSize, quads if the body also has Recombine.

Section edges that lie on a cut of the domain (symmetry plane, periodic seam) get no skin, as in the existing spec.

### 5.4 Building the volume mesh

Stations along each piece every PathSize (rounded so each piece has a whole number of steps, at least 1). The section
nodes are copied to every station by the screw motion; quads become hexahedra, triangles prisms. A closed ring joins
its last station to the first (no duplicate nodes). Pieces join at shared stations. Node and element orientation is
checked (positive Jacobian), as meshfrozen does for copies.

Mesh groups: the body keeps its MAT_ID; excitation faces (SMAT_IDs) on the body's surface are found by which CAD face
each boundary quad or triangle lies on, as today.

### 5.5 Validation

- References are whole bodies; a body in two Swept Body items is refused; Swept Body with Transfinite Body or
  Recombine on the same body is refused (Recombine is honoured only for the section, see 5.3: Validate notes it).
- Not the Air Region; not a body touching the sliding interface surface (this round).
- **Contacts (user's decision, 2026-11-17: option a for now):** a swept body may touch the air and tetrahedral bodies
  only over whole faces (an end face against a terminal, a lateral face in air). Validate refuses a swept body that
  touches another structured body (another Swept Body, a Transfinite Body, a Recombine body, a body with 3D prism
  layers) or that touches any neighbour over only part of one of its faces, naming the two bodies. Sweeping touching
  bodies together (stacked turns, side-by-side busbars) and partial contacts may come later as their own steps.
  The same rule holds between solids of one multi-solid reference (call 10).
- The sweep must be recognised (5.2), with the reason when not.
- 2D Study: Swept Body is refused (a 2D Study is already one section).

## 6. 3D prism layers (Skin Layer `QuadLayers` in 3D)

Today `QuadLayers` in a 3D Study is a Validate warning and ignored. After this work, in 3D:
- the body's surface (the faces the existing spec 5.2 calls real surface, cut faces excluded) is meshed first with
  triangles at δ / ElementsPerDepth near the surface size rules of today's graded skin;
- prism layers grow inward from that surface mesh: first layer δ / ElementsPerDepth, ratio 1.2, total LayerDepth · δ
  (gmsh `extrudeBoundaryLayer` on the surface mesh with negative heights, or built by hand by moving surface nodes
  along averaged inward normals; the Stage 5 spike picks);
- the core is filled with tetrahedra that meet the top of the layer;
- the body joins its neighbours by section 4.

Corners: smooth bodies only, as in 2D (the user's 2026-11-15 rule). A body with a sharp edge on its layer surface gets
today's graded tetrahedra, a Validate warning and a mesher note. A body that is a sweep should use Swept Body instead;
Validate says so when `QuadLayers` is on for a body it can recognise as a sweep.

## 7. Spikes

### 7.1 Stage 1 spike: joining a hand-made mesh

Throwaway gmsh script, two shapes: a straight 10 × 4 × 40 mm bar in an air box, and a round wire r 0.45 mm along a
10 mm-pitch helix (litz1's strand) in an air box. Try section 4's option 1 (pre-mesh plus `MeshOnlyEmpty`), then
option 2 if 1 fails. Pass: one conformal mesh (no free faces inside the domain, every shared face's nodes shared),
gmsh quality as today's meshes, and the air's element count and time within a few percent of meshing the air around a
tet-meshed body. Record the result in this spec, as in the refinement spec.

**Spike result (2026-11-17): joining a hand-made mesh.** gmsh 4.15.2. Bar 10 × 4 × 40 in a 60 × 60 × 100 box at
size 6, 10 × 4 quads × 20 steps (800 hexahedra); litz1 strand (r 0.45, helix r 1.2, pitch 10, 1.5 turns) in a
6 × 6 × 20 box at size 0.6, section 72 quads in layers plus 122 triangles × 60 steps (4320 hexahedra, 7320 prisms).
Reference: the same air around the body meshed with tetrahedra at its surface element size (bar 1.44, wire 0.19).
- Option 1 works: one conformal mesh on both shapes (no free face inside the domain, all 642 / 1709 body surface
  nodes shared with the air), the hand-made nodes unmoved. gmsh closes each quad of the body's surface with its own
  pyramid (640 / 1584) on the air side; no splitting or `quad_pyramids` needed. It takes four things:
  `setTransfiniteVolume` on the body (else gmsh's Delaunay fills the body with tetrahedra: it treats only transfinite
  or extruded volumes as void); the body's points, curves, faces and volume hidden with `Mesh.MeshOnlyVisible` as well
  as `Mesh.MeshOnlyEmpty` (gmsh counts a dimension as meshed only when every visible entity was meshed by gmsh itself,
  else `generate` re-meshes curves and wipes the faces); the hand mesh added one dimension at a time, points and curves
  then `generate(1)`, faces then `generate(2)`, volume then `generate(3)` (with the volume in, `generate(3)` skips the
  1D and 2D meshes of the other entities); and `Mesh.Renumber = 0` with node tags taken from `getMaxNodeTag` at each
  step (gmsh numbers its new nodes from there).
- Air: bar 12.9k elements against 22.6k for the tetrahedral body, wire 28.0k against 46.3k (fewer: gmsh sizes the
  air from the longest edges of the body's surface quads). Meshing time bar 0.35 s against 0.24 s, wire 1.5 s against
  0.7 s (three `generate` calls; the reference also meshes the body), plus 0.03 / 0.9 s to classify the nodes.
- Quality is gmsh's quad-to-tet transition, exactly as with today's Transfinite Body (same bar meshed by gmsh's own
  transfinite hexahedra: 12.8k elements, min SICN 0.0005): air min SICN 0.015 (bar) and 0.003 (wire) against 0.30 and
  0.26 for the tetrahedral body, the 1 % quantile 0.15–0.19 against 0.37; the bad tetrahedra are the ones between
  neighbouring pyramids. `Mesh.OptimizePyramids = -0.6` (apex pushed out before the 3D mesh) raises the minimum to
  0.11 and 0.05, no element below 0.1 on the bar, 4 on the wire; other values (-0.15 to -1) and more optimisation
  passes do no better.
- Option 2 (`quad_pyramids` + `mesh_region` around the frozen body, for comparison) is also conformal and meshes
  better near the body: min SICN 0.29 (bar) and 0.12 (wire), 1 % quantile 0.35–0.36, but with more air elements
  (28.1k and 55.4k, +24 % and +20 % on the tetrahedral body) in about the same time.
- The helix: OCC's pipe is a B-spline approximation. With the Frenet trihedron the lateral face is within 6e-5 of the
  screw copies, the seam and the far vertex within 2e-4 and 4e-4 (the tolerance 1e-6 × model size is 2e-5), so nodes
  are classified with a looser tolerance (2.5e-5 × model size, 5e-4 here) and projected onto their entity
  (`getClosestPoint`). gmsh's default pipe trihedron (`DiscreteTrihedron`) twists the seam around the strand
  (about 70° every 10 steps), so no screw copy of a section node follows it: the 3D mesh still joins (the seam gets no
  line elements), but the far vertex gets no node. A circle lists no boundary points (`getBoundary`), so the seam's
  vertex is matched to the circle by position.
- Not passed as written: the min SICN check (tetrahedral body minus 0.05) fails for both options on the wire and for
  option 1 on the bar, and neither option's air element count is within 10 % of the tetrahedral body's.

**Spike result (Stage 3, 2026-11-17): helices from FreeCAD pipes.** FreeCAD 1.1, gmsh 4.15.2, shapes built as
litz1 was (Part::Helix as the Body's BaseFeature, sketch attached `FrenetNB` to its Edge1, PartDesign AdditivePipe,
Refine on): the strand (helix r 1.2, pitch 10, height 15; circle r 0.45) in `Standard` and `Frenet` mode, the same
with a Part Sweep (`Frenet = False`), a coil turn (rectangle 2 × 4, helix r 20, pitch 6, 1 turn) in `Frenet` and
`Standard` mode. litz1 itself, opened read-only, is a `Frenet` pipe of height 12 (1.2 turns), not a
`DiscreteTrihedron` one (that was gmsh's own pipe in the Stage 1 spike); rebuilt the same way it gives the same volume
(9.56085902) and fits, recognises and meshes like the Frenet strand.
- **The fit.** The lateral-edge fit (axis from the tangents, `(T_i − T̄)·axis = 0`, circle fit of the projection,
  unwrapped angle, rise) is exact on Frenet pipes (strand 540°, 15.000000, error 9e-9; coil 360°, 6.000000, error
  6e-9 on each of its four edges, so the whole turn is found) but fails wherever the profile turns against the
  Frenet frame (`Standard` and Part Sweep strand: 555.4°, error 0.55 mm; `Standard` coil: 0.28–0.33 mm). A better fit,
  used for everything below: the kinematic one from the side faces. Each sample (point p, normal n) gives the row
  `[p × n, n]`, and the screw (ω, v0) is the null vector of those rows (SVD, smallest singular value about 1e-8
  against 0.24 for the next, so it is unique). Axis ω/|ω|, rise per radian h = axis · v0/|ω|, origin axis × v0/|ω|
  (shifted to the point nearest the start face's centre), advance from the end faces' centres, angle = advance / h,
  whole turns included. It is exact on both modes for a round profile (strand `Standard` and `Frenet`: axis Z, pitch
  10.000000, 540.000000°, 15.000000; coil `Frenet`: pitch 6.000000, 360.000001°), 2.9e-5 off on the Part Sweep strand
  (its B-spline is coarser). A revolve (h = 0) still needs Stage 2's angle from the end faces.
- **Checks.** Volume check error 1e-9–1e-8 (Part Sweep 4e-6). Side-face invariance (the start face's boundary moved
  by the screw at 37 fractions, distance to the side faces; side-face samples moved back to the start plane,
  distance to the start face): 1e-8–1e-7 on PartDesign pipes, 3e-5 on the Part Sweep. The `Standard` coil turn
  really twists: invariance 0.55 mm, kinematic residual 5e-3, the start face moved by the screw 0.56 mm off the end
  face. Its volume check passes (6e-7): a twisting profile sweeps the same volume, so the volume check cannot catch
  it; the invariance check must.
- **Option (b) on the `Standard` strand.** Its seam's far vertex is 0.55 mm (76°) from the screw image of its start,
  and the Stage 2 mesher path (with throwaway helical stations) fails: "its swept mesh has no node on the corner".
  Rebuilt from the start face's outer wire and the fitted piece (`Part.makeHelix` placed on the piece,
  `BRepOffsetAPI.MakePipeShell` in Frenet mode, tolerance 1e-7): volume 2.7e-8 relative, two-way distance of face
  samples 5.9e-6 (0.35 × 1e-6 × size), and it meshes conformally: no inner free face, 3306 hexahedra and 1406 prisms,
  air 24.5k tetrahedra and 1276 pyramids, air min SICN 0.0095 (1 % quantile 0.026), body 0.055, the same as the
  original `Frenet` strand. `Part.Wire(helix).makePipeShell([wire], True, True)` (default tolerance) is 7.6e-6 off
  and 7.7e-7 in volume: also within, but less exact. The Part Sweep strand's rebuild is 3.6e-5 off, outside
  1e-6 × size (its own surface is 3e-5 off the screw copies), so by the rule it would be refused, though the mesher's
  tolerance (2.5e-5 × size, 4e-4 here) would take it.
- **Decision: (b).** The `Standard` mode is PartDesign's default, so most pipes a user makes have a twisting seam;
  with (b) the round ones mesh, with (a) they would be refused. The rebuild equals the original well within
  1e-6 × size and meshes conformally where the original does not. A non-round profile that twists (the `Standard`
  coil) fails the invariance check and is refused either way; (b) is used only when the side faces are invariant
  and the rebuild passes the two-way distance check. OCC booleans cannot measure the difference (cut volumes of 2 ×
  the solid); use the distance check.

**Spike result (Stage 4, 2026-11-18): swept cells in symmetric Studies.** FreeCAD 1.1, gmsh 4.15.2, the jobs written
by `write_job` with the grouped refusal patched in memory and meshed by `mesher.py` with in-memory patches. Cases:
litz1 (a copy; the strand the cell of 6 rotations, Padding Box air 3 mm at 0.6, size 0.3, Skin Layer 100 kHz copper,
2 δ, path 0.4, section 0.2); a 2 × 4 ring sector at rc 20 revolved 45° (size 1, Skin Layer 10 kHz, Padding Box air
6 mm at 4) as the cell of 8 rotations, of 4 rotations × mirror, the same mirrored with a non-symmetric pentagon section
(prisms), and with a tetrahedral iron sector (r 21..25) as a second cell beside it.
- **The swept mesh never reaches the cell's `generate`.** `mesh_cell` builds a copy of the cell job and
  `_generate_cell` passes another, so `swept_tags` / `swept_add` are lost and the cell is silently meshed with
  tetrahedra (litz1: 9906 per strand, no note). With them passed on, every case meshes as swept.
- **Real faces in the cell model:** `real_boundary` sees none (litz1, sector), only the face against the iron cell in
  the iron case; no end is graded. So the skin silently disappears (litz1 1862 prisms per strand instead of 3612
  hexahedra and 1462 prisms; sector 128 hexahedra instead of 768). With every face but the seams real (a stand-in for
  `free_faces`) the sections get the skin and litz1's ends are graded.
- **Seams (S):** made periodic by gmsh before the hand mesh is in, they fail at `generate(1)` ("Cannot find periodic
  counterpart of node 2 of curve 4 on curve 3"). Leaving the swept faces out works for a swept cell alone, but not
  beside the iron cell: the iron's periodic seam face carries its periodicity to the curve it shares with the swept
  body, and fails the same way. Every `setPeriodic` of the cell model made after the hand mesh's points and curves are
  added (before `generate(1)`) works in all cases, with the swept faces left out or in; gmsh never touches the hand
  mesh (every face's elements are faces of the swept cells, no other node). Decision: leave the swept faces out of
  `_periodic` and `pair_images`, and defer all other pairing of the cell model until after the hand points and curves.
- **Copies and air:** in every case the copies join (no facet in three elements) and the full mesh has no free face
  inside. Air min SICN: litz1 0.126 (none below 0.1; 208k tetrahedra, 8232 pyramids; body 21672 hexahedra, 8772
  prisms), sector 0.032 (68 below 0.1, all on the ring's outer rim edges, none at a seam; 50.5k tetrahedra, 3584
  pyramids), mirrored 0.018–0.032, pentagon 0.029 (62), iron 0.211 (none). Without the skin the sector's air is 0.26.
- **Mirror (M):** both seams of the mirrored sector lie on the mirror planes, so no pairing is needed; hexahedra and
  prisms (pentagon section) keep positive volumes and the seams are conformal as built.
- **Free side (P):** `quad_pyramids` closes the copies' quads (8232 / 3584 pyramids), as for Transfinite Body cells.
  In the iron case the iron cell, meshed in the cell model, gets gmsh's own pyramids on the shared quads.

### 7.2 Stage 5 spike: prism layers

Sphere, a rounded busbar (r ≥ 3δ edges), and a disc with sharp rims, in an air box. Try `extrudeBoundaryLayer` and the
hand-made inward copy. Record which works and where it fails; if neither gives valid prisms on smooth bodies, work
stops and the user decides.

Result (2026-11-18, throwaway scripts, gmsh 4.15.2; δ 1, 2 per depth, layer 2 δ, so 3 layers 0.5 / 0.6 / 0.72, in an
air box):
- **Hand-made inward copy works and is chosen.** gmsh meshes the body's curves and real faces in the main model with
  the body's volume hidden. Each surface node moves inward along the angle-weighted mean of its triangles' outward
  normals, giving prisms. A sub-model meshes the core with tetrahedra: the inner surface goes in as a discrete
  surface, and a `geo` surface loop and volume on it work, while `addDiscreteEntity(3)` is never meshed. The prisms
  and core tetrahedra go onto the body's volume; then gmsh meshes the rest with `MeshOnlyEmpty`.
  - sphere r 5: 2256 prisms, min SICN 0.563; core 972 tetrahedra, min SICN 0.276; air min SICN 0.306. No unmatched
    faces, 0.6 s.
  - busbar 20 x 10 x 8, all edges filleted r 3: 8088 prisms, min SICN 0.397; core min SICN 0.15; air min SICN 0.297.
- **Cut faces work when flat.** Spike 7.2b: a wire through the model boundary, and a quarter ring with two cut faces
  through its axis. At a rim node (on a curve between a real face and a cut face) the normal is projected into the cut
  plane. The cut face gets the prisms' side quads and a cap inside the inner rim: a `geo` plane surface, its lines
  with 2 nodes each, meshed in its own sub-model. The core loop is the inner surface plus the caps.
  - wire: prisms min SICN 0.628, core 0.12.
  - quarter ring: prisms 0.588, core 0.088.
  - Both had no unmatched faces and air min SICN about 0.29.
- **`extrudeBoundaryLayer` is not used.** It needs `classifySurfaces` and `createGeometry` on a copy of the surface.
  These re-mesh the surface, so the layer no longer matches the air's faces (1668 prisms instead of 2256 on the
  sphere). Its busbar is worse too (min SICN 0.048), and on the disc it fails.
- **Where it fails:**
  - Sharp edges fail as expected. On the disc (rims at 90°), the core sub-model reports "PLC Error: A segment and a facet
    intersect". On a wire ending in air, the worst angle between a node's normal and its faces is 47° and every prism
    is inside out.
  - A busbar 20 x 8 x 5 with r 2.4 fillets fails although r > the layer: 59 prisms are inside out on the 0.2 mm flat
    strips between fillets, and the core reports overlapping facets. So a smoothness check before the build cannot
    be the only guard. The built prisms are checked (all corner volumes positive) and the core fill must succeed;
    otherwise the body gets today's graded tetrahedra and a note.
- The surface triangles in the spike were 2 × the first layer; Stage 5 keeps the spec's size, today's graded skin
  sizes on the surface (section 6).

Probe for cells (Stage 5 Task 4, 2026-11-18, gmsh 4.15.2): the quarter round ring R 20, r 3 as the cell of 4 copies
about Z, its two cut discs a seam pair. Curve-only pairing was tried: the seam faces are left out of the periodic
pairing (hidden, filled by hand at d = 3), and `setPeriodic(1, slave rim, master rim, T)` on the rims, set before gmsh
meshes the curves. gmsh accepts curve pairing on faces that are not paired; the rims come out node for node (39 nodes
each, at most 4e-15 apart), the master's hand-made cap moved by T matches the slave's rim, and generate and the copy
succeed: prisms in all 4 copies, the same count in each, every seam node shared, no unmatched faces. Curve-only pairing
is used. The face pairing (`setPeriodic(2, ...)`) is still needed in one place: when a layered cell falls back (N3,
N4), its cuts are shown again for gmsh to mesh at d = 3, and without it the two seam faces are meshed apart, which the
seam check refuses; so the fallback sets the face pairs just before it shows them.

## 8. Stages and the review catalogue

As before: each stage ends with catalogue rows in `experiments/refinement_catalogue` (new ids `SW-..`, `PL-..`), the
user reviews them, and the next stage starts after their review. Each row shows the new mesh next to today's (graded
Skin Layer), element counts and a cut picture. Add-on tests green, lint clean, smoke test when GUI code changes.

| Stage | Built | Rows (ids are proposals) |
|---|---|---|
| 1 | Spike 7.1; Swept Body item, panel, command, icon; straight sweeps in ordinary Studies | SW-01 rectangular busbar in air, 1 kHz skin (graded grid section); SW-02 round straight wire, quad-layer section; SW-03 thin plate (extruded rectangle) with skin; SW-04 straight sweep with no Skin Layer; SW-05 refusals (not a sweep, Air Region, with Transfinite Body, touching another swept body, partial contact); SW-12 busbar end against a tet-meshed terminal |
| 2 | Revolved sweeps, closed rings | SW-06 winding turn ring of rectangular section; SW-07 toroidal round conductor; SW-08 a 90° revolved busbar bend |
| 3 | Helices and joined pieces | SW-09 single litz strand (litz1's helix); SW-10 coil turn with pitch; SW-11 bent busbar: line + arc + line |
| 4 | Symmetric Studies | SW-S1 litz1 (6 strands, the strand as the cell); SW-S2 a winding sector as a cell |
| 5 | Spike 7.2; 3D prism layers | PL-01 round straight wire as a non-sweep comparison; PL-02 rounded busbar; PL-03 sphere; PL-04 disc with sharp rims (falls back, warning) |

## 9. Testing

- Unit tests (GUI-free): sweep recognition on FreeCAD shapes built in the test (extrusion, revolution, helix pipe,
  line-arc-line pipe, a B-spline pipe refused, a loft refused); job keys written only when the item exists; property
  defaults; validation messages.
- Mesher tests: the swept volume mesh of a known profile has the expected node and element counts, positive
  Jacobians, no duplicate nodes on a closed ring; the joined mesh with air has no internal free faces.
- A job without the new keys gives the same mesh as before.
- Catalogue rows as the end-to-end check.

## 10. Left to the builder

- Tolerances for recognising a screw motion and matching end faces.
- Where a closed ring is cut for its profile.
- Transfinite progression vs bump for the rectangular section grid.
- Panel layout and message wording in the house style of `validation.py`.
- Icon artwork in the existing set's style.

## 11. Calls I made (for the user to check)

1. Swept Body is a separate item (approach A); the cross-section takes the body's existing Skin Layer instead of new
   skin settings on Swept Body.
2. Paths are chains of lines, arcs and helices; free-form paths are refused this round.
3. Recognition works on the shape, not the CAD history.
4. Rectangular sections get a graded structured grid instead of quad layers (gmsh's layers fail at corners).
5. Swept bodies may not touch the sliding interface surface this round.
6. 3D prism layers keep the 2D rule: smooth bodies only, otherwise today's graded tetrahedra plus a warning.
7. From the builder check: stations are graded toward an end face that is real surface (not a cut and not a face
   shared with another conductor): first step δ / ElementsPerDepth, ratio 1.2, until PathSize. A busbar ending in
   air gets its end skin too.
8. From the builder check: `QuadLayers` already ticked in a 3D Study (today ignored, with a warning) becomes active,
   with no migration. The anti-goal "same mesh as before" covers Studies without the new methods; a Study with
   QuadLayers ticked in 3D asked for layers.
9. From the builder check: in Studies with Symmetric Groups, Swept Body and 3D prism layers apply to cells only; on a
   free object Validate refuses them, as 2D quad layers are refused there today.
10. From the builder check: a reference may be one FreeCAD object holding several solids (a coil as one compound of N
    turns, a bundle of strands). Each solid is recognised and swept on its own; the job entry carries a list of
    `{"profile", "pieces"}` per solid under one MAT_ID; `StartFace` may name one face per solid.
11. From the builder check: if the Stage 1 spike finds neither joining option conformal and within the targets, work
    stops and the user decides (as for the Stage 5 spike).
