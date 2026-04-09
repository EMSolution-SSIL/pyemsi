# Packaging And Distribution

This repository produces two primary distributables:

- The `pyemsi` API wheel (`.whl`) via the standard Python build flow.
- A Windows portable `pyemsi` GUI runtime staged under `dist/`.

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

The portable Windows builder lives at [tools/build_windows_private_runtime.py](./tools/build_windows_private_runtime.py). It assembles an embeddable Python runtime under `dist/pyemsi-windows-portable/`, stages the local `pyemsi` and `pyemsi_gui` source trees into `app/`, installs GUI dependencies into `runtime/`, and generates launcher batch files.

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
- The main launcher is `dist/pyemsi-windows-portable/run_pyemsi.bat`.
- The helper script launcher is `dist/pyemsi-windows-portable/run_script.bat`.

## Windows Packaging Notes

- This flow currently targets Windows only because it relies on the official embeddable CPython distribution.
- The builder expects `pyemsi/core/femap_parser*.pyd` and `pyemsi/resources/resources.py` to already exist in the repo tree.
- The portable build preserves a real `runtime/python.exe` so packaged subprocess flows that depend on `sys.executable` continue to work.
- This produces a portable folder, not an installer. Installer and shell-integration work can be added later as a separate step.

## Related Guides

- For installation and runtime requirements, see [INSTALLATION.md](./INSTALLATION.md).
- For developer build steps, see [BUILDING.md](./BUILDING.md).