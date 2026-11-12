# One Study, Whole Document: Study Geometry Design

Date: 2026-11-12
Branch: `feature/symmetric-rules`
Status: design, not implemented

## 1. Why

Today a Study meshes only the bodies the user ticks in its *Main geometry* tree (and, when sliding, its *Moving
geometry* tree). Symmetric Studies added more ways to say the same things, so a symmetric sliding Study now has
four overlapping mechanisms for "what is meshed" and "what moves":

| Question | Mechanism today |
|---|---|
| Is this body meshed? | ticked in Main or Moving geometry (Unassigned / Container / Manual modes) |
| | a Symmetric Group's `Cells` — meshed automatically, and **refused** if also ticked |
| | an Air Region's Custom `Source` — meshed as air, and refused if ticked |
| Which side moves? | ticked in the Moving geometry tree |
| | a Symmetric Group's `Side` property |

The tree does not show what will be meshed, and the user cannot remember why opt-in was chosen. The opt-in list
existed for three reasons (2026-10-02 Study-setup plan): several Studies in one document, the fixed/moving split, and
bodies that are drawn but must not be meshed. This design removes the first, replaces the second with a geometric
rule, and keeps the third as an opt-out.

The user's goal: a consistent, simple model. The add-on is still experimental and has not shipped, so there are no
customer documents to migrate.

## 2. Decisions (the user's)

1. **One Study per document.**
2. **Everything is meshed by default.** Every body of the Study's dimension in the document is meshed, including
   bodies added later. The user excludes bodies by unticking them.
3. **Cut tools and the Air Region's Custom source are left out automatically.** These are the user's common cases.
   Other cases (helper shapes, imported bolts and covers, old versions) are excluded by hand.
   - **Cut tools are never meshed and are hidden from the Study tree.** To mesh a body that is a cut tool (the coil
     in `Air = Cut(AirBox, Coil)`), the user makes an `App::Link` to it by hand; the link is meshed as a body. The
     tree gives no hint on cut-tool rows (there are none).
   - **Validate warns only when a cut tool has an assignment** (a Material or an item on it).
4. **The Sliding Interface decides what moves** (option 3 of three discussed). Each interface says once which side
   moves; everything on that side is moving. The Moving geometry tree and the Symmetric Group `Side` property go away.
5. **No migration.** Old properties are removed; experimental files saved before the change open with everything
   included and may need their setup redone.
6. **A Material (or other item) left on a body that a Cut or Fuse is now made from gets a Validate warning.** The
   add-on does not move the assignment automatically.

## 3. Goals, non-goals, anti-goals

Goals
- The Study panel's geometry tree is the one place that shows what is meshed and, when sliding, what moves.
- Drawing a new body needs no extra step for it to be meshed.
- One rule for "what moves", in symmetric and non-symmetric Studies alike.

Non-goals
- Several Studies per document (variants and 2D/3D pairs become separate `.FCStd` files; they can share a simulation
  folder because 2D and 3D meshes have different file names).
- Fixing FreeCAD's face renumbering: a face or edge pick can still point at another face after a shape edit.
- Moving assignments to a boolean result automatically.
- Linear or Axial gap sliding with Symmetric Groups (still refused, unchanged).
- Converting old files.

Anti-goals (a failure even if it works)
- A body meshed or dropped without the tree saying so. Every body the tree lists is either ticked, or unticked with a
  visible reason. Cut tools are the one deliberate exception: they are not listed (decision 3), and the
  assignment warning (section 6) catches the case where the user meant to mesh one.
- A hidden cut tool filling its hole with a body. The add-on ignores visibility, so this is exactly what
  whole-document meshing would do without the automatic exclusion.

## 4. What the Study meshes

### 4.1 The Study's bodies

`study_bodies(study)` becomes: every body that `geometry.tree(doc, dimension)` lists today (top-level and inside
Parts/Groups; PartDesign Body as one; sketches, Study objects, bodies of the other dimension and bodies another body
is made from left out), minus:

- **Excluded by the user**: a new Study property `Excluded` (`App::PropertyLinkListGlobal`, hidden, edited in the
  panel).
- **Cut tools**: a body that is the `Tool` of a `Part::Cut` or of a Part Join Cutout (`FeatureCutout`). Not the
  `Source` of a Mirror or the original of a Draft Clone: those are real bodies and stay in, as today (see `OUTSIDE` in
  `geometry.py`). A Cut whose `Tool` is an `App::Link` leaves out the link (which is not a body), not the object it
  links: `Air = Cut(AirBox, CoilLink)` meshes Coil, as `test_a_link_to_the_tool_of_a_cut_keeps_the_tool_a_body` pins
  today. When the `Tool` is a Part or Group, the bodies inside it are cut tools. *(My call.)*
- **Air sources**: the `Source` of an Air Region in Custom mode.
- **Cell objects of a Symmetric Group**: meshed by their group (unchanged), listed under it (4.3).
- **Drawings of a Symmetric Group** *(my call, found while planning)*: a body made from a cell object (a cell's
  `geometry.inputs` chain, following also the inputs `OUTSIDE` skips: the Mirror / Polar Array / Fragments chain that
  "Read from drawing" reads) is the drawing of that group's copies. Meshing it would put a body over the copies, so it
  is left out and the tree shows it unticked and disabled: "drawing of Symmetric Group Stator".

A cut tool cannot be ticked back in. To mesh it, the user makes an `App::Link` to it (4.1.1).

Validation of each body is unchanged (`geometry.collect`: 3D needs solids; 2D needs planar faces in one plane, XY or
ZX). A body of the right kind that fails those checks is an error naming it; the fix is to exclude it.

#### 4.1.1 Links are bodies (new)

Today `geometry.collect` and `geometry.tree` refuse or skip `App::Link`. They become bodies when they link one body:

- A top-level `App::Link` (or one inside a Part/Group) whose linked object is a body (a `Part::Feature` or PartDesign
  Body, not a container, sketch or Study object) and that is not a link array (`ElementCount` 0) is a body of the
  Study: listed and ticked in the tree, excludable, meshed with its own shape where the user sees it (link placement
  and the containers' placements included; `global_shape` must handle it).
- The linked object is **not** an input of the link: add `App::Link`'s `LinkedObject` to `OUTSIDE`, like a Draft
  Clone's original ("a copy placed elsewhere"). So linking a visible body somewhere else keeps the original meshed
  too; a link left at the original's place overlaps it, which `_body_overlaps` reports. For a cut tool the original
  is not meshed anyway (it is a cut tool).
- Materials, Excitations, Mesh Sizes and the other items can be assigned to the link, including face, edge and
  vertex picks on it (`Link.Face3`); highlight and picking (`pick_body`, `owning_body`, `ItemGate`) work on it.
- A link that is not one body (a link to a Part or Group, a link array, a link to a non-geometry object): Validate
  warns that it is not meshed. *(My call: a warning, not an error, so a link kept for display does not block the
  mesh.)*

Other objects that are not bodies (spreadsheets, sketches, Draft dimensions, FEM mesh results, origins) are ignored
silently, as `geometry.tree` does today. *(My call while planning: a warning for each would be noise; links are the
one case where the user expects geometry.)*

### 4.2 Properties removed

From Study: `MainMode`, `MainSource`, `MainObjects`, `MovingMode`, `MovingSource`, `MovingObjects`.
From SymmetricGroup: `Side`.
`SIZING_PROPERTIES` (what refreshes the Air Regions' `SizedBy`) becomes `Excluded` alone: the bodies that size the
air no longer depend on `Movement` or on the moving side. Bodies drawn later are picked up by
`validation.refresh_padding`, as for a Container source today.

No conversion code: a file with the old properties keeps them as dead properties or drops them on restore — the
builder's choice, but nothing reads them.

### 4.3 The Study panel tree

One tree, titled *Geometry*, replacing the Main/Fixed and Moving trees.

- Rows: Parts and Groups as in FreeCAD's tree (tristate), bodies as leaves — as `geometry.tree` gives today.
- Ticked = meshed. Unticking adds the body (or each body under a container) to `Excluded`; ticking removes it.
- Cut tools are not shown (decision 3).
- The Custom air source is shown unticked and disabled, with the reason beside it: "air shape of Air".
- Each Symmetric Group appears as a row with its cell objects under it, ticked and disabled, with the note "meshed by
  Symmetric Group Rotor". To leave a cell out the user edits the group.
- When the Study slides, rows on the moving side carry the label "moving" (bodies and group rows).
- The count line stays ("Included: N solids (M objects)").
- The `ValidationPanel` and diagnostics below the tree are unchanged.

The validation error "X is a cell object of Symmetric Group G and is also in the Main geometry" goes away: a cell is
never one of the Study's free bodies.

### 4.4 What moves

Each Sliding Interface gets a property saying which side moves:

| Kind | Moving side choices | Default |
|---|---|---|
| Rotational | Inside / Outside the radius | Inside |
| Axial gap (disc at z = Position) | Above / Below (z greater / smaller than Position) | Above |
| Linear (plane at Position along NormalAxis) | Positive / Negative side along NormalAxis | Positive |

*(Names and storage — one enumeration re-filled per Kind, or one per Kind — are the builder's call.)*

Rule: the interfaces cut the air into pieces (`airshapes.cells`, as today). A piece is **moving** if it is on the
moving side of every interface it borders. Each interface separates a moving piece from a fixed one; if the settings
make a piece moving by one interface and fixed by another, Validate reports it: "Sliding Interfaces A and B disagree
about the side of the air between them: change the moving side of one."
Examples: a motor with one rotational interface, Inside → the bore moves. A double-air-gap machine with interfaces at
r = 30 (Outside) and r = 50 (Inside) → the ring between them moves. A linear mover between planes y = −5 (Positive)
and y = 5 (Negative) → the slab between them moves.

A body (free object) is moving if it lies in a moving piece (`airshapes.cell_of`, as today). A body crossing a sliding
surface stays an error.

**Symmetric Studies** (Rotational only, no Air Region pieces needed): a group is moving if its drawing is on the
moving side of the interface radius; a free object likewise. A group or free object whose drawing crosses the radius is
an error (as today for bodies). This replaces `SymmetricGroup.Side` everywhere it is read: `objects.part_key`,
`validation._air_off_moving`, `_groups`, `_part_materials` (part keys `fixed|…` / `moving|…`), the job writer's group
entries and slide block.

**Part keys lose the side** *(my call)*. Today a part Material's `PartKey` is `side|name`, re-keyed only when the
group panel's OK is pressed. With the side computed from geometry, any change to the interface Radius, its moving side,
`Movement` or the drawing would orphan every part Material (and re-keying through `sync_parts` recreates them, losing
Potential and custom names). So `PartKey` becomes the part name alone. The side is not needed for uniqueness:
`_part_materials` already refuses one part name on both sides, and keeps doing so with the side computed from geometry.
No migration (decision 5): old `fixed|…` / `moving|…` keys are not converted.
A group whose side cannot be worked out (no Sliding Interface yet, or its drawing crosses the radius) gets the
existing Validate error for that case; nothing else depends on its side.

Removed errors: "No body is in the moving geometry" becomes "No body is on the moving side of the Sliding
Interfaces". "Part of the air next to … holds no body; its side is unknown" goes away (the side is now always known).
"Moving body X and fixed body Y are on the same side" goes away (sides come from geometry).

The Air Region rules are unchanged: non-symmetric sliding Studies split it into fixed and moving halves by the
pieces; in symmetric Studies it is all on the fixed side and must keep clear of the moving copies and the surface.

## 5. One Study per document

- `NewStudy.IsActive` is false when the document already has a Study.
- `active_study()` becomes the document's Study (`find_study`); the selection tracking and the "selection spans two
  Studies" case in `taskpanels.active_study` go.
- Validate refuses a document with more than one Study (a safety net for copy-paste between documents): "This
  document has two Studies, A and B: delete one." Generate mesh is refused with it.
- `owner_study` stays: items still find their Study by group membership.
- Scratch folder path keeps the Study Name segment *(my call: no churn, harmless)*.

## 6. Edits after setup (validation messages)

Assignments link to the object, not its Label, so renaming keeps Materials, items and MAT_IDs (unchanged). The cases
that change:

- **New body**: meshed at once; Validate warns "No material: NewBody" (existing warning).
- **Body consumed by a boolean** (Box with Material Iron is cut; Cut is now the meshed body): Validate warns
  "Material Iron is on Box, which Cut is now made from: assign it to Cut." The same warning, worded for the item,
  replaces today's "… is not used for Box: not in the main geometry" for Mesh Sizes, Excitations, Transfinite and
  Recombine items. Not moved automatically.
- **Cut tool with assignments** (the coil in `Air = Cut(AirBox, Coil)` has Material Copper): Validate warns
  "Material Copper is on Coil, the tool of Air_Cut, which is not meshed. To mesh it, make a Link to it." (and the
  item-worded variant). This is the only message about cut tools; a cut tool with no assignment is silent. *(The
  "make a Link" sentence in the warning is my call; the tree itself gives no hint.)*
- **Excluded body with assignments**: Validate warns "Material Iron is on Box, which is excluded from the Study."
  (and the item-worded variant).
- **Body moved across a sliding surface**: its side follows by itself; crossing the surface is an error (unchanged).
- Deleted body, renumbered faces, changed group cells: unchanged.

The assignment gate (`objects.assignment_problem`, `ItemGate`) refuses bodies that are not meshed — excluded,
cut tool, air source or consumed — with the reason: "Box is excluded from the Study: tick it in the Study panel." The
`NO_MAIN_GEOMETRY` message and its "select the Study" redirect go; a document with no bodies has nothing to pick.

## 7. Things that read the old properties

Every reader of the removed properties changes to the new rule. Known places:
- `objects.py`: `study_bodies`, `_main_bodies`, `air_sizing_bodies`, `assignable`, `assignment_problem`,
  `SIZING_PROPERTIES`, `make_symmetric_group(side=…)`, `part_key`.
- `geometry.py`: `region`, `stored`, `setup` (the fixed/moving split and the "assigned to both" error), `whole`,
  `collect` and `tree` (cut tools out, links in), `OUTSIDE` (`App::Link`'s `LinkedObject`), `global_shape` (links).
- `validation.py`: `validate`, `free_bodies`, `_skipped_picks` (no Manual mode any more; drop or reword), `_slides`,
  `_free_cells`, `_groups`, `_air_off_moving`, `_part_materials`, `_links`.
- `jobwriter.py`: `check`, `write_groups`, `write_job`, `write_slides`.
- `airshapes.study_plane`.
- `taskpanels.py`: `StudyView` (tree), `SymmetricGroupPanel` (Side combo removed; show the computed side read-only
  *(my call)*), `SlidingInterfacePanel` (new moving-side choice), `ItemGate`, `active_study`.
- `commands.py`: `gate`, `NewStudy`.
- Tests: helpers that tick geometry (`include(...)` in `test_study.py`, ~100 uses; `cases.py`, `symcases.py`,
  `test_air.py`, `test_studymaterials.py`, `test_symmetric_groups.py`), the three multi-Study tests in
  `test_study.py` (delete), `gui_smoke.py`. The tests that pin "the tool of a Cut stays a body"
  (`test_the_tool_of_a_cut_stays_a_body` in `test_study.py`, `test_the_tool_of_a_join_cutout_stays_a_body` in
  `test_inputs.py`) are reversed; `test_a_link_to_the_tool_of_a_cut_keeps_the_tool_a_body` keeps its meaning.
- Example builders: `tests/freecad_addon/build_examples.py`, `experiments/symmetric_catalogue/build_catalogue.py`
  (rerun after the change; the catalogue should still pass 91 of 91 plus `motor_sliding-air`).

## 8. Left to the builder

- Storage of the moving-side setting and its labels per Kind.
- Whether dead properties are removed on restore.
- Tree widget details (columns vs. text for the reason and "moving" labels).
- How exclusion of a container is stored (each body under it, or the container itself) — as long as a body added
  later inside an excluded container is also excluded *(my call: excluding a container means its contents, now and
  later)*.
- Test structure.

## 9. Verification

- `pixi run -e addon test-addon` passes.
- GUI smoke (`tests/freecad_addon/gui_smoke.py`) passes.
- The symmetric catalogue rebuilds with the same results.
- New tests at least for: whole-document inclusion and a body added later; cut tool not meshed and not in the tree
  (a Cut whose tool is not meshed into the hole); a Link to a cut tool meshed as a body, with a Material and a face
  pick on it; a link to a Part refused with a warning; the cut-tool assignment warning; Custom air source auto-excluded; exclusion of a body and of a container; the moving side
  for one rotational interface, a double air gap and a linear slab; disagreeing interfaces; a symmetric sliding Study
  with the rotor group and a free shaft both moving without any per-object setting; the consumed-body Material
  warning; a second Study refused.
