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

## Documentation

For comprehensive API documentation and tutorials, visit:

https://emsolution-ssil.github.io/pyemsi

## Requirements

- Python >= 3.8
- VTK >= 9.0.0
- PyVista >= 0.43.0
- PySide6 >= 6.5.0
- NumPy >= 1.21.0

## License

GNU General Public License v3.0 or later (GPLv3+) - Copyright (c) 2026 SSIL

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

## Contact

For questions or support, contact: emsolution@ssil.co.jp
