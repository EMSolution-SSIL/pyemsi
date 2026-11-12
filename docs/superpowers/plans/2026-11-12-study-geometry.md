# One Study, Whole Document: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A Study meshes every body of its document unless excluded; one Study per document; the Sliding Interface
decides what moves.

**Architecture:** `geometry.py` learns cut tools, links, exclusions and group drawings and gives the Study's bodies
(`study_geometry`). A new FreeCAD-only, GUI-free module `sides.py` works out the moving side from the Sliding
Interfaces. The Study's Main/Moving properties and the Symmetric Group `Side` go; every reader moves to the two new
sources. The Study panel shows one tree.

**Tech Stack:** FreeCAD 1.1.0 Python add-on (`freecad_addon/emsolution/`), PySide, pytest/unittest, Pixi.

**Spec:** `docs/superpowers/specs/2026-11-12-study-geometry-design.md` — read it first; this plan does not repeat its
reasons.

## Global Constraints

- Run everything through Pixi: `pixi run -e addon test-addon` (whole add-on suite), `pixi run -e addon pytest
  tests/freecad_addon/test_x.py -k name`, GUI smoke `pixi run -e addon freecad tests\freecad_addon\gui_smoke.py` then
  the last line of `%TEMP%\ems_gui_smoke.txt` must be `PASS`.
- Ruff only, line length 120, `pixi run format` on changed files; `pixi run lint` passes. Never sort or reorder imports.
- `mesher.py`, `mesher2d.py`, `meshcommon.py` never import FreeCAD. `objects.py`, `geometry.py`, `sides.py`,
  `studymaterials.py` have no GUI code; GUI lives in `commands.py` and `taskpanels.py`.
- No migration code (spec decision 5). Missing new properties are added on restore; old ones are removed on restore.
- Commit after each task; message style `Study geometry: <what>`; end with
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Never `--no-verify`.
- Do not touch `freecad_addon/emsolution/highlight.py`'s uncommitted change in the working tree (not part of this work):
  stage files by name.
- User-visible texts below are exact.

## Review Focus

1. A document with objects that are not bodies (a Spreadsheet, a sketch, a Draft dimension, the FEM mesh result Run
   Mesh adds) must validate with no message about them. Test in Task 3.
2. A hidden body that is not a cut tool is still meshed (visibility is ignored). Test in Task 3.
3. A body added later inside an excluded Part is excluded too. Test in Task 3.
4. A 2D Study ignores the document's solids, and a 3D Study its flat faces. Test in Task 3.
5. A Padding Air Region grows to a body drawn after it, on the next Validate. Test in Task 3.

---

### Task 1: Cut tools out, links in (geometry)

**Files:**
- Modify: `freecad_addon/emsolution/geometry.py` (`global_shape`, `inputs`, `collect`, `tree`; new functions)
- Test: `tests/freecad_addon/test_inputs.py`, `tests/freecad_addon/test_study.py` (geometry tests near line 1317)

**Interfaces:**
- Produces:
  - `geometry.cut_tools(doc) -> dict[str, App.DocumentObject]`: body Name -> the Cut (`Part::Cut`) or Join Cutout
    (`FeatureCutout`) it is the `Tool` of. A Part/Group tool contributes every body `collect([tool], dim)` would give
    (either dimension); an `App::Link` tool contributes nothing (the link is not a body, its target stays one).
  - `geometry.link_target(obj) -> App.DocumentObject | None`: the body an `App::Link` names (`obj.getLinkedObject(True)`
    or the subname target), when it is a `Part::Feature` (not a link, not a sketch, not a Study object) or a PartDesign
    Body, and the link is not an array (`ElementCount` 0). Else None (also for non-links).
  - `geometry.inputs(obj, outside=False) -> set[str]`: `outside=True` also follows the property `OUTSIDE` skips.
  - `global_shape(obj)` returns a link body's shape where the user sees it.
  - `tree(doc, dimension)` and `collect(roots, dimension)`: cut tools are never returned; link bodies are returned
    like bodies. A link body does not consume its target (the target stays a body unless something else consumes it);
    a link that something else uses still passes through to its target, as today.

- [ ] **Step 1: Write the failing tests**

In `test_inputs.py` (helpers `box`, `shown` exist):
```python
def test_the_tool_of_a_join_cutout_is_not_meshed(doc):  # replaces test_the_tool_of_a_join_cutout_stays_a_body
    air_box, coil = box(doc, "AirBox", 0, 30), box(doc, "Coil", 10)
    cut = JoinFeatures.makeCutout(name="AirCut")
    cut.Base, cut.Tool = air_box, coil
    assert shown(doc) == ["AirCut"]
    assert geometry.cut_tools(doc) == {"Coil": cut}

def test_a_link_to_a_cut_tool_is_a_body(doc):
    air_box, coil = box(doc, "AirBox", 0, 30), box(doc, "Coil", 10)
    cut = doc.addObject("Part::Cut", "Air")
    cut.Base, cut.Tool = air_box, coil
    link = doc.addObject("App::Link", "CoilLink")
    link.LinkedObject = coil
    doc.recompute()
    assert shown(doc) == ["Air", "CoilLink"]
    assert geometry.link_target(link) is coil

def test_a_link_body_does_not_consume_its_target(doc):
    coil = box(doc, "Coil", 10)
    link = doc.addObject("App::Link", "CoilCopy")
    link.LinkedObject = coil
    link.LinkPlacement.Base = App.Vector(50, 0, 0)
    doc.recompute()
    assert shown(doc) == ["Coil", "CoilCopy"]
    assert abs(geometry.global_shape(link).BoundBox.XMin - 60) < 1e-6  # Coil starts at x = 10

def test_a_link_in_a_moved_part_is_where_it_is_seen(doc):
    coil = box(doc, "Coil", 10)
    part = doc.addObject("App::Part", "Holder")
    part.Placement.Base = App.Vector(0, 100, 0)
    link = doc.addObject("App::Link", "CoilLink")
    link.LinkedObject = coil
    part.addObject(link)
    doc.recompute()
    assert abs(geometry.global_shape(link).BoundBox.YMin - 100) < 1e-6

def test_a_link_array_and_a_link_to_a_part_are_not_bodies(doc):
    coil = box(doc, "Coil", 10)
    arr = doc.addObject("App::Link", "Arr")
    arr.LinkedObject, arr.ElementCount = coil, 3
    part = doc.addObject("App::Part", "P")
    to_part = doc.addObject("App::Link", "ToPart")
    to_part.LinkedObject = part
    doc.recompute()
    assert geometry.link_target(arr) is None and geometry.link_target(to_part) is None
    assert "Arr" not in shown(doc) and "ToPart" not in shown(doc)

def test_a_part_used_as_a_tool_makes_its_bodies_cut_tools(doc):
    air_box = box(doc, "AirBox", 0, 30)
    holder = doc.addObject("App::Part", "Coils")
    a, b = box(doc, "CoilA", 5, 3), box(doc, "CoilB", 15, 3)
    holder.addObject(a)
    holder.addObject(b)
    cut = doc.addObject("Part::Cut", "Air")
    cut.Base, cut.Tool = air_box, holder
    doc.recompute()
    assert set(geometry.cut_tools(doc)) == {"CoilA", "CoilB"}
```
Change `test_a_link_with_a_subname_is_the_object_it_names` to expect `["Magnet", "Air"]` (Coil is a cut tool).
In `test_study.py`, rename `test_the_tool_of_a_cut_stays_a_body` to `test_the_tool_of_a_cut_is_not_meshed` and expect
`geometry.collect([air, coil], "3D") == ([air], [])` and `geometry.tree(self.doc, "3D") == [(air, None)]`;
`test_a_link_to_the_tool_of_a_cut_keeps_the_tool_a_body` keeps its assertions.

- [ ] **Step 2: Run them, expect FAIL**

Run: `pixi run -e addon pytest tests/freecad_addon/test_inputs.py tests/freecad_addon/test_study.py -k "cut or link" -v`
Expected: the new and changed tests FAIL (cut tools still shown, links refused).

- [ ] **Step 3: Implement in `geometry.py`**

`collect` drops cut tools after resolving containers and accepts link bodies where it accepts `Part::Feature`;
`tree`'s `shapes` set gets link bodies and loses cut tools; the consumed set is built from non-link candidates only.
`global_shape` for a link: the target's shape moved by the link's global placement (check `LinkTransform` and
`LinkPlacement` with the `freecad-addon-api` skill; the two placement tests pin it). Update the `collect` docstring
("the tool of a Cut stays a body of its own" is no longer true).

- [ ] **Step 4: Run the whole add-on suite**

Run: `pixi run -e addon test-addon`
Expected: PASS except tests that relied on a cut tool being a body; fix those by giving them the new expectation, not
by changing the rule.

- [ ] **Step 5: Commit** — `git add freecad_addon/emsolution/geometry.py tests/freecad_addon/test_inputs.py tests/freecad_addon/test_study.py`, message `Study geometry: cut tools are never meshed, a Link to one body is a body`.

---

### Task 2: `sides.py` and the interface's moving side

**Files:**
- Create: `freecad_addon/emsolution/sides.py`
- Modify: `freecad_addon/emsolution/objects.py` (`SlidingInterface`, `make_sliding_interface`)
- Test: create `tests/freecad_addon/test_sides.py`

**Interfaces:**
- Produces:
  - `objects.MOVING_SIDES = {"Rotational": ["Inside", "Outside"], "Axial gap": ["Above", "Below"], "Linear": ["Positive", "Negative"]}`
  - `SlidingInterface.MovingSide` (`App::PropertyEnumeration`, group "Sliding", tooltip "Which side of the surface
    moves"). Its choices follow `Kind` (refilled in `onChanged` when `Kind` changes, keeping the index; added on
    restore when missing, index 0). `make_sliding_interface(..., MovingSide="Outside")` works because `Kind` is set
    before the props.
  - `sides.side_of(shape, iface, plane) -> str | None`: `"moving"`, `"fixed"`, or None when the shape is on both
    sides. Half-spaces: Rotational — within radius R of the Z axis (a cylinder solid in 3D, a disc in XY);
    Axial gap — z > Position (3D only); Linear — coordinate along `NormalAxis` > Position. Inside/Above/Positive is
    the half-space; Outside/Below/Negative its complement. A shape is on a side when all but 1e-6 of its volume (area
    in 2D) is in it, measured like `airshapes.cell_of`. plane is `"3D"` or `"XY"`.
  - `sides.piece_sides(pieces, interfaces, surfaces, plane) -> tuple[list[str | None], list[tuple[str, object]]]`:
    for each air piece, the interfaces whose surface is within `airshapes.TOL` of it vote with `side_of`; all agree ->
    that side; else None, plus one error per piece: `f"Sliding Interfaces {a.Label} and {b.Label} disagree about the side of the air between them: change the moving side of one."` (with the first interface as the problem's object).

- [ ] **Step 1: Write the failing tests** in `test_sides.py` (a fixture makes a doc, a 2D or 3D Study and interfaces
with `objects.make_sliding_interface`; shapes are plain `Part` shapes):
```python
def test_rotational_inside_moves(study2d):
    i = objects.make_sliding_interface(study2d, "Rotational", Radius=50)
    assert sides.side_of(disc(0, 40), i, "XY") == "moving"
    assert sides.side_of(ring(60, 70), i, "XY") == "fixed"
    assert sides.side_of(ring(40, 60), i, "XY") is None
    i.MovingSide = "Outside"
    assert sides.side_of(ring(60, 70), i, "XY") == "moving"

def test_choices_follow_the_kind(study2d):
    i = objects.make_sliding_interface(study2d, "Rotational", Radius=50)
    assert i.getEnumerationsOfProperty("MovingSide") == ["Inside", "Outside"]
    i.Kind = "Linear"
    assert i.getEnumerationsOfProperty("MovingSide") == ["Positive", "Negative"]

def test_axial_gap_above_moves(study3d):  # box z 10..20, plane z = 5
    i = objects.make_sliding_interface(study3d, "Axial gap", Position=5)
    assert sides.side_of(Part.makeBox(10, 10, 10, V(0, 0, 10)), i, "3D") == "moving"

def test_linear_negative_moves(study2d):  # NormalAxis Y, plane y = 0
    i = objects.make_sliding_interface(study2d, "Linear", Position=0, NormalAxis="Y", MovingSide="Negative")
    assert sides.side_of(square(0, -5, 4), i, "XY") == "moving"

def test_double_air_gap(study2d):  # air disc R 100 cut at 30 and 50
    a = objects.make_sliding_interface(study2d, "Rotational", Radius=30, MovingSide="Outside")
    b = objects.make_sliding_interface(study2d, "Rotational", Radius=50, MovingSide="Inside")
    pieces, surfaces = cut_disc(100, [30, 50])  # helper: airshapes.cells of the disc and the two circles, inner first
    assert sides.piece_sides(pieces, [a, b], surfaces, "XY") == (["fixed", "moving", "fixed"], [])
    b.MovingSide = "Outside"
    found, errors = sides.piece_sides(pieces, [a, b], surfaces, "XY")
    assert found[1] is None and len(errors) == 1 and "disagree" in errors[0][0]
```
Write the small helpers `disc`, `ring`, `square`, `cut_disc` in the test file.

- [ ] **Step 2: Run, expect FAIL** — `pixi run -e addon pytest tests/freecad_addon/test_sides.py -v` (no module `sides`).

- [ ] **Step 3: Implement** `sides.py` (imports `Part`, `airshapes`, `objects`; no GUI) and the property.

- [ ] **Step 4: Run** `pixi run -e addon pytest tests/freecad_addon/test_sides.py -v` → PASS, then
`pixi run -e addon test-addon` → PASS (nothing reads the new property yet).

- [ ] **Step 5: Commit** — `Study geometry: the Sliding Interface says which side moves`.

---

### Task 3: The whole document is the Study's geometry; one Study

The core change. After it the Main/Moving properties are gone and every reader uses `geometry.study_geometry` and
`sides.moving`. Group sides still come from `SymmetricGroup.Side` (Task 4 removes it).

**Files:**
- Modify: `objects.py`, `geometry.py`, `sides.py`, `validation.py`, `jobwriter.py`, `airshapes.py`, `commands.py`,
  `taskpanels.py`
- Test: `test_study.py`, `test_air.py`, `test_studymaterials.py`, `test_symmetric_groups.py`,
  `test_symmetric_study*.py`, `cases.py`, `symcases.py`, others the suite shows

**Interfaces:**
- Consumes: Task 1 (`cut_tools`, `link_target`, `inputs(outside=True)`), Task 2 (`side_of`, `piece_sides`).
- Produces:
  - `Study.Excluded` (`App::PropertyLinkListGlobal`, group "Geometry", editor mode 2). Removed: `MainMode`,
    `MainSource`, `MainObjects`, `MovingMode`, `MovingSource`, `MovingObjects` (also removed in `onDocumentRestored`
    when present; `Excluded` added there when missing).
  - `objects.SIZING_PROPERTIES = ("Excluded",)`.
  - `objects.set_excluded(study, objs) -> None`: stores objs once each, in order.
  - `geometry.is_excluded(study, obj) -> bool`: obj or any container above it (`getParentGroup`,
    `getParentGeoFeatureGroup`) is in `Excluded`.
  - `geometry.air_sources(study) -> dict[str, App.DocumentObject]`: body Name -> its Custom Air Region.
  - `geometry.group_drawings(study) -> dict[str, App.DocumentObject]`: Name of each body (not a cell) whose
    `inputs(body, outside=True)` holds a cell object Name -> that cell's group.
  - `geometry.study_geometry(study) -> tuple[list, list[str]]`: the Study's free bodies in tree order — the leaves of
    `tree(doc, study.Dimension)` that are not excluded, not air sources, not cell objects, not group drawings — and
    `collect`'s errors for them (2D plane checks). Replaces `region`, `stored`, `setup`, `whole`.
  - `objects.study_bodies(study)` = `study_geometry(study)[0]`. `_main_bodies` and `NO_MAIN_GEOMETRY` are removed.
  - `sides.moving(study) -> set[str]`: Names of the free bodies on the moving side; empty without Sliding motion or
    when it cannot be worked out (validation reports why). Non-grouped: the piece (`airshapes.cell_of`) of each body,
    moving per `piece_sides`. Grouped: `side_of(global_shape(body), iface, plane)` against the one interface.
  - `sides.moving_pieces(study) -> list[int]`: indices of the moving pieces of `airshapes.cells(...)` (non-grouped).
  - `objects.assignment_problem(study, bodies) -> str`: for bodies that are neither `assignable` nor cells:
    `f"Not meshed by the Study: {names}. Tick them in the Study panel or select other bodies."` (Task 5 makes the
    reason specific).

- [ ] **Step 1: Move the test helpers to the new model**

`StudyTest.setUp` loses `self.study.MainMode = "Manual"`. Delete `StudyTest.include` and every call to it; `assign`
no longer includes. Add `def exclude(self, *bodies): objects.set_excluded(self.study, [*self.study.Excluded, *bodies])`.
Same in `test_air.py`, `test_studymaterials.py`. `cases.new_study` and `cases.slide_study` lose the Main/Moving lines
(slide cases set `MovingSide` in their interface props when the old moving bodies are not on the default side).
`symcases.add_free` and `test_symmetric_groups.free_body` lose `side`. Delete the three multi-Study tests in
`test_study.py` (`test_second_study_replaces_the_mesh_and_keeps_its_own_scratch_folder`,
`test_multiple_studies_have_independent_ownership_and_ids`, `test_two_studies_restore_their_sources_settings_and_ids`)
and `test_main_geometry_has_no_materials_mode`. A test that relied on a body being outside the Study now calls
`exclude()` on it; a test about a removed message gets the new one from this task.

- [ ] **Step 2: Write the failing tests** (in `test_study.py` unless noted):
```python
def test_every_body_is_meshed_and_one_drawn_later_too(self):
    a, b = self.box("A"), self.box("B", 20)
    self.assertEqual(objects.study_bodies(self.study), [a, b])
    c = self.box("C", 40)
    self.assertEqual(objects.study_bodies(self.study), [a, b, c])

def test_a_hidden_body_is_meshed(self):  # Review Focus 2
    a = self.box("A")
    a.Visibility = False
    self.assertEqual(objects.study_bodies(self.study), [a])

def test_an_excluded_part_keeps_out_a_body_added_later(self):  # Review Focus 3
    part = self.doc.addObject("App::Part", "Helpers")
    part.addObject(self.box("H1"))
    keep = self.box("Keep", 40)
    self.exclude(part)
    part.addObject(self.box("H2", 20))
    self.assertEqual(objects.study_bodies(self.study), [keep])

def test_objects_that_are_not_bodies_are_ignored(self):  # Review Focus 1
    self.assign([self.box("A")])
    self.doc.addObject("Spreadsheet::Sheet", "Sheet")
    self.doc.addObject("Sketcher::SketchObject", "Sketch")
    self.doc.addObject("Fem::FemMeshObject", "Mesh")
    self.doc.recompute()
    self.assertEqual(validation.errors(validation.validate(self.study)), [])

def test_a_2d_study_ignores_solids(self):  # Review Focus 4 (and the 3D mirror: a face is ignored by a 3D Study)
    ...  # a 2D Study (new document) with a box and a z = 0 face: study_bodies == [face]; the 3D Study here ignores a face

def test_a_second_study_is_refused(self):
    objects.make_study(self.doc, "2D", "Other")
    texts = [p.text for p in validation.errors(validation.validate(self.study))]
    self.assertIn(f"This document has two Studies, {self.study.Label} and Other: delete one.", texts)

def test_the_custom_air_source_is_not_a_body(self):  # test_air.py
    ...  # a Custom Air Region on body S: S not in study_bodies; air_sources(study) == {S.Name: air}

def test_the_drawing_of_a_group_is_not_a_body(self):  # test_symmetric_groups.py, on symcases.motor_doc
    ...  # the Fragments top of the stator chain is in group_drawings and not in study_bodies; validate has no overlap error

def test_padding_air_grows_to_a_body_drawn_later(self):  # test_air.py, Review Focus 5
    ...  # Padding Box air round A; draw B outside it; validation.validate; the air's BoundBox holds B
```
Sliding (in `test_air.py`, replacing the MovingObjects setups): a stator ring outside and a rotor inside a Rotational
interface with the default Inside: `sides.moving(study) == {rotor.Name}` with no per-body setting; with both bodies
inside, validation reports `"No body is on the moving side of the Sliding Interfaces."` only when no body is inside.
Linear: a body above `y = 0` moves with Positive, the other with Negative.

- [ ] **Step 3: Run, expect FAIL** — `pixi run -e addon pytest tests/freecad_addon -k "meshed or excluded or ignored or second_study or not_a_body or grows or moving" -v`.

- [ ] **Step 4: Implement**

- `objects.py`: properties above; `study_bodies`, `air_sizing_bodies` (free bodies, plus the groups when grouped),
  `assignable`, `assignment_problem`; `make_study` unchanged otherwise.
- `geometry.py`: the functions above; delete `region`, `stored`, `setup`, `whole`.
- `validation.py`: `validate` starts with the two-Studies error (`objects.studies(study.Document)`, Labels in document
  order; return after it) and uses `bodies, errors = geometry.study_geometry(study)`, `moving = sides.moving(study)`.
  Delete `free_bodies` and `_skipped_picks`. `_free_cells` keeps only the "two groups" check. `_slides(study, bodies,
  moving, r)`: keeps "needs an Air Region…", ZX, "crosses a Sliding Interface", the outside-the-air skip; adds the
  `piece_sides` errors; replaces "No body is in the moving geometry." by `"No body is on the moving side of the
  Sliding Interfaces."`; drops "Moving body … same side" and "Part of the air … holds no body". `_groups` gets
  `moved = moving | {g.Name for g in groups if g.Side == "Moving"}`. `_links`' outside warning text becomes
  `f"{kind} {item.Label} is not used for {names}: not meshed by the Study."` (Task 5 refines).
- `jobwriter.py`: `check` uses `study_geometry` (docstring: tree order); `write_groups` `on_moving = sides.moving(study)`;
  `write_job` `job["moving"]` = MAT_IDs of the moving bodies in body order; `write_slides` exports
  `sides.moving_pieces(study)`.
- `airshapes.study_plane`: from `study_geometry` (cells first when grouped, as today).
- `commands.py`: `NewStudy.IsActive` also needs `not objects.studies(App.ActiveDocument)`; `gate` loses the
  `NO_MAIN_GEOMETRY` redirect.
- `taskpanels.py`: `active_study()` returns `objects.find_study(App.ActiveDocument)` (drop `_active` and
  `set_active_study`, and their callers); `StudyView` keeps one tree titled "Geometry" built from `geometry.tree` with
  every leaf ticked unless `is_excluded`; unticking saves `Excluded` (a fully unticked container as itself, else its
  unticked leaves), in one transaction "Choose Study geometry". The Moving box goes. `FolderView`'s notice drops the
  `NO_MAIN_GEOMETRY` branch. (Task 6 adds reasons, groups and labels.)

- [ ] **Step 5: Run** `pixi run -e addon test-addon` → PASS; `pixi run lint` → PASS.
  `gui_smoke.py` still sets the removed properties; it is updated and run in Task 7 and fails until then.

- [ ] **Step 6: Commit** — `Study geometry: the whole document is the Study's geometry, one Study per document`.

---

### Task 4: Group sides from the geometry; part keys are names

**Files:**
- Modify: `objects.py` (`SymmetricGroup`, `make_symmetric_group`, `part_key`, `study_parts`, `sync_parts`),
  `sides.py`, `validation.py` (`_groups`, `_group_sliding`, `_air_off_moving`, `_part_materials`), `jobwriter.py`
  (lines ~308, ~321), `taskpanels.py` (`SymmetricGroupPanel`)
- Test: `test_symmetric_groups.py`, `test_symmetric_study*.py`, `test_rules_end_to_end.py`, `symcases.py`

**Interfaces:**
- Consumes: Task 2 `side_of`, Task 3 `sides.moving`.
- Produces:
  - `sides.group_side(study, item) -> str | None`: `"fixed"` without Sliding motion or without an interface; else
    `side_of(item.Shape, iface, plane)` against the Study's one interface (None when the drawing is on both sides).
  - `objects.part_key` is removed; a part's key is its name. `Material.PartKey` holds the part name. `study_parts`
    returns `{name: [(item, row, copy), ...]}`.
  - `SymmetricGroup.Side` is removed (and removed on restore); `make_symmetric_group(study, cells, rules=(), name="Symmetric Group")`.

- [ ] **Step 1: Write the failing tests** (`test_symmetric_groups.py`):
```python
def test_the_rotor_inside_the_interface_moves_with_no_setting(study):
    rotor, iface = sliding(study)  # helper loses side="Moving"; Radius 35, default Inside
    assert sides.group_side(study, rotor) == "moving"
    assert sides.group_side(study, objects.symmetric_groups(study)[0]) == "fixed"  # the stator
    iface.MovingSide = "Outside"
    assert sides.group_side(study, rotor) == "fixed"

def test_part_materials_survive_a_new_radius(study):
    rotor, iface = sliding(study)
    objects.sync_parts(study)
    before = {m.Name: m.PartKey for m in objects.part_assignments(study)}
    iface.Radius = 36
    study.Document.recompute()
    objects.sync_parts(study)
    assert {m.Name: m.PartKey for m in objects.part_assignments(study)} == before
    assert all("|" not in key for key in before.values())

def test_same_name_on_the_two_sides_is_refused(study):  # replaces test_same_name_on_the_two_sides_is_two_parts
    ...  # a stator row and a rotor row named "Iron": "Part names on both sides of the Sliding Interface: Iron." error
```
Delete the assertions on `.Side` (lines ~58, ~153, ~578) and the `side=` arguments everywhere.

- [ ] **Step 2: Run, expect FAIL** — `pixi run -e addon pytest tests/freecad_addon/test_symmetric_groups.py -v`.

- [ ] **Step 3: Implement.** Every `part_key(...)` call becomes the name; `key.partition("|")[2]` becomes the key;
the `fixed|`/`moving|` prefix tests in `_part_materials` become `sides.group_side` of the part's items (an item whose
side is None is skipped there: `_group_sliding` already reports a group crossing the radius). `_group_sliding`'s
`sides` set and `_air_off_moving` and `_groups`' `moved` use `group_side`. `jobwriter`'s group entry `"side"` is
`group_side(...)`. `SymmetricGroupPanel`: remove the Side combo and `write_side`; when sliding, show a read-only
label `"Side: moving"` or `"Side: fixed"` (or `"Side: unknown, the drawing crosses the Sliding Interface"`).

- [ ] **Step 4: Run** `pixi run -e addon test-addon` → PASS.

- [ ] **Step 5: Commit** — `Study geometry: a group's side comes from the Sliding Interface, part keys are names`.

---

### Task 5: Links take Materials, items and picks

**Files:**
- Modify: `geometry.py` (new `body_shape`), `objects.py` (`pick_body`), and every read of a Study body's `.Shape` in
  `validation.py`, `jobwriter.py`, `objects.py`, `airshapes.py`, `labels.py`, `highlight.py`, `taskpanels.py`
  (`grep -n "\(body\|b\|obj\)\.Shape"` lists about 23)
- Test: `tests/freecad_addon/test_study.py`

**Interfaces:**
- Consumes: Task 1 `link_target`, `global_shape`.
- Produces: `geometry.body_shape(obj) -> Part.Shape`: what `obj.Shape` is for a `Part::Feature`; for a link body the
  linked shape in the link's own coordinates (so `global_shape` = `body_shape` moved by the global placement, for both).
  `objects.pick_body(obj)` returns a link body as itself.

- [ ] **Step 1: Write the failing tests**
```python
def test_a_link_takes_a_material_and_a_face_size(self):
    coil = self.box("Coil", 10)
    self.air_cut_by(coil)
    link = self.doc.addObject("App::Link", "CoilLink")
    link.LinkedObject = coil
    self.doc.recompute()
    self.assign([link])
    objects.make_mesh_size(self.study, 1.0, [(link, "Face1")])
    volumes, _, elements = jobwriter.check(self.study)
    self.assertIn(link, [b for b, _ in volumes])
    self.assertEqual([(b, subs) for _, b, subs in elements], [(link, ["Face1"])])

def test_a_missing_face_on_a_link_is_reported(self):
    ...  # a Mesh Size on (link, "Face99"): error "Mesh size … body CoilLink has no Face99. Reselect it."
```
Also: `jobwriter.write_job` on that Study writes a BREP for the link whose bounding box is the link's global one.

- [ ] **Step 2: Run, expect FAIL**, **Step 3: implement**, **Step 4: run** `pixi run -e addon test-addon` → PASS.

- [ ] **Step 5: Commit** — `Study geometry: a Link body takes Materials, Mesh Sizes and picks`.

---

### Task 6: Why a body is not meshed — gate and Validate messages

**Files:**
- Modify: `geometry.py`, `objects.py` (`assignment_problem`), `validation.py` (`_links`, `_materials`, new `_links_not_bodies`)
- Test: `test_study.py`, `test_air.py`

**Interfaces:**
- Consumes: Task 1, Task 3.
- Produces: `geometry.not_meshed(study, obj) -> tuple[str, App.DocumentObject | None] | None`: None when obj is a
  Study body, a cell object or a group; else `(reason, other)`, reason one of `"excluded"`, `"cut tool"` (other = the
  Cut), `"made from"` (other = the meshed body made from it), `"air shape"` (other = the Air Region), `"drawing"`
  (other = the group), `"not a body"`.

Exact texts (`{b}` = `display_name` of the body, `{o}` of other, `{m}` the Material's `display_name`, `{k} {i}` the
item kind and Label as `_links` writes them):

| reason | gate (`assignment_problem`) | Material warning | item warning |
|---|---|---|---|
| excluded | `{b} is excluded from the Study: tick it in the Study panel.` | `Material {m} is on {b}, which is excluded from the Study.` | `{k} {i} is not used for {b}, which is excluded from the Study.` |
| cut tool | `{b} is the tool of {o} and is not meshed. To mesh it, make a Link to it.` | `Material {m} is on {b}, the tool of {o}, which is not meshed. To mesh it, make a Link to it.` | `{k} {i} is not used for {b}, the tool of {o}, which is not meshed. To mesh it, make a Link to it.` |
| made from | `{b} is not meshed on its own: {o} is made from it.` | `Material {m} is on {b}, which {o} is now made from: assign it to {o}.` | `{k} {i} is not used for {b}, which {o} is now made from: put it on {o}.` |
| air shape | `{b} is the Custom shape of Air Region {o}.` | (none: the Air Region has its own Material) | `{k} {i} is not used for {b}, the Custom shape of Air Region {o}: put it on the Air Region.` |
| drawing | `{b} is the drawing of Symmetric Group {o}: pick its copies on the group.` | `Material {m} is on {b}, the drawing of Symmetric Group {o}: the group's parts take the Materials.` | `{k} {i} is not used for {b}, the drawing of Symmetric Group {o}: put it on the cell objects.` |

The gate joins several bodies' texts with a space. A link that `link_target` refuses gets the warning
`f"{link.Label} is not meshed: a Link is meshed only when it links one body."` (Validate, once per link, from the
document's `App::Link` objects that are not used by another body).

- [ ] **Step 1: Write the failing tests** — one per table row and column that has a text (14), plus the link warning.
Example:
```python
def test_a_material_on_a_cut_tool_is_warned_about(self):
    coil = self.box("Coil", 10)
    _, air = self.air_cut_by(coil)
    objects.assign(self.study, [coil], self.steel(), 0)
    texts = [p.text for p in validation.validate(self.study) if p.severity == "warning"]
    self.assertIn(f"Material {objects.display_name(objects.materials(self.study)[0])} is on Coil, the tool of Air, which is not meshed. To mesh it, make a Link to it.", texts)

def test_a_cut_tool_without_assignments_is_silent(self):
    coil = self.box("Coil", 10)
    self.air_cut_by(coil)
    self.assertFalse([p for p in validation.validate(self.study) if "Coil" in p.text])
```
(`objects.assign` bypasses the gate, so assignments on unmeshed bodies can be set up directly.)

- [ ] **Step 2: Run, expect FAIL**, **Step 3: implement**, **Step 4: run** `pixi run -e addon test-addon` → PASS.

- [ ] **Step 5: Commit** — `Study geometry: say why a body is not meshed`.

---

### Task 7: Study panel tree, Sliding Interface panel, GUI smoke

**Files:**
- Modify: `taskpanels.py` (`StudyView`, `SlidingInterfacePanel`), `tests/freecad_addon/gui_smoke.py`

**Interfaces:**
- Consumes: `geometry.tree`, `is_excluded`, `not_meshed`, `air_sources`, `group_drawings`, `sides.moving`,
  `sides.group_side`, `objects.symmetric_groups`, `MOVING_SIDES`.

Tree rules (spec 4.3): leaves ticked unless excluded; air sources and group drawings unticked and disabled with the
reason in a second column (`"air shape of {air}"`, `"drawing of Symmetric Group {group}"`); cut tools not shown; each
Symmetric Group is a row after the document's nodes, ticked and disabled, its cell objects under it with
`"meshed by Symmetric Group {group}"`, and the cells are not shown where they sit in the document; when sliding, rows on
the moving side (bodies by `sides.moving`, groups by `group_side`) show `"moving"` in the second column. The count line
and diagnostics are unchanged. `SlidingInterfacePanel`: a "Moving side" combo with `MovingSide`'s choices, refilled
when the Kind changes, saved with the panel's other fields.

- [ ] **Step 1: Update `gui_smoke.py`**: the "Outside" body is now excluded through the Study tree (untick it in
`StudyView`'s tree and check `study.Excluded == [doc.Outside]`); the gate text is
`"Outside is excluded from the Study: tick it in the Study panel."`; the empty-Study Air Region check excludes the
bodies instead of emptying `MainObjects`; add: the tree's reason column for an air source; the Sliding Interface panel
changes the moving side and `MovingSide` follows.

- [ ] **Step 2: Run the smoke test, expect FAIL** — `pixi run -e addon freecad tests\freecad_addon\gui_smoke.py`,
then read the last line of `%TEMP%\ems_gui_smoke.txt`: `FAIL`.

- [ ] **Step 3: Implement** the tree and the combo.

- [ ] **Step 4: Run** the smoke test → `PASS`; `pixi run -e addon test-addon` → PASS.

- [ ] **Step 5: Commit** — `Study geometry: one Study tree with reasons, moving side in the Sliding Interface panel`.

---

### Task 8: Example builders and the catalogue

**Files:**
- Modify: `tests/freecad_addon/build_examples.py`, `experiments/symmetric_catalogue/build_catalogue.py`, and any
  helper they use that still sets Main/Moving geometry or `side=`; `experiments/structured_examples/README.md`,
  `experiments/symmetric_examples/README.md` (their "main geometry" wording)

- [ ] **Step 1:** `grep -rn "MainMode\|MainObjects\|MovingObjects\|MovingMode\|MainSource\|\.Side\b\|side=\"Moving\"" tests experiments freecad_addon`
→ no hits outside history docs (`docs/superpowers/plans/` older plans stay as written).

- [ ] **Step 2:** Run `pixi run -e addon test-addon` (includes `test_examples.py`) → PASS.

- [ ] **Step 3:** Rebuild the catalogue with `--coarse` first, then in full:
`pixi run -e addon python experiments/symmetric_catalogue/build_catalogue.py --coarse`, then without `--coarse`.
Expected: 91 of 91 plus `motor_sliding-air` pass, as before this work.

- [ ] **Step 4: Commit** — `Study geometry: examples and catalogue on the whole-document Study`.
