# 2D Mesh Generation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run Mesh on a 2D Study writes `pre_geom2D.msh` with Gmsh, from bodies (faces with `MAT_ID`) and mesh sizes.

**Architecture:** A new `mesher2d.py` (own process, like `mesher.py`) meshes faces with `generate(2)`. What both scripts share (job reading, size fields, writing and replacing the mesh, the one-line `ERROR:`) moves into `meshcommon.py`. `jobwriter` writes a job with `"dimension": "2D"` and a `bodies` list; `runner` starts the script that matches. The add-on switches Run Mesh, Material and Mesh Size on for 2D. Excitations stay 3D-only.

**Tech Stack:** Python 3.11 (Pixi), FreeCAD 1.1 Python API, Gmsh Python API, unittest/pytest, PySide.

**Spec:** [docs/superpowers/specs/2026-10-15-2d-mesh-generation-design.md](../specs/2026-10-15-2d-mesh-generation-design.md)

## Global Constraints

- Run everything through Pixi: `pixi run pytest ...`, `pixi run python ...`. Never `pip install`.
- Format with `pixi run format` and check with `pixi run lint`. Line length is **120**; no trailing comma on a construct that fits on one line. Never run Black/isort or Ruff with overrides.
- **Never sort or reorder imports.** Add new imports next to related ones.
- Only format files you changed.
- `mesher.py`, `mesher2d.py` and `meshcommon.py` run in their own process: **never import FreeCAD** in them.
- Output file names: `pre_geom.msh` (3D), `pre_geom2D.msh` (2D). Scratch files: `mesh.unv` and `job.json` in the scratch folder.
- 2D plane: all faces in z = 0 (XY) **or** all in y = 0 (ZX), tolerance `1e-6`.
- Do not change the 3D job file or 3D behaviour. A job without `"dimension"` is 3D.
- **Never run `git commit`.** At each "Checkpoint" step, stop, tell the user what changed, ask them to check and test it, and suggest the commit message. Wait for their yes. (User rule; it overrides any "commit frequently" habit.)

## Review Focus

- A 2D body made of several faces (a Boolean result with a hole or two parts) gets one `MAT_ID`; it must not fail "expected one entity". Pinned in Task 2.
- Two touching bodies share nodes on the common edge (a conforming mesh). Pinned in Task 2.
- A 2D Study with leftover excitation items must not write them or crash. Pinned in Task 4.
- A 2D body outside both allowed planes (for example lifted by its Part to z = 5) gives a clear error that names the object. Pinned in Task 3.
- A failed 2D run must keep the existing `pre_geom2D.msh`. Pinned in Task 2.

---

### Task 1: Shared module `meshcommon.py`, `mesher.py` uses it

**Files:**
- Create: `freecad_addon/emsolution/meshcommon.py`
- Modify: `freecad_addon/emsolution/mesher.py` (whole file)
- Test: `tests/freecad_addon/test_mesher.py` (unchanged; it is the safety net)

**Interfaces:**
- Produces (used by Task 2):
  - `meshcommon.JobError(Exception)`
  - `meshcommon.apply_size_fields(by_size: dict[float, dict[int, list[int]]]) -> None` (sizes → dim → entity tags)
  - `meshcommon.run(job_path: str, build, dim: int) -> dict` (returns the job dict)
  - `meshcommon.main(argv: list[str], script: str, run_job) -> int`

- [ ] **Step 1: Confirm the 3D tests pass before touching anything**

Run: `pixi run pytest tests/freecad_addon/test_mesher.py -q`
Expected: all pass.

- [ ] **Step 2: Create `meshcommon.py`**

```python
"""What mesher.py (3D) and mesher2d.py (2D) share. Runs in their process. Never import FreeCAD here."""

import json
import os
import sys

import gmsh


class JobError(Exception):
    pass


FIELD_LISTS = {0: "PointsList", 1: "CurvesList", 2: "SurfacesList", 3: "VolumesList"}


def apply_size_fields(by_size):
    """by_size: {size: {dim: [entity tags]}}. One Constant field per size; the smallest size wins."""
    fields = []
    for size, by_dim in by_size.items():
        f = gmsh.model.mesh.field.add("Constant")
        gmsh.model.mesh.field.setNumber(f, "VIn", size)
        for d, tags in by_dim.items():
            gmsh.model.mesh.field.setNumbers(f, FIELD_LISTS[d], tags)
        gmsh.model.mesh.field.setNumber(f, "IncludeBoundary", 1)
        fields.append(f)
    fmin = gmsh.model.mesh.field.add("Min")
    gmsh.model.mesh.field.setNumbers(fmin, "FieldsList", fields)
    gmsh.model.mesh.field.setAsBackgroundMesh(fmin)
    for opt in ("Mesh.MeshSizeExtendFromBoundary", "Mesh.MeshSizeFromPoints", "Mesh.MeshSizeFromCurvature"):
        gmsh.option.setNumber(opt, 0)


def run(job_path, build, dim):
    """Read the job, call build(job, folder) on a fresh model, mesh to dimension dim, write mesh.unv and
    replace job["mesh_file"] with the finished .msh. Returns the job."""
    folder = os.path.dirname(os.path.abspath(job_path))
    with open(job_path, encoding="utf-8") as fh:
        job = json.load(fh)
    msh = os.path.join(folder, "mesh.msh")
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 1)
        gmsh.model.add(job["model_name"])
        build(job, folder)
        for name, value in job.get("options", {}).items():  # the user's mesh settings
            gmsh.option.setNumber(name, value)
        gmsh.option.setNumber("Mesh.ElementOrder", 1)  # set last: the settings may not change it
        gmsh.option.setNumber("Mesh.Optimize", 1)
        gmsh.model.mesh.generate(dim)
        gmsh.option.setNumber("Mesh.MshFileVersion", float(job["msh_version"]))
        gmsh.option.setNumber("Mesh.Binary", 0)
        gmsh.write(msh)
        gmsh.write(os.path.join(folder, "mesh.unv"))
    finally:
        gmsh.finalize()
    try:
        os.replace(msh, job["mesh_file"])  # only a finished mesh replaces the solver's file
    except PermissionError:
        raise JobError(f"Could not replace {job['mesh_file']}: it is read-only or open in another program.") from None
    return job


def main(argv, script, run_job):
    for stream in (sys.stdout, sys.stderr):  # the runner reads UTF-8, whatever the console code page
        stream.reconfigure(encoding="utf-8", errors="replace")
    if len(argv) != 2:
        print(f"ERROR: usage: {script} <job.json>", file=sys.stderr)
        return 1
    try:
        run_job(argv[1])
    except Exception as exc:  # anything -> one clean ERROR line for the runner
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0
```

- [ ] **Step 3: Rewrite `mesher.py` to use it**

Replace the whole file with:

```python
"""Job file -> Gmsh .msh at job["mesh_file"] + mesh.unv beside the job. Runs in its own process.
Never import FreeCAD here.

Usage: python mesher.py <job.json>
"""

import os
import sys

import gmsh

from meshcommon import JobError, apply_size_fields, main, run


def _import_one(path, *dims):
    tags = gmsh.model.occ.importShapes(path, highestDimOnly=True)
    if len(tags) != 1 or tags[0][0] not in dims:
        raise JobError(f"{os.path.basename(path)}: expected one {'/'.join(map(str, dims))}D entity, got {tags}")
    return tags[0]


def build(job, folder):
    """Import, fragment, check, tag and size the model. Gmsh must be initialized."""
    vols, surfs = job["volumes"], job["surfaces"]
    if not vols:
        raise JobError("job has no volumes")
    inputs = [_import_one(os.path.join(folder, v["file"]), 3) for v in vols]
    surf_files = [(s, os.path.join(folder, f)) for s in surfs for f in s["files"]]
    inputs += [_import_one(path, 2) for _, path in surf_files]
    size_files = [(z, os.path.join(folder, f)) for z in job["sizes"] for f in z["files"]]
    inputs += [_import_one(path, 0, 1, 2) for _, path in size_files]

    if len(inputs) == 1:  # Gmsh skips a fragment with no tools and returns no map
        out_map = [inputs]
    else:
        _, out_map = gmsh.model.occ.fragment(inputs[:1], inputs[1:])
    gmsh.model.occ.synchronize()

    body_vols = {}  # MAT_ID -> list of final 3D tags
    owner = {}  # final 3D tag -> body name
    for v, dimtags in zip(vols, out_map):
        tags = [t for d, t in dimtags if d == 3]
        for t in tags:
            if t in owner:
                raise JobError(f"bodies {owner[t]} and {v['name']} overlap")
            owner[t] = v["name"]
        body_vols[v["mat_id"]] = tags

    surf_tags = {s["smat_id"]: [] for s in surfs}
    for (s, _), dimtags in zip(surf_files, out_map[len(vols) :]):
        surf_tags[s["smat_id"]] += [t for d, t in dimtags if d == 2]

    for s in surfs:
        boundary = {
            abs(t)
            for _, t in gmsh.model.getBoundary([(3, t) for t in body_vols[s["mat_id"]]], combined=False, oriented=False)
        }
        if not surf_tags[s["smat_id"]] or not set(surf_tags[s["smat_id"]]) <= boundary:
            raise JobError(
                f"excitation surface {s['name']} does not lie on its body (face did not merge with the body boundary)"
            )

    for v in vols:
        gmsh.model.addPhysicalGroup(3, body_vols[v["mat_id"]], v["mat_id"], name=v["name"])
    for s in surfs:
        gmsh.model.addPhysicalGroup(2, sorted(set(surf_tags[s["smat_id"]])), s["smat_id"], name=s["name"])

    by_size = {}  # size -> {dim: [tags]}
    for v in vols:
        by_size.setdefault(float(v["size"]), {}).setdefault(3, []).extend(body_vols[v["mat_id"]])
    first = len(vols) + len(surf_files)
    for (z, path), dimtags in zip(size_files, out_map[first:]):
        for d, t in dimtags:
            if len(gmsh.model.getAdjacencies(d, t)[0]) == 0:  # nothing above it: not merged
                raise JobError(f"mesh size {z['name']}: {os.path.basename(path)} did not merge with the bodies")
            by_size.setdefault(float(z["size"]), {}).setdefault(d, []).append(t)
    apply_size_fields(by_size)


def run_job(job_path):
    job = run(job_path, build, 3)
    for item in job["volumes"]:
        print(f"MAT_ID  {item['mat_id']:>6}  {item['name']}")
    for item in job["surfaces"]:
        print(f"SMAT_ID {item['smat_id']:>6}  {item['name']}")
    print(f"Wrote {job['mesh_file']}")


if __name__ == "__main__":
    sys.exit(main(sys.argv, "mesher.py", run_job))
```

- [ ] **Step 4: Run the 3D tests again**

Run: `pixi run pytest tests/freecad_addon/test_mesher.py -q`
Expected: all pass, same count as Step 1. If one fails, the refactor changed behaviour: compare with the old code (`git diff`) and fix `meshcommon.py`, not the test.

- [ ] **Step 5: Format and lint**

Run: `pixi run format` then `pixi run lint`
Expected: lint passes. Check `git diff --stat` shows only `meshcommon.py` and `mesher.py` changed.

- [ ] **Step 6: Checkpoint**

Stop. Tell the user: `mesher.py` now uses the new `meshcommon.py`; all 3D mesher tests still pass. Ask them to check. Suggested commit message: `Move what the Gmsh job scripts share into meshcommon.py`. Wait for their yes.

---

### Task 2: `mesher2d.py`

**Files:**
- Create: `freecad_addon/emsolution/mesher2d.py`
- Create: `tests/freecad_addon/test_mesher2d.py`

**Interfaces:**
- Consumes: `meshcommon.JobError`, `apply_size_fields`, `run`, `main` (Task 1).
- Produces: the 2D job file format used by Task 4:
  ```
  {"dimension": "2D", "model_name": str, "msh_version": float, "mesh_file": str,
   "options": {gmsh option: number}, "bodies": [{"mat_id": int, "name": str, "file": str, "size": float}],
   "sizes": [{"name": str, "size": float, "files": [str]}]}
  ```
  Paths in the job are relative to the folder of `job.json`.
- Script usage: `python mesher2d.py <job.json>`; exit 0 and prints `Wrote <mesh_file>`; on failure exit 1 and the last stderr line is `ERROR: ...`.

- [ ] **Step 1: Write the failing tests**

Create `tests/freecad_addon/test_mesher2d.py`:

```python
"""2D mesher tests. Run from the repo root: pixi run pytest tests/freecad_addon/test_mesher2d.py"""

import json
import math
import os
import stat
import subprocess
import sys
import tempfile
import unittest

import gmsh

from .test_mesher import write_line, write_point

MESHER2D = os.path.join(os.path.dirname(__file__), "..", "..", "freecad_addon", "emsolution", "mesher2d.py")


def write_rects(path, rects, plane="XY"):
    """One BREP holding rectangles (x, y, dx, dy) in the XY plane, or turned into the ZX plane (y = 0)."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        tags = [gmsh.model.occ.addRectangle(x, y, 0, dx, dy) for x, y, dx, dy in rects]
        if plane == "ZX":
            gmsh.model.occ.rotate([(2, t) for t in tags], 0, 0, 0, 1, 0, 0, math.pi / 2)  # (x, y, 0) -> (x, 0, y)
        gmsh.model.occ.synchronize()
        gmsh.write(path)
    finally:
        gmsh.finalize()


def write_box(path):
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.model.occ.addBox(0, 0, 0, 1, 1, 1)
        gmsh.model.occ.synchronize()
        gmsh.write(path)
    finally:
        gmsh.finalize()


class Mesher2DTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name
        os.mkdir(os.path.join(self.dir, "geometry"))

    def tearDown(self):
        self.tmp.cleanup()

    def geo(self, name):
        return os.path.join(self.dir, "geometry", name)

    def body(self, id_, name, file, size=0.5):
        return {"mat_id": id_, "name": name, "file": "geometry/" + file, "size": size}

    def run_job(self, bodies, sizes=(), version=4.1, options=None, mesh_file=None):
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
        path = os.path.join(self.dir, "job.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(job, fh)
        return subprocess.run([sys.executable, MESHER2D, path], capture_output=True, encoding="utf-8", errors="replace")

    def open_msh(self):
        gmsh.initialize()
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(os.path.join(self.dir, "pre_geom2D.msh"))
        self.addCleanup(gmsh.finalize)

    def triangles(self, group):
        ents = gmsh.model.getEntitiesForPhysicalGroup(2, group)
        return sum(len(gmsh.model.mesh.getElements(2, e)[1][0]) for e in ents)

    def last_error(self, r):
        self.assertEqual(r.returncode, 1)
        last = r.stderr.strip().splitlines()[-1]
        self.assertTrue(last.startswith("ERROR:"), last)
        return last

    def test_two_touching_squares_get_ids_names_triangles_and_shared_nodes(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        write_rects(self.geo("vol_2.brep"), [(1, 0, 1, 1)])
        r = self.run_job([self.body(1, "Copper_Sq", "vol_1.brep"), self.body(2, "Air_Sq001", "vol_2.brep")])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.path.exists(os.path.join(self.dir, "mesh.unv")))
        self.open_msh()
        groups = {t: gmsh.model.getPhysicalName(2, t) for _, t in gmsh.model.getPhysicalGroups(2)}
        self.assertEqual(groups, {1: "Copper_Sq", 2: "Air_Sq001"})
        self.assertEqual(list(gmsh.model.mesh.getElementTypes(2)), [2], "only 3-node triangles")
        nodes1 = set(gmsh.model.mesh.getNodesForPhysicalGroup(2, 1)[0])
        nodes2 = set(gmsh.model.mesh.getNodesForPhysicalGroup(2, 2)[0])
        self.assertTrue(nodes1 & nodes2, "no shared nodes on the common edge")

    def test_body_of_several_faces_is_one_group(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1), (1, 0, 1, 1)])  # one body, two touching faces
        r = self.run_job([self.body(1, "Two_Part", "vol_1.brep")])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        self.assertEqual(gmsh.model.getPhysicalName(2, 1), "Two_Part")
        self.assertEqual(len(gmsh.model.getEntitiesForPhysicalGroup(2, 1)), 2)

    def test_smaller_size_gives_denser_mesh(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        write_rects(self.geo("vol_2.brep"), [(1, 0, 1, 1)])
        r = self.run_job(
            [self.body(1, "Fine_Sq", "vol_1.brep", size=0.05), self.body(2, "Coarse_Sq", "vol_2.brep", size=0.5)]
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        self.assertGreater(self.triangles(1), 20 * self.triangles(2))

    def mesh_square_with_size(self, make=None, size=0.05):
        """Mesh a unit square at size 0.5, plus one size item from geometry/size_1_1.brep when make(path) writes it.
        Returns the node coordinates as (x, y, z) tuples."""
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        sizes = []
        if make:
            make(self.geo("size_1_1.brep"))
            sizes = [{"name": "Fine", "size": size, "files": ["geometry/size_1_1.brep"]}]
        r = self.run_job([self.body(1, "Copper_Sq", "vol_1.brep")], sizes=sizes)
        self.assertEqual(r.returncode, 0, r.stderr)
        gmsh.initialize()
        try:
            gmsh.option.setNumber("General.Terminal", 0)
            gmsh.open(os.path.join(self.dir, "pre_geom2D.msh"))
            c = gmsh.model.mesh.getNodes()[1]
        finally:
            gmsh.finalize()
        return [tuple(c[i : i + 3]) for i in range(0, len(c), 3)]

    def test_face_size_refines_that_face(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        write_rects(self.geo("vol_2.brep"), [(1, 0, 1, 1)])
        write_rects(self.geo("size_1_1.brep"), [(1, 0, 1, 1)])  # the second square, as a size item
        r = self.run_job(
            [self.body(1, "A_Sq", "vol_1.brep"), self.body(2, "B_Sq001", "vol_2.brep")],
            sizes=[{"name": "Fine", "size": 0.05, "files": ["geometry/size_1_1.brep"]}],
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        self.assertGreater(self.triangles(2), 20 * self.triangles(1))

    def test_edge_size_refines_that_edge(self):
        nodes = self.mesh_square_with_size(lambda p: write_line(p, (0, 0, 0), (1, 0, 0)))  # the bottom edge
        bottom = sum(abs(y) < 1e-9 for x, y, z in nodes)
        top = sum(abs(y - 1) < 1e-9 for x, y, z in nodes)
        self.assertGreaterEqual(bottom, 20)
        self.assertLess(top, 5)

    def test_vertex_size_refines_around_that_corner(self):
        def near_corner(nodes):
            return sum(0 < x * x + y * y < 0.3**2 for x, y, z in nodes)

        before = near_corner(self.mesh_square_with_size())
        after = near_corner(self.mesh_square_with_size(lambda p: write_point(p, (0, 0, 0))))
        self.assertGreater(after, before)

    def test_zx_plane_keeps_y_zero(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)], plane="ZX")
        r = self.run_job([self.body(1, "Copper_Sq", "vol_1.brep")])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        coords = gmsh.model.mesh.getNodes()[1]
        self.assertTrue(len(coords) > 0)
        for y in coords[1::3]:
            self.assertAlmostEqual(y, 0.0, places=9)
        self.assertGreater(max(coords[2::3]), 0.9)  # the square really stands along z

    def test_options_are_applied(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        plain = self.run_job([self.body(1, "Copper_Sq", "vol_1.brep")])
        self.assertEqual(plain.returncode, 0, plain.stderr)
        self.open_msh()
        before = self.triangles(1)
        finer = self.run_job([self.body(1, "Copper_Sq", "vol_1.brep")], options={"Mesh.MeshSizeFactor": 0.5})
        self.assertEqual(finer.returncode, 0, finer.stderr)
        gmsh.clear()
        gmsh.open(os.path.join(self.dir, "pre_geom2D.msh"))
        self.assertGreater(self.triangles(1), 2 * before)

    def test_unknown_option_fails_cleanly(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        r = self.run_job([self.body(1, "Copper_Sq", "vol_1.brep")], options={"Mesh.NoSuchOption": 1})
        self.assertIn("NoSuchOption", self.last_error(r))

    def test_msh_version_22(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        r = self.run_job([self.body(1, "Copper_Sq", "vol_1.brep")], version=2.2)
        self.assertEqual(r.returncode, 0, r.stderr)
        with open(os.path.join(self.dir, "pre_geom2D.msh"), encoding="ascii") as fh:
            self.assertEqual(fh.read().split()[:2], ["$MeshFormat", "2.2"])

    def test_mesh_goes_to_mesh_file_and_unv_beside_the_job(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        target = os.path.join(self.dir, "run dir", "pre_geom2D.msh")
        os.mkdir(os.path.dirname(target))
        r = self.run_job([self.body(1, "Copper_Sq", "vol_1.brep")], mesh_file=target)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.path.isfile(target))
        self.assertTrue(os.path.isfile(os.path.join(self.dir, "mesh.unv")))
        self.assertFalse(os.path.exists(os.path.join(self.dir, "pre_geom2D.msh")))
        self.assertIn("MAT_ID", r.stdout)
        self.assertIn(f"Wrote {target}", r.stdout)

    def write_old_mesh(self):
        path = os.path.join(self.dir, "pre_geom2D.msh")
        with open(path, "w", encoding="ascii") as fh:
            fh.write("old")
        return path

    def read_text(self, path):
        with open(path, encoding="ascii") as fh:
            return fh.read()

    def test_existing_mesh_is_replaced(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        target = self.write_old_mesh()
        r = self.run_job([self.body(1, "Copper_Sq", "vol_1.brep")])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(self.read_text(target).startswith("$MeshFormat"))

    def test_failed_run_keeps_the_existing_mesh(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        write_rects(self.geo("vol_2.brep"), [(0.5, 0, 1, 1)])  # overlaps vol_1
        target = self.write_old_mesh()
        r = self.run_job([self.body(1, "A_Sq", "vol_1.brep"), self.body(2, "B_Sq001", "vol_2.brep")])
        self.last_error(r)
        self.assertEqual(self.read_text(target), "old")

    def test_read_only_mesh_fails_cleanly_and_stays(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        target = self.write_old_mesh()
        os.chmod(target, stat.S_IREAD)
        try:
            r = self.run_job([self.body(1, "Copper_Sq", "vol_1.brep")])
        finally:
            os.chmod(target, stat.S_IREAD | stat.S_IWRITE)  # let the temporary folder be deleted
        self.assertEqual(
            self.last_error(r), f"ERROR: Could not replace {target}: it is read-only or open in another program."
        )
        self.assertEqual(self.read_text(target), "old")

    def test_overlapping_squares_fail(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        write_rects(self.geo("vol_2.brep"), [(0.5, 0, 1, 1)])
        r = self.run_job([self.body(1, "A_Sq", "vol_1.brep"), self.body(2, "B_Sq001", "vol_2.brep")])
        self.assertIn("overlap", self.last_error(r))

    def test_size_item_off_the_bodies_fails(self):
        write_rects(self.geo("vol_1.brep"), [(0, 0, 1, 1)])
        write_rects(self.geo("size_1_1.brep"), [(5, 5, 1, 1)])  # a square far from the body
        r = self.run_job(
            [self.body(1, "Copper_Sq", "vol_1.brep")],
            sizes=[{"name": "Fine", "size": 0.1, "files": ["geometry/size_1_1.brep"]}],
        )
        self.assertIn("Fine", self.last_error(r))

    def test_a_solid_body_fails(self):
        write_box(self.geo("vol_1.brep"))
        r = self.run_job([self.body(1, "Copper_Box", "vol_1.brep")])
        self.assertIn("vol_1.brep", self.last_error(r))

    def test_no_bodies_fails(self):
        self.assertIn("no bodies", self.last_error(self.run_job([])))

    def test_missing_geometry_file_fails_cleanly(self):
        self.last_error(self.run_job([self.body(1, "Copper_Sq", "vol_1.brep")]))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pixi run pytest tests/freecad_addon/test_mesher2d.py -q`
Expected: every test FAILS (the script `mesher2d.py` does not exist, so `returncode` is not 0 or the error line is missing).

- [ ] **Step 3: Write `mesher2d.py`**

```python
"""2D job file -> Gmsh .msh at job["mesh_file"] + mesh.unv beside the job. Runs in its own process.
Never import FreeCAD here.

Usage: python mesher2d.py <job.json>
"""

import os
import sys

import gmsh

from meshcommon import JobError, apply_size_fields, main, run


def _import(path, *dims):
    """All entities of a BREP file; every one must have a dimension in dims."""
    tags = gmsh.model.occ.importShapes(path, highestDimOnly=True)
    if not tags or any(d not in dims for d, _ in tags):
        raise JobError(f"{os.path.basename(path)}: expected {'/'.join(map(str, dims))}D entities, got {tags}")
    return tags


def _on_bodies(dim, tag, faces):
    """True when the entity is a body face, or lies on one: an edge of a face, a point of such an edge."""
    if dim == 2:
        return tag in faces
    above = gmsh.model.getAdjacencies(dim, tag)[0]
    if dim == 1:
        return any(t in faces for t in above)
    return any(_on_bodies(1, t, faces) for t in above)


def build(job, folder):
    """Import, fragment, check, tag and size the model. Gmsh must be initialized."""
    bodies = job["bodies"]
    if not bodies:
        raise JobError("job has no bodies")
    inputs, body_spans = [], []  # body i owns inputs[start:end]
    for b in bodies:
        start = len(inputs)
        inputs += _import(os.path.join(folder, b["file"]), 2)
        body_spans.append((start, len(inputs)))
    size_files = [(z, os.path.join(folder, f)) for z in job["sizes"] for f in z["files"]]
    size_spans = []
    for _, path in size_files:
        start = len(inputs)
        inputs += _import(path, 0, 1, 2)
        size_spans.append((start, len(inputs)))

    if len(inputs) == 1:  # Gmsh skips a fragment with no tools and returns no map
        out_map = [inputs]
    else:
        _, out_map = gmsh.model.occ.fragment(inputs[:1], inputs[1:])
    gmsh.model.occ.synchronize()

    body_faces = {}  # MAT_ID -> list of final 2D tags
    owner = {}  # final 2D tag -> body name
    for b, (start, end) in zip(bodies, body_spans):
        tags = sorted({t for dimtags in out_map[start:end] for d, t in dimtags if d == 2})
        for t in tags:
            if owner.get(t, b["name"]) != b["name"]:
                raise JobError(f"bodies {owner[t]} and {b['name']} overlap")
            owner[t] = b["name"]
        body_faces[b["mat_id"]] = tags

    for b in bodies:
        gmsh.model.addPhysicalGroup(2, body_faces[b["mat_id"]], b["mat_id"], name=b["name"])

    by_size = {}  # size -> {dim: [tags]}
    for b in bodies:
        by_size.setdefault(float(b["size"]), {}).setdefault(2, []).extend(body_faces[b["mat_id"]])
    for (z, path), (start, end) in zip(size_files, size_spans):
        for dimtags in out_map[start:end]:
            for d, t in dimtags:
                if not _on_bodies(d, t, owner):
                    raise JobError(f"mesh size {z['name']}: {os.path.basename(path)} did not merge with the bodies")
                by_size.setdefault(float(z["size"]), {}).setdefault(d, []).append(t)
    apply_size_fields(by_size)


def run_job(job_path):
    job = run(job_path, build, 2)
    for item in job["bodies"]:
        print(f"MAT_ID  {item['mat_id']:>6}  {item['name']}")
    print(f"Wrote {job['mesh_file']}")


if __name__ == "__main__":
    sys.exit(main(sys.argv, "mesher2d.py", run_job))
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `pixi run pytest tests/freecad_addon/test_mesher2d.py -q`
Expected: all pass.

If a test fails because of Gmsh behaviour (not a typo), look at it before changing code:
- `test_body_of_several_faces_is_one_group`: if `importShapes` merges the two faces into one, the `len(...) == 2` assert is the only thing wrong; relax it to `>= 1`.
- `test_edge_size_refines_that_edge` / `test_vertex_size...`: if `_on_bodies` wrongly raises "did not merge", print `gmsh.model.getAdjacencies(dim, tag)` for the failing entity in a throwaway script and fix `_on_bodies` to match what Gmsh reports. Do not remove the check.
- `test_options_are_applied` uses `gmsh.clear()` on the open model from `open_msh`; if that errors, call `gmsh.finalize()` and `gmsh.initialize()` again instead.

- [ ] **Step 5: Also run the 3D tests (shared code)**

Run: `pixi run pytest tests/freecad_addon/test_mesher.py tests/freecad_addon/test_mesher2d.py -q`
Expected: all pass.

- [ ] **Step 6: Format and lint**

Run: `pixi run format` then `pixi run lint`
Expected: lint passes; only the two new files changed.

- [ ] **Step 7: Checkpoint**

Stop. Tell the user: `mesher2d.py` meshes faces (several faces per body, sizes on faces/edges/points, XY and ZX); 2D mesher tests pass. Ask them to check. Suggested commit message: `Add mesher2d.py: Gmsh 2D meshing of faces with MAT_ID groups and local sizes`. Wait for their yes.

---

### Task 3: Plane rule and 2D no longer blocked in `geometry.py`

**Files:**
- Modify: `freecad_addon/emsolution/geometry.py:26-84` (`collect`) and `:129-134` (`export_unavailable`)
- Modify: `tests/freecad_addon/test_study.py:642-655` (plane test) and `:725-737` (deferred export test)

**Interfaces:**
- Produces (used by Task 4): `geometry.plane_of(face) -> "XY" | "ZX" | None`; `geometry.collect(roots, "2D")` accepts only faces in z = 0 or all in y = 0; `geometry.export_unavailable(study)` returns `""` for a 2D Study without sliding motion.

- [ ] **Step 1: Write the failing tests**

In `tests/freecad_addon/test_study.py`, replace `test_planar_sources_are_checked_in_global_coordinates` (lines 642-655) with:

```python
    def test_planar_sources_are_checked_in_global_coordinates(self):
        a, b = self.face("A"), self.face("B", 5)  # b is lifted to z = 5
        part = self.doc.addObject("App::Part", "Part")
        part.addObject(a)
        part.Placement.Base = App.Vector(0, 0, 5)  # and so is a, by its Part
        self.doc.recompute()
        for lifted in (a, b):
            found, errors = geometry.collect([lifted], "2D")
            self.assertEqual(found, [])
            self.assertIn("XY plane", errors[0])
            self.assertIn(lifted.Label, errors[0])
        part.Placement = App.Placement()
        self.doc.recompute()
        self.assertEqual(geometry.collect([a], "2D"), ([a], []))
        self.assertIn("exactly one solid", geometry.collect([b], "3D")[1][0])
        self.assertIn("without solids", geometry.collect([self.box("Solid")], "2D")[1][0])

    def test_2d_faces_may_be_in_the_zx_plane_but_not_in_both(self):
        xy, zx = self.face("XY"), self.face("ZX")
        zx.Placement = App.Placement(App.Vector(0, 0, 0), App.Rotation(App.Vector(1, 0, 0), 90))  # (x, y, 0) -> (x, 0, y)
        self.doc.recompute()
        self.assertEqual(geometry.collect([zx], "2D"), ([zx], []))
        found, errors = geometry.collect([xy, zx], "2D")
        self.assertEqual(found, [xy])
        self.assertIn("share one plane", errors[0])
```

Replace `test_deferred_export_cannot_change_ids_or_write_files` (lines 725-737) with (the 2D row is gone; add the 2D-not-blocked test after it):

```python
    def test_deferred_export_cannot_change_ids_or_write_files(self):
        self.include(self.box("A"))
        self.study.Movement = "Sliding motion"
        with self.assertRaisesRegex(jobwriter.StudyError, "Sliding-motion"):
            jobwriter.write_job(self.study)
        self.assertEqual(self.study.MatIds, {})
        self.assertFalse(os.path.exists(self.scratch("job.json")))

    def test_2d_study_is_not_blocked_but_sliding_motion_still_is(self):
        study = objects.make_study(self.doc, "2D", "Section")
        self.assertEqual(geometry.export_unavailable(study), "")
        study.Movement = "Sliding motion"
        self.assertIn("Sliding-motion", geometry.export_unavailable(study))
```

- [ ] **Step 2: Run to verify they fail**

Run: `pixi run pytest tests/freecad_addon/test_study.py -k "planar_sources or zx_plane or deferred_export or not_blocked" -q`
Expected: FAIL (no "XY plane" message; ZX face rejected as not sharing a plane with the check; `export_unavailable` still returns the 2D text).

- [ ] **Step 3: Implement**

In `geometry.py`, add above `collect` (after `is_source`):

```python
PLANE_TOL = 1e-6


def plane_of(face):
    """"XY" for a face in the plane z = 0, "ZX" for a face in the plane y = 0, else None."""
    box = face.BoundBox
    if max(abs(box.ZMin), abs(box.ZMax)) < PLANE_TOL:
        return "XY"
    if max(abs(box.YMin), abs(box.YMax)) < PLANE_TOL:
        return "ZX"
    return None
```

In `collect`, replace the loop body that starts at `for face in shape.Faces:` (lines 70-80) with:

```python
            for face in shape.Faces:
                if not face.Surface.isPlanar():
                    errors.append(f"{obj.Label}: 2D faces must be planar.")
                    valid = False
                    break
                found = plane_of(face)
                if found is None:
                    errors.append(f"{obj.Label}: 2D faces must lie in the XY plane (z = 0) or the ZX plane (y = 0).")
                    valid = False
                    break
                if plane is None:
                    plane = found
                elif found != plane:
                    errors.append(f"{obj.Label}: 2D faces must share one plane.")
                    valid = False
                    break
```

In `export_unavailable`, delete the two lines:

```python
    if study.Dimension != "3D":
        return "2D mesh generation is planned for a later phase. You can save this setup now."
```

- [ ] **Step 4: Run to verify they pass**

Run: `pixi run pytest tests/freecad_addon/test_study.py -q`
Expected: all pass. If the lifted face test fails because `BoundBox` includes a tiny margin larger than `1e-6`, print `face.BoundBox` for a z = 0 square in a throwaway `pixi run python` script and raise `PLANE_TOL` just above that margin (keep it below `1e-3`).

- [ ] **Step 5: Format and lint**

Run: `pixi run format` then `pixi run lint`
Expected: lint passes.

- [ ] **Step 6: Checkpoint**

Stop. Tell the user: 2D faces must lie in XY or ZX with a clear error; 2D Studies are no longer blocked by `export_unavailable` (sliding motion still is). Suggested commit message: `2D geometry must lie in the XY or ZX plane; stop blocking 2D export`. Wait for their yes.

---

### Task 4: 2D job in `jobwriter`, no excitations in 2D, runner picks the script

**Files:**
- Modify: `freecad_addon/emsolution/jobwriter.py:40-156` (`check`, `mesh_options`, `write_job`)
- Modify: `freecad_addon/emsolution/objects.py:495-501` (`surface_keys`)
- Modify: `freecad_addon/emsolution/runner.py:1-58`
- Modify: `tests/freecad_addon/test_study.py` (new tests; constant `MESHER2D`)

**Interfaces:**
- Consumes: 2D job format from Task 2; `geometry.export_unavailable` and the plane rule from Task 3.
- Produces: `jobwriter.mesh_options(settings, dimension="3D") -> dict`; `jobwriter.write_job(study)` writes `"dimension": "2D"` and `"bodies"` (no `"volumes"`, no `"surfaces"`) for a 2D Study; `runner.MESHER_2D` path.

- [ ] **Step 1: Write the failing tests**

In `test_study.py`, next to `MESHER = ...` add:

```python
MESHER2D = os.path.join(os.path.dirname(__file__), "..", "..", "freecad_addon", "emsolution", "mesher2d.py")
```

Add these tests inside `StudyTest` (near `test_bodies_without_materials_are_meshed_and_listed`):

```python
    def make_2d_study(self, *faces):
        study = objects.make_study(self.doc, "2D", "Section")
        study.MainMode, study.MainObjects = "Manual", list(faces)
        study.MeshSizesGroup.DefaultMeshSize = 5
        return study

    def test_2d_study_writes_a_2d_job_and_meshes_it(self):
        a, b = self.face("A"), self.face("B")
        b.Placement.Base = App.Vector(10, 0, 0)  # touches A along x = 10
        study = self.make_2d_study(a, b)
        objects.make_mesh_size(study, 1.0, [(a, "Edge1")])
        path = jobwriter.write_job(study)
        with open(path, encoding="utf-8") as fh:
            job = json.load(fh)
        self.assertEqual(job["dimension"], "2D")
        self.assertEqual([(v["mat_id"], v["name"]) for v in job["bodies"]], [(1, "A"), (2, "B")])
        self.assertNotIn("volumes", job)
        self.assertNotIn("surfaces", job)
        self.assertEqual(len(job["sizes"]), 1)
        self.assertNotIn("Mesh.Algorithm3D", job["options"])
        self.assertEqual(job["mesh_file"], os.path.join(self.tmp.name, "pre_geom2D.msh"))
        result = subprocess.run(
            [sys.executable, MESHER2D, path], capture_output=True, encoding="utf-8", errors="replace"
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        with open(job["mesh_file"], encoding="utf-8") as fh:
            names = fh.read().split("$PhysicalNames\n", 1)[1].split("$EndPhysicalNames", 1)[0]
        self.assertIn('2 1 "A"', names)
        self.assertIn('2 2 "B"', names)

    def test_3d_job_keeps_its_old_shape(self):
        self.include(self.box("A"))
        with open(jobwriter.write_job(self.study), encoding="utf-8") as fh:
            job = json.load(fh)
        self.assertNotIn("dimension", job)
        self.assertEqual([v["name"] for v in job["volumes"]], ["A"])
        self.assertIn("Mesh.Algorithm3D", job["options"])

    def test_2d_study_ignores_excitation_items(self):
        a = self.face("A")
        study = self.make_2d_study(a)
        objects.make_excitation(study, "Terminal", [(a, "Face1")])
        with open(jobwriter.write_job(study), encoding="utf-8") as fh:
            job = json.load(fh)
        self.assertNotIn("surfaces", job)
        self.assertEqual(study.SmatIds, {})

    def test_2d_body_outside_the_planes_is_a_study_error(self):
        study = self.make_2d_study(self.face("Lifted", 5))
        with self.assertRaisesRegex(jobwriter.StudyError, "XY plane"):
            jobwriter.check(study)
```

- [ ] **Step 2: Run to verify they fail**

Run: `pixi run pytest tests/freecad_addon/test_study.py -k "2d_ or 3d_job" -q`
Expected: FAIL (`write_job` produces a `volumes` job; the 2D mesher gets the wrong keys; `mesh_options` has no dimension).

- [ ] **Step 3: Implement `objects.surface_keys`**

In `objects.py`, replace `surface_keys` with:

```python
def surface_keys(study):
    if study.Dimension == "2D":
        return []  # 2D Studies have no excitations yet
    included = set(volume_keys(study))
    return list(
        dict.fromkeys(
            f"{e.Name}|{b.Name}" for e in excitations(study) for b, _ in subs_by_body(e) if b.Name in included
        )
    )
```

- [ ] **Step 4: Implement `jobwriter`**

In `check`, change the `surfaces = [...]` statement (lines 54-56) to:

```python
    excitation_items = objects.excitations(study) if study.Dimension == "3D" else []  # 2D: none yet
    surfaces = [
        (e, b, faces) for e in excitation_items for b, faces in objects.subs_by_body(e) if b.Name in included
    ]
```

Replace `mesh_options` with:

```python
def mesh_options(settings, dimension="3D"):
    """Gmsh options from the Mesh Sizes folder; a min or max size of 0 keeps Gmsh's default."""
    opts = {
        "Mesh.Algorithm": objects.ALGORITHMS_2D[settings.SurfaceAlgorithm],
        "Mesh.MeshSizeFactor": settings.SizeFactor,
        "Mesh.Smoothing": settings.SmoothingSteps,
    }
    if dimension == "3D":
        opts["Mesh.Algorithm3D"] = objects.ALGORITHMS_3D[settings.VolumeAlgorithm]
        opts["Mesh.OptimizeNetgen"] = int(settings.OptimizeNetgen)
    if settings.MinSize.Value > 0:
        opts["Mesh.MeshSizeMin"] = settings.MinSize.Value
    if settings.MaxSize.Value > 0:
        opts["Mesh.MeshSizeMax"] = settings.MaxSize.Value
    return opts
```

In `write_job`, replace the `job = {...}` block and the `for body, size in volumes:` loop (lines 125-138) with:

```python
    two_d = study.Dimension == "2D"
    job = {
        "model_name": objects.clean(study.Label),
        "msh_version": float(study.MshVersion),
        "mesh_file": mesh_file(study),
        "options": mesh_options(study.MeshSizesGroup, study.Dimension),
    }
    if two_d:
        job["dimension"] = "2D"
        job["bodies"] = []
    else:
        job["volumes"] = []
        job["surfaces"] = []
    job["sizes"] = []
    for body, size in volumes:
        mat_id = int(study.MatIds[body.Name])
        rel = f"geometry/vol_{mat_id}.brep"
        global_shape(body).exportBrep(os.path.join(folder, rel))
        job["bodies" if two_d else "volumes"].append(
            {"mat_id": mat_id, "name": objects.volume_name(body), "file": rel, "size": size}
        )
```

(The `for exc, body, faces in surfaces:` loop below stays as is: `surfaces` is empty in 2D, so `job["surfaces"]` is never touched.) Also update the module docstring's first line to `"""Study -> checks -> job.json + BREP files for mesher.py / mesher2d.py."""`.

- [ ] **Step 5: Implement `runner`**

In `runner.py` replace lines 1 and 13 and the start of `MeshRun.__init__`:

```python
"""Run mesher.py or mesher2d.py in a background process, stream its output, load the result."""
```

```python
MESHER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mesher.py")
MESHER_2D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mesher2d.py")
```

and in `MeshRun.__init__` replace

```python
        with open(job, encoding="utf-8") as fh:
            self.mesh_file = json.load(fh)["mesh_file"]
```

with

```python
        with open(job, encoding="utf-8") as fh:
            data = json.load(fh)
        self.mesh_file = data["mesh_file"]
        script = MESHER_2D if data.get("dimension") == "2D" else MESHER
```

and `self.proc.start(python_exe(), [MESHER, job])` with `self.proc.start(python_exe(), [script, job])`.

- [ ] **Step 6: Run to verify they pass**

Run: `pixi run pytest tests/freecad_addon -q --ignore=tests/freecad_addon/gui_smoke.py`
Expected: all pass (3D tests included: the 3D job shape did not change).

- [ ] **Step 7: Format and lint**

Run: `pixi run format` then `pixi run lint`
Expected: lint passes.

- [ ] **Step 8: Checkpoint**

Stop. Tell the user: a 2D Study now writes a 2D job (`bodies`, `"dimension": "2D"`), ignores excitations, and the runner starts `mesher2d.py`; tests pass including a real 2D mesh from a Study. Suggested commit message: `Write a 2D job from a 2D Study and start mesher2d.py for it`. Wait for their yes.

---

### Task 5: Turn the 2D commands and panels on; GUI smoke test

**Files:**
- Modify: `freecad_addon/emsolution/commands.py:48-55`, `:79-83`, `:131-150`
- Modify: `freecad_addon/emsolution/taskpanels.py:353-365`, `:471-472`, `:535`
- Modify: `tests/freecad_addon/gui_smoke.py:451-457` and add a 2D run block

**Interfaces:**
- Consumes: Tasks 3 and 4 (`export_unavailable` empty for 2D, 2D job, `runner.start`).
- Produces: Material, Mesh Size and Run Mesh work for 2D Studies; Excitation is inactive for 2D.

- [ ] **Step 1: Update the smoke test first (it is the failing test)**

In `gui_smoke.py`, replace

```python
    assert not commands.COMMANDS["EMS_Material"].IsActive()
    assert not commands.COMMANDS["EMS_RunMesh"].IsActive()
```

with

```python
    assert commands.COMMANDS["EMS_Material"].IsActive() and commands.COMMANDS["EMS_MeshSize"].IsActive()
    assert not commands.COMMANDS["EMS_Excitation"].IsActive(), "excitations are 3D-only for now"
    assert commands.COMMANDS["EMS_RunMesh"].IsActive()
```

and, right after the line `assert combo.findData("source:" + source.Name) >= 0 and combo.findData("source:" + part.Name) >= 0`, add:

```python
    second.MainMode, second.MainSource = "Container", source
    view.refresh()
    assert view.diagnostics.text() == "", view.diagnostics.text()
    assert view.run_button.isEnabled()
    assert view.export_notice.text() == f"Writes {jobwriter.mesh_file(second)}", view.export_notice.text()
    run2d = runner.start(second)
    assert run2d is not None and run2d.proc.waitForFinished(120000)
    Gui.updateGui()
    assert run2d.error == "" and not runner.busy(), run2d.error
    assert os.path.basename(run2d.mesh_file) == "pre_geom2D.msh" and os.path.isfile(run2d.mesh_file)
    assert second.MeshResult.FemMesh.NodeCount > 0
    log.append("2D mesh ok")
```

- [ ] **Step 2: Run the smoke test to verify it fails**

Run (PowerShell, repo root):

```powershell
Remove-Item "$env:TEMP\ems_gui_smoke.txt" -ErrorAction SilentlyContinue
pixi run freecad tests\freecad_addon\gui_smoke.py
Get-Content "$env:TEMP\ems_gui_smoke.txt" -Tail 15
```

Expected: last line `FAIL` and a traceback at the first new assert (Material still inactive for 2D). If FreeCAD has not linked the add-on, run `pixi run install-addon` once (see the header of `gui_smoke.py` for the throwaway-profile alternative).

- [ ] **Step 3: Implement `commands.py`**

Replace `assignment_study` with:

```python
def assignment_study():
    study = active_study()
    if study is None:
        warn("Select the Study you want to edit first.")
    return study
```

Replace `_StudyCommand.IsActive` with:

```python
class _StudyCommand:
    def IsActive(self):
        return active_study() is not None and not Gui.Control.activeDialog()
```

In `AddExcitation` add an override (excitations are 3D-only until the field sources replace them) and a message guard:

```python
    def IsActive(self):
        study = active_study()
        return study is not None and study.Dimension == "3D" and not Gui.Control.activeDialog()
```

(`AddExcitation.Activated` stays as is; the command is inactive for 2D so it cannot run.)

- [ ] **Step 4: Implement `taskpanels.py`**

Delete the notice block (lines 353-358):

```python
        if study.Dimension == "2D":
            notice = QtWidgets.QLabel(
                "2D material, excitation and local size assignments will be added with 2D meshing."
            )
            notice.setWordWrap(True)
            layout.addWidget(notice)
```

Delete the three lines that disable the settings box for 2D (inside `if isinstance(folder.Proxy, objects.MeshSizesFolder):`):

```python
            if study.Dimension == "2D":
                self.settings.box.setEnabled(False)
                self.settings.box.setToolTip("2D mesh settings will be enabled with 2D generation.")
```

In `open_item` delete

```python
        elif self.study.Dimension != "3D":
            return
```

(the next branch becomes `elif isinstance(self.folder_proxy, objects.MaterialsFolder):`). Change `self.id_button.setEnabled(study.Dimension == "3D")` to `self.id_button.setEnabled(True)` — or simply delete that line, since a button is enabled by default.

- [ ] **Step 5: Run the smoke test to verify it passes**

Run the same commands as Step 2.
Expected: last line `PASS`, and the log contains `2D mesh ok`. FreeCAD may report a crash on quit after that; ignore it (stated in the smoke test header).

If `second.MeshResult.FemMesh.NodeCount` fails because `Fem.read` rejects the 2D `mesh.unv`: stop and tell the user. Do not change the mesher format on your own; the options are loading the `.msh` instead or skipping the preview for 2D, and that is their choice.

- [ ] **Step 6: Run the whole add-on test set**

Run: `pixi run pytest tests/freecad_addon -q --ignore=tests/freecad_addon/gui_smoke.py`
Expected: all pass.

- [ ] **Step 7: Format and lint**

Run: `pixi run format` then `pixi run lint`
Expected: lint passes; only the files in this task changed.

- [ ] **Step 8: Manual check by the user (cannot be automated)**

Ask the user to: open FreeCAD with the add-on, create a 2D Study, put two touching squares (Part::Plane or a Draft rectangle face) in a Part, set it as Main geometry, assign a material to each, add one Mesh Size on an edge, and press Run Mesh. They should check that `pre_geom2D.msh` appears beside the `.FCStd` and the mesh shows in the 3D view. Then, if they can, point an EMSolution input file with `GEOMETRY(12) = 1` at it. This is the check the spec marks "not verified with EMSolution".

- [ ] **Step 9: Checkpoint**

Stop. Tell the user: Run Mesh, Material and Mesh Size now work for 2D Studies, the Excitation command stays off for 2D, the smoke test passes with a real 2D run. Ask them to do the manual check in Step 8. Suggested commit message: `Turn on Run Mesh, Material and Mesh Size for 2D Studies`. Wait for their yes.
