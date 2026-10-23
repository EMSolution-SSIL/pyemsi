# Air Region Padding and Formula Fields Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** An Air Region can be sized by live padding around the Study's bodies (% and mm per side), and every numeric field of the Air Region and Sliding Interface panels accepts FreeCAD formulas.

**Architecture:** `AirRegion` gains a `SizeMode` and padding properties; in `Padding` mode its `execute` computes the size properties from the bodies (`airshapes.padded_size`) before building the shape, and a hidden link list to the bodies makes FreeCAD recompute it when they change. Job, meshers and slide logic are untouched because they already build the air from the size properties. The panels switch to formula-capable fields that write to the properties live inside the panel's transaction.

**Tech Stack:** FreeCAD 1.1 (Part, `Gui::QuantitySpinBox`, `FreeCADGui.ExpressionBinding`), PySide, pytest via pixi.

**Spec:** `docs/superpowers/specs/2026-10-21-air-padding-design.md`

## Global Constraints

- Run everything through pixi: `pixi run pytest tests/freecad_addon/...`, `pixi run lint`, `pixi run format` (only files you changed; revert `highlight.py` if it is touched).
- Ruff, line length 120, double quotes. Never reorder imports. `objects.py`, `airshapes.py`, `validation.py` have no GUI code.
- GUI changes need the smoke test from PowerShell: `pixi run freecad tests\freecad_addon\gui_smoke.py`; last line of `%TEMP%\ems_gui_smoke.txt` must be `PASS`.
- `SizeMode` values exactly `Manual`, `Padding`; old documents open as `Manual` with zero padding and mesh exactly as before.
- Padding of a side = `percent / 100 × (bodies' bound box size along that axis) + length`; values ≥ 0; sides named +X, −X, +Y, −Y, +Z, −Z.
- Bodies = the Study's main geometry plus moving geometry when sliding (`objects.study_bodies`), never the air.
- Sector angles and the ZX half disc's centre z always stay manual; Custom has no `Padding`.
- Validation texts exactly: `"Air Region <name>: Padding needs bodies in the main or moving geometry."` and `"Air Region <name>: padding must not be negative (<side>)."`
- "Fit to bodies" is removed; a new Box Air Region starts in `Padding` at 20 % on every side when the Study has bodies, else `Manual` with today's defaults.
- Commit messages end with your environment's Co-Authored-By line. Never `--no-verify`.

## Decisions this plan adds to the spec

1. **Panels edit live.** The Air Region and Sliding Interface panels write each field to its property as it changes and recompute, inside the panel's transaction; OK commits, Cancel aborts (a new item) or undoes (an edit). This is what makes the spec's live 3D preview and formula binding work; today's panels apply on OK only.
2. **Names of computed limits.** Side keys used in code and messages: `"+X"`, `"-X"`, `"+Y"`, `"-Y"`, `"+Z"`, `"-Z"`, `"outer"`, `"inner"`.
3. **Zero size is an error.** If padding gives a size ≤ 0 along an axis (e.g. a flat 3D body with only % padding on Z), `padded_size` raises `ValueError("Air Region <name>: padding gives no size along <axis>; add a length padding.")`, which validation reports like other shape errors.
4. **When `SizedBy` is refreshed:** in `Study.onChanged` for `MainMode`, `MainSource`, `MainObjects`, `MovingMode`, `MovingSource`, `MovingObjects`, `Movement`; at the start of `validation.validate`; in `jobwriter.write_job`. A body added to a Part container used as the main source is therefore picked up at the next Validate / Run Mesh.
5. **Radial measures.** Largest distance from the Z axis = max over the body's tessellation points (`shape.tessellate(tol)`, `tol` = 1e-3 × its bound box diagonal) and vertices; smallest = `shape.distToShape(Z-axis line)`. ZX half disc: largest distance from (0, 0, `Center.z`) over the same points.

## Review Focus

1. A body inside a PartDesign Body or a Part::Box whose size is edited: after `doc.recompute()` the padded air has followed it (Task 3 test).
2. A Study whose main geometry is a Part container, with a body added to the container afterwards: after `validation.validate` the air has grown to include it (Task 3 test).
3. A padding property bound to a VarSet expression: changing the VarSet and recomputing changes the air (Task 2 test).
4. A ZX Study in Padding with bodies starting at x = 5: the rectangle's left edge stays at x = 0 (Task 2 test).
5. A sliding Study with a Sector in Padding: the angles, the period and the job's `periodic` are unchanged (Task 3 test).

---

### Task 1: Formula field and the Sliding Interface panel

**Files:**
- Modify: `freecad_addon/emsolution/taskpanels.py` (new `formula_box`; `SlidingInterfacePanel` fields)
- Test: `tests/freecad_addon/gui_smoke.py`

**Interfaces:**
- Produces: `taskpanels.formula_box(obj, prop, minimum=None, maximum=None) -> QWidget`: a `Gui::QuantitySpinBox` (from `FreeCADGui.UiLoader().createWidget("Gui::QuantitySpinBox")`) bound to `obj.prop` with `FreeCADGui.ExpressionBinding(widget).bind(obj, prop)`; shows the property's unit (length, angle, or none for Float/Integer); writing a value sets the property and recomputes the object. Fallback if binding is unavailable in FreeCAD 1.1: a plain spin box that still writes live; report it as a concern.
- `SlidingInterfacePanel`: Radius, Position, Divisions, CrossDivisions use `formula_box`; the panel follows decision 1 (live edit in a transaction).

- [ ] **Step 1: Spike** in the pixi FreeCAD GUI: create a `Part::Box`, `formula_box(box, "Length")`, set the expression `=2 * 5 mm` through the binding, check `box.ExpressionEngine` holds it and `box.Length == 10`. Record what works in the report.
- [ ] **Step 2: Add smoke steps:** in the existing sliding-interface smoke section, set Divisions to the formula `=36 * 2` through the panel field, OK, assert `iface.Divisions == 72` and `("Divisions", "36 * 2")` (or equivalent) in `iface.ExpressionEngine`; open the panel again, change Radius, Cancel, assert the radius is unchanged.
- [ ] **Step 3: Run** the smoke test — `FAIL`.
- [ ] **Step 4: Implement** `formula_box` and convert `SlidingInterfacePanel`.
- [ ] **Step 5: Run** the smoke test — `PASS`; `pixi run pytest tests/freecad_addon` — pass; `pixi run lint`.
- [ ] **Step 6: Commit** — "Formula fields: Sliding Interface panel accepts expressions".

### Task 2: Padding properties and padded sizes

**Files:**
- Modify: `freecad_addon/emsolution/objects.py` (`AirRegion` properties, `execute`, `onChanged`, `onDocumentRestored`)
- Modify: `freecad_addon/emsolution/airshapes.py` (new `padded_size`, `radial_extent`)
- Test: `tests/freecad_addon/test_air.py`

**Interfaces:**
- Produces:
  - `AirRegion` properties per spec section 4, group `"Padding"`: `SizeMode`, `Pad{X,Y,Z}{Plus,Minus}Percent` (Float), `Pad{X,Y,Z}{Plus,Minus}` (Length), `PadOuterPercent`, `PadInnerPercent` (Float), `PadOuter`, `PadInner` (Length), `InnerFromBodies` (Bool), `SizedBy` (`App::PropertyLinkListHidden`, editor mode hidden). Added by `objects.add_padding(obj)` from `__init__` and `onDocumentRestored` (only the missing ones).
  - `onChanged(obj, "SizeMode")`: size properties (`Center`, `Length`, `Width`, `Height`, `InnerRadius`, `OuterRadius`, `ZMin`) editor mode 1 in `Padding`, 0 in `Manual`.
  - `airshapes.padded_size(air, bodies, plane) -> dict[str, object]`: the size properties to write (`Center` as `App.Vector`, others as floats in mm), per spec decision 5 and plan decisions 2, 3, 5. Raises `ValueError` for Custom: `"Air Region <name>: Padding is not available for a Custom shape."`
  - `airshapes.radial_extent(shapes, center_z=None) -> (float, float)`: (smallest, largest) distance from the Z axis, or from the point (0, 0, center_z) for the ZX half disc.
  - `AirRegion.execute`: in `Padding` mode, write `padded_size(obj, list(obj.SizedBy), plane)` (only values that differ) before building the shape.
- [ ] **Step 1: Write the failing tests** (bodies are `Part::Box`/`Part::Cylinder` or faces; set `air.SizedBy` directly in this task):
  - `test_padded_box_percent_and_mm`: box body x 0–10, y 0–20, z 0–30; +X 20 %, −X 0 % + 5 mm, ±Y 0, ±Z 10 % → Center/Length/Width/Height give x −5–12, y 0–20, z −3–33.
  - `test_padded_rectangle_xy` and `test_padded_rectangle_zx_left_edge_on_axis` (Review Focus 4: bodies x 5–15 → x from 0 to 15 + padding).
  - `test_padded_sector_ring_from_bodies`: ring body r 30–50, z 0–10; outer 10 %, inner 2 mm, `InnerFromBodies` True, ±Z 1 mm → InnerRadius 28, OuterRadius 55, ZMin −1, Height 12; angles unchanged.
  - `test_padded_sector_disc_ignores_inner`: `InnerFromBodies` False → InnerRadius 0.
  - `test_padded_half_disc_zx`: body face at distance ≤ 40 from (0, 0, Center.z) + 5 mm → OuterRadius 45.
  - `test_flat_body_without_length_padding_is_an_error` (plan decision 3).
  - `test_custom_padding_is_an_error`.
  - `test_padding_follows_a_varset_expression` (Review Focus 3): `PadXPlus` bound to `=VarSet.Gap * 2`; change `Gap`, recompute → Length changes.
  - `test_size_properties_read_only_in_padding`.
  - `test_old_air_region_opens_manual_with_same_size`: remove the padding properties from an Air Region, save, reopen → `SizeMode == "Manual"`, sizes unchanged.
- [ ] **Step 2: Run** `pixi run pytest tests/freecad_addon/test_air.py -v` — new tests fail.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `test_air.py`, then `pixi run pytest tests/freecad_addon`, `pixi run lint` — pass.
- [ ] **Step 5: Commit** — "Air Region padding: properties and sizes from the bodies".

### Task 3: Live dependency and validation

**Files:**
- Modify: `freecad_addon/emsolution/objects.py` (`refresh_sized_by`, `Study.onChanged`)
- Modify: `freecad_addon/emsolution/validation.py` (padding checks; refresh at start)
- Modify: `freecad_addon/emsolution/jobwriter.py` (refresh in `write_job`)
- Test: `tests/freecad_addon/test_air.py`

**Interfaces:**
- Consumes: Task 2 properties and `padded_size`.
- Produces: `objects.refresh_sized_by(study)`: for each Air Region in `Padding`, `SizedBy = study_bodies(study)` (only when different); in `Manual`, `SizedBy = []`. Called per plan decision 4.
- Validation texts: the two from Global Constraints (side names from plan decision 2), plus `padded_size`'s `ValueError`s reported like other Air Region shape errors.
- [ ] **Step 1: Write the failing tests:**
  - `test_air_follows_an_edited_body` (Review Focus 1): Part::Box body in Padding air; change its Length; `doc.recompute()` → air Length changed without calling anything else.
  - `test_air_grows_when_a_body_joins_main_geometry`: add a body to `MainObjects` → recompute → air includes it.
  - `test_body_added_to_container_source_is_picked_up_at_validate` (Review Focus 2).
  - `test_padding_without_bodies_is_an_error` and `test_negative_padding_is_an_error` (exact texts).
  - `test_sliding_sector_padding_keeps_period` (Review Focus 5): sliding Study, Sector air 0–45° in Padding → `airshapes.period(study)` and the job's `periodic` unchanged; validation clean.
  - `test_manual_air_has_no_sized_by`.
- [ ] **Step 2: Run** — fail.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `pixi run pytest tests/freecad_addon`, `pixi run lint` — pass.
- [ ] **Step 5: Commit** — "Padded air follows the bodies; padding validation".

### Task 4: Air Region panel and command

**Files:**
- Modify: `freecad_addon/emsolution/taskpanels.py` (`AirRegionPanel`)
- Modify: `freecad_addon/emsolution/commands.py` (`AddAirRegion`)
- Test: `tests/freecad_addon/gui_smoke.py`

**Interfaces:**
- Consumes: `formula_box` (Task 1), padding properties and `refresh_sized_by` (Tasks 2–3).
- Produces:
  - `AirRegionPanel` (plan decision 1): shape combo as today; Size `Manual` / `Padding` radio (Padding hidden for Custom); Manual fields as today but `formula_box`; Padding table per spec section 5 (rows by shape per spec decision 5, columns `%` and `mm`, each a `formula_box`); `Symmetric` check box copying + to − (value or expression) while checked; result line `"Result: centre (x, y, z) · L × W × H mm"` (or radii for a Sector) updated on every change; `Convert to Manual` button; no "Fit to bodies".
  - `AddAirRegion`: new Box in `Padding` with every applicable `%` = 20 and `refresh_sized_by` when the Study has bodies, else `Manual` defaults.
- [ ] **Step 1: Update smoke steps:** replace the "Fit to bodies" checks with: new Air Region is in Padding and encloses the bodies; set +X % to the formula `=10 + 10`, Symmetric on → −X follows; result line shows the new length; Convert to Manual → `SizeMode == "Manual"`, sizes unchanged; Cancel on an edit undoes a change.
- [ ] **Step 2: Run** the smoke test — `FAIL`.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** the smoke test — `PASS`; `pixi run pytest tests/freecad_addon`, `pixi run lint` — pass.
- [ ] **Step 5: Commit** — "Air Region panel: padding table, formulas, Convert to Manual".

### Task 5: Examples and removing the old fit

**Files:**
- Modify: `tests/freecad_addon/cases.py` (`fit_air` uses Padding; three new cases), `tests/freecad_addon/test_air.py` (drop `fit_box` / `fit_study` tests)
- Modify: `freecad_addon/emsolution/airshapes.py` (remove `fit_box`, `fit_study` once unused)
- Test: `tests/freecad_addon/test_examples.py`

**Interfaces:**
- `cases.fit_air(study, bodies, padding=50)` makes a Box Air Region in `Padding` with that % on every side, so cases 01–20 keep their air sizes.
- New cases: `21_padded_box_3d` (unequal padding: ±X 20 %, +Y 10 mm, −Y 0, ±Z 50 %), `22_padded_sector_ring_2d` (`InnerFromBodies`, outer 20 %, inner 5 mm), `23_padded_rect_zx` (+X 30 %, ±Z 10 mm); checklists name the expected limits.
- [ ] **Step 1: Write** the new cases and a test that each existing case's air size equals the size it had before: run `fit_air` for cases 01, 09 and 13 and assert the air Center/Length/Width/Height equal the numbers the old `fit_box` gives today (hard-code them, read from the current code before changing it).
- [ ] **Step 2: Run** `pixi run pytest tests/freecad_addon/test_examples.py -v` — new cases fail.
- [ ] **Step 3: Implement**; remove `fit_box` / `fit_study` and their tests.
- [ ] **Step 4: Run** `pixi run pytest tests/freecad_addon`, `pixi run lint`, the smoke test, and `pixi run python tests/freecad_addon/build_examples.py` (01–23 OK, E1–E6 expected ERROR).
- [ ] **Step 5: Commit** — "Examples for padded air; remove the one-shot fit".
