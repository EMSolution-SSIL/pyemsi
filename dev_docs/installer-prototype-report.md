# Windows installer prototype: report

Date: 2026-10-08. The prototype was built in the EMSolution-FreeCAD repo and then merged into pyemsi. The addon now lives in `freecad_addon/`, and the installer in `installer/freecad/`, next to the existing pyemsi installer (`installer/pyemsi.nsi`).

## Goal

Ship FreeCAD + the EMSolution addon + pyemsi (Femap converter, VTK viewer, input control editor) to customers as one Windows installer. Stock FreeCAD can't run pyemsi's web editors because it has no QtWebEngine (see "From before" under "Open matters"). The prototype therefore bundles conda-forge FreeCAD with QtWebEngine, the same stack as pyemsi's pixi env. It was built and tested with FreeCAD 1.1.0, Python 3.11 and Qt 6.10.2. It must stay on Python 3.11 because pyemsol needs it (see open matter 7).

## What was built

| File | Purpose |
|---|---|
| `installer/freecad/pixi.toml` | Build tools env (rattler-build 0.76.1, constructor 3.17.3, conda-standalone, nsis) and tasks |
| `installer/freecad/recipes/ems-file-format-converter/recipe.yaml` | Repackages the PyPI wheel 0.5.1, which isn't on conda-forge |
| `installer/freecad/recipes/pyemsi/recipe.yaml` | Builds pyemsi 0.6.0 (with the Cython `femap_parser`) from this repo |
| `installer/freecad/recipes/emsolution-freecad/recipe.yaml` | Addon package: copies `InitGui.py`, `package.xml`, `emsolution/` and `icons/` from `freecad_addon/` to `<prefix>\Library\Mod\EMSolution`; adds the launcher and the shortcut definition |
| `installer/freecad/recipes/emsolution-freecad/emsolution-freecad.bat` | Launcher: sets the conda PATH, runs `etc\conda\activate.d\*.bat`, sets `QT_API` and `QTWEBENGINE_CHROMIUM_FLAGS`, then starts `freecad.exe` |
| `installer/freecad/recipes/emsolution-freecad/menu.json` | menuinst shortcut "EMSolution FreeCAD" (Start Menu + desktop), using freecad.exe's icon |
| `installer/freecad/construct.yaml` | Installer definition: offline, per-user NSIS `.exe` with an uninstaller and silent install support |
| `installer/freecad/smoke_test.py` | `freecad.exe smoke_test.py <out_dir> <input.json>`: checks the workbench, imports pyemsi, opens the input control editor in its own window, writes `result.txt` and screenshots |

Build it with:

```
cd installer\freecad
pixi run installer      # = pixi run packages, then constructor -> dist\EMSolution-FreeCAD-0.1.0-Windows-x86_64.exe
```

Install silently with `EMSolution-FreeCAD-0.1.0-Windows-x86_64.exe /S /D=<prefix>`. The prefix must be the last argument, without quotes or spaces.

## Developer mode (no installer)

Day to day you don't need the installer. pyemsi's own pixi env already has FreeCAD 1.1.0 and an editable install of pyemsi. Point FreeCAD's user Mod folder at the addon:

```
mklink /J "%APPDATA%\FreeCAD\v1-1\Mod\EMSolution" "<pyemsi checkout>\freecad_addon"
```

Then start FreeCAD from pyemsi's root with:

```
pixi run freecad
```

Restart FreeCAD after you change the addon or pyemsi's Python code. After a change to the Cython code, rebuild it with `pixi run python setup.py build_ext --inplace`. An installed EMSolution FreeCAD also reads this Mod folder, so remove the junction while you test an installed build.

## Results

- Packages built:
  - `ems-file-format-converter` (noarch);
  - `pyemsi` (win-64); its import test passed, including `pyemsi.core.femap_parser`;
  - `emsolution-freecad` (noarch).
  - setuptools found Visual Studio 18 by itself. The recipe deliberately doesn't use `compiler('c')`, because conda-forge's vs2022 activation can't find VS 18.
- Installer: 1.06 GB `.exe`. It installs about 330 packages, 4.6 GB on disk.
- Silent install to `%LOCALAPPDATA%\EMSFC-test`: exit 0. It created the Start Menu (`EMSolution\EMSolution FreeCAD`) and desktop shortcuts, plus `Uninstall-EMSolution-FreeCAD.exe`.
- Smoke test through the installed launcher, with a fresh FreeCAD user profile:
  - FreeCAD 1.1.0 starts from the installed prefix.
  - `EMSolutionWorkbench` is registered.
  - pyemsi 0.6.0 imports from the installed site-packages.
  - The input control editor (QWebEngineView, own top-level window) reports `_ready`, and its page has 1097 characters of text.
  - FreeCAD exits cleanly.
- Not verified: how the editor looks in the installed build. Every screenshot came out black, but the whole RDP desktop captured black too, including a control run on the dev env that had rendered fine earlier. So the cause is most likely the remote session, not the build. Check it by launching the desktop shortcut.
- These results are from before the merge into pyemsi. The installer has not been rebuilt from the new layout yet.

## Findings and gotchas

1. **conda's `freecad.exe` can't start without the conda PATH.** It fails with `0xC0000135` (DLL not found) because `python311.dll` and other DLLs live in the prefix root, `Library\mingw-w64\bin` and so on. Hence the `.bat` launcher.
2. **Windows MAX_PATH (260) applies.** `LongPathsEnabled` is 0 on this machine, as it is by default.
   - **Building pyemsi:** Monaco's deepest file (`.../monaco-editor/min/vs/basic-languages/restructuredtext/restructuredtext.js`) went over the limit inside rattler-build's work dir.
     - Fixed with `--no-build-id`.
     - That flag makes rattler-build reuse the build dir, so the task deletes `output/bld` first. It uses PowerShell for that because pixi's `rm -rf` fails on read-only files.
   - **Installing:** constructor extracts packages to `<prefix>\pkgs\<pkg>\...`.
     - VTK's `viskores` headers make that 203 characters, so the installer aborts (silently, exit 2) when the prefix is longer than 55 characters.
     - When the installer runs as admin, it enables long paths itself.
   - **Default prefix:** I changed it to `%LOCALAPPDATA%\EMS-FreeCAD`, which fits user names of up to 20 characters. The `.exe` was built before this change, so it still uses `%LOCALAPPDATA%\EMSolution-FreeCAD`. Rebuild to pick it up.
3. **constructor only renders Jinja when the YAML fails to parse.** `construct.yaml` therefore starts with a `{% set %}` line, which is invalid YAML on purpose. That's how it gets an absolute path for the local channel; a bare `output` was treated as an anaconda.org channel name.
4. **pyemsi's package data leaves out `.ico` files.** `pyemsi/resources/icons/Icon.ico` is tracked in git but isn't installed. The shortcut uses `freecad.exe`'s icon instead.
5. **The dev pixi env has Mesa's `opengl32.dll` in `Library\bin`** (pulled in by an older `viskores` build); the installed env doesn't. Adding Mesa didn't change the black screenshots, so it wasn't the cause. It's still worth knowing, because the earlier WebEngine spikes may have rendered with Mesa.
6. **The conda-forge FreeCAD 1.1.0 solve pulls in Qt5:** the Qt5 build of `pivy`, plus `soqt`, `qt-main` 5.15 and `pyqt` 5. The dev env has the same packages.

## Open matters

### From this prototype

1. **The install takes 45 minutes** (2736 s). Almost all of it is package extraction, probably slowed by Defender scanning. This is the main blocker for customers. Things to try:
   - Trim packages (next item).
   - `compression_level` in `construct.yaml`.
   - Measure with Defender's real-time scanning excluded.
   - Compare against a zip of a pre-installed prefix.
2. **Size trimming.** The largest packages:
   - qt6-webengine 177 MB, freecad 117 MB, mkl 109 MB, qt6-main 83 MB, qt-main (Qt5) 56 MB, vtk-base 54 MB;
   - libclang13 36 MB, nodejs 33 MB (pulled in by basedpyright), libboost-headers 14 MB, viskores 11 MB (headers).
   - Candidates:
     - drop Qt5 (pin a Qt6 `pivy` build if one exists);
     - use OpenBLAS instead of MKL;
     - make basedpyright/nodejs optional;
     - drop dev headers. Removing the long headers would also relax the 55-character prefix limit.
3. **The console window flashes** briefly because the shortcut runs a `.bat`. Options:
   - menuinst `activate: true` (it activates through the bundled `_conda.exe`);
   - a small launcher `.exe`.
   - Setting PATH and env vars in the addon's `Init.py` won't work for DLL loading, because `freecad.exe` needs the PATH before it starts.
4. **Hard-coded versions** (0.6.0, 0.1.0, 0.5.1) in the recipes. For CI, read them from `pyproject.toml` and `freecad_addon/package.xml`.
5. **CI:** pyemsi already has a Windows packaging workflow (`windows-packaging.yml`, portable build + `pyemsi.nsi`), and the FreeCAD installer could become a job there. It needs:
   - a short checkout path (MAX_PATH);
   - caching of the constructor/rattler package caches (several GB);
   - `smoke_test.py` run after a silent install;
   - an uninstall test.
6. **Not yet integrated:** the addon only *bundles* pyemsi. No workbench command opens the editor, converter, viewer, output view or file explorer yet; the smoke test opens the editor from a script.
7. **Addon code and pyemsi's tooling:**
   - pyemsi's pre-commit hooks (ruff format + ruff check) now also run on `freecad_addon/`.
   - The addon's tests are in `tests/freecad_addon/` and run with `pixi run test`.
   - The GUI smoke test `tests/freecad_addon/gui_smoke.py` used to fail its folder-panels check on the pixi env's FreeCAD 1.1.0. Started from a script, 1.1.0 left the Tasks dock (in the right-hand overlay) stays hidden, so the folder panels and the edit dialogs never show. `dock.show()`, the dock's toggle action, `Gui.Control.showTaskView()`, a fresh profile and a 3 s delay all leave it hidden. The diff from 1.1.0 to 1.1.4 is in `DockWindowManager.cpp`, `OverlayManager.cpp` and `MainWindow.cpp` (overlay title bar and geometry restore); `TaskView.cpp` and `Control.cpp` are unchanged. Running `Std_DockOverlayAll` (View → Overlay → Toggle overlay for all) once makes the Tasks dock appear, and it stays visible after being put back into the overlay. So the fault is the overlay's state at startup, not the addon. Used by hand, 1.1.0 shows the panel normally, so only a FreeCAD started from a script is affected. On 1.1.0 the smoke test now takes the docks out of the overlay when the Tasks dock is in it, and it passes on both 1.1.0 and 1.1.4.
   - Newer FreeCAD can't be used: conda-forge has no Python 3.11 build of 1.1.3 or later, and pyemsol needs Python 3.11. So the pins stay at FreeCAD 1.1.0, Python 3.11 and Qt 6.10.2. If a newer FreeCAD is ever needed, it would have to be built for Python 3.11 from the conda-forge feedstock with rattler-build.
   - The mesher could not start on conda FreeCAD, because `python.exe` is in the env root, not `Library\bin`. `runner.python_exe()` now checks both.

### From before (spikes in the same session)

8. **Where web editors can be hosted.** With `freecad.exe` as the host, QtWebEngine views (input control editor, Monaco, xterm) only work as **separate top-level windows**, with Qt's default RHI and **without** `QSG_RHI_BACKEND=opengl`.
   - Embedding them in FreeCAD's MDI tabs or docks crashes or renders black.
   - Tab embedding only worked in a Python-owned host:
     - Python creates the QApplication;
     - a web view is created *and shown* before `FreeCADGui.showMainWindow()`;
     - FreeCAD's main window sits in a sibling tab (pyemsi's approach).
   - Decide: own windows in stock `freecad.exe` (what the prototype assumes), or a custom Python launcher host.
9. **Exit crash `0xC0000409`** with the pyemsi graphics policy (`QSG_RHI_BACKEND=opengl` + `AA_ShareOpenGLContexts`) in the Python-host setup. Not investigated.
10. **pyvista `QtInteractor` tabs** need `plotter.close()` before FreeCAD exits, otherwise there are about 77 `wglMakeCurrent failed` errors at shutdown.
11. **Licensing:** decided. The addon is open source like pyemsi, and `freecad_addon/package.xml` now says `GPL-3.0-or-later`.
    - Keep the closed-source solver (pyemsol) a separate process, as pyemsi already runs it.
    - The FreeCAD installer has no licence page yet (`license_file` in `construct.yaml`); `pyemsi.nsi` already has one.
12. **Branding and trust:**
    - FreeCAD branding (`branding.xml`: splash, title, icon);
    - Authenticode signing of the installer and uninstaller (SmartScreen);
    - an update and upgrade strategy (in-place upgrade vs uninstall and reinstall).
13. **Stock FreeCAD option** (if web editors are rewritten natively): pyemsi's converter and field viewer run on stock FreeCAD 1.1.4 with vendored pure-Python deps, but this needs two changes:
    - lazy QtWebEngine imports in pyemsi (`plotter` -> `widgets/__init__` -> `split_container` -> `monaco_lsp` import it eagerly);
    - a stub for the missing `vtkmodules.vtkRenderingMatplotlib`.

## Changes outside the repo

These files outside the repo were left on this machine. Delete them if they're not needed.

- **Test install:** `%LOCALAPPDATA%\EMSFC-test` (4.6 GB), plus the Start Menu folder `EMSolution` and the desktop shortcut `EMSolution FreeCAD.lnk`. Remove them with `Uninstall-EMSolution-FreeCAD.exe` in that folder.
- **Package caches:** `~/.conda/constructor` (constructor's download cache) and `%LOCALAPPDATA%\rattler\cache` (shared with pixi).
- **Build outputs**, all ignored by git: `.pixi` (tools env), `output` (local conda channel with the three packages) and `dist` (the `.exe`).
  - The existing ones are in the EMSolution-FreeCAD worktree where they were built (`.claude/worktrees/installer-prototype/installer/`).
  - A build in pyemsi writes them to `installer/freecad/`.
- **Old addon repo:** `C:\Users\eskandarih\EMSolution-FreeCAD` is unchanged and can be archived.
