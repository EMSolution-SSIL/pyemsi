# One Branch, Two Installers: Design

Date: 2026-10-22
Status: decisions agreed in conversation, waiting for spec review
Branch: `feature/freecad-addon`

## 1. Goal

`main` holds both pyemsi and the EMSolution FreeCAD add-on, and one release produces two products:

- **pyemsi**: the wheel, the sdist and the Windows installer, with no FreeCAD in them, as in earlier releases.
- **EMSolution-FreeCAD**: a Windows installer with conda-forge FreeCAD (with QtWebEngine), the add-on and pyemsi.

The FreeCAD tabs inside the pyemsi GUI (opening `.FCStd` files in pyemsi) leave `main` and are kept on an
experimental branch.

## 2. Background

Facts from the repository on 2026-10-22:

- `feature/freecad-addon` is 106+ commits ahead of `main` (`4c6b980`, release 0.6.0) and changes nothing in
  `pyemsi/`. It adds `freecad_addon/`, `tests/freecad_addon/`, `installer/freecad/`, docs, the
  `.claude/skills/freecad-addon-api` reference, and in `pyproject.toml` the dependencies `ems-material-manager`
  and `qtpy` plus the pixi tasks `freecad` and `install-addon`.
- `main` already contains FreeCAD:
  - `freecad = "==1.1.0"` in `[tool.pixi.dependencies]` (since 0.5.1), so the default pixi environment carries it.
  - The FreeCAD tabs in the pyemsi GUI (release 0.6.0): `pyemsi/gui/freecad_runtime.py`, `freecad_session.py`,
    `_viewers/_freecad.py`, and FreeCAD code in `main_window.py` (diagnostics log tab, "New FreeCAD Document"
    action, logger names), `file_viewers.py`, `_viewers/_constants.py`, `gui/__init__.py`,
    `widgets/explorer_icons.py`, `widgets/split_container.py`, `widgets/xterm/_widget.py`, plus tests
    `test_freecad_*.py`, `test_main_window_freecad.py` and FreeCAD parts of a few other tests.
- What each pyemsi output takes:
  - wheel: `[tool.setuptools.packages.find] include = ["pyemsi*"]`, so nothing outside `pyemsi/`.
  - sdist: the files `MANIFEST.in` names, all under `pyemsi/` (plus README, LICENSE, requirements).
  - Windows installer (`tools/build_windows_private_runtime.py`, workflow `windows-packaging.yml`): copies only
    `pyemsi/` and pip-installs `[project].dependencies` (+ the tool's extra dependencies).
- `ems-material-manager` is used only by the add-on (`freecad_addon/emsolution/studymaterials.py`, `objects.py`,
  `materialstandins.py`); `qtpy` is used by pyemsi itself.
- `installer/freecad/` (prototype, see `dev_docs/installer-prototype-report.md`) builds conda packages with
  rattler-build and the `.exe` with constructor. Its pyemsi recipe hard-codes version `0.6.0`; the add-on recipe
  and `construct.yaml` hard-code `0.1.0`.
- The repository `EMSolution-SSIL/pyemsi` is public; publishing the add-on is fine (user, 2026-10-22).

## 3. Decisions

1. **One branch.** `main` keeps pyemsi and the add-on together; no separate repository.
2. **One version.** The add-on, the EMSolution-FreeCAD installer and pyemsi always share pyemsi's version
   (`pyemsi.__version__`). Nothing else holds a version number.
3. **The FreeCAD tabs move to `experimental/freecad-viewer`.** That branch is made from `main` as it is today, so
   the work is kept. On the integration branch the tabs are removed from pyemsi: the three FreeCAD modules, the
   FreeCAD parts of the other files listed in section 2, and their tests. `.FCStd` files are then handled like
   any other unknown file in the pyemsi explorer.
4. **pyemsi outputs carry no FreeCAD and no add-on dependency.** `ems-material-manager` leaves
   `[project].dependencies`; the add-on's conda recipe declares it instead.
5. **FreeCAD gets its own pixi environment.** The default environment has no FreeCAD. A pixi feature `freecad`
   (FreeCAD 1.1.0, `ems-material-manager`) builds an environment `addon`; the tasks `freecad`, `install-addon` and
   the add-on tests run there (`pixi run -e addon ...`). `pixi run test` in the default environment runs the pyemsi
   tests; a task `test-addon` runs `tests/freecad_addon` in `addon`. CI runs both.
6. **Two installer tasks, one version.** pixi tasks `installer-pyemsi` (the existing portable build + NSIS) and
   `installer-freecad` (the `installer/freecad` rattler-build + constructor build). The recipes and
   `construct.yaml` take the version from `pyemsi.__version__` (one source, passed in by the task), never a
   literal.
7. **CI chooses which installers to build.** `windows-packaging.yml` gets an input with the choices `pyemsi`,
   `freecad`, `both` (default `pyemsi`); the FreeCAD installer job runs only when chosen. The wheel/sdist workflow
   is unchanged.
8. **A guard against leaks.** A test or CI step checks that the pyemsi wheel, sdist and portable runtime contain no
   `freecad_addon`, no `FreeCAD` imports and no `ems_material`.
9. **Docs and agent files stay in `main`**: `docs/superpowers/`, `dev_docs/`, `AGENTS.md`, and the
   `.claude/skills/freecad-addon-api` reference.
10. **Merging and publishing need the user's go.** Creating the experimental branch is local; pushing it, merging
    into `main`, tagging and releasing happen only after the user says so.

## 4. Order of work

1. Create `experimental/freecad-viewer` from `main` (local).
2. On `feature/freecad-addon`: remove the FreeCAD tabs from pyemsi (decision 3).
3. Dependencies and pixi environments (decisions 4, 5), CI test jobs.
4. Version wiring and the two installer tasks (decisions 2, 6), CI input (decision 7).
5. Leak guard (decision 8).
6. Build both installers once locally; check the pyemsi installer has no FreeCAD, add-on or `ems_material`, and
   that the EMSolution-FreeCAD installer starts FreeCAD with the workbench and opens pyemsi's editors (its existing
   `smoke_test.py`).
7. With the user's go: merge into `main`, push, release.

## 5. Tests

- pyemsi suite in the default environment passes without FreeCAD installed.
- Add-on suite and GUI smoke test pass in `addon`.
- The leak guard (decision 8).
- Both installers build from one commit with the same version in their file names and metadata.

## 6. Open points for review

- **Explorer and `.FCStd`.** After the tabs are removed, should pyemsi open an `.FCStd` file with the system's
  default program (FreeCAD if installed), or do nothing? Assumed: system default, like other unknown files.
- **xterm widget.** `pyemsi/widgets/xterm/_widget.py` mentions FreeCAD; to be checked whether it is FreeCAD-only
  code or just a comment.
- **Python 3.11.** The EMSolution-FreeCAD installer stays on Python 3.11 because pyemsol needs it (prototype
  report); unchanged here.

## 7. Not in this step

Publishing the installers somewhere (GitHub Releases upload), code signing, an update channel, a pyemsi build that
bundles FreeCAD tabs.
