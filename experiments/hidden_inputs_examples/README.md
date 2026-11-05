# Hidden inputs examples (3D)

The Study geometry tree hides a body another body is made from: a Fuse's operands, a Compound's children, the base of
a Cut. These four files are the cases where that rule (`geometry.inputs`) got it wrong, before and while the branch
`feature/cut-tool-bodies` changed it; they now all give the right tree (tests: `tests/freecad_addon/test_inputs.py`).
Each Study is in Manual mode with every body the tree offers ticked, as a user ticking all would do.
Rebuild them with `pixi run -e addon python experiments/hidden_inputs_examples/build_examples.py`, which also prints
the tree and the validation problems quoted below. The files have no Materials, so Validate also lists that warning.

| File | Tree on `main` | First version of the branch | Now (right) |
|---|---|---|---|
| 1_link_with_subname | Air | AirBox, Coil, Air | Coil, Air |
| 2_thickness | ShellOut, ShellIn | SolidOut, ShellOut, SolidIn, ShellIn | SolidOut, ShellOut, SolidIn, ShellIn |
| 3_draft_clone | RodClone | RodClone | Rod, RodClone |
| 4_join_cutout | AirCut | AirCut | Coil, AirCut |

## 1. A Link with a subname as the base of a Cut (fixed regression of the branch)

`AirBox` (30 mm cube) sits inside the Part `Stator`. `AirBoxLink` is an App::Link to it written as
`(Stator, "AirBox.")`, the way FreeCAD links an object inside a Part. `Air` = Cut of `AirBoxLink` minus `Coil`.

- **What went wrong:** the first version of the branch skipped every link with a subname, as it skips the curves of a
  Ruled Surface. But `"AirBox."` names a whole object, not an edge or face. So `AirBox` was not seen as inside `Air`, and the tree
  offered it. Validate then said *Bodies AirBox and Coil overlap by 1e+03 mm³* and *Bodies AirBox and Air overlap by
  2.6e+04 mm³*.
- **Fix:** a subname is a reference only when it ends in an element (`Edge3`, `Stator.AirBox.Face2`); one ending in
  `.` is the object it names, here `AirBox`, not the whole Part.

## 2. Part Thickness: works, shown for the record

Two 20 mm cubes, each with a Part Thickness open at its top face. `ShellOut` grows 2 mm outward and wraps `SolidOut`.
`ShellIn` grows 2 mm inward and lies inside `SolidIn`.

- The Thickness links its solid through a face (`Faces = (Solid, ["Face6"])`), so the branch shows both solids. That
  is right for `SolidOut`: it is the content of the cup and only touches its shell. On `main` it was hidden.
- **Validate:** *Bodies SolidIn and ShellIn overlap by 3.39e+03 mm³*. The inward one is caught; nothing to fix.

## 3. A Draft Clone moved away (fixed, was wrong on `main`)

`Rod` (cylinder r 3, h 20) and `RodClone`, a Draft Clone of it moved 30 mm along x: two separate rods.

- **What went wrong:** a Clone links its original as a whole (`Objects`), so `Rod` counted as inside `RodClone` and
  was hidden. Only the copy could be picked. Patterns of rods, coils or magnets made with Clones lost their original.
- **Fix:** a Clone's `Objects` is treated like a Mirror's `Source`: the copy does not hold the original's volume. A
  Clone left in place overlaps its original, and the overlap check reports that. (A Draft Array is different: the array
  includes its base, so hiding the base is right.)

## 4. Part Join Cutout (fixed, was wrong on `main`)

`AirCut` = Part > Join > Cutout of `AirBox` (30 mm cube) with `Coil`: the air with room cut out for the coil.

- **What went wrong:** Cutout is a Python feature, not `Part::Cut`, so its `Tool` counted as inside the result, and
  `Coil` was hidden. Same problem as the rods file before the branch.
- **Fix:** Cutout's `Tool` is one of the inputs whose volume the result leaves out. (Join Embed fuses the tool into the
  base, so hiding the tool there is right.)
