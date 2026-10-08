# Windows installer prototype: report

Date: 2026-10-08. Branch: `installer-prototype`. All new files are under `installer/`; no existing file was changed.

## Goal

Ship FreeCAD + the EMSolution addon + pyemsi (Femap converter, VTK viewer, input control editor) to customers as one Windows installer. Stock FreeCAD can't run pyemsi's web editors because it has no QtWebEngine (see "From before" under "Open matters"). The prototype therefore bundles conda-forge FreeCAD 1.1.0 with QtWebEngine 6.10.2, which is the stack pyemsi's pixi env already uses.

## What was built

| File | Purpose |
|---|---|
| `installer/pixi.toml` | Build tools env (rattler-build 0.76.1, constructor 3.17.3, conda-standalone, nsis) and tasks |
| `installer/recipes/ems-file-format-converter/recipe.yaml` | Repackages the PyPI wheel 0.5.1, which isn't on conda-forge |
| `installer/recipes/pyemsi/recipe.yaml` | Builds pyemsi 0.6.0 (with the Cython `femap_parser`) from a local checkout; set `PYEMSI_SRC`, default `C:/Users/eskandarih/pyemsi` |
| `installer/recipes/emsolution-freecad/recipe.yaml` | Addon package: copies `InitGui.py`, `package.xml`, `emsolution/`, `icons/` to `<prefix>\Library\Mod\EMSolution`; adds the launcher and the shortcut definition |
| `installer/recipes/emsolution-freecad/emsolution-freecad.bat` | Launcher: sets the conda PATH, runs `etc\conda\activate.d\*.bat`, sets `QT_API` and `QTWEBENGINE_CHROMIUM_FLAGS`, then starts `freecad.exe` |
| `installer/recipes/emsolution-freecad/menu.json` | menuinst shortcut "EMSolution FreeCAD" (Start Menu + desktop), using freecad.exe's icon |
| `installer/construct.yaml` | Installer definition: offline, per-user NSIS `.exe` with an uninstaller and silent install support |
| `installer/smoke_test.py` | `freecad.exe smoke_test.py <out_dir> <input.json>`: checks the workbench, imports pyemsi, opens the input control editor in its own window, writes `result.txt` and screenshots |

Build it with:

```
cd installer
pixi run installer      # = pixi run packages, then constructor -> dist\EMSolution-FreeCAD-0.1.0-Windows-x86_64.exe
```

Install silently with `EMSolution-FreeCAD-0.1.0-Windows-x86_64.exe /S /D=<prefix>`. The prefix must be the last argument, without quotes or spaces.

## Results

- Packages built: `ems-file-format-converter` (noarch), `pyemsi` (win-64; its import test passed, including `pyemsi.core.femap_parser`), `emsolution-freecad` (noarch).
  - setuptools found Visual Studio 18 by itself. The recipe deliberately doesn't use `compiler('c')`, because conda-forge's vs2022 activation can't find VS 18.
- Installer: 1.06 GB `.exe`. It installs about 330 packages, 4.6 GB on disk.
- Silent install to `%LOCALAPPDATA%\EMSFC-test`: exit 0. It created the Start Menu (`EMSolution\EMSolution FreeCAD`) and desktop shortcuts, plus `Uninstall-EMSolution-FreeCAD.exe`.
- Smoke test through the installed launcher, with a fresh FreeCAD user profile:
  - FreeCAD 1.1.0 starts from the installed prefix.
  - `EMSolutionWorkbench` is registered.
  - pyemsi 0.6.0 imports from the installed site-packages.
  - The input control editor (QWebEngineView, own top-level window) reports `_ready`, and its page has 1097 characters of text.
  - FreeCAD exits cleanly.
- Not verified: how the editor looks in the installed build. Every screenshot was black, but at that point the whole RDP desktop captured black, including a control run on the dev env that had rendered fine earlier. So this looks like the remote session, not the build. Check it by launching the desktop shortcut.

## Findings and gotchas

1. **conda's `freecad.exe` can't start without the conda PATH.** It fails with `0xC0000135` (DLL not found) because `python311.dll` and other DLLs live in the prefix root, `Library\mingw-w64\bin` and so on. Hence the `.bat` launcher.
2. **Windows MAX_PATH (260) applies.** `LongPathsEnabled` is 0 on this machine, as it is by default.
   - Building pyemsi: Monaco's deepest file (`.../monaco-editor/min/vs/basic-languages/restructuredtext/restructuredtext.js`) went over the limit inside rattler-build's work dir. Fixed with `--no-build-id`. That flag makes rattler-build reuse the build dir, so the task deletes `output/bld` first. It uses PowerShell for that because pixi's `rm -rf` fails on read-only files.
   - Installing: constructor extracts packages to `<prefix>\pkgs\<pkg>\...`. VTK's `viskores` headers make that 203 characters, so the installer aborts (silently, exit 2) when the prefix is longer than 55 characters. When the installer runs as admin, it enables long paths itself.
   - I changed the default prefix to `%LOCALAPPDATA%\EMS-FreeCAD`, which fits user names of up to 20 characters. The `.exe` was built before this change, so it still has `%LOCALAPPDATA%\EMSolution-FreeCAD`. Rebuild to pick it up.
3. **constructor only renders Jinja when the YAML fails to parse.** `construct.yaml` therefore starts with a `{% set %}` line, which is invalid YAML on purpose, to get an absolute path for the local channel. A bare `output` was treated as an anaconda.org channel name.
4. **pyemsi's package data leaves out `.ico` files.** `pyemsi/resources/icons/Icon.ico` is tracked in git but isn't installed. The shortcut uses `freecad.exe`'s icon instead.
5. **The dev pixi env has Mesa's `opengl32.dll` in `Library\bin`** (pulled in by an older `viskores` build); the installed env doesn't. Adding Mesa didn't change the black screenshots, so this was a red herring. It's worth knowing, though, because the earlier WebEngine spikes may have rendered with Mesa.
6. **The conda-forge FreeCAD 1.1.0 solve pulls in Qt5:** the Qt5 build of `pivy`, plus `soqt`, `qt-main` 5.15 and `pyqt` 5. The dev env has the same packages.

## Open matters

### From this prototype

1. **The install takes 45 minutes** (2736 s, almost all of it package extraction, probably slowed by Defender scanning). This is the main blocker for customers. Things to try:
   - Trim packages (next item).
   - `compression_level` in `construct.yaml`.
   - Measure with Defender's real-time scanning excluded.
   - Compare against a zip of a pre-installed prefix.
2. **Size trimming.** The largest packages:
   - qt6-webengine 177 MB, freecad 117 MB, mkl 109 MB, qt6-main 83 MB, qt-main (Qt5) 56 MB, vtk-base 54 MB, libclang13 36 MB, nodejs 33 MB (pulled in by basedpyright), libboost-headers 14 MB, viskores 11 MB (headers).
   - Candidates: drop Qt5 (pin a Qt6 `pivy` build if one exists), use OpenBLAS instead of MKL, make basedpyright/nodejs optional, drop dev headers. Removing the long headers would also relax the 55-character prefix limit.
3. **The console window flashes** briefly because the shortcut runs a `.bat`. Options: menuinst `activate: true` (it activates through the bundled `_conda.exe`), a small launcher `.exe`, or setting PATH and env vars in the addon's `Init.py`. The last one is not possible for DLL loading, because `freecad.exe` needs the PATH before it starts.
4. **Hard-coded versions** (0.6.0, 0.1.0, 0.5.1) and a local checkout path for pyemsi. For CI, read versions from the sources and build pyemsi from a git tag.
5. **CI:** a short checkout path (MAX_PATH), caching of the constructor/rattler package caches (several GB), running `smoke_test.py` after a silent install, and an uninstall test.
6. **Not yet integrated:** the addon only *bundles* pyemsi. No workbench command opens the editor, converter, viewer, output view or file explorer yet; the smoke test opens the editor from a script.

### From before (spikes in the same session)

7. **Where web editors can be hosted.** With `freecad.exe` as the host, QtWebEngine views (input control editor, Monaco, xterm) only work as **separate top-level windows**, with Qt's default RHI and **without** `QSG_RHI_BACKEND=opengl`.
   - Embedding them in FreeCAD's MDI tabs or docks crashes or renders black.
   - Tab embedding only worked in a Python-owned host: QApplication created by Python, a web view created *and shown* before `FreeCADGui.showMainWindow()`, and FreeCAD's main window in a sibling tab (pyemsi's approach).
   - Decide: own windows in stock `freecad.exe` (what the prototype assumes), or a custom Python launcher host.
8. **Exit crash `0xC0000409`** with the pyemsi graphics policy (`QSG_RHI_BACKEND=opengl` + `AA_ShareOpenGLContexts`) in the Python-host setup. Not investigated.
9. **pyvista `QtInteractor` tabs** need `plotter.close()` before FreeCAD exits, otherwise there are about 77 `wglMakeCurrent failed` errors at shutdown.
10. **Licensing:** pyemsi is GPLv3, while the addon's `package.xml` says `Proprietary`. Bundling and importing pyemsi from the addon needs a licence decision before shipping. The installer also has no licence page yet (`license_file` in `construct.yaml`).
11. **Branding and trust:** FreeCAD branding (`branding.xml`: splash, title, icon), Authenticode signing of the installer and uninstaller (SmartScreen), and an update and upgrade strategy (in-place upgrade vs uninstall and reinstall).
12. **Stock FreeCAD option** (if web editors are rewritten natively): pyemsi's converter and field viewer run on stock FreeCAD 1.1.4 with vendored pure-Python deps, but this needs two changes:
    - lazy QtWebEngine imports in pyemsi (`plotter` -> `widgets/__init__` -> `split_container` -> `monaco_lsp` import it eagerly);
    - a stub for the missing `vtkmodules.vtkRenderingMatplotlib`.

## Changes outside the repo

These files outside the repo were left on this machine. Delete them if they're not needed.

- Test install: `%LOCALAPPDATA%\EMSFC-test` (4.6 GB), plus the Start Menu folder `EMSolution` and the desktop shortcut `EMSolution FreeCAD.lnk`. Remove with `Uninstall-EMSolution-FreeCAD.exe` in that folder.
- Package caches: `~/.conda/constructor` (constructor's download cache) and `%LOCALAPPDATA%\rattler\cache` (shared with pixi).
- Build outputs, all ignored by git: `installer/.pixi` (tools env), `installer/output` (local conda channel with the three packages), `installer/dist` (the `.exe`). They live in the worktree where they were built: `.claude/worktrees/installer-prototype/installer/`.
- The pyemsi checkout and its pixi env are unchanged. I added a temporary launcher copy to the env's `Scripts` folder and removed it again.
