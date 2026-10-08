# Runtime smoke validation

Use `scripts/check_runtime.py` in a **separate, empty FreeCAD process** to verify
native box geometry, units and placement, undo/redo, model-proxy persistence,
and observer cleanup. With a GUI it also checks command activation predicates,
view-provider restoration, and selection-observer removal. It refuses to start
with existing documents and closes only documents it creates or opens. Its small
command registrations last for that isolated process; the GUI launcher exits it.

This smoke test samples specific contracts. It does not establish availability
of the complete generated catalogue or validate every addon lifecycle.

## Observed build and results

On 2026-09-30, an existing per-user installation was discovered through the
Windows uninstall registry:

- GUI: `C:/Users/eskandarih/AppData/Local/Programs/FreeCAD 1.1/bin/FreeCAD.exe`
- CLI: `C:/Users/eskandarih/AppData/Local/Programs/FreeCAD 1.1/bin/FreeCADCmd.exe`
- Bundled Python: `C:/Users/eskandarih/AppData/Local/Programs/FreeCAD 1.1/bin/python.exe`
- `FreeCAD.Version()`: `1.1.4`, build `20260928 (Git shallow)`, commit
  `4fd3bf320d9566a27e60069fc8387448aaa3a094`.

This installed build differs from the reference checkout (`26.3.0-dev`,
`3160daf1e2`). Runtime results apply to that installed build; they do not prove
behavior of an unbuilt checkout. No FreeCAD installation or dependency changes
were needed.

| Check | Observed result |
| --- | --- |
| Native `Part::Box`, unit-string dimensions, placement and recompute | Passed in CLI and GUI |
| Native box undo/redo | Passed in CLI after enabling undo on the owned document; passed in GUI |
| Application document observer removal | Passed in CLI and GUI; removal stopped new-object notifications |
| Model proxy save/reopen and geometry | Passed in CLI and GUI |
| Fresh-process proxy restore | Passed in a second FreeCADCmd process |
| View proxy restore | Passed in GUI; skipped in CLI |
| GUI command boolean predicate and activation | Passed in GUI; `True` activated the command, integer `1` was rejected |
| GUI selection observer removal | Passed in GUI; removal stopped subsequent selection notifications |

The persistence checks verify `dumps`/`loads`, `onDocumentRestored`, stable module
lookup, exclusion of constructor-only state, and regenerated geometry. The model
class lives in the importable `check_runtime` module; it is not saved as a class
defined only in `__main__`.

### Compatibility and launch discoveries

In this installed 1.1.4 CLI build, a new document starts with `UndoMode == 0`.
The first undo check failed until the disposable document set `UndoMode = 1`.
That differs from this checkout's `src/App/DocumentPyImp.cpp:980`, whose getter
returns 1 unconditionally and setter does nothing. The installed build's own
`Mod/Test/Document.py` sets `UndoMode = 1` for undo tests. The smoke runner records
the mode before and after enabling it; do not carry either implementation's
behavior into an unconditional rule for all versions.
The isolated GUI document already had `UndoMode == 1`. The GUI process completed
all seven checks and exited after closing its owned documents.

FreeCADCmd imports positional `.py` files as modules. A `__main__`-only guard
initially produced no report even though FreeCAD loaded the file and exited 0.
The runner therefore also recognizes direct invocation from the positional file
argument. An ordinary `import check_runtime` does not run checks, which keeps
proxy restoration and GUI macro imports separate from test startup.

FreeCAD may exit 0 after Python failures. **Read `result.json` or
`restore-result.json` and inspect every check**, rather than using process exit
alone as evidence. Reports contain `success`; older retained reports can be
evaluated by confirming no check has `status: "failed"`.

The first safe-mode run emitted temporary-cache creation errors. Subsequent runs
used pre-created isolated profile/cache directories and explicit configuration
paths, with no cache errors. `FREECAD_USER_HOME` must name an existing directory
to be honored (`src/App/Application.cpp:3517`, `getCustomPaths`). A fresh isolated
profile avoids loading user addons without depending on safe-mode temporary paths.

## CLI invocation

Set paths appropriate to the installed build and checkout. The following
PowerShell example keeps runtime configuration, cache and output under a new
test directory. It does not use ordinary system Python to import FreeCAD.

```powershell
$smokeDirectory = 'C:/path/to/disposable/freecad-smoke-cli'
$skillScripts = 'C:/path/to/checkout/contrib/skills/freecad-addon-api/scripts'
$freecadCmd = 'C:/path/to/FreeCAD/bin/FreeCADCmd.exe'
New-Item -ItemType Directory -Force -Path $smokeDirectory,"$smokeDirectory/profile","$smokeDirectory/cache" | Out-Null
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:FREECAD_USER_HOME = "$smokeDirectory/profile"
$env:FREECAD_USER_TEMP = "$smokeDirectory/cache"
$env:FREECAD_SKILL_RUNTIME_OUTPUT = $smokeDirectory
& $freecadCmd --user-cfg "$smokeDirectory/user.cfg" --system-cfg "$smokeDirectory/system.cfg" --log-file "$smokeDirectory/freecad.log" -P $skillScripts "$skillScripts/check_runtime.py"
Get-Content "$smokeDirectory/result.json"
```

For a fresh-process restoration check, retain the saved `smoke.FCStd`, set
`$env:FREECAD_SKILL_RUNTIME_RESTORE = '1'`, and execute the same command in a
second FreeCADCmd process. Inspect `restore-result.json`. Remove that phase
environment variable before another full run. Always use a disposable output
directory: a full run writes its own `smoke.FCStd` there.

## Isolated GUI invocation

Create another output/profile/cache directory and use separate config files.
Create a small `.FCMacro` launcher with this content, replacing the output path:

```python
import sys
sys.dont_write_bytecode = True
import check_runtime
import FreeCADGui as Gui
from PySide import QtCore

try:
    check_runtime.run("C:/path/to/disposable/freecad-smoke-gui")
finally:
    QtCore.QTimer.singleShot(250, Gui.getMainWindow().close)
```

Launch the GUI binary with the same configuration flags and `-P` script-directory
flag, passing this macro as the positional file. On Windows use
`Start-Process -WindowStyle Hidden` for this helper process. Wait for that owned
process to close, then inspect the GUI `result.json`; no result file means the
checks have not been confirmed as executed. The GUI macro's timer closes the
isolated application after the runner closes its documents.

## Maintained evidence

Source contracts exercised by this script:
`src/App/FeaturePython.cpp:74`, `:216`;
`src/App/PropertyPythonObject.cpp:238`, `:463`;
`src/Gui/ViewProviderFeaturePython.cpp:651`, `:779`;
`src/Gui/Command.cpp:1528`, `:1552`;
`src/App/DocumentObserverPython.cpp:42`;
`src/Gui/Selection/SelectionObserverPython.cpp:99`, `:229`.

The run artifacts for this session are outside the skill in the task's
visualization directory, under `freecad-skill-forward-test/runtime-cli` and
`runtime-gui`. Keep runtime outputs, configuration, saved documents and bytecode
out of the skill folder. The runner uses only the Python standard library and
FreeCAD modules available in the target application.
