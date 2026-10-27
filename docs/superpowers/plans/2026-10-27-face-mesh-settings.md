# Structured Mesh on Chosen Faces Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** In 2D Studies, Transfinite Body and Recombine take picked faces (`FaceN`) of a body as well as whole bodies.

**Architecture:** One helper in `objects.py` turns an item's references into "structured faces per body". Validation,
the job writer and the panels use it. The job carries picked faces as BREP files (the existing sub-element file
pattern), and the Gmsh side maps them through the fragment like corner and edge files. Whole-body references keep
today's job shape and mesh.

**Tech Stack:** FreeCAD 1.1 (Python 3.11), Gmsh Python API, unittest/pytest via Pixi.

**Spec:** `docs/superpowers/specs/2026-10-27-face-mesh-settings-design.md`

## Global Constraints

- Run everything through Pixi: `pixi run -e addon test-addon`; one file: `pixi run -e addon pytest tests/freecad_addon/test_study.py -q -p no:cacheprovider -k <name>`.
- `meshcommon.py`, `mesher.py`, `mesher2d.py` run outside FreeCAD: never import FreeCAD there. GUI code only in `taskpanels.py` / `commands.py`.
- Ruff only, line length 120, double quotes; `pixi run format` on changed files; `pixi run lint` must pass. Never reorder imports.
- Never `--no-verify`. Commit message ends with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- 2D only. In 3D Studies everything stays whole-body (panels, job, mesher).
- G4: a document with only whole-body references writes the same job keys and meshes the same as before. Existing tests must pass unchanged.
- Materials and MAT_IDs stay per body.
- Messages name body and face as `stator_cell_fragments Face2` / `A.Face2` style, never a BREP file name alone or a Gmsh tag.

## Review Focus

- Face references on Transfinite Body or Recombine in a **3D** Study (scripted, or an old 2D item moved): Validate Study refuses with one clear message, nothing reaches the mesher. Test in Task 1.
- One item holding a **whole body and a face of the same body**: the whole body wins (all faces), no duplicate error, no face file. Tests in Task 1 and Task 2.
- The **same face picked twice** in one item: no error, one face entry. Test in Task 2.
- Recombine with the whole body in one item and a face of it in another: whole body only, no `recombine_faces` entry. Test in Task 2.
- A picked face whose edge is **split by a touching body** (extra boundary point): it is still structured, using the points where the boundary turns, and the NOTE names body and face. Test in Task 3.

---

### Task 1: Structured faces per body, and validation (V1, V2, V4, V5, V6, 3D refusal)

**Files:**
- Modify: `freecad_addon/emsolution/objects.py` (near `subs_by_body`, line ~884)
- Modify: `freecad_addon/emsolution/validation.py` (`_links` ~110, `_transfinite` ~409)
- Test: `tests/freecad_addon/test_study.py` (validation tests near line 708)

**Interfaces:**
- Produces: `objects.face_picks(item) -> list[tuple[body, list[str]]]` in reference order, one entry per body. An
  empty list means the whole body: a `(body, "")` reference anywhere in the item wins over its face references.
  Otherwise the sorted-by-index, de-duplicated `FaceN` names. Non-`Face` subs are ignored (Corners are a separate
  property).
- Produces: `objects.structured_faces(body, faces) -> list[str]`: `faces` if not empty, else
  `[f"Face{i}" for i in 1..len(body.Shape.Faces)]`.

- [ ] **Step 1: Write the failing tests** in `test_study.py`, in the class that has `face`, `make_2d_study`, `all_edges`.
  Add a helper `two_blocks(self, name)`: a `Part::Feature` whose shape is
  `Part.makePlane(10, 10).generalFuse([Part.makePlane(10, 10, App.Vector(10, 0, 0))])[0]` (two faces sharing the
  edge x = 10), and `face_at(self, body, x, y) -> "FaceN"` (the face whose `CenterOfMass` is nearest (x, y)), and
  `face_edges(self, body, face) -> [(body, "EdgeN")]` (edges of that face by `isSame` against `body.Shape.Edges`).

```python
def test_face_picks_whole_body_wins_over_its_faces(self):
    b = self.two_blocks("B")
    study = self.make_2d_study(b)
    t = objects.make_transfinite_body(study, [b])
    t.References = [(b, "Face2"), (b, ""), (b, "Face2")]
    self.assertEqual(objects.face_picks(t), [(b, [])])
    t.References = [(b, "Face2"), (b, "Face1"), (b, "Face2")]
    self.assertEqual(objects.face_picks(t), [(b, ["Face1", "Face2"])])

def test_picked_face_needs_only_its_own_edges(self):  # V2
    b = self.two_blocks("B")
    study = self.make_2d_study(b)
    right = self.face_at(b, 15, 5)
    t = objects.make_transfinite_body(study, [])
    t.References = [(b, right)]
    objects.make_transfinite_edges(study, 4, self.face_edges(b, right)[:3])
    self.assertStudyErrorIn(study, f"B {right} has edges without Transfinite Edges: ")
    objects.make_transfinite_edges(study, 4, self.face_edges(b, right)[3:])
    jobwriter.check(study)  # the left face's other edges are not required

def test_face_in_two_transfinite_bodies_is_refused(self):  # V1, face/face and whole/face
    b = self.two_blocks("B")
    study = self.make_2d_study(b)
    objects.make_transfinite_edges(study, 4, self.all_edges(b))
    right = self.face_at(b, 15, 5)
    t1 = objects.make_transfinite_body(study, [b])
    t2 = objects.make_transfinite_body(study, [])
    t2.References = [(b, right)]
    self.assertStudyErrorIn(study, f"B.{right} is in Transfinite Body {t1.Label} and {t2.Label}.")

def test_faces_of_one_body_in_two_transfinite_bodies_are_fine(self):
    b = self.two_blocks("B")
    study = self.make_2d_study(b)
    objects.make_transfinite_edges(study, 4, self.all_edges(b))
    for x in (5, 15):
        objects.make_transfinite_body(study, []).References = [(b, self.face_at(b, x, 5))]
    jobwriter.check(study)

def test_missing_face_on_transfinite_body_and_recombine_is_refused(self):  # V4, V5
    b = self.two_blocks("B")
    study = self.make_2d_study(b)
    objects.make_transfinite_body(study, []).References = [(b, "Face7")]
    self.assertStudyErrorIn(study, "Transfinite Body TransfiniteBody: body B has no Face7. Reselect it.")
    objects.make_recombine(study, []).References = [(b, "Face9")]
    self.assertStudyErrorIn(study, "Recombine Recombine: body B has no Face9. Reselect it.")

def test_whole_body_in_two_recombine_items_is_still_fine(self):  # V5, G4
    b = self.two_blocks("B")
    study = self.make_2d_study(b)
    objects.make_recombine(study, [b])
    objects.make_recombine(study, []).References = [(b, "Face1")]
    jobwriter.check(study)

def test_corner_on_no_structured_face_of_its_item_is_refused(self):  # V6
    b = self.two_blocks("B")
    study = self.make_2d_study(b)
    right = self.face_at(b, 15, 5)
    objects.make_transfinite_edges(study, 4, self.face_edges(b, right))
    far = next(f"Vertex{i}" for i, v in enumerate(b.Shape.Vertexes, 1) if v.Point.x < 1e-6)  # on the left face only
    t = objects.make_transfinite_body(study, [], [(b, far)])
    t.References = [(b, right)]
    self.assertStudyErrorIn(study, f"Transfinite Body {t.Label}: corner B.{far} is on none of its structured faces.")

def test_face_picks_in_a_3d_study_are_refused(self):
    a = self.box("A")
    self.include(a)
    objects.make_transfinite_edges(self.study, 3, self.all_edges(a))
    objects.make_transfinite_body(self.study, []).References = [(a, "Face1")]
    objects.make_recombine(self.study, []).References = [(a, "Face2")]
    self.assertStudyError("Transfinite Body TransfiniteBody: pick whole solids in a 3D Study (A.Face1).")
    self.assertStudyError("Recombine Recombine: pick whole solids in a 3D Study (A.Face2).")
```

  `assertStudyErrorIn(study, text)`: like the existing `assertStudyError` but for the given Study (add it next to
  `assertStudyError` if that one only uses `self.study`).

- [ ] **Step 2: Run them, expect FAIL**

Run: `pixi run -e addon pytest tests/freecad_addon/test_study.py -q -p no:cacheprovider -k "face_picks or picked_face or face_in_two or faces_of_one or missing_face or two_recombine or no_structured_face or 3d_study_are"`
Expected: FAIL (`face_picks` missing; messages missing).

- [ ] **Step 3: Implement `face_picks` and `structured_faces` in `objects.py`.**

- [ ] **Step 4: Change `validation._transfinite(study, bodies, r)`** to work per (body, face):
  - Owner map keyed `(body.Name, face)` over `structured_faces(b, faces)` for each `face_picks(t)` entry. On a clash:
    when both items hold the whole body keep today's text `Body {b.Label} is in Transfinite Body {X} and {Y}.`;
    otherwise `{b.Label}.{face} is in Transfinite Body {X} and {Y}.`, refs `[(b, face)]`. Report each clash once.
  - Required edges (V2): the edges of the structured faces only, matched by `isSame` against `b.Shape.Edges`.
    Whole-body owner: today's message unchanged. Face owners: `Transfinite Body {t.Label}: {b.Label} {face} has edges
    without Transfinite Edges: Edge3, Edge5`.
  - `loose_pieces` check (V3) stays per body, when any face of it is structured.
  - V6: for each corner `(b, VertexN)` of item `t` whose body is in `t`'s references and in the Study: error unless the
    vertex lies on (`isSame` with a vertex of) one of `t`'s structured faces of `b`. Text:
    `Transfinite Body {t.Label}: corner {b.Label}.{VertexN} is on none of its structured faces.`
  - 3D: in `_links` (or a new `_face_picks_3d(study, r)` called from `validate`), for each Transfinite Body or
    Recombine item in a 3D Study with any `FaceN` reference: `{kind} {item.Label}: pick whole solids in a 3D Study
    ({b.Label}.{FaceN}, ...).`
  - V4/V5 missing faces are already reported by `_links` ("has no {sub}"); the tests only pin that. `_transfinite`
    skips a picked face the body does not have, so it raises nothing of its own for it.

- [ ] **Step 5: Run the Step 2 command, expect PASS; then `pixi run -e addon test-addon`, expect all pass.**

- [ ] **Step 6: Commit** — `git add freecad_addon/emsolution/objects.py freecad_addon/emsolution/validation.py tests/freecad_addon/test_study.py`, message `Face picks: structured faces per body and their validation`.

---

### Task 2: Job writer: picked faces and per-item corners

**Files:**
- Modify: `freecad_addon/emsolution/jobwriter.py` (`transfinite_items` ~84, `write_job` ~246-272)
- Test: `tests/freecad_addon/test_study.py` (job tests near line 684)

**Interfaces:**
- Consumes: `objects.face_picks`, `objects.structured_faces` (Task 1).
- Produces (job.json, read by Task 3):
  - `job["transfinite"]["bodies"]`: one entry per (Transfinite Body item, body), in item then reference order:
    `{"name": volume_name, "mat_id": int, "corner_files": [...]}` plus, only for face picks,
    `"faces": [{"face": "Face2", "file": "geometry/tface_<k>_<n>.brep"}]`. `k` = entry number from 1. Corner files
    are `geometry/corner_<k>_<n>.brep` and hold only that item's corners on that body.
  - `job["recombine_faces"]`: `[{"name": volume_name, "mat_id": int, "face": "Face2", "file": "geometry/rface_<k>_1.brep"}]`,
    `k` from 1, only for faces of bodies not already in `job["recombine"]`; key absent when empty.
  - `transfinite_items(study, bodies)` returns `structured = [(item, body, faces, corners)]` (`faces` as in
    `face_picks`, `corners` = that item's vertex names on that body), `edges` unchanged.

- [ ] **Step 1: Write the failing tests**

```python
def test_picked_faces_go_to_the_job(self):
    b = self.two_blocks("B")
    study = self.make_2d_study(b)
    right = self.face_at(b, 15, 5)
    objects.make_transfinite_edges(study, 4, self.face_edges(b, right))
    t = objects.make_transfinite_body(study, [])
    t.References = [(b, right), (b, right)]  # twice: one entry
    objects.make_recombine(study, []).References = [(b, right)]
    with open(jobwriter.write_job(study), encoding="utf-8") as fh:
        job = json.load(fh)
    (entry,) = job["transfinite"]["bodies"]
    self.assertEqual(entry["faces"], [{"face": right, "file": "geometry/tface_1_1.brep"}])
    self.assertEqual(job["recombine_faces"], [{"name": "B", "mat_id": entry["mat_id"], "face": right, "file": "geometry/rface_1_1.brep"}])
    self.assertNotIn("recombine", job)
    shape = Part.Shape()
    shape.read(self.scratch_of(study, "geometry", "tface_1_1.brep"))
    self.assertEqual(shape.ShapeType, "Face")
    self.assertAlmostEqual(shape.CenterOfMass.x, 15)

def test_whole_body_and_its_face_in_one_item_write_the_whole_body(self):
    b = self.two_blocks("B")
    study = self.make_2d_study(b)
    objects.make_transfinite_edges(study, 4, self.all_edges(b))
    objects.make_transfinite_body(study, []).References = [(b, "Face1"), (b, "")]
    objects.make_recombine(study, [b])
    objects.make_recombine(study, []).References = [(b, "Face1")]
    with open(jobwriter.write_job(study), encoding="utf-8") as fh:
        job = json.load(fh)
    self.assertNotIn("faces", job["transfinite"]["bodies"][0])
    self.assertNotIn("recombine_faces", job)

def test_corners_stay_with_their_item(self):
    b = self.two_blocks("B")
    study = self.make_2d_study(b)
    objects.make_transfinite_edges(study, 4, self.all_edges(b))
    left, right = self.face_at(b, 5, 5), self.face_at(b, 15, 5)
    shared = next(f"Vertex{i}" for i, v in enumerate(b.Shape.Vertexes, 1) if abs(v.Point.x - 10) < 1e-6)
    objects.make_transfinite_body(study, [], [(b, shared)]).References = [(b, left)]
    objects.make_transfinite_body(study, []).References = [(b, right)]
    with open(jobwriter.write_job(study), encoding="utf-8") as fh:
        first, second = json.load(fh)["transfinite"]["bodies"]
    self.assertEqual(first["corner_files"], ["geometry/corner_1_1.brep"])
    self.assertEqual(second["corner_files"], [])
```

  `scratch_of`:
  the existing `scratch` helper for a given Study (use `jobwriter.scratch_folder(study)`), add it if `scratch` is
  bound to `self.study`.

- [ ] **Step 2: Run, expect FAIL** — `pixi run -e addon pytest tests/freecad_addon/test_study.py -q -p no:cacheprovider -k "picked_faces_go or its_face_in_one_item or corners_stay"`.

- [ ] **Step 3: Implement** `transfinite_items` and the `write_job` changes with `export_subs` for face and corner
  files (prefixes `tface_<k>`, `corner_<k>`, `rface_<k>`). Whole-body entries get no `"faces"` key.

- [ ] **Step 4: Run Step 2 command, expect PASS; run `pixi run -e addon test-addon`** — `test_transfinite_items_go_to_the_job` (expects `corner_1_1.brep`) and `test_recombine_items_go_to_the_job` must pass unchanged.

- [ ] **Step 5: Commit** — `Face picks: picked faces and per-item corners in the job`.

---

### Task 3: Mesher: structure and recombine the picked faces

**Files:**
- Modify: `freecad_addon/emsolution/meshcommon.py` (`transfinite_files` ~71, `_set_face` ~129, `apply_transfinite` ~181, `apply_recombine` ~268)
- Modify: `freecad_addon/emsolution/mesher2d.py` (`build` ~73-134, `run_job` ~148)
- Modify: `freecad_addon/emsolution/mesher.py` (~55 and ~132: only the new import dims and return shape)
- Test: `tests/freecad_addon/test_mesher2d.py`

**Interfaces:**
- Consumes: the job keys from Task 2.
- Produces:
  - `meshcommon.FILE_DIMS = {"edge": 1, "corner": 0, "face": 2, "rface": 2}`; both meshers import each
    `transfinite_files` path with `FILE_DIMS[kind]`.
  - `transfinite_files(job, folder) -> [(kind, item, path)]`: edges, then corners, then `("face", (entry, face), path)`
    for each `"faces"` item of each body entry, then `("rface", entry, path)` for `job["recombine_faces"]`. Corner
    `item` is the body entry dict itself (corners are keyed by `id(entry)`, not by name, since names repeat).
  - `apply_transfinite(job, mapped, body_tags, dim) -> (curves, faces)`: `curves` as today
    (`{curve: (nodes, item name)}`); `faces` = set of final 2D tags made transfinite.
  - `apply_recombine(job, body_tags, dim, tf, mapped)`: `tf` is that tuple; `mapped` is the same list passed to
    `apply_transfinite` (it reads the `"rface"` rows).
  - `_set_face(face, chosen, curve_set, label)`: `label` replaces the body name and is `structured body {name}` for a
    whole body or `structured body {name} {FaceN}` for a picked face; message shape `"{label}: face at (x, y, z) ..."`
    unchanged.

- [ ] **Step 1: Write the failing tests** in `Mesher2DTest`. Helper `face_file(self, name, loop)`: `write_polygons(self.geo(f"{name}.brep"), [loop])`, returns `f"geometry/{name}.brep"`. The body file is two touching squares: `write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1), (1, 0, 1, 1)])`.

  Helper `face_types(self, x) -> dict[str, int]`: like `element_counts(1)`, but only for the entity of group 1 whose
  mesh nodes have mean x within 0.25 of `x` (an opened msh has no OCC geometry, so use the nodes).

```python
def test_only_the_picked_face_is_structured(self):
    write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1), (1, 0, 1, 1)])
    right = self.face_file("tface_1_1", [(1, 0), (2, 0), (2, 1), (1, 1)])
    tf = {"bodies": [{"name": "Core", "mat_id": 1, "corner_files": [], "faces": [{"face": "Face2", "file": right}]}],
          "edges": [self.edge_item("tedge_1", square_lines(1), 4)]}
    r = self.run_job([self.body(1, "Core", "vol_1.brep", size=0.1)], transfinite=tf, extra={"recombine_faces": [
        {"name": "Core", "mat_id": 1, "face": "Face2", "file": right}]})
    self.assertEqual(r.returncode, 0, r.stderr)
    self.assertIn("Structured      Core Face2", r.stdout)
    self.assertIn("Recombined      Core Face2", r.stdout)
    self.open_msh()
    self.assertEqual(self.face_types(1.5), {"Quadrilateral 4": 16})
    self.assertEqual(set(self.face_types(0.5)), {"Triangle 3"})
```

```python
def test_recombine_only_the_picked_face(self):
    # same body, no transfinite key, recombine_faces on Face2 only, RecombinationAlgorithm 1 (Blossom)
    # right square: quads (and maybe a few triangles from Blossom); left square: triangles only
```

```python
def test_picked_face_message_names_body_and_face(self):
    # pentagon Face2 [(1,0),(2,0),(2,1),(1.5,1.5),(1,1)] next to square Face1, no corners, edge counts that make
    # the turning points ambiguous (5 turning points): stderr contains "structured body Core Face2: face at ("
    # and "it needs 3 or 4"
```

```python
def test_picked_face_with_a_split_edge_uses_the_turning_points(self):
    # Review Focus: a second body (mat_id 2) [(1.4, 1, 0.2, 0.2)] touches Face2's top edge and splits it;
    # Face2 gets 6 boundary points; give the top edge 4 elements (split share); expect returncode 0 and the NOTE
    # "structured body Core Face2: face at (" ... "using the 4 where the boundary turns as corners" in stderr
```

```python
def test_face_file_outside_its_body_is_an_error(self):
    # face file is a square at (5, 5): stderr contains "structured body Core Face2: tface_1_1.brep did not merge with the body"
```

  Write the bodies of the outline tests from their comments, in the style of the tests near line 405-470.

- [ ] **Step 2: Run, expect FAIL** — `pixi run -e addon pytest tests/freecad_addon/test_mesher2d.py -q -p no:cacheprovider -k "picked_face or only_the_picked or face_file_outside"`.

- [ ] **Step 3: Implement in `meshcommon.py`:**
  - `FILE_DIMS`, the new `transfinite_files` order.
  - `apply_transfinite`: corners collected per `id(entry)`. For each body entry: with `"faces"`, take each face row's
    mapped 2D tags; every tag must be in `body_tags[mat_id]`, else `JobError(f"structured body {name} {face}: {file} did not merge with the body")`;
    structure those tags with label `structured body {name} {face}`. Without `"faces"`: today's behaviour and label.
    Return `(curves, faces)`.
  - `apply_recombine`: 2D recombined faces = whole-body faces from `job["recombine"]` + mapped `"rface"` tags (same
    merge check, label `recombine {name} {face}`). `_check_full_quad` gets the recombined faces not in the
    transfinite `faces` set (today: not in a structured body). 3D path unchanged (it receives `tf[0]`).
- [ ] **Step 4: Implement in `mesher2d.py` / `mesher.py`:** import with `FILE_DIMS[kind]`; unpack the new return;
  `run_job` prints `Structured      {name}` for whole entries and `Structured      {name} {face}` per picked face, and
  `Recombined      {name} {face}` per `recombine_faces` row after the whole-body lines.

- [ ] **Step 5: Run Step 2 command, expect PASS; then `pixi run -e addon test-addon`, expect all pass** (3D mesher tests included).

- [ ] **Step 6: Commit** — `Face picks: the mesher structures and recombines picked faces`.

---

### Task 4: End to end on a sample-like Study (A1, A2, A3)

**Files:**
- Test: `tests/freecad_addon/test_study.py`

**Interfaces:**
- Consumes: everything above through `jobwriter.write_job` and `MESHER2D`.

- [ ] **Step 1: Write the tests.** Helper `three_blocks(self)`: a `Part::Feature` "Core" from
  `generalFuse` of `Part.makePlane(10, 10)`, `Part.makePlane(10, 10, App.Vector(10, 0, 0))` and a pentagon face
  (20,0)-(30,0)-(30,10)-(25,13)-(20,10) (build it with `Part.Face(Part.makePolygon([...closed]))`). Helper
  `assert_no_inverted(self, msh)`: open with gmsh; for every 2D element, the shoelace area of its corner nodes; all
  areas non-zero and of one sign per face entity (signed area, not minSJ).

```python
def test_all_blocks_structured_with_corners_on_the_pentagon(self):  # A1
    core = self.three_blocks()
    study = self.make_2d_study(core)
    pent = self.face_at(core, 25, 5)
    corners = [self.vertex_at(core, x, y) for x, y in ((20, 0), (30, 0), (30, 10), (20, 10))]
    objects.make_transfinite_body(study, [core], [(core, v) for v in corners])
    # straight edges 4 elements; the two roof edges of the pentagon 2 each
    ...
    objects.make_recombine(study, [core])
    # run MESHER2D: returncode 0; msh_element_types(..., 2) == {3}; assert_no_inverted

def test_only_the_middle_block_structured(self):  # A2
    # Transfinite Body on the middle face only, edges of that face 4; Recombine on that face only
    # each final face: middle -> quads only; others -> triangles only; 5 nodes on x = 10 and on x = 20 shared

def test_recombine_on_one_face_only(self):  # A3
    # no transfinite; Recombine on the middle face; middle has quadrangles, the others triangles only
```

  `vertex_at(body, x, y) -> "VertexN"` helper next to `face_at`. Per-face element types: open the msh with gmsh and
  group elements by entity tag; identify the entity by the mean x of its nodes.

- [ ] **Step 2: Run** `pixi run -e addon pytest tests/freecad_addon/test_study.py -q -p no:cacheprovider -k "all_blocks or middle_block or one_face_only"` — expect PASS (Tasks 1-3 are in). If one fails, fix the cause in the owning module, not the test.

- [ ] **Step 3: Commit** — `Face picks: end-to-end tests on a three-block body`.

---

### Task 5: Panels pick faces in 2D; GUI smoke

**Files:**
- Modify: `freecad_addon/emsolution/taskpanels.py` (`ITEM_PICKS` ~986, `ItemPanel.__init__` ~1034, `accept` ~1151)
- Modify: `tests/freecad_addon/gui_smoke.py` (2D transfinite step ~985-1015, and its docstring step list)

**Interfaces:**
- Produces: `taskpanels.selected_face_picks(vertices: bool) -> list[tuple[body, str]]`: per selection, no sub-element
  → `(body, "")`; each `FaceN` → `(body, FaceN)`, or `(body, "")` when the body has exactly one face; each
  `VertexN` when `vertices` → `(body, VertexN)`; other subs dropped.
- Produces: `ITEM_PICKS_2D = {TransfiniteBody: (pick, label, hint), Recombine: (...)}` overriding the pick, list label
  and 2D hint of `ITEM_PICKS` in 2D Studies:
  - Transfinite Body: `lambda: selected_face_picks(True)`, `"Bodies, faces,\ncorner vertices"`,
    `"Click a face to structure that block, or select the body in the tree for all its faces. Clicked vertices become corners."`
  - Recombine: `lambda: selected_face_picks(False)`, `"Bodies, faces"`,
    `"Click a face to recombine that block, or select the body in the tree for all its faces."`

- [ ] **Step 1: Write the failing smoke steps** in the 2D section of `gui_smoke.py`, after the existing transfinite
  run and cleanup: add a two-face body (`generalFuse` as in Task 1) to the 2D Study's main objects, then

```python
Gui.Selection.clearSelection()
Gui.Selection.addSelection(doc.Name, blocks.Name, right)  # a face of the two-face body
Gui.runCommand("EMS_TransfiniteBody")
texts = [w.text() for w in opened[-1].form.findChildren(QtWidgets.QLabel)]
assert any(t.startswith("Click a face to structure that block") for t in texts), texts
ok()
(tb,) = objects.transfinite_bodies(second)
assert tb.References == [(blocks, (right,))], tb.References
Gui.Selection.clearSelection()
Gui.Selection.addSelection(doc.Name, blocks.Name)  # tree pick
Gui.runCommand("EMS_Recombine")
ok()
(rc,) = objects.recombine_items(second)
assert rc.References == [(blocks, ("",))], rc.References
Gui.Selection.clearSelection()
Gui.Selection.addSelection(doc.Name, section.Name, "Face1")  # one-face body: stored whole
Gui.runCommand("EMS_Recombine")
ok()
assert objects.recombine_items(second)[-1].References == [(section, ("",))]
```

  Then remove the added items and body so the rest of the smoke test sees the Study as before. Add one line to the
  module docstring's step list for this step.

- [ ] **Step 2: Run the smoke test, expect FAIL**: `pixi run -e addon freecad tests\freecad_addon\gui_smoke.py`, then the last line of `%TEMP%\ems_gui_smoke.txt` is `FAIL` naming the new assertion.

- [ ] **Step 3: Implement** `selected_face_picks` and `ITEM_PICKS_2D`; in `ItemPanel.__init__` use the 2D override
  when `study.Dimension == "2D"`. `accept` for Transfinite Body: `VertexN` refs → `Corners`, all others (`""` and
  `FaceN`) → `References`. The commands that open the panel with a preselection (`EMS_TransfiniteBody`,
  `EMS_Recombine` in `commands.py`) must use the same pick, so a preselected face stays a face; check how they
  call `self.pick` and change them only if they bypass it.

- [ ] **Step 4: Run the smoke test again**: last line `PASS` (a crash report on quit after PASS is normal). Then `pixi run -e addon test-addon`, all pass.

- [ ] **Step 5: Commit** — `Face picks: Transfinite Body and Recombine panels take faces in 2D`.

---

### Task 6: Finish

- [ ] **Step 1:** `pixi run format` (changed files only show in `git diff`), `pixi run lint`, `pixi run -e addon test-addon`: all clean.
- [ ] **Step 2:** In the spec, set `Status: implemented on feature/freecad-addon` and list the job keys as built if they differ from section 5.4. Commit `Spec: face picks implemented`.
