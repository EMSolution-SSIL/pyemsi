# Monaco / VTK rendering issues with `QSG_RHI_BACKEND=opengl`

Status: open, not part of the FreeCAD `.FCStd` tab feature. Recorded here so it can be picked up separately.
Observed on: Windows 11, AMD GPU (`atio6axx.dll`), PySide6 / Qt 6.10.2, Pixi env `.pixi/envs/default`, branch `feat/freecad-fcstd-tab`.

## Background

`pyemsi.gui.launch()` now applies a startup graphics policy before the `QApplication` exists: `os.environ.setdefault("QSG_RHI_BACKEND", "opengl")` and `QCoreApplication.setAttribute(AA_ShareOpenGLContexts)`. It is required for the FreeCAD tab: without it FreeCAD's `QOpenGLWidget` view crashes the process ("The top-level window is not using OpenGL for composition, 'D3D11' is not compatible with QOpenGLWidget", "No valid GL context found!", exit `-1073740771`). With only `AA_ShareOpenGLContexts` and no RHI override, the FreeCAD view renders black.

The two issues below are side effects of that policy on the Monaco editor (`QWebEngineView`) and the VTK field tab (`QVTKRenderWindowInteractor`). Both reproduce **without** FreeCAD ever being initialised, so they are a Qt WebEngine / VTK / OpenGL-composition interaction, not a FreeCAD integration bug.

## Issue 1: Monaco tab turns black after a window resize while the VTK tab is current

Steps (automated, 12 iterations per run, real desktop `QApplication`, launched via `pixi run python`):

1. Open a text file (Monaco tab) and add a VTK field tab (`SplitContainer.add_field(Plotter(...))`).
2. Make the VTK tab current.
3. Resize the main window.
4. Switch back to the Monaco tab.

Result: the Monaco view is fully black (screenshot ink fraction 1.0) in 12/12 iterations with the policy on, 0/12 with the policy off. It does not recover after waiting 3 s, `update()`, a 1 px widget resize, or hide/show. Happens with or without a FreeCAD tab present. If a Monaco tab is current during the resize, it stays fine. Not reproduced by the user during manual testing.

Untested ideas: `QCoreApplication.setAttribute(AA_DontCreateNativeWidgetSiblings)`, `QT_WIDGETS_RHI=1`, forcing the VTK widget to a native window before the WebEngine view is created, or re-creating the WebEngine page on `showEvent` when the previous paint was black.

## Issue 2: `0xC0000409` (-1073740791) at process exit

3 runs per configuration, exit code identical every time:

| Configuration | Exit code |
|---|---|
| policy ON, Monaco only (no FreeCAD, no VTK) | `0xC0000409` |
| policy ON, Monaco + FreeCAD + VTK | `0xC0000409` |
| policy OFF, Monaco only | `0` |

The crash is in the Qt WebEngine teardown on the AMD D3D11/OpenGL driver after the main window closed normally; all pyemsi cleanup (settings persistence, kernel shutdown, FreeCAD detach) has already completed. The handoff for the FreeCAD feature forbids masking it with `os._exit()` or GPU toggles (`QT_OPENGL=software`, `--disable-gpu`, ANGLE overrides).

Untested ideas: explicitly `deleteLater()` all `QWebEngineView`/`QWebEnginePage` instances and process events before `QApplication` quits; `QSG_RHI_BACKEND=opengl` combined with `QTWEBENGINE_CHROMIUM_FLAGS=--use-angle=gl`; checking whether a newer AMD driver or Qt 6.10.x patch release changes the result.

## How the data was gathered

Scratch scripts (not committed): a smoke driver that launches `pyemsi.gui.launch()` with a stub `_exec_app`, opens files through `SplitContainer.open_file`, grabs per-tab screenshots and computes an "ink" fraction; and a resize probe that repeats step 1-4 above per policy variant. Both must run under `pixi run python`; a bare interpreter leaves WebEngine views blank for unrelated reasons (missing Qt WebEngine resources on `PATH`).
