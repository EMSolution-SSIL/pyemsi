# Transfinite (Structured) Mesh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let the user mesh chosen bodies of a 2D or 3D Study as a structured Gmsh Transfinite grid, with a global Recombine switch for quads / hexahedra.

Replaced by [2026-10-16-recombine-design.md](../specs/2026-10-16-recombine-design.md): per-body Recombine item.

**Architecture:** Two new items in the Mesh Sizes folder (`TransfiniteBody`, `TransfiniteEdges`) and a `Recombine` Bool on the folder. `jobwriter` checks R1–R3 and R8 and writes a `"transfinite"` key plus `"Mesh.RecombineAll": 1` in `options`. Both mesher scripts import the edge and corner BREPs into their one `fragment` call and hand the mapped tags to one shared function, `meshcommon.apply_transfinite`, which checks R4–R7 and sets transfinite curves, surfaces and volumes.

**Tech Stack:** Python 3.11 (Pixi), FreeCAD 1.1 Python API, Gmsh Python API, unittest/pytest, PySide.

**Spec:** [docs/superpowers/specs/2026-10-15-transfinite-mesh-design.md](../specs/2026-10-15-transfinite-mesh-design.md)

## Global Constraints

- Run everything through Pixi: `pixi run pytest ...`, `pixi run python ...`. Never `pip install`.
- Format with `pixi run format`, check with `pixi run lint`. Line length is **120**; no trailing comma on a construct that fits on one line. Never run Black/isort or Ruff with overrides.
- **Never sort or reorder imports.** Add new imports next to related ones.
- Only format files you changed.
- `mesher.py`, `mesher2d.py` and `meshcommon.py` run in their own process: **never import FreeCAD** in them.
- A job without `"transfinite"` and without `"Mesh.RecombineAll"` must mesh exactly as today. Write the `"transfinite"` key only when the Study has transfinite items, and `"Mesh.RecombineAll"` only when Recombine is on.
  Replaced by [2026-10-16-recombine-design.md](../specs/2026-10-16-recombine-design.md): per-body Recombine item.
- Transfinite Edges count is in **elements**; the job writes `nodes = Elements + 1`.
- Distribution is `Uniform` (Gmsh `Progression`, coef 1) or `Bump` (Gmsh `Bump`, coef from the item). No Progression, no direction.
- Bad shape = **error and stop**: one `ERROR:` line naming the body (and face) and the reason. No fallback to an unstructured mesh.
- What the mesher fixes by itself after `fragment` (a split Uniform edge shares its elements by length; a face with more than 4 points gets corners where its boundary turns) is printed as one `NOTE:` line on **stderr**. The runner already shows stderr in FreeCAD's Report view as a warning; the runner is not changed.
- 3D + Recombine needs `VolumeAlgorithm == "Delaunay"` (checked with Gmsh: Frontal says "Cannot use frontal 3D algorithm with quadrangles on boundary", HXT says "only supports triangles").
  Replaced by [2026-10-16-recombine-design.md](../specs/2026-10-16-recombine-design.md): per-body Recombine item.
- **Never run `git commit`.** At each "Checkpoint" step, stop, tell the user what changed, ask them to check and test it, and suggest the commit message. Wait for their yes. (User rule; it overrides any "commit frequently" habit.)

## Review Focus

- Two touching structured bodies whose shared edge gets different Transfinite Edges settings must give a clear error, not a Gmsh crash. Pinned in Task 2.
- A touching body whose vertex splits a transfinite edge must keep the edge's total element count (not double it) and tell the user with a `NOTE:`; a split Bump edge is an error. Pinned in Task 2.
- Documents saved before this feature (no `Recombine` on the folder) must open and mesh as before. Pinned in Task 1 and Task 4.
- 3D Recombine with HXT or Frontal must be refused in FreeCAD before Gmsh runs. Pinned in Task 4.
- A structured face with a hole must give a clear error and never loop forever. Pinned in Task 2.

---

### Task 1: Transfinite items and the Recombine setting in `objects.py`

**Files:**
- Modify: `freecad_addon/emsolution/objects.py` (MeshSizesFolder ~line 68–89, after `MeshSize` ~line 185–194, `make_mesh_size` ~line 334, `mesh_sizes` ~line 350, `is_item` ~line 396, `item_refs`, `mesh_size_rows`)
- Test: `tests/freecad_addon/test_study.py`

**Interfaces:**
- Produces (used by Tasks 4 and 5):
  - `objects.TransfiniteBody` proxy; properties `References` (whole bodies, sub `""`), `Corners` (`(body, "VertexN")`)
  - `objects.TransfiniteEdges` proxy; properties `References` (`(body, "EdgeN")`), `Elements` (int, default 10, min 1), `Distribution` (`"Uniform"`/`"Bump"`), `BumpCoefficient` (float, default 0.5)
  - `objects.make_transfinite_body(study, bodies, corners=()) -> obj`
  - `objects.make_transfinite_edges(study, elements, edges, distribution="Uniform", coef=0.5) -> obj`
  - `objects.transfinite_bodies(study) -> list`, `objects.transfinite_edges(study) -> list`
  - `objects.mesh_sizes(study)` now returns **only** `MeshSize` items
  - `objects.add_recombine(folder)`; folder property `Recombine` (Bool, default False)

- [ ] **Step 1: Write the failing tests**

Add to `StudyTest` in `tests/freecad_addon/test_study.py`, after `test_folder_overview_rows`:

```python
    def test_transfinite_items_are_listed_with_mesh_sizes(self):
        a = self.box("A")
        self.include(a)
        size = objects.make_mesh_size(self.study, 1.5, [(a, "")])
        body = objects.make_transfinite_body(self.study, [a], [(a, "Vertex1")])
        edges = objects.make_transfinite_edges(self.study, 4, [(a, "Edge1"), (a, "Edge2")], "Bump", 0.2)
        self.assertEqual(objects.mesh_sizes(self.study), [size])
        self.assertEqual(objects.transfinite_bodies(self.study), [body])
        self.assertEqual(objects.transfinite_edges(self.study), [edges])
        self.assertTrue(objects.is_item(body) and objects.is_item(edges))
        self.assertEqual(objects.item_refs(body), [(a, ""), (a, "Vertex1")])
        self.assertEqual(
            objects.mesh_size_rows(self.study),
            [
                (size, [(a, "")], ["MeshSize", "1.5 mm", "A"]),
                (body, [(a, ""), (a, "Vertex1")], ["TransfiniteBody", "structured", "A, A.Vertex1"]),
                (edges, [(a, "Edge1"), (a, "Edge2")], ["TransfiniteEdges", "4 el, Bump 0.2", "A.Edge1, A.Edge2"]),
            ],
        )
        self.assertFalse(self.study.MeshSizesGroup.Recombine)

    def test_transfinite_items_survive_save_and_reload(self):
        a = self.box("A")
        self.include(a)
        objects.make_transfinite_body(self.study, [a])
        objects.make_transfinite_edges(self.study, 7, [(a, "Edge1")], "Bump", 0.3)
        path = os.path.join(self.tmp.name, "t.FCStd")
        self.doc.saveAs(path)
        App.closeDocument(self.doc.Name)
        self.doc = App.openDocument(path)
        study = objects.find_study(self.doc)
        (body,) = objects.transfinite_bodies(study)
        (edges,) = objects.transfinite_edges(study)
        self.assertIsInstance(body.Proxy, objects.TransfiniteBody)
        self.assertEqual((edges.Elements, edges.Distribution, edges.BumpCoefficient), (7, "Bump", 0.3))

    def test_old_mesh_sizes_folder_gets_recombine_on_load(self):
        self.study.MeshSizesGroup.removeProperty("Recombine")  # as saved before Recombine existed
        path = os.path.join(self.tmp.name, "t.FCStd")
        self.doc.saveAs(path)
        App.closeDocument(self.doc.Name)
        self.doc = App.openDocument(path)
        self.assertFalse(objects.find_study(self.doc).MeshSizesGroup.Recombine)
```

- [ ] **Step 2: Run them to see them fail**

Run: `pixi run pytest tests/freecad_addon/test_study.py -k "transfinite or recombine" -q`
Expected: FAIL with `AttributeError: module 'emsolution.objects' has no attribute 'make_transfinite_body'`.

- [ ] **Step 3: Add `Recombine` to the folder**

In `objects.py`, in `MeshSizesFolder.__init__`, after the `OptimizeNetgen` line add:

```python
        add_recombine(obj)

    def onDocumentRestored(self, obj):
        add_recombine(obj)  # documents saved before Recombine existed
```

Directly after the `MeshSizesFolder` class (before `FOLDERS = (`), add:

```python
def add_recombine(folder):
    if not hasattr(folder, "Recombine"):
        folder.addProperty("App::PropertyBool", "Recombine", "Mesh", "Quads and hexahedra where possible (Gmsh RecombineAll)")
```

- [ ] **Step 4: Add the two proxies**

After the `MeshSize` class add:

```python
class TransfiniteBody(_Proxy):
    def __init__(self, obj):
        obj.Proxy = self
        obj.addProperty("App::PropertyLinkSubListGlobal", "References", "EMSolution", "Bodies meshed as a structured grid")
        obj.addProperty(
            "App::PropertyLinkSubListGlobal",
            "Corners",
            "EMSolution",
            "Vertices used as corners of faces with more than 4 boundary points",
        )


class TransfiniteEdges(_Proxy):
    def __init__(self, obj):
        obj.Proxy = self
        obj.addProperty("App::PropertyLinkSubListGlobal", "References", "EMSolution", "Edges with a fixed element count")
        obj.addProperty("App::PropertyIntegerConstraint", "Elements", "EMSolution", "Elements on each edge")
        obj.Elements = (10, 1, 100000, 1)
        obj.addProperty("App::PropertyEnumeration", "Distribution", "EMSolution", "Node spacing along the edge")
        obj.Distribution = ["Uniform", "Bump"]
        obj.addProperty("App::PropertyFloat", "BumpCoefficient", "EMSolution", "Gmsh Bump coefficient; below 1 refines both ends")
        obj.BumpCoefficient = 0.5
```

- [ ] **Step 5: Add the make and list helpers, filter `mesh_sizes`**

After `make_mesh_size` add:

```python
def make_transfinite_body(study, bodies, corners=()):
    """bodies: list of bodies; corners: list of (body, "VertexN")."""
    obj = _add(study, "MeshSizesGroup", TransfiniteBody, "TransfiniteBody")
    obj.References = [(b, "") for b in bodies]
    obj.Corners = list(corners)
    return obj


def make_transfinite_edges(study, elements, edges, distribution="Uniform", coef=0.5):
    """edges: list of (body, "EdgeN")."""
    obj = _add(study, "MeshSizesGroup", TransfiniteEdges, "TransfiniteEdges")
    obj.Elements, obj.Distribution, obj.BumpCoefficient = elements, distribution, coef
    obj.References = list(edges)
    return obj
```

Replace `mesh_sizes` and add the two list helpers after it:

```python
def mesh_sizes(study):
    return [o for o in study.MeshSizesGroup.Group if isinstance(o.Proxy, MeshSize)]


def transfinite_bodies(study):
    return [o for o in study.MeshSizesGroup.Group if isinstance(o.Proxy, TransfiniteBody)]


def transfinite_edges(study):
    return [o for o in study.MeshSizesGroup.Group if isinstance(o.Proxy, TransfiniteEdges)]
```

- [ ] **Step 6: `is_item`, `item_refs`, `mesh_size_rows`**

Replace `is_item`:

```python
def is_item(obj):
    return isinstance(getattr(obj, "Proxy", None), (Material, Excitation, MeshSize, TransfiniteBody, TransfiniteEdges))
```

Replace `item_refs`:

```python
def item_refs(item):
    """[(body, sub)] of a Material, Excitation, Mesh Size or transfinite item; sub "" = the whole body."""
    if isinstance(item.Proxy, Material):
        return [(item.Body, "")] if item.Body else []
    refs = [(b, s) for b, subs in item.References for s in subs]
    if isinstance(item.Proxy, TransfiniteBody):
        refs += [(b, s) for b, subs in item.Corners for s in subs]
    return refs
```

Replace `mesh_size_rows`:

```python
def _size_text(item):
    if isinstance(item.Proxy, MeshSize):
        return f"{item.Size.Value:g} mm"
    if isinstance(item.Proxy, TransfiniteBody):
        return "structured"
    bump = f" {item.BumpCoefficient:g}" if item.Distribution == "Bump" else ""
    return f"{item.Elements} el, {item.Distribution}{bump}"


def mesh_size_rows(study):
    """Rows for the Mesh Sizes panel: (item, refs, [name, size, applies to])."""
    return [
        (s, item_refs(s), [display_name(s), _size_text(s), ", ".join(ref_label(b, sub) for b, sub in item_refs(s))])
        for s in study.MeshSizesGroup.Group
    ]
```

- [ ] **Step 7: Run the tests**

Run: `pixi run pytest tests/freecad_addon/test_study.py -q`
Expected: all pass (the new three and every old one).

- [ ] **Step 8: Format and lint**

Run: `pixi run format` then `pixi run lint`
Expected: lint passes; only `objects.py` and `test_study.py` changed by format, if at all.

- [ ] **Step 9: Checkpoint**

Tell the user: two new item types and the Recombine setting exist; nothing uses them yet. Ask them to check. Suggested commit message:
`Add Transfinite Body, Transfinite Edges items and the Recombine setting`

---

### Task 2: `meshcommon.apply_transfinite` and the 2D mesher

**Files:**
- Modify: `freecad_addon/emsolution/meshcommon.py` (add after `apply_size_fields`)
- Modify: `freecad_addon/emsolution/mesher2d.py` (`build`, `run_job`, import line)
- Test: `tests/freecad_addon/test_mesher2d.py`

**Interfaces:**
- Consumes: job dict with optional `"transfinite": {"bodies": [{"name", "mat_id", "corner_files": [...]}], "edges": [{"name", "nodes", "distribution", "coef", "files": [...]}]}`.
- Produces (used by Task 3):
  - `meshcommon.transfinite_files(job: dict, folder: str) -> list[tuple[str, dict, str]]` — `(kind, item, path)`, kind `"edge"` or `"corner"`; edges first, then corners, in job order.
  - `meshcommon.apply_transfinite(job: dict, mapped: list[tuple[str, dict, str, list[tuple[int, int]]]], body_tags: dict[int, list[int]], dim: int) -> None` — `mapped` is `(kind, item, file base name, final dimtags)` in `transfinite_files` order; `body_tags` maps `mat_id` to the body's final entity tags of dimension `dim`.

- [ ] **Step 1: Extend the test job runner and add helpers**

In `tests/freecad_addon/test_mesher2d.py`, change `run_job` to take `transfinite`:

```python
    def run_job(self, bodies, sizes=(), version=4.1, options=None, mesh_file=None, transfinite=None):
        job = {
            "dimension": "2D",
            "model_name": "Model",
            "msh_version": version,
            "mesh_file": mesh_file or os.path.join(self.dir, "pre_geom2D.msh"),
            "bodies": list(bodies),
            "sizes": list(sizes),
        }
        if options is not None:
            job["options"] = options
        if transfinite is not None:
            job["transfinite"] = transfinite
        path = os.path.join(self.dir, "job.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(job, fh)
        return subprocess.run([sys.executable, MESHER2D, path], capture_output=True, encoding="utf-8", errors="replace")
```

Add a module-level helper after `write_rects`:

```python
def write_polygons(path, loops):
    """One BREP holding one plane face in z = 0 bounded by the point loops (first = outer, rest = holes)."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        curve_loops = []
        for pts in loops:
            tags = [gmsh.model.occ.addPoint(x, y, 0) for x, y in pts]
            lines = [gmsh.model.occ.addLine(tags[k], tags[(k + 1) % len(tags)]) for k in range(len(tags))]
            curve_loops.append(gmsh.model.occ.addCurveLoop(lines))
        gmsh.model.occ.addPlaneSurface(curve_loops)
        gmsh.model.occ.synchronize()
        gmsh.write(path)
    finally:
        gmsh.finalize()
```

Add these methods to `Mesher2DTest` (after `last_error`):

```python
    def edge_item(self, name, lines, n, distribution="Uniform", coef=1.0):
        """Write each (p, q) line as geometry/<name>_<k>.brep; returns the job's Transfinite Edges entry."""
        files = []
        for k, (p, q) in enumerate(lines, 1):
            write_line(self.geo(f"{name}_{k}.brep"), p, q)
            files.append(f"geometry/{name}_{k}.brep")
        return {"name": name, "nodes": n + 1, "distribution": distribution, "coef": coef, "files": files}

    def corner_files(self, name, points):
        files = []
        for k, p in enumerate(points, 1):
            write_point(self.geo(f"{name}_{k}.brep"), p)
            files.append(f"geometry/{name}_{k}.brep")
        return files

    def element_counts(self, group, dim=2):
        """{element name: count} in a physical group of the open mesh."""
        out = {}
        for e in gmsh.model.getEntitiesForPhysicalGroup(dim, group):
            types, tags = gmsh.model.mesh.getElements(dim, e)[:2]
            for t, ts in zip(types, tags):
                name = gmsh.model.mesh.getElementProperties(t)[0]
                out[name] = out.get(name, 0) + len(ts)
        return out


def square_lines(x=0.0, y=0.0, w=1.0, h=1.0):
    """Bottom, right, top, left edges of a rectangle in z = 0 as point pairs."""
    c = [(x, y, 0), (x + w, y, 0), (x + w, y + h, 0), (x, y + h, 0)]
    return [(c[k], c[(k + 1) % 4]) for k in range(4)]
```

(`square_lines` is module level: put it after `write_polygons`, not inside the class.)

- [ ] **Step 2: Write the failing tests**

Add to `Mesher2DTest`:

```python
    def structured(self, *names_ids, corners=None):
        return [{"name": n, "mat_id": i, "corner_files": (corners or {}).get(n, [])} for n, i in names_ids]

    def test_structured_square_with_recombine_has_only_quads(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        tf = {"bodies": self.structured(("Core", 1)), "edges": [self.edge_item("tedge_1", square_lines(), 4)]}
        r = self.run_job([self.body(1, "Core", "vol_1.brep")], options={"Mesh.RecombineAll": 1}, transfinite=tf)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        self.assertEqual(self.element_counts(1), {"Quadrilateral 4": 16})

    def test_structured_square_without_recombine_has_structured_triangles(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        tf = {"bodies": self.structured(("Core", 1)), "edges": [self.edge_item("tedge_1", square_lines(), 4)]}
        r = self.run_job([self.body(1, "Core", "vol_1.brep")], transfinite=tf)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        self.assertEqual(self.element_counts(1), {"Triangle 3": 32})

    def test_bump_below_one_refines_the_edge_ends(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        edges = self.edge_item("tedge_1", square_lines(), 10, "Bump", 0.2)
        r = self.run_job([self.body(1, "Core", "vol_1.brep")], transfinite={"bodies": [], "edges": [edges]})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        c = gmsh.model.mesh.getNodes()[1]
        xs = sorted(c[i] for i in range(0, len(c), 3) if abs(c[i + 1]) < 1e-9)  # nodes on the bottom edge
        gaps = [b - a for a, b in zip(xs, xs[1:])]
        self.assertEqual(len(gaps), 10)
        self.assertLess(gaps[0] * 2, gaps[5])

    def test_structured_square_next_to_an_unstructured_one_shares_nodes(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        write_rects(self.geo("vol_2.brep"), [(1, 0, 1, 1)])
        tf = {"bodies": self.structured(("Core", 1)), "edges": [self.edge_item("tedge_1", square_lines(), 4)]}
        r = self.run_job(
            [self.body(1, "Core", "vol_1.brep"), self.body(2, "Air", "vol_2.brep", size=0.1)], transfinite=tf
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        self.assertEqual(self.element_counts(1), {"Triangle 3": 32})
        nodes1 = set(gmsh.model.mesh.getNodesForPhysicalGroup(2, 1)[0])
        nodes2 = set(gmsh.model.mesh.getNodesForPhysicalGroup(2, 2)[0])
        self.assertEqual(len(nodes1 & nodes2), 5, "the shared edge has 4 elements, so 5 shared nodes")

    def test_five_point_face_with_chosen_corners(self):
        write_polygons(self.geo("vol_1.brep"), [[(0, 0), (0.5, 0), (1, 0), (1, 1), (0, 1)]])
        bottom = self.edge_item("tedge_1", [((0, 0, 0), (0.5, 0, 0)), ((0.5, 0, 0), (1, 0, 0))], 2)
        sides = self.edge_item("tedge_2", square_lines()[1:], 4)  # right, top, left
        corners = {"Core": self.corner_files("corner_1", [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)])}
        tf = {"bodies": self.structured(("Core", 1), corners=corners), "edges": [bottom, sides]}
        r = self.run_job([self.body(1, "Core", "vol_1.brep")], options={"Mesh.RecombineAll": 1}, transfinite=tf)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        self.assertEqual(self.element_counts(1), {"Quadrilateral 4": 16})

    def test_five_point_face_finds_corners_where_the_boundary_turns(self):
        write_polygons(self.geo("vol_1.brep"), [[(0, 0), (0.5, 0), (1, 0), (1, 1), (0, 1)]])
        bottom = self.edge_item("tedge_1", [((0, 0, 0), (0.5, 0, 0)), ((0.5, 0, 0), (1, 0, 0))], 2)
        sides = self.edge_item("tedge_2", square_lines()[1:], 4)
        tf = {"bodies": self.structured(("Core", 1)), "edges": [bottom, sides]}
        r = self.run_job([self.body(1, "Core", "vol_1.brep")], options={"Mesh.RecombineAll": 1}, transfinite=tf)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("NOTE: structured body Core", r.stderr)
        self.assertIn("5 boundary points; using the 4 where the boundary turns", r.stderr)
        self.open_msh()
        self.assertEqual(self.element_counts(1), {"Quadrilateral 4": 16})

    def test_pentagon_without_corners_is_an_error(self):
        pts = [(0, 0), (1, 0), (1, 1), (0.5, 1.5), (0, 1)]
        write_polygons(self.geo("vol_1.brep"), [pts])
        lines = [((*pts[k], 0), (*pts[(k + 1) % 5], 0)) for k in range(5)]
        tf = {"bodies": self.structured(("Core", 1)), "edges": [self.edge_item("tedge_1", lines, 2)]}
        last = self.last_error(self.run_job([self.body(1, "Core", "vol_1.brep")], transfinite=tf))
        self.assertIn("structured body Core", last)
        self.assertIn("5 boundary points and 5 corners", last)

    def test_opposite_sides_with_different_counts_are_an_error(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        b, r_, t, l_ = square_lines()
        tf = {
            "bodies": self.structured(("Core", 1)),
            "edges": [self.edge_item("tedge_1", [b, t, l_], 4), self.edge_item("tedge_2", [r_], 6)],
        }
        last = self.last_error(self.run_job([self.body(1, "Core", "vol_1.brep")], transfinite=tf))
        self.assertIn("opposite sides", last)

    def test_structured_face_edge_without_item_is_an_error(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        tf = {"bodies": self.structured(("Core", 1)), "edges": [self.edge_item("tedge_1", square_lines()[:3], 4)]}
        last = self.last_error(self.run_job([self.body(1, "Core", "vol_1.brep")], transfinite=tf))
        self.assertIn("without Transfinite Edges", last)

    def test_edge_that_did_not_merge_is_an_error(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        far = self.edge_item("tedge_1", [((5, 5, 0), (6, 5, 0))], 4)
        last = self.last_error(
            self.run_job([self.body(1, "Core", "vol_1.brep")], transfinite={"bodies": [], "edges": [far]})
        )
        self.assertIn("Transfinite Edges tedge_1", last)
        self.assertIn("did not merge", last)

    def test_shared_edge_with_two_settings_is_an_error(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        write_rects(self.geo("vol_2.brep"), [(1, 0, 1, 1)])
        tf = {
            "bodies": self.structured(("A", 1), ("B", 2)),
            "edges": [self.edge_item("tedge_1", square_lines(), 4), self.edge_item("tedge_2", square_lines(1), 6)],
        }
        last = self.last_error(
            self.run_job([self.body(1, "A", "vol_1.brep"), self.body(2, "B", "vol_2.brep")], transfinite=tf)
        )
        self.assertIn("different settings", last)

    def test_edge_split_by_a_touching_body_shares_its_elements(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        write_rects(self.geo("vol_2.brep"), [(1, 0, 1, 0.5)])  # its corner (1, 0.5) splits Core's right edge
        tf = {"bodies": self.structured(("Core", 1)), "edges": [self.edge_item("tedge_1", square_lines(), 4)]}
        r = self.run_job(
            [self.body(1, "Core", "vol_1.brep"), self.body(2, "Air", "vol_2.brep")],
            options={"Mesh.RecombineAll": 1},
            transfinite=tf,
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("NOTE: Transfinite Edges tedge_1: tedge_1_2.brep was split into 2 pieces", r.stderr)
        self.assertIn("elements 2 + 2", r.stderr)
        self.assertIn("where the boundary turns", r.stderr)  # the split adds a 5th point to Core's face
        self.open_msh()
        self.assertEqual(self.element_counts(1), {"Quadrilateral 4": 16}, "the total stays 4 per side")

    def test_split_bump_edge_is_an_error(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        write_rects(self.geo("vol_2.brep"), [(1, 0, 1, 0.5)])
        edges = self.edge_item("tedge_1", square_lines(), 4, "Bump", 0.5)
        tf = {"bodies": self.structured(("Core", 1)), "edges": [edges]}
        last = self.last_error(
            self.run_job([self.body(1, "Core", "vol_1.brep"), self.body(2, "Air", "vol_2.brep")], transfinite=tf)
        )
        self.assertIn("split into 2 pieces", last)
        self.assertIn("Bump", last)

    def test_structured_face_with_a_hole_is_an_error(self):
        outer, inner = [(0, 0), (3, 0), (3, 3), (0, 3)], [(1, 1), (2, 1), (2, 2), (1, 2)]
        write_polygons(self.geo("vol_1.brep"), [outer, inner])
        lines = square_lines(0, 0, 3, 3) + square_lines(1, 1, 1, 1)
        corners = {"Frame": self.corner_files("corner_1", [(x, y, 0) for x, y in outer])}
        tf = {"bodies": self.structured(("Frame", 1), corners=corners), "edges": [self.edge_item("tedge_1", lines, 3)]}
        last = self.last_error(self.run_job([self.body(1, "Frame", "vol_1.brep")], transfinite=tf))
        self.assertIn("not one loop", last)
```

- [ ] **Step 3: Run them to see them fail**

Run: `pixi run pytest tests/freecad_addon/test_mesher2d.py -q`
Expected: the new structured/quads tests FAIL (the mesher ignores `"transfinite"`, so element counts differ and no errors are raised); old tests pass.

- [ ] **Step 4: Add the shared code to `meshcommon.py`**

Add `import math` between `import json` and `import os` (an addition, not a reorder). After `apply_size_fields` add:

```python
def _note(text):
    """Something the mesher fixed by itself; the runner shows stderr in FreeCAD's Report view."""
    print(f"NOTE: {text}", file=sys.stderr)


def transfinite_files(job, folder):
    """[(kind, item, path)] for job["transfinite"]: every edge file ("edge"), then every corner file ("corner")."""
    tf = job.get("transfinite") or {}
    out = [("edge", e, os.path.join(folder, f)) for e in tf.get("edges", []) for f in e["files"]]
    out += [("corner", b, os.path.join(folder, f)) for b in tf.get("bodies", []) for f in b["corner_files"]]
    return out


def _boundary(dim, tag):
    return list(dict.fromkeys(abs(t) for _, t in gmsh.model.getBoundary([(dim, tag)], combined=False, oriented=False)))


def _share(n, lengths, label, name):
    """n elements over the pieces of a split edge, by length: each at least 1, the total stays n."""
    if n < len(lengths):
        raise JobError(f"{label}: {name} was split into {len(lengths)} pieces by a touching body but has only {n} elements")
    raw = [n * x / sum(lengths) for x in lengths]
    counts = [max(1, round(r)) for r in raw]
    while sum(counts) < n:
        counts[max(range(len(raw)), key=lambda i: raw[i] - counts[i])] += 1
    while sum(counts) > n:
        counts[max((i for i in range(len(raw)) if counts[i] > 1), key=lambda i: counts[i] - raw[i])] -= 1
    return counts


def _direction(curve, point):
    """Unit tangent of curve at its end point."""
    lo, hi = gmsh.model.getParametrizationBounds(1, curve)
    xyz = gmsh.model.getValue(0, point, [])
    u = min((lo[0], hi[0]), key=lambda v: math.dist(gmsh.model.getValue(1, curve, [v]), xyz))
    d = gmsh.model.getDerivative(1, curve, [u])
    size = math.hypot(*d)
    return [x / size for x in d]


def _turns(point, c1, c2):
    """True when the boundary changes direction at point, where curves c1 and c2 meet."""
    return abs(abs(sum(a * b for a, b in zip(_direction(c1, point), _direction(c2, point)))) - 1) > 1e-6


def _loop(face, curves, ends, at, start, body):
    """[(curve, its first point)] once around the face boundary from point start. at: point -> its curves."""
    loop, p, c = [], start, at[start][0]
    for _ in curves:  # bounded: a bad boundary cannot loop forever
        loop.append((c, p))
        p = ends[c][1] if ends[c][0] == p else ends[c][0]
        if p == start:
            break
        c = next((x for x in at[p] if x != c), c)
    if p != start or len(loop) != len(curves):
        raise JobError(f"structured body {body}: face {face} boundary is not one loop (a hole?); it cannot be structured")
    return loop


def _set_face(face, chosen, curve_set, body):
    """Check one face of a structured body (R4, R6) and make it transfinite. curve_set: curve -> (nodes, ...)."""
    curves = _boundary(2, face)
    if any(c not in curve_set for c in curves):
        raise JobError(f"structured body {body}: face {face} has edges without Transfinite Edges")
    ends = {c: _boundary(1, c) for c in curves}
    if any(len(e) != 2 for e in ends.values()):
        raise JobError(f"structured body {body}: face {face} has a closed edge (circle?); it cannot be structured")
    at = {}  # point -> the curves meeting there
    for c in curves:
        for p in ends[c]:
            at.setdefault(p, []).append(c)
    points = set(at)
    corners = points if len(points) <= 4 else {p for p in chosen if p in points}
    if not corners:  # more than 4 points and none chosen: the points where the boundary turns
        corners = {p for p in points if len(at[p]) == 2 and _turns(p, *at[p])}
        if len(corners) in (3, 4):
            _note(
                f"structured body {body}: face {face} has {len(points)} boundary points;"
                f" using the {len(corners)} where the boundary turns as corners"
            )
    if len(corners) not in (3, 4):
        raise JobError(
            f"structured body {body}: face {face} has {len(points)} boundary points and {len(corners)} corners"
            " on it; it needs 3 or 4 (choose Corners in the Transfinite Body)"
        )
    loop = _loop(face, curves, ends, at, min(corners), body)
    sides = []
    for c, p in loop:
        if p in corners:
            sides.append(0)
        sides[-1] += curve_set[c][0] - 1
    if len(sides) == 4 and (sides[0] != sides[2] or sides[1] != sides[3]):
        raise JobError(
            f"structured body {body}: face {face} opposite sides have {sides[0]}/{sides[2]} and"
            f" {sides[1]}/{sides[3]} elements; they must match"
        )
    gmsh.model.mesh.setTransfiniteSurface(face, cornerTags=[p for _, p in loop if p in corners])


def apply_transfinite(job, mapped, body_tags, dim):
    """Transfinite curves, faces and (3D) volumes from job["transfinite"].

    mapped: [(kind, item, file name, final dimtags)] in transfinite_files order, from the fragment map.
    body_tags: {mat_id: the body's final entity tags of dimension dim}.
    """
    curve_set, corners = {}, {}  # final curve -> (nodes, distribution, coef, item name); body name -> points
    for kind, item, name, dimtags in mapped:
        want = 1 if kind == "edge" else 0
        label = f"Transfinite Edges {item['name']}" if kind == "edge" else f"structured body {item['name']}"
        tags = [t for d, t in dimtags if d == want]
        if not tags or any(len(gmsh.model.getAdjacencies(want, t)[0]) == 0 for t in tags):
            raise JobError(f"{label}: {name} did not merge with the bodies")
        if kind == "corner":
            corners.setdefault(item["name"], set()).update(tags)
            continue
        counts = [item["nodes"] - 1]
        if len(tags) > 1:  # a touching body's vertex lies on the edge
            if item["distribution"] == "Bump":
                raise JobError(
                    f"{label}: {name} was split into {len(tags)} pieces by a touching body;"
                    " a Bump edge cannot be shared out (use Uniform, or make the bodies match)"
                )
            counts = _share(item["nodes"] - 1, [gmsh.model.occ.getMass(1, t) for t in tags], label, name)
            _note(
                f"{label}: {name} was split into {len(tags)} pieces by a touching body;"
                " elements " + " + ".join(map(str, counts))
            )
        for t, n in zip(tags, counts):
            setting = (n + 1, item["distribution"], item["coef"])
            old = curve_set.setdefault(t, (*setting, item["name"]))
            if old[:3] != setting:
                raise JobError(f"Transfinite Edges {old[3]} and {item['name']} give one edge different settings")
    for t, (nodes, distribution, coef, _) in curve_set.items():
        bump = distribution == "Bump"
        gmsh.model.mesh.setTransfiniteCurve(t, nodes, "Bump" if bump else "Progression", coef if bump else 1.0)
    for b in (job.get("transfinite") or {}).get("bodies", []):
        tags = body_tags[b["mat_id"]]
        faces = list(tags) if dim == 2 else []
        for v in tags if dim == 3 else []:
            vfaces = _boundary(3, v)
            if len(vfaces) not in (5, 6):
                raise JobError(
                    f"structured body {b['name']}: volume has {len(vfaces)} faces, needs 5 or 6"
                    " (split by a touching body?)"
                )
            faces += vfaces
        for f in dict.fromkeys(faces):
            _set_face(f, corners.get(b["name"], set()), curve_set, b["name"])
        for v in tags if dim == 3 else []:
            gmsh.model.mesh.setTransfiniteVolume(v)
```

- [ ] **Step 5: Use it in `mesher2d.py`**

Change the import line to:

```python
from meshcommon import JobError, apply_size_fields, apply_transfinite, main, run, transfinite_files
```

In `build`, right after the `for _, path in size_files:` loop (before `if len(inputs) == 1:`), add:

```python
    tf_files = transfinite_files(job, folder)
    tf_spans = []
    for kind, _, path in tf_files:
        start = len(inputs)
        inputs += _import(path, 1 if kind == "edge" else 0)
        tf_spans.append((start, len(inputs)))
```

At the end of `build`, after `apply_size_fields(by_size)`, add:

```python
    mapped = [
        (kind, item, os.path.basename(path), [dt for dimtags in out_map[start:end] for dt in dimtags])
        for (kind, item, path), (start, end) in zip(tf_files, tf_spans)
    ]
    apply_transfinite(job, mapped, body_faces, 2)
```

In `run_job`, after the `MAT_ID` loop add:

```python
    for item in (job.get("transfinite") or {}).get("bodies", []):
        print(f"Structured      {item['name']}")
```

- [ ] **Step 6: Run the tests**

Run: `pixi run pytest tests/freecad_addon/test_mesher2d.py -q`
Expected: all pass. If `test_structured_square_without_recombine_has_structured_triangles` finds a count other than 32, print `self.element_counts(1)` and report it before changing anything: the spec assumes Gmsh's default `Left` arrangement (2 triangles per cell).

- [ ] **Step 7: Run the 3D mesher tests (shared module changed)**

Run: `pixi run pytest tests/freecad_addon/test_mesher.py -q`
Expected: all pass.

- [ ] **Step 8: Format and lint**

Run: `pixi run format` then `pixi run lint`
Expected: lint passes.

- [ ] **Step 9: Checkpoint**

Tell the user: the 2D mesher now makes structured faces, checks R4–R7, shares the elements of an edge split by a touching body, finds corners where the boundary turns, and prints a `NOTE:` line (Report view) for each of these. Ask them to check. Suggested commit message:
`Structured (transfinite) faces in mesher2d.py through shared meshcommon code`

---

### Task 3: The 3D mesher

**Files:**
- Modify: `freecad_addon/emsolution/mesher.py` (`build`, `run_job`, import line)
- Test: `tests/freecad_addon/test_mesher.py`

**Interfaces:**
- Consumes: `meshcommon.transfinite_files`, `meshcommon.apply_transfinite` from Task 2 (exact signatures there).

- [ ] **Step 1: Extend the test job runner and add helpers**

In `tests/freecad_addon/test_mesher.py`, change `run_job`:

```python
    def run_job(self, volumes, surfaces=(), version=4.1, sizes=(), options=None, mesh_file=None, transfinite=None):
        job = {
            "model_name": "Model",
            "msh_version": version,
            "mesh_file": mesh_file or os.path.join(self.dir, "pre_geom.msh"),
            "volumes": list(volumes),
            "surfaces": list(surfaces),
            "sizes": list(sizes),
        }
        if options is not None:
            job["options"] = options
        if transfinite is not None:
            job["transfinite"] = transfinite
        path = os.path.join(self.dir, "job.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(job, fh)
        return subprocess.run([sys.executable, MESHER, path], capture_output=True, encoding="utf-8", errors="replace")
```

Add a module-level helper after `write_point`:

```python
def box_lines(x=0.0):
    """The 12 edges of the unit box at x as point pairs."""
    pts = [(x + i, j, k) for i in (0, 1) for j in (0, 1) for k in (0, 1)]
    return [(p, q) for a, p in enumerate(pts) for q in pts[a + 1 :] if sum(abs(u - v) for u, v in zip(p, q)) == 1]
```

Add these methods to `MesherTest`:

```python
    def edge_item(self, name, lines, n):
        files = []
        for k, (p, q) in enumerate(lines, 1):
            write_line(self.geo(f"{name}_{k}.brep"), p, q)
            files.append(f"geometry/{name}_{k}.brep")
        return {"name": name, "nodes": n + 1, "distribution": "Uniform", "coef": 1.0, "files": files}

    def element_counts(self, group, dim=3):
        out = {}
        for e in gmsh.model.getEntitiesForPhysicalGroup(dim, group):
            types, tags = gmsh.model.mesh.getElements(dim, e)[:2]
            for t, ts in zip(types, tags):
                name = gmsh.model.mesh.getElementProperties(t)[0]
                out[name] = out.get(name, 0) + len(ts)
        return out

    def structured_box(self, n=3):
        return {"bodies": [{"name": "Core", "mat_id": 1, "corner_files": []}], "edges": [self.edge_item("tedge_1", box_lines(), n)]}
```

- [ ] **Step 2: Write the failing tests**

```python
    def test_structured_box_with_recombine_has_only_hexahedra(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        r = self.run_job(
            [self.vol(1, "Core", "vol_1.brep")], options={"Mesh.RecombineAll": 1}, transfinite=self.structured_box()
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        self.assertEqual(self.element_counts(1), {"Hexahedron 8": 27})

    def test_structured_box_without_recombine_has_six_tetrahedra_per_cell(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        r = self.run_job([self.vol(1, "Core", "vol_1.brep")], transfinite=self.structured_box())
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        self.assertEqual(self.element_counts(1), {"Tetrahedron 4": 162})

    def test_structured_box_next_to_unstructured_box_gets_pyramids(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_box(self.geo("vol_2.brep"), 1, 0, 0, 1, 1, 1)
        r = self.run_job(
            [self.vol(1, "Core", "vol_1.brep"), self.vol(2, "Air", "vol_2.brep", size=0.3)],
            options={"Mesh.RecombineAll": 1, "Mesh.Algorithm3D": 1},
            transfinite=self.structured_box(),
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        self.assertEqual(self.element_counts(1), {"Hexahedron 8": 27})
        self.assertIn("Pyramid 5", self.element_counts(2))

    def test_structured_box_edge_without_item_is_an_error(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        tf = self.structured_box()
        tf["edges"] = [self.edge_item("tedge_1", box_lines()[:11], 3)]
        r = self.run_job([self.vol(1, "Core", "vol_1.brep")], transfinite=tf)
        self.assertEqual(r.returncode, 1)
        self.assertIn("without Transfinite Edges", r.stderr.strip().splitlines()[-1])

    def test_structured_volume_with_seven_faces_is_an_error(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_box(self.geo("vol_2.brep"), 1, 0.25, 0.25, 1, 0.5, 0.5)  # touches the middle of Core's x = 1 face
        r = self.run_job(
            [self.vol(1, "Core", "vol_1.brep"), self.vol(2, "Air", "vol_2.brep")], transfinite=self.structured_box()
        )
        self.assertEqual(r.returncode, 1)
        last = r.stderr.strip().splitlines()[-1]
        self.assertTrue(last.startswith("ERROR:"), last)
        self.assertIn("7 faces, needs 5 or 6", last)
```

- [ ] **Step 3: Run them to see them fail**

Run: `pixi run pytest tests/freecad_addon/test_mesher.py -k structured -q`
Expected: FAIL (the 3D mesher ignores `"transfinite"`).

- [ ] **Step 4: Use the shared code in `mesher.py`**

Change the import line to:

```python
from meshcommon import JobError, apply_size_fields, apply_transfinite, main, run, transfinite_files
```

In `build`, after `inputs += [_import_one(path, 0, 1, 2) for _, path in size_files]` add:

```python
    tf_files = transfinite_files(job, folder)
    inputs += [_import_one(path, 1 if kind == "edge" else 0) for kind, _, path in tf_files]
```

At the end of `build`, after `apply_size_fields(by_size)`, add:

```python
    tf_maps = out_map[first + len(size_files) :]
    mapped = [(kind, item, os.path.basename(path), dimtags) for (kind, item, path), dimtags in zip(tf_files, tf_maps)]
    apply_transfinite(job, mapped, body_vols, 3)
```

In `run_job`, after the `SMAT_ID` loop add:

```python
    for item in (job.get("transfinite") or {}).get("bodies", []):
        print(f"Structured      {item['name']}")
```

- [ ] **Step 5: Run the tests**

Run: `pixi run pytest tests/freecad_addon/test_mesher.py tests/freecad_addon/test_mesher2d.py -q`
Expected: all pass.

- [ ] **Step 6: Format and lint**

Run: `pixi run format` then `pixi run lint`
Expected: lint passes.

- [ ] **Step 7: Checkpoint**

Tell the user: the 3D mesher now makes structured volumes (hexahedra with Recombine, pyramids next to tetrahedra). Ask them to check. Suggested commit message:
`Structured (transfinite) volumes in mesher.py`

---

### Task 4: Job writer: checks R1–R3, R8 and the job content

**Files:**
- Modify: `freecad_addon/emsolution/jobwriter.py` (`check`, `mesh_options`, `write_job`; new `transfinite_items`)
- Test: `tests/freecad_addon/test_study.py`

**Interfaces:**
- Consumes: `objects.transfinite_bodies`, `objects.transfinite_edges`, `objects.subs_by_body` (Task 1); folder property `Recombine`.
- Produces: `jobwriter.transfinite_items(study, bodies) -> (structured, edges)`
  - `structured = [(body, [corner vertex names])]` in tree order
  - `edges = [(item, body, [edge names])]` in tree order
  - Raises `StudyError` for R1–R3 and a Bump coefficient ≤ 0.
- `jobwriter.check(study)` keeps its 3-tuple return; it now also raises for R1–R3 and R8.

- [ ] **Step 1: Write the failing tests**

Add to `StudyTest`, after `test_check_missing_edge`:

```python
    def all_edges(self, body):
        return [(body, f"Edge{i}") for i in range(1, len(body.Shape.Edges) + 1)]

    def test_transfinite_items_go_to_the_job(self):
        a = self.box("A")
        self.include(a)
        objects.make_transfinite_body(self.study, [a], [(a, "Vertex1")])
        objects.make_transfinite_edges(self.study, 3, self.all_edges(a), "Bump", 0.4)
        with open(jobwriter.write_job(self.study), encoding="utf-8") as fh:
            job = json.load(fh)
        tf = job["transfinite"]
        self.assertEqual(tf["bodies"], [{"name": "A", "mat_id": 1, "corner_files": ["geometry/corner_1_1.brep"]}])
        (edges,) = tf["edges"]
        self.assertEqual(
            (edges["name"], edges["nodes"], edges["distribution"], edges["coef"]), ("TransfiniteEdges", 4, "Bump", 0.4)
        )
        self.assertEqual(len(edges["files"]), 12)
        edge = Part.Shape()
        edge.read(self.scratch("geometry", "tedge_1_1.brep"))
        self.assertEqual(edge.ShapeType, "Edge")
        self.assertNotIn("Mesh.RecombineAll", job["options"])

    def test_job_without_transfinite_items_has_no_transfinite_key(self):
        self.include(self.box("A"))
        with open(jobwriter.write_job(self.study), encoding="utf-8") as fh:
            self.assertNotIn("transfinite", json.load(fh))

    def test_recombine_goes_to_the_options(self):
        self.include(self.box("A"))
        self.study.MeshSizesGroup.Recombine = True
        with open(jobwriter.write_job(self.study), encoding="utf-8") as fh:
            self.assertEqual(json.load(fh)["options"]["Mesh.RecombineAll"], 1)

    def test_structured_body_edge_without_item_is_refused(self):
        a = self.box("A")
        self.include(a)
        objects.make_transfinite_body(self.study, [a])
        objects.make_transfinite_edges(self.study, 3, self.all_edges(a)[:11])
        self.assertStudyError("edges without Transfinite Edges: Edge12")

    def test_edge_in_two_transfinite_edges_is_refused(self):
        a = self.box("A")
        self.include(a)
        objects.make_transfinite_edges(self.study, 3, [(a, "Edge1")])
        objects.make_transfinite_edges(self.study, 4, [(a, "Edge1")])
        self.assertStudyError("A.Edge1 is in Transfinite Edges")

    def test_body_in_two_transfinite_bodies_is_refused(self):
        a = self.box("A")
        self.include(a)
        objects.make_transfinite_edges(self.study, 3, self.all_edges(a))
        objects.make_transfinite_body(self.study, [a])
        objects.make_transfinite_body(self.study, [a])
        self.assertStudyError("Body A is in Transfinite Body")

    def test_corner_on_another_body_is_refused(self):
        a, b = self.box("A"), self.box("B", 10)
        self.include(a, b)
        objects.make_transfinite_edges(self.study, 3, self.all_edges(a))
        objects.make_transfinite_body(self.study, [a], [(b, "Vertex1")])
        self.assertStudyError("is not on one of its bodies")

    def test_3d_recombine_needs_delaunay(self):
        self.include(self.box("A"))
        self.study.MeshSizesGroup.Recombine = True
        self.study.MeshSizesGroup.VolumeAlgorithm = "HXT"
        self.assertStudyError("Delaunay")

    def test_structured_box_job_meshes_to_hexahedra(self):
        a = self.box("A")
        self.include(a)
        objects.make_transfinite_body(self.study, [a])
        objects.make_transfinite_edges(self.study, 3, self.all_edges(a))
        self.study.MeshSizesGroup.Recombine = True
        path = jobwriter.write_job(self.study)
        r = subprocess.run([sys.executable, MESHER, path], capture_output=True, encoding="utf-8", errors="replace")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("Structured      A", r.stdout)
        self.assertEqual(msh_element_types(os.path.join(self.tmp.name, "pre_geom.msh"), 3), {5}, "only hexahedra")

    def test_2d_structured_face_job_meshes_to_quads(self):
        a = self.face("A")
        study = self.make_2d_study(a)
        objects.make_transfinite_body(study, [a])
        objects.make_transfinite_edges(study, 4, self.all_edges(a))
        study.MeshSizesGroup.Recombine = True
        path = jobwriter.write_job(study)
        r = subprocess.run([sys.executable, MESHER2D, path], capture_output=True, encoding="utf-8", errors="replace")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(msh_element_types(os.path.join(self.tmp.name, "pre_geom2D.msh"), 2), {3}, "only quadrangles")
```

Add this module-level helper after the `MESHER2D = ...` line. It reads the file as text, because importing `gmsh` into the FreeCAD test process can clash with FreeCAD's own OpenCASCADE libraries:

```python
def msh_element_types(path, dim):
    """Gmsh element type numbers of the dim-D entity blocks in an ASCII msh 4.1 file."""
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().split("$Elements\n", 1)[1].split("$EndElements", 1)[0].splitlines()
    types, k = set(), 1  # line 0: numEntityBlocks numElements minTag maxTag
    while k < len(lines):
        d, _, t, n = map(int, lines[k].split())  # block header: entityDim entityTag elementType numElements
        if d == dim:
            types.add(t)
        k += n + 1
    return types
```

Note: `test_structured_box_job_meshes_to_hexahedra` and `test_2d_structured_face_job_meshes_to_quads` sit in the class before `face` / `make_2d_study` are defined; that is fine in Python (methods are looked up at call time).

- [ ] **Step 2: Run them to see them fail**

Run: `pixi run pytest tests/freecad_addon/test_study.py -k "transfinite or recombine or structured or delaunay or corner or two_transfinite" -q`
Expected: FAIL (no `"transfinite"` key, no checks).

- [ ] **Step 3: Add `transfinite_items`**

In `jobwriter.py`, after `check`, add:

```python
def transfinite_items(study, bodies):
    """R1 to R3 for the Study's transfinite items on bodies. Returns (structured, edges):
    structured = [(body, [corner vertex names])] in tree order
    edges      = [(item, body, [edge names])] in tree order
    """
    included = {b.Name for b in bodies}
    structured, owner = [], {}
    for t in objects.transfinite_bodies(study):
        refs = [b for b, _ in objects.subs_by_body(t)]
        corners = {}
        for b, subs in t.Corners:
            if b.Name not in {r.Name for r in refs}:
                raise StudyError(f"Transfinite Body {t.Label}: corner {b.Label}.{subs[0]} is not on one of its bodies.")
            corners.setdefault(b.Name, []).extend(subs)
        for b in refs:
            if b.Name not in included:
                continue
            if b.Name in owner:
                raise StudyError(f"Body {b.Label} is in Transfinite Body {owner[b.Name].Label} and {t.Label}.")
            owner[b.Name] = t
            _check_subs("Transfinite Body", t, b, corners.get(b.Name, []))
            structured.append((b, corners.get(b.Name, [])))
    edges, seen = [], {}
    for e in objects.transfinite_edges(study):
        if e.Distribution == "Bump" and e.BumpCoefficient <= 0:
            raise StudyError(f"Transfinite Edges {e.Label}: the Bump coefficient must be greater than 0.")
        for b, subs in objects.subs_by_body(e):
            if b.Name not in included:
                continue
            _check_subs("Transfinite Edges", e, b, subs)
            for s in subs:
                if (b.Name, s) in seen:
                    raise StudyError(f"{b.Label}.{s} is in Transfinite Edges {seen[(b.Name, s)].Label} and {e.Label}.")
                seen[(b.Name, s)] = e
            edges.append((e, b, list(subs)))
    for b, _ in structured:
        missing = [f"Edge{i}" for i in range(1, len(b.Shape.Edges) + 1) if (b.Name, f"Edge{i}") not in seen]
        if missing:
            raise StudyError(
                f"Transfinite Body {owner[b.Name].Label}: {b.Label} has edges without Transfinite Edges: "
                + ", ".join(missing)
            )
    return structured, edges
```

- [ ] **Step 4: Call it and R8 from `check`**

In `check`, right after the `if 0 < settings.MaxSize.Value < settings.MinSize.Value:` block, add:

```python
    if study.Dimension == "3D" and settings.Recombine and settings.VolumeAlgorithm != "Delaunay":
        raise StudyError(
            "Recombine in 3D needs the Delaunay volume algorithm: Frontal and HXT cannot mesh next to quads."
        )
    transfinite_items(study, bodies)
```

- [ ] **Step 5: Recombine in `mesh_options`**

In `mesh_options`, before `return opts`, add:

```python
    if settings.Recombine:
        opts["Mesh.RecombineAll"] = 1
```

- [ ] **Step 6: Write the `"transfinite"` key in `write_job`**

In `write_job`, after the `for k, (item, body, subs) in enumerate(elements, 1):` loop and before `path = os.path.join(folder, "job.json")`, add:

```python
    structured, tf_edges = transfinite_items(study, [b for b, _ in volumes])
    if structured or tf_edges:
        tf_bodies = []
        for body, corners in structured:
            mat_id = int(study.MatIds[body.Name])
            files = export_subs(folder, body, corners, f"corner_{mat_id}")
            tf_bodies.append({"name": objects.volume_name(body), "mat_id": mat_id, "corner_files": files})
        job["transfinite"] = {
            "bodies": tf_bodies,
            "edges": [
                {
                    "name": item.Label,
                    "nodes": item.Elements + 1,
                    "distribution": item.Distribution,
                    "coef": item.BumpCoefficient,
                    "files": export_subs(folder, body, subs, f"tedge_{k}"),
                }
                for k, (item, body, subs) in enumerate(tf_edges, 1)
            ],
        }
```

- [ ] **Step 7: Run all Study tests**

Run: `pixi run pytest tests/freecad_addon/test_study.py -q`
Expected: all pass, including the unchanged `test_mesh_settings_go_to_the_job` (Recombine off adds no key) and `test_3d_job_keeps_its_old_shape`.

- [ ] **Step 8: Format and lint**

Run: `pixi run format` then `pixi run lint`
Expected: lint passes.

- [ ] **Step 9: Checkpoint**

Tell the user: Run Mesh now writes structured items to the job and refuses R1–R3 and R8 with a clear message. Ask them to check. Suggested commit message:
`Write transfinite items and Recombine to the mesh job, with checks`

---

### Task 5: Commands, icons, edit panel and the Recombine checkbox

**Files:**
- Create: `freecad_addon/icons/transfinitebody.svg`, `freecad_addon/icons/transfiniteedges.svg`
- Modify: `freecad_addon/emsolution/commands.py` (new `ask_elements`, two command classes, `COMMANDS`)
- Modify: `freecad_addon/emsolution/taskpanels.py` (`MeshSettings`, `ItemPanel`)
- Test: `tests/freecad_addon/gui_smoke.py`

**Interfaces:**
- Consumes: `objects.make_transfinite_body`, `objects.make_transfinite_edges`, `objects.TransfiniteBody`, `objects.TransfiniteEdges`, `objects.transfinite_bodies`, `objects.transfinite_edges` (Task 1); `taskpanels.selected_subs`, `taskpanels.selected_bodies`.
- Produces: commands `EMS_TransfiniteBody`, `EMS_TransfiniteEdges`; `commands.ask_elements() -> int | None`.

- [ ] **Step 1: Icons**

`freecad_addon/icons/transfinitebody.svg`:

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64"><path d="M8 8h48v48H8z M8 24h48 M8 40h48 M24 8v48 M40 8v48" fill="none" stroke="#2a8c3c" stroke-width="3"/></svg>
```

`freecad_addon/icons/transfiniteedges.svg`:

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64"><path d="M6 32h52" fill="none" stroke="#2a8c3c" stroke-width="3"/><path d="M6 24v16 M16 24v16 M26 24v16 M38 24v16 M48 24v16 M58 24v16" fill="none" stroke="#2a8c3c" stroke-width="3"/></svg>
```

(Item icons come from `ViewProviderItem.getIcon`, which uses the proxy class name in lower case.)

- [ ] **Step 2: Commands**

In `commands.py`, after `ask_size` add:

```python
def ask_elements():
    value, ok = QtWidgets.QInputDialog.getInt(
        Gui.getMainWindow(), "Transfinite Edges", "Elements per edge:", 10, 1, 100000
    )
    return value if ok else None
```

After the `AddMeshSize` class add:

```python
class AddTransfiniteBody(_StudyCommand):
    def GetResources(self):
        return {
            "Pixmap": icon("transfinitebody"),
            "MenuText": "Transfinite Body",
            "ToolTip": "Mesh the selected bodies as a structured grid; selected vertices become face corners",
        }

    def Activated(self):
        study = assignment_study()
        if study is None:
            return
        bodies = taskpanels.selected_bodies()
        if not bodies:
            return warn("Select one or more bodies first.")
        if gate(study, bodies):
            corners = taskpanels.selected_subs(("Vertex",))
            _create(study, "Add Transfinite Body", lambda: objects.make_transfinite_body(study, bodies, corners))


class AddTransfiniteEdges(_StudyCommand):
    def GetResources(self):
        return {
            "Pixmap": icon("transfiniteedges"),
            "MenuText": "Transfinite Edges",
            "ToolTip": "Give the selected edges a fixed number of elements",
        }

    def Activated(self):
        study = assignment_study()
        if study is None:
            return
        edges = taskpanels.selected_subs(("Edge",))
        if not edges:
            return warn("Select one or more edges first.")
        if not gate(study, [b for b, _ in edges]):
            return
        elements = ask_elements()
        if elements:
            _create(study, "Add Transfinite Edges", lambda: objects.make_transfinite_edges(study, elements, edges))
```

In `COMMANDS`, after `"EMS_MeshSize": AddMeshSize(),` add:

```python
    "EMS_TransfiniteBody": AddTransfiniteBody(),
    "EMS_TransfiniteEdges": AddTransfiniteEdges(),
```

- [ ] **Step 3: Recombine checkbox in `MeshSettings`**

In `taskpanels.py`, `MeshSettings.__init__`, after `form.addRow(self.netgen)` add:

```python
        self.recombine = QtWidgets.QCheckBox("Recombine into quads / hexahedra")
        self.recombine.setToolTip("Gmsh RecombineAll. In 3D it needs the Delaunay volume algorithm.")
        self.recombine.setChecked(folder.Recombine)
        form.addRow(self.recombine)
```

After `self.netgen.toggled.connect(self.save)` add:

```python
        self.recombine.toggled.connect(self.save)
```

In `values`, add `Recombine=self.recombine.isChecked(),` after `OptimizeNetgen=self.netgen.isChecked(),`.

- [ ] **Step 4: `ItemPanel` for the two items**

Replace the docstring and the pick selection at the top of `ItemPanel.__init__`:

```python
class ItemPanel:
    """Edit name, settings and references of an Excitation, Mesh Size or transfinite item."""

    def __init__(self, obj):
        self.obj = obj
        study = objects.owner_study(obj)
        highlight.clear()  # it would not follow the edits
        if isinstance(obj.Proxy, objects.Excitation):
            self.pick, label = selected_faces, "Faces"
        elif isinstance(obj.Proxy, objects.TransfiniteBody):
            self.pick, label = lambda: selected_subs(("Vertex",), whole_bodies=True), "Bodies,\ncorner vertices"
        elif isinstance(obj.Proxy, objects.TransfiniteEdges):
            self.pick, label = lambda: selected_subs(("Edge",)), "Edges"
        else:
            self.pick, label = selected_mesh_refs, "Bodies, faces,\nedges, vertices"
```

After the `if isinstance(obj.Proxy, objects.MeshSize):` block (the Size row) add:

```python
        self.elements = self.distribution = self.bump = None
        if isinstance(obj.Proxy, objects.TransfiniteEdges):
            self.elements = QtWidgets.QSpinBox()
            self.elements.setRange(1, 100000)
            self.elements.setValue(obj.Elements)
            layout.addRow("Elements", self.elements)
            self.distribution = QtWidgets.QComboBox()
            self.distribution.addItems(obj.getEnumerationsOfProperty("Distribution"))
            self.distribution.setCurrentText(obj.Distribution)
            layout.addRow("Distribution", self.distribution)
            self.bump = QtWidgets.QDoubleSpinBox()
            self.bump.setDecimals(3)
            self.bump.setRange(0.001, 1000.0)
            self.bump.setValue(obj.BumpCoefficient)
            self.bump.setEnabled(obj.Distribution == "Bump")
            layout.addRow("Bump coefficient", self.bump)
            self.distribution.currentTextChanged.connect(lambda text: self.bump.setEnabled(text == "Bump"))
```

In `accept`, replace `self.obj.References = list(self.current)` with:

```python
        if self.elements is not None:
            self.obj.Elements = self.elements.value()
            self.obj.Distribution = self.distribution.currentText()
            self.obj.BumpCoefficient = self.bump.value()
        if isinstance(self.obj.Proxy, objects.TransfiniteBody):
            self.obj.References = [(b, s) for b, s in self.current if not s]
            self.obj.Corners = [(b, s) for b, s in self.current if s]
        else:
            self.obj.References = list(self.current)
```

(The spec says the Bump coefficient is "shown only for Bump"; it is disabled instead of hidden, which needs no row-hiding code.)

- [ ] **Step 5: Smoke test**

In `tests/freecad_addon/gui_smoke.py`, right after `log.append("2D mesh ok")`, add:

```python
    commands.ask_elements = lambda: 4
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(doc.Name, section.Name)
    Gui.runCommand("EMS_TransfiniteBody")
    Gui.Selection.clearSelection()
    for k in range(1, 5):
        Gui.Selection.addSelection(doc.Name, section.Name, f"Edge{k}")
    Gui.runCommand("EMS_TransfiniteEdges")
    (tb,) = objects.transfinite_bodies(second)
    (te,) = objects.transfinite_edges(second)
    assert tb.References == [(section, ("",))], tb.References
    assert te.Elements == 4 and len(te.References[0][1]) == 4, te.References
    second.MeshSizesGroup.Recombine = True
    run_tf = runner.start(second)
    assert run_tf is not None and run_tf.proc.waitForFinished(120000)
    Gui.updateGui()
    assert run_tf.error == "" and not runner.busy(), run_tf.error
    log.append("2D transfinite mesh ok")
    for item in (tb, te):  # leave the Study as the rest of the smoke test expects it
        doc.removeObject(item.Name)
    second.MeshSizesGroup.Recombine = False
```

- [ ] **Step 6: Run the unit tests**

Run: `pixi run pytest tests/freecad_addon -q --ignore=tests/freecad_addon/gui_smoke.py`
Expected: all pass.

- [ ] **Step 7: Run the GUI smoke test**

Run (PowerShell, repo root):

```powershell
pixi run freecad tests\freecad_addon\gui_smoke.py
Get-Content "$env:TEMP\ems_gui_smoke.txt"
```

Expected: the log contains `2D transfinite mesh ok` and the last line is `PASS`.

- [ ] **Step 8: Format and lint**

Run: `pixi run format` then `pixi run lint`
Expected: lint passes.

- [ ] **Step 9: Checkpoint**

Tell the user: two toolbar commands, item editing and the Recombine checkbox are in. Ask them to try it in FreeCAD: a 2D Study with a square face, Transfinite Body on it, Transfinite Edges on its 4 edges, Recombine on, Run Mesh → quads; and a 3D box the same way → hexahedra. Suggested commit message:
`Transfinite Body and Transfinite Edges commands, edit panel and Recombine checkbox`

---

### Task 6: Full check

**Files:** none new.

- [ ] **Step 1: All tests**

Run: `pixi run test`
Expected: all pass.

- [ ] **Step 2: Lint**

Run: `pixi run lint`
Expected: passes.

- [ ] **Step 3: Diff review**

Run: `git diff --stat`
Expected: only the files named in Tasks 1–5 (plus the plan and spec). No formatting-only changes in other files.

- [ ] **Step 4: Checkpoint**

Tell the user everything is done and tested, list what is not verified by tests (running the solver on a hexa/pyramid mesh is the user's call), and wait.
