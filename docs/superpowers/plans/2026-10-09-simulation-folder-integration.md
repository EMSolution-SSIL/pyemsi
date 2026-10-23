# Simulation Folder Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run Mesh writes `pre_geom.msh` (3D) or `pre_geom2D.msh` (2D) into the folder that holds the `.FCStd`, with Gmsh working files under `.pyemsi/freecad/<FCStd stem>/<Study Name>/`, and Studies lose their `OutputFolder` / `LegacyOutput` properties.

**Architecture:** `jobwriter` owns the path rules (`simulation_folder`, `scratch_folder`, `mesh_file`) and puts the absolute target path into `job.json` as `"mesh_file"`. `mesher.py` (a separate process with no FreeCAD imports) writes the mesh into the scratch folder, then moves it onto `job["mesh_file"]`, so only a finished mesh replaces the solver's file. `runner` reads `mesh.unv` from the scratch folder for display and reports which file it wrote.

**Tech Stack:** Python 3.11, FreeCAD 1.1.0 scripted objects, Gmsh Python API, PySide (Qt), unittest run through pytest, Pixi.

**Spec:** `docs/superpowers/specs/2026-10-09-simulation-folder-integration-design.md`

## Global Constraints

- Run everything through Pixi: `pixi run pytest ...`, `pixi run lint`, `pixi run ruff format <files>`. Never `pip install`.
- Line length 120, double quotes, LF. Keep a call or literal on one line if it fits in 120 columns; no trailing comma on a construct that fits on one line.
- Never sort or reorder imports. Add a new import on its own line next to related ones.
- Only format files you changed. Never run Black, isort or `ruff check --fix`.
- Never commit with `--no-verify`. The pre-commit hook runs `ruff format` and `ruff check` on staged files; if it reformats, review, `git add` again, commit.
- Every commit message ends with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Unsaved document error text, verbatim: `Save the document in the simulation folder first.`
- Mesh names, verbatim: `pre_geom.msh` (3D Study), `pre_geom2D.msh` (2D Study).
- Scratch folder, verbatim: `<simulation folder>/.pyemsi/freecad/<FCStd file stem>/<Study Name>/` holding `job.json`, `geometry/*.brep`, `mesh.unv`.
- `mesher.py` must never import FreeCAD.
- Work only inside the worktree `C:\Users\eskandarih\pyemsi\.claude\worktrees\freecad` (branch `feature/freecad-addon`).

## Review Focus

1. The user does Save As into another folder: the mesh target and the scratch folder follow the new `.FCStd` location (test in Task 2).
2. The simulation folder or `.FCStd` name has spaces and Persian letters: meshing still succeeds and `pre_geom.msh` lands beside the `.FCStd` (test in Task 2).
3. The Study is renamed (Label) after meshing: it keeps the same scratch folder, keyed by the internal Name (test in Task 2).
4. `pre_geom.msh` is read-only or locked by another program: the mesher exits with an `ERROR:` line and the old file is untouched (test in Task 1).
5. Meshing fails part-way: the previous `pre_geom.msh` stays as it was, so the input files never see a half-written mesh (test in Task 1).

---

### Task 0: Ruff-format the addon files this change touches

`jobwriter.py`, `mesher.py`, `objects.py` and `taskpanels.py` are not Ruff-formatted yet, and the pre-commit hook
reformats every staged file. Without this task the feature commits would carry formatting churn. AGENTS.md: make the
formatting-only commit separately and add its hash to `.git-blame-ignore-revs`.

**Files:**
- Modify (format only): `freecad_addon/emsolution/jobwriter.py`, `freecad_addon/emsolution/mesher.py`, `freecad_addon/emsolution/objects.py`, `freecad_addon/emsolution/taskpanels.py`
- Modify: `.git-blame-ignore-revs`

**Interfaces:**
- Consumes: nothing.
- Produces: the four files in Ruff format. Later tasks show code in that format; match it.

- [ ] **Step 1: Format the four files**

Run: `pixi run ruff format freecad_addon/emsolution/jobwriter.py freecad_addon/emsolution/mesher.py freecad_addon/emsolution/objects.py freecad_addon/emsolution/taskpanels.py`
Expected: `4 files reformatted`

- [ ] **Step 2: Confirm nothing but formatting changed**

Run: `pixi run pytest tests/freecad_addon -q`
Expected: all pass (same count as before formatting).

Run: `git diff --stat`
Expected: only the four files.

- [ ] **Step 3: Commit the formatting**

```bash
git add freecad_addon/emsolution/jobwriter.py freecad_addon/emsolution/mesher.py freecad_addon/emsolution/objects.py freecad_addon/emsolution/taskpanels.py
git commit -m "Apply Ruff format to the addon files the simulation folder change touches

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

- [ ] **Step 4: Record the hash in `.git-blame-ignore-revs`**

Run: `git rev-parse HEAD` and append to `.git-blame-ignore-revs`:

```
# Ruff format for jobwriter, mesher, objects and taskpanels
<full hash from git rev-parse HEAD>
```

```bash
git add .git-blame-ignore-revs
git commit -m "Ignore the addon Ruff format commit in blame

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 1: Mesher writes to `job["mesh_file"]` and `mesh.unv`

**Files:**
- Modify: `freecad_addon/emsolution/mesher.py` (module docstring and `run`)
- Test: `tests/freecad_addon/test_mesher.py`

**Interfaces:**
- Consumes: nothing from other tasks.
- Produces: job contract used by Task 2. `job.json` gains a required key `"mesh_file"` (absolute path of the `.msh`).
  The mesher writes `<job folder>/mesh.msh` first, then `os.replace`s it onto `job["mesh_file"]`, and writes
  `<job folder>/mesh.unv`. Its last stdout line is `Wrote <mesh_file>`. `model_name` stays in the job (Gmsh model name).

Between this task's commit and Task 2's, a GUI Run Mesh fails (the job writer does not write `mesh_file` yet). The
pytest suite stays green.

- [ ] **Step 1: Point the existing tests at the new names**

In `tests/freecad_addon/test_mesher.py`, add the `mesh_file` parameter to `run_job`:

```python
    def run_job(self, volumes, surfaces=(), version=4.1, sizes=(), options=None, mesh_file=None):
        job = {
            "model_name": "Model",
            "msh_version": version,
            "mesh_file": mesh_file or os.path.join(self.dir, "pre_geom.msh"),
            "volumes": list(volumes),
            "surfaces": list(surfaces),
            "sizes": list(sizes),
        }
```

Then rename the output files the tests read (5 × `Model.msh`, 1 × `Model.unv`):

Run: `sed -i 's/"Model\.msh"/"pre_geom.msh"/; s/"Model\.unv"/"mesh.unv"/' tests/freecad_addon/test_mesher.py`
Then: `grep -n "Model\." tests/freecad_addon/test_mesher.py`
Expected: no output.

- [ ] **Step 2: Add the new tests**

Add `import stat` after `import os` at the top of `tests/freecad_addon/test_mesher.py` (keep the other imports where they are):

```python
import json
import os
import stat
import subprocess
```

Add these methods to `MesherTest`, after `test_msh_version_22`:

```python
    def test_mesh_goes_to_mesh_file_and_unv_beside_the_job(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        target = os.path.join(self.dir, "run dir", "pre_geom.msh")
        os.mkdir(os.path.dirname(target))
        r = self.run_job([self.vol(1, "Copper_Box", "vol_1.brep")], mesh_file=target)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.path.isfile(target))
        self.assertTrue(os.path.isfile(os.path.join(self.dir, "mesh.unv")))
        self.assertFalse(os.path.exists(os.path.join(self.dir, "pre_geom.msh")))
        self.assertIn(f"Wrote {target}", r.stdout)

    def write_old_mesh(self):
        path = os.path.join(self.dir, "pre_geom.msh")
        with open(path, "w", encoding="ascii") as fh:
            fh.write("old")
        return path

    def read_text(self, path):
        with open(path, encoding="ascii") as fh:
            return fh.read()

    def test_existing_mesh_is_replaced(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        target = self.write_old_mesh()
        r = self.run_job([self.vol(1, "Copper_Box", "vol_1.brep")])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(self.read_text(target).startswith("$MeshFormat"))

    def test_failed_run_keeps_the_existing_mesh(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        write_box(self.geo("vol_2.brep"), 0.5, 0, 0, 1, 1, 1)  # overlaps vol_1
        target = self.write_old_mesh()
        r = self.run_job([self.vol(1, "A_Box", "vol_1.brep"), self.vol(2, "B_Box001", "vol_2.brep")])
        self.assertEqual(r.returncode, 1)
        self.assertEqual(self.read_text(target), "old")

    def test_read_only_mesh_fails_cleanly_and_stays(self):
        write_box(self.geo("vol_1.brep"), 0, 0, 0, 1, 1, 1)
        target = self.write_old_mesh()
        os.chmod(target, stat.S_IREAD)
        try:
            r = self.run_job([self.vol(1, "Copper_Box", "vol_1.brep")])
        finally:
            os.chmod(target, stat.S_IREAD | stat.S_IWRITE)  # let the temporary folder be deleted
        self.assertEqual(r.returncode, 1)
        self.assertTrue(r.stderr.strip().splitlines()[-1].startswith("ERROR:"), r.stderr)
        self.assertEqual(self.read_text(target), "old")
```

- [ ] **Step 3: Run the mesher tests and see them fail**

Run: `pixi run pytest tests/freecad_addon/test_mesher.py -q`
Expected: FAIL. The renamed tests fail because `pre_geom.msh` / `mesh.unv` are not written (the mesher still writes
`Model.msh`). `test_read_only_mesh_fails_cleanly_and_stays` fails with return code 0. `test_failed_run_keeps_the_existing_mesh` already passes.

- [ ] **Step 4: Change the mesher**

In `freecad_addon/emsolution/mesher.py`, replace the module docstring:

```python
"""Job file -> Gmsh .msh at job["mesh_file"] + mesh.unv beside the job. Runs in its own process.
Never import FreeCAD here.

Usage: python mesher.py <job.json>
"""
```

Replace `run`:

```python
def run(job_path):
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
        gmsh.model.mesh.generate(3)
        gmsh.option.setNumber("Mesh.MshFileVersion", float(job["msh_version"]))
        gmsh.option.setNumber("Mesh.Binary", 0)
        gmsh.write(msh)
        gmsh.write(os.path.join(folder, "mesh.unv"))
    finally:
        gmsh.finalize()
    os.replace(msh, job["mesh_file"])  # only a finished mesh replaces the solver's file
    for item in job["volumes"] + job["surfaces"]:
        print(f"{item['id']:>6}  {item['name']}")
    print(f"Wrote {job['mesh_file']}")
```

A read-only or locked target makes `os.replace` raise `PermissionError`; `main` turns it into the `ERROR:` line.

- [ ] **Step 5: Run the mesher tests and see them pass**

Run: `pixi run pytest tests/freecad_addon/test_mesher.py -q`
Expected: all PASS.

- [ ] **Step 6: Lint, format, commit**

Run: `pixi run lint` → `All checks passed!`
Run: `pixi run ruff format freecad_addon/emsolution/mesher.py tests/freecad_addon/test_mesher.py` → `2 files left unchanged`
(if it reformats, review the diff; it should only touch lines you wrote).

```bash
git add freecad_addon/emsolution/mesher.py tests/freecad_addon/test_mesher.py
git commit -m "Write the mesh to the job's mesh_file and mesh.unv beside the job

The mesher writes into the job folder and then replaces the target, so a failed
or blocked run leaves the existing pre_geom.msh untouched.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: The job writer targets the simulation folder

**Files:**
- Modify: `freecad_addon/emsolution/jobwriter.py` (replace `output_folder`; `write_job`)
- Modify: `freecad_addon/emsolution/runner.py` (`MeshRun.__init__`, `load_result`)
- Modify: `freecad_addon/emsolution/taskpanels.py` (`StudyView.refresh` notice)
- Test: `tests/freecad_addon/test_study.py`, `tests/freecad_addon/gui_smoke.py`

**Interfaces:**
- Consumes (Task 1): the mesher reads `job["mesh_file"]`, writes the `.msh` there and `mesh.unv` beside `job.json`.
- Produces:
  - `jobwriter.simulation_folder(study) -> str`: absolute directory of `study.Document.FileName`; raises
    `jobwriter.StudyError("Save the document in the simulation folder first.")` when the document was never saved.
  - `jobwriter.scratch_folder(study) -> str`: `<simulation_folder>/.pyemsi/freecad/<FCStd stem>/<study.Name>`. Pure path, not created.
  - `jobwriter.mesh_file(study) -> str`: `<simulation_folder>/pre_geom2D.msh` if `study.Dimension == "2D"`, else `<simulation_folder>/pre_geom.msh`.
  - `jobwriter.write_job(study) -> str`: same contract as before (returns the `job.json` path), now inside
    `scratch_folder(study)`, with `"mesh_file": mesh_file(study)` in the job. The shared-output-folder check is gone.
  - `runner.MeshRun.mesh_file` (str) and `runner.MeshRun.replaced` (bool: the file existed before the mesher started).
  - `jobwriter.output_folder` no longer exists.

- [ ] **Step 1: Save the test document in the temporary folder**

In `tests/freecad_addon/test_study.py`, `StudyTest.setUp`, replace

```python
        self.study.OutputFolder = self.tmp.name
```

with

```python
        self.doc.saveAs(os.path.join(self.tmp.name, "T.FCStd"))  # the temporary folder is the simulation folder
```

Add this helper after `ids`:

```python
    def scratch(self, *parts):
        return os.path.join(jobwriter.scratch_folder(self.study), *parts)
```

- [ ] **Step 2: Move the existing path expectations**

Edit these tests in `tests/freecad_addon/test_study.py`:

`test_body_in_app_part_is_exported_in_global_coordinates`:

```python
        vol.read(self.scratch("geometry", "vol_1.brep"))
```
```python
        face.read(self.scratch("geometry", "surf_1001_1.brep"))
```

`test_job_json_contents`: after `job = json.load(fh)`, insert

```python
        mesh_file = job.pop("mesh_file")
        self.assertEqual(os.path.basename(mesh_file), "pre_geom.msh")
        self.assertTrue(os.path.samefile(os.path.dirname(mesh_file), self.tmp.name))
```

and change the last loop line to

```python
            self.assertTrue(os.path.exists(self.scratch("geometry", rel)))
```

(`samefile` because the temp path may come back in 8.3 short form or with other separators.)

`test_face_edge_and_vertex_sizes_go_to_the_job`:

```python
        vertex.read(self.scratch("geometry", "size_2_1.brep"))
```

`test_written_job_meshes`: replace the last line with

```python
        self.assertTrue(os.path.exists(os.path.join(self.tmp.name, "pre_geom.msh")))
        self.assertTrue(os.path.isfile(self.scratch("mesh.unv")))
        self.assertTrue(os.path.isfile(self.scratch("job.json")))
```

`test_selected_geometry_controls_export_and_filters_other_assignments`:

```python
        self.assertTrue(os.path.isfile(self.scratch("mesh.unv")))
        with open(os.path.join(self.tmp.name, "pre_geom.msh"), encoding="utf-8") as fh:
```

`test_deferred_export_cannot_change_ids_or_write_files` and
`test_missing_selected_materials_are_named_before_ids_or_files_change`:

```python
            self.assertFalse(os.path.exists(self.scratch("job.json")))
```
(the second one is indented one level less: `        self.assertFalse(os.path.exists(self.scratch("job.json")))`)

`test_old_study_upgrade_preserves_settings_ids_and_default_output`: delete the three lines

```python
        self.assertEqual(
            os.path.normpath(jobwriter.output_folder(self.study)), os.path.normpath(os.path.splitext(path)[0] + "_mesh")
        )
```

(Task 3 rewrites the rest of this test.)

Delete these three tests entirely; the new tests in Step 3 replace them:
`test_output_folder_with_persian_letters`, `test_check_unsaved_document`,
`test_new_output_directories_are_independent_and_stable_under_rename`.

- [ ] **Step 3: Add the simulation folder tests**

Add after `test_names_equal_after_cleanup_are_refused` in `tests/freecad_addon/test_study.py`:

```python
    # --- simulation folder ----------------------------------------------------

    def test_mesh_file_is_the_emsolution_name_in_the_document_folder(self):
        folder = jobwriter.simulation_folder(self.study)
        self.assertTrue(os.path.samefile(folder, self.tmp.name))
        self.assertEqual(jobwriter.mesh_file(self.study), os.path.join(folder, "pre_geom.msh"))
        cross = objects.make_study(self.doc, "2D", "Cross-section")
        self.assertEqual(jobwriter.mesh_file(cross), os.path.join(folder, "pre_geom2D.msh"))

    def test_scratch_folder_is_per_document_and_study_and_survives_rename(self):
        second = objects.make_study(self.doc)
        folder = jobwriter.scratch_folder(self.study)
        rel = os.path.relpath(folder, jobwriter.simulation_folder(self.study))
        self.assertEqual(rel, os.path.join(".pyemsi", "freecad", "T", self.study.Name))
        self.study.Label = "Renamed"
        self.assertEqual(jobwriter.scratch_folder(self.study), folder)
        self.assertNotEqual(jobwriter.scratch_folder(second), folder)

    def test_save_as_moves_the_mesh_and_scratch_folders(self):
        other = os.path.join(self.tmp.name, "other")
        os.mkdir(other)
        self.doc.saveAs(os.path.join(other, "Moved.FCStd"))
        self.assertTrue(os.path.samefile(jobwriter.simulation_folder(self.study), other))
        self.assertEqual(os.path.dirname(jobwriter.mesh_file(self.study)), jobwriter.simulation_folder(self.study))
        self.assertIn(os.path.join(".pyemsi", "freecad", "Moved", self.study.Name), jobwriter.scratch_folder(self.study))

    def test_unsaved_document_is_refused_before_ids_or_files_change(self):
        doc = App.newDocument("Unsaved")
        self.addCleanup(App.closeDocument, doc.Name)
        study = objects.make_study(doc)
        study.MainMode = "Materials"
        box = doc.addObject("Part::Box", "A")
        doc.recompute()
        objects.make_material(study, "Copper", [box])
        with self.assertRaisesRegex(jobwriter.StudyError, "Save the document in the simulation folder first"):
            jobwriter.write_job(study)
        self.assertEqual(study.VolumeIds, {})

    def test_simulation_folder_with_spaces_and_persian_letters(self):
        objects.make_material(self.study, "Copper", [self.box("A")])
        folder = os.path.join(self.tmp.name, "my model مدل")
        os.mkdir(folder)
        self.doc.saveAs(os.path.join(folder, "موتور.FCStd"))
        path = jobwriter.write_job(self.study)
        r = subprocess.run([sys.executable, MESHER, path], capture_output=True, encoding="utf-8", errors="replace")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.path.isfile(os.path.join(folder, "pre_geom.msh")))
        self.assertTrue(os.path.isfile(self.scratch("mesh.unv")))

    def test_second_study_replaces_the_mesh_and_keeps_its_own_scratch_folder(self):
        objects.make_material(self.study, "Iron", [self.box("A")])
        second = objects.make_study(self.doc)
        second.MainMode = "Materials"
        objects.make_material(second, "Air", [self.box("B", 10)])
        for study in (self.study, second):
            path = jobwriter.write_job(study)
            r = subprocess.run([sys.executable, MESHER, path], capture_output=True, encoding="utf-8", errors="replace")
            self.assertEqual(r.returncode, 0, r.stderr)
        with open(os.path.join(self.tmp.name, "pre_geom.msh"), encoding="utf-8") as fh:
            names = fh.read().split("$PhysicalNames\n", 1)[1].split("$EndPhysicalNames", 1)[0]
        self.assertIn('"B"', names)
        self.assertNotIn('"A"', names)
        self.assertNotEqual(jobwriter.scratch_folder(self.study), jobwriter.scratch_folder(second))
        self.assertTrue(os.path.isfile(self.scratch("mesh.unv")))
```

- [ ] **Step 4: Run the Study tests and see them fail**

Run: `pixi run pytest tests/freecad_addon/test_study.py -q`
Expected: FAIL with `AttributeError: module 'emsolution.jobwriter' has no attribute 'scratch_folder'` (and
`simulation_folder` / `mesh_file`) in the tests above and in every test that calls `self.scratch`.

- [ ] **Step 5: Implement the path rules and the new `write_job`**

In `freecad_addon/emsolution/jobwriter.py`, replace `output_folder` with:

```python
def simulation_folder(study):
    """The folder of the saved .FCStd: EMSolution's run folder."""
    if not study.Document.FileName:
        raise StudyError("Save the document in the simulation folder first.")
    return os.path.dirname(os.path.abspath(study.Document.FileName))


def scratch_folder(study):
    """Gmsh working files: <simulation folder>/.pyemsi/freecad/<FCStd stem>/<Study Name>."""
    stem = os.path.splitext(os.path.basename(study.Document.FileName))[0]
    return os.path.join(simulation_folder(study), ".pyemsi", "freecad", stem, study.Name)


def mesh_file(study):
    """The fixed name EMSolution reads from the run folder."""
    return os.path.join(simulation_folder(study), "pre_geom2D.msh" if study.Dimension == "2D" else "pre_geom.msh")
```

In `write_job`, replace the docstring and everything from `folder = output_folder(study)` through the `job = {...}`
literal with the following. The rest of the function (volume, surface and size exports, writing `job.json`) is unchanged.

```python
def write_job(study):
    """Run the checks, update the ID table, write job.json and BREPs to the scratch folder. Returns the job path."""
    volumes, surfaces, elements = check(study)
    folder = scratch_folder(study)  # raises for an unsaved document, before the IDs change
    objects.update_ids(study)
    os.makedirs(os.path.join(folder, "geometry"), exist_ok=True)
    job = {
        "model_name": objects.clean(study.Label),
        "msh_version": float(study.MshVersion),
        "mesh_file": mesh_file(study),
        "options": mesh_options(study.MeshSizesGroup),
        "volumes": [],
        "surfaces": [],
        "sizes": [],
    }
```

- [ ] **Step 6: Run the Study tests and see them pass**

Run: `pixi run pytest tests/freecad_addon/test_study.py -q`
Expected: all PASS.

- [ ] **Step 7: Runner reads `mesh.unv` and reports the written file**

In `freecad_addon/emsolution/runner.py`, `MeshRun.__init__`, after `self.error = ""` add:

```python
        with open(job, encoding="utf-8") as fh:
            self.mesh_file = json.load(fh)["mesh_file"]
        self.replaced = os.path.exists(self.mesh_file)  # before the mesher starts
```

Replace `load_result` from its `with open(self.job ...)` line to the end with:

```python
        doc = self.study.Document
        mesh_obj = self.study.MeshResult
        if mesh_obj is None:
            mesh_obj = doc.addObject("Fem::FemMeshObject", "MeshResult")
            self.study.addObject(mesh_obj)
            self.study.MeshResult = mesh_obj
        mesh_obj.FemMesh = Fem.read(os.path.join(os.path.dirname(self.job), "mesh.unv"))
        doc.recompute()
        folder, name = os.path.split(self.mesh_file)
        replaced = " (replaced existing file)" if self.replaced else ""
        App.Console.PrintMessage(
            f"{name} written to {folder} from Study {self.study.Label}{replaced}\n"
            'Input files read it with INPUT_MESH_FILE = "GMSH" (11).\n'
        )
```

(The two `import` lines at the top of `load_result` stay as they are.)

- [ ] **Step 8: Panel notice names the target file**

In `freecad_addon/emsolution/taskpanels.py`, `StudyView.refresh`, replace the `try` block that calls
`jobwriter.output_folder` with:

```python
            try:
                self.export_notice.setText(f"Writes {jobwriter.mesh_file(study)}")
            except jobwriter.StudyError as exc:
                self.export_notice.setText(str(exc))
```

- [ ] **Step 9: GUI smoke test saves its document and checks the new files**

In `tests/freecad_addon/gui_smoke.py`:

After `from emsolution import commands, objects, runner, taskpanels` add a new line:

```python
    from emsolution import jobwriter
```

Replace `    study.OutputFolder = tempfile.mkdtemp()` with:

```python
    doc.saveAs(os.path.join(tempfile.mkdtemp(), "Smoke.FCStd"))  # the simulation folder
```

Before `    log.append(f"mesh ok: {study.MeshResult.FemMesh.VolumeCount} volumes")` add:

```python
    assert os.path.isfile(jobwriter.mesh_file(study)), "no pre_geom.msh beside the document"
    assert os.path.isfile(os.path.join(jobwriter.scratch_folder(study), "mesh.unv"))
    assert not run.replaced
```

The line `mat.References = [doc.A, doc.B]` appears twice. Take the second one (near the end of `main`, followed by
`view.refresh()` and the second `run = runner.start(study)`) and replace that two-line pair with:

```python
    mat.References = [doc.A, doc.B]
    view.refresh()
    assert view.export_notice.text() == f"Writes {jobwriter.mesh_file(study)}", view.export_notice.text()
```

After the second `assert run.error == "" and not runner.busy()` add:

```python
    assert run.replaced, "the second run did not replace pre_geom.msh"
```

- [ ] **Step 10: Run the GUI smoke test**

Link the addon once if not done (PowerShell, repo root; from the docstring of `gui_smoke.py`):

```powershell
$h = "$env:TEMP\ems_fc_home"; New-Item -ItemType Directory -Force "$h\Mod" | Out-Null
if (-not (Test-Path "$h\Mod\EMSolution")) { New-Item -ItemType Junction -Path "$h\Mod\EMSolution" -Target "$PWD\freecad_addon" | Out-Null }
$env:FREECAD_USER_HOME = $h
pixi run freecad tests\freecad_addon\gui_smoke.py
Get-Content "$env:TEMP\ems_gui_smoke.txt"
```

Expected: the last line is `PASS`. (A crash report from FreeCAD after quitting is known and harmless.) If the junction
already points at another checkout, the smoke test exercises that checkout: check with
`(Get-Item "$env:TEMP\ems_fc_home\Mod\EMSolution").Target` and recreate it to point at this worktree.

- [ ] **Step 11: Lint, format, commit**

Run: `pixi run lint` → `All checks passed!`
Run: `pixi run ruff format freecad_addon/emsolution/jobwriter.py freecad_addon/emsolution/runner.py freecad_addon/emsolution/taskpanels.py tests/freecad_addon/test_study.py tests/freecad_addon/gui_smoke.py`
Expected: `5 files left unchanged` (if not, review: only your lines may move).

```bash
git add freecad_addon/emsolution/jobwriter.py freecad_addon/emsolution/runner.py freecad_addon/emsolution/taskpanels.py tests/freecad_addon/test_study.py tests/freecad_addon/gui_smoke.py
git commit -m "Write Study meshes as pre_geom.msh into the simulation folder

The simulation folder is the folder of the saved .FCStd. job.json, the BREPs and
mesh.unv go to .pyemsi/freecad/<FCStd stem>/<Study Name>/. Several Studies may
target the same folder; the last Run Mesh wins.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: Remove `OutputFolder` and `LegacyOutput`

**Files:**
- Modify: `freecad_addon/emsolution/objects.py` (`Study.__init__`, `Study.add_setup`, `Study.onDocumentRestored`)
- Modify: `freecad_addon/emsolution/taskpanels.py` (`StudyView.__init__`, delete `save_output` and `browse_output`)
- Test: `tests/freecad_addon/test_study.py`

**Interfaces:**
- Consumes (Task 2): `jobwriter.mesh_file(study)`; nothing reads `OutputFolder` or `LegacyOutput` any more.
- Produces: Studies without `OutputFolder` / `LegacyOutput`. `Study.add_setup(obj, legacy=False)` keeps its
  signature; `legacy=True` still sets a missing `MainMode` to `"Materials"`.

- [ ] **Step 1: Update the restore and upgrade tests**

In `test_two_studies_restore_their_sources_settings_and_ids`, replace

```python
        self.assertFalse(first.LegacyOutput)
```

with

```python
        self.assertNotIn("LegacyOutput", first.PropertiesList)
        self.assertNotIn("OutputFolder", first.PropertiesList)
```

Replace the whole `test_old_study_upgrade_preserves_settings_ids_and_default_output` with:

```python
    def test_old_study_upgrade_preserves_settings_ids_and_drops_output_properties(self):
        objects.make_material(self.study, "Iron", [self.box("A")])
        objects.update_ids(self.study)
        self.study.MeshSizesGroup.DefaultMeshSize = 1.25
        for prop in (
            "Dimension",
            "Movement",
            "MainMode",
            "MovingMode",
            "MainSource",
            "MovingSource",
            "MainObjects",
            "MovingObjects",
        ):
            self.study.removeProperty(prop)
        # what a Study saved before the simulation folder change carried
        self.study.addProperty("App::PropertyString", "OutputFolder", "EMSolution")
        self.study.OutputFolder = os.path.join(self.tmp.name, "elsewhere")
        self.study.addProperty("App::PropertyBool", "LegacyOutput", "Setup")
        path = os.path.join(self.tmp.name, "old.FCStd")
        self.doc.saveAs(path)
        App.closeDocument(self.doc.Name)
        self.doc = App.openDocument(path)
        self.study = objects.find_study(self.doc)
        self.study.Proxy.onDocumentRestored(self.study)  # repeat must not reset data
        self.assertEqual(self.study.VolumeIds, {"A": "1"})
        self.assertEqual(self.study.MeshSizesGroup.DefaultMeshSize.Value, 1.25)
        self.assertEqual(self.study.MainMode, "Materials")
        self.assertNotIn("OutputFolder", self.study.PropertiesList)
        self.assertNotIn("LegacyOutput", self.study.PropertiesList)
        self.assertEqual(geometry.export_unavailable(self.study), "")
        self.assertTrue(os.path.isfile(jobwriter.write_job(self.study)))
        self.assertTrue(os.path.samefile(os.path.dirname(jobwriter.mesh_file(self.study)), self.tmp.name))
```

Add after `test_study_survives_save_and_reload`:

```python
    def test_new_study_has_no_output_properties(self):
        for prop in ("OutputFolder", "LegacyOutput"):
            self.assertNotIn(prop, self.study.PropertiesList)
```

- [ ] **Step 2: Run the tests and see them fail**

Run: `pixi run pytest tests/freecad_addon/test_study.py -q -k "output_properties or restore_their_sources"`
Expected: FAIL. The new Study still has both properties; the upgrade test fails on
`assertNotIn("OutputFolder", ...)`; the restore test fails on `assertNotIn("LegacyOutput", ...)`.

- [ ] **Step 3: Remove the properties in `objects.py`**

In `Study.__init__`, delete the whole `obj.addProperty("App::PropertyString", "OutputFolder", ...)` statement, with its
doc string `"Empty = folder <document>_mesh next to the .FCStd"` (Ruff may have wrapped it over several lines).

At the end of `Study.add_setup`, delete:

```python
        if "LegacyOutput" not in obj.PropertiesList:
            obj.addProperty("App::PropertyBool", "LegacyOutput", "Setup")
            obj.LegacyOutput = legacy
        obj.setEditorMode("LegacyOutput", 2)
```

Replace `onDocumentRestored` with:

```python
    def onDocumentRestored(self, obj):
        for prop in ("OutputFolder", "LegacyOutput"):  # replaced by the simulation folder
            if prop in obj.PropertiesList:
                obj.removeProperty(prop)
        self.add_setup(obj, legacy=True)
```

- [ ] **Step 4: Run the Study tests and see them pass**

Run: `pixi run pytest tests/freecad_addon/test_study.py -q`
Expected: all PASS.

- [ ] **Step 5: Remove the Output folder field from the Study panel**

In `freecad_addon/emsolution/taskpanels.py`, `StudyView.__init__`, delete the folder row (keep `output = QtWidgets.QFormLayout()`
and `layout.addLayout(output)`, which still hold the MSH version row):

```python
        folder_row = QtWidgets.QHBoxLayout()
        self.output = QtWidgets.QLineEdit(study.OutputFolder)
        self.output.setPlaceholderText("Automatic folder beside the saved document")
        browse = QtWidgets.QPushButton("Browse…")
        browse.clicked.connect(self.browse_output)
        folder_row.addWidget(self.output)
        folder_row.addWidget(browse)
        output.addRow("Output folder", folder_row)
```

and the signal hookup:

```python
        self.output.editingFinished.connect(self.save_output)
```

Delete the methods `save_output` and `browse_output` entirely.

Then check nothing else refers to them:

Run: `grep -rn "OutputFolder\|LegacyOutput\|output_folder\|save_output\|browse_output\|self\.output\b" freecad_addon tests/freecad_addon`
Expected: only the `onDocumentRestored` tuple in `objects.py`, the lines in
`test_old_study_upgrade_preserves_settings_ids_and_drops_output_properties` that recreate the old properties, and the
`assertNotIn` lines in `test_study.py`.

- [ ] **Step 6: Lint, format, commit**

Run: `pixi run lint` → `All checks passed!`
Run: `pixi run ruff format freecad_addon/emsolution/objects.py freecad_addon/emsolution/taskpanels.py tests/freecad_addon/test_study.py`
Expected: `3 files left unchanged`.

```bash
git add freecad_addon/emsolution/objects.py freecad_addon/emsolution/taskpanels.py tests/freecad_addon/test_study.py
git commit -m "Remove the Study OutputFolder and LegacyOutput properties

Run Mesh always writes into the simulation folder now. Restoring an older
document drops both properties so they no longer show in the property editor.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: Final verification

**Files:** none changed unless a check fails.

**Interfaces:**
- Consumes: everything above.
- Produces: a verified branch.

- [ ] **Step 1: Full test suite**

Run: `pixi run test`
Expected: all PASS. Report the pass count; if anything fails, show the output and fix it in the task that owns the code.

- [ ] **Step 2: Lint and format check on the changed files**

Run: `pixi run lint` → `All checks passed!`
Run: `pixi run ruff format --check freecad_addon/emsolution/jobwriter.py freecad_addon/emsolution/mesher.py freecad_addon/emsolution/objects.py freecad_addon/emsolution/runner.py freecad_addon/emsolution/taskpanels.py tests/freecad_addon/test_study.py tests/freecad_addon/test_mesher.py tests/freecad_addon/gui_smoke.py`
Expected: `8 files already formatted`.

- [ ] **Step 3: GUI smoke test**

Run the PowerShell block from Task 2, Step 10.
Expected: last line `PASS`.

- [ ] **Step 4: Manual check in FreeCAD (report the result, do not automate)**

Open a saved `.FCStd` with a Study, open the Study panel, and confirm: there is no Output folder field; the notice reads
`Writes <folder>\pre_geom.msh`; after Generate mesh the Report view shows
`pre_geom.msh written to <folder> from Study <Label>` and the `INPUT_MESH_FILE = "GMSH" (11)` reminder, and on a second run
`(replaced existing file)`.

Out of scope here (spec section 9): running the real `EMSolution.exe` against `pre_geom.msh`.
