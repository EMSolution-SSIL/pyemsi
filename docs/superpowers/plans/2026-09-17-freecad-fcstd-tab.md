# FreeCAD `.FCStd` Tab Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **First action at execution time:** copy this file to `docs/superpowers/plans/2026-09-17-freecad-fcstd-tab.md` and create the feature branch `feat/freecad-fcstd-tab` from `main` (use `superpowers:using-git-worktrees`). Every task below ends in a commit on that branch.

**Goal:** Opening a `.FCStd` file from the pyemsi explorer (or `gui.open_file`) shows it inside one dedicated "FreeCAD" tab that embeds the real FreeCAD 1.1 GUI, reusing that tab and the single FreeCAD session for every further `.FCStd` file.

**Architecture:** Three new modules with one responsibility each. `pyemsi/gui/freecad_runtime.py` finds and imports FreeCAD strictly from the active `sys.prefix`. `pyemsi/gui/freecad_session.py` owns the process-wide FreeCAD GUI: it creates the native main window once, parks it in a hidden widget, attaches/detaches it to a host shell, and opens/activates/saves documents by normalized path. `pyemsi/gui/_viewers/_freecad.py` is a thin disposable `QWidget` shell (`FreeCADViewer`) that only borrows the native window from the session and gives it back in `closeEvent`. `SplitContainer.open_file()` routes the `"freecad"` category to a singleton open path above the per-file factory, and `PyEmsiMainWindow.closeEvent()` prompts Save/Discard/Cancel for modified FreeCAD documents before the normal tab close. Startup gains a graphics policy (`QSG_RHI_BACKEND=opengl` + `AA_ShareOpenGLContexts`) applied before `QApplication` exists, without which WebEngine goes black next to FreeCAD's OpenGL view.

**Tech Stack:** Python 3.11, PySide6 / Qt 6.10.2, FreeCAD 1.1.0 (conda-forge, already in the Pixi env), pytest (plain `QApplication([])` helper, no pytest-qt). Existing code reused: `_resolve_open_path`, `_TabPanel`, `SplitContainer.add_tab/focus_widget/_refresh_tab_title`, `FieldViewer` disposal pattern, `main_window` lazy-import globals pattern.

**Spec:** `dev_docs/FreeCAD dev/FreeCAD_Integration_Technical_Handoff.md` (source of truth) plus `dev_docs/FreeCAD dev/AI_Implementation_Directive.md`. User decisions taken on 2026-09-17: full FreeCAD GUI embedded (not trimmed); Save/Discard/Cancel prompt for modified documents on exit; FreeCAD tab cannot be moved to the right panel in v1.

## Context

The handoff was written against `main @ 9a5989e`. `main` is now at `e912178` (19 commits, all in the EMSolution.exe run backend and input-control editor). None of them touch `pyemsi/gui/__init__.py`, `split_container.py`, `_viewers/_constants.py`, or the close/launch code paths, so the handoff's code descriptions still match. The runtime API below was verified live in `.pixi/envs/default` (FreeCAD 1.1.0, PySide6 6.10.2, `QT_QPA_PLATFORM=offscreen`):

| Verified fact | Consequence for the plan |
|---|---|
| Before `showMainWindow()`, `FreeCADGui` exposes only `embedToWindow, exec_loop, setupWithoutGUI, showMainWindow` | Session must call `showMainWindow()` first; `getMainWindow` does not exist before that |
| `FreeCADGui.getMainWindow()` returns a `PySide6.QtWidgets.QMainWindow` (top-level, visible, parent `None`), and `QApplication.instance()` stays our own PySide6 app | Reparenting is plain `setParent`/`layout.addWidget`; no shiboken wrapping needed |
| `FreeCAD.openDocument(path)` returns the `App.Document`; opening the same path twice returns the same document and does not duplicate | Still compare `doc.FileName` ourselves (spec §9.4); FreeCAD returns forward-slash paths, so normalize with `normpath` + `normcase` |
| Invalid file → `OSError("Invalid project file")`; missing file → `OSError("File ... does not exist!")` | Wrap `openDocument` in `except Exception` → `FreeCADDocumentError` |
| `FreeCADGui.getDocument(name).Modified` is the dirty flag (False after open, True after edits); `App.Document.isSaved()` / `.FileName` / `.save()` exist | Exit prompt uses `Gui.Document.Modified`; save uses `App.Document.save()` and requires a `FileName` |
| `Gui.Document.ActiveView` is a `View3DInventorPy` with `fitAll()` and `viewAxonometric()` | Post-open fit uses those; `SendMsgToActiveView` is deprecated |
| `FreeCAD.pyd` / `FreeCADGui.pyd` live in `<prefix>/Library/bin`; `Mod`, `Ext`, `lib` under `<prefix>/Library` | Runtime search list; Pixi activation already puts `Library\bin` on `PYTHONPATH`, so `import FreeCAD` may work even before our path setup, but the packaged runtime will not |

## Global Constraints

- Python 3.11 / PySide6 / Qt6 / FreeCAD 1.1.0; do not downgrade or pin anything new in `pyproject.toml`.
- `QSG_RHI_BACKEND=opengl` via `os.environ.setdefault` and `QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)` before `QApplication` creation in `launch()`; never set `QT_OPENGL=software`, `--disable-gpu`, or ANGLE/Mesa overrides.
- Exactly one `FreeCADSession` per process (`get_freecad_session()`), one outer FreeCAD tab; multiple `.FCStd` files are FreeCAD documents inside it.
- The native FreeCAD main window is never `close()`d or `deleteLater()`d by tab code; it is parked in a hidden widget owned by the session.
- FreeCAD imports are lazy (inside functions) and resolved from `sys.prefix` only; `import pyemsi.gui` must not import `FreeCAD`/`FreeCADGui` (extend `tests/test_lazy_imports.py`).
- `.FCStd` routing is a branch inside `SplitContainer.open_file()`; the per-file `create_viewer` factory is not used for FreeCAD.
- Do not add `os._exit()`/force-kill; the known WebEngine/AMD `0xC0000409` teardown crash is tracked separately (§Known independent issue) and reported honestly.
- Scope is development/Pixi only; portable installer packaging is out of scope.
- Logging: `LOGGER = logging.getLogger(__name__)` per module; event messages from spec §18.
- Tests follow repo conventions: no conftest, no pytest-qt, each GUI test calls a module-level `_app()` helper that does `QApplication.instance() or QApplication([])`. Run the suite with `pixi run test`; a single file with `pixi run pytest tests/<file>.py -v`.

---

## File Structure

- `pyemsi/gui/__init__.py` — add `_configure_graphics_policy()` and call it first in `launch()` (modify). Test: `tests/test_gui_launch.py` (modify).
- `pyemsi/gui/freecad_runtime.py` — new pure module: `FreeCADRuntimeError`, `freecad_search_paths()`, `prepare_freecad_paths()`, `FreeCADModules`, `import_freecad()` (create). Test: `tests/test_freecad_runtime.py` (create).
- `pyemsi/gui/freecad_session.py` — new: `FreeCADDocumentError`, `normalize_document_path()`, `FreeCADSession`, `get_freecad_session()`, `peek_freecad_session()` (create). Test: `tests/test_freecad_session.py` (create).
- `pyemsi/gui/_viewers/_freecad.py` — new: `FreeCADViewer` shell (create). Test: `tests/test_freecad_viewer.py` (create).
- `pyemsi/gui/_viewers/_constants.py` — add `_FREECAD_EXTENSIONS = {".fcstd"}` → `"freecad"` (modify). `pyemsi/gui/file_viewers.py` — export `_FREECAD_EXTENSIONS`, `FreeCADViewer` (modify). Test: `tests/test_freecad_file_routing.py` (create).
- `pyemsi/widgets/split_container.py` — route `"freecad"` in `open_file()`, add `_open_freecad_file()`/`_find_freecad_viewer()`, honour `supports_panel_move` in `_TabPanel._show_context_menu` (modify). Test: `tests/test_freecad_file_routing.py`.
- `pyemsi/gui/main_window.py` — `_confirm_freecad_documents()` + session shutdown hook in `closeEvent()` (modify). Test: `tests/test_main_window_freecad.py` (create).
- `tests/test_lazy_imports.py` — watch `FreeCAD`, `FreeCADGui` (modify).
- `tests/test_freecad_session_integration.py` — subprocess, offscreen, real FreeCAD; skipped when FreeCAD is absent (create).
- `dev_docs/FreeCAD dev/IMPLEMENTATION_REPORT.md` — manual Windows smoke results and deviations (create, last task).

---

### Task 0: Baseline

**Files:** none modified.

- [ ] **Step 1: Create the branch and copy the plan**

```bash
git checkout -b feat/freecad-fcstd-tab main
mkdir -p docs/superpowers/plans
cp "C:/Users/eskandarih/.claude/plans/in-dev-docs-freecad-dev-i-async-heron.md" docs/superpowers/plans/2026-09-17-freecad-fcstd-tab.md
git add docs/superpowers/plans/2026-09-17-freecad-fcstd-tab.md
git commit -m "Add FreeCAD .FCStd tab implementation plan"
```

- [ ] **Step 2: Run the existing suite and record the result**

Run: `pixi run test`
Expected: all tests pass (record any pre-existing failures verbatim in the final report; do not fix them here).

---

### Task 1: Startup graphics policy

**Files:**
- Modify: `pyemsi/gui/__init__.py` (add helper above `_exec_app`, call at top of `launch()` before `from PySide6.QtWidgets import QApplication`)
- Test: `tests/test_gui_launch.py`

**Interfaces:**
- Produces: `pyemsi.gui._configure_graphics_policy(environ: MutableMapping[str, str] | None = None) -> None`. Idempotent. Called as the first statement of `launch()`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_gui_launch.py`:

```python
import os

from PySide6.QtCore import QCoreApplication, Qt


def test_configure_graphics_policy_defaults_rhi_backend_to_opengl():
    env: dict[str, str] = {}
    gui_module._configure_graphics_policy(env)
    assert env["QSG_RHI_BACKEND"] == "opengl"


def test_configure_graphics_policy_preserves_explicit_rhi_backend():
    env = {"QSG_RHI_BACKEND": "d3d11"}
    gui_module._configure_graphics_policy(env)
    assert env["QSG_RHI_BACKEND"] == "d3d11"


def test_configure_graphics_policy_requests_shared_opengl_contexts():
    gui_module._configure_graphics_policy({})
    assert QCoreApplication.testAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)


def test_launch_applies_graphics_policy_before_splash_and_window(monkeypatch):
    _ensure_app()
    call_log: list[str] = []

    def _mock_policy(environ=None):
        call_log.append("policy")

    def _mock_create_splash(app):
        call_log.append("splash")
        return _FakeSplash()

    class _RecordingWindow(_FakeWindow):
        def __init__(self, parent=None):
            super().__init__(parent)
            call_log.append("window")

    monkeypatch.setattr(gui_module, "_configure_graphics_policy", _mock_policy)
    monkeypatch.setattr(gui_module, "_create_splash", _mock_create_splash)
    monkeypatch.setattr(main_window_module, "PyEmsiMainWindow", _RecordingWindow)
    monkeypatch.setattr(gui_module, "_exec_app", lambda app: None)
    monkeypatch.setattr(gui_module, "_window", None)
    monkeypatch.setattr(gui_module, "_app", None)

    gui_module.launch()

    assert call_log[:3] == ["policy", "splash", "window"]
```

- [ ] **Step 2: Run to verify failure**

Run: `pixi run pytest tests/test_gui_launch.py -v`
Expected: the four new tests FAIL with `AttributeError: module 'pyemsi.gui' has no attribute '_configure_graphics_policy'`.

- [ ] **Step 3: Implement**

In `pyemsi/gui/__init__.py`, add above `_exec_app`:

```python
def _configure_graphics_policy(environ=None) -> None:
    """Align Qt Quick / WebEngine composition with FreeCAD's OpenGL view.

    Must run before ``QApplication`` exists. Validated on Windows/Qt 6.10:
    without ``QSG_RHI_BACKEND=opengl`` the Monaco WebEngine view renders
    black once a FreeCAD (QOpenGLWidget) view is shown in the same window,
    and ``AA_ShareOpenGLContexts`` alone is not sufficient. ``setdefault``
    keeps an explicit user/diagnostic override intact.
    """
    import os

    from PySide6.QtCore import QCoreApplication, Qt

    env = os.environ if environ is None else environ
    env.setdefault("QSG_RHI_BACKEND", "opengl")
    QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts, True)
```

In `launch()`, insert as the first statement after `global _window, _app`:

```python
    _configure_graphics_policy()
```

- [ ] **Step 4: Run tests**

Run: `pixi run pytest tests/test_gui_launch.py -v`
Expected: PASS (all, including the four pre-existing launch tests).

- [ ] **Step 5: Commit**

```bash
git add pyemsi/gui/__init__.py tests/test_gui_launch.py
git commit -m "Apply OpenGL graphics policy before QApplication creation"
```

---

### Task 2: FreeCAD runtime bootstrap

**Files:**
- Create: `pyemsi/gui/freecad_runtime.py`
- Test: `tests/test_freecad_runtime.py`

**Interfaces:**
- Produces:
  - `class FreeCADRuntimeError(RuntimeError)`
  - `freecad_search_paths(prefix: str | None = None) -> list[str]` — existing dirs among `Library/bin, Library/lib, Library/Ext, Library/Mod, lib, Ext, Mod` under `prefix` (default `sys.prefix`).
  - `prepare_freecad_paths(prefix=None, *, sys_path: list[str] | None = None, dll_adder=None) -> list[str]` — appends missing dirs to `sys_path` (default `sys.path`), registers `<prefix>/Library/bin` with `dll_adder` (default `os.add_dll_directory` when present) once per prefix, raises `FreeCADRuntimeError` when no dirs exist.
  - `@dataclass(frozen=True) class FreeCADModules: app: ModuleType; gui: ModuleType`
  - `import_freecad(prefix=None, *, importer=None, sys_path=None, dll_adder=None) -> FreeCADModules` — imports `FreeCAD` and `FreeCADGui` via `importer` (default `importlib.import_module`), rejects modules whose `__file__` is outside `prefix`.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_freecad_runtime.py`:

```python
from __future__ import annotations

import os
import types

import pytest

from pyemsi.gui import freecad_runtime


def _make_prefix(tmp_path, *subdirs):
    prefix = tmp_path / "env"
    for sub in subdirs:
        (prefix / sub).mkdir(parents=True)
    return str(prefix)


def _fake_module(name, file):
    mod = types.ModuleType(name)
    mod.__file__ = file
    return mod


def test_search_paths_only_returns_existing_dirs_inside_prefix(tmp_path):
    prefix = _make_prefix(tmp_path, "Library/bin", "Library/Mod")

    paths = freecad_runtime.freecad_search_paths(prefix)

    assert paths == [
        os.path.normpath(os.path.join(prefix, "Library", "bin")),
        os.path.normpath(os.path.join(prefix, "Library", "Mod")),
    ]
    assert all(p.startswith(prefix) for p in paths)


def test_search_paths_defaults_to_sys_prefix(monkeypatch, tmp_path):
    prefix = _make_prefix(tmp_path, "Library/bin")
    monkeypatch.setattr(freecad_runtime.sys, "prefix", prefix)

    assert freecad_runtime.freecad_search_paths() == [os.path.normpath(os.path.join(prefix, "Library", "bin"))]


def test_prepare_paths_is_idempotent_and_registers_dll_dir_once(tmp_path, monkeypatch):
    prefix = _make_prefix(tmp_path, "Library/bin", "Library/Mod")
    monkeypatch.setattr(freecad_runtime, "_prepared_prefixes", set())
    monkeypatch.setattr(freecad_runtime, "_dll_handles", [])
    sys_path: list[str] = ["already"]
    dll_calls: list[str] = []

    first = freecad_runtime.prepare_freecad_paths(prefix, sys_path=sys_path, dll_adder=dll_calls.append)
    second = freecad_runtime.prepare_freecad_paths(prefix, sys_path=sys_path, dll_adder=dll_calls.append)

    assert first == second
    assert sys_path == ["already", *first]
    assert dll_calls == [os.path.normpath(os.path.join(prefix, "Library", "bin"))]


def test_prepare_paths_raises_clear_error_when_no_freecad_dirs(tmp_path):
    prefix = _make_prefix(tmp_path)

    with pytest.raises(freecad_runtime.FreeCADRuntimeError) as excinfo:
        freecad_runtime.prepare_freecad_paths(prefix, sys_path=[], dll_adder=lambda p: None)

    message = str(excinfo.value)
    assert "FreeCAD could not be initialized" in message
    assert prefix in message


def test_import_freecad_returns_modules_from_active_prefix(tmp_path, monkeypatch):
    prefix = _make_prefix(tmp_path, "Library/bin")
    monkeypatch.setattr(freecad_runtime, "_prepared_prefixes", set())
    bin_dir = os.path.join(prefix, "Library", "bin")
    modules = {
        "FreeCAD": _fake_module("FreeCAD", os.path.join(bin_dir, "FreeCAD.pyd")),
        "FreeCADGui": _fake_module("FreeCADGui", os.path.join(bin_dir, "FreeCADGui.pyd")),
    }

    result = freecad_runtime.import_freecad(prefix, importer=modules.__getitem__, sys_path=[], dll_adder=lambda p: None)

    assert result.app is modules["FreeCAD"]
    assert result.gui is modules["FreeCADGui"]


def test_import_freecad_reports_missing_module_with_diagnostics(tmp_path, monkeypatch):
    prefix = _make_prefix(tmp_path, "Library/bin")
    monkeypatch.setattr(freecad_runtime, "_prepared_prefixes", set())

    def _importer(name):
        raise ModuleNotFoundError(f"No module named '{name}'")

    with pytest.raises(freecad_runtime.FreeCADRuntimeError) as excinfo:
        freecad_runtime.import_freecad(prefix, importer=_importer, sys_path=[], dll_adder=lambda p: None)

    message = str(excinfo.value)
    assert "No module named 'FreeCAD'" in message
    assert freecad_runtime.sys.executable in message
    assert os.path.join("Library", "bin") in message


def test_import_freecad_rejects_module_outside_prefix(tmp_path, monkeypatch):
    prefix = _make_prefix(tmp_path, "Library/bin")
    monkeypatch.setattr(freecad_runtime, "_prepared_prefixes", set())
    elsewhere = str(tmp_path / "other" / "FreeCAD.pyd")
    modules = {
        "FreeCAD": _fake_module("FreeCAD", elsewhere),
        "FreeCADGui": _fake_module("FreeCADGui", elsewhere),
    }

    with pytest.raises(freecad_runtime.FreeCADRuntimeError) as excinfo:
        freecad_runtime.import_freecad(prefix, importer=modules.__getitem__, sys_path=[], dll_adder=lambda p: None)

    assert "outside the active environment" in str(excinfo.value)
```

- [ ] **Step 2: Run to verify failure**

Run: `pixi run pytest tests/test_freecad_runtime.py -v`
Expected: FAIL at import with `ModuleNotFoundError: No module named 'pyemsi.gui.freecad_runtime'`.

- [ ] **Step 3: Implement**

Create `pyemsi/gui/freecad_runtime.py`:

```python
"""Locate and import FreeCAD strictly from the active Python environment.

FreeCAD's Python modules in a conda/Pixi environment live under
``<sys.prefix>/Library/bin`` (Windows) with workbenches under ``Library/Mod``
and ``Library/Ext``. This module adds those directories to ``sys.path`` once,
registers the DLL directory on Windows, imports ``FreeCAD``/``FreeCADGui``
lazily and refuses modules that resolve outside the active prefix. It never
searches system-wide FreeCAD installations.
"""

from __future__ import annotations

import importlib
import logging
import os
import sys
from dataclasses import dataclass
from types import ModuleType
from typing import Callable

LOGGER = logging.getLogger(__name__)


class FreeCADRuntimeError(RuntimeError):
    """FreeCAD could not be located or imported from the active environment."""


_CANDIDATE_SUBDIRS: tuple[str, ...] = (
    os.path.join("Library", "bin"),
    os.path.join("Library", "lib"),
    os.path.join("Library", "Ext"),
    os.path.join("Library", "Mod"),
    "lib",
    "Ext",
    "Mod",
)

# Module state so path/DLL setup happens once per prefix per process.
_prepared_prefixes: set[str] = set()
_dll_handles: list[object] = []


def _normalize_prefix(prefix: str | None) -> str:
    return os.path.normcase(os.path.abspath(prefix or sys.prefix))


def freecad_search_paths(prefix: str | None = None) -> list[str]:
    """Return the existing FreeCAD directories under *prefix* (default ``sys.prefix``)."""
    base = os.path.abspath(prefix or sys.prefix)
    found: list[str] = []
    for sub in _CANDIDATE_SUBDIRS:
        candidate = os.path.normpath(os.path.join(base, sub))
        if os.path.isdir(candidate):
            found.append(candidate)
    return found


def _describe_failure(prefix: str, paths: list[str], reason: str) -> str:
    searched = ", ".join(paths) if paths else "(no FreeCAD directories found under the prefix)"
    return "\n".join(
        [
            "FreeCAD could not be initialized in the active pyemsi environment.",
            f"Reason: {reason}",
            f"Python executable: {sys.executable}",
            f"Environment prefix: {prefix}",
            f"Searched: {searched}",
        ]
    )


def prepare_freecad_paths(
    prefix: str | None = None,
    *,
    sys_path: list[str] | None = None,
    dll_adder: Callable[[str], object] | None = None,
) -> list[str]:
    """Make FreeCAD importable from *prefix*. Idempotent; returns the directories used."""
    norm_prefix = _normalize_prefix(prefix)
    target_path = sys.path if sys_path is None else sys_path
    paths = freecad_search_paths(norm_prefix)
    if not paths:
        raise FreeCADRuntimeError(_describe_failure(norm_prefix, paths, "no FreeCAD directories exist in this environment"))

    for directory in paths:
        if directory not in target_path:
            target_path.append(directory)

    if norm_prefix not in _prepared_prefixes:
        adder = dll_adder if dll_adder is not None else getattr(os, "add_dll_directory", None)
        bin_dir = os.path.normpath(os.path.join(norm_prefix, "Library", "bin"))
        if adder is not None and os.path.isdir(bin_dir):
            _dll_handles.append(adder(bin_dir))
        _prepared_prefixes.add(norm_prefix)
    return paths


@dataclass(frozen=True)
class FreeCADModules:
    """The two FreeCAD entry modules needed by the session."""

    app: ModuleType
    gui: ModuleType


def _is_within(path: str, prefix: str) -> bool:
    try:
        return os.path.commonpath([os.path.normcase(os.path.abspath(path)), prefix]) == prefix
    except ValueError:  # different drives on Windows
        return False


def import_freecad(
    prefix: str | None = None,
    *,
    importer: Callable[[str], ModuleType] | None = None,
    sys_path: list[str] | None = None,
    dll_adder: Callable[[str], object] | None = None,
) -> FreeCADModules:
    """Import ``FreeCAD`` and ``FreeCADGui`` from *prefix* or raise :class:`FreeCADRuntimeError`."""
    norm_prefix = _normalize_prefix(prefix)
    do_import = importer or importlib.import_module
    LOGGER.info("FreeCAD runtime bootstrap started (prefix=%s)", norm_prefix)
    paths = prepare_freecad_paths(norm_prefix, sys_path=sys_path, dll_adder=dll_adder)

    try:
        app = do_import("FreeCAD")
        gui = do_import("FreeCADGui")
    except ImportError as exc:
        LOGGER.error("FreeCAD import failed: %s", exc)
        raise FreeCADRuntimeError(_describe_failure(norm_prefix, paths, f"{type(exc).__name__}: {exc}")) from exc

    for module in (app, gui):
        origin = getattr(module, "__file__", None)
        if origin is None or not _is_within(origin, norm_prefix):
            reason = f"{module.__name__} resolved outside the active environment: {origin}"
            LOGGER.error(reason)
            raise FreeCADRuntimeError(_describe_failure(norm_prefix, paths, reason))
        LOGGER.debug("%s imported from %s", module.__name__, origin)

    LOGGER.info("FreeCAD runtime bootstrap complete")
    return FreeCADModules(app=app, gui=gui)
```

- [ ] **Step 4: Run tests**

Run: `pixi run pytest tests/test_freecad_runtime.py -v`
Expected: PASS (7 tests).

- [ ] **Step 5: Commit**

```bash
git add pyemsi/gui/freecad_runtime.py tests/test_freecad_runtime.py
git commit -m "Add FreeCAD runtime bootstrap scoped to the active environment"
```

---

### Task 3: FreeCADSession

**Files:**
- Create: `pyemsi/gui/freecad_session.py`
- Test: `tests/test_freecad_session.py`

**Interfaces:**
- Consumes: `FreeCADModules`, `FreeCADRuntimeError`, `import_freecad` from Task 2.
- Produces:
  - `class FreeCADDocumentError(RuntimeError)`
  - `normalize_document_path(path: str) -> str` (abspath + normpath + normcase)
  - `class FreeCADSession(loader: Callable[[], FreeCADModules] | None = None)` with `is_initialized: bool`, `main_window: QWidget | None`, `attached_host: QWidget | None`, `ensure_initialized() -> None`, `attach(host: QWidget) -> None`, `detach(host: QWidget | None = None) -> None`, `find_document(path) -> object | None`, `is_document_open(path) -> bool`, `open_document(path: str) -> str` (returns FreeCAD document `Name`), `modified_documents() -> list[tuple[str, str]]` (`(Name, FileName)`), `save_document(name: str) -> None`, `prepare_for_application_exit() -> None`.
  - `get_freecad_session() -> FreeCADSession` (process singleton), `peek_freecad_session() -> FreeCADSession | None` (no creation).

- [ ] **Step 1: Write the failing tests**

Create `tests/test_freecad_session.py`:

```python
from __future__ import annotations

import os
import types

import pytest
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from pyemsi.gui import freecad_session as session_module
from pyemsi.gui.freecad_runtime import FreeCADModules, FreeCADRuntimeError


def _app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class _FakeView:
    def __init__(self):
        self.calls: list[str] = []

    def fitAll(self):  # noqa: N802
        self.calls.append("fitAll")

    def viewAxonometric(self):  # noqa: N802
        self.calls.append("viewAxonometric")


class _FakeAppDoc:
    def __init__(self, name, file_name):
        self.Name = name
        self.Label = name
        self.FileName = file_name
        self.saved = 0

    def save(self):
        if not self.FileName:
            raise RuntimeError("no file name")
        self.saved += 1


class _FakeGuiDoc:
    def __init__(self, modified=False):
        self.Modified = modified
        self.ActiveView = _FakeView()


class _FakeFreeCAD:
    """Stands in for FreeCAD (App) + FreeCADGui with the verified 1.1 API surface."""

    def __init__(self, *, open_error=None):
        self.app = types.SimpleNamespace()
        self.gui = types.SimpleNamespace()
        self._docs: dict[str, _FakeAppDoc] = {}
        self._gui_docs: dict[str, _FakeGuiDoc] = {}
        self.active: list[str] = []
        self.show_main_window_calls = 0
        self.open_error = open_error
        self.main_window = QMainWindow()
        self.main_window.show()

        self.app.listDocuments = lambda: dict(self._docs)
        self.app.getDocument = lambda name: self._docs[name]
        self.app.openDocument = self._open
        self.app.setActiveDocument = lambda name: self.active.append(("app", name))
        self.gui.showMainWindow = self._show_main_window
        self.gui.getMainWindow = lambda: self.main_window
        self.gui.getDocument = lambda name: self._gui_docs[name]
        self.gui.setActiveDocument = lambda name: self.active.append(("gui", name))

    def _show_main_window(self):
        self.show_main_window_calls += 1

    def _open(self, path):
        if self.open_error is not None:
            raise self.open_error
        name = os.path.splitext(os.path.basename(path))[0]
        doc = _FakeAppDoc(name, path.replace("\\", "/"))  # FreeCAD reports forward slashes
        self._docs[name] = doc
        self._gui_docs[name] = _FakeGuiDoc()
        return doc

    def modules(self) -> FreeCADModules:
        return FreeCADModules(app=self.app, gui=self.gui)


def _host() -> QWidget:
    host = QWidget()
    layout = QVBoxLayout(host)
    layout.setContentsMargins(0, 0, 0, 0)
    return host


def test_normalize_document_path_matches_freecad_forward_slash_paths(tmp_path):
    original = str(tmp_path / "Motor.FCStd")
    from_freecad = original.replace("\\", "/")
    assert session_module.normalize_document_path(original) == session_module.normalize_document_path(from_freecad)


def test_ensure_initialized_is_idempotent_and_parks_native_window():
    _app()
    fake = _FakeFreeCAD()
    session = session_module.FreeCADSession(loader=fake.modules)

    session.ensure_initialized()
    session.ensure_initialized()

    assert fake.show_main_window_calls == 1
    assert session.is_initialized
    assert session.main_window is fake.main_window
    assert not fake.main_window.isVisible()
    assert fake.main_window.parent() is not None  # parked, not top-level


def test_ensure_initialized_wraps_loader_failure():
    _app()

    def _boom():
        raise FreeCADRuntimeError("nope")

    session = session_module.FreeCADSession(loader=_boom)
    with pytest.raises(FreeCADRuntimeError):
        session.ensure_initialized()
    assert not session.is_initialized


def test_attach_and_detach_move_native_window_between_host_and_parking():
    _app()
    fake = _FakeFreeCAD()
    session = session_module.FreeCADSession(loader=fake.modules)
    session.ensure_initialized()
    host = _host()

    session.attach(host)
    assert fake.main_window.parent() is host
    assert host.layout().indexOf(fake.main_window) != -1
    assert session.attached_host is host

    session.detach(host)
    assert fake.main_window.parent() is not host
    assert not fake.main_window.isVisible()
    assert session.attached_host is None
    assert fake.main_window.parent() is not None  # back in parking


def test_detach_ignores_foreign_host_and_repeated_calls():
    _app()
    fake = _FakeFreeCAD()
    session = session_module.FreeCADSession(loader=fake.modules)
    session.ensure_initialized()
    host, other = _host(), _host()
    session.attach(host)

    session.detach(other)
    assert session.attached_host is host

    session.detach()
    session.detach()  # must not raise
    assert session.attached_host is None


def test_reattach_after_detach_reuses_same_native_window():
    _app()
    fake = _FakeFreeCAD()
    session = session_module.FreeCADSession(loader=fake.modules)
    session.ensure_initialized()
    for _ in range(3):
        host = _host()
        session.attach(host)
        assert fake.main_window.parent() is host
        session.detach(host)
    assert fake.show_main_window_calls == 1


def test_open_document_opens_activates_and_fits_new_document(tmp_path):
    _app()
    fake = _FakeFreeCAD()
    session = session_module.FreeCADSession(loader=fake.modules)
    session.ensure_initialized()
    path = str(tmp_path / "Motor.FCStd")

    name = session.open_document(path)

    assert name == "Motor"
    assert fake.active == [("app", "Motor"), ("gui", "Motor")]
    assert fake._gui_docs["Motor"].ActiveView.calls == ["viewAxonometric", "fitAll"]
    assert session.is_document_open(path)


def test_open_document_activates_existing_document_instead_of_duplicating(tmp_path):
    _app()
    fake = _FakeFreeCAD()
    session = session_module.FreeCADSession(loader=fake.modules)
    session.ensure_initialized()
    path = str(tmp_path / "Motor.FCStd")
    session.open_document(path)
    open_calls: list[str] = []
    fake.app.openDocument = lambda p: open_calls.append(p)

    name = session.open_document(path.upper() if os.name == "nt" else path)

    assert name == "Motor"
    assert open_calls == []
    assert fake._gui_docs["Motor"].ActiveView.calls == ["viewAxonometric", "fitAll", "fitAll"]


def test_open_document_wraps_freecad_errors(tmp_path):
    _app()
    fake = _FakeFreeCAD(open_error=OSError("Invalid project file"))
    session = session_module.FreeCADSession(loader=fake.modules)
    session.ensure_initialized()

    with pytest.raises(session_module.FreeCADDocumentError) as excinfo:
        session.open_document(str(tmp_path / "bad.FCStd"))

    assert "Invalid project file" in str(excinfo.value)
    assert "bad.FCStd" in str(excinfo.value)
    assert session.is_initialized  # session survives a bad file


def test_open_document_requires_initialization(tmp_path):
    session = session_module.FreeCADSession(loader=lambda: None)
    with pytest.raises(FreeCADRuntimeError):
        session.open_document(str(tmp_path / "x.FCStd"))


def test_modified_documents_reports_only_dirty_docs(tmp_path):
    _app()
    fake = _FakeFreeCAD()
    session = session_module.FreeCADSession(loader=fake.modules)
    session.ensure_initialized()
    a = str(tmp_path / "A.FCStd")
    b = str(tmp_path / "B.FCStd")
    session.open_document(a)
    session.open_document(b)
    fake._gui_docs["B"].Modified = True

    assert session.modified_documents() == [("B", b.replace("\\", "/"))]


def test_modified_documents_is_empty_before_initialization():
    session = session_module.FreeCADSession(loader=lambda: None)
    assert session.modified_documents() == []


def test_save_document_calls_freecad_save(tmp_path):
    _app()
    fake = _FakeFreeCAD()
    session = session_module.FreeCADSession(loader=fake.modules)
    session.ensure_initialized()
    session.open_document(str(tmp_path / "A.FCStd"))

    session.save_document("A")

    assert fake._docs["A"].saved == 1


def test_save_document_refuses_unnamed_document():
    _app()
    fake = _FakeFreeCAD()
    session = session_module.FreeCADSession(loader=fake.modules)
    session.ensure_initialized()
    fake._docs["Unnamed"] = _FakeAppDoc("Unnamed", "")
    fake._gui_docs["Unnamed"] = _FakeGuiDoc(modified=True)

    with pytest.raises(session_module.FreeCADDocumentError):
        session.save_document("Unnamed")


def test_prepare_for_application_exit_detaches():
    _app()
    fake = _FakeFreeCAD()
    session = session_module.FreeCADSession(loader=fake.modules)
    session.ensure_initialized()
    session.attach(_host())

    session.prepare_for_application_exit()

    assert session.attached_host is None


def test_get_freecad_session_is_a_process_singleton(monkeypatch):
    monkeypatch.setattr(session_module, "_SESSION", None)
    assert session_module.peek_freecad_session() is None
    first = session_module.get_freecad_session()
    assert session_module.get_freecad_session() is first
    assert session_module.peek_freecad_session() is first
```

- [ ] **Step 2: Run to verify failure**

Run: `pixi run pytest tests/test_freecad_session.py -v`
Expected: FAIL at import with `ModuleNotFoundError: No module named 'pyemsi.gui.freecad_session'`.

- [ ] **Step 3: Implement**

Create `pyemsi/gui/freecad_session.py`:

```python
"""Process-wide FreeCAD GUI session shared by every FreeCADViewer shell.

The FreeCAD GUI is a singleton native main window. This session creates it
once, keeps it alive in a hidden *parking* widget while no pyemsi tab shows
it, and lends it to at most one host widget at a time. Tab shells come and
go; the native window and the open documents persist for the process.
"""

from __future__ import annotations

import logging
import os
from typing import Callable

from PySide6.QtWidgets import QApplication, QWidget

from pyemsi.gui.freecad_runtime import FreeCADModules, FreeCADRuntimeError, import_freecad

LOGGER = logging.getLogger(__name__)


class FreeCADDocumentError(RuntimeError):
    """A FreeCAD document could not be opened or saved."""


def normalize_document_path(path: str) -> str:
    """Canonical form for comparing document paths (FreeCAD reports forward slashes)."""
    return os.path.normcase(os.path.abspath(os.path.normpath(path)))


class FreeCADSession:
    """Owns the native FreeCAD main window and the document open/activate logic."""

    def __init__(self, loader: Callable[[], FreeCADModules] | None = None) -> None:
        self._loader = loader or import_freecad
        self._modules: FreeCADModules | None = None
        self._main_window: QWidget | None = None
        self._parking: QWidget | None = None
        self._host: QWidget | None = None

    # ------------------------------------------------------------------
    # state
    # ------------------------------------------------------------------

    @property
    def is_initialized(self) -> bool:
        return self._main_window is not None

    @property
    def main_window(self) -> QWidget | None:
        return self._main_window

    @property
    def attached_host(self) -> QWidget | None:
        return self._host

    def _require_initialized(self) -> FreeCADModules:
        if self._modules is None or self._main_window is None:
            raise FreeCADRuntimeError("FreeCAD session is not initialized; call ensure_initialized() first.")
        return self._modules

    # ------------------------------------------------------------------
    # lifecycle
    # ------------------------------------------------------------------

    def ensure_initialized(self) -> None:
        """Import FreeCAD, create the native main window once and park it hidden."""
        if self._main_window is not None:
            return
        if QApplication.instance() is None:
            raise FreeCADRuntimeError("A QApplication must exist before the FreeCAD GUI can be initialized.")

        modules = self._loader()
        LOGGER.info("FreeCAD GUI initialization started")
        # showMainWindow() is the only way to create the GUI singleton in
        # FreeCAD 1.1; it briefly shows a top-level window (known flash).
        modules.gui.showMainWindow()
        main_window = modules.gui.getMainWindow()

        parking = QWidget()
        parking.setObjectName("freecad_parking")
        parking.hide()

        self._modules = modules
        self._main_window = main_window
        self._parking = parking
        self._park()
        LOGGER.info("FreeCAD GUI initialization complete")

    def _park(self) -> None:
        assert self._main_window is not None and self._parking is not None
        self._main_window.hide()
        self._main_window.setParent(self._parking)  # resets window flags to Qt.Widget
        LOGGER.info("FreeCAD native window parked")

    def attach(self, host: QWidget) -> None:
        """Show the native window inside *host* (which must own a layout)."""
        self._require_initialized()
        if self._host is host:
            return
        if self._host is not None:
            self.detach()
        layout = host.layout()
        if layout is None:
            raise ValueError("FreeCADSession.attach() requires a host widget with a layout")
        layout.addWidget(self._main_window)  # reparents into host
        self._main_window.show()
        self._host = host
        LOGGER.info("FreeCAD native window attached")

    def detach(self, host: QWidget | None = None) -> None:
        """Return the native window to parking. No-op if not attached (or attached elsewhere)."""
        if self._main_window is None or self._host is None:
            return
        if host is not None and host is not self._host:
            return
        try:
            layout = self._host.layout()
            if layout is not None:
                layout.removeWidget(self._main_window)
        except RuntimeError:
            # Host's C++ object is already gone (detach reached via QObject.destroyed).
            LOGGER.warning("FreeCAD host shell was destroyed before detach; re-parking native window")
        self._host = None
        self._park()

    def prepare_for_application_exit(self) -> None:
        """Detach from any shell so pyemsi's tab teardown never owns the native window."""
        LOGGER.info("FreeCAD application-shutdown preparation")
        self.detach()

    # ------------------------------------------------------------------
    # documents
    # ------------------------------------------------------------------

    def _documents(self) -> list:
        modules = self._require_initialized()
        return list(modules.app.listDocuments().values())

    def find_document(self, path: str):
        """Return the open FreeCAD document stored at *path*, or ``None``."""
        target = normalize_document_path(path)
        for doc in self._documents():
            file_name = getattr(doc, "FileName", "") or ""
            if file_name and normalize_document_path(file_name) == target:
                return doc
        return None

    def is_document_open(self, path: str) -> bool:
        return self.find_document(path) is not None

    def open_document(self, path: str) -> str:
        """Open *path* (or activate it if already open), fit the view, return the document name."""
        modules = self._require_initialized()
        norm_path = os.path.abspath(os.path.normpath(path))
        LOGGER.info("FreeCAD document open requested: %s", norm_path)

        doc = self.find_document(norm_path)
        newly_opened = doc is None
        if newly_opened:
            try:
                doc = modules.app.openDocument(norm_path)
            except Exception as exc:  # FreeCAD raises OSError / Base.FreeCADError
                LOGGER.error("FreeCAD could not open %s: %s", norm_path, exc)
                raise FreeCADDocumentError(f"FreeCAD could not open {norm_path}:\n{exc}") from exc

        modules.app.setActiveDocument(doc.Name)
        modules.gui.setActiveDocument(doc.Name)

        view = self._active_view(doc.Name)
        if view is not None:
            if newly_opened and hasattr(view, "viewAxonometric"):
                view.viewAxonometric()
            if hasattr(view, "fitAll"):
                view.fitAll()
        LOGGER.info("FreeCAD document activated: %s", norm_path)
        return doc.Name

    def _active_view(self, name: str):
        modules = self._require_initialized()
        try:
            gui_doc = modules.gui.getDocument(name)
        except Exception:
            return None
        return getattr(gui_doc, "ActiveView", None)

    def modified_documents(self) -> list[tuple[str, str]]:
        """Return ``(Name, FileName)`` for every document whose GUI ``Modified`` flag is set."""
        if self._modules is None:
            return []
        result: list[tuple[str, str]] = []
        for doc in self._documents():
            try:
                gui_doc = self._modules.gui.getDocument(doc.Name)
            except Exception:
                continue
            if getattr(gui_doc, "Modified", False):
                result.append((doc.Name, getattr(doc, "FileName", "") or ""))
        return result

    def save_document(self, name: str) -> None:
        """Save document *name* to its existing FileName."""
        modules = self._require_initialized()
        doc = modules.app.getDocument(name)
        if not (getattr(doc, "FileName", "") or ""):
            raise FreeCADDocumentError(
                f"FreeCAD document '{doc.Label}' has never been saved. Use FreeCAD's File > Save As inside the FreeCAD tab first."
            )
        try:
            doc.save()
        except Exception as exc:
            raise FreeCADDocumentError(f"Could not save {doc.FileName}:\n{exc}") from exc


# ----------------------------------------------------------------------
# process singleton
# ----------------------------------------------------------------------

_SESSION: FreeCADSession | None = None


def get_freecad_session() -> FreeCADSession:
    """Return the process-wide session, creating it (uninitialized) on first use."""
    global _SESSION
    if _SESSION is None:
        _SESSION = FreeCADSession()
    return _SESSION


def peek_freecad_session() -> FreeCADSession | None:
    """Return the session if one was ever created, without creating it."""
    return _SESSION
```

- [ ] **Step 4: Run tests**

Run: `pixi run pytest tests/test_freecad_session.py -v`
Expected: PASS (16 tests).

- [ ] **Step 5: Commit**

```bash
git add pyemsi/gui/freecad_session.py tests/test_freecad_session.py
git commit -m "Add FreeCADSession owning the parked native FreeCAD window"
```

---

### Task 4: FreeCADViewer shell

**Files:**
- Create: `pyemsi/gui/_viewers/_freecad.py`
- Modify: `pyemsi/gui/file_viewers.py` (import + `__all__`)
- Test: `tests/test_freecad_viewer.py`

**Interfaces:**
- Consumes: `FreeCADSession.attach/detach/open_document` from Task 3.
- Produces: `class FreeCADViewer(QWidget)` with class attributes `viewer_kind = "freecad"`, `supports_panel_move = False`; `__init__(session, parent=None)` (calls `session.attach(self)`); `session` property; `current_path: str | None` property; `open_file(path: str) -> str`; `closeEvent` detaches before base close; `destroyed` guard against double detach. No `dirty`/`save` API (so `_TabPanel._close_tab` never prompts for it).

**Lifecycle invariant (why closeEvent is the real guard):** Qt deletes a widget's children *before* emitting `destroyed`, so the `destroyed` fallback cannot rescue the native window once the shell is being torn down. The guarantee comes from `_TabPanel._close_tab` (`split_container.py:114-117`), the only deletion path in the container, which calls `widget.close()` before `widget.deleteLater()`. Task 5's `test_closing_freecad_tab_detaches_before_shell_deletion` pins that ordering; if anyone later adds a removal path that skips `close()`, that test must be extended to cover it.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_freecad_viewer.py`:

```python
from __future__ import annotations

import os

from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QApplication, QWidget

from pyemsi.gui._viewers._freecad import FreeCADViewer


def _app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class _RecordingSession:
    def __init__(self):
        self.events: list[tuple] = []

    def attach(self, host):
        self.events.append(("attach", host))

    def detach(self, host=None):
        self.events.append(("detach", host))

    def open_document(self, path):
        self.events.append(("open", path))
        return os.path.splitext(os.path.basename(path))[0]


def test_viewer_attaches_session_on_construction_and_has_zero_margin_layout():
    _app()
    session = _RecordingSession()

    viewer = FreeCADViewer(session)

    assert session.events == [("attach", viewer)]
    assert viewer.layout() is not None
    assert viewer.layout().contentsMargins().left() == 0
    assert viewer.viewer_kind == "freecad"
    assert viewer.supports_panel_move is False
    assert not hasattr(viewer, "dirty") and not hasattr(viewer, "save")


def test_open_file_delegates_to_session_and_records_normalized_path(tmp_path):
    _app()
    session = _RecordingSession()
    viewer = FreeCADViewer(session)
    raw = str(tmp_path / "sub" / ".." / "Motor.FCStd")

    name = viewer.open_file(raw)

    assert name == "Motor"
    assert session.events[-1] == ("open", os.path.abspath(os.path.normpath(raw)))
    assert viewer.current_path == os.path.abspath(os.path.normpath(raw))


def test_close_detaches_session_exactly_once():
    _app()
    session = _RecordingSession()
    viewer = FreeCADViewer(session)

    viewer.close()
    viewer.close()

    assert session.events == [("attach", viewer), ("detach", viewer)]


def test_delete_without_close_still_detaches_once():
    app = _app()
    session = _RecordingSession()
    viewer = FreeCADViewer(session)

    viewer.deleteLater()
    # processEvents() alone never runs deferred deletes outside a nested loop.
    app.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    app.processEvents()

    detaches = [e for e in session.events if e[0] == "detach"]
    assert len(detaches) == 1
```

- [ ] **Step 2: Run to verify failure**

Run: `pixi run pytest tests/test_freecad_viewer.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'pyemsi.gui._viewers._freecad'`.

- [ ] **Step 3: Implement**

Create `pyemsi/gui/_viewers/_freecad.py`:

```python
"""Disposable pyemsi tab shell that hosts the shared FreeCAD GUI."""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QVBoxLayout, QWidget

if TYPE_CHECKING:
    from pyemsi.gui.freecad_session import FreeCADSession

LOGGER = logging.getLogger(__name__)


class FreeCADViewer(QWidget):
    """Tab widget that borrows the native FreeCAD main window from a session.

    The shell is disposable: closing it hands the native window back to the
    session's parking widget. It never deletes the native window itself and
    deliberately exposes no ``dirty``/``save`` API; unsaved FreeCAD documents
    are handled by ``PyEmsiMainWindow`` at application exit.
    """

    viewer_kind = "freecad"
    supports_panel_move = False  # honoured by _TabPanel context menu

    def __init__(self, session: FreeCADSession, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._session = session
        self._current_path: str | None = None
        self._detached = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._session.attach(self)
        self.destroyed.connect(self._detach_session)

    @property
    def session(self) -> FreeCADSession:
        return self._session

    @property
    def current_path(self) -> str | None:
        """Last path opened through this shell (for tab title purposes)."""
        return self._current_path

    def open_file(self, path: str) -> str:
        """Open or activate *path* in the shared session; returns the FreeCAD document name."""
        norm_path = os.path.abspath(os.path.normpath(path))
        name = self._session.open_document(norm_path)
        self._current_path = norm_path
        return name

    def _detach_session(self, *_args) -> None:
        if self._detached:
            return
        self._detached = True
        LOGGER.info("FreeCAD viewer shell closing")
        self._session.detach(self)

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        self._detach_session()
        super().closeEvent(event)
```

In `pyemsi/gui/file_viewers.py`, add `from ._viewers._freecad import FreeCADViewer` after the `_field_viewer` import and `"FreeCADViewer",` to `__all__` after `"FieldViewer",`.

- [ ] **Step 4: Run tests**

Run: `pixi run pytest tests/test_freecad_viewer.py tests/test_lazy_imports.py -v`
Expected: PASS. (`_freecad.py` imports nothing FreeCAD-related, so `import pyemsi.gui` stays clean.)

- [ ] **Step 5: Commit**

```bash
git add pyemsi/gui/_viewers/_freecad.py pyemsi/gui/file_viewers.py tests/test_freecad_viewer.py
git commit -m "Add FreeCADViewer tab shell that borrows the session window"
```

---

### Task 5: `.FCStd` classification and singleton routing in SplitContainer

**Files:**
- Modify: `pyemsi/gui/_viewers/_constants.py` (add set + loop), `pyemsi/gui/file_viewers.py` (export `_FREECAD_EXTENSIONS`)
- Modify: `pyemsi/widgets/split_container.py` — `_TabPanel._show_context_menu` (lines 143-149), `SplitContainer.open_file` (lines 365-408), new `_open_freecad_file`/`_find_freecad_viewer` next to `_find_tab_by_path`
- Test: `tests/test_freecad_file_routing.py`

**Interfaces:**
- Consumes: `FreeCADViewer` (Task 4), `get_freecad_session`, `FreeCADRuntimeError`, `FreeCADDocumentError` (Tasks 2-3), all imported lazily inside `_open_freecad_file`.
- Produces: `_CATEGORY[".fcstd"] == "freecad"`; `SplitContainer.open_file()` returns the singleton `FreeCADViewer` for `.FCStd` paths, or `None` when the FreeCAD runtime cannot initialize (after a `QMessageBox.critical`); `SplitContainer._find_freecad_viewer() -> QWidget | None`; FreeCAD tab title `"FreeCAD — <basename>"`; the Move-to-panel action is hidden for widgets with `supports_panel_move = False`.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_freecad_file_routing.py`:

```python
from __future__ import annotations

import os

import pytest
from PySide6.QtCore import QPoint
from PySide6.QtWidgets import QApplication, QWidget

from pyemsi.gui import freecad_session as session_module
from pyemsi.gui._viewers._constants import _CATEGORY
from pyemsi.gui._viewers._freecad import FreeCADViewer
from pyemsi.gui.freecad_runtime import FreeCADRuntimeError
from pyemsi.widgets import split_container as split_container_module
from pyemsi.widgets.split_container import SplitContainer


def _app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class _FakeSession:
    def __init__(self, *, init_error=None, open_error=None):
        self.init_error = init_error
        self.open_error = open_error
        self.events: list[tuple] = []
        self.host = None

    @property
    def is_initialized(self):
        return any(e[0] == "init" for e in self.events)

    def ensure_initialized(self):
        if self.init_error is not None:
            raise self.init_error
        self.events.append(("init",))

    def attach(self, host):
        self.host = host
        self.events.append(("attach", host))

    def detach(self, host=None):
        self.host = None
        self.events.append(("detach", host))

    def open_document(self, path):
        if self.open_error is not None:
            raise self.open_error
        self.events.append(("open", path))
        return os.path.splitext(os.path.basename(path))[0]


@pytest.fixture
def fake_session(monkeypatch):
    session = _FakeSession()
    monkeypatch.setattr(session_module, "get_freecad_session", lambda: session)
    return session


def _open_calls(session):
    return [e[1] for e in session.events if e[0] == "open"]


def test_fcstd_extension_maps_to_freecad_category():
    assert _CATEGORY[".fcstd"] == "freecad"
    assert _CATEGORY[".py"] == "python"
    assert _CATEGORY[".png"] == "image"
    assert ".FCStd".lower() in _CATEGORY


def test_first_fcstd_creates_single_freecad_tab(fake_session, tmp_path):
    _app()
    container = SplitContainer()
    path = str(tmp_path / "Motor.FCStd")

    viewer = container.open_file(path)

    assert isinstance(viewer, FreeCADViewer)
    assert container.left_panel.count() == 1
    assert container.left_panel.tabText(0) == "FreeCAD — Motor.FCStd"
    assert fake_session.events[0] == ("init",)
    assert _open_calls(fake_session) == [os.path.abspath(os.path.normpath(path))]


def test_second_fcstd_reuses_tab_and_passes_new_path(fake_session, tmp_path):
    _app()
    container = SplitContainer()
    first = container.open_file(str(tmp_path / "A.FCStd"))
    other = QWidget()
    container.add_tab(other, "other")

    second = container.open_file(str(tmp_path / "b.fcstd"))

    assert second is first
    assert container.left_panel.count() == 2
    assert container.left_panel.currentWidget() is first
    assert container.left_panel.tabText(container.left_panel.indexOf(first)) == "FreeCAD — b.fcstd"
    assert [os.path.basename(p) for p in _open_calls(fake_session)] == ["A.FCStd", "b.fcstd"]


def test_reopening_same_path_does_not_add_tab(fake_session, tmp_path):
    _app()
    container = SplitContainer()
    path = str(tmp_path / "A.FCStd")
    container.open_file(path)
    container.open_file(path)
    assert container.left_panel.count() == 1
    assert len(_open_calls(fake_session)) == 2  # session decides activate-vs-open


def test_closing_freecad_tab_detaches_before_shell_deletion(fake_session, tmp_path):
    app = _app()
    container = SplitContainer()
    viewer = container.open_file(str(tmp_path / "A.FCStd"))

    assert container.left_panel._close_tab(container.left_panel.indexOf(viewer)) is True
    app.processEvents()

    assert container.left_panel.count() == 0
    assert ("detach", viewer) in fake_session.events
    assert fake_session.host is None


def test_reopen_after_close_creates_new_shell_with_same_session(fake_session, tmp_path):
    app = _app()
    container = SplitContainer()
    first = container.open_file(str(tmp_path / "A.FCStd"))
    container.left_panel._close_tab(container.left_panel.indexOf(first))
    app.processEvents()

    second = container.open_file(str(tmp_path / "A.FCStd"))

    assert isinstance(second, FreeCADViewer)
    assert second is not first
    assert second.session is fake_session
    assert [e[0] for e in fake_session.events].count("init") == 2  # ensure_initialized is idempotent in the real session
    assert fake_session.host is second


def test_runtime_failure_shows_message_and_creates_no_tab(monkeypatch, tmp_path):
    _app()
    session = _FakeSession(init_error=FreeCADRuntimeError("FreeCAD could not be initialized in the active pyemsi environment."))
    monkeypatch.setattr(session_module, "get_freecad_session", lambda: session)
    shown: list[str] = []
    monkeypatch.setattr(split_container_module.QMessageBox, "critical", lambda parent, title, text, *a: shown.append(text))
    container = SplitContainer()

    result = container.open_file(str(tmp_path / "A.FCStd"))

    assert result is None
    assert container.left_panel.count() == 0
    assert shown and "could not be initialized" in shown[0]


def test_invalid_document_shows_warning_and_keeps_tab(monkeypatch, tmp_path):
    _app()
    session = _FakeSession(open_error=session_module.FreeCADDocumentError("FreeCAD could not open bad.FCStd:\nInvalid project file"))
    monkeypatch.setattr(session_module, "get_freecad_session", lambda: session)
    shown: list[str] = []
    monkeypatch.setattr(split_container_module.QMessageBox, "warning", lambda parent, title, text, *a: shown.append(text))
    container = SplitContainer()

    viewer = container.open_file(str(tmp_path / "bad.FCStd"))

    assert isinstance(viewer, FreeCADViewer)
    assert container.left_panel.count() == 1
    assert shown and "Invalid project file" in shown[0]


def test_non_freecad_files_still_use_generic_path(fake_session, tmp_path):
    _app()
    container = SplitContainer()
    text_file = tmp_path / "notes.txt"
    text_file.write_text("hello", encoding="utf-8")

    viewer = container.open_file(str(text_file))

    assert not isinstance(viewer, FreeCADViewer)
    assert viewer.property("file_path") == str(text_file)
    assert fake_session.events == []


def test_context_menu_hides_move_action_for_freecad_viewer(fake_session, tmp_path, monkeypatch):
    _app()
    container = SplitContainer()
    viewer = container.open_file(str(tmp_path / "A.FCStd"))
    captured: list[list[str]] = []

    class _RecordingMenu(split_container_module.QMenu):
        def exec(self, *args, **kwargs):  # noqa: A003
            captured.append([a.text() for a in self.actions() if not a.isSeparator()])
            return None

    monkeypatch.setattr(split_container_module, "QMenu", _RecordingMenu)
    panel = container.left_panel
    panel.setCurrentWidget(viewer)
    panel._show_context_menu(QPoint(0, 0))  # _tab_index_at falls back to currentIndex()

    assert captured == [["Close Tab", "Close Others", "Close All"]]
```

- [ ] **Step 2: Run to verify failure**

Run: `pixi run pytest tests/test_freecad_file_routing.py -v`
Expected: `test_fcstd_extension_maps_to_freecad_category` FAILS with `KeyError: '.fcstd'`; the routing tests FAIL because `open_file` builds an `UnsupportedViewer` (assertions on `isinstance(..., FreeCADViewer)` fail); the context-menu test FAILS because `"Move to Right Panel"` is present.

- [ ] **Step 3: Implement classification**

In `pyemsi/gui/_viewers/_constants.py`, after `_AUDIO_EXTENSIONS`:

```python
_FREECAD_EXTENSIONS = {
    ".fcstd",
}
```

and after the audio loop:

```python
for _ext in _FREECAD_EXTENSIONS:
    _CATEGORY[_ext] = "freecad"
```

In `pyemsi/gui/file_viewers.py`, add `_FREECAD_EXTENSIONS` to the `_constants` import list and to `__all__` after `"_AUDIO_EXTENSIONS",`.

- [ ] **Step 4: Implement routing in `split_container.py`**

Replace the body of `open_file` from `norm_path = _resolve_open_path(path)` through the `existing` block with:

```python
        norm_path = _resolve_open_path(path)

        ext = os.path.splitext(norm_path)[1].lower()
        effective_category = category if category is not None else _CATEGORY.get(ext)
        if effective_category == "freecad":
            return self._open_freecad_file(norm_path)

        existing = self._find_tab_by_path(norm_path)
        if existing is not None:
            self.focus_widget(existing)
            return existing

        viewer = create_viewer(norm_path, effective_category, parent=self._left)
```

(delete the now-duplicated `ext`/`effective_category` lines that followed `existing`). Update the docstring's `category` bullet to mention `"freecad"` and the return annotation to `QWidget | None` with a note: `None` only when the FreeCAD runtime failed to initialize.

Add after `_find_tab_by_path`:

```python
    def _find_freecad_viewer(self) -> QWidget | None:
        """Return the singleton FreeCAD tab shell if one is open."""
        for panel in (self._left, self._right):
            for i in range(panel.count()):
                w = panel.widget(i)
                if getattr(w, "viewer_kind", None) == "freecad":
                    return w
        return None

    def _open_freecad_file(self, norm_path: str) -> QWidget | None:
        """Open *norm_path* in the single shared FreeCAD tab, creating the shell if needed.

        The FreeCAD GUI is a process singleton, so this path bypasses the
        per-file factory: at most one ``FreeCADViewer`` exists, and every
        ``.FCStd`` becomes a document inside the shared session.
        """
        from pyemsi.gui import freecad_session as freecad_session_module
        from pyemsi.gui.freecad_runtime import FreeCADRuntimeError

        session = freecad_session_module.get_freecad_session()
        try:
            session.ensure_initialized()
        except FreeCADRuntimeError as exc:
            QMessageBox.critical(self, "FreeCAD", str(exc))
            return None

        viewer = self._find_freecad_viewer()
        if viewer is None:
            from pyemsi.gui.file_viewers import FreeCADViewer

            viewer = FreeCADViewer(session, parent=self._left)
            self.add_tab(viewer, "FreeCAD")
        else:
            self.focus_widget(viewer)

        try:
            viewer.open_file(norm_path)
        except freecad_session_module.FreeCADDocumentError as exc:
            QMessageBox.warning(self, "FreeCAD", str(exc))
            return viewer

        self._refresh_tab_title(viewer, f"FreeCAD — {os.path.basename(norm_path)}")
        return viewer
```

In `_TabPanel._show_context_menu`, wrap the move block:

```python
        # Show only the action that moves to the *other* panel. Widgets that
        # opt out (e.g. the FreeCAD shell hosting a native singleton window)
        # get no move action at all.
        if getattr(widget, "supports_panel_move", True):
            if not self._is_left:
                move_left = menu.addAction("Move to Left Panel")
                move_left.triggered.connect(lambda: self.tab_move_requested.emit(widget, title, "left"))
            else:
                move_right = menu.addAction("Move to Right Panel")
                move_right.triggered.connect(lambda: self.tab_move_requested.emit(widget, title, "right"))
            menu.addSeparator()
```

(and remove the original unconditional `menu.addSeparator()` that followed).

- [ ] **Step 5: Run tests**

Run: `pixi run pytest tests/test_freecad_file_routing.py tests/test_gui_path_resolution.py tests/test_external_file_change_handling.py tests/test_gui_add_figure.py -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add pyemsi/gui/_viewers/_constants.py pyemsi/gui/file_viewers.py pyemsi/widgets/split_container.py tests/test_freecad_file_routing.py
git commit -m "Route .FCStd files to a singleton FreeCAD tab in SplitContainer"
```

---

### Task 6: Application-exit handling of modified FreeCAD documents

**Files:**
- Modify: `pyemsi/gui/main_window.py` — `closeEvent` (lines 1114-1126) and a new `_confirm_freecad_documents` method placed directly above it
- Test: `tests/test_main_window_freecad.py`

**Interfaces:**
- Consumes: `peek_freecad_session()`, `FreeCADSession.is_initialized/modified_documents/save_document/prepare_for_application_exit`, `FreeCADDocumentError` (Task 3), imported lazily.
- Produces: `PyEmsiMainWindow._confirm_freecad_documents() -> bool` (False = user cancelled exit). `closeEvent` order: FreeCAD prompt → `close_all_tabs()` → existing cleanup → `session.prepare_for_application_exit()` → `super().closeEvent`.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_main_window_freecad.py` (reuses the window-building recipe from `tests/test_main_window_emsolution_run.py`):

```python
from __future__ import annotations

from PySide6.QtWidgets import QApplication, QDockWidget, QMessageBox, QWidget

from pyemsi.gui import freecad_session as session_module
from pyemsi.gui import main_window as main_window_module
from pyemsi.settings import SettingsManager


class _DummyExternalTerminalDock(QDockWidget):
    def __init__(self, parent=None) -> None:
        super().__init__("External Terminal", parent)

    def add_terminal(self, *args, **kwargs):
        return None

    def close_all_terminals(self) -> None:
        return None


class _DummyKernelManager:
    def shutdown_kernel(self) -> None:
        return None


def _stub_ipython_terminal(self) -> None:
    self._ipython_widget = QWidget(self._ipython_dock)
    self._kernel_manager = _DummyKernelManager()
    self._ipython_dock.setWidget(self._ipython_widget)


def _app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _make_window(tmp_path, monkeypatch):
    _app()
    monkeypatch.setattr(main_window_module, "ExternalTerminalDock", _DummyExternalTerminalDock)
    monkeypatch.setattr(main_window_module.PyEmsiMainWindow, "_setup_ipython_terminal", _stub_ipython_terminal)
    manager = SettingsManager(global_settings_path=tmp_path / "config" / "settings.json")
    return main_window_module.PyEmsiMainWindow(settings_manager=manager)


class _FakeSession:
    def __init__(self, modified, *, initialized=True, save_error=None):
        self._modified = modified
        self.is_initialized = initialized
        self.saved: list[str] = []
        self.exit_prepared = 0
        self.save_error = save_error

    def modified_documents(self):
        return list(self._modified)

    def save_document(self, name):
        if self.save_error is not None:
            raise self.save_error
        self.saved.append(name)

    def prepare_for_application_exit(self):
        self.exit_prepared += 1


def _install(monkeypatch, session):
    monkeypatch.setattr(session_module, "peek_freecad_session", lambda: session)


def test_close_without_freecad_session_proceeds(tmp_path, monkeypatch):
    _install(monkeypatch, None)
    window = _make_window(tmp_path, monkeypatch)
    try:
        assert window.close() is True
    finally:
        window.deleteLater()


def test_close_with_clean_documents_prepares_session_for_exit(tmp_path, monkeypatch):
    session = _FakeSession([])
    _install(monkeypatch, session)
    asked: list[str] = []
    monkeypatch.setattr(main_window_module.QMessageBox, "question", lambda *a, **k: asked.append(a[2]) or QMessageBox.StandardButton.Discard)
    window = _make_window(tmp_path, monkeypatch)
    try:
        assert window.close() is True
        assert asked == []
        assert session.exit_prepared == 1
    finally:
        window.deleteLater()


def test_close_prompts_per_modified_document_and_saves_on_save(tmp_path, monkeypatch):
    session = _FakeSession([("Motor", str(tmp_path / "Motor.FCStd")), ("Coil", "")])
    _install(monkeypatch, session)
    asked: list[str] = []
    monkeypatch.setattr(main_window_module.QMessageBox, "question", lambda *a, **k: asked.append(a[2]) or QMessageBox.StandardButton.Save)
    window = _make_window(tmp_path, monkeypatch)
    try:
        assert window.close() is True
        assert asked == ["Save changes to Motor.FCStd?", "Save changes to Coil?"]
        assert session.saved == ["Motor", "Coil"]
        assert session.exit_prepared == 1
    finally:
        window.deleteLater()


def test_close_cancel_keeps_window_open_and_skips_cleanup(tmp_path, monkeypatch):
    session = _FakeSession([("Motor", str(tmp_path / "Motor.FCStd"))])
    _install(monkeypatch, session)
    monkeypatch.setattr(main_window_module.QMessageBox, "question", lambda *a, **k: QMessageBox.StandardButton.Cancel)
    close_all_calls: list[int] = []
    window = _make_window(tmp_path, monkeypatch)
    monkeypatch.setattr(window._container, "close_all_tabs", lambda: close_all_calls.append(1) or True)
    try:
        assert window.close() is False
        assert close_all_calls == []
        assert session.exit_prepared == 0
    finally:
        window.deleteLater()


def test_close_discard_does_not_save(tmp_path, monkeypatch):
    session = _FakeSession([("Motor", str(tmp_path / "Motor.FCStd"))])
    _install(monkeypatch, session)
    monkeypatch.setattr(main_window_module.QMessageBox, "question", lambda *a, **k: QMessageBox.StandardButton.Discard)
    window = _make_window(tmp_path, monkeypatch)
    try:
        assert window.close() is True
        assert session.saved == []
    finally:
        window.deleteLater()


def test_close_save_failure_warns_and_cancels(tmp_path, monkeypatch):
    session = _FakeSession(
        [("Motor", "")],
        save_error=session_module.FreeCADDocumentError("FreeCAD document 'Motor' has never been saved."),
    )
    _install(monkeypatch, session)
    monkeypatch.setattr(main_window_module.QMessageBox, "question", lambda *a, **k: QMessageBox.StandardButton.Save)
    warnings: list[str] = []
    monkeypatch.setattr(main_window_module.QMessageBox, "warning", lambda *a, **k: warnings.append(a[2]))
    window = _make_window(tmp_path, monkeypatch)
    try:
        assert window.close() is False
        assert warnings and "never been saved" in warnings[0]
    finally:
        window.deleteLater()


def test_uninitialized_session_is_ignored(tmp_path, monkeypatch):
    session = _FakeSession([("Motor", "x")], initialized=False)
    _install(monkeypatch, session)
    monkeypatch.setattr(main_window_module.QMessageBox, "question", lambda *a, **k: QMessageBox.StandardButton.Cancel)
    window = _make_window(tmp_path, monkeypatch)
    try:
        assert window.close() is True
    finally:
        window.deleteLater()
```

- [ ] **Step 2: Run to verify failure**

Run: `pixi run pytest tests/test_main_window_freecad.py -v`
Expected: `test_close_prompts_per_modified_document_and_saves_on_save`, `test_close_cancel_keeps_window_open_and_skips_cleanup`, `test_close_save_failure_warns_and_cancels`, and `test_close_with_clean_documents_prepares_session_for_exit` FAIL (no prompt, `exit_prepared == 0`).

- [ ] **Step 3: Implement**

In `pyemsi/gui/main_window.py` (confirm `QMessageBox` and `os` are already imported at the top; they are used elsewhere in the file), add above `closeEvent`:

```python
    def _confirm_freecad_documents(self) -> bool:
        """Prompt Save/Discard/Cancel for every modified FreeCAD document.

        Returns False when the user cancels or a requested save fails, in
        which case the application must stay open. Runs before the generic
        tab close so a cancel leaves every tab intact.
        """
        from pyemsi.gui import freecad_session as freecad_session_module

        session = freecad_session_module.peek_freecad_session()
        if session is None or not session.is_initialized:
            return True

        for name, file_name in session.modified_documents():
            label = os.path.basename(file_name) if file_name else name
            answer = QMessageBox.question(
                self,
                "Unsaved FreeCAD Changes",
                f"Save changes to {label}?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
            )
            if answer == QMessageBox.StandardButton.Cancel:
                return False
            if answer == QMessageBox.StandardButton.Save:
                try:
                    session.save_document(name)
                except freecad_session_module.FreeCADDocumentError as exc:
                    QMessageBox.warning(self, "FreeCAD", str(exc))
                    return False
        return True
```

Rewrite `closeEvent`:

```python
    def closeEvent(self, event):
        """Confirm unsaved FreeCAD documents, close tabs, then clean up kernel/session."""
        if not self._confirm_freecad_documents():
            event.ignore()
            return
        if not self._container.close_all_tabs():
            event.ignore()
            return

        self._persist_workspace_state()
        for path in list(self._temp_converter_configs):
            self._cleanup_temp_converter_config(path)
        self._external_terminal_dock.close_all_terminals()
        if self._kernel_manager is not None:
            self._kernel_manager.shutdown_kernel()

        from pyemsi.gui import freecad_session as freecad_session_module

        session = freecad_session_module.peek_freecad_session()
        if session is not None and session.is_initialized:
            session.prepare_for_application_exit()
        super().closeEvent(event)
```

- [ ] **Step 4: Run tests**

Run: `pixi run pytest tests/test_main_window_freecad.py tests/test_main_window_settings.py tests/test_main_window_emsolution_run.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add pyemsi/gui/main_window.py tests/test_main_window_freecad.py
git commit -m "Prompt for modified FreeCAD documents before pyemsi exits"
```

---

### Task 7: Lazy-import guard and real-FreeCAD offscreen integration test

**Files:**
- Modify: `tests/test_lazy_imports.py` (watched list in `test_import_pyemsi_gui_keeps_optional_stacks_lazy`)
- Create: `tests/test_freecad_session_integration.py`

**Interfaces:** consumes the public API of Tasks 2-3 only.

- [ ] **Step 1: Extend the lazy-import test**

In `tests/test_lazy_imports.py`, change `watched_modules` to:

```python
    watched_modules = [
        "qtconsole",
        "IPython",
        "ipykernel",
        "pyemsi.plotter",
        "pyemsi.io",
        "FreeCAD",
        "FreeCADGui",
    ]
```

Run: `pixi run pytest tests/test_lazy_imports.py -v` → PASS (if it fails, some new module imports FreeCAD at module scope; fix that, do not relax the test).

- [ ] **Step 2: Write the integration test**

Create `tests/test_freecad_session_integration.py`. It runs the real FreeCAD in a **subprocess** with `QT_QPA_PLATFORM=offscreen` so the desktop test run does not flash a FreeCAD window, and so a native crash cannot take pytest down. Skips when FreeCAD is not in the active prefix.

```python
"""End-to-end check of FreeCADSession against the real FreeCAD in the Pixi env.

Runs in a subprocess (offscreen Qt) so a native failure cannot kill pytest.
Takes ~15-30 s because FreeCAD's GUI initializes all workbenches.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from pyemsi.gui.freecad_runtime import freecad_search_paths

REPO_ROOT = Path(__file__).resolve().parents[1]

_SCRIPT = r"""
import json, os, sys, tempfile
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget
app = QApplication.instance() or QApplication([])

from pyemsi.gui.freecad_session import FreeCADDocumentError, FreeCADSession

out = {}
session = FreeCADSession()
session.ensure_initialized()
session.ensure_initialized()
out["initialized"] = session.is_initialized
out["parked_hidden"] = not session.main_window.isVisible()

tmp = tempfile.mkdtemp()
path = os.path.join(tmp, "Box.FCStd")
import FreeCAD
doc = FreeCAD.newDocument("Box")
doc.addObject("Part::Box", "Box")
doc.recompute()
doc.saveAs(path)
FreeCAD.closeDocument("Box")

name1 = session.open_document(path)
name2 = session.open_document(path.replace("\\", "/"))
out["names"] = [name1, name2]
out["doc_count"] = len(FreeCAD.listDocuments())
out["is_open"] = session.is_document_open(path)
out["modified_after_open"] = session.modified_documents()

bad = os.path.join(tmp, "bad.FCStd")
with open(bad, "w") as fh:
    fh.write("not a zip")
try:
    session.open_document(bad)
    out["bad_error"] = None
except FreeCADDocumentError as exc:
    out["bad_error"] = str(exc)
out["still_initialized"] = session.is_initialized

cycles = 0
for _ in range(3):
    host = QWidget(); QVBoxLayout(host)
    session.attach(host)
    assert session.main_window.parent() is host
    session.detach(host)
    assert session.attached_host is None
    host.deleteLater()
    app.processEvents()
    cycles += 1
out["cycles"] = cycles
session.prepare_for_application_exit()
print(json.dumps(out))
"""


@pytest.mark.skipif(not freecad_search_paths(), reason="FreeCAD is not installed in the active environment")
def test_real_freecad_session_lifecycle():
    result = subprocess.run(
        [sys.executable, "-c", _SCRIPT],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    payload = json.loads(result.stdout.strip().splitlines()[-1])

    assert payload["initialized"] and payload["parked_hidden"]
    assert payload["names"] == ["Box", "Box"]
    assert payload["doc_count"] == 1
    assert payload["is_open"] is True
    assert payload["modified_after_open"] == []
    assert payload["bad_error"] and "Invalid project file" in payload["bad_error"]
    assert payload["still_initialized"] is True
    assert payload["cycles"] == 3
```

- [ ] **Step 3: Run it**

Run: `pixi run pytest tests/test_freecad_session_integration.py -v -s`
Expected: PASS in under a minute. If `returncode != 0`, read the printed stderr: an `OSError` about DLLs means `prepare_freecad_paths` missed a directory; an `AttributeError: getMainWindow` means `showMainWindow()` was not called before `getMainWindow()`.

- [ ] **Step 4: Full suite, then commit**

Run: `pixi run test`
Expected: everything green (compare against the Task 0 baseline).

```bash
git add tests/test_lazy_imports.py tests/test_freecad_session_integration.py
git commit -m "Add lazy-import guard and offscreen FreeCAD session integration test"
```

---

### Task 8: Windows manual smoke, lifecycle hardening and report

**Files:**
- Create: `dev_docs/FreeCAD dev/IMPLEMENTATION_REPORT.md`
- Modify: any file where the smoke run reveals a defect (fix with a failing test first, per the tasks above)

- [ ] **Step 1: Create two sample files**

```bash
pixi run python -c "from pyemsi.gui.freecad_runtime import import_freecad; import_freecad(); import FreeCAD; import os; d=FreeCAD.newDocument('Box'); d.addObject('Part::Box','Box'); d.recompute(); d.saveAs(os.path.abspath('Box.FCStd')); d2=FreeCAD.newDocument('Cyl'); c=d2.addObject('Part::Cylinder','Cyl'); d2.recompute(); d2.saveAs(os.path.abspath('Cylinder.FCStd')); print('ok')"
```

(Run from a scratch folder that you will open as the pyemsi workspace; do not commit the `.FCStd` files.)

- [ ] **Step 2: Run the smoke matrix**

Launch with `pixi run gui` and open the scratch folder as the workspace. Watch the terminal for Qt messages. Record every row as PASS/FAIL with notes:

| # | Scenario | Pass criteria |
|---|---|---|
| 1 | Monaco only: open a `.py`/`.txt` | Editor renders text (not black) |
| 2 | Monaco + FreeCAD: double-click `Box.FCStd` | Tab "FreeCAD — Box.FCStd" appears; box visible; rotate/zoom with mouse works; Monaco tab still renders when switched back |
| 3 | Open `Cylinder.FCStd` | Same outer tab reused; title updates; FreeCAD shows both documents in its own MDI/tree |
| 4 | Re-open `Box.FCStd` | No duplicate document in FreeCAD's tree; Box becomes active |
| 5 | Close FreeCAD tab, open Monaco file, re-open `Box.FCStd` | Tab recreated, model visible, documents still open (no reload) |
| 6 | Monaco + FreeCAD + VTK: in IPython run `add_field(...)`/open a field plot | All three visible when switching among them |
| 7 | Resize main window & splitter repeatedly, switch tabs 20× | No blank views, no `QQuickWidget`/`QOpenGLWidget`/`D3D11` incompatibility messages in the terminal |
| 8 | Right-click the FreeCAD tab | No "Move to Right Panel" action |
| 9 | Corrupt file: write `echo bad > bad.FCStd`, open it | Warning dialog with "Invalid project file"; app and other tabs keep working |
| 10 | Modify a document in FreeCAD (e.g. change Box Length), then File > Exit pyemsi | Prompt "Save changes to Box.FCStd?"; Cancel keeps app open; Save writes file (check mtime); Discard exits |
| 11 | Lifecycle: 20× close/recreate the FreeCAD tab in one process; 20× alternate opening Box/Cylinder | No crash, no duplicate FreeCAD main windows (`FreeCADGui.getMainWindow()` in IPython stays the same object), memory not visibly runaway |
| 12 | 10× full launch → open `.FCStd` → interact → close | Record the exit code of each run (`echo $LASTEXITCODE`); `0xC0000409` (-1073740791) is the known WebEngine/AMD teardown issue and is reported, not hidden. Also record whether a `web-only` run (never open `.FCStd`) shows the same code. |

- [ ] **Step 3: Fix anything that fails**

For each FAIL, reproduce in a unit test in the matching `tests/test_freecad_*.py` file first, fix, re-run the smoke row, commit with a message naming the scenario. Likely candidates and their intended fixes:
- Native window not laid out after re-attach → call `self._main_window.updateGeometry()` and `host.layout().activate()` at the end of `FreeCADSession.attach`.
- FreeCAD's own toolbars/docks misbehave when embedded → acceptable in v1 (full GUI decision); note in report.
- Initialization flash → accepted per spec §9.1; note in report.

- [ ] **Step 4: Write the report**

Create `dev_docs/FreeCAD dev/IMPLEMENTATION_REPORT.md` with these sections, filled from the actual results (no placeholders):
1. **Baseline reconciliation** — `main` HEAD used, statement that no commits since `9a5989e` touched the integration files.
2. **Changed files** — the list from *File Structure*.
3. **Architecture used** — one paragraph: graphics policy → `freecad_runtime` → `FreeCADSession` (parking) → `FreeCADViewer` shell → `SplitContainer` routing → `closeEvent` prompt.
4. **Tests added / passed** — file names, counts, and the `pixi run test` summary line.
5. **Windows manual smoke results** — the table from Step 2 with PASS/FAIL and observed exit codes for row 12, including the web-only control.
6. **Deviations from the handoff and why** — at minimum: `setParent`/`layout.addWidget` used instead of explicit window-flag juggling (setParent resets flags); `open_file` returns `None` on runtime failure (message box shown); `supports_panel_move` opt-out attribute instead of a FreeCAD-specific check in `_TabPanel`.
7. **Unresolved issues / follow-ups** — WebEngine/AMD `0xC0000409` teardown crash (separate defect); initialization flash; portable packaging (FreeCAD `.pyd`, Coin3D, OCCT, `Mod`/`Ext` not in the private-runtime builder); optional viewer-only trimming; scope statement **"development/Pixi only"**.

- [ ] **Step 5: Final verification and commit**

Run: `pixi run test`
Expected: PASS.

```bash
git add "dev_docs/FreeCAD dev/IMPLEMENTATION_REPORT.md"
git commit -m "Add FreeCAD integration implementation report with Windows smoke results"
```

Then follow `superpowers:finishing-a-development-branch` (PR into `main` from `feat/freecad-fcstd-tab`, PR body = report summary + the required attribution footer).

---

## Verification summary

- Unit/GUI tests (fast, desktop `QApplication`): `pixi run pytest tests/test_gui_launch.py tests/test_freecad_runtime.py tests/test_freecad_session.py tests/test_freecad_viewer.py tests/test_freecad_file_routing.py tests/test_main_window_freecad.py tests/test_lazy_imports.py -v`
- Real FreeCAD, offscreen, subprocess: `pixi run pytest tests/test_freecad_session_integration.py -v`
- Whole suite: `pixi run test`
- Manual Windows smoke: Task 8 table, results in `dev_docs/FreeCAD dev/IMPLEMENTATION_REPORT.md`.

## Known independent issue (do not "fix" here)

A Qt6 WebEngine-only control run reproduces a final-process `0xC0000409` in `atio6axx.dll` (AMD D3D11 teardown from `Qt6WebEngineCore` shutdown). FreeCAD-only exits normally. Record exit codes honestly in the report; no `os._exit`, no GPU toggles.
