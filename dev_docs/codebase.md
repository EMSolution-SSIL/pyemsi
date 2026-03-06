# pyemsi Codebase Guide

**Version:** 0.1.2  
**Python:** ≥ 3.9  
**License:** GPL-3.0-or-later

---

## Overview

`pyemsi` is a Python toolkit for processing and visualizing **EMSolution** simulation output files. Its three main capabilities are:

1. **Parsing** FEMAP Neutral (`.neu`) files into structured data (Cython-accelerated).
2. **Converting** parsed data to VTK MultiBlock (`.vtm`/`.pvd`) format for ParaView or PyVista.
3. **Visualizing** the resulting meshes interactively via a dual-mode plotter (Qt desktop or Jupyter notebook) and a full Qt desktop GUI.

---

## Package Structure

```
pyemsi/
├── __init__.py           ← Public API surface
├── core/                 ← Backend: parsing (no Qt, no GUI)
├── tools/                ← Tools: data conversion
├── plotter/              ← Shared: visualization (PyVista + optional Qt)
├── widgets/              ← Shared: reusable Qt widgets
├── gui/                  ← Frontend: full Qt desktop application
├── resources/            ← Compiled Qt resources (icons, etc.)
└── examples/             ← Bundled example data files
```

---

## Section Details

### `pyemsi/__init__.py` — Public API

**Purpose:** The single importable surface of the library. Re-exports the most useful symbols so callers need only `import pyemsi`.

**Key exports:**
- `FemapConverter` — the conversion tool
- `Plotter` — the visualization class
- `examples` — bundled example data access
- `configure_logging(level, handler, format_string)` — library-level log configuration
- `gui` — the desktop GUI module (lazy, via `pyemsi.gui.launch()`)

**AI agent notes:**
- Do not add new top-level symbols here without a strong reason. Keep this file thin.
- `gui` is intentionally *not* eagerly imported at the top level to avoid triggering Qt initialization when the library is used headlessly.

---

### `pyemsi/core/` — Backend Parser

**Purpose:** Cython-compiled, high-performance FEMAP Neutral file parser. Has **no Qt or GUI dependency** and is safe to import anywhere.

| File | Role |
|---|---|
| `femap_parser.pyx` | Cython source — defines `FEMAPParser` and `FEMAPBlock` |
| `femap_parser.pxd` | Cython declaration file (typed C-level interface) |
| `femap_parser.c` | Auto-generated C source (used when Cython is unavailable) |
| `femap_parser.cp313-win_amd64.pyd` | Pre-compiled Windows extension for CPython 3.13 |
| `femap_parser_bak.py` | Pure-Python reference implementation (not imported anywhere) |

**`FEMAPParser(filepath: str)`**
- Parses a FEMAP Neutral file on construction and groups all data blocks by their integer block ID.
- Blocks can appear in any order and can repeat.
- Block delimiter is `"   -1"` (3 spaces + `-1`).
- Stores result as `self.blocks: dict[int, list[FEMAPBlock]]`.

**`FEMAPBlock(block_id: int, lines: list[str])`**
- Lightweight container: holds `block_id` and the raw lines of one block.

**AI agent notes:**
- The compiled `.pyd` only works on Windows/CPython 3.13. On other platforms the `.c` file is compiled at install time via `setup.py`.
- If you change `femap_parser.pyx`, you must re-run `python setup.py build_ext --inplace` to regenerate `.c` and `.pyd`.
- Import path: `from pyemsi.core.femap_parser import FEMAPParser, FEMAPBlock`
- The `femap_parser_bak.py` is kept for reference only and should not be imported.

---

### `pyemsi/tools/` — Conversion Tools

**Purpose:** High-level data-processing tools. No Qt dependency.

| File | Role |
|---|---|
| `FemapConverter.py` | Converts FEMAP Neutral output to VTK MultiBlock `.vtm`/`.pvd` |

**`FemapConverter(input_dir, output_dir, output_name, ...)`**

The conversion pipeline (executed by calling `.run()`):
1. **Build mesh** — reads `post_geom` (or custom mesh file) via `FEMAPParser`, maps FEMAP topology IDs to VTK cell types using `FEMAP_TO_VTK`, assembles a `pv.MultiBlock` dataset.
2. **Parse data files** — reads displacement, magnetic, current, force, `force_J_B`, and heat files (all optional, controlled by constructor arguments).
3. **Initialize PVD** — creates a ParaView dataset series file referencing each time step's `.vtm` file.
4. **Time stepping** — iterates time steps, writes one `.vtm` per step via `vtkXMLMultiBlockDataWriter`.

**Key constants:**

```python
FEMAP_TO_VTK: dict[int, tuple[int, int]]
# Maps femap_topology_id → (vtk_cell_type_constant, num_nodes)
# Covers: vertex, line, tri3, tri6, quad4, quad8, tetra4, tetra10, wedge6, wedge15, brick8, brick20

FORCE_2D_TOPOLOGY: dict[int, int]
# Maps 3D topology IDs to their 2D face equivalent when force_2d=True
# e.g. Brick8(8) → Quad4(4)
```

**Constructor parameters of note:**
- `force_2d: bool` — extract surface faces instead of volumetric cells (useful for surface-only visualization).
- `ascii_mode: bool` — write `.vtm` in ASCII instead of binary (larger files, human-readable).
- `mesh`, `displacement`, `magnetic`, `current`, `force`, `force_J_B`, `heat` — relative file names (or absolute `Path`s) within `input_dir`. Pass `None` to disable any data channel.

**AI agent notes:**
- Import path: `from pyemsi.tools.FemapConverter import FemapConverter`
- Or via the top-level: `from pyemsi import FemapConverter`
- Output is always placed in `output_dir/<output_name>/` with a controlling `<output_name>.pvd`.
- The converter uses `threading` internally; do not call `.run()` from multiple threads simultaneously.

---

### `pyemsi/plotter/` — Shared Visualization Layer

**Purpose:** The bridge between the pure-data backend and the visual frontend. Used both by API callers (scripts/Jupyter) and by the Qt GUI. PyVista is always required; Qt is optional.

| File | Role |
|---|---|
| `plotter.py` | `Plotter` — dual-mode (Qt / Jupyter) visualization class |
| `qt_window.py` | `QtPlotterWindow` — Qt window + toolbar + picker |
| `color_utils.py` | Color format conversion utilities |
| `block_visibility_dialog.py` | Dialog: toggle visibility of individual mesh blocks |
| `cell_query_dialog.py` | Dialog: interactive cell picking + matplotlib chart |
| `display_settings_dialog.py` | Dialog: axes, grid, colormap configuration |
| `pick_result_history_dialog.py` | Dialog: non-modal pick history log |
| `point_query_dialog.py` | Dialog: interactive point picking + matplotlib chart |
| `sample_arcs_dialog.py` | Dialog: arc-path sampling (A, B, center, resolution) |
| `sample_lines_dialog.py` | Dialog: line-path sampling (start, end, resolution) |
| `scalar_bar_settings_dialog.py` | Dialog: add/remove and style scalar bars |

#### `Plotter`

**Dual-mode design:**
- **Desktop mode** (`notebook=False`, default): creates a `QtInteractor` and a `QtPlotterWindow`, renders in a native OS window.
- **Notebook mode** (`notebook=True`): falls back to a plain `pv.Plotter` with the PyVista Trame/static backend.

**Key API:**
```python
p = Plotter(title="My Plot", window_size=(1024, 768))
p.set_file("output.pvd")      # load a PVD/VTM file
p.show()                       # open the window (blocking in desktop mode)
```

**AI agent notes:**
- `from pyemsi.plotter import Plotter` — the package `__init__` re-exports it.
- Or `from pyemsi import Plotter`.
- `HAS_QT` flag at module level — if Qt/pyvistaqt is not installed, only notebook mode works.
- `QtPlotterWindow` should not be instantiated directly; it is owned and managed by `Plotter`.

#### `QtPlotterWindow`

Wraps `QApplication` + `QMainWindow` + `QtInteractor`. Provides:
- A **camera toolbar** (standard views: front, back, top, isometric, etc.)
- A **display toolbar** (open dialogs for display settings, block visibility, scalar bars)
- A **query toolbar** (activate point/cell pick mode, line/arc sampling, pick history)
- Interactive **point pick mode** and **cell pick mode** with VTK `vtkCellPicker`.

#### `color_utils.py`

Utility functions for converting between all common color formats:

| Function | Converts |
|---|---|
| `normalize_rgb(rgb)` | `(0-255)` → `(0.0-1.0)` |
| `denormalize_rgb(rgb)` | `(0.0-1.0)` → `(0-255)` |
| `hex_to_rgb(hex_color, normalized)` | `"#RRGGBB"` → RGB tuple |
| `rgb_to_hex(rgb)` | RGB tuple → `"#RRGGBB"` |
| `to_hex(color)` | Any `ColorType` → `"#RRGGBB"` |
| `to_pyvista(color)` | Any `ColorType` → `pv.Color` |
| `to_qcolor(color)` | Any `ColorType` → `QColor` |

`ColorType` alias covers hex strings, named color strings, int/float RGB(A) tuples.

---

### `pyemsi/widgets/` — Reusable Qt Widgets

**Purpose:** Self-contained PySide6 widgets with **no PyVista dependency**. Used by both the plotter dialogs and the main GUI window.

| File | Class | Role |
|---|---|---|
| `property_delegate.py` | `PropertyDelegate`, `SliderLineEditWidget` | Custom `QStyledItemDelegate` with slider+spinbox, combo, checkbox, and color-picker editors |
| `property_tree_widget.py` | `PropertyTreeWidget` | Editable `QTreeWidget` with per-row validators, `PropertyDelegate`-powered editing |
| `explorer_widget.py` | `ExplorerWidget` | VSCode-style file system tree; empty-state hint when no folder is open |
| `split_container.py` | `SplitContainer`, `_TabPanel` | Two-panel horizontal `QSplitter` with tabbed panels; right-click context menu for moving/closing tabs |

#### `widgets/monaco_lsp` (Python LSP + Semantic Highlighting Rollout)

- `MonacoLspWidget` keeps a WebSocket contract to Monaco (`ws://127.0.0.1:<port>`).
- Default Python server path remains `pylsp --ws --port <port>`.
- Feature-flag path uses a local relay (`pyemsi.widgets.monaco_lsp._relay`) that proxies WebSocket JSON-RPC to `basedpyright-langserver --stdio`.
- Rollout gate:
  - Python viewer requests semantic highlighting by default.
  - `PYEMSI_PY_SEMANTIC_TOKENS=0` forces legacy `pylsp --ws` behavior.
  - `PYEMSI_PY_SEMANTIC_TOKENS=1` forces relay + BasedPyright semantic-token path.
- Viewer scope:
  - Python viewer enables semantic-highlighting support (`MonacoLspWidget(..., enable_python_semantic_highlighting=True)`).
  - Non-Python Monaco paths are unchanged.
- Fail-open behavior:
  - If `basedpyright-langserver` is unavailable or relay launch fails, startup falls back to legacy `pylsp --ws`.
  - If runtime capabilities omit `semanticTokensProvider` or token requests fail, syntax highlighting remains active.
- Debug diagnostics:
  - `PYEMSI_MONACO_LSP_DEBUG=1` enables concise launch/capability diagnostics.

#### `PropertyTreeWidget`

- Each row has a *key* column and an *editable value* column.
- Supports value types: `str`, `int`, `float`, `bool` (checkbox), `color` (QColor picker), `combo` (dropdown).
- Validators: attach a `Callable[[Any], str]` per row; return `""` for valid or an error string to reject the edit.
- Built-in validator factories: `range_validator(min, max)`, `regex_validator(pattern)`.

#### `ExplorerWidget`

- Emits `file_activated(str)` when a file is double-clicked.
- Emits `open_folder_requested()` when the user activates the empty-state button.
- Call `set_directory(path)` to populate the tree.

#### `SplitContainer`

- Two `_TabPanel` instances inside a `QSplitter`.
- Right panel is hidden until the first tab is moved there.
- `add_tab(widget, title, panel="left")` — programmatic tab insertion.
- Right-click tab → *Move to Left/Right Panel*, *Close Tab*, *Close Others*, *Close All*.

**AI agent notes:**
- Import via `from pyemsi.widgets import ExplorerWidget, SplitContainer, PropertyTreeWidget, PropertyDelegate`.
- `PropertyDelegate` is the lower-level editor; most users only need `PropertyTreeWidget`.
- These widgets have no dependency on `pyemsi.core`, `pyemsi.tools`, or `pyemsi.plotter`.

---

### `pyemsi/gui/` — Desktop GUI Frontend

**Purpose:** A full-featured PySide6 desktop application that orchestrates all other layers. Entry point: `python -m pyemsi.gui` or `pyemsi.gui.launch()`.

| File | Role |
|---|---|
| `__init__.py` | `launch()` function; module acts as a proxy to `PyEmsiMainWindow` |
| `__main__.py` | Enables `python -m pyemsi.gui` |
| `main_window.py` | `PyEmsiMainWindow` — the top-level `QMainWindow` |
| `terminal_widget.py` | `create_terminal_widget()` — embedded in-process IPython terminal |
| `file_viewers.py` | Text / image / audio file viewer widgets (opened as tabs) |

#### `PyEmsiMainWindow`

Layout:
- **Central widget:** `SplitContainer` (two-panel tabbed area for plotter views and file viewers).
- **Left dock:** `ExplorerWidget` (file system browser; double-click opens a file as a tab).
- **Bottom dock:** Embedded `RichJupyterWidget` (IPython terminal, in-process kernel).
- **Menu bar:** *File → Open Folder*, *View → toggle Explorer / Terminal*.

#### `gui/__init__.py` — Proxy Pattern

After `launch()` is called, the module itself proxies attribute access to the `PyEmsiMainWindow` instance:

```python
from pyemsi import gui
gui.launch()

# After launch, gui acts like the window:
gui.container.add_tab(widget, "My Tab")
gui.terminal         # the IPython RichJupyterWidget
gui.push_to_namespace(plotter=my_plotter)
```

#### `terminal_widget.py`

Creates an in-process IPython kernel (`QtInProcessKernelManager`) so the terminal can directly access live Python objects in the GUI process. Initial namespace can be injected:

```python
widget, km = create_terminal_widget(namespace={"plotter": p, "container": c})
```

#### `file_viewers.py`

Factory function `open_file_viewer(path) -> QWidget` returns the appropriate viewer:
- **Text viewer:** `QPlainTextEdit` (read-only) for `.py`, `.txt`, `.json`, `.yaml`, `.toml`, `.csv`, `.md`, `.xml`, `.log`, `.cfg`, `.ini`, `.rst`, `.sh`, and more.
- **Image viewer:** `QLabel` inside `QScrollArea` for `.png`, `.jpg`, `.bmp`, `.gif`, `.svg`, etc.
- **Audio viewer:** `QMediaPlayer` + `QAudioOutput` for `.mp3`, `.wav`, `.ogg` (requires `PySide6.QtMultimedia`; gracefully absent if not installed).

---

### `pyemsi/resources/` — Qt Resources

| File | Role |
|---|---|
| `resources.qrc` | Qt resource descriptor (lists all icon files) |
| `resources.py` | Auto-generated Python resource registration (`pyrcc6` output) |
| `icons/` | SVG icon files used by toolbars and dialogs |

**AI agent notes:**
- Import with `import pyemsi.resources.resources` (side-effect import; registers resources into Qt's virtual filesystem).
- After import, icons are available via paths like `QIcon(":/icons/Icon.svg")`.
- If you add a new icon, add it to `resources.qrc` and regenerate `resources.py` with `pyside6-rcc resources.qrc -o resources.py`.

---

### `pyemsi/examples/` — Bundled Example Data

| File | Role |
|---|---|
| `__init__.py` | `transient_path() -> str` — returns absolute path to the bundled PVD file |
| `transient.pvd` | Example ParaView dataset series descriptor |
| `transient/` | Directory of `.vtm` files referenced by `transient.pvd` |

Usage:
```python
import pyemsi
p = pyemsi.Plotter()
p.set_file(pyemsi.examples.transient_path())
p.show()
```

---

## Dependency Map

```
pyemsi.core
  └── (no pyemsi deps)

pyemsi.tools
  └── pyemsi.core

pyemsi.plotter
  ├── pyemsi.widgets     (dialogs use PropertyTreeWidget)
  └── (no pyemsi.core / pyemsi.tools deps)

pyemsi.widgets
  └── (no pyemsi deps)

pyemsi.gui
  ├── pyemsi.widgets
  └── (no direct pyemsi.plotter dep — plotter is opened programmatically from the terminal)
```

---

## Key Inter-Module Import Patterns

| From | Imports | How |
|---|---|---|
| `tools/FemapConverter.py` | `FEMAPParser` | `from pyemsi.core.femap_parser import FEMAPParser` |
| `plotter/plotter.py` | `QtPlotterWindow` | runtime `try/except`; also TYPE_CHECKING guard |
| `plotter/qt_window.py` | `Plotter` | TYPE_CHECKING guard only (avoids circular import) |
| `plotter/dialogs` | `PropertyTreeWidget` | `from pyemsi.widgets.property_tree_widget import PropertyTreeWidget` |
| `plotter/dialogs` | `QtPlotterWindow` | TYPE_CHECKING guard only |
| `gui/main_window.py` | `ExplorerWidget`, `SplitContainer` | direct import from `pyemsi.widgets` |
| `pyemsi/__init__.py` | `FemapConverter`, `Plotter` | from `.tools` and `.plotter` |

**Circular import prevention:** `Plotter` ↔ `QtPlotterWindow` is a mutual reference. It is resolved by:
1. `plotter.py` imports `QtPlotterWindow` lazily inside `try/except` at module level.
2. `qt_window.py` imports `Plotter` only under `TYPE_CHECKING` (never at runtime).

---

## Build & Compilation

The Cython extension is declared in `setup.py`:

```
Extension name : pyemsi.core.femap_parser
Source (.pyx)  : pyemsi/core/femap_parser.pyx
Fallback (.c)  : pyemsi/core/femap_parser.c
```

Build commands:
```bash
# Development (in-place)
python setup.py build_ext --inplace

# Install (editable)
pip install -e .
```

Compiler directives applied: `boundscheck=False`, `wraparound=False`, `cdivision=True`, `initializedcheck=False`.

---

## Running the GUI

```bash
python -m pyemsi.gui
```

Or from Python:
```python
import pyemsi.gui
pyemsi.gui.launch(title="My Session", size=(1600, 1000))
```

Required extras: `qtconsole`, `ipykernel` (listed in `install_requires`).

---

## Testing

Tests live in `tests/` and use `unittest`:

| Test file | Tests |
|---|---|
| `test_femap_parser.py` | `FEMAPParser` block parsing against `.neu` fixture files |
| `test_femap_to_vtm.py` | `FemapConverter` conversion pipeline |

Fixture files (`.neu` mesh files) are in `tests/fixtures/`.

Run with:
```bash
pytest tests/
```

---

## AI Agent Guidelines

- **Adding a new data field to the converter:** Edit `pyemsi/tools/FemapConverter.py` — add a constructor parameter for the new file, parse it after the mesh phase, and attach point/cell data to the `pv.MultiBlock` before writing.
- **Adding a new dialog to the plotter toolbar:** Create the dialog in `pyemsi/plotter/`, import it in `qt_window.py`, and add the triggering action to one of the three `QToolBar` instances.
- **Adding a new reusable widget:** Place it in `pyemsi/widgets/` with no dependency on `pyemsi.core`, `pyemsi.tools`, or `pyemsi.plotter`.
- **Adding a new viewer type in the GUI:** Add the extension to `_CATEGORY` in `gui/file_viewers.py` and implement a viewer widget class following the existing pattern.
- **Avoid importing Qt at module level in `core/` or `tools/`:** These must stay headless.
- **Avoid importing `pyemsi.plotter` or `pyemsi.gui` inside `__init__.py` eagerly** unless the symbol is specifically part of the public API.
- **Circular import risk:** Any file that imports both `Plotter` and `QtPlotterWindow` at runtime (not TYPE_CHECKING) will cause a circular import. Use the established pattern: one side uses TYPE_CHECKING only.
- **Resources must be imported first:** Any code that uses `QIcon(":/icons/...")` must ensure `import pyemsi.resources.resources` has been executed beforehand.
