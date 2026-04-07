# Packaging And Distribution

This repository produces two primary distributables:

- The `pyemsi` API wheel (`.whl`) via the standard Python build flow.
- The `pyemsi_gui` desktop installer via Briefcase.

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

## Build The `pyemsi_gui` Installer

The Briefcase configuration lives in `pyproject.toml` under `[tool.briefcase.app.pyemsi_gui]`.

1. Install Briefcase in the Python 3.11 environment:

   ```bash
   .venv311\Scripts\python.exe -m pip install --upgrade briefcase
   ```

2. Create or refresh the Windows app bundle:

   ```bash
   .venv311\Scripts\python.exe -m briefcase create windows app --no-input
   ```

   If the template already exists, run:

   ```bash
   .venv311\Scripts\python.exe -m briefcase update windows app -r --no-input
   ```

3. Build the app:

   ```bash
   .venv311\Scripts\python.exe -m briefcase build windows app --no-input
   ```

4. Package the MSI installer:

   ```bash
   .venv311\Scripts\python.exe -m briefcase package windows -p msi --no-input
   ```

Output:

- Built app files are created under `build/pyemsi_gui/windows/app/`.
- The MSI installer is written to `dist/` once WiX installation completes.

## Windows Packaging Notes

- The first MSI packaging run may prompt for WiX toolset installation.
- If `briefcase create` fails because the app already exists, use `briefcase update windows app -r --no-input` and continue.
- You can run the app without packaging it:

```bash
.venv311\Scripts\python.exe -m briefcase run windows app
```

## Related Guides

- For installation and runtime requirements, see [INSTALLATION.md](./INSTALLATION.md).
- For developer build steps, see [BUILDING.md](./BUILDING.md).