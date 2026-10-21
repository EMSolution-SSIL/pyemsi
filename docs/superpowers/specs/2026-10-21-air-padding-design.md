# Air Region Padding and Formula Fields: Design

Date: 2026-10-21
Status: decisions agreed in conversation, waiting for spec review
Branch: `feature/freecad-addon`
Builds on: `2026-10-20-air-region-and-sliding-design.md` (implemented)

## 1. Goal

Today an Air Region is sized by numbers only: centre and lengths for a Box, radii, angles, bottom and height for a
Sector. The panel has a one-shot "Fit to bodies" button with one padding % for all sides. Two things are missing:

- **Padding as a way to define the air.** The user wants to say "20 % beyond the bodies on the −X side, 15 mm on
  ±Y", and have the air follow the bodies when they change.
- **Formulas in the panels.** The Air Region's properties accept FreeCAD expressions in the property editor, but
  the task panels use plain Qt spin boxes, so a field cannot hold `=VarSet.Gap * 2` or `2 cm`.

## 2. Background

- The air shape is built only from the Air Region's properties (`airshapes.air_shape`); the job exports that
  shape (final review fix). So a new way of filling those properties changes nothing in the job, the meshers or
  the slide/cell logic.
- `airshapes.fit_box` / `fit_study` compute the bodies' global bound box (main and moving geometry, never the air)
  and grow it by one padding % on every side. `commands.AddAirRegion` fits a new Box at 50 %;
  `taskpanels.AirRegionPanel` has the "Fit to bodies" button and its padding box.
- FreeCAD's own task panels (FEM, Draft) use `Gui::QuantitySpinBox` bound with `FreeCADGui.ExpressionBinding`: the
  field understands units, shows the f(x) button, and an entry starting with `=` becomes an expression stored on the
  property.
- In a sliding Study the Sector angles are the period (`ANGLE`); they are a physical choice, not a geometric one.

## 3. Decisions

1. **Size mode.** The Air Region gets `SizeMode`: `Manual` (today's behaviour, the default for existing documents)
   or `Padding`.
2. **Padding is live.** In `Padding` mode the size is recomputed from the Study's bodies (main and moving geometry,
   never the air) at every recompute, so the air follows a body that is moved, added or removed.
3. **Two columns per side, no unit choice.** Each side has a percentage and a length; the padding of that side is
   their sum: `padding = percent / 100 × (bound box size along that axis) + length`. Either may be 0; both may be
   used ("20 % but at least 5 mm more"). Each column has a fixed type, so both accept formulas.
4. **Sides are named by axis direction**: +X, −X, +Y, −Y, +Z, −Z ("20 % on −X" means 20 % on the negative X side,
   never a negative value). Padding values must be ≥ 0.
5. **Per shape:**

   | Shape | Padding sides | Stays manual |
   |---|---|---|
   | 3D Box | ±X, ±Y, ±Z | — |
   | 2D XY Rectangle | ±X, ±Y | — |
   | 3D Sector | outer radius, inner radius, +Z (top), −Z (bottom) | start / end angle |
   | 2D XY Sector | outer radius, inner radius | start / end angle |
   | ZX Rectangle | +X, +Z, −Z (left edge stays on the axis, x = 0) | — |
   | ZX Half disc | outer radius (about the centre on the axis) | centre z |
   | Custom | — (`Padding` not offered) | — |

   - Box: the bounding box is the bodies' global bound box.
   - Sector, radial: outer radius = largest distance of the bodies from the Z axis + outer padding; inner radius =
     smallest distance − inner padding, clamped at 0. An "Inner radius" switch chooses full disc (inner 0) or ring.
     Percent of a radial side is of the outer radius of the bodies.
   - ZX half disc: radius = largest distance of the bodies from the centre (0, 0, `Center.z`) + padding.
6. **Symmetric switch.** A panel check box ties the − side to the + side of each axis (and nothing for radial
   padding). It is a panel convenience: it writes the same values (or expressions) to both properties.
7. **Computed sizes stay visible.** In `Padding` mode `Center`, `Length`, `Width`, `Height`, `InnerRadius`,
   `OuterRadius`, `ZMin` are written by the recompute and shown read-only in the panel and the property editor,
   so formulas elsewhere that read `Air.Length` keep working.
8. **Recompute dependency.** The Air Region keeps a hidden link list to the Study's bodies (`SizedBy`), refreshed
   when the main or moving geometry changes, so FreeCAD recomputes it when a body changes. It is empty in `Manual`
   mode. The air never links to anything that depends on the air, so no cycle can form.
9. **Formula fields everywhere.** Every numeric field of the Air Region panel and the Sliding Interface panel
   becomes a `Gui::QuantitySpinBox` bound to its property with `ExpressionBinding` (lengths and angles with units,
   percentages and counts as plain numbers). An expression typed there is stored on the property.
10. **"Fit to bodies" is removed** (button, its padding box, `fit_study`'s use in the panel). A new Box Air Region
    starts in `Padding` mode at 20 % on every side when the Study has bodies, else `Manual` with today's defaults.
11. **Convert to Manual.** A panel button switches to `Manual` keeping the current computed sizes, to freeze the
    air.
12. **Validation:**
    - `Padding` with no bodies in the Study: error `"Air Region <name>: Padding needs bodies in the main or moving
      geometry."`
    - A negative padding value: error `"Air Region <name>: padding must not be negative (<side>)."`
    - A body outside the air, a Custom shape with `Padding`: existing / obvious errors.
    - In a sliding Study a Sector keeps its manual angles, so the period is unchanged.
13. **Old documents.** `onDocumentRestored` adds the new properties with `SizeMode = Manual` and zero padding, so
    saved Studies mesh exactly as before.

## 4. Properties added to `AirRegion`

| Property | Type | Default |
|---|---|---|
| `SizeMode` | Enumeration `Manual`, `Padding` | `Manual` |
| `PadXPlusPercent`, `PadXMinusPercent`, `PadYPlusPercent`, `PadYMinusPercent`, `PadZPlusPercent`, `PadZMinusPercent` | Float | 0 |
| `PadXPlus`, `PadXMinus`, `PadYPlus`, `PadYMinus`, `PadZPlus`, `PadZMinus` | Length | 0 |
| `PadOuterPercent`, `PadInnerPercent` | Float | 0 |
| `PadOuter`, `PadInner` | Length | 0 |
| `InnerFromBodies` | Bool (Sector: ring from the bodies' inner radius, else inner radius 0) | False |
| `SizedBy` | LinkListHidden (hidden) | empty |

Group `"Padding"`. Sector top/bottom use the Z pair.

## 5. Panel

```
Shape      [ Box ▾ ]          Size  ( ) Manual  (•) Padding
                 %        mm
  +X  [  20  f(x)]  [ 0 mm f(x)]
  −X  [  20  f(x)]  [ 0 mm f(x)]
  +Y  [   0  f(x)]  [15 mm f(x)]
  −Y  [   0  f(x)]  [15 mm f(x)]
  +Z  [  50  f(x)]  [ 0 mm f(x)]      (3D only)
  −Z  [  50  f(x)]  [ 5 mm f(x)]
  [✓] Symmetric
  Result: centre (…) · 120 × 60 × 90 mm      [Convert to Manual]
```

The 3D view updates while typing (transparent air), as the Manual fields do today.

## 6. Code changes

- `objects.py`: the properties above; `AirRegion.execute` fills the size properties from padding in `Padding` mode
  before building the shape; `SizedBy` refresh; `onDocumentRestored` upgrade; `make_air_region` default per
  decision 10.
- `airshapes.py`: `padded_size(air, bodies, plane)` returning the size properties for each shape; `fit_box` /
  `fit_study` removed if nothing else uses them.
- `validation.py`: the checks of decision 12.
- `taskpanels.py`: `AirRegionPanel` mode switch, padding table, Symmetric, result line, Convert to Manual; formula
  fields in `AirRegionPanel` and `SlidingInterfacePanel`; "Fit to bodies" removed.
- `commands.py`: `AddAirRegion` default per decision 10.
- Jobwriter, meshers, meshreport: unchanged.

## 7. Tests

- `test_air.py`: padded Box / Rectangle / Sector / ZX sizes match hand-computed values (percent, mm, both);
  moving a body and recomputing moves the air; adding a body to the main geometry grows it; Convert to Manual keeps
  the sizes; negative padding and no-body errors; an old document opens in `Manual` with unchanged sizes; an
  expression on a padding property (`=VarSet.Gap * 2`) drives the air.
- `gui_smoke.py`: switch to Padding, type a formula in a padding field, Symmetric, Convert to Manual; a formula in a
  Sliding Interface field.
- Examples: three new cases (Box with unequal padding, Sector ring from the bodies, ZX rectangle); existing cases
  keep their numbers.

## 8. Open points for review

- **ExpressionBinding from Python in FreeCAD 1.1.** Assumed available as `FreeCADGui.ExpressionBinding` with
  `Gui::QuantitySpinBox` created through `FreeCADGui.UiLoader()`. To confirm at the start of implementation; if a
  piece is missing, fall back to plain fields plus the property editor for formulas, and say so.
- **Percent of what for Sector radial padding.** Assumed: of the bodies' outer radius, for both inner and outer.

## 9. Not in this step

Padding for Custom shapes, padded Sector angles, padding per body or per group, several Air Regions.
