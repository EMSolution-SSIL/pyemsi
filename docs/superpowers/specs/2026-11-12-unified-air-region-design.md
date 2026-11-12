# One Air Region for Every Study: Requirements and Design

Date: 2026-11-12
Status: implemented on feature/symmetric-rules
Branch: written on `feature/symmetric-rules`
Changes: `2026-11-09-symmetric-mesh-rules-design.md` (sections 2, 3, 4.4, 6, 8; listed in section 9 here) and
`2026-10-20-air-region-and-sliding-design.md` (the Air Region is no longer for non-symmetric Studies only).

## 1. Why

Today the outer air is made in two different ways, and each works in one kind of Study only.

| | Non-symmetric Study | Study with Symmetric Groups |
|---|---|---|
| Outer air | **Air Region**: Box, Sector or Custom, Manual or Padding | An ordinary body with the Air Material, drawn by the user |
| The other way | A drawn body that overlaps others is refused (`validation._body_overlaps`) | An Air Region is refused (`validation._groups`) |
| What wins an overlap | The bodies win over the Air Region | The copies win over every free object |

So a user learns the Air Region, switches to a symmetric Study, and finds that it is refused at Validate, not when it is
added. The cylinder that works in D-04 is an overlap error in a non-symmetric Study, and Padding ("20 % round everything")
is not available with symmetry at all.

**The goal:** one way to make the air, and one rule, in every Study: *the Air Region gives way to everything; bodies only
touch each other.*

## 2. Decisions (the user's, 2026-11-12)

1. The Air Region comes into Studies with Symmetric Groups and behaves as in a non-symmetric Study. Drawing your own air
   is the Air Region's **Custom** shape, as in a non-symmetric Study.
2. **Free objects may only touch the copies**, as bodies may only touch each other. Only the Air Region gives way. A body
   with the Air Material is an ordinary body and follows the same rule (the D-06 air gap ring, flush against both
   groups, stays a free object).
3. **Sliding, first version:** the Air Region keeps clear of the sliding surface, as free objects do today, and lies on
   the fixed side. Splitting it into a fixed and a moving part comes later (section 8).

Rejected: cutting the copies out of the Air Region with FreeCAD booleans before meshing. A boolean against hundreds of
copies is slow and fragile, and the mesher already cuts at mesh level (rules spec, section 7.4).

## 3. What the user sees

1. Add Air Region works in every Study. With Symmetric Groups it starts in Padding mode, sized round the **drawing of
   every copy** and the free objects, not round the cell objects alone.
2. The panel is the same: Box, Sector, Custom, Manual or Padding, the padding per side. One Air Region per Study.
3. To draw the air: draw a body, choose Custom and pick it. It is not put in the Main or Moving geometry (as today, Validate
   says so when it is).
4. Mesh Size works on the Air Region, on the whole of it and on its faces, as in a non-symmetric Study. (The whole-body
   size reaches the job through `air_size`; the plan checks that face picks reach the free job too and adds them if
   not.)
5. A drawn body that overlaps a copy is refused, naming both and the place, and the message says what to do: "make it the
   Custom shape of the Air Region, or cut the copies out of it."
6. Add Sliding Interface in a symmetric Study no longer asks for an Air Region first (today it does, although the
   interface of a symmetric Study takes its radius and never reads the air: `commands.AddSlidingInterface`).

## 4. Validate Study

In a Study with Symmetric Groups, `_groups` stops refusing the Air Region. These run instead:

- **The checks of `_air`, as in a non-symmetric Study:** one Air Region; a shape the plane allows (ZX: a half disc or a
  rectangle starting on the Z axis); Padding that can be built; a Custom source that is a solid (a face in the plane in
  2D) and is not in the Main or Moving geometry.
- **Everything inside the air.** The free objects and each Symmetric Group's drawing (`SymmetricGroup.Shape`, all its
  copies) must be inside the Air Region's outer boundary, its holes filled (a ring air outside the stator holds the motor). A
  copy sticking out is named with its group.
- **Free objects only touch the copies.** A free object (any body of the Main or Moving geometry that is not a cell
  object; never the Air Region) that overlaps a copy of a group on its side is refused. Method as `_touch_groups`: the
  copies' pieces with their bound boxes (`_elements`), a `distToShape` gate, then `common` only for pieces that meet. Touching
  over an area is allowed: that is today's flush contact. A pair OCC cannot compute is a warning, as in `_touch_groups`.
- **Sliding:** the Air Region must not cross or touch the Sliding Interface (`_on_interface` on the air's shape), with a
  message that says it is a limit of the tool and how to keep clear: a Sector whose inner radius is past the band, or a
  Custom shape. The Air Region is on the fixed side.
- **Structured settings:** a Transfinite Body or Recombine on the Air Region is refused, as on any free object
  (`_free_transfinite`), and the Recombine check gets the same.
- **Excitations** on the Air Region are refused, as today (`commands.AddExcitation`).

Removed: "An Air Region in a symmetric Study" (rules spec, section 6).

## 5. Objects and IDs

- `objects.volume_keys`: a grouped Study lists the part assignments, the free bodies, then the Air Region. One key, the
  air's Name, also when sliding: the air is all fixed (decision 3). The halves `#fixed` / `#moving` stay for non-symmetric
  Studies.
- `objects.refresh_sized_by` and `airshapes.padded_size`: in a grouped Study, SizedBy is the free bodies and the
  Symmetric Groups (their drawings), not the cell objects. Moving a container of a cell is already caught by
  `stale_drawing`; the drawing is a link of the air, so its recompute reaches the air.
- `AddAirRegion` seeds the padding from the same set.
- Sliding Interface: in a grouped Study the interface keeps its own radius and never reads the Air Region. `execute`
  tests `is_grouped` before `air_of`, and `make_air_region` / `make_sliding_interface` do not link the two in a grouped
  Study.
- Default Material: Add Air Region gives it the Study's Air, as today. The Material checks treat it as in a non-symmetric
  Study (a Material on the Air Region is not a part assignment).

## 6. Job and mesher

The parts exist already; they are joined.

- **Job writer** (`jobwriter.write_groups`): the fixed side's free job gets an `"air"` entry as `write_job` writes it for a
  non-symmetric Study (`geometry/air.brep`, mat_id, name, `air_size`). With no free bodies on the fixed side the job is
  made for the air alone.
- **Build** (`mesher.build`, unchanged): the air is added after the free bodies and fragmented with them; `claim_air` gives
  it what no free body owns. So the air gives way to the free objects exactly as in a non-symmetric Study.
- **Free meshing** (`meshgroups.mesh_free`): the bodies it meshes are the job's bodies plus `air_items(free_job)`. Each OCC
  volume of the air is surveyed and meshed round the frozen facets of the copies like any free body: the copies inside it
  become holes, a face of it under copies is opened (section 7.4 of the rules spec). A face it shares with a free body is
  the same case as two free bodies that touch. Several regions (the bore and the outside) are already handled.
- **Errors:** the existing refusals name the Air Region by its name ("free object Air: it lies inside a copy …"). "The air
  region is fully covered by bodies" stays for an air that nothing is left of.
- **Output:** the air is one physical group and one MAT_ID, as in a non-symmetric Study.

## 7. Catalogue and tests

**Catalogue** (`experiments/symmetric_catalogue`): every row that draws air over copies uses an Air Region instead.

- A plain box or cylinder over everything (D-04, D-05, the D rows at `free_air`, M3 rows, R-07, `common.py:422`):
  **Padding** where the padding gives the same size, else Manual Box/Sector, else Custom.
- L-10: the air is drawn today with the terminal plates cut out of it, because free objects only touch. It becomes a plain
  Box or Custom cylinder, and the plates are cut by the mesher like any body.
- M2-11 (the uneven gap disc over the rotor copies) and M2-12 (the gap sector over the magnets): Custom Air Regions, as
  they overlap copies.
- T-01, T-02 (the air rectangle round either order): a Box Air Region.
- Rows whose drawn air only touches copies (D-06's gap ring) stay as they are.
- New rows: a drawn body over copies, refused with the new message; a copy outside the Air Region, refused; a sliding
  Study with a ring Sector Air Region outside the band, meshes; one with a disc over everything, refused as a limit of the
  tool.
- Every row keeps its expected outcome, and the mesh of a converted row has the same element counts as before (the same
  air, made another way), within gmsh's run-to-run noise.

**Unit tests** (`pixi run -e addon test-addon`): Validate (Air Region allowed in a grouped Study, copies inside,
free-object overlap refused and touch allowed, sliding clearance, Transfinite refused); `volume_keys` with groups and air;
Padding round the drawings; the job's air entry in the free job with and without free bodies; meshing an air round copies
and a free body together (the air takes what both leave).

**GUI smoke** (`tests/freecad_addon/gui_smoke.py`): in a Study with a Symmetric Group, Add Air Region opens in Padding
mode round the drawing, and Validate passes.

## 8. Later (not in this work)

| What | Why later |
|---|---|
| An Air Region that crosses the sliding surface, split into fixed and moving air | After removing the copies, each region of the air must be put on the side whose copies enclose it (as `split_air` does for a non-symmetric Study). In 3D it also depends on how the band ends at the stack ends. |
| Air on the moving side (rotor end air in 3D) | Follows from the row above. Today it is a cell object or a free body that only touches. |
| Structured (Transfinite) Air Region with groups | Free objects cannot be structured yet (rules spec 4.4). |

## 9. Changes to the rules spec (2026-11-09)

| Section | Today | Becomes |
|---|---|---|
| 2, Anti-goals | "The automatic Air Region does not come into symmetric Studies." | Removed. |
| 2, In | "Objects meshed normally beside the copies, in particular air drawn by the user." | "…, and the Air Region." |
| 3, step 2 | Draw the air as an ordinary body over everything. | Add an Air Region (Padding, or Custom with a drawn body). |
| 4.4 | The user may draw the air solid, right over the copies; the Air Region is refused. | The Air Region gives way to the copies and the free objects; a free object only touches the copies; the mesher cuts at mesh level, as before. |
| 6 | "An Air Region in a symmetric Study" refused. | Section 4 here. |
| 7.5 | Free objects may not touch the sliding surface. | Free objects and the Air Region may not touch it (first version). |
| 8, item 2 | "M3-10 with drawn air", "L-06 and L-07 with drawn air". | "… with an Air Region". |

The plan updates the rules spec in the same commit as the code that changes it.
