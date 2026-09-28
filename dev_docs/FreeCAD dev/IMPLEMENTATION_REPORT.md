# FreeCAD `.FCStd` Integration — Implementation Report

Sections 1–7 record the original integration completed on 2026-09-17. Section 8
records the current design after the 2026-09-18 follow-up work and supersedes
the original single-tab details where they differ.

Branch: `feat/freecad-fcstd-tab` (10 commits on top of `main @ e912178`).
Plan: `docs/superpowers/plans/2026-09-17-freecad-fcstd-tab.md`.
Original research and implementation constraints are summarized in this report;
the temporary AI handoff files were removed after implementation.
Environment: Windows 11, Pixi env `.pixi/envs/default` (Python 3.11, PySide6 / Qt 6.10.2, FreeCAD 1.1.0 conda package), AMD GPU.

## 1. Baseline reconciliation

The handoff was written against `main @ 9a5989e`. `main` was at `e912178` when the branch was cut (19 commits later, all in the EMSolution.exe run backend and input-control editor). None of those commits touched `pyemsi/gui/__init__.py`, `pyemsi/widgets/split_container.py`, `pyemsi/gui/_viewers/_constants.py`, or the launch/close code paths, so the handoff's code descriptions still applied and no re-baselining of the design was needed.

The runtime facts in the handoff were re-verified live before coding (offscreen Qt, real FreeCAD 1.1.0): `FreeCADGui` exposes only `showMainWindow`/`embedToWindow`/`exec_loop`/`setupWithoutGUI` before the GUI exists; `getMainWindow()` returns a top-level PySide6 `QMainWindow`; `FreeCAD.openDocument` de-duplicates by path; `Gui.Document.Modified` is the dirty flag; `View3DInventorPy` has `fitAll()`/`viewAxonometric()`; the `.pyd` files live in `<prefix>/Library/bin`.

## 2. Changed files

| File | Change |
|---|---|
| `pyemsi/gui/__init__.py` | `_configure_graphics_policy()` (`QSG_RHI_BACKEND=opengl` via `setdefault`, `AA_ShareOpenGLContexts`) called first in `launch()` |
| `pyemsi/gui/freecad_runtime.py` | new: `FreeCADRuntimeError`, `freecad_search_paths`, `prepare_freecad_paths`, `FreeCADModules`, `import_freecad` (imports strictly from `sys.prefix`) |
| `pyemsi/gui/freecad_session.py` | new: `FreeCADDocumentError`, `normalize_document_path`, `FreeCADSession` (parking, attach/detach, open/activate/save, exit preparation, Report-view message listeners), `get_freecad_session`, `peek_freecad_session` |
| `pyemsi/gui/_viewers/_freecad.py` | new: `FreeCADViewer` disposable tab shell (`viewer_kind="freecad"`, `supports_panel_move=False`) |
| `pyemsi/gui/_viewers/_constants.py`, `pyemsi/gui/file_viewers.py` | `.fcstd` → `"freecad"` category; exports |
| `pyemsi/widgets/split_container.py` | `"freecad"` branch in `open_file()`, `_open_freecad_file`/`_find_freecad_viewer`, `freecad_session_initialized` signal, `supports_panel_move` honoured in the tab context menu |
| `pyemsi/gui/main_window.py` | `_confirm_freecad_documents()` Save/Discard/Cancel prompt and session exit preparation in `closeEvent`; `_attach_freecad_messages()` opens the "FreeCAD messages" log tab |
| `pyemsi/gui/external_terminal_dock.py` | `add_log_tab(title)` — process-free xterm tab |
| `pyemsi/widgets/xterm/_widget.py` | `XtermWidget.write(text)` — push text to xterm.js with CRLF line endings |
| `tests/test_gui_launch.py`, `tests/test_lazy_imports.py`, `tests/test_xterm_widget.py` | extended |
| `tests/test_freecad_runtime.py`, `tests/test_freecad_session.py`, `tests/test_freecad_viewer.py`, `tests/test_freecad_file_routing.py`, `tests/test_main_window_freecad.py`, `tests/test_freecad_session_integration.py`, `tests/test_external_terminal_dock.py` | new |
| `docs/superpowers/plans/2026-09-17-freecad-fcstd-tab.md` | the executed plan |

## 3. Architecture used

`launch()` first applies the graphics policy so Qt Quick / WebEngine compose through OpenGL, which is the only configuration in which a `QOpenGLWidget`-based FreeCAD view and the Monaco `QWebEngineView` coexist in one window on this machine. When the first `.FCStd` file is opened, `SplitContainer.open_file()` routes the `"freecad"` category to `_open_freecad_file()`, which asks the process singleton `FreeCADSession` to `ensure_initialized()`. The session imports `FreeCAD`/`FreeCADGui` lazily through `freecad_runtime` (active `sys.prefix` only), calls `showMainWindow()` once, re-parents the native FreeCAD `QMainWindow` into a hidden parking widget, waits for FreeCAD's deferred Start page, and hooks the Report view for message forwarding. A disposable `FreeCADViewer` shell is inserted as the leftmost tab of the primary panel and borrows the native window via `session.attach(shell)`; closing the tab detaches it back to parking, and the next `.FCStd` recreates a shell around the same live session and documents. Every further `.FCStd` becomes a FreeCAD document inside that one tab (`open_document` de-duplicates by normalized path, activates, fits, and raises the 3D view above the Start page). On exit, `PyEmsiMainWindow.closeEvent` prompts Save/Discard/Cancel per modified FreeCAD document, then detaches the native window so pyemsi's tab teardown never owns it. The session's Report-view hook feeds a "FreeCAD messages" tab in the External Terminal dock.

## 4. Tests added / passed

| File | Tests | Notes |
|---|---|---|
| `tests/test_gui_launch.py` | 9 (4 new) | graphics policy, call ordering |
| `tests/test_freecad_runtime.py` | 7 | search paths, idempotent DLL registration, prefix rejection, diagnostics |
| `tests/test_freecad_session.py` | 26 | fake FreeCAD API surface; parking, attach/detach cycles, open/activate/save, Modified reset, Start page settle, message listeners |
| `tests/test_freecad_viewer.py` | 4 | attach on construction, detach once on close/delete |
| `tests/test_freecad_file_routing.py` | 13 | singleton tab, reuse, leftmost insertion, runtime/document errors, context menu, `freecad_session_initialized` |
| `tests/test_main_window_freecad.py` | 9 | Save/Discard/Cancel prompt paths, message tab wiring and listener cleanup |
| `tests/test_external_terminal_dock.py` | 2 | `add_log_tab` |
| `tests/test_xterm_widget.py` | 4 (1 new) | `write()` CRLF handling |
| `tests/test_lazy_imports.py` | 5 | `FreeCAD`/`FreeCADGui` stay lazy on `import pyemsi.gui` |
| `tests/test_freecad_session_integration.py` | 1 | real FreeCAD, offscreen subprocess: init, open, de-dup, invalid file, 3 attach/detach cycles |

Targeted run: `pixi run pytest tests/test_freecad_*.py tests/test_main_window_freecad.py tests/test_external_terminal_dock.py tests/test_xterm_widget.py tests/test_gui_launch.py tests/test_lazy_imports.py` → all pass.

Full suite (`pixi run pytest tests --ignore=tests/test_femap_to_vtm.py --ignore=tests/test_gui_add_figure.py`): see the summary line recorded at the end of this section. The 20 failures present on `main` before this branch (EMSolution converter/GUI figure tests that depend on local assets) are unchanged; `tests/test_femap_to_vtm.py` and `tests/test_gui_add_figure.py` are excluded because they hang or need assets not in the repo, exactly as on `main`.

Full-suite summary line (2026-09-17, after the last commit): `20 failed, 426 passed, 1 warning in 76.49s`. The failures are in `tests/test_femap_parser.py` (15), `tests/test_plotter_deformation.py` (3), `tests/test_emsolution_output_plot_dialog.py` (1) and `tests/test_femap_converter_field_plot_cache.py` (1), none of which this branch touches.

## 5. Windows manual smoke results

Automated driver (scratch script, run under `pixi run python` with a real desktop `QApplication`, screenshots + "ink" pixel checks) plus the user's own manual session ("everything works well, I didn't notice any problems").

| # | Scenario | Result | Notes |
|---|---|---|---|
| 1 | Monaco only: open `.py`/`.txt` | PASS | text renders (must run under `pixi run python`; a bare interpreter leaves WebEngine views blank) |
| 2 | Monaco + FreeCAD: open `Box.FCStd` | PASS | tab "FreeCAD — Box.FCStd" leftmost, box visible, mouse rotate/zoom works, Monaco renders after switching back |
| 3 | Open `Cylinder.FCStd` | PASS | same tab reused, title updates, both documents in FreeCAD's tree |
| 4 | Re-open `Box.FCStd` | PASS | no duplicate document, Box activated |
| 5 | Close FreeCAD tab, open Monaco file, re-open `Box.FCStd` | PASS | after fix `0ac4cc0` (3D view was black before it): shell recreated, documents kept, view raised above Start page |
| 6 | Monaco + FreeCAD + VTK field tab | PASS | all three render when switching among them |
| 7 | Resize window/splitter, switch tabs 20× | PASS | no `D3D11`/`QOpenGLWidget` incompatibility messages with the policy on; FreeCAD and Monaco stay visible. A separate Monaco/VTK interaction that is independent of FreeCAD is tracked in `dev_docs/Monaco_VTK_rendering_issue.md` |
| 8 | Right-click FreeCAD tab | PASS | no "Move to Right Panel" action |
| 9 | Corrupt `bad.FCStd` | PASS | warning "Invalid project file", app and tabs keep working |
| 10 | Modify Box, File > Exit | PASS | prompt per document; Cancel keeps app open, Save writes file, Discard exits |
| 11 | 20× close/recreate tab, 20× alternate Box/Cylinder | PASS | one `FreeCADGui.getMainWindow()` object throughout, no crash, ~12 s first init with a brief top-level window flash |
| 12 | Exit codes at process teardown | RECORDED | see table below |

Exit codes (each row 3 runs, identical each time):

| Configuration | Exit code |
|---|---|
| Graphics policy ON, Monaco only (web-only control) | `0xC0000409` (-1073740791) |
| Graphics policy ON, Monaco + FreeCAD + VTK | `0xC0000409` (-1073740791) |
| Graphics policy OFF, Monaco only | `0` |
| Graphics policy OFF, Monaco + FreeCAD | hard crash mid-run, `-1073740771`; "The top-level window is not using OpenGL for composition, 'D3D11' is not compatible with QOpenGLWidget", "No valid GL context found!" |
| `AA_ShareOpenGLContexts` only, no `QSG_RHI_BACKEND` | FreeCAD view renders black |

The web-only control shows the `0xC0000409` teardown code is caused by the graphics policy plus Qt WebEngine on this driver, not by FreeCAD. Details and repro notes: `dev_docs/Monaco_VTK_rendering_issue.md`.

## 6. Deviations from the handoff and why

- **Re-parenting via `setParent`/`layout.addWidget`** instead of explicit window-flag juggling: `setParent` resets the flags to `Qt.Widget`, and attach/detach cycles proved stable this way.
- **Parking widget is a child of the pyemsi main window** (`_adopt_top_level`) rather than a free top-level widget, so FreeCAD's window never appears as a second top-level window in the taskbar and its native handle stays under the same top-level as WebEngine.
- **Start page settle + view raise**: FreeCAD 1.1 creates its Start page deferred; the session pumps the event loop briefly after init and, after each `open_document`, activates the document's MDI sub-window so the 3D view is not hidden under the Start page.
- **`Gui.Document.Modified` is reset after `save_document`**: FreeCAD leaves the flag set after `App.Document.save()`, which would re-prompt on exit.
- **`open_file` returns `None` on runtime failure** (after a critical message box) instead of raising, matching how the explorer double-click path treats other failures.
- **`supports_panel_move` opt-out attribute** on the viewer instead of a FreeCAD-specific check in `_TabPanel`.
- **pyemsi tab bars forced left-aligned.** FreeCAD's GUI init installs an application-wide stylesheet (`FreeCAD.qss`, ~70 KB, together with its own `QStyle`) that contains `QTabWidget::tab-bar { alignment: center; }`, which centred every pyemsi tab bar once a `.FCStd` was opened. `PyEmsiMainWindow` now sets `QTabWidget::tab-bar { alignment: left; }` on itself; widget-level rules win over the application stylesheet for all descendants (split panels, External Terminal tabs, dialogs parented to the window). Other FreeCAD.qss rules (buttons, frames, etc.) still apply to pyemsi widgets after FreeCAD init and were not overridden.
- **Report-view mirroring** (user request): FreeCAD 1.1 has no Python console observer, so the session listens to the Report view `QTextEdit` document and forwards inserted text verbatim to a "FreeCAD messages" xterm tab. Because FreeCAD redirects Python stdout/stderr into its Report view once the GUI exists, Python `print` output from pyemsi also shows up there after FreeCAD is initialised.
- **Smoke driver must run under Pixi** (`pixi run python`); noted so future smoke runs do not misreport blank Monaco tabs.

## 7. Unresolved issues / follow-ups

- **Graphics-policy side effects on Monaco/VTK** (`0xC0000409` at process exit, Monaco black after a resize while the VTK tab is current). Both reproduce without FreeCAD, so they are tracked outside this feature in `dev_docs/Monaco_VTK_rendering_issue.md`. Left as is per the handoff (no `os._exit`, no GPU toggles).
- **Initialisation flash**: `showMainWindow()` shows FreeCAD's top-level window for a moment before parking (~12 s first init on this machine). Accepted per handoff §9.1.
- **FreeCAD's Start page tab remains** inside the embedded MDI area; the opened document is raised above it but the Start page is not closed.
- **Redirected Python output** in the "FreeCAD messages" tab (see §6). Filtering by FreeCAD message type is not possible without a console observer.
- **Portable packaging is out of scope**: FreeCAD `.pyd`, Coin3D, OCCT, `Mod`/`Ext` are not handled by the private-runtime builder. This feature is **development/Pixi only**.
- **Optional viewer-only trimming** of the embedded FreeCAD GUI was not done (full GUI decision).

## 8. Current integration state (2026-09-18)

The current UI presents one pyemsi tab per `.FCStd` file while retaining one
FreeCAD engine and one native FreeCAD main window for the entire process. Each
outer tab is a lightweight shell. Selecting a tab moves the shared native window
into that shell and activates its already-open FreeCAD document. This preserves
the performance advantage of a single runtime without exposing FreeCAD's own MDI
document tabs, which are hidden after documents are opened.

Current user-visible behavior:

- FreeCAD files open with `FreeCAD.openDocument(path, False)` and remain loaded
  in the shared session.
- Each file has a separately named pyemsi tab showing only its filename.
- A modified FreeCAD document adds `*` to its pyemsi tab title and participates
  in pyemsi save handling.
- FreeCAD tabs suppress pyemsi's tab context menu so only FreeCAD's relevant
  context menus appear.
- Runtime and document loading are deferred through the Qt event loop. A tab
  displays an indeterminate loading page instead of freezing without feedback.
- Switching back to a loaded FreeCAD tab explicitly selects the shared native
  window in that tab's stacked layout; the old `Opening …` page cannot remain
  visible after the document has loaded.
- FreeCAD's Tasks dock defaults to the right, its status bar is visible, and the
  requested File and Part Design toolbars default to visible. These defaults are
  versioned in FreeCAD preferences and applied once, so later user choices are
  not overwritten.
- The FreeCAD messages terminal captures Report-view text, status messages,
  selected pyemsi debug logs, Python stdout/stderr, Qt messages, application and
  device details, and an offscreen VTK/OpenGL capability probe.
- Diagnostics are also written to the active workspace at
  `.pyemsi/freecad-diagnostics.log`, with a 5 MB limit and two backups. ANSI
  terminal colour codes are removed from the file.
- File > New FreeCAD Document and the main-toolbar button create an empty
  `.FCStd` file in the current workspace and open it through the same shared
  session.

Relevant follow-up commits:

- `957a3c3` — responsive per-document FreeCAD tabs
- `6bfe25d` — loaded-tab switching fix
- `d3e2c0c` — one-time layout defaults
- `0eb15fa` — diagnostics and rotating workspace log
- `72914f3` — New FreeCAD Document action

Focused verification after these changes:

```text
95 passed in 23.88s
```

The known Qt WebEngine/AMD shutdown issue remains independent of FreeCAD and is
documented in `dev_docs/Monaco_VTK_rendering_issue.md`.
