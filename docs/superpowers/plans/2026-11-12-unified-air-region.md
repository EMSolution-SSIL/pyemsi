# One Air Region for Every Study: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** The Air Region works in Studies with Symmetric Groups as it does in non-symmetric Studies, and free objects may
only touch the copies.

**Architecture:** Validate stops refusing the Air Region in a grouped Study and runs the ordinary `_air` checks against
the free objects and the groups' drawings. The job writer puts the air into the fixed side's free job as the `"air"` entry
`mesher.build` already understands, so the air gives way to the free bodies (`claim_air`); `meshgroups.mesh_free` then
meshes the air's pieces round the copies like any free body.

**Tech Stack:** FreeCAD 1.1 add-on (Python 3.11), gmsh in the mesher process, pytest through Pixi.

**Spec:** `docs/superpowers/specs/2026-11-12-unified-air-region-design.md`. Its section 9 lists the lines of
`docs/superpowers/specs/2026-11-09-symmetric-mesh-rules-design.md` to change (Task 6).

## Global Constraints

- Run everything through Pixi: `pixi run -e addon test-addon` (all add-on tests, about 2 min), or
  `pixi run -e addon pytest tests/freecad_addon/test_x.py -k name`; `pixi run lint` must pass; format with `pixi run format`.
- Line length 120, double quotes; never sort or reorder imports; no Black/isort.
- `mesher.py`, `mesher2d.py`, `meshcommon.py`, `meshgroups.py`, `meshfrozen.py` never import FreeCAD.
- No code that knows a device, a catalogue row or a name (rules spec section 1). Refusals that are a limit of the tool
  say "a limit of the tool".
- One Air Region per Study, as today.
- The rule, everywhere: the Air Region gives way to everything; bodies (free objects, copies) only touch each other.
- Sliding (first version): the Air Region must not cross or touch the Sliding Interface; it is all on the fixed side,
  one MAT_ID key (`air.Name`, no `#fixed` / `#moving` halves) in a grouped Study.
- Commit after each task; the pre-commit hook must run (never `--no-verify`). End messages with
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Review Focus

1. **A stale group drawing under a Padding air.** `validation.refresh_padding` recomputes the Padding air before it
   recomputes stale drawings (`objects.stale_drawing`), so a moved container of a cell would size the air round the old
   drawing. Expected: the air follows the drawing as it is now. Test in Task 3.
2. **A Custom source that is a cell object.** Expected: refused, like a source in the Main geometry. Test in Task 1.
3. **An older grouped document whose Sliding Interface is linked to an Air Region** (`iface.AirRegion` set). Expected:
   the interface keeps its own radius (grouped path), not the slide surface of the air. Test in Task 3.
4. **Free bodies only on the moving side.** Expected: the fixed side still gets a free job holding just the air. Test in
   Task 4.
5. **An Air Region smaller than the copies.** Expected: Validate names the group that sticks out, before any meshing.
   Test in Task 1.

---

### Task 1: Validate accepts the Air Region in a grouped Study

**Files:**
- Modify: `freecad_addon/emsolution/validation.py` (`_groups` near line 1209, `_air` near line 368)
- Test: `tests/freecad_addon/test_symmetric_groups.py`

**Interfaces:**
- Produces: `validation._air(study, bodies, moving, r, cells=())`. `bodies` are what must lie inside the air; `cells`
  are names a Custom source may not be (besides `bodies`). In a grouped Study `_groups` calls it with
  `bodies = free + objects.symmetric_groups(study)` (a group's `Shape` is its drawing of every copy), `moving` = the
  names of the moving free bodies and the groups whose `Side` is `"Moving"`, `cells = {b.Name for b in cell_bodies}`.

- [ ] **Step 1: Write the failing tests**

Remove `(break_air_region, "Air Region")` from the parametrised refusals and its helper. Add, using the `study` fixture
(stator cells to r 60), `ready`, `texts` and `free_body`:

```python
def test_air_region_round_the_copies_validates(study):
    ready(study)
    objects.make_air_region(study, "Sector", OuterRadius=90)
    study.Document.recompute()
    assert texts(study) == []


def test_air_region_smaller_than_the_copies_names_the_group(study):
    ready(study)
    objects.make_air_region(study, "Sector", OuterRadius=50)
    study.Document.recompute()
    assert any("Stator" in t and "not fully inside Air Region" in t for t in texts(study))


def test_custom_air_on_a_cell_object_is_refused(study):
    ready(study)
    objects.make_air_region(study, "Custom", Source=study.Document.getObject("CoilCell"))
    study.Document.recompute()
    assert any("CoilCell is the Custom shape of Air Region" in t for t in texts(study))


def test_two_air_regions_are_refused_in_a_grouped_study(study):
    ready(study)
    for _ in range(2):
        objects.make_air_region(study, "Sector", OuterRadius=90)
    study.Document.recompute()
    assert any(t.startswith("Only one Air Region per Study") for t in texts(study))
```

- [ ] **Step 2: Run them to see them fail**

Run: `pixi run -e addon pytest tests/freecad_addon/test_symmetric_groups.py -k "air_region or custom_air" -v`
Expected: FAIL, the first with "a Study with Symmetric Groups has no Air Region".

- [ ] **Step 3: Implement**

In `_groups`, replace the refusal loop with the `_air` call described under Interfaces. In `_air`, the Custom-source
check refuses `source.Name in {b.Name for b in bodies} | set(cells)`; for a cell object the message names the group
geometry: "take it out of the Symmetric Group" (the existing text for main/moving bodies stays). The "not fully inside"
loop already works for a group, since `geometry.global_shape(group)` is its drawing.

- [ ] **Step 4: Run the tests**

Run: `pixi run -e addon pytest tests/freecad_addon/test_symmetric_groups.py -v`
Expected: PASS (`test_free_air_and_copies_validate` still passes here; Task 2 rewrites it).

- [ ] **Step 5: Commit** — `Validate: an Air Region in a Study with Symmetric Groups`

### Task 2: Free objects may only touch the copies

**Files:**
- Modify: `freecad_addon/emsolution/validation.py` (new `_free_on_copies`, called from `_groups`)
- Test: `tests/freecad_addon/test_symmetric_groups.py`, `tests/freecad_addon/test_rules_end_to_end.py`

**Interfaces:**
- Consumes: `_elements(item) -> ([(piece, BoundBox)], tol)` and `_contact` as `_touch_groups` uses them.
- Produces: `validation._free_on_copies(groups, free, three, r)`: for each free body and each group (any side), each
  copy piece whose bound box meets the body's: `distToShape` gate (> tol: skip), then `common`; an overlap above
  `1e-6 * min(measure)` is an error. A pair OCC cannot compute is one warning per pair, as in `_touch_groups`. Touching
  is allowed.

Error text (exact):
`f"Free object {name} overlaps the copies of Symmetric Group {group.Label} by {amount:.3g} {unit} near ({x:.6g}, {y:.6g}, {z:.6g}). Free objects may only touch the copies: make it the Custom shape of the Air Region, or cut the copies out of it."`

- [ ] **Step 1: Write the failing tests**

Rewrite `test_free_air_and_copies_validate` and add a touch case:

```python
def test_free_body_over_the_copies_is_refused(study):
    ready(study)
    free_body(study, "FreeAir", Part.Face(Part.Wire(Part.makeCircle(80))))
    (text,) = [t for t in texts(study) if t.startswith("Free object")]
    assert "FreeAir overlaps the copies of Symmetric Group Stator" in text and "Custom shape of the Air Region" in text


def test_free_body_flush_against_the_copies_validates(study):
    ready(study)
    ring = Part.Face(Part.Wire(Part.makeCircle(90))).cut(Part.Face(Part.Wire(Part.makeCircle(60)))).Faces[0]
    free_body(study, "Ring", ring)
    assert texts(study) == []
```

In `test_rules_end_to_end.py`, `general_study` draws `FreeAir` over the copies: make it a Manual Box Air Region of the
same size (`objects.make_air_region(study, "Box", Center=reach.Center, Length=reach.XLength, Width=reach.YLength,
Height=reach.ZLength)` with `objects.assign(study, [air], lib["Air"], 0, name="Air")`), and make
`test_nothing_overlaps_and_everything_is_in_the_free_box` read `objects.air_regions(study)[0].Shape`.

- [ ] **Step 2: Run them to see the new one fail**

Run: `pixi run -e addon pytest tests/freecad_addon/test_symmetric_groups.py -k "free_body" -v`
Expected: `test_free_body_over_the_copies_is_refused` FAILS (no error today).

- [ ] **Step 3: Implement `_free_on_copies` and call it from `_groups` after the group loop.**

- [ ] **Step 4: Run the add-on suite**

Run: `pixi run -e addon test-addon`
Expected: PASS. Any other test that draws a free body over copies is converted the same way as `general_study`; list
them in the commit message.

- [ ] **Step 5: Commit** — `Validate: free objects only touch the copies of Symmetric Groups`

### Task 3: Objects, sizing and sliding with an Air Region in a grouped Study

**Files:**
- Modify: `freecad_addon/emsolution/objects.py` (`volume_keys` ~1757, `refresh_sized_by` ~467, `SlidingInterface.execute`
  ~636, `make_air_region` ~762, `make_sliding_interface` ~783, new `air_sizing_bodies`)
- Modify: `freecad_addon/emsolution/validation.py` (`refresh_padding` ~292, `_group_sliding` ~1077, `_free_transfinite` ~1188)
- Modify: `freecad_addon/emsolution/commands.py` (`AddAirRegion.Activated` ~228, `AddSlidingInterface.Activated` ~263)
- Test: `tests/freecad_addon/test_symmetric_groups.py`

**Interfaces:**
- Produces: `objects.air_sizing_bodies(study) -> list`: `study_bodies(study)` in a non-grouped Study; in a grouped one
  the study bodies that are not cell objects, then `symmetric_groups(study)`. `refresh_sized_by` and `AddAirRegion` use
  it in place of `study_bodies`.
- Produces: `volume_keys` of a grouped Study = part assignments, free bodies, `[a.Name for a in air_regions(study)]`,
  then the interfaces when sliding.

- [ ] **Step 1: Write the failing tests**

```python
def test_padding_air_sizes_round_the_drawing(study, stator):
    ready(study)
    air = objects.make_air_region(study, "Sector", SizeMode="Padding", PadOuterPercent=20)
    study.Document.recompute()
    assert [o.Name for o in air.SizedBy] == [stator.Name]  # the group, not its cell objects
    assert air.OuterRadius.Value == pytest.approx(60 * 1.2)  # the drawing reaches r 60; one cell alone would too,
    assert air.Shape.BoundBox.isInside(stator.Shape.BoundBox)  # but only the drawing covers the full circle


def test_padding_air_follows_a_moved_drawing_on_validate(study, stator):  # Review Focus 1
    # put the stator cells in an App::Part as test_drawing_follows_a_moved_part_on_validate does, add a Padding
    # Sector air, move the Part by (5, 0, 0), validate: the air's OuterRadius is the new reach * 1.2


def test_air_has_one_mat_id_key_when_sliding(study):
    sliding(study)
    ready(study)
    air = objects.make_air_region(study, "Sector", InnerRadius=60, OuterRadius=90)
    study.Document.recompute()
    assert air.Name in objects.volume_keys(study) and f"{air.Name}#fixed" not in objects.volume_keys(study)


def test_sliding_interface_keeps_its_radius_beside_an_air_region(study):  # Review Focus 3
    sliding(study)
    air = objects.make_air_region(study, "Sector", InnerRadius=60, OuterRadius=90)
    (iface,) = objects.sliding_interfaces(study)
    assert iface.AirRegion is None
    iface.AirRegion = air  # an older document
    study.Document.recompute()
    assert iface.Shape.Edges[0].Curve.Radius == pytest.approx(35)


def test_air_region_across_the_sliding_surface_is_a_limit_of_the_tool(study):
    sliding(study)
    ready(study)
    objects.make_air_region(study, "Sector", OuterRadius=90)
    study.Document.recompute()
    assert any("Air Region" in t and "Sliding Interface" in t and "a limit of the tool" in t for t in texts(study))


def test_transfinite_air_region_is_refused_with_groups(study):
    ready(study)
    air = objects.make_air_region(study, "Sector", OuterRadius=90)
    objects.make_transfinite_body(study, [air])
    study.Document.recompute()
    assert any("Transfinite" in t and "Air" in t for t in texts(study))
```

(`sliding(study)` is the existing helper: Sliding motion, rotor group Moving, interface at r 35.)

- [ ] **Step 2: Run them to see them fail**

Run: `pixi run -e addon pytest tests/freecad_addon/test_symmetric_groups.py -k "padding_air or mat_id_key or keeps_its_radius or across_the_sliding or transfinite_air" -v`
Expected: FAIL.

- [ ] **Step 3: Implement**

- `objects`: `air_sizing_bodies`; `volume_keys` as under Interfaces (the matching `objects.py:1759` docstring loses
  "and no Air Region"); `SlidingInterface.execute` tests
  `study is not None and is_grouped(study)` before `air_of`; `make_air_region` and `make_sliding_interface` leave
  `AirRegion` empty in a grouped Study.
- `validation.refresh_padding`: recompute stale drawings first, then the Padding air.
- `validation._group_sliding`: for the Air Region, `_on_interface(airshapes.air_shape(air, plane), radius, three)` gives
  `f"Air Region {name} crosses or touches Sliding Interface {iface.Label}. With Symmetric Groups the air must keep clear of the sliding surface, a limit of the tool: use a Sector whose inner radius is past the copied air band, or a Custom shape."`
- `validation._free_transfinite`: the Air Region counts as a free object (same message, Recombine included if the check
  covers it).
- `commands.AddSlidingInterface`: no "Add an Air Region first." in a grouped Study. `AddAirRegion` seeds padding from
  `air_sizing_bodies`.

- [ ] **Step 4: Run the add-on suite** — `pixi run -e addon test-addon`, expected PASS.

- [ ] **Step 5: Commit** — `Air Region with Symmetric Groups: sizing round the drawings, its own ID, clear of sliding`

### Task 4: The job writer puts the air in the fixed side's free job

**Files:**
- Modify: `freecad_addon/emsolution/jobwriter.py` (`write_groups` ~338)
- Test: `tests/freecad_addon/test_symmetric_groups.py` (beside `test_free_bodies_go_to_free_with_final_mat_ids`)

**Interfaces:**
- Produces, in `job["symmetric"]["free"]`: the `"fixed"` entry's job has
  `"air": {"name": objects.key_name(study, air.Name), "mat_id": int(study.MatIds[air.Name]), "file": "geometry/air.brep", "size": air_size(study)}`,
  the BREP written from `meshed_shape(air)`. Mesh Size picks on the air's faces go into that job's `"sizes"` (the
  `elements` filter of the fixed side takes `air.Name` too). With no fixed free bodies the fixed job is
  `_body_job(..., [], [], <air elements>, {}, "free_fixed_")` plus the air.

- [ ] **Step 1: Write the failing tests**

```python
def test_air_region_goes_to_the_fixed_free_job(study):
    ready(study)
    air = objects.make_air_region(study, "Sector", OuterRadius=90)
    objects.make_mesh_size(study, 4.0, [(air, "")])
    objects.make_mesh_size(study, 2.0, [(air, "Edge1")])
    study.Document.recompute()
    (free,) = load_job(study)["symmetric"]["free"]
    assert free["side"] == "fixed" and free["job"]["bodies"] == []
    entry = free["job"]["air"]
    assert entry["mat_id"] == int(study.MatIds[air.Name]) and entry["name"] == "Air" and entry["size"] == 4.0
    assert os.path.exists(os.path.join(jobwriter.scratch_folder(study), entry["file"]))
    assert [s["size"] for s in free["job"]["sizes"]] == [2.0]


def test_air_gets_a_fixed_job_when_free_bodies_are_only_moving(study):  # Review Focus 4
    sliding(study)
    ready(study)
    objects.make_air_region(study, "Sector", InnerRadius=60, OuterRadius=90)
    free_body(study, "Bore", Part.Face(Part.Wire(Part.makeCircle(8))), side="Moving")
    study.Document.recompute()
    free = {f["side"]: f["job"] for f in load_job(study)["symmetric"]["free"]}
    assert "air" in free["fixed"] and "air" not in free["moving"]
```

- [ ] **Step 2: Run them to see them fail** — `pixi run -e addon pytest tests/freecad_addon/test_symmetric_groups.py -k "fixed_free_job or fixed_job" -v`, expected FAIL.

- [ ] **Step 3: Implement in `write_groups`.** The air BREP name `geometry/air.brep` does not collide with the free
  jobs' `free_<side>_vol_*` files.

- [ ] **Step 4: Run the tests** — same command, expected PASS.

- [ ] **Step 5: Commit** — `Job: the Air Region of a grouped Study in the fixed side's free job`

### Task 5: The mesher meshes the air round the copies and the free bodies

**Files:**
- Modify: `freecad_addon/emsolution/meshgroups.py` (`mesh_free` ~1430, `_structured_names` ~732 if it needs the air)
- Test: `tests/freecad_addon/test_meshgroups.py` (class `GroupJobTest`, beside `test_box_of_air_around_rotated_copies`)

**Interfaces:**
- Consumes: the `"air"` entry of Task 4; `meshcommon.air_items(job)`; `mesher.build` / `mesher2d.build` unchanged.
- Produces: `mesh_free` meshes `bodies + [dict(a, size=free_job["air"]["size"]) for a in air_items(free_job)]`; the
  returned `{mat_id: FreeBody}` holds the air under its own MAT_ID. An air that the free bodies cover wholly gets no
  entry (`free_job["unwritten"]`, set by `build`).

- [ ] **Step 1: Write the failing tests**

```python
def air_entry(self, *boxes, size=6.0):
    """An "air" entry: the boxes (x, y, z, dx, dy, dz) as geometry/air_region.brep, MAT_ID 30, named Air."""
    write_boxes(self.geo("air_region.brep"), *boxes)
    return {"name": "Air", "mat_id": 30, "file": "geometry/air_region.brep", "size": size}

def test_air_region_gives_way_to_the_copies_and_a_free_body(self):
    write_boxes(self.geo("plate.brep"), PLATE)  # a box inside BOX, clear of the ring's copies
    plate = {"mat_id": 20, "name": "Plate", "file": "geometry/plate.brep", "size": 4.0}
    free = {"side": "fixed", "job": {"volumes": [plate], "surfaces": [], "sizes": [], "air": self.air_entry(self.BOX)}}
    mesh = self.meshed([self.ring_3d(self.TWELVE, ())], free=[free], dim=3)
    self.assertEqual(groups(mesh)[30][0], "Air")
    self.assertAlmostEqual(volume(mesh) / (60 * 60 * 15), 1, delta=1e-6)  # air + plate + copies fill the box
    self.assertAlmostEqual(shared_area(mesh, 20, 30), <PLATE's whole surface>, delta=1e-6)  # the air wraps it
    self.assertEqual(faces_in_three(mesh), 0)
    self.assertEqual(mesh_check_3d(mesh, (), ())[1], 0)

def test_air_region_alone_in_the_free_job_2d(self):
    # a 2D sector group, a free job {"bodies": [], "sizes": [], "air": <a square face as air_region.brep>}: the air
    # meshes, area of air + copies == the square, no edge in three elements
```

Choose `PLATE = (x, y, z, dx, dy, dz)` from `ring_3d`'s geometry so that it lies inside `BOX` and clear of every copy;
its whole surface is `2 * (dx * dy + dy * dz + dz * dx)`.

- [ ] **Step 2: Run them to see them fail** — `pixi run -e addon pytest tests/freecad_addon/test_meshgroups.py -k "air_region" -v`, expected FAIL (no MAT_ID 30 in the mesh).

- [ ] **Step 3: Implement in `mesh_free`** as under Interfaces. `_structured_names` includes the air's name only if a
  transfinite entry names its MAT_ID (Validate already refuses it; keep the mesher refusal general).

- [ ] **Step 4: Run** `pixi run -e addon pytest tests/freecad_addon/test_meshgroups.py -v`, expected PASS.

- [ ] **Step 5: Commit** — `Mesher: the Air Region of a grouped Study gives way to the free bodies and the copies`

### Task 6: End to end, GUI and the rules spec

**Files:**
- Modify: `tests/freecad_addon/symcases.py` (new `add_air_region`), `tests/freecad_addon/test_symmetric_groups.py`,
  `tests/freecad_addon/gui_smoke.py` (the Symmetric section after line 1394)
- Modify: `docs/superpowers/specs/2026-11-09-symmetric-mesh-rules-design.md` (the rows of the new spec's section 9)

**Interfaces:**
- Produces: `symcases.add_air_region(study, lib=None, shape=None, **props)`: with `shape`, a feature `AirShape` (not in
  any geometry) and a Custom Air Region on it; else `objects.make_air_region(study, props.pop("AirShape", "Box"), **props)`.
  With `lib`, `objects.assign(study, [air], lib, 0, name="Air")`. Returns the Air Region.

- [ ] **Step 1: Write the failing end-to-end test** — in `test_symmetric_groups.py`, the `study` fixture made `ready`,
  `symcases.add_air_region(study, lib, AirShape="Sector", OuterRadius=90)`, Run Mesh the way the existing mesh tests do
  (`mesh_parts`): the mesh has an `Air` group, no inverted element, and air area + copies area = π · 90².

- [ ] **Step 2: Run it to see it fail, implement `add_air_region`, run it to see it pass.**

- [ ] **Step 3: GUI smoke** — in the motor section (`sym_study`, sliding at r 35): `EMS_AddAirRegion` is active and opens
  the panel; the new air is Padding with `SizedBy` = the two groups and encloses both drawings; Validate reports the
  air crosses Sliding Interface; set `AirShape = "Sector"`, `InnerRadius = 60` (Manual) and the error is gone. Then
  delete the air so the rest of the smoke test runs as before.

Run: `pixi run -e addon freecad tests\freecad_addon\gui_smoke.py`, then the last line of `%TEMP%\ems_gui_smoke.txt`.
Expected: `PASS`.

- [ ] **Step 4: Update the rules spec** rows listed in section 9 of the new spec; set the new spec's Status to
  "implemented on feature/symmetric-rules".

- [ ] **Step 5: Run** `pixi run -e addon test-addon` and `pixi run lint`, expected PASS. **Commit** —
  `Air Region with Symmetric Groups: end to end, GUI smoke, rules spec`

### Task 7: The catalogue and the success list use Air Regions

**Files:**
- Modify: `experiments/symmetric_catalogue/common.py` (`wire_air` ~419), `devices.py` (`free_air` ~53 and its callers,
  `d_04`), `litz.py` (`l_10`), `m2.py` (`m2_11`, `quarter`), `m3.py` (the `add_free(... lib["Air"])` rows, not the
  refused M3-04 branch), `rods.py`, `traps.py` (`order`), `experiments/symmetric_rules/success_list.py` (lines 269,
  336, 387)

**Interfaces:**
- Consumes: `symcases.add_air_region` (Task 6).

- [ ] **Step 1: Convert** each drawn air that overlaps copies into an Air Region: `free_air` and `wire_air` keep their
  names and arguments and call `add_air_region(study, lib, shape=<the drawn shape>)` (Custom), so every caller converts at
  once; a Mesh Size given to the drawn air goes on the Air Region. L-10: the air becomes the plain cylinder (no plates cut
  out). M2-11, M2-12 static, T-01/T-02: Custom on the drawn face. Leave as free bodies the drawn air that only touches
  (D-06 `AirGap`, `success_list` lines 238 and 413 if they only touch; check with Validate).
- [ ] **Step 2: New rows** in `traps.py` CASES: `T-08` a drawn body over copies, `("refused", "may only touch the
  copies")`; `T-09` an Air Region smaller than the copies, `("refused", "not fully inside Air Region")`; in `m2.py`
  `M2-12-sliding-air` = `M2-12-sliding`'s Study with a disc Air Region over everything,
  `("refused", "keep clear of the sliding surface")`.
- [ ] **Step 3: Run the catalogue**

Run: `pixi run -e addon python experiments/symmetric_catalogue/build_catalogue.py`
Expected: every row matches (88 + 3), exit code 0. Compare the element counts of the converted rows with the previous
run's outputs in `C:\Users\hamed\Desktop\delme\catalogue_studies`: the same air, so within gmsh's run-to-run noise;
report any row that differs by more than 2 %.

- [ ] **Step 4: Commit** — `Catalogue: drawn air over copies becomes an Air Region`
