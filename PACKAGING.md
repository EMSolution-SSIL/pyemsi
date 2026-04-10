# Packaging And Distribution

This repository produces three distributables:

- The `pyemsi` API wheel (`.whl`) via the standard Python build flow.
- A Windows portable `pyemsi` GUI runtime staged under `dist/`.
- A Windows NSIS installer built from the portable runtime.

## Build The `pyemsi` Wheel

From the repository root:

```bash
python -m pip install --upgrade pip build
python -m build --wheel
```

Output:

- Wheel files are written to `dist/`.

Optional reinstall check:

```bash
python -m pip install --force-reinstall dist/*.whl
```

## Build The Windows Portable GUI Runtime

The portable Windows builder lives at [tools/build_windows_private_runtime.py](./tools/build_windows_private_runtime.py). It assembles an embeddable Python runtime under `dist/pyemsi-windows-portable/`, stages the local `pyemsi` source tree into `app/`, installs GUI dependencies into `runtime/`, and generates native `.exe` launchers (or `.bat` fallbacks when MSVC is not available).

1. Rebuild the compiled extension in place before packaging:

   ```bash
   .venv311\Scripts\python.exe setup.py build_ext --inplace
   ```

2. Run the Windows private-runtime builder:

   ```bash
   .venv311\Scripts\python.exe .\tools\build_windows_private_runtime.py
   ```

Optional flags:

```bash
.venv311\Scripts\python.exe .\tools\build_windows_private_runtime.py --skip-dependency-install --skip-smoke-test
```

Output:

- The embeddable Python cache is stored under `build/windows-private-runtime/cache/`.
- The portable app is written to `dist/pyemsi-windows-portable/`.
- The main launcher is `dist/pyemsi-windows-portable/run_pyemsi.exe` (uses `pythonw.exe`, no console window).
- The helper script launcher is `dist/pyemsi-windows-portable/run_script.exe`.
- If MSVC is not found, `.bat` launchers are generated instead.

## Windows Packaging Notes

- This flow currently targets Windows only because it relies on the official embeddable CPython distribution.
- The builder expects `pyemsi/core/femap_parser*.pyd` and `pyemsi/resources/resources.py` to already exist in the repo tree.
- When MSVC is available (Developer Command Prompt or discoverable via `vswhere`), the builder compiles native `.exe` launchers from [tools/launcher.c](./tools/launcher.c). The GUI launcher links as a Windows subsystem app and uses `pythonw.exe` so no console window appears.
- The portable build preserves a real `runtime/python.exe` so packaged subprocess flows that depend on `sys.executable` continue to work.
- This produces a portable folder. To create an installer from it, see the next section.

## Build The Windows NSIS Installer

The NSIS script lives at [installer/pyemsi.nsi](./installer/pyemsi.nsi). It packages the portable runtime into a user-level installer with a modern UI wizard, GPLv3 license page, desktop shortcut, Start Menu group, and an "Open with pyemsi" folder context menu.

Prerequisites:

- [NSIS 3.x](https://nsis.sourceforge.io/) installed and `makensis` on `PATH`.
- A completed portable runtime build under `dist/pyemsi/` (see above).

From the repository root:

```bash
makensis installer\pyemsi.nsi
```

Output:

- `dist/pyemsi-<version>-setup.exe`

The installer:

- Installs to `%LOCALAPPDATA%\pyemsi` by default (no admin required).
- Creates a desktop shortcut and a Start Menu group.
- Registers an "Open with pyemsi" entry in the Windows Explorer folder context menu.
- Writes an uninstaller and Add/Remove Programs entry under `HKCU`.

## Related Guides

- For installation and runtime requirements, see [INSTALLATION.md](./INSTALLATION.md).
- For developer build steps, see [BUILDING.md](./BUILDING.md).