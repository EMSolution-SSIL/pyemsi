# Recombine per Body Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the global Recombine switch with a per-body `Recombine` item and a global recombination algorithm, so the user picks which bodies get quads / hexahedra and Gmsh never crashes on a quad face between two tetrahedral bodies.

**Architecture:** A new `Recombine` item in the Mesh Sizes folder (same pattern as `TransfiniteBody`) and a `RecombinationAlgorithm` enumeration on the folder. `jobwriter` writes `"recombine": [MAT_IDs]` and `"Mesh.RecombinationAlgorithm"` in `options`. Both mesher scripts call one new shared function, `meshcommon.apply_recombine`, after `apply_transfinite`; in 3D it sorts each candidate face by its neighbours (quads / triangles + NOTE / error) before calling `setRecombine(2, face)`.

**Tech Stack:** Python 3.11 (Pixi), FreeCAD 1.1 Python API, Gmsh Python API, unittest/pytest, PySide.

**Spec:** [docs/superpowers/specs/2026-10-16-recombine-design.md](../specs/2026-10-16-recombine-design.md)

## Global Constraints

- Run everything through Pixi: `pixi run pytest ...`, `pixi run python ...`. Never `pip install`.
- Format with `pixi run format`, check with `pixi run lint`. Line length is **120**; no trailing comma on a construct that fits on one line. Never run Black/isort or Ruff with overrides. Only format files you changed.
- **Never sort or reorder imports.** Add new imports next to related ones.
- `mesher.py`, `mesher2d.py` and `meshcommon.py` run in their own process: **never import FreeCAD** in them.
- `Mesh.RecombineAll` is **never** written to a job and never set by the mesher.
- A job without `"recombine"` meshes with no recombined faces. Write `"recombine"` only when the list is not empty.
- Algorithm names and Gmsh values, first = default: `{"Blossom": 1, "Simple": 0, "Blossom full-quad": 3, "Simple full-quad": 2}`.
- Faces the mesher leaves as triangles are reported as `NOTE:` lines on **stderr** through `meshcommon._note`; errors are `JobError` (one `ERROR:` line). NOTE and ERROR lines name the bodies, not the Recombine item.
- **Never run `git commit`.** At each "Checkpoint" step, stop, tell the user what changed, ask them to check and test it, and suggest the commit message. Wait for their yes. (User rule; it overrides any "commit frequently" habit.)

## Review Focus

- A document saved with the old `Recombine` Bool must open, lose the property, and write a valid job. Pinned in Task 1.
- A body in a Recombine item that is not in the Study's main geometry is skipped, not an error; a body in two Recombine items appears once in the job. Pinned in Task 4.
- A structured, recombined box on its own with the HXT volume algorithm must still mesh: the Delaunay rule applies only when quads touch tetrahedra. Pinned in Task 3.
- A chosen body whose faces are all shared with tetrahedral bodies (a coil inside air) must mesh as all tetrahedra with a NOTE, not crash or error. Pinned in Task 3.
- An existing 2D structured triangle job (3 corners, collapsed corner) still gives quads plus the corner triangles when recombined. Pinned in Task 2 (existing test moved to the new key).

---

### Task 1: `Recombine` item and the algorithm setting in `objects.py`

**Files:**
- Modify: `freecad_addon/emsolution/objects.py` (`ALGORITHMS_3D` line 8, `MeshSizesFolder` lines 68–99, after `TransfiniteEdges` ~line 236, after `make_transfinite_edges` ~line 396, after `transfinite_edges()` ~line 416, `is_item` ~line 462, `_size_text` ~line 517)
- Test: `tests/freecad_addon/test_study.py`

**Interfaces:**
- Produces (used by Tasks 4 and 5):
  - `objects.RECOMBINATION_ALGORITHMS = {"Blossom": 1, "Simple": 0, "Blossom full-quad": 3, "Simple full-quad": 2}`
  - folder property `RecombinationAlgorithm` (`App::PropertyEnumeration`, group `"Mesh"`, default `"Blossom"`); folder property `Recombine` is gone
  - `objects.add_recombination_algorithm(folder) -> None`: adds `RecombinationAlgorithm` if missing; removes `Recombine` if present. Replaces `add_recombine`.
  - `objects.Recombine` proxy (subclass of `_Proxy`), one property `References` (`App::PropertyLinkSubListGlobal`, group `"EMSolution"`, doc `"Bodies meshed with quads (2D) or quad faces and hexahedra (3D)"`)
  - `objects.make_recombine(study, bodies) -> obj` (label `"Recombine"`, `References = [(b, "") for b in bodies]`)
  - `objects.recombine_items(study) -> list`
  - `is_item` and `item_refs` accept a `Recombine`; `_size_text` returns `"recombine"` for it

- [ ] **Step 1: Write the failing tests**

In `tests/freecad_addon/test_study.py`:

In `test_transfinite_items_are_listed_with_mesh_sizes`, replace the last line `self.assertFalse(self.study.MeshSizesGroup.Recombine)` with:

```python
        self.assertEqual(self.study.MeshSizesGroup.RecombinationAlgorithm, "Blossom")
        self.assertFalse(hasattr(self.study.MeshSizesGroup, "Recombine"))
```

Add after it:

```python
    def test_recombine_item_is_listed_with_mesh_sizes(self):
        a, b = self.box("A"), self.box("B", 10)
        self.include(a, b)
        item = objects.make_recombine(self.study, [a, b])
        self.assertEqual(objects.recombine_items(self.study), [item])
        self.assertEqual(objects.mesh_sizes(self.study), [])
        self.assertTrue(objects.is_item(item))
        self.assertEqual(objects.item_refs(item), [(a, ""), (b, "")])
        self.assertEqual(objects.mesh_size_rows(self.study), [(item, [(a, ""), (b, "")], ["Recombine", "recombine", "A, B"])])

    def test_recombination_algorithms_are_the_gmsh_values(self):
        self.assertEqual(
            self.study.MeshSizesGroup.getEnumerationsOfProperty("RecombinationAlgorithm"),
            ["Blossom", "Simple", "Blossom full-quad", "Simple full-quad"],
        )
        self.assertEqual(objects.RECOMBINATION_ALGORITHMS, {"Blossom": 1, "Simple": 0, "Blossom full-quad": 3, "Simple full-quad": 2})
```

Replace `test_old_mesh_sizes_folder_gets_recombine_on_load` with:

```python
    def test_folder_saved_with_the_old_recombine_switch_loads_without_it(self):
        folder = self.study.MeshSizesGroup
        folder.removeProperty("RecombinationAlgorithm")
        folder.addProperty("App::PropertyBool", "Recombine", "Mesh", "")  # as saved by the global switch
        folder.Recombine = True
        path = os.path.join(self.tmp.name, "t.FCStd")
        self.doc.saveAs(path)
        App.closeDocument(self.doc.Name)
        self.doc = App.openDocument(path)
        folder = objects.find_study(self.doc).MeshSizesGroup
        self.assertFalse(hasattr(folder, "Recombine"))
        self.assertEqual(folder.RecombinationAlgorithm, "Blossom")
```

Extend `test_transfinite_items_survive_save_and_reload`: before `self.doc.saveAs(path)` add `objects.make_recombine(self.study, [a])`; at the end add `(rec,) = objects.recombine_items(study)`, `self.assertIsInstance(rec.Proxy, objects.Recombine)`.

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pixi run pytest tests/freecad_addon/test_study.py -k "recombin or transfinite_items" -q`
Expected: FAIL (`make_recombine` / `RecombinationAlgorithm` do not exist).

- [ ] **Step 3: Implement in `objects.py`**

- `RECOMBINATION_ALGORITHMS` next to `ALGORITHMS_3D`, same comment style.
- `MeshSizesFolder.__init__` and `onDocumentRestored` call `add_recombination_algorithm(obj)` instead of `add_recombine(obj)`; delete `add_recombine`. The property doc: `"Gmsh recombination algorithm for bodies in Recombine items"`. Set the enumeration with `folder.RecombinationAlgorithm = list(RECOMBINATION_ALGORITHMS)` only when the property was just added.
- `Recombine` proxy after `TransfiniteEdges`; `make_recombine` after `make_transfinite_edges`; `recombine_items` after `transfinite_edges()` (same `isinstance` filter pattern).
- Add `Recombine` to the tuple in `is_item`. `item_refs` needs no change (it reads `References`). `_size_text`: `if isinstance(item.Proxy, Recombine): return "recombine"` before the Transfinite Edges fallback.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `pixi run pytest tests/freecad_addon/test_study.py -q`
Expected: the new tests pass. Tests that still set `MeshSizesGroup.Recombine` (`test_recombine_goes_to_the_options`, `test_3d_recombine_needs_delaunay`, `test_structured_box_job_meshes_to_hexahedra`, `test_2d_structured_face_job_meshes_to_quads`) fail; Task 4 rewrites them. Note the failing names in the checkpoint.

- [ ] **Step 5: Format and lint**

Run: `pixi run format` then `pixi run lint`
Expected: `All checks passed!`

- [ ] **Step 6: Checkpoint**

Tell the user: the Recombine item and the algorithm setting exist; the old switch is removed from the folder; four job tests wait for Task 4. Suggested commit message:
`Add the Recombine item and the recombination algorithm setting`

---

### Task 2: `meshcommon.apply_recombine` and the 2D mesher

**Files:**
- Modify: `freecad_addon/emsolution/meshcommon.py` (new function after `apply_transfinite`)
- Modify: `freecad_addon/emsolution/mesher2d.py` (`build` line 89, `run_job` lines 92–98)
- Test: `tests/freecad_addon/test_mesher2d.py`

**Interfaces:**
- Consumes: job keys `"recombine"` (list of MAT_IDs, optional), `"bodies"` (each has `mat_id`, `name`), `"transfinite"["bodies"]` (each has `mat_id`).
- Produces (Task 3 extends it):
  - `meshcommon.apply_recombine(job, body_tags, dim) -> None`. `body_tags`: `{mat_id: [final entity tags of dimension dim]}` (the same dict passed to `apply_transfinite`). In 2D: `setRecombine(2, f)` for every face of every chosen body. In 3D: Task 3.
  - The 2D mesher prints `Recombined      <name>` after the `Structured` lines for each chosen body.

- [ ] **Step 1: Write the failing tests**

In `Mesher2DTest`:
- Add a `recombine=None` parameter to `run_job`; when not `None`, set `job["recombine"] = list(recombine)`.
- Change every existing `options={"Mesh.RecombineAll": 1}` to `recombine=[1]` (tests at lines ~336, 381, 391, 450). In `triangle_job`, replace the `recombine=0` parameter's use with `recombine=[1] if recombine else None` and drop the `options` argument.

New tests:

```python
    def test_recombine_gives_quads_only_in_the_chosen_body(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        write_rects(self.geo("vol_2.brep"), [(1, 0, 1, 1)])
        r = self.run_job(
            [self.body(1, "A", "vol_1.brep", 0.2), self.body(2, "B", "vol_2.brep", 0.2)],
            options={"Mesh.RecombinationAlgorithm": 3},
            recombine=[1],
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Recombined      A", r.stdout)
        self.open_msh()
        self.assertEqual(set(self.element_counts(1)), {"Quadrilateral 4"})
        self.assertEqual(set(self.element_counts(2)), {"Triangle 3"})

    def test_full_quad_algorithm_reaches_gmsh(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        counts = {}
        for alg in (1, 3):
            r = self.run_job([self.body(1, "A", "vol_1.brep", 0.2)], options={"Mesh.RecombinationAlgorithm": alg}, recombine=[1])
            self.assertEqual(r.returncode, 0, r.stderr)
            gmsh.initialize()
            try:
                gmsh.option.setNumber("General.Terminal", 0)
                gmsh.open(os.path.join(self.dir, "pre_geom2D.msh"))
                counts[alg] = self.element_counts(1)
            finally:
                gmsh.finalize()
        self.assertEqual(set(counts[3]), {"Quadrilateral 4"})
        self.assertGreater(counts[3]["Quadrilateral 4"], sum(counts[1].values()), "full-quad splits into more quads")

    def test_job_without_recombine_key_has_only_triangles(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        r = self.run_job([self.body(1, "A", "vol_1.brep", 0.2)], options={"Mesh.RecombinationAlgorithm": 1})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        self.assertEqual(set(self.element_counts(1)), {"Triangle 3"})
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pixi run pytest tests/freecad_addon/test_mesher2d.py -q`
Expected: FAIL — the recombine tests get triangles (nothing reads `"recombine"` yet).

- [ ] **Step 3: Implement `apply_recombine(job, body_tags, dim)` in `meshcommon.py` (2D part) and call it in `mesher2d.build`**

Call `apply_recombine(job, body_faces, 2)` right after `apply_transfinite(...)`; import it in the existing `from meshcommon import ...` line (append to the end of the name list, no reordering). For `dim == 2`: chosen = `job.get("recombine", [])`; `setRecombine(2, f)` for each face of each chosen MAT_ID (`dict.fromkeys` to keep order and avoid repeats). In `run_job` print `f"Recombined      {name}"` for each body whose `mat_id` is in `job.get("recombine", [])`.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `pixi run pytest tests/freecad_addon/test_mesher2d.py -q`
Expected: all pass (including the moved structured/triangle tests).

- [ ] **Step 5: Format and lint**

Run: `pixi run format` then `pixi run lint`
Expected: `All checks passed!`

- [ ] **Step 6: Checkpoint**

Tell the user: 2D jobs now recombine only the chosen bodies; the algorithm option reaches Gmsh. Suggested commit message:
`Recombine only the chosen bodies in 2D jobs`

---

### Task 3: 3D face rules in `apply_recombine` and the 3D mesher

**Files:**
- Modify: `freecad_addon/emsolution/meshcommon.py` (`apply_recombine`; remove the temporary fix: the `setRecombine` lines in `apply_transfinite` and the `if dim == 3: gmsh.option.setNumber("Mesh.RecombineAll", 0)` lines in `run`)
- Modify: `freecad_addon/emsolution/mesher.py` (`build` line 82, `run_job` lines 85–93)
- Test: `tests/freecad_addon/test_mesher.py`

**Interfaces:**
- Consumes: `apply_recombine` from Task 2; job keys `"volumes"` (`mat_id`, `name`), `"transfinite"["bodies"]`, `"options"["Mesh.Algorithm3D"]` (missing = 1, Gmsh's default).
- Produces: `apply_recombine` handles `dim == 3` as below. The 3D mesher prints `Recombined      <name>` like the 2D one.

- [ ] **Step 1: Write the failing tests**

In `MesherTest`:
- Add `recombine=None` to `run_job` (same as Task 2).
- `test_structured_box_with_recombine_has_only_hexahedra` and `test_structured_box_next_to_unstructured_box_gets_pyramids`: replace `"Mesh.RecombineAll": 1` with `recombine=[1]` (keep `"Mesh.Algorithm3D": 1` in the second).
- Replace `test_recombine_leaves_faces_between_unstructured_bodies_triangles` with the version below.
- Add a helper `def structured_boxes(self, *names_ids_x)` returning a `"transfinite"` dict with one body per `(name, mat_id, x)` and one edge item per box (`self.edge_item(f"tedge_{i}", box_lines(x), 3)`).

```python
    def three_boxes(self):
        for i, x in enumerate((0, 1, 2), 1):
            write_box(self.geo(f"vol_{i}.brep"), x, 0, 0, 1, 1, 1)
        return [self.vol(1, "Core", "vol_1.brep"), self.vol(2, "Air", "vol_2.brep"), self.vol(3, "Coil", "vol_3.brep")]

    def test_faces_between_two_tet_bodies_stay_triangles_with_a_note(self):
        r = self.run_job(self.three_boxes(), options={"Mesh.Algorithm3D": 1}, transfinite=self.structured_box(), recombine=[1, 2, 3])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("NOTE: recombine: faces between Air and Coil stay triangles", r.stderr)
        self.open_msh()
        self.assertEqual(self.element_counts(1), {"Hexahedron 8": 27})
        self.assertIn("Pyramid 5", self.element_counts(2))
        self.assertIn("Pyramid 5", self.element_counts(3))  # Coil's outside faces are quads

    def test_only_the_structured_body_chosen_next_to_two_tet_bodies(self):
        r = self.run_job(self.three_boxes(), transfinite=self.structured_box(), recombine=[1])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("NOTE: recombine", r.stderr)
        self.open_msh()
        self.assertEqual(self.element_counts(1), {"Hexahedron 8": 27})
        self.assertEqual(set(self.element_counts(3)), {"Tetrahedron 4"})

    def test_unstructured_box_alone_gets_pyramids(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        r = self.run_job([self.vol(1, "Air", "vol_1.brep", 0.3)], recombine=[1])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        self.assertIn("Pyramid 5", self.element_counts(1))

    def test_body_inside_a_tet_body_stays_tetrahedra_with_a_note(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 3, 3, 3)
        write_box(self.geo("vol_2.brep"), 1, 1, 1, 1, 1, 1)  # fully inside: every face shared with Air
        r = self.run_job([self.vol(1, "Air", "vol_1.brep"), self.vol(2, "Coil", "vol_2.brep", 0.3)], recombine=[2])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("NOTE: recombine: Coil has no face that can be recombined", r.stderr)
        self.open_msh()
        self.assertEqual(set(self.element_counts(2)), {"Tetrahedron 4"})

    def test_structured_body_not_chosen_next_to_a_chosen_structured_body_is_an_error(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_box(self.geo("vol_2.brep"), 1, 0, 0, 1, 1, 1)
        tf = self.structured_boxes(("Core", 1, 0), ("Yoke", 2, 1))
        r = self.run_job([self.vol(1, "Core", "vol_1.brep"), self.vol(2, "Yoke", "vol_2.brep")], transfinite=tf, recombine=[1])
        self.assertEqual(r.returncode, 1)
        last = r.stderr.strip().splitlines()[-1]
        self.assertTrue(last.startswith("ERROR: recombine: Yoke is structured"), last)
        self.assertIn("Core", last)

    def test_quads_next_to_tets_need_delaunay(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_box(self.geo("vol_2.brep"), 1, 0, 0, 1, 1, 1)
        r = self.run_job(
            [self.vol(1, "Core", "vol_1.brep"), self.vol(2, "Air", "vol_2.brep")],
            options={"Mesh.Algorithm3D": 10},
            transfinite=self.structured_box(),
            recombine=[1],
        )
        self.assertEqual(r.returncode, 1)
        self.assertIn("Delaunay", r.stderr.strip().splitlines()[-1])

    def test_structured_box_alone_meshes_with_hxt(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        r = self.run_job([self.vol(1, "Core", "vol_1.brep")], options={"Mesh.Algorithm3D": 10}, transfinite=self.structured_box(), recombine=[1])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        self.assertEqual(self.element_counts(1), {"Hexahedron 8": 27})
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pixi run pytest tests/freecad_addon/test_mesher.py -k "recombine or pyramids or hexahedra or note or delaunay or hxt or chosen" -q`
Expected: FAIL — no NOTE lines, no RC2/RC3 errors; with the temporary fix still in, chosen unstructured bodies get no quads.

- [ ] **Step 3: Implement the 3D part of `apply_recombine` and call it in `mesher.build`**

Call `apply_recombine(job, body_vols, 3)` right after `apply_transfinite(...)` (import as in Task 2). Remove the temporary fix (see Files). The 3D algorithm, per the spec's section 7 table:

```
chosen     = set(job.get("recombine", []))
structured = {b["mat_id"] for b in job["transfinite"]["bodies"]} (empty when no "transfinite")
kind(vol)  = "hex" if its mat_id in chosen & structured, "stet" if in structured only, else "tet"
name(vol)  = the volume's body name from job["volumes"]
candidates = boundary faces (getBoundary(..., combined=False, oriented=False), abs tags) of the chosen bodies' volumes, in order, no repeats
for each face: sides = getAdjacencies(2, face)[0]
    kinds = [kind(v) for v in sides]
    ok = "stet" not in kinds and kinds.count("tet") <= 1
    if ok: keep the face
    elif "hex" in kinds: raise JobError("recombine: <stet body> is structured and touches recombined structured body <hex body>; add <stet body> to a Recombine item too")
    else: remember the (sorted) pair of body names; drop the face
one _note per remembered pair: "recombine: faces between <A> and <B> stay triangles (a quad face there would need pyramids on both sides)"
for each chosen body with no kept face: _note("recombine: <name> has no face that can be recombined; it stays all triangles")
if any kept face has a "tet" side and job.get("options", {}).get("Mesh.Algorithm3D", 1) != 1:
    raise JobError("recombine: quad faces next to tetrahedra need the Delaunay volume algorithm")
setRecombine(2, face) for each kept face
```

In `mesher.run_job` print `Recombined      <name>` like the 2D mesher.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `pixi run pytest tests/freecad_addon/test_mesher.py tests/freecad_addon/test_mesher2d.py -q`
Expected: all pass.

- [ ] **Step 5: Format and lint**

Run: `pixi run format` then `pixi run lint`
Expected: `All checks passed!`

- [ ] **Step 6: Checkpoint**

Tell the user: 3D jobs recombine only chosen bodies, faces Gmsh cannot recombine stay triangles with a NOTE, the structured-neighbour and Delaunay cases are errors, and the temporary fix is gone. Suggested commit message:
`Recombine chosen bodies in 3D; leave faces between tet bodies as triangles`

---

### Task 4: Job writer

**Files:**
- Modify: `freecad_addon/emsolution/jobwriter.py` (`check` lines 70–73, `mesh_options` lines 141–157, `write_job` after the `transfinite` block ~line 231)
- Test: `tests/freecad_addon/test_study.py`

**Interfaces:**
- Consumes: `objects.recombine_items`, `objects.subs_by_body`, `objects.RECOMBINATION_ALGORITHMS`, folder `RecombinationAlgorithm` (Task 1).
- Produces: job `options["Mesh.RecombinationAlgorithm"]` (always, 2D and 3D); job `"recombine"`: MAT_IDs of included bodies in any Recombine item, in the order of the job's `volumes` / `bodies`, no repeats; key absent when empty. No `Mesh.RecombineAll`. The old Delaunay check in `check` is deleted.

- [ ] **Step 1: Write the failing tests**

In `tests/freecad_addon/test_study.py`:
- `test_mesh_settings_go_to_the_job`: set `settings.RecombinationAlgorithm = "Simple full-quad"` and add `"Mesh.RecombinationAlgorithm": 2` to the expected dict.
- Delete `test_recombine_goes_to_the_options` and `test_3d_recombine_needs_delaunay`.
- `test_structured_box_job_meshes_to_hexahedra` and `test_2d_structured_face_job_meshes_to_quads`: replace `...MeshSizesGroup.Recombine = True` with `objects.make_recombine(<study>, [a])`.
- New:

```python
    def test_recombine_items_go_to_the_job(self):
        a, b, c, d = self.box("A"), self.box("B", 10), self.box("C", 20), self.box("D", 40)
        self.include(a, b, c)  # D is outside the main geometry: skipped
        objects.make_recombine(self.study, [c, a, d])
        objects.make_recombine(self.study, [a])  # twice: listed once
        self.study.MeshSizesGroup.VolumeAlgorithm = "HXT"  # no longer refused here
        with open(jobwriter.write_job(self.study), encoding="utf-8") as fh:
            job = json.load(fh)
        ids = {v["name"]: v["mat_id"] for v in job["volumes"]}
        self.assertEqual(job["recombine"], [ids["A"], ids["C"]])
        self.assertEqual(job["options"]["Mesh.RecombinationAlgorithm"], 1)
        self.assertNotIn("Mesh.RecombineAll", job["options"])

    def test_job_without_recombine_items_has_no_recombine_key(self):
        self.include(self.box("A"))
        with open(jobwriter.write_job(self.study), encoding="utf-8") as fh:
            self.assertNotIn("recombine", json.load(fh))

    def test_2d_job_gets_recombine_and_meshes_quads_only_there(self):
        a, b = self.face("A"), self.face("B")
        b.Placement.Base = App.Vector(10, 0, 0)
        study = self.make_2d_study(a, b)
        study.MeshSizesGroup.RecombinationAlgorithm = "Blossom full-quad"
        objects.make_recombine(study, [a])
        path = jobwriter.write_job(study)
        r = subprocess.run([sys.executable, MESHER2D, path], capture_output=True, encoding="utf-8", errors="replace")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("Recombined      A", r.stdout)
        self.assertEqual(msh_element_types(os.path.join(self.tmp.name, "pre_geom2D.msh"), 2), {2, 3}, "triangles and quads")
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pixi run pytest tests/freecad_addon/test_study.py -k "recombine or mesh_settings or hexahedra or quads" -q`
Expected: FAIL (no `recombine` key, no algorithm option).

- [ ] **Step 3: Implement in `jobwriter.py`**

- `check`: delete the `settings.Recombine` / Delaunay block (lines 70–73).
- `mesh_options`: replace the `Recombine` lines with `opts["Mesh.RecombinationAlgorithm"] = objects.RECOMBINATION_ALGORITHMS[settings.RecombinationAlgorithm]` (both dimensions).
- `write_job`: after the `transfinite` block, collect body names from `objects.subs_by_body(item)` over `objects.recombine_items(study)`; write `job["recombine"]` as the MAT_IDs of `volumes` (job order) whose body is in that set, only when not empty.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `pixi run pytest tests/freecad_addon/test_study.py -q`
Expected: all pass.

- [ ] **Step 5: Format and lint**

Run: `pixi run format` then `pixi run lint`
Expected: `All checks passed!`

- [ ] **Step 6: Checkpoint**

Tell the user: Studies now write the Recombine bodies and the algorithm into the job; the old FreeCAD-side Delaunay check is gone (the mesher checks it exactly). Suggested commit message:
`Write Recombine bodies and the recombination algorithm to the job`

---

### Task 5: GUI — command, icon, item panel, mesh settings

**Files:**
- Create: `freecad_addon/icons/recombine.svg`
- Modify: `freecad_addon/emsolution/commands.py` (new class after `AddTransfiniteEdges` ~line 222, `COMMANDS` ~line 250)
- Modify: `freecad_addon/emsolution/taskpanels.py` (`MeshSettings` lines 256–303, `ItemPanel` lines 862–955)
- Test: `tests/freecad_addon/gui_smoke.py`

**Interfaces:**
- Consumes: `objects.make_recombine`, `objects.Recombine`, `objects.recombine_items`, folder `RecombinationAlgorithm` (Task 1).
- Produces: FreeCAD command `EMS_Recombine` (after `EMS_TransfiniteEdges` in `COMMANDS`, so it lands in the toolbar and menu through `commands.NAMES`).

- [ ] **Step 1: Update the GUI smoke test (it is the failing test)**

In `tests/freecad_addon/gui_smoke.py`, replace `second.MeshSizesGroup.Recombine = True` (~line 492) with:

```python
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(doc.Name, section.Name)
    Gui.runCommand("EMS_Recombine")
    (rc,) = objects.recombine_items(second)
    assert rc.References == [(section, ("",))], rc.References
    second.MeshSizesGroup.RecombinationAlgorithm = "Blossom full-quad"
```

Change the cleanup loop to `for item in (tb, te, rc):` and replace `second.MeshSizesGroup.Recombine = False` with `second.MeshSizesGroup.RecombinationAlgorithm = "Blossom"`. If the smoke test opens the Mesh Sizes folder panel elsewhere, assert the panel has a `RecombinationAlgorithm` entry in `MeshSettings.algorithms`.

- [ ] **Step 2: Run the smoke test to verify it fails**

Run:
```
pixi run freecad tests\freecad_addon\gui_smoke.py
Get-Content "$env:TEMP\ems_gui_smoke.txt"
```
Expected: FAIL — `EMS_Recombine` is not a command.

- [ ] **Step 3: Implement**

- `commands.py`: `class AddRecombine(_StudyCommand)` like `AddTransfiniteBody` without corners: `Pixmap` `icon("recombine")`, `MenuText` `"Recombine"`, `ToolTip` `"Mesh the selected bodies with quads (2D) or quad faces and hexahedra (3D)"`; `Activated` picks `taskpanels.selected_bodies()`, warns `"Select one or more bodies first."` when empty, `gate(...)`, then `_create(study, "Add Recombine", lambda: objects.make_recombine(study, bodies))`. Register as `"EMS_Recombine": AddRecombine()` right after `EMS_TransfiniteEdges`.
- `icons/recombine.svg`: same canvas and stroke style as `transfinitebody.svg`; picture: a square split into four quads.
- `taskpanels.MeshSettings`: delete the `self.recombine` checkbox, its `toggled` connection and `Recombine=` in `values()`. Add `("RecombinationAlgorithm", "Recombination algorithm")` to the tuple in the `self.algorithms` loop; give that combo the tooltip `"Gmsh algorithm for bodies in Recombine items. Full-quad gives only quads but more of them."`.
- `taskpanels.ItemPanel`: a `Recombine` branch next to `TransfiniteBody`: `self.pick, label = lambda: [(b, "") for b in selected_bodies()], "Bodies"`; the docstring lists the Recombine item. `accept` needs no change (`References = list(self.current)`).

- [ ] **Step 4: Run the smoke test to verify it passes**

Run the two commands from Step 2.
Expected: the log ends with the smoke test's success line and contains `2D transfinite mesh ok`.

- [ ] **Step 5: Format and lint**

Run: `pixi run format` then `pixi run lint`
Expected: `All checks passed!`

- [ ] **Step 6: Checkpoint**

Tell the user: the Recombine button, its panel and the algorithm combo are in FreeCAD; ask them to try it on `C:\Users\eskan\OneDrive\Desktop\delme\TransFreeCAD\Unnamed.FCStd` (Core in a Recombine item, then Core + Air). Suggested commit message:
`Add the Recombine command, icon and recombination algorithm setting to the GUI`

---

### Task 6: Point the transfinite docs here and run everything

**Files:**
- Modify: `docs/superpowers/specs/2026-10-15-transfinite-mesh-design.md` (decision 6, R8, section 5 `Recombine` row, section 7 options line, section 8 RecombineAll bullet)
- Modify: `docs/superpowers/plans/2026-10-15-transfinite-mesh.md` (header Goal/Architecture and the Global Constraints lines that mention `Recombine` / `RecombineAll`)

- [ ] **Step 1: Mark the replaced parts**

At each place listed above add one line: `Replaced by [2026-10-16-recombine-design.md](2026-10-16-recombine-design.md): per-body Recombine item.` (relative link from each file's folder). Do not rewrite the old text.

- [ ] **Step 2: Run the whole suite**

Run: `pixi run test`
Expected: all tests pass.

- [ ] **Step 3: Lint and check the diff**

Run: `pixi run lint`, then `git diff --stat`
Expected: `All checks passed!`; only the files named in Tasks 1–6 changed (plus the ones already modified before this work started).

- [ ] **Step 4: Checkpoint**

Tell the user the feature is done and what to try in FreeCAD. Suggested commit message:
`Point the transfinite spec and plan to the per-body Recombine design`
