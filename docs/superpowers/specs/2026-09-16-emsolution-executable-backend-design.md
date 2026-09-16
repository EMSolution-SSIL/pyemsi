# EMSolution executable as a run backend

## Problem

pyemsi runs EMSolution input files through `pyemsol` (a Python binding of
the EMSolution solver). This is the only supported path today: the "Run"
button in `EMSolutionInputViewer` always builds a command that invokes
`pyemsi/tools/run_emsol.py`, which does `import pyemsol` and calls
`initialize()` / `solve()` / `finalize()`.

`pyemsol` is hard to install for many customers. Those same customers
already have the plain Windows program, `EMSolution.exe`, which does the
same computation and which they are used to running directly (see
[runWindows](https://emsolution-ssil.github.io/EMSolutionDocs/handbook/run/runWindows.html)).
`EMSolution.exe` can run two ways:

- **Interactive**: double-click it, pick the input file via its own
  `File > Open` dialog, watch its own convergence chart.
- **Batch**: `EMSolution.exe -b [-m] [-v] -d <run_dir> -f <input_file_name>`,
  which runs headlessly (or with a live progress window if `-m` is given)
  and is fully driven by command-line flags — no manual file picking.

This design adds `EMSolution.exe` as a second, selectable run backend,
so users without `pyemsol` can still use pyemsi's Run/Stop workflow.

## Goals

- Let a user choose, globally, whether Run uses `pyemsol` or
  `EMSolution.exe`.
- Let a user override that choice for a single run without changing the
  global setting.
- When `EMSolution.exe` is selected, let the user choose between running
  it quietly in the background (default, matches today's experience) or
  with its native progress window also visible.
- Reuse the existing terminal dock / Stop button plumbing as-is — no new
  widget types or process-tracking paths.
- First time `EMSolution.exe` is selected, ask once where it lives and
  remember it (with a way to re-check/change it later).

## Non-goals

- Bundling, installing, or auto-updating `EMSolution.exe`.
- Supporting the executable backend on non-Windows platforms. The
  executable option is Windows-only and hidden/disabled elsewhere;
  `pyemsol` remains the only backend on Linux/macOS.
- Changing anything about the existing `pyemsol` code path.
- Converting between input file formats (see Assumptions).

## User-facing design

### Global setting

A new setting, "How should pyemsi run simulations?", with two values:
`pyemsol` (default, current behavior) and `EMSolution executable`. This
lives alongside pyemsi's other per-tool settings (`tools.*` in
`pyemsi/settings/manager.py`).

### Configuring the executable path

The first time the executable backend is chosen without a saved path,
pyemsi prompts with a "Browse..." dialog (same `_PathSelector` pattern
already used by `femap_converter_dialog.py`). The chosen path is checked
(file exists, and pyemsi attempts `<path> -v` to sanity-check it launches;
this check is informational, not a hard gate, since `-v` is only
documented from the 2024.11 release onward) and then remembered globally.

A small settings dialog (opened from the Settings menu, e.g. "EMSolution
Run Settings...") lets the user view/change the saved path and re-run the
check later.

### Per-run override

Next to Run/Stop in `EMSolutionInputViewer`'s toolbar, two small combo
boxes are added:

- **Backend**: `Pyemsol` / `EMSolution.exe`, initialized from the global
  default each time the viewer loads.
- **Style**: `Background` / `Window`, only shown/enabled when Backend is
  `EMSolution.exe`, also initialized from the global default.

Changing either combo only affects this viewer's next Run click — it is
not written back to settings. This gives a lightweight one-off override
without a trip to a settings dialog.

### Running and stopping

Both styles reuse the exact mechanism `_run_emsol_external` already uses
for `pyemsol` today: build a `cmd` + `args` + `cwd`, hand them to
`ExternalTerminalDock.add_terminal(...)`, track the returned `XtermWidget`
in `_active_external_terminals`, and call `xterm.kill()` on Stop. Nothing
new is added to the terminal dock or its widgets.

The only thing that changes per backend/style is which command is built:

| Backend / style              | cmd                | args (conceptually)                                   |
|-------------------------------|--------------------|--------------------------------------------------------|
| pyemsol                       | `sys.executable`   | `[run_emsol.py, path]` (unchanged, today's behavior)   |
| EMSolution.exe / Background   | `<exe path>`       | `-b -d <folder> -f <filename>`                         |
| EMSolution.exe / Window       | `<exe path>`       | `-b -m -d <folder> -f <filename>`                       |

`<folder>` and `<filename>` are derived the same way `_run_emsol_external`
already derives `cwd`/`path` today (folder containing the input file,
file's own name).

Because `-m` only adds a native progress window on top of the same batch
run — it does not change whether console text is produced — the terminal
tab behaves the same way for both styles: it shows whatever text
`EMSolution.exe` prints, and pyemsi also writes one short informational
line to that tab up front (e.g. "Running EMSolution.exe — its own progress
window may also open") so the user isn't confused if the console pane
stays quiet while the native window does the work. That line is emitted by
prefixing the launched command in `cmd.exe` (`cmd /c echo ... && "<exe>" ...`),
not by adding a new UI element.

### Errors

- Executable backend selected but no path saved yet → first-run browse
  flow (above) runs before Run proceeds; if the user cancels, Run is a
  no-op.
- Saved path no longer points at a file (moved/uninstalled) → same
  browse flow is re-triggered; pyemsi does not silently fall back to
  `pyemsol`.
- `pyemsol` missing when that backend is selected → unchanged existing
  behavior (the import error surfaces as today, in the terminal tab).

## Settings schema additions

New keys in `pyemsi/settings/manager.py`, following the existing
`SettingDefinition` pattern:

- `tools.emsolution_run.backend`: `"pyemsol"` (default) or
  `"executable"`, `SCOPE_GLOBAL`.
- `tools.emsolution_run.executable_path`: optional path,
  `SCOPE_GLOBAL`, validated with the existing `_normalize_optional_path`.
- `tools.emsolution_run.run_style`: `"background"` (default) or
  `"window"`, `SCOPE_GLOBAL`.

All global-scoped, since the executable's location and the
background/window preference are machine-level, not workspace-level.
The per-run toolbar combo boxes read these as their initial values but
never write to them.

## Runtime architecture

A single new function centralizes command construction, e.g.
`pyemsi/tools/emsolution_run.py::build_run_command(settings, input_path, backend, run_style) -> RunCommand`
where `RunCommand` is a small `(cmd, args, cwd, title)` value. This
function is pure (no Qt, no process spawning), so it is unit-testable
without a real `pyemsol` install or a real `EMSolution.exe` binary.
`main_window._run_emsol_external` (and friends) call this instead of
hardcoding the `run_emsol.py` invocation, and the resulting
`cmd`/`args`/`cwd` are passed to `add_terminal` exactly as they are today.

## Assumptions / open questions to verify during implementation

- **Input file format compatibility** — VERIFIED. A real pyemsi-saved
  input JSON (see the manual-verification memory note below) runs
  directly via `EMSolution.exe -f/-d` batch mode with no conversion
  step, confirmed across multiple full runs.
- **`-d` trailing backslash** — applied unconditionally in
  `build_run_command` (`run_dir = folder + os.sep`), matching the
  docs' example. Every manual run with the trailing backslash present
  has completed successfully; whether omitting it would actually break
  parsing was not isolated separately, so the code keeps it rather
  than relying on that being optional.
- **Console output under `-m`** — CORRECTED, not just verified: on the
  real, CodeMeter-licensed binary used for manual verification
  (`EMSolution x64 r2025.11.2 (CodeMeter)`), a native window appears
  **regardless of whether `-m` is passed** — `-b` alone also opens it,
  contradicting `runWindows.rst`'s documented behavior (window only
  with `-m`). This is external/vendor behavior on this specific build,
  not something `build_run_command`'s flag construction can change.
  See "Known limitations" below.

## Known limitations (discovered during manual verification)

- **"Background" style still shows a native window on this binary.**
  The Goals section above states Background should run "quietly ...
  (default, matches today's experience)". In practice, on the
  CodeMeter-licensed `EMSolution.exe` build used for verification,
  both `Background` (`-b`) and `Window` (`-b -m`) styles show the same
  native progress window — `-m` makes no observable difference on this
  build. Investigated as a full root-cause pass (not assumed): ruled
  out pyemsi's flag construction (verified correct against the docs)
  and ruled out a misleading test harness (an initial repro using raw
  `subprocess.Popen` was discarded because `Popen` can itself allocate
  a console window for a console-subsystem exe; the corrected repro
  drove the real `XtermWidget`/pywinpty code path used in production).
  No pyemsi-side fix is possible for this; users on affected builds
  will see a window either way.
- **Stop must kill the whole process tree, not just the immediate
  child.** `EMSolution.exe` runs as a grandchild of the PTY's tracked
  process (`cmd /c echo ... && EMSolution.exe ...`, see
  `build_run_command`). `PtyProcess.terminate()`/`kill()` only signal
  the single top-level pid winpty tracks (`cmd.exe`) — never
  descendants — so a naive Stop only killed `cmd.exe` and left
  `EMSolution.exe` running unattended mid-simulation.
  `XtermWidget.kill()` now also runs `taskkill /F /T /PID <pid>`
  (terminates the full process tree) before falling back to
  `PtyProcess.terminate()`. Fixed and covered by a regression test in
  `tests/test_xterm_widget.py`.

## Testing

- Unit tests for the three new setting keys (defaults, validation,
  round-trip through `SettingsManager`), matching existing tests for
  other `tools.*` settings.
- Unit tests for `build_run_command` covering all three
  backend/style combinations, asserting the exact `cmd`/`args`/`cwd`
  produced — no Qt or real binaries required.
- Extend the existing GUI test for `EMSolutionInputViewer`
  (`tests/test_file_viewers_emsolution_json.py` or a sibling) to cover
  the new toolbar combo boxes: default values from settings, and the
  Style combo's enabled/visible state tracking the Backend combo.
- Manual verification against a real `EMSolution.exe` for the open
  questions above, since no such binary is available in this
  environment/repo.
