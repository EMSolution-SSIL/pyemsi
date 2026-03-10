# pyemsi

Python tools for EMSolution FEMAP Neutral file conversion and interactive 3D visualization with VTK.

## Overview

`pyemsi` provides powerful tools for working with EMSolution FEMAP Neutral (.neu) files, enabling seamless conversion to VTK formats for advanced visualization in ParaView and interactive 3D exploration through Qt-based desktop applications.

### Key Features

- **FEMAP to VTK Conversion**: Convert EMSolution FEMAP Neutral files to VTK MultiBlock UnstructuredGrid (.vtm) format
- **High-Performance Parsing**: Cython-accelerated parser for fast processing of large models
- **Interactive 3D Visualization**: Desktop Qt and Jupyter notebook visualization with PyVista
- **Comprehensive Data Support**: Handle displacement, magnetic, current, force, and heat data


## Installation

### Standard Installation

```bash
pip install pyemsi
```

### With Jupyter Notebook Support

For interactive visualization in Jupyter notebooks:

```bash
pip install pyemsi[jupyter]
```

### From Source

For development or the latest features:

```bash
git clone https://github.com/EMSolution-SSIL/pyemsi.git
cd pyemsi
pip install -e .
```

**Note**: Building from source requires Cython>=3.0.0 and numpy>=1.21.0. These will be installed automatically during the build process.

### Qt Resources

If you're developing pyemsi and need to modify Qt resources (icons, UI files), you'll need to manually compile them:

```bash
pyside6-rcc.exe .\pyemsi\resources\resources.qrc -g python -o .\pyemsi\resources\resources.py
```

### Cython Extension

The `femap_parser` module is implemented in Cython for performance. When building from source, the extension will be compiled automatically. Pre-generated C files are included in source distributions for users without Cython.

To manually compile the extension in-place (produces a `.pyd` file on Windows):

```bash
python setup.py build_ext --inplace
```

The compiled `.pyd` file will be placed in `pyemsi/core/`.

## Build Artifacts

This repository is configured to produce two distributables:

- `pyemsi` API wheel (`.whl`) via PEP 517 build
- `pyemsi_gui` desktop installer via Briefcase

### Build the `pyemsi` API Wheel

From the repository root:

```bash
python -m pip install --upgrade pip build
python -m build --wheel
```

Output:

- Wheel file in `dist/` (for example: `dist/pyemsi-0.1.2-cp313-cp313-win_amd64.whl`)

Optional check:

```bash
python -m pip install --force-reinstall dist/*.whl
```

### Build the `pyemsi_gui` Installer (Briefcase)

`pyproject.toml` already contains Briefcase configuration under `[tool.briefcase.app.pyemsi_gui]`.

1. Install Briefcase (in your Python 3.11 environment):

```bash
.venv311\\Scripts\\python.exe -m pip install --upgrade briefcase
```

2. Create/update the Windows app bundle:

```bash
.venv311\\Scripts\\python.exe -m briefcase create windows app --no-input
# If the app template already exists, use:
.venv311\\Scripts\\python.exe -m briefcase update windows app -r --no-input
```

3. Build the app:

```bash
.venv311\\Scripts\\python.exe -m briefcase build windows app --no-input
```

4. Package installer:

```bash
.venv311\\Scripts\\python.exe -m briefcase package windows -p msi --no-input
```

Output:

- Built app folder under `build/pyemsi_gui/windows/app/`
- MSI installer under `dist/` (once WiX toolset installation completes)

### Notes for Windows Packaging

- The first MSI packaging run may prompt/install the WiX toolset.
- If `briefcase create` fails because the app already exists, run `briefcase update windows app -r --no-input` and continue.
- You can run the app without packaging using:

```bash
.venv311\\Scripts\\python.exe -m briefcase run windows app
```

## Documentation

For comprehensive API documentation and tutorials, visit:

https://emsolution-ssil.github.io/pyemsi

## Requirements

- Python >= 3.11, < 3.12
- VTK >= 9.0.0
- PyVista >= 0.43.0
- PySide6 >= 6.5.0
- NumPy >= 1.21.0

## License

GNU General Public License v3.0 or later (GPLv3+) - Copyright (c) 2026 SSIL

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
