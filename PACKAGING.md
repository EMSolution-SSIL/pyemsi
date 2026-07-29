# Packaging And Distribution

This repository produces three distributables:

- The `pyemsi` API wheel (`.whl`) via the standard Python build flow.
- A Windows portable `pyemsi` GUI runtime staged under `dist/`.
- A Windows NSIS installer built from the portable runtime.

The local packaging commands use the checked-in Pixi environment. Run the following command from the repository root before building:

```powershell
pixi install
```

Pixi installs the locked Python version, build dependencies, and packaging tools. Do not create a separate virtual environment or install packaging tools with `pip`.

## Build The `pyemsi` Wheel

From the repository root:

```powershell
pixi run python -m build --wheel
```

Wheel files are written to `dist/`.

Check the generated wheel metadata:

```powershell
pixi run python -m twine check dist/*.whl
```

To produce a source distribution alongside the wheel, build both artifact types:

```powershell
pixi run python -m build
```

The wheel and source distribution are written to `dist/`. Check all generated artifacts before publishing:

```powershell
pixi run python -m twine check dist/*
```

## Build Distributions With GitHub Actions

The repository also includes a manual GitHub Actions workflow at [.github/workflows/build.yml](./.github/workflows/build.yml). It builds:

- Linux wheels
- Windows wheels
- A source distribution (`sdist`)

The workflow manages its own Python build environment and does not use the local Pixi environment.

To run it from the GitHub web UI:

1. Open the repository on GitHub.
2. Go to **Actions**.
3. Select **Build Wheels** in the left sidebar.
4. Click **Run workflow**.
5. Confirm the branch you want to build from.
6. Click **Run workflow** again.
7. Wait for the workflow to finish.
8. Open the completed workflow run.
9. Download the `all-dist` artifact.

Notes:

- The workflow is configured with `workflow_dispatch`, so it only runs when started manually.
- The combined `all-dist` artifact contains the wheels and source distribution in one download.
- GitHub downloads artifacts as a `.zip`; extract it locally before uploading.

## Upload Distributions To PyPI

PyPI uploads can use artifacts built locally or downloaded from GitHub Actions.

1. Create a PyPI account if needed.
2. Generate a PyPI API token from **Account settings** -> **API tokens**.
3. Set `TWINE_USERNAME` to `__token__`.
4. Set `TWINE_PASSWORD` to the API token.
5. Check and upload the files with the Pixi-managed `twine`.

From `cmd.exe`:

```cmd
set TWINE_USERNAME=__token__
set TWINE_PASSWORD=pypi-...
pixi run python -m twine check dist/*
pixi run python -m twine upload dist/*
```

PowerShell equivalent:

```powershell
$env:TWINE_USERNAME = "__token__"
$env:TWINE_PASSWORD = "pypi-..."
pixi run python -m twine check dist/*
pixi run python -m twine upload dist/*
```

After upload, open the project page on PyPI and confirm the version and files.

## Build The Windows Portable GUI Runtime

The portable Windows builder lives at [tools/build_windows_private_runtime.py](./tools/build_windows_private_runtime.py). It assembles an embeddable Python runtime under `dist/pyemsi/`, stages the local `pyemsi` source tree into `app/`, installs GUI dependencies into `runtime/`, and generates native `.exe` launchers (or `.bat` fallbacks when MSVC is unavailable).

1. Rebuild the compiled extension in place:

   ```powershell
   pixi run python setup.py build_ext --inplace
   ```

2. Run the Windows private-runtime builder:

   ```powershell
   pixi run python .\tools\build_windows_private_runtime.py
   ```

Optional flags:

```powershell
pixi run python .\tools\build_windows_private_runtime.py --skip-dependency-install --skip-smoke-test
```

Output:

- The embeddable Python cache is stored under `build/windows-private-runtime/cache/`.
- The portable app is written to `dist/pyemsi/`.
- The main launcher is `dist/pyemsi/pyemsi.exe` (GUI mode, no console window).
- The helper script launcher is `dist/pyemsi/run_script.exe`.
- If MSVC is unavailable, `.bat` launchers are generated instead.

## Windows Packaging Notes

- This flow currently targets Windows because it relies on the official embeddable CPython distribution.
- The builder expects `pyemsi/core/femap_parser*.pyd` and `pyemsi/resources/resources.py` to already exist in the repository tree.
- When MSVC is available (in a Developer Command Prompt or discoverable through `vswhere`), the builder compiles native `.exe` launchers from [tools/launcher.c](./tools/launcher.c). The GUI launcher links as a Windows subsystem app and uses `pythonw.exe`, so no console window appears.
- The portable build preserves a real `runtime/python.exe`, allowing packaged subprocess flows that depend on `sys.executable` to continue working.
- This produces a portable folder. To create an installer from it, continue with the next section.

## Build The Windows NSIS Installer

The NSIS script lives at [installer/pyemsi.nsi](./installer/pyemsi.nsi). It packages the portable runtime into a user-level installer with a modern UI wizard, GPLv3 license page, desktop shortcut, Start Menu group, and an "Open with pyemsi" folder context menu.

Prerequisites:

- [NSIS 3.x](https://nsis.sourceforge.io/) installed with `makensis` on `PATH`.
- A completed portable runtime under `dist/pyemsi/`.

From the repository root in `cmd.exe`:

```cmd
for /f %%v in ('pixi run python -c "import pathlib,re; print(re.search(r'^__version__\\s*=\\s*\"([^\"]+)\"', pathlib.Path(r'pyemsi/__init__.py').read_text(encoding='utf-8'), re.M).group(1))"') do set APPVER=%%v
makensis /DAPP_VERSION=%APPVER% installer\pyemsi.nsi
```

PowerShell equivalent:

```powershell
$version = (Select-String -Path pyemsi\__init__.py -Pattern '^__version__\s*=\s*"([^"]+)"').Matches[0].Groups[1].Value
makensis /DAPP_VERSION=$version installer\pyemsi.nsi
```

Output:

- `dist/pyemsi-<version>-setup.exe`

The installer:

- Installs to `%LOCALAPPDATA%\pyemsi` by default (no administrator privileges required).
- Creates a desktop shortcut and a Start Menu group.
- Registers an "Open with pyemsi" entry in the Windows Explorer folder context menu.
- Writes an uninstaller and an Add/Remove Programs entry under `HKCU`.

## Related Guides

- For installation and runtime requirements, see [INSTALLATION.md](./INSTALLATION.md).
- For developer build steps, see [BUILDING.md](./BUILDING.md).
