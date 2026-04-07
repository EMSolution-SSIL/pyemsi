
<p align="center">
	<img src="https://raw.githubusercontent.com/EMSolution-SSIL/pyemsi/main/docs/static/img/logo.svg" alt="pyemsi logo" width="120">
</p>

<p align="center"><strong><font size="12">pyemsi</font></strong></p>


<p align="center">
	<a href="https://pypi.org/project/pyemsi/"><img src="https://img.shields.io/pypi/v/pyemsi" alt="PyPI version"></a>
	<a href="https://www.python.org/downloads/release/python-3110/"><img src="https://img.shields.io/badge/python-3.11-blue" alt="Python 3.11"></a>
	<a href="https://github.com/EMSolution-SSIL/pyemsi/blob/main/LICENSE"><img src="https://img.shields.io/github/license/EMSolution-SSIL/pyemsi" alt="License"></a>
	<a href="https://github.com/EMSolution-SSIL/pyemsi/actions/workflows/build.yml"><img src="https://github.com/EMSolution-SSIL/pyemsi/actions/workflows/build.yml/badge.svg?branch=main" alt="Build Wheels"></a>
</p>

Python tools for EMSolution FEMAP Neutral file conversion and interactive 3D visualization with VTK.

`pyemsi` converts EMSolution FEMAP Neutral (`.neu`) models into VTK datasets for ParaView workflows and provides interactive desktop and notebook visualization built on PyVista, VTK, and Qt.

**Quick links**

- [Documentation](https://emsolution-ssil.github.io/pyemsi)
- [API reference](https://emsolution-ssil.github.io/pyemsi/docs/api/installation)
- [Issues](https://github.com/EMSolution-SSIL/pyemsi/issues)
- [Releases](https://github.com/EMSolution-SSIL/pyemsi/releases)

## Highlights

- Convert EMSolution FEMAP Neutral files into VTK MultiBlock UnstructuredGrid (`.vtm`) output.
- Parse large models with a Cython-accelerated FEMAP reader.
- Explore simulation results in a Qt desktop app or inside Jupyter notebooks.
- Work with displacement, magnetic, current, force, and heat result data.

## Get Started

Install the base package:

```bash
pip install pyemsi
```

Install with notebook support:

```bash
pip install pyemsi[jupyter]
```

## Guides

- [Installation and setup](https://github.com/EMSolution-SSIL/pyemsi/blob/main/INSTALLATION.md)
- [Building from source](https://github.com/EMSolution-SSIL/pyemsi/blob/main/BUILDING.md)
- [Packaging and distribution](https://github.com/EMSolution-SSIL/pyemsi/blob/main/PACKAGING.md)

## Requirements

- Python 3.11
- VTK >= 9.0.0
- PyVista >= 0.43.0
- PySide6 >= 6.5.0
- NumPy >= 1.21.0

