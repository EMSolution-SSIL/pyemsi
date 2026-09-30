# EMSolution Mesher (version 1) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A FreeCAD 1.1 workbench that lets the user tag 3D bodies with materials, excitation faces and mesh sizes in a tree, then writes a Gmsh `.msh` file with fixed physical-group IDs, using Gmsh in a background process.

**Architecture:** Four layers, each in its own file. `mesher.py` turns a `job.json` plus BREP files into `.msh`/`.unv` with Gmsh and never imports FreeCAD. `objects.py` holds the tree objects and the ID table (no GUI). `jobwriter.py` checks the study and writes the job file. The GUI files (`commands.py`, `taskpanels.py`, `runner.py`, `InitGui.py`) only call into those.

**Tech Stack:** FreeCAD 1.1 (Windows) and its bundled Python 3.11, gmsh 4.15.2 Python module and PySide (Qt 6); tests use `unittest`.

**Spec:** `docs/superpowers/specs/2026-09-30-emsolution-mesher-design.md`

## Global Constraints

- Repository: `C:\Users\eskandarih\EMSolution-FreeCAD`. Do not change the FreeCAD source repository.
- FreeCAD 1.1 on Windows, its bundled `python.exe` and gmsh (4.15.2). No extra packages.
- 3D only, first-order tetrahedra, `Mesh.Algorithm3D` = 1, `Mesh.ElementOrder` = 1, `Mesh.Optimize` = 1.
- `mesher.py` must never import FreeCAD.
- Names: `<item Label>_<body Label>`; every character outside `A–Z a–z 0–9 _ -` becomes `_`.
- Volume IDs start at 1, surface IDs at 1001; counters only grow; IDs are keyed by the body's internal Name (and `<excitation Name>|<body Name>` for surfaces).
- Output: `<model_name>.msh` (MSH 4.1 or 2.2, ASCII) and `<model_name>.unv` in the output folder; `model_name` is the cleaned Study Label.
- On any mesher error: last stderr line is `ERROR: <message>`, exit code 1.
- The mesher writes UTF-8 to stdout/stderr whatever the console code page (this PC uses cp932); callers decode UTF-8.

**Python used in every command below** (PowerShell, from the repo root):

```
$py = "C:\Users\eskandarih\AppData\Local\Programs\FreeCAD 1.1\bin\python.exe"
```

This `python.exe` has `gmsh`, and can `import FreeCAD` once `bin` and `lib` are on `sys.path` (the study tests do that themselves). It replaces the spec's `FreeCADCmd` for tests.

## Differences from the spec (decided while prototyping)

- Tests run with FreeCAD's `python.exe`, not `FreeCADCmd`.
- Spec check 2 ("a referenced object no longer exists") needs no code: FreeCAD removes deleted objects from link lists by itself.
- Extra check: an excitation that names a face the body no longer has (for example after the body was edited) → "Reselect the faces".
- Extra check: two group names that become equal after cleanup (for example Persian labels) are refused.
- New IDs skip numbers already used in either table, and editing an ID raises that table's counter above it, so an edit can never cause a clash later.
- The ID table dialog hands out missing IDs when it opens, so new bodies show up there before the first run.
- One study per document. The Material, Excitation and Mesh Size buttons warn when nothing suitable is selected.
- `package.xml` licence is set to `Proprietary`. Change it if another licence applies.

## Review Focus

1. A study with a single body and no excitations must mesh (Gmsh skips a one-entity fragment) → `test_single_box_without_faces`, Task 1.
2. An output folder with spaces or Persian letters must work → `test_folder_with_spaces_and_persian_letters`, Task 1.
3. A terminal on the face shared by two touching bodies must become a surface group on that face → `test_excitation_on_face_shared_by_two_bodies`, Task 1.
4. Labels that become the same name after cleanup (Persian or symbols) must be refused with a clear message, not silently merged → `test_names_equal_after_cleanup_are_refused`, Task 3.
5. A body inside an `App::Part` with its own placement must be exported where the user sees it → `test_body_in_app_part_is_exported_in_global_coordinates`, Task 3.

---

### Task 1: Mesher

**Files:**
- Create: `.gitignore`
- Create: `emsolution/mesher.py`
- Create: `tests/__init__.py` (empty)
- Test: `tests/test_mesher.py`

**Interfaces:**
- Consumes: nothing.
- Produces: command `python.exe emsolution/mesher.py <job.json>`. Job format:
  `{"model_name": str, "msh_version": 4.1 | 2.2, "volumes": [{"id": int, "name": str, "file": "geometry/vol_<id>.brep", "size": float}], "surfaces": [{"id": int, "name": str, "volume_id": int, "files": ["geometry/surf_<id>_<n>.brep", ...]}]}`.
  File paths are relative to `job.json`. Writes `<folder>/<model_name>.msh` and `.unv`. Exit 0 on success; on failure exit 1 with last stderr line `ERROR: ...`.

- [ ] **Step 1: Write `.gitignore` and the failing tests**

`.gitignore`:

```
__pycache__/
```

`tests/__init__.py`: empty file.

`tests/test_mesher.py`:

```python
"""Mesher tests. Run from the repo root with FreeCAD's python.exe:
    python.exe -m unittest tests.test_mesher -v
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

import gmsh

MESHER = os.path.join(os.path.dirname(__file__), "..", "emsolution", "mesher.py")


def write_box(path, x, y, z, dx, dy, dz):
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.model.occ.addBox(x, y, z, dx, dy, dz)
        gmsh.model.occ.synchronize()
        gmsh.write(path)
    finally:
        gmsh.finalize()


def write_rect(path, x, y, z, dx, dy):
    """Rectangle in the plane z = const."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.model.occ.addRectangle(x, y, z, dx, dy)
        gmsh.model.occ.synchronize()
        gmsh.write(path)
    finally:
        gmsh.finalize()


class MesherTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name
        os.mkdir(os.path.join(self.dir, "geometry"))

    def tearDown(self):
        self.tmp.cleanup()

    def geo(self, name):
        return os.path.join(self.dir, "geometry", name)

    def run_job(self, volumes, surfaces=(), version=4.1):
        job = {"model_name": "Model", "msh_version": version,
               "volumes": list(volumes), "surfaces": list(surfaces)}
        path = os.path.join(self.dir, "job.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(job, fh)
        return subprocess.run([sys.executable, MESHER, path],
                              capture_output=True, encoding="utf-8", errors="replace")

    def open_msh(self):
        gmsh.initialize()
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(os.path.join(self.dir, "Model.msh"))
        self.addCleanup(gmsh.finalize)

    def vol(self, id_, name, file, size=0.5):
        return {"id": id_, "name": name, "file": "geometry/" + file, "size": size}

    def test_two_touching_boxes_get_ids_names_and_shared_nodes(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_box(self.geo("vol_2.brep"), 1, 0, 0, 1, 1, 1)
        r = self.run_job([self.vol(1, "Copper_Box", "vol_1.brep"),
                          self.vol(2, "Air_Box001", "vol_2.brep")])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.path.exists(os.path.join(self.dir, "Model.unv")))
        self.open_msh()
        groups = {t: gmsh.model.getPhysicalName(3, t) for _, t in gmsh.model.getPhysicalGroups(3)}
        self.assertEqual(groups, {1: "Copper_Box", 2: "Air_Box001"})
        nodes1 = set(gmsh.model.mesh.getNodesForPhysicalGroup(3, 1)[0])
        nodes2 = set(gmsh.model.mesh.getNodesForPhysicalGroup(3, 2)[0])
        self.assertTrue(nodes1 & nodes2, "no shared nodes on the common face")

    def test_excitation_face_becomes_surface_group(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_rect(self.geo("surf_1001_1.brep"), 0, 0, 1, 1, 1)  # top face
        r = self.run_job([self.vol(1, "Copper_Box", "vol_1.brep")],
                         [{"id": 1001, "name": "Terminal_In_Box", "volume_id": 1,
                           "files": ["geometry/surf_1001_1.brep"]}])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        self.assertEqual(gmsh.model.getPhysicalName(2, 1001), "Terminal_In_Box")
        _, coords = gmsh.model.mesh.getNodesForPhysicalGroup(2, 1001)
        self.assertTrue(len(coords) > 0)
        for z in coords[2::3]:
            self.assertAlmostEqual(z, 1.0, places=6)

    def test_smaller_size_gives_denser_mesh(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_box(self.geo("vol_2.brep"), 1, 0, 0, 1, 1, 1)
        r = self.run_job([self.vol(1, "Fine_Box", "vol_1.brep", size=0.1),
                          self.vol(2, "Coarse_Box", "vol_2.brep", size=0.5)])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()

        def tets(group):
            ents = gmsh.model.getEntitiesForPhysicalGroup(3, group)
            return sum(len(gmsh.model.mesh.getElements(3, e)[1][0]) for e in ents)
        self.assertGreater(tets(1), 5 * tets(2))

    def test_msh_version_22(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        r = self.run_job([self.vol(1, "Copper_Box", "vol_1.brep")], version=2.2)
        self.assertEqual(r.returncode, 0, r.stderr)
        with open(os.path.join(self.dir, "Model.msh"), encoding="ascii") as fh:
            self.assertEqual(fh.read().split()[:2], ["$MeshFormat", "2.2"])

    def test_overlapping_boxes_fail(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_box(self.geo("vol_2.brep"), 0.5, 0, 0, 1, 1, 1)
        r = self.run_job([self.vol(1, "A_Box", "vol_1.brep"),
                          self.vol(2, "B_Box001", "vol_2.brep")])
        self.assertEqual(r.returncode, 1)
        last = r.stderr.strip().splitlines()[-1]
        self.assertIn("ERROR:", last)
        self.assertIn("overlap", last)

    def test_offset_face_fails_merge_check(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_rect(self.geo("surf_1001_1.brep"), 0, 0, 1.5, 1, 1)  # floats above the box
        r = self.run_job([self.vol(1, "Copper_Box", "vol_1.brep")],
                         [{"id": 1001, "name": "Terminal_In_Box", "volume_id": 1,
                           "files": ["geometry/surf_1001_1.brep"]}])
        self.assertEqual(r.returncode, 1)
        last = r.stderr.strip().splitlines()[-1]
        self.assertIn("ERROR:", last)
        self.assertIn("Terminal_In_Box", last)

    def test_missing_geometry_file_fails_cleanly(self):
        r = self.run_job([self.vol(1, "Copper_Box", "vol_1.brep")])
        self.assertEqual(r.returncode, 1)
        self.assertTrue(r.stderr.strip().splitlines()[-1].startswith("ERROR:"))

    def test_single_box_without_faces(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        r = self.run_job([self.vol(1, "Copper_Box", "vol_1.brep")])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        self.assertEqual(gmsh.model.getPhysicalName(3, 1), "Copper_Box")

    def test_excitation_on_face_shared_by_two_bodies(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_box(self.geo("vol_2.brep"), 1, 0, 0, 1, 1, 1)
        gmsh.initialize()  # the x = 1 interface, as a face of box 1
        try:
            gmsh.option.setNumber("General.Terminal", 0)
            gmsh.model.occ.addBox(0, 0, 0, 1, 1, 1)
            gmsh.model.occ.synchronize()
            face = next(t for _, t in gmsh.model.getBoundary([(3, 1)], oriented=False)
                        if abs(gmsh.model.occ.getCenterOfMass(2, t)[0] - 1) < 1e-9)
            gmsh.model.occ.remove([(3, 1)])
            gmsh.model.occ.synchronize()
            gmsh.model.occ.remove([(2, t) for _, t in gmsh.model.getEntities(2) if t != face],
                                  recursive=True)
            gmsh.model.occ.synchronize()
            gmsh.write(self.geo("surf_1001_1.brep"))
        finally:
            gmsh.finalize()
        r = self.run_job([self.vol(1, "Coil_A", "vol_1.brep"), self.vol(2, "Lead_B", "vol_2.brep")],
                         [{"id": 1001, "name": "Terminal_A", "volume_id": 1,
                           "files": ["geometry/surf_1001_1.brep"]}])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.open_msh()
        _, coords = gmsh.model.mesh.getNodesForPhysicalGroup(2, 1001)
        self.assertTrue(len(coords) > 0)
        for x in coords[0::3]:
            self.assertAlmostEqual(x, 1.0, places=6)

    def test_folder_with_spaces_and_persian_letters(self):
        self.dir = os.path.join(self.tmp.name, "my model \u0645\u062f\u0644")
        os.makedirs(os.path.join(self.dir, "geometry"))
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        r = self.run_job([self.vol(1, "Copper_Box", "vol_1.brep")])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.path.exists(os.path.join(self.dir, "Model.msh")))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `& $py -m unittest tests.test_mesher -v`
Expected: all 10 fail (Python cannot open `emsolution\mesher.py`, so return codes are 2, not 0 or 1).

- [ ] **Step 3: Write `emsolution/mesher.py`**

Notes for the implementer: Gmsh returns an empty map when `fragment` gets only one entity ("too few arguments"), so that case is handled by hand. The `getBoundary` keyword is `combined`, not `combine`.

```python
"""Job file -> Gmsh .msh + .unv. Runs in its own process. Never import FreeCAD here.

Usage: python mesher.py <job.json>
"""
import json
import os
import sys

import gmsh


class JobError(Exception):
    pass


def _import_one(path, dim):
    tags = gmsh.model.occ.importShapes(path, highestDimOnly=True)
    if len(tags) != 1 or tags[0][0] != dim:
        raise JobError(f"{os.path.basename(path)}: expected one {dim}D entity, got {tags}")
    return tags[0]


def build(job, folder):
    """Import, fragment, check, tag and size the model. Gmsh must be initialized."""
    vols, surfs = job["volumes"], job["surfaces"]
    if not vols:
        raise JobError("job has no volumes")
    inputs = [_import_one(os.path.join(folder, v["file"]), 3) for v in vols]
    surf_files = [(s, os.path.join(folder, f)) for s in surfs for f in s["files"]]
    inputs += [_import_one(path, 2) for _, path in surf_files]

    if len(inputs) == 1:  # Gmsh skips a fragment with no tools and returns no map
        out_map = [inputs]
    else:
        _, out_map = gmsh.model.occ.fragment(inputs[:1], inputs[1:])
    gmsh.model.occ.synchronize()

    body_vols = {}  # volume id -> list of final 3D tags
    owner = {}      # final 3D tag -> body name
    for v, dimtags in zip(vols, out_map):
        tags = [t for d, t in dimtags if d == 3]
        for t in tags:
            if t in owner:
                raise JobError(f"bodies {owner[t]} and {v['name']} overlap")
            owner[t] = v["name"]
        body_vols[v["id"]] = tags

    surf_tags = {s["id"]: [] for s in surfs}
    for (s, path), dimtags in zip(surf_files, out_map[len(vols):]):
        surf_tags[s["id"]] += [t for d, t in dimtags if d == 2]

    for s in surfs:
        boundary = {abs(t) for _, t in gmsh.model.getBoundary(
            [(3, t) for t in body_vols[s["volume_id"]]], combined=False, oriented=False)}
        if not surf_tags[s["id"]] or not set(surf_tags[s["id"]]) <= boundary:
            raise JobError(f"excitation surface {s['name']} does not lie on its body "
                           f"(face did not merge with the body boundary)")

    for v in vols:
        gmsh.model.addPhysicalGroup(3, body_vols[v["id"]], v["id"], name=v["name"])
    for s in surfs:
        gmsh.model.addPhysicalGroup(2, sorted(set(surf_tags[s["id"]])), s["id"], name=s["name"])

    by_size = {}
    for v in vols:
        by_size.setdefault(float(v["size"]), []).extend(body_vols[v["id"]])
    fields = []
    for size, tags in by_size.items():
        f = gmsh.model.mesh.field.add("Constant")
        gmsh.model.mesh.field.setNumber(f, "VIn", size)
        gmsh.model.mesh.field.setNumbers(f, "VolumesList", tags)
        gmsh.model.mesh.field.setNumber(f, "IncludeBoundary", 1)
        fields.append(f)
    fmin = gmsh.model.mesh.field.add("Min")
    gmsh.model.mesh.field.setNumbers(fmin, "FieldsList", fields)
    gmsh.model.mesh.field.setAsBackgroundMesh(fmin)
    for opt in ("Mesh.MeshSizeExtendFromBoundary", "Mesh.MeshSizeFromPoints",
                "Mesh.MeshSizeFromCurvature"):
        gmsh.option.setNumber(opt, 0)


def run(job_path):
    folder = os.path.dirname(os.path.abspath(job_path))
    with open(job_path, encoding="utf-8") as fh:
        job = json.load(fh)
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 1)
        gmsh.model.add(job["model_name"])
        build(job, folder)
        gmsh.option.setNumber("Mesh.Algorithm3D", 1)
        gmsh.option.setNumber("Mesh.ElementOrder", 1)
        gmsh.option.setNumber("Mesh.Optimize", 1)
        gmsh.model.mesh.generate(3)
        gmsh.option.setNumber("Mesh.MshFileVersion", float(job["msh_version"]))
        gmsh.option.setNumber("Mesh.Binary", 0)
        base = os.path.join(folder, job["model_name"])
        gmsh.write(base + ".msh")
        gmsh.write(base + ".unv")
    finally:
        gmsh.finalize()
    for item in job["volumes"] + job["surfaces"]:
        print(f"{item['id']:>6}  {item['name']}")
    print(f"Wrote {base}.msh")


def main(argv):
    for stream in (sys.stdout, sys.stderr):  # the runner reads UTF-8, whatever the console code page
        stream.reconfigure(encoding="utf-8", errors="replace")
    if len(argv) != 2:
        print("ERROR: usage: mesher.py <job.json>", file=sys.stderr)
        return 1
    try:
        run(argv[1])
    except Exception as exc:  # anything -> one clean ERROR line for the runner
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

- [ ] **Step 4: Run the tests to see them pass**

Run: `& $py -m unittest tests.test_mesher -v`
Expected: `Ran 10 tests ... OK`.

- [ ] **Step 5: Commit**

```
git add .gitignore emsolution/mesher.py tests/__init__.py tests/test_mesher.py
git commit -m "Add Gmsh mesher that turns a job file into a .msh with physical groups"
```

---

### Task 2: Study tree objects and ID table

**Files:**
- Create: `emsolution/__init__.py`
- Create: `emsolution/objects.py`
- Test: `tests/test_study.py`

**Interfaces:**
- Consumes: nothing.
- Produces (`emsolution`): `icon(name) -> str` (path of `icons/<name>.svg`).
- Produces (`emsolution.objects`):
  - `clean(text) -> str`, `item_name(item, body) -> str`
  - classes `Study`, `Material`, `Excitation`, `MeshSize` (proxies; constructor takes the FreeCAD object)
  - `make_study(doc) -> study` (`App::DocumentObjectGroupPython` with properties `OutputFolder`, `DefaultMeshSize`, `MshVersion`, `VolumeIds`, `SurfaceIds`, `NextVolumeId`, `NextSurfaceId`, `MaterialsGroup`, `ExcitationsGroup`, `MeshSizesGroup`, `MeshResult`)
  - `find_study(doc) -> study | None`
  - `make_material(study, label, bodies)`, `make_excitation(study, label, [(body, "FaceN")])`, `make_mesh_size(study, size, bodies)`; each returns the new `App::FeaturePython`
  - `materials(study)`, `excitations(study)`, `mesh_sizes(study)` -> lists in tree order
  - `owning_body(obj)` -> the `PartDesign::Body` that holds `obj`, else `obj`
  - `faces_by_body(excitation) -> [(body, [face names])]`
  - `update_ids(study)`, `set_id(study, "VolumeIds" | "SurfaceIds", key, int)` (raises `ValueError`), `id_rows(study) -> [(table, key, name, id)]`

- [ ] **Step 1: Write the failing tests**

`tests/test_study.py`:

```python
"""Study, ID table and job writer tests. Run from the repo root with FreeCAD's python.exe:
    python.exe -m unittest tests.test_study -v
"""
import os
import sys
import tempfile
import unittest

_BIN = os.path.dirname(sys.executable)
sys.path[:0] = [_BIN, os.path.join(_BIN, "..", "lib")]

import FreeCAD as App  # noqa: E402

from emsolution import objects  # noqa: E402


class StudyTest(unittest.TestCase):
    def setUp(self):
        self.doc = App.newDocument("T")
        self.tmp = tempfile.TemporaryDirectory()
        self.study = objects.make_study(self.doc)
        self.study.OutputFolder = self.tmp.name

    def tearDown(self):
        App.closeDocument(self.doc.Name)
        self.tmp.cleanup()

    def box(self, name, x=0.0, size=10.0):
        b = self.doc.addObject("Part::Box", name)
        b.Length = b.Width = b.Height = size
        b.Placement.Base = App.Vector(x, 0, 0)
        self.doc.recompute()
        return b

    def ids(self):
        return dict(self.study.VolumeIds), dict(self.study.SurfaceIds)

    # --- IDs ---------------------------------------------------------------

    def test_ids_follow_tree_order_and_stay_after_adding_a_body(self):
        a, b, c = self.box("A"), self.box("B", 10), self.box("C", 20)
        objects.make_material(self.study, "Copper", [b, a])
        objects.make_material(self.study, "Iron", [c])
        objects.update_ids(self.study)
        self.assertEqual(self.ids()[0], {"B": "1", "A": "2", "C": "3"})
        d = self.box("D", 30)
        objects.make_material(self.study, "Air", [d])
        objects.update_ids(self.study)
        self.assertEqual(self.ids()[0], {"B": "1", "A": "2", "C": "3", "D": "4"})

    def test_surface_ids_one_per_excitation_and_body(self):
        a, b = self.box("A"), self.box("B", 10)
        objects.make_material(self.study, "Copper", [a, b])
        objects.make_excitation(self.study, "Terminal", [(a, "Face1"), (a, "Face2"), (b, "Face1")])
        objects.update_ids(self.study)
        self.assertEqual(self.ids()[1], {"Excitation|A": "1001", "Excitation|B": "1002"})

    def test_rename_keeps_id_and_changes_name(self):
        a = self.box("A")
        mat = objects.make_material(self.study, "Copper", [a])
        objects.update_ids(self.study)
        a.Label = "Coil"
        mat.Label = "Iron"
        objects.update_ids(self.study)
        self.assertEqual(objects.id_rows(self.study), [("VolumeIds", "A", "Iron_Coil", 1)])

    def test_deleted_body_id_is_not_reused(self):
        a, b = self.box("A"), self.box("B", 10)
        objects.make_material(self.study, "Copper", [a, b])
        objects.update_ids(self.study)
        self.doc.removeObject("B")
        c = self.box("C", 20)
        objects.materials(self.study)[0].References += [c]
        objects.update_ids(self.study)
        self.assertEqual(self.ids()[0], {"A": "1", "C": "3"})

    def test_set_id_refuses_duplicates_and_raises_counter(self):
        a, b = self.box("A"), self.box("B", 10)
        objects.make_material(self.study, "Copper", [a, b])
        objects.make_excitation(self.study, "T", [(a, "Face1")])
        objects.update_ids(self.study)
        with self.assertRaises(ValueError):
            objects.set_id(self.study, "VolumeIds", "A", 2)
        with self.assertRaises(ValueError):
            objects.set_id(self.study, "VolumeIds", "A", 1001)
        objects.set_id(self.study, "VolumeIds", "A", 50)
        self.assertEqual(self.study.NextVolumeId, 51)
        c = self.box("C", 20)
        objects.materials(self.study)[0].References += [c]
        objects.update_ids(self.study)
        self.assertEqual(self.study.VolumeIds["C"], "51")

    def test_new_volume_ids_skip_numbers_used_by_surfaces(self):
        a, b = self.box("A"), self.box("B", 10)
        objects.make_material(self.study, "Copper", [a])
        objects.make_excitation(self.study, "T", [(a, "Face1")])
        objects.update_ids(self.study)
        objects.set_id(self.study, "SurfaceIds", "Excitation|A", 2)
        objects.materials(self.study)[0].References += [b]
        objects.update_ids(self.study)
        self.assertEqual(self.study.VolumeIds["B"], "3")

    # --- tree objects ------------------------------------------------------

    def test_pad_face_resolves_to_body(self):
        body = self.doc.addObject("PartDesign::Body", "Body")
        cube = body.newObject("PartDesign::AdditiveBox", "Cube")
        self.doc.recompute()
        self.assertEqual(objects.owning_body(cube).Name, "Body")
        self.assertEqual(objects.owning_body(body).Name, "Body")

    def test_study_survives_save_and_reload(self):
        a = self.box("A")
        objects.make_material(self.study, "Copper", [a])
        objects.update_ids(self.study)
        path = os.path.join(self.tmp.name, "t.FCStd")
        self.doc.saveAs(path)
        App.closeDocument(self.doc.Name)
        self.doc = App.openDocument(path)
        study = objects.find_study(self.doc)
        self.assertIsNotNone(study)
        self.assertIsInstance(objects.materials(study)[0].Proxy, objects.Material)
        self.assertEqual(study.VolumeIds, {"A": "1"})


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `& $py -m unittest tests.test_study -v`
Expected: `ModuleNotFoundError: No module named 'emsolution'` (or `... has no attribute 'objects'`).

- [ ] **Step 3: Write `emsolution/__init__.py` and `emsolution/objects.py`**

`emsolution/__init__.py`:

```python
import os

ICONS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "icons")


def icon(name):
    return os.path.join(ICONS, name + ".svg")
```

`emsolution/objects.py`:

```python
"""Study tree objects and the ID table. No GUI code here."""
import re

GROUPS = (("MaterialsGroup", "Materials"),
          ("ExcitationsGroup", "Excitations"),
          ("MeshSizesGroup", "Mesh Sizes"))


def clean(text):
    return re.sub(r"[^A-Za-z0-9_-]", "_", text)


def item_name(item, body):
    return f"{clean(item.Label)}_{clean(body.Label)}"


class _Proxy:
    def dumps(self):
        return None

    def loads(self, state):
        return None


class Study(_Proxy):
    def __init__(self, obj):
        obj.Proxy = self
        obj.addProperty("App::PropertyPath", "OutputFolder", "EMSolution",
                        "Empty = folder <document>_mesh next to the .FCStd")
        obj.addProperty("App::PropertyLength", "DefaultMeshSize", "EMSolution",
                        "Mesh size for bodies without a Mesh Size item")
        obj.DefaultMeshSize = 5.0
        obj.addProperty("App::PropertyEnumeration", "MshVersion", "EMSolution",
                        "Gmsh file format version (ASCII)")
        obj.MshVersion = ["4.1", "2.2"]
        obj.addProperty("App::PropertyMap", "VolumeIds", "IDs", "Body Name -> volume ID")
        obj.addProperty("App::PropertyMap", "SurfaceIds", "IDs",
                        "'Excitation Name|Body Name' -> surface ID")
        obj.addProperty("App::PropertyInteger", "NextVolumeId", "IDs", "Next volume ID")
        obj.NextVolumeId = 1
        obj.addProperty("App::PropertyInteger", "NextSurfaceId", "IDs", "Next surface ID")
        obj.NextSurfaceId = 1001
        for prop, _ in GROUPS:
            obj.addProperty("App::PropertyLink", prop, "EMSolution", "")
        obj.addProperty("App::PropertyLink", "MeshResult", "EMSolution", "")
        for prop in ("VolumeIds", "SurfaceIds", "NextVolumeId", "NextSurfaceId"):
            obj.setEditorMode(prop, 1)  # read-only: edit through the ID table
        for prop in [g for g, _ in GROUPS] + ["MeshResult"]:
            obj.setEditorMode(prop, 2)  # hidden


class Material(_Proxy):
    def __init__(self, obj):
        obj.Proxy = self
        obj.addProperty("App::PropertyLinkList", "References", "EMSolution",
                        "Bodies made of this material")


class Excitation(_Proxy):
    def __init__(self, obj):
        obj.Proxy = self
        obj.addProperty("App::PropertyLinkSubList", "References", "EMSolution",
                        "Body faces of this excitation")


class MeshSize(_Proxy):
    def __init__(self, obj):
        obj.Proxy = self
        obj.addProperty("App::PropertyLength", "Size", "EMSolution", "Element size")
        obj.addProperty("App::PropertyLinkList", "References", "EMSolution",
                        "Bodies meshed with this size")


def make_study(doc):
    study = doc.addObject("App::DocumentObjectGroupPython", "Study")
    Study(study)
    for prop, label in GROUPS:
        group = doc.addObject("App::DocumentObjectGroup", prop.replace("Group", ""))
        group.Label = label
        study.addObject(group)
        setattr(study, prop, group)
    return study


def find_study(doc):
    return next((o for o in doc.Objects if isinstance(getattr(o, "Proxy", None), Study)), None)


def _add(study, group_prop, proxy_cls, label):
    obj = study.Document.addObject("App::FeaturePython", proxy_cls.__name__)
    proxy_cls(obj)
    obj.Label = label
    getattr(study, group_prop).addObject(obj)
    return obj


def make_material(study, label, bodies):
    obj = _add(study, "MaterialsGroup", Material, label)
    obj.References = bodies
    return obj


def make_excitation(study, label, faces):
    """faces: list of (body, "FaceN")."""
    obj = _add(study, "ExcitationsGroup", Excitation, label)
    obj.References = faces
    return obj


def make_mesh_size(study, size, bodies):
    obj = _add(study, "MeshSizesGroup", MeshSize, "MeshSize")
    obj.Size = size
    obj.References = bodies
    return obj


def materials(study):
    return list(study.MaterialsGroup.Group)


def excitations(study):
    return list(study.ExcitationsGroup.Group)


def mesh_sizes(study):
    return list(study.MeshSizesGroup.Group)


def owning_body(obj):
    """A face picked in the 3D view resolves to a PartDesign feature; use its Body."""
    parent = obj.getParentGeoFeatureGroup()
    if parent is not None and parent.isDerivedFrom("PartDesign::Body"):
        return parent
    return obj


def faces_by_body(excitation):
    """[(body, [face names])] in reference order, one entry per body."""
    out = {}
    for body, subs in excitation.References:
        out.setdefault(body.Name, (body, []))[1].extend(subs)
    return list(out.values())


def volume_keys(study):
    return list(dict.fromkeys(b.Name for m in materials(study) for b in m.References))


def surface_keys(study):
    return list(dict.fromkeys(f"{e.Name}|{b.Name}"
                              for e in excitations(study) for b, _ in faces_by_body(e)))


def update_ids(study):
    """Give every body and (excitation, body) pair an ID; drop entries that are gone.

    Counters only grow, so a dropped ID is never handed out again.
    """
    vkeys, skeys = volume_keys(study), surface_keys(study)
    vol = {k: v for k, v in study.VolumeIds.items() if k in vkeys}
    surf = {k: v for k, v in study.SurfaceIds.items() if k in skeys}
    used = {int(v) for v in list(vol.values()) + list(surf.values())}

    def give(table, keys, counter):
        for key in keys:
            if key not in table:
                while counter in used:
                    counter += 1
                table[key] = str(counter)
                used.add(counter)
                counter += 1
        return counter

    study.NextVolumeId = give(vol, vkeys, study.NextVolumeId)
    study.NextSurfaceId = give(surf, skeys, study.NextSurfaceId)
    study.VolumeIds, study.SurfaceIds = vol, surf


def set_id(study, table, key, new_id):
    """table: "VolumeIds" or "SurfaceIds". Raises ValueError for a bad or duplicate ID."""
    ids = dict(getattr(study, table))
    if key not in ids:
        raise ValueError(f"unknown entry {key}")
    if new_id < 1:
        raise ValueError("IDs must be 1 or more")
    taken = {int(v) for t in ("VolumeIds", "SurfaceIds")
             for k, v in getattr(study, t).items() if (t, k) != (table, key)}
    if new_id in taken:
        raise ValueError(f"ID {new_id} is already used")
    ids[key] = str(new_id)
    setattr(study, table, ids)
    counter = "NextVolumeId" if table == "VolumeIds" else "NextSurfaceId"
    top = max(int(v) for v in ids.values())
    setattr(study, counter, max(getattr(study, counter), top + 1))


def id_rows(study):
    """Rows for the ID table dialog: (table, key, name, id), volumes first."""
    rows = []
    for m in materials(study):
        for b in m.References:
            if b.Name in study.VolumeIds:
                rows.append(("VolumeIds", b.Name, item_name(m, b), int(study.VolumeIds[b.Name])))
    for e in excitations(study):
        for b, _ in faces_by_body(e):
            key = f"{e.Name}|{b.Name}"
            if key in study.SurfaceIds:
                rows.append(("SurfaceIds", key, item_name(e, b), int(study.SurfaceIds[key])))
    return rows
```

- [ ] **Step 4: Run the tests to see them pass**

Run: `& $py -m unittest tests.test_study -v`
Expected: `Ran 8 tests ... OK`.

- [ ] **Step 5: Commit**

```
git add emsolution/__init__.py emsolution/objects.py tests/test_study.py
git commit -m "Add study tree objects and fixed volume/surface ID table"
```

---

### Task 3: Checks and job writer

**Files:**
- Create: `emsolution/jobwriter.py`
- Modify: `tests/test_study.py` (imports, one helper, 13 new tests)

**Interfaces:**
- Consumes: everything from `emsolution.objects` (Task 2); the job format and `mesher.py` command (Task 1).
- Produces (`emsolution.jobwriter`):
  - `StudyError(Exception)`: its message is shown to the user as is.
  - `check(study) -> (volumes, surfaces)`: `volumes = [(body, material, size_mm)]`, `surfaces = [(excitation, body, [face names])]`.
  - `write_job(study) -> str` (path of `job.json`); runs `check`, then `update_ids`, then writes the BREP files.

- [ ] **Step 1: Write the failing tests**

In `tests/test_study.py`, replace the import block (from `import os` through `from emsolution import objects  # noqa: E402`) with:

```python
import json
import os
import subprocess
import sys
import tempfile
import unittest

_BIN = os.path.dirname(sys.executable)
sys.path[:0] = [_BIN, os.path.join(_BIN, "..", "lib")]

import FreeCAD as App  # noqa: E402
import Part  # noqa: E402

from emsolution import jobwriter, objects  # noqa: E402

MESHER = os.path.join(os.path.dirname(__file__), "..", "emsolution", "mesher.py")
```

Add this method to `StudyTest` after `ids()`:

```python
    def assertStudyError(self, text):
        with self.assertRaises(jobwriter.StudyError) as ctx:
            jobwriter.check(self.study)
        self.assertIn(text, str(ctx.exception))
```

Add these tests to `StudyTest`, after `test_study_survives_save_and_reload`:

```python
    # --- checks ------------------------------------------------------------

    def test_check_no_materials(self):
        self.assertStudyError("no materials")

    def test_check_two_materials(self):
        a = self.box("A")
        objects.make_material(self.study, "Copper", [a])
        objects.make_material(self.study, "Iron", [a])
        self.assertStudyError("more than one material")

    def test_check_not_one_solid(self):
        two = self.doc.addObject("Part::Feature", "Two")
        two.Shape = Part.makeCompound([Part.makeBox(1, 1, 1),
                                       Part.makeBox(1, 1, 1, App.Vector(5, 0, 0))])
        objects.make_material(self.study, "Copper", [two])
        self.assertStudyError("exactly one solid")

    def test_check_excitation_on_body_without_material(self):
        a, b = self.box("A"), self.box("B", 10)
        objects.make_material(self.study, "Copper", [a])
        objects.make_excitation(self.study, "T", [(b, "Face1")])
        self.assertStudyError("which has no material")

    def test_check_mesh_size_on_body_without_material(self):
        a, b = self.box("A"), self.box("B", 10)
        objects.make_material(self.study, "Copper", [a])
        objects.make_mesh_size(self.study, 1.0, [b])
        self.assertStudyError("mesh size but no material")

    def test_check_zero_size(self):
        a = self.box("A")
        objects.make_material(self.study, "Copper", [a])
        objects.make_mesh_size(self.study, 0.0, [a])
        self.assertStudyError("greater than 0")

    def test_check_missing_face(self):
        a = self.box("A")
        objects.make_material(self.study, "Copper", [a])
        objects.make_excitation(self.study, "T", [(a, "Face60")])  # a box has 6 faces
        self.assertStudyError("has no Face60")

    def test_check_unsaved_document(self):
        a = self.box("A")
        objects.make_material(self.study, "Copper", [a])
        self.study.OutputFolder = ""
        with self.assertRaises(jobwriter.StudyError) as ctx:
            jobwriter.write_job(self.study)
        self.assertIn("Save the document", str(ctx.exception))

    def test_smallest_mesh_size_wins(self):
        a = self.box("A")
        objects.make_material(self.study, "Copper", [a])
        objects.make_mesh_size(self.study, 3.0, [a])
        objects.make_mesh_size(self.study, 2.0, [a])
        volumes, _ = jobwriter.check(self.study)
        self.assertEqual(volumes[0][2], 2.0)

    def test_names_equal_after_cleanup_are_refused(self):
        a = self.box("A")
        b = self.box("B", 10)
        b.Label = "A!"   # cleans to "A_"
        a.Label = "A?"   # cleans to "A_" too
        objects.make_material(self.study, "Cu", [a, b])
        self.assertStudyError("Cu_A_")

    # --- geometry and job file ----------------------------------------------

    def test_body_in_app_part_is_exported_in_global_coordinates(self):
        part = self.doc.addObject("App::Part", "Part")
        part.Placement.Base = App.Vector(100, 0, 0)
        a = self.box("A")
        a.Placement.Base = App.Vector(0, 50, 0)
        part.addObject(a)
        self.doc.recompute()
        objects.make_material(self.study, "Copper", [a])
        objects.make_excitation(self.study, "T", [(a, "Face6")])  # top face, z = 10
        jobwriter.write_job(self.study)
        vol = Part.Shape()
        vol.read(os.path.join(self.tmp.name, "geometry", "vol_1.brep"))
        self.assertEqual((vol.BoundBox.XMin, vol.BoundBox.YMin), (100, 50))
        face = Part.Shape()
        face.read(os.path.join(self.tmp.name, "geometry", "surf_1001_1.brep"))
        self.assertAlmostEqual(face.BoundBox.XMin, 100)
        self.assertAlmostEqual(face.BoundBox.ZMin, 10)

    def test_job_json_contents(self):
        a, b = self.box("A"), self.box("B", 10)
        objects.make_material(self.study, "Copper", [a])
        objects.make_material(self.study, "Air", [b])
        objects.make_excitation(self.study, "Terminal In", [(a, "Face1"), (a, "Face2")])
        objects.make_mesh_size(self.study, 2.0, [a])
        self.study.Label = "My Study"
        path = jobwriter.write_job(self.study)
        with open(path, encoding="utf-8") as fh:
            job = json.load(fh)
        self.assertEqual(job, {
            "model_name": "My_Study", "msh_version": 4.1,
            "volumes": [
                {"id": 1, "name": "Copper_A", "file": "geometry/vol_1.brep", "size": 2.0},
                {"id": 2, "name": "Air_B", "file": "geometry/vol_2.brep", "size": 5.0}],
            "surfaces": [
                {"id": 1001, "name": "Terminal_In_A", "volume_id": 1,
                 "files": ["geometry/surf_1001_1.brep", "geometry/surf_1001_2.brep"]}]})
        for rel in ("vol_1.brep", "vol_2.brep", "surf_1001_1.brep", "surf_1001_2.brep"):
            self.assertTrue(os.path.exists(os.path.join(self.tmp.name, "geometry", rel)))

    def test_written_job_meshes(self):
        a, b = self.box("A"), self.box("B", 10)
        objects.make_material(self.study, "Copper", [a])
        objects.make_material(self.study, "Air", [b])
        objects.make_excitation(self.study, "T", [(a, "Face1")])  # x = 0 face
        self.study.DefaultMeshSize = 4.0
        path = jobwriter.write_job(self.study)
        r = subprocess.run([sys.executable, MESHER, path], capture_output=True, encoding="utf-8", errors="replace")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.path.exists(os.path.join(self.tmp.name, "Study.msh")))
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `& $py -m unittest tests.test_study -v`
Expected: `ImportError: cannot import name 'jobwriter' from 'emsolution'`.

- [ ] **Step 3: Write `emsolution/jobwriter.py`**

Notes for the implementer: `global_shape` is the same method FreeCAD FEM uses (`femmesh/gmshtools.py`); it includes `App::Part` placement. A PartDesign face keeps its `FaceN` name on the Body, so faces are read from the body's shape.

```python
"""Study -> checks -> job.json + BREP files for mesher.py."""
import json
import os

import FreeCAD as App

from . import objects


class StudyError(Exception):
    pass


def global_shape(obj):
    """Shape in global coordinates, including App::Part placement (same as FEM's gmshtools)."""
    shape = obj.getPropertyOfGeometry().transformed(App.Placement().Matrix)
    shape.Placement = obj.getGlobalPlacement()
    return shape


def output_folder(study):
    if study.OutputFolder:
        return study.OutputFolder
    if not study.Document.FileName:
        raise StudyError("Save the document first, or set the study's OutputFolder.")
    return os.path.splitext(study.Document.FileName)[0] + "_mesh"


def check(study):
    """Checks before meshing. Returns (volumes, surfaces):
    volumes  = [(body, material, size_mm)] in tree order
    surfaces = [(excitation, body, [face names])] in tree order
    """
    mats = objects.materials(study)
    if not mats:
        raise StudyError("The study has no materials.")
    material_of = {}
    for m in mats:
        for b in m.References:
            material_of.setdefault(b.Name, (b, []))[1].append(m)
    surfaces = [(e, b, faces) for e in objects.excitations(study)
                for b, faces in objects.faces_by_body(e)]
    for e, b, _ in surfaces:
        if b.Name not in material_of:
            raise StudyError(f"Excitation {e.Label} is on body {b.Label}, which has no material.")
    for s in objects.mesh_sizes(study):
        for b in s.References:
            if b.Name not in material_of:
                raise StudyError(f"Body {b.Label} has a mesh size but no material.")
    for b, ms in material_of.values():
        if len(ms) > 1:
            raise StudyError(f"Body {b.Label} has more than one material: "
                             + ", ".join(m.Label for m in ms))
        if len(b.Shape.Solids) != 1:
            raise StudyError(f"Body {b.Label} must be exactly one solid "
                             f"(it has {len(b.Shape.Solids)}).")
    for e, b, faces in surfaces:
        for face in faces:
            try:
                b.Shape.getElement(face)
            except Exception:
                raise StudyError(f"Excitation {e.Label}: body {b.Label} has no {face}. "
                                 "Reselect the faces.") from None
    if study.DefaultMeshSize.Value <= 0:
        raise StudyError("The default mesh size must be greater than 0.")
    size = {}
    for s in objects.mesh_sizes(study):
        if s.Size.Value <= 0:
            raise StudyError(f"Mesh size {s.Label} must be greater than 0.")
        for b in s.References:
            size[b.Name] = min(size.get(b.Name, s.Size.Value), s.Size.Value)
    volumes = [(b, ms[0], size.get(b.Name, study.DefaultMeshSize.Value))
               for b, ms in material_of.values()]
    names = [objects.item_name(m, b) for b, m, _ in volumes]
    names += [objects.item_name(e, b) for e, b, _ in surfaces]
    dups = sorted({n for n in names if names.count(n) > 1})
    if dups:
        raise StudyError("These group names are the same after removing special characters: "
                         + ", ".join(dups) + ". Rename the items or bodies.")
    return volumes, surfaces


def write_job(study):
    """Run the checks, update the ID table, write job.json and BREPs. Returns the job path."""
    volumes, surfaces = check(study)
    folder = output_folder(study)
    objects.update_ids(study)
    os.makedirs(os.path.join(folder, "geometry"), exist_ok=True)
    job = {"model_name": objects.clean(study.Label), "msh_version": float(study.MshVersion),
           "volumes": [], "surfaces": []}
    for body, mat, size in volumes:
        vid = int(study.VolumeIds[body.Name])
        rel = f"geometry/vol_{vid}.brep"
        global_shape(body).exportBrep(os.path.join(folder, rel))
        job["volumes"].append({"id": vid, "name": objects.item_name(mat, body),
                               "file": rel, "size": size})
    for exc, body, faces in surfaces:
        sid = int(study.SurfaceIds[f"{exc.Name}|{body.Name}"])
        shape = global_shape(body)
        files = []
        for n, face in enumerate(faces, 1):
            rel = f"geometry/surf_{sid}_{n}.brep"
            shape.getElement(face).exportBrep(os.path.join(folder, rel))
            files.append(rel)
        job["surfaces"].append({"id": sid, "name": objects.item_name(exc, body),
                                "volume_id": int(study.VolumeIds[body.Name]), "files": files})
    path = os.path.join(folder, "job.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(job, fh, indent=2)
    return path
```

- [ ] **Step 4: Run all tests to see them pass**

Run: `& $py -m unittest discover -s tests -t . -v`
Expected: `Ran 31 tests ... OK`.

- [ ] **Step 5: Commit**

```
git add emsolution/jobwriter.py tests/test_study.py
git commit -m "Add pre-mesh checks and job writer with global-coordinate BREP export"
```

---

### Task 4: Workbench, dialogs and background run

**Files:**
- Create: `package.xml`, `InitGui.py`
- Create: `icons/emsolution.svg`, `icons/study.svg`, `icons/material.svg`, `icons/excitation.svg`, `icons/meshsize.svg`, `icons/runmesh.svg`
- Create: `emsolution/taskpanels.py`, `emsolution/runner.py`, `emsolution/commands.py`
- Test: `tests/gui_smoke.py` (runs inside FreeCAD)

**Interfaces:**
- Consumes: `emsolution.icon`, `emsolution.objects` (Task 2), `emsolution.jobwriter.write_job` / `StudyError` (Task 3), `emsolution/mesher.py` (Task 1).
- Produces:
  - Workbench `EMSolutionWorkbench` and commands `EMS_NewStudy`, `EMS_Material`, `EMS_Excitation`, `EMS_MeshSize`, `EMS_RunMesh`.
  - `commands.ask_text(title, label, default)` and `commands.ask_size(default)` are module-level functions so the smoke test can replace them.
  - `taskpanels.ItemPanel(obj)` (attributes `name`, `size`, `refs`, `current`; methods `add_selection`, `remove`, `accept`, `reject`), `taskpanels.IdTableDialog(study)` (attributes `rows`, `table`).
  - `runner.start(study) -> MeshRun | None`, `runner.busy() -> bool`; `MeshRun.proc` (QProcess), `MeshRun.error` (str).

Two FreeCAD facts the implementer needs:
- FreeCAD 1.1 runs `InitGui.py` with `exec()` inside a function, so the class body and methods cannot see names imported at the top of the file. Import inside methods and set `Icon` after the class.
- `FREECAD_USER_HOME=<dir>` makes FreeCAD use `<dir>\Mod` as its addon folder, so the smoke test can run in a throwaway profile.

- [ ] **Step 1: Write the failing smoke test**

`tests/gui_smoke.py`:

```python
r"""GUI smoke test: runs inside FreeCAD, drives the commands, runs a mesh, then quits.

Needs the addon linked into a throwaway FreeCAD profile (PowerShell, repo root):
    $h = "$env:TEMP\ems_fc_home"; New-Item -ItemType Directory -Force "$h\Mod" | Out-Null
    if (-not (Test-Path "$h\Mod\EMSolution")) { New-Item -ItemType Junction -Path "$h\Mod\EMSolution" -Target (Get-Location).Path | Out-Null }
    $env:FREECAD_USER_HOME = $h
    Start-Process -Wait "$env:LOCALAPPDATA\Programs\FreeCAD 1.1\bin\FreeCAD.exe" tests\gui_smoke.py
    Get-Content "$env:TEMP\ems_gui_smoke.txt"
The last line of the result file is "PASS" or "FAIL".
"""
import os
import tempfile
import traceback

RESULT = os.path.join(tempfile.gettempdir(), "ems_gui_smoke.txt")
log = []


def main():
    import FreeCAD as App
    import FreeCADGui as Gui

    Gui.activateWorkbench("EMSolutionWorkbench")  # loaded by FreeCAD from the Mod folder
    from emsolution import commands, objects, runner, taskpanels

    commands.ask_text = lambda title, label, default: {"Material": "Copper",
                                                       "Excitation": "Terminal In"}[title]
    commands.ask_size = lambda default: 3.0

    doc = App.newDocument("Smoke")
    for name, x in (("A", 0), ("B", 10)):
        box = doc.addObject("Part::Box", name)
        box.Placement.Base = App.Vector(x, 0, 0)
    doc.recompute()

    Gui.runCommand("EMS_NewStudy")
    study = objects.find_study(doc)
    assert study is not None, "no study"
    study.OutputFolder = tempfile.mkdtemp()
    log.append("study ok")

    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(doc.Name, "A")
    Gui.Selection.addSelection(doc.Name, "B")
    Gui.runCommand("EMS_Material")
    Gui.runCommand("EMS_MeshSize")
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(doc.Name, "A", "Face1")
    Gui.runCommand("EMS_Excitation")
    mat, = objects.materials(study)
    exc, = objects.excitations(study)
    size, = objects.mesh_sizes(study)
    assert [b.Name for b in mat.References] == ["A", "B"], mat.References
    assert exc.References == [(doc.A, ("Face1",))], exc.References
    assert size.Size.Value == 3.0
    log.append("commands ok")

    panel = taskpanels.ItemPanel(mat)
    panel.name.setText("Iron")
    panel.refs.item(1).setSelected(True)
    panel.remove()
    Gui.Control.showDialog(panel)
    panel.accept()
    assert mat.Label == "Iron" and [b.Name for b in mat.References] == ["A"]
    mat.References = [doc.A, doc.B]
    log.append("panel ok")

    dialog = taskpanels.IdTableDialog(study)
    assert [r[2] for r in dialog.rows] == ["Iron_A", "Iron_B", "Terminal_In_A"], dialog.rows
    dialog.table.item(0, 2).setText("7")
    assert study.VolumeIds["A"] == "7"
    log.append("id table ok")

    run = runner.start(study)
    assert run is not None, "start failed"
    assert run.proc.waitForFinished(120000), "mesher timed out"
    App.Gui.updateGui()
    assert not runner.busy(), "run did not finish"
    assert run.error == "", run.error
    assert study.MeshResult is not None and study.MeshResult.FemMesh.VolumeCount > 0
    log.append(f"mesh ok: {study.MeshResult.FemMesh.VolumeCount} volumes")
    App.closeDocument(doc.Name)


try:
    main()
    log.append("PASS")
except Exception:
    log.append(traceback.format_exc())
    log.append("FAIL")
with open(RESULT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(log) + "\n")
os._exit(0)
```

- [ ] **Step 2: Run the smoke test to see it fail**

Run the five PowerShell lines from the test's docstring, from the repo root.
Expected: the result file ends with `FAIL`, after a traceback saying the workbench `EMSolutionWorkbench` does not exist.

- [ ] **Step 3: Write the addon shell (`package.xml`, `InitGui.py`, icons)**

`package.xml`:

```xml
<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<package format="1" xmlns="https://wiki.freecad.org/Package_Metadata">
  <name>EMSolution</name>
  <description>Prepare 3D Gmsh meshes for the EMSolution electromagnetic solver.</description>
  <version>0.1.0</version>
  <date>2026-09-30</date>
  <maintainer email="eskandari.hmd@gmail.com">eskandarih</maintainer>
  <license>Proprietary</license>
  <freecadmin>1.1.0</freecadmin>
  <content>
    <workbench>
      <classname>EMSolutionWorkbench</classname>
      <subdirectory>./</subdirectory>
      <icon>icons/emsolution.svg</icon>
    </workbench>
  </content>
</package>
```

`InitGui.py`:

```python
import FreeCADGui as Gui

import emsolution  # the Mod folder is on sys.path


class EMSolutionWorkbench(Gui.Workbench):
    # FreeCAD exec()s this file inside a function, so the class body and methods
    # cannot see names imported above. Import inside methods; set Icon below.
    MenuText = "EMSolution"
    ToolTip = "Prepare 3D meshes for EMSolution"

    def Initialize(self):
        from emsolution import commands

        self.appendToolbar("EMSolution", commands.NAMES)
        self.appendMenu("EMSolution", commands.NAMES)

    def GetClassName(self):
        return "Gui::PythonWorkbench"


EMSolutionWorkbench.Icon = emsolution.icon("emsolution")
Gui.addWorkbench(EMSolutionWorkbench())
```

`icons/emsolution.svg`:

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64"><rect x="4" y="4" width="56" height="56" rx="8" fill="#1f5fa8"/><text x="32" y="44" font-family="sans-serif" font-size="30" font-weight="bold" fill="#fff" text-anchor="middle">EM</text></svg>
```

`icons/study.svg`:

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64"><rect x="6" y="10" width="52" height="44" rx="4" fill="#1f5fa8"/><path d="M14 22h36M14 32h36M14 42h24" stroke="#fff" stroke-width="4"/></svg>
```

`icons/material.svg`:

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64"><path d="M32 6 56 20v24L32 58 8 44V20z" fill="#c8702a" stroke="#6b3a12" stroke-width="3"/></svg>
```

`icons/excitation.svg`:

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64"><rect x="8" y="20" width="48" height="24" fill="#999"/><path d="M36 4 20 34h12l-6 26 20-34H34z" fill="#e8c21a" stroke="#6b5a00" stroke-width="2"/></svg>
```

`icons/meshsize.svg`:

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64"><path d="M6 58 32 6l26 52z M19 32h26 M32 6v52 M19 32l13 26 13-26" fill="none" stroke="#2a8c3c" stroke-width="3"/></svg>
```

`icons/runmesh.svg`:

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64"><path d="M6 58 32 6l26 52z M19 32h26 M32 58 19 32M32 58l13-26" fill="none" stroke="#2a8c3c" stroke-width="3"/><path d="M40 36v24l20-12z" fill="#1f5fa8"/></svg>
```

- [ ] **Step 4: Write `emsolution/taskpanels.py`**

```python
"""View providers, the item edit panel, the ID table dialog and selection helpers."""
import FreeCADGui as Gui
from PySide import QtCore, QtWidgets

from . import icon, objects


def selected_bodies():
    out = {}
    for sel in Gui.Selection.getSelectionEx():
        body = objects.owning_body(sel.Object)
        out.setdefault(body.Name, body)
    return list(out.values())


def selected_faces():
    out = []
    for sel in Gui.Selection.getSelectionEx():
        body = objects.owning_body(sel.Object)
        out += [(body, s) for s in sel.SubElementNames if s.startswith("Face")]
    return out


class _ViewProvider:
    def __init__(self, vobj):
        vobj.Proxy = self

    def attach(self, vobj):
        self.Object = vobj.Object

    def dumps(self):
        return None

    def loads(self, state):
        return None


class ViewProviderStudy(_ViewProvider):
    def getIcon(self):
        return icon("study")

    def doubleClicked(self, vobj):
        IdTableDialog(vobj.Object).exec()
        return True


class ViewProviderItem(_ViewProvider):
    def getIcon(self):
        obj = getattr(self, "Object", None)
        return icon(type(obj.Proxy).__name__.lower()) if obj else icon("emsolution")

    def doubleClicked(self, vobj):
        Gui.Control.showDialog(ItemPanel(vobj.Object))
        return True


class ItemPanel:
    """Edit name, size (Mesh Size only) and references of a tree item."""

    def __init__(self, obj):
        self.obj = obj
        self.faces = isinstance(obj.Proxy, objects.Excitation)
        if self.faces:
            self.current = [(b, f) for b, subs in obj.References for f in subs]
        else:
            self.current = [(b, None) for b in obj.References]
        self.form = QtWidgets.QWidget()
        self.form.setWindowTitle(obj.Label)
        layout = QtWidgets.QFormLayout(self.form)
        self.name = QtWidgets.QLineEdit(obj.Label)
        layout.addRow("Name", self.name)
        self.size = None
        if isinstance(obj.Proxy, objects.MeshSize):
            self.size = QtWidgets.QDoubleSpinBox()
            self.size.setDecimals(3)
            self.size.setRange(0.001, 1e6)
            self.size.setSuffix(" mm")
            self.size.setValue(obj.Size.Value)
            layout.addRow("Size", self.size)
        self.refs = QtWidgets.QListWidget()
        self.refs.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        layout.addRow("Faces" if self.faces else "Bodies", self.refs)
        add = QtWidgets.QPushButton("Add selection")
        remove = QtWidgets.QPushButton("Remove")
        add.clicked.connect(self.add_selection)
        remove.clicked.connect(self.remove)
        buttons = QtWidgets.QHBoxLayout()
        buttons.addWidget(add)
        buttons.addWidget(remove)
        layout.addRow(buttons)
        self.refresh()

    def refresh(self):
        self.refs.clear()
        self.refs.addItems([f"{b.Label}.{f}" if f else b.Label for b, f in self.current])

    def add_selection(self):
        new = selected_faces() if self.faces else [(b, None) for b in selected_bodies()]
        have = {(b.Name, f) for b, f in self.current}
        self.current += [(b, f) for b, f in new if (b.Name, f) not in have]
        self.refresh()

    def remove(self):
        rows = {i.row() for i in self.refs.selectedIndexes()}
        self.current = [r for i, r in enumerate(self.current) if i not in rows]
        self.refresh()

    def accept(self):
        doc = self.obj.Document
        doc.openTransaction("Edit " + self.obj.Label)
        self.obj.Label = self.name.text().strip() or self.obj.Label
        if self.size is not None:
            self.obj.Size = self.size.value()
        if self.faces:
            self.obj.References = list(self.current)
        else:
            self.obj.References = [b for b, _ in self.current]
        doc.commitTransaction()
        doc.recompute()
        Gui.Control.closeDialog()
        return True

    def reject(self):
        Gui.Control.closeDialog()
        return True


class IdTableDialog(QtWidgets.QDialog):
    """Lists every group with its ID. The ID column is editable; duplicates are refused."""

    def __init__(self, study):
        super().__init__(Gui.getMainWindow())
        self.study = study
        self.setWindowTitle("EMSolution IDs")
        objects.update_ids(study)  # so bodies added since the last run show up
        self.rows = objects.id_rows(study)
        self.table = QtWidgets.QTableWidget(len(self.rows), 3)
        self.table.setHorizontalHeaderLabels(["Type", "Name", "ID"])
        for r, (table, _key, name, id_) in enumerate(self.rows):
            kind = "Volume" if table == "VolumeIds" else "Surface"
            for c, text in enumerate((kind, name, str(id_))):
                item = QtWidgets.QTableWidgetItem(text)
                if c < 2:
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
                self.table.setItem(r, c, item)
        self.table.resizeColumnsToContents()
        self.table.itemChanged.connect(self.changed)
        close = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Close)
        close.rejected.connect(self.reject)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.table)
        layout.addWidget(close)

    def changed(self, item):
        table, key, name, old = self.rows[item.row()]
        try:
            new = int(item.text())
            objects.set_id(self.study, table, key, new)
        except ValueError as exc:
            QtWidgets.QMessageBox.warning(self, "EMSolution IDs", str(exc))
            self.table.blockSignals(True)
            item.setText(str(old))
            self.table.blockSignals(False)
            return
        self.rows[item.row()] = (table, key, name, new)
```

- [ ] **Step 5: Write `emsolution/runner.py`**

Notes for the implementer: the progress dialog emits `canceled` when it is closed, so `_finished` disconnects it first; otherwise every successful run would count as cancelled. The mesher writes UTF-8, so its output is decoded as UTF-8 (the default of `bytes.decode`).

```python
"""Run mesher.py in a background process, stream its output, load the result."""
import json
import os

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtWidgets

from . import jobwriter

MESHER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mesher.py")
_run = None  # the active MeshRun; the reference also keeps it alive


def busy():
    return _run is not None


def python_exe():
    return os.path.join(App.getHomePath(), "bin", "python.exe")


def start(study):
    global _run
    try:
        job = jobwriter.write_job(study)
    except jobwriter.StudyError as exc:
        QtWidgets.QMessageBox.warning(Gui.getMainWindow(), "EMSolution", str(exc))
        return None
    _run = MeshRun(study, job)
    return _run


class MeshRun:
    def __init__(self, study, job):
        self.study, self.job = study, job
        self.cancelled = False
        self.error = ""
        self.dialog = QtWidgets.QProgressDialog("Meshing…", "Cancel", 0, 0, Gui.getMainWindow())
        self.dialog.setWindowTitle("EMSolution")
        self.dialog.setWindowModality(QtCore.Qt.WindowModal)
        self.dialog.canceled.connect(self.cancel)
        self.proc = QtCore.QProcess()
        self.proc.readyReadStandardOutput.connect(self._stdout)
        self.proc.readyReadStandardError.connect(self._stderr)
        self.proc.finished.connect(self._finished)
        self.proc.errorOccurred.connect(self._failed_to_start)
        self.proc.start(python_exe(), [MESHER, job])
        self.dialog.show()

    def _stdout(self):
        App.Console.PrintMessage(bytes(self.proc.readAllStandardOutput()).decode(errors="replace"))

    def _stderr(self):
        text = bytes(self.proc.readAllStandardError()).decode(errors="replace")
        App.Console.PrintWarning(text)
        for line in text.splitlines():
            if line.startswith("ERROR:"):
                self.error = line[len("ERROR:"):].strip()

    def cancel(self):
        self.cancelled = True
        self.proc.kill()

    def _failed_to_start(self, err):
        if err == QtCore.QProcess.FailedToStart:
            self.error = f"Could not start {python_exe()}"
            self._finished(-1, None)

    def _finished(self, code, _status):
        global _run
        _run = None
        self.dialog.canceled.disconnect(self.cancel)  # closing the dialog emits canceled
        self.dialog.close()
        parent = Gui.getMainWindow()
        if self.cancelled:
            QtWidgets.QMessageBox.information(parent, "EMSolution", "Meshing cancelled.")
        elif code != 0:
            QtWidgets.QMessageBox.critical(
                parent, "EMSolution", self.error or f"The mesher stopped with exit code {code}.")
        else:
            self.load_result()

    def load_result(self):
        import Fem
        import FemGui  # noqa: F401  registers the view provider for FEM meshes

        with open(self.job, encoding="utf-8") as fh:
            base = os.path.join(os.path.dirname(self.job), json.load(fh)["model_name"])
        doc = self.study.Document
        mesh_obj = self.study.MeshResult
        if mesh_obj is None:
            mesh_obj = doc.addObject("Fem::FemMeshObject", "MeshResult")
            self.study.addObject(mesh_obj)
            self.study.MeshResult = mesh_obj
        mesh_obj.FemMesh = Fem.read(base + ".unv")
        doc.recompute()
        App.Console.PrintMessage(f"EMSolution mesh written to {base}.msh\n")
```

- [ ] **Step 6: Write `emsolution/commands.py`**

```python
"""Toolbar and menu commands."""
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtWidgets

from . import icon, objects, runner, taskpanels


def ask_text(title, label, default):
    text, ok = QtWidgets.QInputDialog.getText(Gui.getMainWindow(), title, label, text=default)
    return text.strip() if ok and text.strip() else None


def ask_size(default):
    value, ok = QtWidgets.QInputDialog.getDouble(
        Gui.getMainWindow(), "Mesh Size", "Element size (mm):", default, 0.001, 1e6, 3)
    return value if ok else None


def warn(text):
    QtWidgets.QMessageBox.warning(Gui.getMainWindow(), "EMSolution", text)


def active_study():
    return objects.find_study(App.ActiveDocument) if App.ActiveDocument else None


def _create(study, title, make):
    doc = study.Document
    doc.openTransaction(title)
    obj = make()
    taskpanels.ViewProviderItem(obj.ViewObject)
    doc.commitTransaction()
    doc.recompute()
    return obj


class _StudyCommand:
    def IsActive(self):
        return active_study() is not None


class NewStudy:
    def GetResources(self):
        return {"Pixmap": icon("study"), "MenuText": "New Study",
                "ToolTip": "Create an EMSolution study in this document"}

    def IsActive(self):
        return App.ActiveDocument is not None and active_study() is None

    def Activated(self):
        doc = App.ActiveDocument
        doc.openTransaction("New Study")
        study = objects.make_study(doc)
        taskpanels.ViewProviderStudy(study.ViewObject)
        doc.commitTransaction()
        doc.recompute()


class AddMaterial(_StudyCommand):
    def GetResources(self):
        return {"Pixmap": icon("material"), "MenuText": "Material",
                "ToolTip": "Give the selected bodies a material"}

    def Activated(self):
        bodies = taskpanels.selected_bodies()
        if not bodies:
            return warn("Select one or more bodies first.")
        name = ask_text("Material", "Material name:", "Material")
        if name:
            _create(active_study(), "Add Material",
                    lambda: objects.make_material(active_study(), name, bodies))


class AddExcitation(_StudyCommand):
    def GetResources(self):
        return {"Pixmap": icon("excitation"), "MenuText": "Excitation",
                "ToolTip": "Make the selected faces an excitation surface"}

    def Activated(self):
        faces = taskpanels.selected_faces()
        if not faces:
            return warn("Select one or more faces first.")
        name = ask_text("Excitation", "Excitation name:", "Excitation")
        if name:
            _create(active_study(), "Add Excitation",
                    lambda: objects.make_excitation(active_study(), name, faces))


class AddMeshSize(_StudyCommand):
    def GetResources(self):
        return {"Pixmap": icon("meshsize"), "MenuText": "Mesh Size",
                "ToolTip": "Set the mesh size of the selected bodies"}

    def Activated(self):
        bodies = taskpanels.selected_bodies()
        if not bodies:
            return warn("Select one or more bodies first.")
        size = ask_size(active_study().DefaultMeshSize.Value)
        if size:
            _create(active_study(), "Add Mesh Size",
                    lambda: objects.make_mesh_size(active_study(), size, bodies))


class RunMesh(_StudyCommand):
    def GetResources(self):
        return {"Pixmap": icon("runmesh"), "MenuText": "Run Mesh",
                "ToolTip": "Write the .msh file with Gmsh"}

    def IsActive(self):
        return super().IsActive() and not runner.busy()

    def Activated(self):
        runner.start(active_study())


COMMANDS = {"EMS_NewStudy": NewStudy(), "EMS_Material": AddMaterial(),
            "EMS_Excitation": AddExcitation(), "EMS_MeshSize": AddMeshSize(),
            "EMS_RunMesh": RunMesh()}
for _name, _cmd in COMMANDS.items():
    Gui.addCommand(_name, _cmd)
NAMES = list(COMMANDS)
```

- [ ] **Step 7: Run the smoke test and the unit tests to see them pass**

Run the five PowerShell lines from `tests/gui_smoke.py`'s docstring again.
Expected result file:

```
study ok
commands ok
panel ok
id table ok
mesh ok: <number above 0> volumes
PASS
```

Run: `& $py -m unittest discover -s tests -t . -v`
Expected: `Ran 31 tests ... OK` (`gui_smoke.py` is not collected, because its name does not start with `test`).

- [ ] **Step 8: Install into the real FreeCAD profile**

```
New-Item -ItemType Junction -Path "$env:APPDATA\FreeCAD\v1-1\Mod\EMSolution" -Target C:\Users\eskandarih\EMSolution-FreeCAD
```

Start FreeCAD normally. Expected: **EMSolution** appears in the workbench list with the blue "EM" icon, and the Report view shows no errors for `Mod\EMSolution`.

- [ ] **Step 9: Manual checklist (spec section 11)**

In FreeCAD, with two touching Part boxes and one PartDesign Body:

1. Create a study: New Study; the tree shows Study → Materials, Excitations, Mesh Sizes. New Study is greyed out afterwards.
2. Add each item type: Material on two bodies, Excitation on a face of the PartDesign Body (it must list the Body, not the Pad), Mesh Size on one body.
3. Edit: double-click each item, add and remove references, change the Mesh Size value, press OK. Undo (Ctrl+Z) reverts it.
4. Rename a body and a material; double-click the Study; the names in the ID table change and the IDs stay the same.
5. Delete a body that has a material; Run Mesh still works and its ID is gone from the table.
6. Run the mesh: the "Meshing…" dialog appears, the Report view shows Gmsh output, and a Mesh Result appears under the Study.
7. Cancel a run: set the default mesh size very small (for example 0.2 mm), run, press Cancel; the message says "Meshing cancelled." and the document is unchanged apart from the IDs.
8. View the result: hide the bodies; the Mesh Result shows the tetrahedral mesh.
9. Edit the ID table: set an ID to a number already in use; a warning appears and the old value comes back. Set a free number; run again; open the `.msh` in Gmsh and check the physical group numbers and names.
10. Errors: give a body two materials, then Run Mesh; the message names the body.

- [ ] **Step 10: Commit**

```
git add package.xml InitGui.py icons emsolution/taskpanels.py emsolution/runner.py emsolution/commands.py tests/gui_smoke.py
git commit -m "Add EMSolution workbench: tree commands, edit dialogs, ID table and background meshing"
```
